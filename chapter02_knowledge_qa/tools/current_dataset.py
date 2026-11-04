"""Independent current dataset authoring, source validation and publication."""
from collections import Counter
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
EXPERIMENT=WORK/'graduation-experiment-results/chapter2_retrieval'
CORPUS=EXPERIMENT/'data/resources/corpus'
def digest(data):return hashlib.sha256(data).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def capability(g):return ('M' if g['labels']['evidence_integration']=='multiple' else 'S')+str(int(g['labels']['condition_discrimination']))

def build():
    inputs={p:load(ROOT/p/'scoring/authoring/items.json') for p in ('open','objective')}
    qs={p:[x['question'] for x in v['items']] for p,v in inputs.items()}
    gs={p:[x['gold'] for x in v['items']] for p,v in inputs.items()}
    ev=inputs['open']['evidence'];cache={}
    assert len(qs['open'])==100 and len(qs['objective'])==200
    assert Counter(capability(g) for g in gs['open'])==dict(S0=25,S1=25,M0=25,M1=25)
    assert Counter(q['type'] for q in qs['objective'])==dict(fill=60,short=60,single=50,judge=30)
    assert len({g['theme_id'] for g in gs['open']})==69
    assert len({g['knowledge_group'] for g in gs['open']})==24
    assert len({e['path'] for e in ev.values()})==42
    assert len({g['contrast_group'] for g in gs['open'] if g.get('contrast_group')})==8
    def source(rel):
        p=(CORPUS/rel).resolve();assert p.is_relative_to(CORPUS.resolve())
        if rel not in cache:
            raw=p.read_bytes();cache[rel]=(digest(raw),raw.decode('utf-8-sig').splitlines())
        return cache[rel]
    for e in ev.values():
        h,lines=source(e['path'])
        assert h==e['file_sha256']
        assert '\n'.join(lines[e['line_start']-1:e['line_end']]).rstrip()==e['excerpt'].rstrip()
        assert digest(e['excerpt'].encode())==e['excerpt_sha256']
    used=set()
    for g in gs['open']:
        assert set(g['required_evidence_ids'])<=ev.keys()
        points={p['id']:p for p in g['required_points']}
        assert points and len(points)==len(g['required_points'])
        for p in points.values():
            assert p['weight']>0 and set(p['evidence_ids'])<=ev.keys()
            for k,text in p.get('quotes',{}).items():assert k in p['evidence_ids'] and text in ev[k]['excerpt']
            used.update(p['evidence_ids'])
        for k,ids in g['source_contributions'].items():assert k in ev and set(ids)<=points.keys()
        used.update(g['required_evidence_ids']);used.update(g.get('supporting_evidence_ids',[]))
    assert used==ev.keys()
    for g in gs['objective']:
        for e in g['evidence']:
            h,lines=source(e['path']);assert h==e['file_sha256']
            assert '\n'.join(lines[e['start']-1:e['end']])==e['text']
            assert digest(e['text'].encode())==e['excerpt_sha256']==e['sha256']
            assert '\n'.join(lines[e['context_start']-1:e['context_end']])==e['context']
            assert digest(e['context'].encode())==e['context_sha256']
    for p in qs:
        assert len({q['id'] for q in qs[p]})==len({q['question'] for q in qs[p]})==len(qs[p])
        assert [q['id'] for q in qs[p]]==[g['id'] for g in gs[p]]
        assert all(set(q)=={'id','question'} for q in qs[p]) if p=='open' else all(set(q)<={'id','question','type','options'} for q in qs[p])
    sys.path.insert(0,str(WORK/'PrincipiaBlastFoam-DSH/experiments/chapter2'))
    from objective_scoring import score
    for q,g in zip(qs['objective'],gs['objective']):
        for value in [g['answer']]+g['aliases']:assert score(q,g,dict(status='answered',answer='FINAL: '+value))['score']==1,(q['id'],value)
        assert score(q,g,dict(status='failed'))['score']==0
        assert score(q,g,dict(status='answered',answer='FINAL: __incorrect__'))['score']==0
        if q['type']=='single':
            assert set(q['options'])==set('ABCD') and g['answer'] in q['options']
            for value in set('ABCD')-{g['answer']}:assert score(q,g,dict(status='answered',answer='FINAL: '+value))['score']==0
        if q['type']=='judge':
            value='错误' if g['answer']=='正确' else '正确'
            assert score(q,g,dict(status='answered',answer='FINAL: '+value))['score']==0
    overlap=[]
    for g in gs['objective']:
        related=[a['id'] for a in gs['open'] if any(e['path']==ev[k]['path'] and max(e['start'],ev[k]['line_start'])<=min(e['end'],ev[k]['line_end']) for e in g['evidence'] for k in a['required_evidence_ids'])]
        assert related==g['related_open_ids'],g['id']
        overlap.append(dict(id=g['id'],active_open_ids=related))
    common=dict(partition='full_evaluation',development_split=None,test_split=None,selection_by_method_scores=False,
                independent_human_review='pending',new_experiments='not_run',answering_modes=['single_pass','agentic'])
    om=dict(**common,part='open',count=100,capabilities=dict(Counter(capability(g) for g in gs['open'])),themes=69,knowledge_groups=24,source_files=42,evidence_anchors=len(ev),contrast_pairs=8,metric='EAS; Strict auxiliary')
    jm=dict(**common,part='objective',count=200,types=dict(Counter(q['type'] for q in qs['objective'])),
            fact_clusters=len({g['fact_cluster'] for g in gs['objective']}),source_files=len({e['path'] for g in gs['objective'] for e in g['evidence']}),
            metric='accuracy; four-type macro accuracy auxiliary',evidence_hash_policy='file_sha256 is file bytes; sha256/excerpt_sha256 is excerpt; context_sha256 is context')
    meta=dict(**common,schema='chapter2_current_dataset',total_questions=300,presentation_order=['objective','open'],
              parts={p:dict(count=len(qs[p]),questions=p+'/model/questions.json',gold=p+'/scoring/annotations.json') for p in qs})
    outputs={'dataset.json':encoded(meta),'open/dataset.json':encoded(om),'objective/dataset.json':encoded(jm),'open/scoring/evidence.json':encoded(ev),
             'objective/review/overlap.json':encoded(dict(basis='Required original source range intersection; not semantic equivalence.',items=overlap))}
    for p in qs:
        outputs[p+'/model/questions.json']=encoded(qs[p]);outputs[p+'/scoring/annotations.json']=encoded(gs[p])
        outputs[p+'/scoring/authoring/items.json']=(ROOT/p/'scoring/authoring/items.json').read_bytes()
        rows=[dict(id=q['id'],capability=capability(g),theme_id=g['theme_id'],knowledge_group=g['knowledge_group']) if p=='open' else dict(id=q['id'],type=q['type'],fact_cluster=g['fact_cluster']) for q,g in zip(qs[p],gs[p])]
        outputs[p+'/review/selection.json']=encoded(dict(basis='Current approved questions and source coverage; no model scores.',items=rows))
        text=['# '+('开放问答100题' if p=='open' else '客观题200题'),'','全量评价，不设开发集或测试留出集。此文件仅含公开题目，答案与证据仅在评分侧。','']
        for q in qs[p]:
            text+=['## '+q['id']+(' · '+q['type'] if 'type' in q else ''),'',q['question'],'']
            if q.get('options'):text+=[f'{k}. {v}' for k,v in q['options'].items()]+['']
        outputs[p+'/questions.md']=('\n'.join(text)+'\n').encode()
    binding=dict(schema='chapter2_current_binding',files={k:digest(v) for k,v in sorted(outputs.items())},builder_sha256=digest(Path(__file__).read_bytes()))
    binding['dataset_sha256']=digest(encoded(binding['files']));outputs['binding.json']=encoded(binding)
    baseline=EXPERIMENT/'release/validation/current_dataset_equivalence.json'
    if baseline.exists():
        expected={(x['part'],x['id']):x for x in load(baseline)['items']}
        for p in qs:
            for q,g in zip(qs[p],gs[p]):
                row=expected[p,q['id']]
                assert digest(encoded(q))==row['question_sha256'],q['id']
                assert digest(encoded(g))==row['scoring_semantics_sha256'],g['id']
    return outputs,dict(passed=True,total_questions=300,open=om,objective=jm,dataset_sha256=binding['dataset_sha256'],verified_source_files=len(cache),current_only=True,model_calls=0)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    outputs,report=build()
    if args.write:
        for rel,data in outputs.items():
            p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for part in ('open','objective'):
            p=ROOT/part/'review/records.json';records=load(p)
            q={x['id']:x for x in load(ROOT/part/'model/questions.json')};g={x['id']:x for x in load(ROOT/part/'scoring/annotations.json')}
            records.update(dataset_binding_sha256=report['dataset_sha256'],review_scope='Current questions and Gold; independent review records.')
            for row in records['items']:
                row['question_sha256']=digest(encoded(q[row['id']]));row['annotation_sha256']=digest(encoded(g[row['id']]))
            p.write_bytes(encoded(records))
        (EXPERIMENT/'release/validation/dataset_validation.json').write_bytes(encoded(report))
    differences=[rel for rel,data in outputs.items() if not (ROOT/rel).exists() or (ROOT/rel).read_bytes()!=data];assert not differences,differences
    for part in ('open','objective'):
        records=load(ROOT/part/'review/records.json');assert records['dataset_binding_sha256']==report['dataset_sha256']
        q={x['id']:x for x in load(ROOT/part/'model/questions.json')};g={x['id']:x for x in load(ROOT/part/'scoring/annotations.json')}
        assert {x['id'] for x in records['items']}==q.keys()
        for row in records['items']:
            assert row['question_sha256']==digest(encoded(q[row['id']])) and row['annotation_sha256']==digest(encoded(g[row['id']]))
    print(json.dumps({k:report[k] for k in ('passed','total_questions','dataset_sha256','verified_source_files','current_only','model_calls')},ensure_ascii=False))
