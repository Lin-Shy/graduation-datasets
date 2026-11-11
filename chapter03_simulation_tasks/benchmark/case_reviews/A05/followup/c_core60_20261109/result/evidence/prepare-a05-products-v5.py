import datetime,hashlib,importlib.util,json,shutil,tarfile
from pathlib import Path
B=Path('D:/1/graduation-projects/graduation-datasets/chapter03_simulation_tasks/benchmark');P=B/'supplementary_simulations/20261105';name='A05-PETN0344-products-v5';dst=P/name
sp=importlib.util.spec_from_file_location('builder_a05',B/'tools/build_a05_supplement.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
m.OUT=dst;m.SOURCE_MASS_KG=.344;m.main();c=dst/'case'
f=c/'constant/phaseProperties';old=f.read_text();air=old[old.index('\nair\n{'):]
f.write_text('''FoamFile { version 2.0; format ascii; class dictionary; object phaseProperties; }
phases (petn air); radiationModel none;
petn { type basic;
 thermoType { transport const; thermo eConst; equationOfState JWL; }
 equationOfState { rho0 1770; A 617.1e9; B 16.93e9; R1 4.4; R2 1.2; omega 0.25; e0 0; }
 specie { molWeight 55; } transport { mu 0; Pr 1; }
 thermodynamics { Cv 1000; Hf 0; }
 residualRho 1e-6; residualAlpha 1e-10;
}
'''+air)
f=c/'system/controlDict';f.write_text(f.read_text().replace('maxCo 0.3;','maxCo 0.15;'))
scheme=(P/'ERDC-SL99-5-0p11kg-v3-products/case/system/fvSchemes').read_text().replace('c4','petn')
(c/'system/fvSchemes').write_text(scheme)
(c/'system/decomposeParDict').write_text('FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }\nnumberOfSubdomains 4; method scotch;\n')
d=json.loads((dst/'specification.json').read_text(encoding='utf8'))
d['source_model']='instantaneous_products';d['initializer']='cartesian_products';d['source_phase']='petn'
d['source']['products_Cv_J_kgK']=1000
d['source']['energy_convention']='E0 is total JWL product internal energy per initial explosive volume; no additional activation heat'
d['runtime']={'mpi_ranks':4,'wall_budget_s':86400,'memory_limit_GiB':4,'CPU_quota_percent':400,'minimum_free_disk_GiB':6}
d['comparison'].update(pressure_baseline_Pa=101300,required_sensors=[r['sensor_id'] for r in d['reference_rows']],
 reference_rows=[{'trial':'10','gauge':r['sensor_id'],'peak_pa':r['reference_peak_kpa']*1000} for r in d['reference_rows'] if r['source_valid']],
 feature='maximum native static wall gauge pressure over full50ms',
 repeat_policy='fixed24 reliable references; all25 predictions required',
 excluded_before_run={'BA3C':'author marks reference unreliable; prediction remains required'})
d['execution_revision']={'previous':'A05-paper-PETN-upwind-v4','mass_correction':'original report PDF33 explicitly uses0.86*0.4=0.344kg purePETN; old0.4kg purePETN input is mismatched and retained only as diagnostic',
 'physical_model_change':'independent instantaneous fully detonated products at t0, explicit native e/T/p; does not claim AUTODYN conversion/remap equivalence',
 'numerics':'existing HLL/first_order_upwind/Euler/maxCo0.15; no APE used in selection','source_or_installed_library_repair':False}
d['predeclared_approximations']=[
 'Mass0.344kg purePETN follows the published numerical surrogate for experimental0.4kg m46, not exact experimental material equivalence.',
 'Fully detonated products at t0 replace finite radial burn of about4.3us; E0 interpreted as total product energy.',
 'PETN product Cv1000 is a declared modeling assumption, not a measured m46 value.',
 'JWL retained throughout: no original AUTODYN JWL-to-idealGas or explosive-to-air remapping.',
 'Mesh and domain inherited; convergence and boundary independence not established.',
 'All25 native histories required; missing or unhealthy run cannot supply official24-point MAPE.']
correction={'recorded_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task_id':'A05',
 'source':str(B/'sources/round5/johansson-msb450-2012.pdf'),'source_sha256':hashlib.sha256((B/'sources/round5/johansson-msb450-2012.pdf').read_bytes()).hexdigest(),
 'PDF_page_1based':33,'published_numerical_mass_kg':.344,'calculation':'0.86*0.4',
 'prior_0p4kg_purePETN_versions':'mass mismatched to original paper numerical condition; all retained as failed exploratory diagnostics; not matching reproductions',
 'new_version':name,'source_mass_corrected':True,'remaining_model_match_approved':False,'Gold_approved':False}
(P/'A05_model_identity_correction.json').write_text(json.dumps(correction,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for src in [B/'sources/round5/johansson-msb450-2012.pdf',B/'sources/round5/johansson-msb450-2012.txt',P/'sources/Kim2003_PETN_binder.pdf',P/'sources/Kim2003_receipt.json']:
    shutil.copyfile(src,dst/'sources'/src.name)
for file in ['run_reference_supplement.py','score_reference_supplement.py','initialize_cartesian_products.py','build_a05_supplement.py']:
    shutil.copyfile(B/'tools'/file,dst/file)
shutil.copyfile(B/'evaluator/foam_fields.py',dst/'foam_fields_snapshot.py')
shutil.copyfile(Path(__file__),dst/Path(__file__).name)
(dst/'start.sh').write_text('#!/bin/bash\nsource /data/OpenFOAM/OpenFOAM-9/etc/bashrc\nsource /data/OpenFOAM/blastfoam/etc/bashrc\nset -e\ncd "$(dirname "$0")"\nexec /data/miniconda3/bin/python3 run_reference_supplement.py --package "$PWD"\n',newline='\n')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
d['input_files']=[{'path':f.relative_to(c).as_posix(),'sha256':sha(f)} for f in sorted(c.rglob('*')) if f.is_file()]
d['input_manifest_sha256']=hashlib.sha256(json.dumps(d['input_files'],sort_keys=True).encode()).hexdigest()
d['package_code']=[{'path':f.name,'sha256':sha(f)} for f in sorted(dst.glob('*.py'))]
d['source_files']=[{'path':f.relative_to(dst).as_posix(),'sha256':sha(f)} for f in sorted((dst/'sources').glob('*'))]
d['model_match_approved']=False;d['Gold_approved']=False
(dst/'specification.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with tarfile.open(dst.with_suffix('.tar.gz'),'w:gz') as t:t.add(dst,arcname=name)
print('mass corrected to0.344kg; independent product approximation;25required/24compared')
