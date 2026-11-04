"""Offline audit/binding of the separately frozen transport recovery."""
from pathlib import Path
from copy import deepcopy
import argparse, collections, json, sys
from verify_generation import verify as verify_base, WORK, ROOT, REVIEW, CODE, read, require
from evidence_paths import material
sys.path.insert(0,str(CODE))
from recover_transport import verify_overlay,recovery_root,task_folder
from models import encoded, sha, now, strict_json
from tokenization import ChatCounter
from runtime import action_content

UNRESOLVED={'outcome_unknown','http_result_unknown','deployment_halted','not_dispatched_model_halted','runner_error','usage_unknown','response_persistence_error'}
def audit():
    packets=read(REVIEW/'calibration/packets.json')
    base=verify_base(protocol=packets.get('generation_protocol_sha256'),allow_unresolved=True)
    ph=base['protocol_sha256'];p=read(ROOT/'release/frozen'/ph/'run_protocol.json')
    h=packets.get('transport_execution_overlay_sha256') or read(ROOT/'release/planning/transport_retry.json')['overlay_sha256']
    o=verify_overlay(p,check_current=False,overlay_sha256=h);gate=read(ROOT/'release/planning/execution.json')
    require(not gate.get('transport_recovery_authorized') and not gate['formal_generation_authorized'] and not gate['allowed_stages'],'Close dispatch before sealing')
    root=recovery_root(h);selected={e['task']['task_id']:e for e in o['selected_tasks']}
    require({x.parent.name for x in root.glob('*/*/result.json')}<={s[:16] for s in selected},'Unselected recovery result')
    counters={m:ChatCounter(m) for m in p['deployments']};effective={};new_requests=confirmed_inputs=known_outputs=unknown_attempts=resubmissions=0;statuses=collections.Counter();files={};issues=[]
    for tid,entry in selected.items():
        task=entry['task'];rp=task_folder(root/task['model'],tid)/'result.json';original=ROOT/entry['result']
        require(sha(original.read_bytes())==entry['result_sha256'],'Original task changed')
        if not rp.exists():effective[tid]=read(original);statuses['not_dispatched']+=1;continue
        r=read(rp);require(r['task']==task and r['protocol_sha256']==ph,'Recovered task binding mismatch')
        guard=read(rp.parents[1]/'input_guard.json');require(guard['gold_and_authoring_disabled'] and guard['subprocess_disabled'],'Recovery input guard absent')
        paths=sorted((rp.parent/'requests').glob('*.json'));require(len(paths)==len(r['turns'])<=13,'Recovery turn count mismatch')
        tin=tout=0
        for i,(qpath,turn) in enumerate(zip(paths,r['turns'])):
            q=read(qpath);body=q['request'];require(qpath.name==f'{i:02d}.json' and q['request_sha256']==sha(encoded(body))==turn['request_sha256'],'Recovered request binding mismatch')
            require(q['deployment']==p['deployments'][task['model']],'Recovered deployment mismatch')
            count=counters[task['model']](body['messages']);require(count==turn['counted_input_tokens'] and count+2048<=32768,'Recovered input tokens mismatch')
            require(body['max_tokens']==2048 and body['temperature']==0 and not body['stream'] and 'structured_outputs' in body and 'response_format' not in body,'Inference parameters changed')
            tin+=count;cost=0;network=0
            for a in q['attempts']:
                ap=(qpath.parent/a['record_file']).resolve();require(ap.is_relative_to(qpath.parent.resolve()),'Attempt path escapes task')
                require(sha(ap.read_bytes())==a['record_sha256'],'Attempt changed');ar=read(ap)
                require(ar['request']==body and ar['request_sha256']==q['request_sha256'] and ar['deployment']==q['deployment'],'Retry did not use identical request')
                cost+=1 if ar['status']=='in_flight' else ar['transport_attempts']
                if a['origin']=='imported':
                    src=original.parent/'requests'/qpath.name;original_row=read(src);stripped=dict(ar);stripped.pop('origin');oldhash=stripped.pop('imported_record_sha256')
                    require(oldhash==sha(src.read_bytes()) and stripped==original_row,'Imported original record mismatch')
                else:
                    network+=ar['transport_attempts'];new_requests+=ar['transport_attempts']
                    if ar['transport_attempts'] and cost>1:resubmissions+=1
                    if ar['status']=='response':
                        u=ar['raw_response']['usage'];require(u['prompt_tokens']==count and 0<=u['completion_tokens']<=2048,'Retry usage mismatch')
                        confirmed_inputs+=u['prompt_tokens'];known_outputs+=u['completion_tokens']
                    elif ar['transport_attempts']:unknown_attempts+=1
                if ar.get('response_sha256'):
                    wire=ap.with_suffix('.response.bin');require(sha(wire.read_bytes())==ar['response_sha256'] and strict_json(wire.read_bytes())==ar['raw_response'],'Attempt HTTP body mismatch')
            require(cost==q['transport_attempts']<=o['retry_policy']['max_attempts'],'Transport retry bound exceeded')
            original_request=original.parent/'requests'/qpath.name
            if original_request.exists() and read(original_request)['status']=='response':
                require(network==0 and q.get('response_sha256')==read(original_request)['response_sha256'],'A received original prefix was regenerated')
            if q['status']=='response':
                raw=q['raw_response'];require(raw['model']==p['deployments'][task['model']]['api_model'],'Response model changed')
                wire=qpath.with_suffix('.response.bin');require(sha(wire.read_bytes())==q['response_sha256']==turn['response_sha256'] and strict_json(wire.read_bytes())==raw,'Selected response binding mismatch')
                require(raw['usage']['prompt_tokens']==count,'Response tokenizer mismatch');tout+=raw['usage']['completion_tokens']
                if raw['choices'][0]['finish_reason']!='stop':require(r['status']=='completion_truncated','Truncation not preserved')
        require(tin==r['counted_input_tokens'] and tout==r['completion_tokens'],'Logical task usage mismatch')
        cap=p['budgets'].get(task['budget'],0);events=r['tool_events'];require(sum(len(x['response']) for x in events)==r['knowledge_characters']<=cap,'Evidence budget changed')
        require(len(events)<=(1 if task['mode']=='single_pass' else 12),'Tool call budget changed')
        require(all(len(x['response'])<=(cap if task['mode']=='single_pass' else 6000) for x in events),'Per-call evidence cap changed')
        if r['status']=='answered':
            obj=strict_json(action_content(read(paths[-1])['raw_response']['choices'][0]['message']['content']))
            require(obj['action']=='final' and obj['answer']==r['answer'] and obj['references']==r['references'],'Recovered answer modified')
        else:
            last=read(paths[-1]).get('raw_response',{})
            issues.append(dict(task_id=tid,status=r['status'],finish_reason=last.get('choices',[{}])[0].get('finish_reason'),completion_tokens=last.get('usage',{}).get('completion_tokens')))
        effective[tid]=r;statuses[r['status']]+=1
    for f in root.rglob('*'):
        if f.is_file():files[f.relative_to(ROOT).as_posix()]=sha(f.read_bytes())
    resolved=sum(r['status'] not in UNRESOLVED for r in effective.values())
    answered=44+sum(r['status']=='answered' for r in effective.values())
    all_statuses=collections.Counter()
    by_model={}
    manifest=read(ROOT/'release/manifests/calibration_generation.json')
    for task in manifest['selected_tasks']:
        r=effective.get(task['task_id']) or read(ROOT/'runs'/ph/task['model']/task['task_id']/'result.json')
        all_statuses[r['status']]+=1;by_model.setdefault(task['model'],collections.Counter())[r['status']]+=1
    return dict(schema='transport_recovery_integrity_v1',verified_utc=now(),passed=True,base_protocol_sha256=ph,execution_overlay_sha256=h,
                task_count=60,recovery_tasks=16,recovery_statuses=dict(statuses),effective_statuses=dict(all_statuses),models={m:dict(v) for m,v in by_model.items()},answered=answered,
                model_output_failures=sum(n for s,n in all_statuses.items() if s!='answered' and s not in UNRESOLVED),unresolved=16-resolved,ready_for_complete_calibration=resolved==16,
                additional_transmitted_requests=new_requests,transport_resubmissions=resubmissions,additional_confirmed_input_tokens=confirmed_inputs,additional_known_completion_tokens=known_outputs,new_unknown_attempts=unknown_attempts,
                historical_unknown_attempts=15,historical_unknown_usage_remains_unknown=True,original_run_files_unchanged=len(base['files']),files=files,issues=issues,
                existing_44_answers_repeated=False,query_characters_max=512,output_tokens_max=2048,human_labels_completed=0,acceptance_started=False,full_matrix_started=False,ai_judging_started=False),effective

