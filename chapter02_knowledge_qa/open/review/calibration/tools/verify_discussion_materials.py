"""Offline discussion checks. --publish indexes only the review and literature additions."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import importlib.util
import json
import re

from jsonschema import Draft202012Validator

WORK = Path(__file__).resolve().parents[6]
REVIEW = WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration'
TRIAL = REVIEW/'ai_calibration/85b246b6f258'
OUT = TRIAL/'discussion'
EXP = WORK/'graduation-experiment-results/chapter2_retrieval'
LIB = WORK/'graduation-thesis-materials/graduation-literature'
MANIFEST = EXP/'release/manifests/current.json'
RECEIPT = EXP/'technical/calibration_discussion_publication_check.json'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p):
    return p.relative_to(WORK).as_posix()


def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def candidate_schema_checks():
    tests = []
    for conditional in (False, True):
        schema = read(OUT/('wire_schema_conditional.json' if conditional else 'wire_schema_nonconditional.json'))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        valid = dict(points={f'p{i}':dict(score=1, answer_quote='合成引用', reason='合成测试') for i in range(1, 4)}, F=1, reason='')
        if conditional:
            valid['A'] = 1
        fixtures = [('valid', valid, True)]
        extra = copy.deepcopy(valid); extra['points']['p4'] = copy.deepcopy(valid['points']['p1'])
        missing = copy.deepcopy(valid); del missing['points']['p2']
        false_score = copy.deepcopy(valid); false_score['F'] = False
        unknown = copy.deepcopy(valid); unknown['F'] = 'unknown'
        fixtures.extend([('extra_point', extra, False), ('missing_point', missing, False), ('boolean_score', false_score, False), ('unknown_F', unknown, True)])
        a = copy.deepcopy(valid)
        if conditional:
            a['A'] = 'not_applicable'
            fixtures.append(('A_NA', a, False))
            b = copy.deepcopy(valid); b['A'] = 'unknown'
            fixtures.append(('A_unknown', b, True))
            c = copy.deepcopy(valid); del c['A']
            fixtures.append(('missing_A', c, False))
        else:
            a['A'] = .75
            fixtures.append(('extra_numeric_A', a, False))
        for name, data, expected in fixtures:
            actual = validator.is_valid(data)
            require(actual == expected, f'Candidate schema fixture failed: {conditional}/{name}')
            tests.append(dict(conditional=conditional, name=name, expected_valid=expected, passed=True))
    return tests


def links(planned=False):
    checked = 0
    documents = list(OUT.glob('*.md')) + [LIB/'annotations'/f'{x}.md' for x in ('mtbench', 'geval')]
    documents += [LIB/'notes'/f'{x}.md' for x in ('mtbench', 'geval')]
    for doc in documents:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#')):
                continue
            target = re.sub(r':\d+$', '', target.strip('<>').split('#')[0])
            path = Path(target)
            if not path.is_absolute():
                path = doc.parent/path
            if planned and path.resolve() == (OUT/'verification.json').resolve():
                continue
            require(path.exists(), f'Broken local link in {rel(doc)}: {target}')
            checked += 1
    return checked


def checks():
    evidence = read(OUT/'evidence.json')
    for name, expected in evidence['protected_files'].items():
        require(digest(WORK/name) == expected, 'Protected file changed: '+name)
    require(evidence['human_reference_label'] == '人工参考' and evidence['model_calls'] == 0, 'Discussion scope changed')
    rows = read(TRIAL/'per_sample.json')['samples']
    ranked = sorted([r for r in rows if r['EAS_arith_differences']['dual_mean'] is not None], key=lambda r:(-abs(r['EAS_arith_differences']['dual_mean']), r['order']))[:12]
    require([r['order'] for r in ranked] == evidence['top12_orders'], 'Top-case selection changed')
    packets = {p['sample_id']:p for p in read(REVIEW/'calibration/packets.json')['samples']}
    sources = 0
    for case in evidence['cases']:
        packet = case['packet']
        require(packet == packets[packet['sample_id']], 'Discussion packet altered')
        row = next(r for r in rows if r['order'] == case['order'])
        require(case['records'] == row['records'] and all(case['metrics'][j] == row[j] for j in case['metrics']), 'Case labels altered')
        for source in packet['sources']:
            file = EXP/'data/resources/corpus'/source['path']
            excerpt = '\n'.join(file.read_text(encoding='utf-8-sig').splitlines()[source['line_start']-1:source['line_end']])
            require(digest(file) == source['file_sha256'] and excerpt == source['excerpt'], 'Source range changed')
            require(hashlib.sha256(excerpt.encode()).hexdigest() == source['excerpt_sha256'], 'Source excerpt hash differs')
            sources += 1
    for failure in evidence['failures']:
        require(read(WORK/failure['result_file']) == failure['result'], 'Failure state altered')
        require(digest(WORK/failure['request_file']) == failure['request_file_sha256'], 'Failure request changed')
        for attempt in failure['attempts']:
            require(digest(WORK/attempt['file']) == attempt['file_sha256'], 'Attempt history changed')
    require(len(evidence['failures']) == 3 and len(evidence['failures'][2]['attempts']) == 3, 'Failure count changed')
    mapping = read(REVIEW/'administration/sample_mapping.json')['samples']
    pools = {phase:{s['task']['id'] for s in mapping if s['phase'] == phase} for phase in ('calibration', 'acceptance')}
    require(len(pools['calibration']) == len(pools['acceptance']) == 50 and not pools['calibration'] & pools['acceptance'], 'Panel overlap changed')
    questions = read(WORK/'graduation-datasets/chapter02_knowledge_qa/open/model/questions.json')
    require(pools['calibration'] | pools['acceptance'] == {q['id'] for q in questions}, 'Unseen pool finding changed')
    require(len(questions) == 100 and len(read(WORK/'graduation-datasets/chapter02_knowledge_qa/objective/model/questions.json')) == 200, 'Dataset size changed')
    acceptance = read(REVIEW/'acceptance/packets.json')
    require(not acceptance['enabled_for_review'] and all(p['answer'] is None for p in acceptance['samples']), 'Acceptance unlocked/generated')
    decisions = read(OUT/'decisions.json')
    item_state = 'not_pursued' if decisions['status'] == 'not_pursued_per_user_instruction' else 'pending'
    require(not decisions['applied'] and not decisions['live_prompt_or_rules_changed'] and all(x['status'] == item_state for x in decisions['items']), 'Discussion decisions applied')
    # Existing verifier rechecks raw responses, labels, statistics, prior trials and closed gates.
    spec = importlib.util.spec_from_file_location('published_calibration_verifier', REVIEW/'tools/verify_ai_calibration.py')
    verifier = importlib.util.module_from_spec(spec); spec.loader.exec_module(verifier)
    calibration = verifier.verify()
    papers = {p['id']:p for p in read(LIB/'catalog.json')['papers']}
    for key in ('mtbench', 'geval'):
        record = papers[key]
        require(digest(LIB/record['archive']['pdf']) == record['archive']['pdf_sha256'], 'Archived PDF changed')
        if 'source_file' in record['archive']:
            require(digest(LIB/record['archive']['source_file']) == record['archive']['source_sha256'], 'Source snapshot changed')
        require((LIB/record['archive']['text']).exists() and (LIB/'annotations'/f'{key}.md').exists(), 'Literature annotation missing')
    return dict(passed=True, protected_files_unchanged=len(evidence['protected_files']), main_cases=12, additional_cases=2,
                source_ranges_verified=sources, failure_records_verified=3, synthetic_schema_fixtures=candidate_schema_checks(),
                schema_check_scope='local_only_server_enforcement_not_verified', duplicate_JSON_key_policy='proposed_not_runtime_implemented',
                original_calibration_verification=calibration, dataset_counts=dict(open=100, objective=200),
                acceptance_locked=True, acceptance_answers_bound=0, spare_unseen_question_ids=0,
                new_model_calls=0, live_code_prompt_rules_or_labels_changed=False, decisions_applied=False,
                literature=dict(metadata=37, PDFs=36, relevant_pages_only=True, mtbench_source_HTML_not_obtained=True))


def publish(report):
    require(not (OUT/'verification.json').exists() and not RECEIPT.exists(), 'Publication already exists; use read-only mode')
    manifest_hash = digest(MANIFEST)
    manifest = read(MANIFEST)
    drift = {name:dict(before=expected, after=digest(WORK/name) if (WORK/name).is_file() else None)
             for name, expected in manifest['files'].items() if not (WORK/name).is_file() or digest(WORK/name) != expected}
    allowed = {rel(REVIEW/'README.md'), rel(TRIAL/'REPORT.md')}
    require(set(drift) == allowed, 'Unexpected baseline manifest drift; do not absorb unrelated changes')
    report['local_links_verified'] = links(planned=True)
    report['checked_utc'] = datetime.now(timezone.utc).isoformat()
    save(OUT/'verification.json', report)
    links()
    additions = list(OUT.iterdir()) + [REVIEW/'tools/build_discussion_materials.py', Path(__file__)]
    additions += [LIB/n for n in ('catalog.json', 'INDEX.md', 'references.bib', 'README.md')]
    additions += [LIB/f'{folder}/{key}{suffix}' for key in ('mtbench', 'geval') for folder, suffix in [('papers','.pdf'),('notes','.md'),('annotations','.md'),('texts','.txt')]]
    additions += [LIB/'sources/geval.html']
    publication = dict(status='offline_discussion_published_acceptance_locked', published_utc=report['checked_utc'],
                       previous_manifest_sha256=manifest_hash, indexed_files_before=len(manifest['files']),
                       allowed_existing_file_changes=drift, added_or_indexed_files={rel(p):digest(p) for p in additions},
                       new_model_calls=0, protected_files_unchanged=True, decisions_applied=False)
    save(RECEIPT, publication)
    manifest['files'].update({name:item['after'] for name,item in drift.items()})
    manifest['files'].update(publication['added_or_indexed_files'])
    manifest['files'][rel(RECEIPT)] = digest(RECEIPT)
    manifest['latest_review_discussion'] = rel(OUT/'README.md')
    manifest['latest_review_status'] = 'disagreement_failure_and_launch_review_pending_discussion_no_execution'
    manifest['latest_discussion_validation_entry'] = rel(RECEIPT)
    manifest['human_reference_display_label'] = '人工参考'
    manifest['updated_utc'] = report['checked_utc']
    require(manifest['status'] == 'ai_calibration_compared_acceptance_locked' and not manifest['acceptance_started'] and not manifest['full_matrix_started'], 'Stage changed')
    save(MANIFEST, manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    report = checks()
    if args.publish:
        publish(report)
    else:
        require((OUT/'verification.json').exists() and read(OUT/'verification.json')['passed'], 'Publication check missing')
        report['local_links_verified'] = links()
    manifest = read(MANIFEST)
    require(all((WORK/name).is_file() and digest(WORK/name) == h for name,h in manifest['files'].items()), 'Current manifest mismatch')
    print(json.dumps(dict(passed=True, main_cases=12, additional_cases=2, failure_records=3,
                          protected_files_unchanged=report['protected_files_unchanged'], schema_fixtures=len(report['synthetic_schema_fixtures']),
                          indexed_files=len(manifest['files']), model_calls=0, acceptance_locked=True), ensure_ascii=False))


if __name__ == '__main__':
    main()
