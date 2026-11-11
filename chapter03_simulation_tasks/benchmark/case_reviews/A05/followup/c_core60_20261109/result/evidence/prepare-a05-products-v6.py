import hashlib,json,shutil,tarfile
from pathlib import Path
B=Path('D:/1/graduation-projects/graduation-datasets/chapter03_simulation_tasks/benchmark');P=B/'supplementary_simulations/20261105';old=P/'A05-PETN0344-products-v5';dst=P/'A05-PETN0344-products-v6'
assert not dst.exists();shutil.copytree(old,dst)
f=dst/'case/0/p';s=f.read_text();assert 'value $internalField;' in s;f.write_text(s.replace('value $internalField;','value uniform 101300;'))
shutil.copyfile(B/'tools/initialize_cartesian_products.py',dst/'initialize_cartesian_products.py')
shutil.copyfile(Path(__file__),dst/Path(__file__).name)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
f=dst/'specification.json';d=json.loads(f.read_text(encoding='utf8'));d['case_id']=dst.name
d['physical_model_revision']=d['execution_revision'];d['execution_revision']={'previous':old.name,
 'reason':'decomposePar IO error: value $internalField expands nonuniform volume list into boundary field after explicit e/T/p initialization',
 'change':'outlet p value uses explicit uniform101300Pa; numerical and physical conditions unchanged; no solver source edit',
 'previous_physical_steps':0}
d['input_files']=[{'path':q.relative_to(dst/'case').as_posix(),'sha256':sha(q)} for q in sorted((dst/'case').rglob('*')) if q.is_file()]
d['input_manifest_sha256']=hashlib.sha256(json.dumps(d['input_files'],sort_keys=True).encode()).hexdigest()
d['package_code']=[{'path':q.name,'sha256':sha(q)} for q in sorted(dst.glob('*.py'))]
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with tarfile.open(dst.with_suffix('.tar.gz'),'w:gz') as t:t.add(dst,arcname=dst.name)
print(dst.name,'boundary IO only; source mass, energy, mesh and numerics unchanged')