def bind(report,effective):
    ph=report['base_protocol_sha256'];path=REVIEW/'calibration/packets.json';before=path.read_bytes()
    require(before==material(path.relative_to(WORK).as_posix(),ph).read_bytes(),'Only the preserved partial cohort may be completed')
    packets=read(path);mapping={x['sample_id']:x['task'] for x in read(REVIEW/'administration/sample_mapping.json')['samples'] if x['phase']=='calibration'};transitions=[]
    for packet in packets['samples']:
        tid=mapping[packet['sample_id']]['task_id']
        if tid not in effective:continue
        r=effective[tid]
        require(packet['binding_status']=='awaiting_resolution' and packet['answer'] is None,'Never replace an already received answer')
        if r['status'] in UNRESOLVED:continue
        failed=r['status']!='answered';answer='[未生成有效回答：'+r['status']+']' if failed else r['answer']
        packet.update(answer=answer,answer_sha256=sha(answer.encode()),generation_failed=failed,binding_status='bound',generation_status=r['status'],references=r.get('references',[]),references_delivered=r.get('references_delivered'))
        transitions.append(dict(sample_id=packet['sample_id'],task_id=tid,answer_sha256=packet['answer_sha256'],status=r['status']))
    packets['transport_execution_overlay_sha256']=report['execution_overlay_sha256'];raw=encoded(packets)
    receipt=REVIEW/'administration/cohort_transport_recovery.json';require(not receipt.exists(),'Do not replace a recovery transition')
    receipt.write_bytes(encoded(dict(schema='cohort_transport_recovery_v1',completed_utc=now(),base_protocol_sha256=ph,execution_overlay_sha256=report['execution_overlay_sha256'],previous_packet_sha256=sha(before),packet_sha256=sha(raw),existing_44_unchanged=True,transitions=transitions)))
    temp=path.with_suffix('.new');temp.write_bytes(raw);temp.replace(path)

