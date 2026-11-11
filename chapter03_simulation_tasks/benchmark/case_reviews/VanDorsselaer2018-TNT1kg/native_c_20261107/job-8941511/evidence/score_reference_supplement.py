"""Keep distinct/overlapping reference populations separate; never pool them."""
import argparse,csv,importlib.util,json
from pathlib import Path
loader=importlib.util.spec_from_file_location('fixed_group_core',Path(__file__).with_name('score_reference_core_snapshot.py'))
core=importlib.util.module_from_spec(loader);loader.loader.exec_module(core)
def analyze(package,case):
 spec=json.loads((package/'specification.json').read_text());result=core.analyze(package,case)
 groups=spec['comparison']['MAPE_groups']
 assert {k:sum(r['trial']==k for r in result['rows'])for k in result['per_trial_MAPE_percent']}==groups
 assert len(result['required_sensors'])==spec['comparison']['required_prediction_count']
 for row,reference in zip(result['rows'],spec['comparison']['reference_rows']):
  row['source_trial']=reference.get('source_trial')
  if result['status']=='incomplete_or_unhealthy_not_scored': row['APE_percent']=None
 result['pooled_MAPE_percent']=None
 result['pooled_MAPE_not_defined_reason']='OURANOS and LS-DYNA are distinct published numerical reference groups.'
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,required=True);parser.add_argument('--case',type=Path,required=True);args=parser.parse_args()
 result=analyze(args.package,args.case);out=args.package/'diagnostics';out.mkdir(exist_ok=True)
 (out/'peak_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 with(out/'peak_comparison.csv').open('w',newline='',encoding='utf-8-sig')as f:
  writer=csv.DictWriter(f,fieldnames=list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
 print(json.dumps({'status':result['status'],'per_group_MAPE_percent':result['per_trial_MAPE_percent'],'pooled_MAPE_percent':None}))

 if result['status']=='incomplete_or_unhealthy_not_scored': raise SystemExit(2)
