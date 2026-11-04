"""Explicit, audited replacement of the unscored original calibration cohort.

No generation, retry, scoring, sample replacement, or generic binding override.
Run only after the complete new run has an integrity receipt and dispatch closes.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, json, sys
from evidence_paths import material

WORK = Path(__file__).resolve().parents[6]
ROOT = WORK / 'graduation-experiment-results/chapter2_retrieval'
REVIEW = Path(__file__).resolve().parents[1]
OLD = 'cadc6b76ac42cb356d9fb5072f5862598a5bc4e04019d45257b630bf21fadcfc'
NEW = 'd658134e6df5053454ed78893523eb25320d8354dec558f689d4dacc4524ccf2'
def read(p): return json.loads(p.read_text('utf-8'))
def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(v): return (json.dumps(v, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
def require(ok, msg):
    if not ok: raise ValueError(msg)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--allow-unresolved',action='store_true');args=parser.parse_args()
    gate = read(ROOT / 'release/planning/execution.json')
    require(not gate['formal_generation_authorized'] and not gate['allowed_stages'], 'Close dispatch before binding')
    manifest = read(ROOT / 'release/manifests/calibration_generation.json')
    check = read(REVIEW / 'administration/generation_check.json')
    require(manifest['protocol_sha256'] == check['protocol_sha256'] == NEW and check['passed'] and check['closed_tasks'] == 60, 'New uniform generation is not verified')
    require(args.allow_unresolved or check.get('ready_for_complete_calibration'), 'Unresolved results require explicit partial-material binding')
    tasks = {t['task_id']: t for t in manifest['selected_tasks']}
    prior_manifest = read(material('graduation-experiment-results/chapter2_retrieval/release/manifests/calibration_generation.json', OLD))
    require(tasks == {t['task_id']: t for t in prior_manifest['selected_tasks']}, 'Original task selection changed')
    sys.path.insert(0, str(WORK / 'PrincipiaBlastFoam-DSH/experiments/chapter2'))
    from human_review import verify_plan
    verify_plan()
    path = REVIEW / 'calibration/packets.json'
    prior = material(path.relative_to(WORK).as_posix(), OLD)
    require(path.read_bytes() == prior.read_bytes(), 'Only the preserved original, unscored cohort can be switched')
    labels = {}
    for phase in ('calibration', 'acceptance'):
        lp = REVIEW / phase / 'blank_labels.json'
        require(lp.read_bytes() == material(lp.relative_to(WORK).as_posix(), OLD).read_bytes(), 'Human label template drift')
        require(all(l['record']['status'] == 'pending' and l['reviewer'] is None for l in read(lp)['labels']), 'Existing human labels must not be discarded')
        labels[phase] = sha(lp.read_bytes())
    acceptance = REVIEW / 'acceptance/packets.json'
    require(acceptance.read_bytes() == material(acceptance.relative_to(WORK).as_posix(), OLD).read_bytes(), 'Acceptance material drift')
    mapping_path = REVIEW / 'administration/sample_mapping.json'
    mapping = {s['sample_id']: s['task'] for s in read(mapping_path)['samples'] if s['phase'] == 'calibration'}
    packet = copy.deepcopy(read(prior)); require(len(packet['samples']) == len(mapping) == 60, 'Expected original 60 packets')
    transitions = []
    for sample in packet['samples']:
        task = mapping[sample['sample_id']]
        require(tasks[task['task_id']] == task, 'Sample task mismatch')
        rp = ROOT / 'runs' / NEW / task['model'] / task['task_id'] / 'result.json'
        result = read(rp)
        require(result['protocol_sha256'] == NEW and result['task'] == task, 'Result identity mismatch')
        require(check['files'][rp.relative_to(ROOT).as_posix()] == sha(rp.read_bytes()), 'Unsealed result')
        unresolved = result['status'] in {'outcome_unknown','http_result_unknown','deployment_halted','not_dispatched_model_halted'}
        failed = not unresolved and result['status'] != 'answered'
        answer = None if unresolved else '[未生成有效回答：' + result['status'] + ']' if failed else result['answer']
        ah = None if answer is None else sha(answer.encode('utf-8'))
        transitions.append(dict(sample_id=sample['sample_id'], task_id=task['task_id'], previous_answer_sha256=sample['answer_sha256'], answer_sha256=ah, status=result['status'], result=rp.relative_to(WORK).as_posix(), result_sha256=sha(rp.read_bytes())))
        sample.update(answer=answer, answer_sha256=ah, generation_failed=failed, binding_status='awaiting_resolution' if unresolved else 'bound', generation_status=result['status'], references=result.get('references', []), references_delivered=result.get('references_delivered'))
    packet['generation_protocol_sha256'] = NEW
    new_bytes = encoded(packet)
    receipt = dict(schema='calibration_cohort_transition_v1', completed_utc=datetime.now(timezone.utc).isoformat(), previous_protocol_sha256=OLD, protocol_sha256=NEW, previous_packet_sha256=sha(prior.read_bytes()), packet_sha256=sha(new_bytes), previous_material_manifest='release/frozen/' + OLD + '/calibration_materials/manifest.json', sample_mapping_sha256=sha(mapping_path.read_bytes()), label_template_sha256=labels, acceptance_packet_sha256=sha(acceptance.read_bytes()), human_labels_completed=0, task_selection_unchanged=True, gold_and_questions_unchanged=True, answers_repaired=False, bound_answers=check['answered'], unresolved_packets=check.get('unknown',0)+check.get('interrupted',0), ready_for_complete_calibration=check.get('ready_for_complete_calibration'), transitions=transitions)
    target = REVIEW / 'administration/cohort_transition.json'
    require(not target.exists(), 'Do not overwrite a cohort transition')
    temp = path.with_suffix('.new'); temp.write_bytes(new_bytes)
    with target.open('xb') as out: out.write(encoded(receipt))
    temp.replace(path)
    require(sha(path.read_bytes()) == receipt['packet_sha256'], 'Packet replacement incomplete')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'transitions'}, ensure_ascii=False))

if __name__ == '__main__': main()
