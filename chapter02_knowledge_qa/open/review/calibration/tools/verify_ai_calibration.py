"""Read-only verification of the published AI calibration, human labels and gates."""
from pathlib import Path
import json
import sys

WORK = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(WORK/'PrincipiaBlastFoam-DSH/experiments/chapter2'))
import judge_calibration as jc
from judge_contract import joint_metrics, calculate, schema
from judge_api_adapter import build, parse
from models import sha


def verify():
    # Completed calibration is verified against its executed snapshot. Later
    # formal orchestration changes do not rewrite the calibrated implementation.
    ph, protocol, out, packets = jc.verify(current=False)
    jc.require(not jc.read(jc.AUTH)['authorized'], 'Judge queue still authorized')
    folder = jc.REVIEW/'ai_calibration'/ph[:12]
    report = jc.read(folder/'comparison.json')
    document = jc.read(folder/'per_sample.json')
    jc.require(report['protocol_sha256'] == document['protocol_sha256'] == ph, 'Report protocol mismatch')
    rows = document['samples']
    jc.require(len(rows) == 60 and {x['sample_id'] for x in rows} == set(protocol['sample_ids']), 'Incomplete cohort')
    labels = {r['sample_id']: r['record'] for r in jc.read(jc.LABELS)['labels']}
    validation = jc.human.validate_labels(jc.LABELS, 'calibration')
    for name, h in report['files'].items():
        jc.require(sha((jc.EXPERIMENT/name).read_bytes()) == h, 'Raw artifact changed: '+name)
    for row in rows:
        s = row['sample_id']; p = packets[s]; ids = [x['criterion_id'] for x in p['criteria']]
        jc.require(row['records']['human'] == labels[s], 'Human reference altered')
        jc.require(row['human'] == joint_metrics(labels[s], ids, p['conditional'], p['generation_failed']), 'Human metric drift')
        for j in jc.JUDGES:
            result = jc.read(out/j/s/'result.json')
            if result['status'] == 'complete':
                expected = joint_metrics(result['record'], ids, p['conditional'], p['generation_failed'])
                jc.require(row['records'][j] == result['record'], 'AI record changed')
            else:
                expected = calculate([None]*len(ids), None, None if p['conditional'] else 'not_applicable', p['conditional'])
                jc.require(row['records'][j] is None, 'Invented label for rejected output')
            jc.require(row[j] == expected, 'AI metric changed')
            if not p['generation_failed']:
                q = jc.read(out/j/s/'requests/000.json')
                profile = jc.calibration_profile(j, protocol['judge_output_token_cap'])
                body = build(profile, p, 'joint', jc.prompt_text(), schema())['body']
                jc.require(q['request'] == body, 'Changed request or leaked reference label')
                if result['status'] == 'complete':
                    jc.require(parse(profile, q['raw_response'], p, 'joint')['record'] == result['record'], 'Raw/score mismatch')
        jc.require(row['dual_mean'] == jc.mean_metrics(row[jc.JUDGES[0]], row[jc.JUDGES[1]]), 'Mean not exactly two judges')
    for j in (*jc.JUDGES, 'dual_mean'):
        for metric in ('EAS_arith','EAS_geo','K','F','A','Strict'):
            jc.require(report['comparisons'][j][metric] == jc.comparison(rows, j, metric), 'Comparison statistic drift')
            common = [row for row in rows if all(jc.score_known(row[k][metric]) for k in ('human', *jc.JUDGES))]
            jc.require(report['common_pair_comparisons'][j][metric] == jc.comparison(common,j,metric), 'Common-subset statistic drift')
    resumed = 0
    for path in (jc.EXPERIMENT/'release/frozen/judge_queue_recovery').glob('*/manifest.json'):
        recovery = jc.read(path)
        if recovery['base_protocol_sha256'] != ph: continue
        jc.require(sha((path.parent/'00.py').read_bytes()) == recovery['source_sha256'], 'Queue recovery source drift')
        jc.require(not jc.read(path.parent/'completion.json')['authorized'], 'Queue recovery still open')
        for item in recovery['selected']:
            original = jc.EXPERIMENT/item['result']
            prior = original.with_name('result_before_queue_resume.json')
            qprior = original.parent/'requests/request_before_queue_resume.json'
            jc.require(sha(prior.read_bytes()) == item['result_sha256'] and sha(qprior.read_bytes()) == item['request_sha256'], 'Queued state not preserved')
            old = jc.read(qprior); current = jc.read(original.parent/'requests/000.json')
            jc.require(old['status'] == 'deployment_halted' and old['transport_attempts'] == 0 and old['request'] == current['request'], 'Repeated or altered previously transmitted request')
            resumed += 1
    # Each previous execution remains bound, including unsuccessful sandbox attempts.
    previous = protocol.get('previous_trial')
    prior_files = 0
    while previous:
        for name, h in previous['files'].items():
            jc.require(sha((jc.EXPERIMENT/name).read_bytes()) == h, 'Previous trial changed')
            prior_files += 1
        frozen = jc.read(jc.EXPERIMENT/'release/frozen/judge_calibration'/previous['protocol_sha256']/'manifest.json')
        older = frozen['protocol']
        previous = older.get('previous_trial') or older.get('previous_infrastructure_trial')
    confirmation = jc.read(jc.human.DATASET/'objective/review/reference_answer_confirmation.json')
    for name, key in [('objective/model/questions.json','questions_sha256'), ('objective/scoring/annotations.json','annotations_sha256')]:
        jc.require(sha((jc.human.DATASET/name).read_bytes()) == confirmation[key], 'Approved objective data changed')
    # Legacy calibration dispatch stays closed; formal dispatch has a separate
    # authorization and protocol, so do not report its state from the old gate.
    workflow_path = jc.EXPERIMENT/'release/planning/review_workflow.json'
    workflow = jc.read(workflow_path) if workflow_path.exists() else {}
    formal_auth_path = jc.EXPERIMENT/'release/planning/formal_execution.json'
    formal_auth = jc.read(formal_auth_path) if formal_auth_path.exists() else {}
    formal_pointer_path = jc.EXPERIMENT/'release/planning/formal_experiment.json'
    formal_pointer = jc.read(formal_pointer_path) if formal_pointer_path.exists() else {}
    formal_root = jc.EXPERIMENT/formal_pointer.get('output_root', 'formal/not_prepared')
    formal_started = (formal_root/'supervisor.json').exists()
    return dict(passed=True, protocol_sha256=ph, human_labels=validation['complete'],
                human_unknown_items=sum(x['unknown_items'] for x in validation['metrics']),
                statuses=report['statuses'], raw_files=len(report['files']), previous_trial_files=prior_files, never_transmitted_queue_records_resumed=resumed,
                objective_reference_answers_approved=200, answers_questions_and_Gold_unchanged=True,
                acceptance_cancelled=workflow.get('acceptance_cancelled', False),
                acceptance_locked=not workflow.get('acceptance_cancelled', False),
                calibration_dispatch_closed=True, full_generation_started=formal_started,
                formal_protocol_sha256=formal_pointer.get('protocol_sha256'),
                all_dispatch_closed=not formal_auth.get('authorized', False))


if __name__ == '__main__': print(json.dumps(verify(), ensure_ascii=False))
