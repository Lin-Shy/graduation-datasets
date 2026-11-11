"""Evaluate fixed first-peak references from healthy full-window native traces."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean


def read_probe(case, gauge, end, peak_end, baseline):
    sources, samples, errors = [], {}, []
    for path in sorted((case / 'postProcessing' / gauge).glob('*/p')):
        data = path.read_bytes()
        sources.append({'path': str(path.relative_to(case)), 'sha256': hashlib.sha256(data).hexdigest()})
        for line in data.decode('ascii').splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            try:
                t, p = map(float, line.split())
                if not math.isfinite(t) or not math.isfinite(p) or (t in samples and p != samples[t]):
                    raise ValueError('nonfinite_or_conflicting_record')
                samples[t] = p
            except ValueError as error:
                errors.append(str(error))
    full = bool(samples) and min(samples) <= 1e-7 and max(samples) >= end - 1e-10 and not errors
    gate = [(t, p - baseline) for t, p in sorted(samples.items()) if 0 <= t <= peak_end]
    peak_time, peak = max(gate, key=lambda row: row[1]) if gate else (None, None)
    resolved = len(gate) > 2 and peak > 0 and gate[0][0] < peak_time < gate[-1][0]
    return {'sample_count': len(samples), 'first_time_s': min(samples) if samples else None,
            'last_time_s': max(samples) if samples else None, 'complete': full, 'errors': errors,
            'peak_gate_end_s': peak_end, 'gate_peak_Pa': peak, 'gate_peak_time_s': peak_time,
            'primary_peak_resolved': resolved, 'files': sources}


def analyze(package, case):
    spec = json.loads((package / 'specification.json').read_bytes())
    run = json.loads((package / 'run.json').read_bytes())
    comparison = spec['comparison']
    baseline = comparison['pressure_baseline_Pa']
    start, end = comparison['window_s']
    assert start == 0
    predictions = {gauge: read_probe(case, gauge, end, comparison['peak_gate_end_s'][gauge], baseline)
                   for gauge in comparison['required_sensors']}
    healthy = run.get('completed') is True and not run.get('health_failure')
    full = all(row['complete'] for row in predictions.values())
    scoreable = healthy and full and all(row['primary_peak_resolved'] for row in predictions.values())
    rows = []
    for ref in comparison['reference_rows']:
        reference = ref['peak_pa']
        prediction = predictions[ref['gauge']]
        assert reference > 0
        peak = prediction['gate_peak_Pa'] if healthy and prediction['complete'] and prediction['primary_peak_resolved'] else None
        rows.append({'group': ref['group'], 'source_trial': ref['source_trial'], 'gauge': ref['gauge'],
                     'reference_peak_Pa': reference, 'simulation_peak_Pa': peak,
                     'APE_percent': 100 * abs(peak - reference) / reference if peak is not None else None})
    assert {group: sum(row['group'] == group for row in rows) for group in comparison['MAPE_groups']} == comparison['MAPE_groups']
    mape = {group: mean(row['APE_percent'] for row in rows if row['group'] == group) if scoreable else None
            for group in comparison['MAPE_groups']}
    return {'case_id': spec['case_id'], 'solver_completed_and_passed_log_checks': healthy,
            'full_window_all_sensors': full, 'full_reference_MAPE_available': scoreable,
            'peak_gate_failure_gauges': [gauge for gauge, row in predictions.items() if not row['primary_peak_resolved']],
            'predictions': predictions, 'fixed_denominators': comparison['MAPE_groups'], 'MAPE_percent': mape,
            'rows': rows, 'formal_DSH_score': False, 'model_match_approved': False, 'Gold_approved': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--case', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.package, args.case)
    out = args.package / 'diagnostics'
    out.mkdir(exist_ok=True)
    (out / 'peak_comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    with (out / 'peak_comparison.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result['rows'][0]))
        writer.writeheader()
        writer.writerows(result['rows'])
    print(json.dumps({k: result[k] for k in ('full_window_all_sensors', 'full_reference_MAPE_available', 'MAPE_percent')}))
    raise SystemExit(0 if result['solver_completed_and_passed_log_checks'] and result['full_window_all_sensors'] else 2)
