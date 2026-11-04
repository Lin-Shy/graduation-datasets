"""Offline verification of compact-action traffic, including its failed probe."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,collections,hashlib,json,sys

WORK=Path(__file__).resolve().parents[6]
CODE=WORK/'PrincipiaBlastFoam-DSH/experiments/chapter2'
ROOT=WORK/'graduation-experiment-results/chapter2_retrieval'
REVIEW=WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration'
sys.path.insert(0,str(CODE))
from structured_actions import decode,grammar
from runtime import action_content,parse_action,wire as wire_json
from tokenization import ChatCounter
from models import encoded,sha
from evidence_paths import preserved,material

def read(p):return json.loads(p.read_text('utf-8'))

def verify(run_id='compact_actions_multiline_20261104'):
    if run_id not in {'compact_actions_20261104','compact_actions_multiline_20261104'}:raise ValueError('Unknown technical run')
    root=ROOT/'technical'/run_id;summary=read(root/'summary.json')
    roots=[root]
    completion=ROOT/'technical/compact_actions_multiline_completion_20261104'
    if run_id=='compact_actions_multiline_20261104' and completion.exists():
        plan=read(completion/'completion_plan.json')
        assert plan['source_run']==root.name and plan['source_summary_sha256']==sha((root/'summary.json').read_bytes())
        assert plan['unchanged_fixture_sha256']==sha((root/'fixtures.json').read_bytes())
        assert (completion/'fixtures.json').read_bytes()==(root/'fixtures.json').read_bytes()
        roots.append(completion)
    for segment in roots:
        saved=read(segment/'summary.json')
        for name,h in saved['files'].items():assert sha((segment/name).read_bytes())==h,name
        snapshots=segment/'implementation'
        if not snapshots.exists():snapshots=ROOT/'release/frozen/interface_checks'/sha(encoded(saved['implementation']))
        for name,h in saved['implementation'].items():assert sha((snapshots/name).read_bytes())==h,name
    cases={c['name']:c for c in read(root/'fixtures.json')['cases']};models={};total=0;native_failures=[]
    for model in ('qwen3-8b','qwen3-14b','llama3.1-8b'):
        counter=ChatCounter(model);statuses=collections.Counter();calls=0;transport=[];failures=[]
        for name,case in cases.items():
            folders=[segment/model/name for segment in roots if list((segment/model/name/'requests').glob('*.json'))]
            assert len(folders)<=1,'A submitted case was repeated across segments'
            folder=folders[0] if folders else root/model/name;paths=sorted((folder/'requests').glob('*.json'))
            if not paths:statuses['not_started']+=1;continue
            result=read(folder/'result.json')
            for i,path in enumerate(paths):
                row=read(path);body=row['request'];raw=row['raw_response'];step=case['turns'][i];wire=path.with_suffix('.response.bin').read_bytes()
                assert sha(wire)==row['response_sha256'] and read(path.with_suffix('.response.bin'))==raw
                assert sha(encoded(body))==row['request_sha256']
                assert body['structured_outputs']==dict(grammar=grammar(step['schema'])) and 'response_format' not in body
                assert body['max_tokens']==2048 and body['temperature']==0 and body['stream'] is False
                expected_prompt=step['prompt']+('\n/no_think' if model=='qwen3-8b' else '')
                assert body['messages'][-1]==dict(role='user',content=expected_prompt),'Synthetic input presentation mismatch'
                choice=raw['choices'][0];u=raw['usage'];obj=decode(action_content(choice['message']['content']),step['schema'])
                assert row['http_status']==200 and row['transport_attempts']==1 and raw['model']==body['model']
                assert counter(body['messages'])==u['prompt_tokens'] and u['prompt_tokens']+2048<=32768
                assert 0<=u['completion_tokens']<=2048 and choice['finish_reason']=='stop'
                native={k:v for k,v in obj.items() if k!='final_answer'}
                try:parse_action(wire_json(native),{'search','catalog','read_source'},obj['action']=='final')
                except ValueError:native_failures.append((model,name))
                literal_ok='answer' not in step or obj['answer']==step['answer']
                if not literal_ok:
                    failures.append(dict(case=name,expected_repr=repr(step['answer']),delivered_repr=repr(obj['answer']),
                                         classification='literal_text_fidelity_failure_not_local_JSON_rewrite'))
                semantic_ok=literal_ok
                if 'answer' in step:semantic_ok=semantic_ok and obj['references']==[]
                if 'final_answer' in step:semantic_ok=semantic_ok and obj.get('final_answer')==step['final_answer']
                if step.get('tool'):
                    semantic_ok=semantic_ok and obj['name']==step['tool']
                    a=obj['arguments']
                    if name=='empty_catalog':semantic_ok=semantic_ok and a==dict(query='',offset=0)
                    if obj['name']=='read_source':semantic_ok=semantic_ok and a==dict(path='manual/'+('beta' if name=='multi_read_source' else 'alpha')+'.md',start=1,end=2)
                assert result['turns'][i]['passed']==semantic_ok,'Stored case verdict differs from offline verification'
                transport.append(True);calls+=1
            if result['passed']:statuses['passed']+=1
            elif len(paths)<len(case['turns']):statuses['paused_incomplete']+=1
            else:statuses['failed']+=1
        models[model]=dict(requests=calls,case_statuses=dict(statuses),all_submitted_wire_identity_token_schema_checks_passed=all(transport),
                           literal_fidelity_failures=failures,full_model_suite_passed=statuses['passed']==12)
        total+=calls
    original_ph='cadc6b76ac42cb356d9fb5072f5862598a5bc4e04019d45257b630bf21fadcfc'
    old=read(material((REVIEW/'administration/generation_check.json').relative_to(WORK).as_posix(),original_ph))
    for name,h in old['files'].items():assert sha((ROOT/name).read_bytes())==h
    gate=read(ROOT/'release/planning/execution.json');assert not gate['formal_generation_authorized'] and not gate['allowed_stages']
    source=read(REVIEW/'administration/failure_analysis.json')
    for name,h in source['preserved_files'].items():assert sha(preserved(name,h).read_bytes())==h,name
    precheck=read(ROOT/'release/planning/multiline_synthetic_precheck.json')
    for name,h in precheck['protected_files_before_new_validation'].items():assert sha(preserved(name,h).read_bytes())==h,name
    assert total==sum(read(segment/'summary.json')['model_requests'] for segment in roots)
    accepted=total==42 and all(m['full_model_suite_passed'] for m in models.values())
    assert sum(len(list(segment.glob('*/*/requests/*.json'))) for segment in roots)==total,'Orphan request outside registered cases'
    if len(roots)==1:
        assert summary['passed']==accepted
        assert summary['models']=={m:v['full_model_suite_passed'] for m,v in models.items()}
    complete=total==42 and all(sum(v['case_statuses'].values())==12 and not (set(v['case_statuses'])-{'passed','failed'}) for v in models.values())
    if len(roots)>1:
        for model in models:
            first=read(root/model/'summary.json');second=read(completion/model/'summary.json')
            assert first['deployment']==second['deployment'] and first['tokenizer']==second['tokenizer'],'Deployment changed across segments'
        native_report=read(REVIEW/'administration/multiline_action_contract_check.json')
        assert sorted(native_failures)==sorted((f['model'],f['case']) for f in native_report['failures'])
        assert native_report['requests']==total and native_report['passed_actions']==total-len(native_failures)
    active=read(ROOT/'release/manifests/calibration_generation.json')
    rerun_started=active['protocol_sha256']!=original_ph and bool(list((ROOT/'runs'/active['protocol_sha256']).glob('*/*/claim.json')))
    return dict(schema='compact_interface_repair_offline_review_v1',verified_utc=datetime.now(timezone.utc).isoformat(),
                run_id=run_id,segments={segment.name:read(segment/'summary.json')['model_requests'] for segment in roots},
                integrity_passed=True,complete=complete,interface_acceptance_passed=accepted,
                status='synthetic_interface_passed' if accepted else 'synthetic_checks_complete_not_passed' if complete else 'paused_after_literal_fidelity_failure',
                model_requests=total,planned_requests=42,remaining_unsubmitted_requests=42-total,models=models,
                query_limit=512,output_limit=2048,old_calibration_files_unchanged=len(old['files']),
                formal_dispatch_closed=True,calibration_rerun_started=rerun_started,acceptance_started=False,full_matrix_started=False,
                original_human_material_preserved=True,new_human_labels=0,ai_judge_calls=0,
                native_actions_passed=total-len(native_failures),native_actions_failed=len(native_failures),
                previous_technical_files_unchanged=True,
                interpretation='Historical synthetic interface checks, not formal QA scores or human judge acceptance. Strict all-case acceptance remains false. A later user authorization accepts model-output failures for the uniform calibration rerun without changing these case verdicts; previous failed probes remain unchanged.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--run-id',default='compact_actions_multiline_20261104');args=p.parse_args();r=verify(args.run_id)
    if args.write:
        name='multiline_interface_check.json' if args.run_id=='compact_actions_multiline_20261104' else 'interface_repair_check.json'
        with (REVIEW/'administration'/name).open('xb') as f:f.write(encoded(r))
    print(json.dumps(r,ensure_ascii=False))

if __name__=='__main__':main()
