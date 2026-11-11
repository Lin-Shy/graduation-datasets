"""Fixed-set native peak APE and MAPE; missing required data blocks the mean."""
import argparse, csv, hashlib, json, math
from pathlib import Path

def analyze(package,case):
    spec=json.loads((package/'specification.json').read_text());c=spec['comparison'];lo,hi=c['window_s']
    predictions={};provenance=[]
    for sensor in c['required_sensors']:
        samples={};errors=[]
        for f in sorted((case/'postProcessing'/sensor).glob('*/p')):
            provenance.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
            for line in f.read_text().splitlines():
                if not line.strip() or line.lstrip().startswith('#'):continue
                try:
                    values=[float(x) for x in line.split()]
                    if len(values)!=2 or not all(math.isfinite(x) for x in values):raise ValueError('invalid_one_sensor_row')
                    t,v=values
                    if t in samples and samples[t]!=v:raise ValueError('conflicting_duplicate_time')
                    samples[t]=v
                except ValueError as e:errors.append(str(e))
        in_window=[v for t,v in samples.items() if lo<=t<=hi]
        complete=bool(samples) and min(samples)<=lo+1e-7 and max(samples)>=hi-1e-10 and not errors
        predictions[sensor]={'sample_count':len(samples),'first_time_s':min(samples) if samples else None,
            'last_time_s':max(samples) if samples else None,'complete':complete,'errors':errors,
            'observed_partial_peak_Pa':max(in_window)-c['pressure_baseline_Pa'] if in_window else None,
            'full_peak_Pa':max(in_window)-c['pressure_baseline_Pa'] if complete else None}
    rows=[]
    for r in c['reference_rows']:
        reference=float(r['peak_pa']);assert reference>0
        pred=predictions[r['gauge']]['full_peak_Pa']
        rows.append({'trial':r['trial'],'sensor_id':r['gauge'],'reference_peak_Pa':reference,
                     'simulation_peak_Pa':pred,'APE_percent':100*abs(pred-reference)/reference if pred is not None else None})
    all_complete=all(r['complete'] for r in predictions.values())
    def mape(rr):return math.fsum(r['APE_percent'] for r in rr)/len(rr) if all_complete and rr and all(r['APE_percent'] is not None for r in rr) else None
    per_trial={t:mape([r for r in rows if r['trial']==t]) for t in sorted({r['trial'] for r in rows})}
    receipt=package/'run.json'
    run=json.loads(receipt.read_text()) if receipt.exists() else {}
    healthy_completed=run.get('completed') is True and not run.get('health_failure')
    if not healthy_completed:
        for row in rows:row['APE_percent']=None
    return {'case_id':spec['case_id'],'status':'complete_conditional_pressure_diagnostic' if all_complete and healthy_completed else 'incomplete_or_unhealthy_not_scored',
        'predictions':predictions,'rows':rows,'full_window_all_sensors':all_complete,
        'required_sensors':c['required_sensors'],'fixed_APE_denominator':len(rows),
        'pooled_MAPE_percent':mape(rows) if healthy_completed else None,
        'per_trial_MAPE_percent':per_trial if healthy_completed else {t:None for t in per_trial},
        'model_match_approved':False,'Gold_approved':False,'admission':'requires independent model health and reference matching review',
        'pressure_baseline_Pa':c['pressure_baseline_Pa'],'time_shift_s':0,'source_files':provenance}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',required=True,type=Path);p.add_argument('--case',required=True,type=Path);a=p.parse_args()
    d=analyze(a.package,a.case);out=a.package/'diagnostics';out.mkdir(exist_ok=True)
    (out/'peak_comparison.json').write_text(json.dumps(d,indent=2)+'\n')
    with (out/'peak_comparison.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(d['rows'][0]));w.writeheader();w.writerows(d['rows'])
    print(json.dumps({'status':d['status'],'pooled_MAPE_percent':d['pooled_MAPE_percent']}))
