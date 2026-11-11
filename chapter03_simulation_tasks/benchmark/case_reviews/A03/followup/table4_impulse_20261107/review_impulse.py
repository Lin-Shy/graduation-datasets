"""Add the PIPE91 impulse comparison to the archived A03 run."""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys


OUT = Path(__file__).resolve().parent
CASE = OUT.parents[1]
sys.path.insert(0, str(CASE.parent / 'Kristoffersen2024-Pipe99-400g'))
from review_impulse import END_S, publish, read, sha, source_rows


GAUGES = ('Pi02', 'Pi03', 'Pi04')
TABLE_4_PEAKS = {'T1': (1947, 1002, 1020), 'T2': (1935, 1184, 1008)}
TRIALS = {'T1': '1', 'T2': '4'}


def main():
    archive = read(CASE / 'archive_manifest.json')
    hashes = {item['archive_path']: item['sha256'] for item in archive['files']}
    run_path = 'simulation/A03-run.json'
    trace_path = 'simulation/A03/postProcessing/probes/0/p'
    reference_path = 'reviewed_package/peak_comparison_diagnostic.csv'
    for name in (run_path, trace_path, reference_path):
        assert sha(CASE / name) == hashes[name]
    run = read(CASE / run_path)
    assert run['solver_completed'] and run['solver_end_marker']
    assert run['last_log_time_s'] == run['target_time_s'] == float(END_S)
    assert all(command['exit_code'] == 0 and not command['timed_out'] for command in run['commands'])
    assert next(row for row in run['output_files'] if row['path'] == 'postProcessing/probes/0/p')['sha256'] == hashes[trace_path]
    with (CASE / reference_path).open(encoding='utf-8-sig', newline='') as source:
        peaks = {(row['trial'], row['experiment_sensor']): Decimal(row['reference_table1_kpa'])
                 for row in csv.DictReader(source)}
    for trial, archived_trial in TRIALS.items():
        rounded = tuple(peaks[archived_trial, gauge].to_integral_value(rounding=ROUND_HALF_UP)
                        for gauge in GAUGES)
        assert rounded == TABLE_4_PEAKS[trial]

    traces = {gauge: [] for gauge in GAUGES}
    with (CASE / trace_path).open(encoding='ascii') as source:
        assert [next(source).strip() for _ in GAUGES] == [
            f'# Probe {index} ({position} 0.0999048221582 0)' for index, position in enumerate(('0.6', '1.3', '1.4'))
        ]
        for line in source:
            if not line.strip() or line.startswith('#'):
                continue
            time, *pressures = map(Decimal, line.split())
            assert time.is_finite()
            for gauge, pressure in zip(GAUGES, pressures, strict=True):
                points = traces[gauge]
                assert pressure.is_finite() and pressure > 0 and (not points or time > points[-1][0])
                points.append((time, pressure - Decimal('101300')))
    assert all(len(points) == 6015 and points[0][0] == 0 and points[-1][0] == END_S
               for points in traces.values())
    number, _, conditions, _ = source_rows('pipe91')
    assert number == '4' and conditions['diameter_mm'] == 200 and conditions['charge_g'] == [20, 2]
    pdf = next((CASE / 'sources').glob('Kristoffersen*2024*.pdf'))
    assert sha(pdf) == hashes[pdf.relative_to(CASE).as_posix()]
    provenance = {
        'case_id': 'A03', 'case_key': 'pipe91', 'archived_run_receipt_sha256': hashes[run_path],
        'native_pressure_sha256': hashes[trace_path], 'reference_pdf_sha256': sha(pdf),
        'published_trial_to_archived_trial': TRIALS,
    }
    result = publish(OUT, traces, 'pipe91', 'A03 已归档原生仿真', provenance,
                     {'experimental_repeats': 6, 'published_EPX': 3},
                     '../../reviewed_package/a03-complete-review-standalone.html',
                     '表 4 的 T1 和 T2 分别对应原始试次 1 和 4。原始试次 2 保留在已审核的峰值资料中。')
    print(result['MAPE_percent'])


if __name__ == '__main__':
    main()
