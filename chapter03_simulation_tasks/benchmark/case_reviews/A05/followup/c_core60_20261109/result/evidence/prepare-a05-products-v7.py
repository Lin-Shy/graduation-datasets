"""Preserve the corrected physical input; try the installed HLLC flux option."""
import hashlib,json,shutil,tarfile
from pathlib import Path
B=Path('D:/1/graduation-projects/graduation-datasets/chapter03_simulation_tasks/benchmark')
P=B/'supplementary_simulations/20261105';old=P/'A05-PETN0344-products-v6';dst=P/'A05-PETN0344-products-v7-hllc'
if dst.exists():
    assert json.loads((dst/'specification.json').read_text(encoding='utf8'))['case_id']==old.name
    assert not (dst/'run.json').exists() and not dst.with_suffix('.tar.gz').exists()
else:shutil.copytree(old,dst)
f=dst/'case/system/fvSchemes';s=f.read_text();assert 'fluxScheme HLL;' in s or 'fluxScheme HLLC;' in s
f.write_text(s.replace('fluxScheme HLL;','fluxScheme HLLC;'))
shutil.copyfile(Path(__file__),dst/Path(__file__).name)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
f=dst/'specification.json';d=json.loads(f.read_text(encoding='utf8'));d['case_id']=dst.name
d['execution_revision']={'previous':old.name,
 'reason':'native nonpositive temperature during early interface transport with HLL; no useful wave arrival or APE exists',
 'change':'only fluxScheme HLL -> installed HLLC; first-order reconstruction/Euler/maxCo0.15 and physical inputs remain fixed',
 'selection_basis':'native contact-wave resolving flux option; test numerical health without consulting reference errors',
 'solver_source_changes':0,'not_proof_of_stability_or_accuracy':True}
d['numerical_configuration']={'flux':'HLLC','reconstruction':'first_order_upwind','integrator':'Euler','maxCo':0.15}
d['input_files']=[{'path':q.relative_to(dst/'case').as_posix(),'sha256':sha(q)} for q in sorted((dst/'case').rglob('*')) if q.is_file()]
d['input_manifest_sha256']=hashlib.sha256(json.dumps(d['input_files'],sort_keys=True).encode()).hexdigest()
d['package_code']=[{'path':q.name,'sha256':sha(q)} for q in sorted(dst.glob('*.py'))]
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with tarfile.open(dst.with_suffix('.tar.gz'),'w:gz') as t:t.add(dst,arcname=dst.name)
print(json.dumps({'case_id':dst.name,'specification_sha256':sha(f),'archive_sha256':sha(dst.with_suffix('.tar.gz'))}))
