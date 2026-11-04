"""Read-only, score-side verification of the authorized 60-task generation.

No inference client, retries, answer repair, AI scoring or human label creation.
Use --write to save an immutable integrity receipt after the run closes.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,sys

WORK=Path(__file__).resolve().parents[6]
ROOT=WORK/'graduation-experiment-results/chapter2_retrieval'
REVIEW=WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration'
CODE=WORK/'PrincipiaBlastFoam-DSH/experiments/chapter2'
sys.path.insert(0,str(CODE))
from models import encoded,sha,strict_json
from tokenization import ChatCounter
from runtime import action_content
from evidence_paths import material

def read(path):return json.loads(Path(path).read_text('utf-8'))
def require(condition,message):
    if not condition:raise ValueError(message)

def review_material(name,ph,historical):
    path=REVIEW/name
    return material(path.relative_to(WORK).as_posix(),ph) if historical else path

def verify(protocol=None,allow_unresolved=False):
    manifest=read(ROOT/'release/manifests/calibration_generation.json')
    historical=protocol is not None and protocol!=manifest['protocol_sha256']
    if historical:manifest=read(material('graduation-experiment-results/chapter2_retrieval/release/manifests/calibration_generation.json',protocol))
    ph=manifest['protocol_sha256']
    frozen=ROOT/manifest['frozen_protocol'];require(sha(frozen.read_bytes())==ph,'Frozen protocol hash mismatch')
    p=read(frozen);tasks={r['task_id']:r for r in manifest['selected_tasks']};selected=set(p['generation_panels']['calibration'])
    require(len(tasks)==60 and set(tasks)==selected,'Expected exactly the preselected 60 calibration tasks')
    require(manifest['authorization']['allowed_stages']==['calibration'],'Authorization scope mismatch')
    data=WORK/'graduation-datasets/chapter02_knowledge_qa';binding=read(data/'binding.json')
    require(binding['dataset_sha256']==p['dataset_sha256'],'Current dataset drift')
    for name,h in binding['files'].items():require(sha((data/name).read_bytes())==h,'Dataset content drift: '+name)
    resources=ROOT/'data/resources';require(sha((resources/'manifest.json').read_bytes())==p['resources_sha256'],'Resource manifest drift')
    for name,h in read(resources/'manifest.json')['files'].items():require(sha((resources/name).read_bytes())==h,'Resource drift: '+name)
    snapshots=frozen.parent/'implementation'
    for name,h in p['implementation'].items():require(sha((snapshots/name).read_bytes())==h,'Frozen code drift: '+name)
    run=ROOT/'runs'/ph;claims={q.parent.name for q in run.glob('*/*/claim.json')};results={q.parent.name for q in run.glob('*/*/result.json')}
    require(claims<=selected and results<=selected,'An unselected task was run')
    require(claims==results==selected,'Missing or unresolved task; do not resubmit automatically')
    expected_paths={run/t['model']/tid/'result.json' for tid,t in tasks.items()}
    require(set(run.glob('*/*/result.json'))==expected_paths and len(list(run.glob('*/*/claim.json')))==60,'Duplicated or misplaced task directory')
    questions={q['id']:q['question'] for q in read(data/'open/model/questions.json')}
    counters={m:ChatCounter(m) for m in p['deployments']};models={};issues=[];all_files={};inputs=outputs=request_count=0
    unknown={'outcome_unknown','http_result_unknown','usage_unknown','runner_error','deployment_halted','not_dispatched_model_halted'}
    unresolved_count=interrupted_count=confirmed_inputs=transmitted_requests=0
    for model in p['deployments']:
        status=collections.Counter();requests=0;model_inputs=model_outputs=0;reference_flags=0;model_confirmed_inputs=model_transmitted=0
        guard=read(run/model/'input_guard.json');require(guard['gold_and_authoring_disabled'] and guard['subprocess_disabled'],'Input guard missing')
        require(counters[model].public()==p['tokenizers'][model],'Tokenizer drift')
        for tid,task in tasks.items():
            if task['model']!=model:continue
            folder=run/model/tid;r=read(folder/'result.json');claim=read(folder/'claim.json')
            require(r['task']==claim['task']==task,'Task identity mismatch')
            require(r['protocol_sha256']==claim['protocol_sha256']==ph,'Result protocol mismatch')
            require(allow_unresolved or r['status'] not in unknown,'Unknown outcome requires reconciliation: '+tid+'; --allow-unresolved only documents the incomplete run')
            status[r['status']]+=1;paths=sorted((folder/'requests').glob('*.json'))
            require(len(paths)==len(r['turns'])<=13,'Turn count mismatch')
            tin=tout=0
            for i,(path,turn) in enumerate(zip(paths,r['turns'])):
                q=read(path);raw=q.get('raw_response',{});u=raw.get('usage',{});body=q['request']
                require(path.name==f'{i:02d}.json' and turn['turn']==i,'Turn ordering mismatch')
                require(q['status']=='response' or (allow_unresolved and q['status'] in {'outcome_unknown','http_result_unknown','deployment_halted'} and i==len(paths)-1 and r['status']==q['status']),'Incomplete or unexpected request')
                require(q['transport_attempts']==(0 if q['status']=='deployment_halted' else 1),'Repeated request')
                require(q['deployment']==p['deployments'][model],'Deployment mismatch')
                model_transmitted+=q['transport_attempts']
                require(sha(encoded(body))==q['request_sha256']==turn['request_sha256'],'Request hash mismatch')
                require(q.get('response_sha256')==turn.get('response_sha256'),'Response binding mismatch')
                if p.get('response_body_capture') and q['status']=='response':
                    wire=path.with_suffix('.response.bin');require(sha(wire.read_bytes())==q['response_sha256'] and strict_json(wire.read_bytes())==raw,'Original HTTP body mismatch')
                    require('structured_outputs' in body and 'response_format' not in body,'Compact action transport missing')
                count=counters[model](body['messages'])
                require(next(m['content'] for m in body['messages'] if m['role']=='user').startswith(questions[task['id']]),'Wrong public question sent')
                require(count==turn['counted_input_tokens'],'Local chat tokenizer mismatch')
                require(count+body['max_tokens']<=32768 and body['max_tokens']==2048,'Token budget exceeded')
                require(body['temperature']==0 and body['stream'] is False,'Sampling parameters drift')
                if model=='llama3.1-8b':require('enable_thinking' not in body and all('/no_think' not in m['content'] for m in body['messages']),'Qwen parameters sent to Llama')
                tin+=count;requests+=1
                if q['status']=='response':
                    require(raw.get('model')==p['deployments'][model]['api_model'],'Response model mismatch')
                    require(type(u.get('prompt_tokens')) is int and type(u.get('completion_tokens')) is int,'Missing usage')
                    require(count==u['prompt_tokens'] and 0<=u['completion_tokens']<=2048,'Provider token mismatch')
                    model_confirmed_inputs+=count;tout+=u['completion_tokens']
                    if raw['choices'][0]['finish_reason']!='stop':require(r['status']=='completion_truncated' and i==len(paths)-1,'Unrecorded truncation')
                else:
                    require(not raw and turn.get('response_sha256') is None,'Unexpected response in unresolved request')
                    if q['status']=='outcome_unknown':require(q.get('error_type')=='TimeoutError','An unresolved non-timeout needs separate review')
            require(tin==r['counted_input_tokens'] and tout==r['completion_tokens'],'Cumulative usage mismatch')
            events=r['tool_events'];cap=0 if task['method']=='direct' else p['budgets'][task['budget']]
            max_calls=0 if task['method']=='direct' else 1 if task['mode']=='single_pass' else 12
            require(len(events)<=max_calls,'Tool call budget exceeded')
            require(sum(len(e['response']) for e in events)==r['knowledge_characters']<=cap,'Evidence budget mismatch')
            require(all(len(e['response'])==e['delivered_characters'] and len(e['response'])<=(cap if task['mode']=='single_pass' else 6000) for e in events),'Per-tool budget mismatch')
            if r['status']=='answered':
                require(bool(r['answer']) and bool(paths),'Answered record lacks a final response')
                obj=strict_json(action_content(read(paths[-1])['raw_response']['choices'][0]['message']['content']))
                require(obj['action']=='final' and obj['answer']==r['answer'] and obj['references']==r['references'],'Final answer altered')
                reference_flags+=not r['references_delivered']
            else:
                last=read(paths[-1]);last_raw=last.get('raw_response',{});reason=last_raw.get('choices',[{}])[0].get('finish_reason')
                issues.append(dict(task_id=tid,question_id=task['id'],model=model,method=task['method'],mode=task['mode'],budget=task['budget'],status=r['status'],finish_reason=reason,
                    request_count=len(paths),last_completion_tokens=last_raw.get('usage',{}).get('completion_tokens'),error_type=last.get('error_type'),resubmitted=False))
            model_inputs+=tin;model_outputs+=tout
        require(sum(status.values())==20,'Per-model denominator must be 20')
        models[model]=dict(tasks=20,statuses=dict(status),requests=requests,transmitted_requests=model_transmitted,input_tokens=model_inputs,provider_confirmed_input_tokens=model_confirmed_inputs,completion_tokens=model_outputs,reference_delivery_flags=reference_flags)
        unresolved_count+=sum(status[k] for k in unknown-{'deployment_halted','not_dispatched_model_halted'})
        interrupted_count+=status['deployment_halted']+status['not_dispatched_model_halted']
        confirmed_inputs+=model_confirmed_inputs;transmitted_requests+=model_transmitted
        inputs+=model_inputs;outputs+=model_outputs;request_count+=requests
    files=run.rglob('*') if p.get('response_body_capture') else run.rglob('*.json')
    for file in files:
        if file.is_file():all_files[file.relative_to(ROOT).as_posix()]=sha(file.read_bytes())
    require(request_count==len(list(run.glob('*/*/requests/*.json'))),'An orphan request exists')
    initial=review_material('administration/generation_check.json',ph,historical)
    if initial.exists():
        original=read(initial)
        if original['protocol_sha256']==ph:require(original['files']==all_files,'Original run files changed after integrity verification')
        else:
            saved=material(initial.relative_to(WORK).as_posix(),original['protocol_sha256'])
            require(sha(saved.read_bytes())==sha(initial.read_bytes()),'Previous receipt was not preserved before cohort switch')
    answered=sum(m['statuses'].get('answered',0) for m in models.values())
    return dict(schema='calibration_generation_integrity_v1',verified_utc=datetime.now(timezone.utc).isoformat(),passed=True,closed_tasks=60,
        answered=answered,failed=60-answered-unresolved_count-interrupted_count,unknown=unresolved_count,interrupted=interrupted_count,resolved_tasks=60-unresolved_count-interrupted_count,ready_for_complete_calibration=not (unresolved_count or interrupted_count),models=models,request_count=request_count,transmitted_requests=transmitted_requests,input_tokens=inputs,provider_confirmed_input_tokens=confirmed_inputs,completion_tokens=outputs,
        protocol_sha256=ph,dataset_sha256=p['dataset_sha256'],selected_task_ids=sorted(selected),issues=issues,files=all_files,
        full_matrix_dispatch_started=False,acceptance_generation_started=False,ai_judging_started=False,human_labels_completed=0,
        interpretation='Integrity verification only. closed_tasks counts local terminal records, not resolved provider outcomes. Unknown and interrupted tasks are not model failures or zero scores; complete calibration requires resolved outcomes. input_tokens are locally counted request inputs including a possible unsent halted request; provider_confirmed_input_tokens and completion_tokens cover returned responses only. Missing response usage remains unknown. No retries, repairs or replacement samples.')

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--write',action='store_true');a.add_argument('--binding',action='store_true');a.add_argument('--protocol');a.add_argument('--allow-unresolved',action='store_true',help='Audit incomplete transport records without treating them as resolved or model failures');args=a.parse_args()
    if args.binding and not args.protocol and read(REVIEW/'calibration/packets.json').get('transport_execution_overlay_sha256'):
        from verify_transport_recovery import run
        report=run(binding=True,write=args.write);print(json.dumps({k:v for k,v in report.items() if k not in {'files','issues'}},ensure_ascii=False));return
    report=verify(args.protocol,args.allow_unresolved)
    ph=report['protocol_sha256'];historical=ph!=read(ROOT/'release/manifests/calibration_generation.json')['protocol_sha256']
    if args.binding:
        from human_review import verify_plan
        verify_plan()
        mapping={r['sample_id']:r['task'] for r in read(REVIEW/'administration/sample_mapping.json')['samples'] if r['phase']=='calibration'}
        packets=read(review_material('calibration/packets.json',ph,historical));run=ROOT/'runs'/report['protocol_sha256'];valid=failed=unresolved=0
        if packets.get('generation_protocol_sha256'):require(packets['generation_protocol_sha256']==ph,'Mixed generation protocols in human material')
        forbidden={'model','method','budget','task','task_id','judge_scores','human_scores','ai_scores'}
        for packet in packets['samples']:
            require(not forbidden&set(packet),'Model/method/grade information leaked into human packet')
            task=mapping[packet['sample_id']];result=read(run/task['model']/task['task_id']/'result.json')
            if result['status'] in {'outcome_unknown','http_result_unknown','deployment_halted','not_dispatched_model_halted'}:
                require(args.allow_unresolved and packet['answer'] is None and packet['answer_sha256'] is None and packet['binding_status']=='awaiting_resolution' and not packet['generation_failed'] and packet['generation_status']==result['status'],'Unknown outcome was bound as an answer/failure')
                unresolved+=1;continue
            isfailed=result['status']!='answered'
            expected=result['answer'] if not isfailed else '[未生成有效回答：'+result['status']+']'
            require(packet['answer']==expected and packet['answer_sha256']==sha(expected.encode()),'Bound answer differs from the actual result')
            require(packet['binding_status']=='bound' and packet['generation_failed']==isfailed and packet['generation_status']==result['status'],'Bound status mismatch')
            require(packet['references']==result.get('references',[]) and packet['references_delivered']==result.get('references_delivered'),'Reference binding mismatch')
            valid+=not isfailed;failed+=isfailed
        acceptance=read(review_material('acceptance/packets.json',ph,historical))
        require(not acceptance['enabled_for_review'] and all(p['answer'] is None and p['binding_status']=='awaiting_generation' for p in acceptance['samples']),'Acceptance was generated or unlocked')
        for phase in ('calibration','acceptance'):
            require(all(l['record']['status']=='pending' and l['reviewer'] is None for l in read(review_material(phase+'/blank_labels.json',ph,historical))['labels']),'Human labels were prefilled')
        gate=read(ROOT/'release/planning/execution.json');require(not gate['formal_generation_authorized'] and not gate['allowed_stages'],'Dispatch is still enabled')
        ui=read(review_material('administration/human_form_checks.json',ph,historical));require(ui['passed'] and ui['currentCounts']['valid_answers']==valid and ui['currentCounts']['failed']==failed,'Post-binding browser check mismatch')
        require(unresolved==report.get('unknown',0)+report.get('interrupted',0),'Unresolved packet count mismatch')
        report.update(binding_verified=True,bound_valid_answers=valid,bound_failures=failed,unbound_unresolved=unresolved,acceptance_still_locked=True,dispatch_disabled=True,
            human_material_files={(REVIEW/n).relative_to(WORK).as_posix():sha(review_material(n,ph,historical).read_bytes()) for n in ['calibration/packets.json','acceptance/packets.json','index.html']})
    if args.write:
        require(not historical,'Historical receipts remain immutable')
        path=REVIEW/'administration'/('binding_check.json' if args.binding else 'generation_check.json')
        if path.exists():
            old=read(path);require(old['protocol_sha256']!=ph,'Do not overwrite a same-protocol receipt')
            saved=material(path.relative_to(WORK).as_posix(),old['protocol_sha256']);require(sha(saved.read_bytes())==sha(path.read_bytes()),'Previous receipt not preserved')
            temp=path.with_suffix('.new');temp.write_bytes(encoded(report));temp.replace(path)
        else:
            with path.open('xb') as stream:stream.write(encoded(report))
    print(json.dumps({k:v for k,v in report.items() if k not in {'files','issues','selected_task_ids'}},ensure_ascii=False))

if __name__=='__main__':main()
