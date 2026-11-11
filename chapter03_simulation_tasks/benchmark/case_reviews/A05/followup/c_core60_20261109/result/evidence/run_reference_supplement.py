"""One immutable, resource-bounded original-reference diagnostic attempt."""
import argparse, hashlib, json, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path

def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)
def run(package):
    assert os.name=='posix' and os.getuid()!=0
    spec=json.loads((package/'specification.json').read_text());source=package/'case'
    for group,root in [('input_files',source),('package_code',package),('source_files',package)]:
        for r in spec[group]:assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
    assert shutil.disk_usage(package).free>spec['runtime']['minimum_free_disk_GiB']*1024**3
    case=package/'run-case';receipt=package/'run.json'
    assert not case.exists() and not receipt.exists(),'Existing attempt refused'
    shutil.copytree(source,case)
    record={'case_id':spec['case_id'],'pid':os.getpid(),'uid':os.getuid(),'started_at':time.time(),
      'specification_sha256':hashlib.sha256((package/'specification.json').read_bytes()).hexdigest(),
      'commands':[],'completed':False,'health_failure':None}
    save(receipt,record);deadline=time.monotonic()+spec['runtime']['wall_budget_s']
    initialization=([['setFields'],['postProcess','-func','writeCellVolumes','-time','0'],
          [sys.executable,str(package/'initialize_cartesian_products.py'),'--package',str(package),'--case',str(case)]]
        if spec.get('initializer')=='cartesian_products' else
        [[sys.executable,str(package/'initialize_erdc_source.py'),'--package',str(package),'--case',str(case)]])
    plans=[['blockMesh'],*initialization,['checkMesh'],['decomposePar'],
           ['mpirun','-np',str(spec['runtime']['mpi_ranks']),'blastFoam','-parallel']]
    try:
        for i,argv in enumerate(plans):
            log=package/f'{i}-{Path(argv[0]).name}.log'
            item={'argv':argv,'started_at':time.time(),'log':log.name};record['commands'].append(item);save(receipt,record)
            with log.open('wb') as out:
                child=subprocess.Popen(argv,cwd=case,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
                offset=0;tail=''
                while child.poll() is None:
                    time.sleep(.5)
                    with log.open('rb') as f:f.seek(offset);new=f.read();offset=f.tell()
                    tail=(tail+new.decode(errors='replace'))[-20000:]
                    times=re.findall(r'^Time = ([-+\deE.]+)',tail,re.M)
                    if times:record['observed_time_s']=float(times[-1])
                    if 'blastFoam' in argv:
                        temps=[float(t) for t in re.findall(r'min\(T\):\s*([-+\deE.]+)',tail)]
                        if any(t<=0 for t in temps):record['health_failure']='nonpositive_temperature_native_log'
                        elif 'FOAM FATAL IO ERROR' in tail:record['health_failure']='input_dictionary_error'
                        elif re.search(r'FOAM FATAL|\bnan\b|^\s*(?:\[\d+\]\s*)?Floating point exception(?:\s|$)',tail,re.I|re.M):
                            record['health_failure']='fatal_native_log'
                    if shutil.disk_usage(package).free<2*1024**3:record['stop_reason']='disk_reserve'
                    if time.monotonic()>deadline:record['stop_reason']='wall_budget'
                    if record['health_failure'] or record.get('stop_reason'):
                        os.killpg(child.pid,signal.SIGTERM);break
                    if times:save(receipt,record)
                try:code=child.wait(timeout=20)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
            text=log.read_text(errors='replace');item.update(exit_code=code,finished_at=time.time(),sha256=hashlib.sha256(log.read_bytes()).hexdigest());save(receipt,record)
            if code or record['health_failure'] or record.get('stop_reason'):break
            if argv==['checkMesh'] and 'Mesh OK' not in text:record['stop_reason']='mesh_not_OK';break
        else:
            times=[float(x) for x in re.findall(r'^Time = ([-+\deE.]+)',text,re.M)]
            if any(float(t)<=0 for t in re.findall(r'min\(T\):\s*([-+\deE.]+)',text)):record['health_failure']='nonpositive_temperature_native_log'
            record['completed']=bool(re.search(r'^End\s*$',text,re.M)) and bool(times) and max(times)>=spec['comparison']['window_s'][1]-1e-10 and not record['health_failure']
    finally:
        record['finished_at']=time.time();save(receipt,record)
        subprocess.run([sys.executable,str(package/'score_reference_supplement.py'),'--package',str(package),'--case',str(case)],check=True)
    return record['completed']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);a=p.parse_args();raise SystemExit(0 if run(a.package.resolve()) else 2)