def binding_check(report,effective):
    from human_review import verify_plan
    verify_plan();ph=report['base_protocol_sha256'];packets=read(REVIEW/'calibration/packets.json');old=read(material((REVIEW/'calibration/packets.json').relative_to(WORK).as_posix(),ph))
    oldby={p['sample_id']:p for p in old['samples']};mapping={x['sample_id']:x['task'] for x in read(REVIEW/'administration/sample_mapping.json')['samples'] if x['phase']=='calibration'}
    require(packets['transport_execution_overlay_sha256']==report['execution_overlay_sha256'],'Human material execution mismatch')
    bound=failed=unresolved=0
    for packet in packets['samples']:
        require(not {'model','method','budget','task_id','task','human_scores','ai_scores'}&set(packet),'Identity leak in anonymous material')
        task=mapping[packet['sample_id']];tid=task['task_id']
        if tid not in effective:require(packet==oldby[packet['sample_id']],'An existing answer or scoring basis changed')
        r=effective.get(tid) or read(ROOT/'runs'/ph/task['model']/tid/'result.json')
        if r['status'] in UNRESOLVED:
            require(packet['answer'] is None and packet['binding_status']=='awaiting_resolution','Unresolved outcome assigned an answer');unresolved+=1;continue
        isfailed=r['status']!='answered';expected='[未生成有效回答：'+r['status']+']' if isfailed else r['answer']
        require(packet['answer']==expected and packet['answer_sha256']==sha(expected.encode()) and packet['generation_failed']==isfailed and packet['generation_status']==r['status'] and packet['binding_status']=='bound','Recovered answer binding mismatch')
        require(packet['references']==r.get('references',[]) and packet['references_delivered']==r.get('references_delivered'),'Recovered reference binding mismatch')
        bound+=not isfailed;failed+=isfailed
    for phase in ('calibration','acceptance'):
        lp=REVIEW/phase/'blank_labels.json';require(lp.read_bytes()==material(lp.relative_to(WORK).as_posix(),ph).read_bytes(),'Human template changed')
    acceptance=REVIEW/'acceptance/packets.json';require(acceptance.read_bytes()==material(acceptance.relative_to(WORK).as_posix(),ph).read_bytes(),'Acceptance changed')
    ui=read(REVIEW/'administration/human_form_checks.json');require(ui['passed'] and ui['currentCounts']['valid_answers']==bound and ui['currentCounts']['failed']==failed,'Browser check mismatch')
    report.update(binding_verified=True,bound_answers=bound,bound_failures=failed,unbound=unresolved,packet_sha256=sha((REVIEW/'calibration/packets.json').read_bytes()),existing_44_unchanged=True)

def run(*,do_bind=False,binding=False,write=False):
    report,effective=audit()
    if do_bind:bind(report,effective)
    if binding:binding_check(report,effective)
    target=REVIEW/'administration'/('transport_recovery_binding_check.json' if binding else 'transport_recovery_generation_check.json')
    if target.exists():require(read(target)['files']==report['files'],'Sealed recovery files changed')
    elif write:
        with target.open('xb') as f:f.write(encoded(report))
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bind',action='store_true');p.add_argument('--binding',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    report=run(do_bind=a.bind,binding=a.binding,write=a.write);print(json.dumps({k:v for k,v in report.items() if k not in {'files','issues'}},ensure_ascii=False))
if __name__=='__main__':main()
