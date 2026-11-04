"""Verify descriptive calibration documentation. No model calls or scoring changes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re

WORK=Path(__file__).resolve().parents[6]
REVIEW=WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration'
TRIAL=REVIEW/'ai_calibration/85b246b6f258'
OUT=TRIAL/'discussion'
EXP=WORK/'graduation-experiment-results/chapter2_retrieval'
MANIFEST=EXP/'release/manifests/current.json'
RECEIPT=EXP/'technical/calibration_results_documentation_check.json'


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(WORK).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def require(x,msg):
    if not x:raise AssertionError(msg)


def check_links(planned=False):
    count=0
    for doc in OUT.glob('*.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
            if target.startswith(('http://','https://','#')):continue
            p=Path(re.sub(r':\d+$','',target.strip('<>').split('#')[0]))
            if not p.is_absolute():p=doc.parent/p
            if planned and p.resolve()==(OUT/'results_verification.json').resolve():continue
            require(p.exists(),'Broken link: '+str(p));count+=1
    return count


def verify():
    spec=importlib.util.spec_from_file_location('discussion_verification',REVIEW/'tools/verify_discussion_materials.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    protected=old.checks()
    data=read(OUT/'descriptive_results.json');report=read(TRIAL/'comparison.json');rows=read(TRIAL/'per_sample.json')['samples']
    for name,h in data['source_files'].items():require(digest(WORK/name)==h,'Descriptive input changed')
    judges=('gpt_sol','deepseek_flash','dual_mean')
    common=[r for r in rows if all(isinstance(r[j]['EAS_arith'],(float,int)) for j in ('human',*judges))]
    require(len(common)==56 and len({r['question_id'] for r in common})==46,'Common cohort changed')
    for judge in judges:
        value=data['common_cohort'][judge];prior=report['common_pair_comparisons'][judge]['EAS_arith']
        require(value['n']==56 and abs(value['mae']-prior['mae'])<1e-10 and abs(value['bias']-prior['bias_AI_minus_human'])<1e-10,'Summary differs from original')
        for threshold,metric in value['within_points'].items():
            count=sum(abs(r[judge]['EAS_arith']-r['human']['EAS_arith'])<=float(threshold)+1e-9 for r in common)
            require(metric==dict(count=count,denominator=56,rate=count/56),'Error interval count differs')
        largest=max((r for r in rows if r['EAS_arith_differences'][judge] is not None),key=lambda r:abs(r['EAS_arith_differences'][judge]))
        require(data['maximum_errors'][judge]==dict(order=largest['order'],question_id=largest['question_id'],difference=largest['EAS_arith_differences'][judge]),'Largest error differs')
        # The builder's deterministic output also binds the descriptive correlations and sensitivity cohort.
        buildspec=importlib.util.spec_from_file_location('descriptive_builder',REVIEW/'tools/build_calibration_results_materials.py')
        builder=importlib.util.module_from_spec(buildspec);buildspec.loader.exec_module(builder)
        require(value==builder.descriptive(common,judge),'Descriptive calculation drift')
        require(data['common_valid_answers_only'][judge]==builder.descriptive([r for r in common if not r['generation_failed']],judge),'Sensitivity calculation drift')
    for judge in judges[:2]:
        point=data['point_agreement'][judge];prior=report['point_agreement'][judge]
        require(point['quadratic_weighted_kappa']==prior['quadratic_kappa'] and point['exact_rate']==prior['exact'] and point['identified_pairs']==prior['n'],'Point agreement differs')
        require(point['within_one_count']==sum(v['count'] for v in prior['confusion'] if abs(v['left']-v['right'])<=.25+1e-9),'Point interval count differs')
    decisions=read(OUT/'decisions.json')
    require(decisions['status']=='not_pursued_per_user_instruction' and not decisions['applied'],'Improvement scope not retired')
    analysis=(OUT/'DISAGREEMENT_ANALYSIS.md').read_text(encoding='utf-8')
    require('拟议处理：' not in analysis and '拟议诊断：' not in analysis,'Proposals remain in active analysis')
    require('DeepSeek −33.33分' in analysis and 'GPT自身最大绝对误差' in analysis,'Maximum-error wording not corrected')
    require(not data['new_model_calls'] and not data['human_labels_questions_Gold_or_live_rules_changed'],'Data scope changed')
    return dict(passed=True,scope='existing_calibration_description_and_thesis_materials_only',
                common_pairs=56,common_question_ids=46,protected_files_unchanged=protected['protected_files_unchanged'],
                original_calibration_verification=protected['original_calibration_verification'],
                scoring_prompt_rules_and_Gold_unchanged=True,new_model_calls=0,improvement_or_recalibration_requested=False,
                maximum_error_correction=dict(overall_single_judge='DeepSeek sample 3, -33.3333333333',GPT_only='sample 37, +31.25'),
                acceptance_locked=True,full_generation_started=False)


def publish(result):
    require(not RECEIPT.exists() and not (OUT/'results_verification.json').exists(),'Already published; use read-only mode')
    baseline=digest(MANIFEST);manifest=read(MANIFEST)
    drift={name:dict(before=h,after=digest(WORK/name) if (WORK/name).is_file() else None) for name,h in manifest['files'].items() if not (WORK/name).is_file() or digest(WORK/name)!=h}
    allowed={rel(REVIEW/'README.md'),rel(TRIAL/'REPORT.md'),*[rel(OUT/n) for n in ('README.md','THESIS_REFERENCE.md','DISAGREEMENT_ANALYSIS.md','IMPROVEMENT_PROPOSAL.md','LAUNCH_CHECKLIST.md','prompt_candidate.txt','decisions.json','evidence.json')],*[rel(REVIEW/'tools'/n) for n in ('build_discussion_materials.py','verify_discussion_materials.py')]}
    require(set(drift)==allowed,'Unrelated manifest drift: '+str(set(drift)^allowed))
    require(all(v['after'] for v in drift.values()),'Unexpected removal')
    result['local_links_verified_before_publication']=check_links(planned=True)
    result['checked_utc']=datetime.now(timezone.utc).isoformat()
    result['derived_source_sha256']=digest(OUT/'descriptive_results.json')
    save(OUT/'results_verification.json',result)
    check_links()
    additions=[OUT/'CALIBRATION_RESULTS.md',OUT/'descriptive_results.json',OUT/'results_verification.json',REVIEW/'tools/build_calibration_results_materials.py',Path(__file__)]
    publication=dict(status='calibration_results_documented_no_improvement_requested',published_utc=result['checked_utc'],previous_manifest_sha256=baseline,
                     existing_file_changes=drift,new_files={rel(p):digest(p) for p in additions},protected_files_unchanged=True,
                     new_model_calls=0,original_scores_unchanged=True,acceptance_locked=True,full_generation_started=False)
    save(RECEIPT,publication)
    manifest['files'].update({name:v['after'] for name,v in drift.items()})
    manifest['files'].update(publication['new_files']);manifest['files'][rel(RECEIPT)]=digest(RECEIPT)
    manifest.update(latest_review_discussion=rel(OUT/'README.md'),latest_review_status='existing_calibration_results_documented_no_improvement_requested',
                    latest_discussion_validation_entry=rel(RECEIPT),latest_results_documentation_verifier=rel(Path(__file__)),updated_utc=result['checked_utc'])
    require(manifest['status']=='ai_calibration_compared_acceptance_locked' and not manifest['acceptance_started'] and not manifest['full_matrix_started'],'Stage changed')
    save(MANIFEST,manifest)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    result=verify()
    if args.publish:publish(result)
    else:
        require(read(OUT/'results_verification.json')['passed'],'Publication verification missing');check_links()
    manifest=read(MANIFEST)
    require(all((WORK/name).is_file() and digest(WORK/name)==h for name,h in manifest['files'].items()),'Current manifest mismatch')
    print(json.dumps(dict(passed=True,common_pairs=56,protected_files_unchanged=result['protected_files_unchanged'],indexed_files=len(manifest['files']),new_model_calls=0,acceptance_locked=True),ensure_ascii=False))


if __name__=='__main__':main()
