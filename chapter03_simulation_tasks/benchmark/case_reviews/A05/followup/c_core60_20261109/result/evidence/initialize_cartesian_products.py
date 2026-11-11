"""Explicit JWL product e/T/p on fixed, already-initialized Cartesian source."""
import argparse, hashlib, json, math, re
from pathlib import Path
from foam_fields_snapshot import read_field,read_internal_volume_scalar

def initialize(package,case):
    spec=json.loads((package/'specification.json').read_text());s=spec['source'];air=spec['initial_air'];phase=spec['source_phase'];layout={'byte_order':'little','scalar_bits':64,'label_bits':32}
    af=read_field(case/'0'/('alpha.'+phase),layout);values=af['internal']
    # The native mesh writer may use volScalarField or volScalarField::Internal.
    vf=case/'0/V'
    native=vf.read_bytes()[:1500]
    vdata=(read_internal_volume_scalar(vf,layout) if b'volScalarField::Internal' in native else read_field(vf,layout))
    volumes=vdata['internal']
    assert len(values)==len(volumes)==spec['mesh']['cells']
    assert all(0<=a<=1 for a in values) and all(v>0 for v in volumes)
    rho=s['density_kg_m3'];ra=air['rho_kg_m3'];cv=s['products_Cv_J_kgK'];cva=air['Cv_J_kgK'];ta=air['EOS_consistent_T_K'];ga=air['gamma']-1
    j=s['JWL'];om=j['omega'];cold=(j['A_Pa']/j['R1']*math.exp(-j['R1'])+j['B_Pa']/j['R2']*math.exp(-j['R2']))/rho
    pi=j['A_Pa']*(om/j['R1']-1)*math.exp(-j['R1'])+j['B_Pa']*(om/j['R2']-1)*math.exp(-j['R2'])
    energies=[];temperatures=[];pressures=[]
    for a in values:
        ev=a*s['E0_J_m3']+(1-a)*ra*cva*ta
        energies.append(ev/(a*rho+(1-a)*ra))
        temperatures.append((ev-a*rho*cold)/(a*rho*cv+(1-a)*ra*cva))
        pressures.append((ev-a*pi/om)/(a/om+(1-a)/ga))
    assert min(temperatures)>0 and min(energies)>0 and min(pressures)>0
    for name,data in [('e',energies),('T',temperatures),('p',pressures)]:
        template=(package/'case/0'/('alpha.'+phase if name=='e' else name)).read_text()
        if name=='e':
            template=template.replace('object alpha.'+phase+';','object e;').replace('dimensions [0 0 0 0 0 0 0];','dimensions [0 2 -2 0 0 0 0];')
            assert 'object e;' in template and 'dimensions [0 2 -2 0 0 0 0];' in template
        output,n=re.subn(r'internalField\s+uniform\s+[^;]+;',
            'internalField nonuniform List<scalar>\n'+str(len(data))+'\n(\n'+'\n'.join(format(v,'.17g') for v in data)+'\n);',template)
        assert n==1
        if name=='p':output=output.replace('value $internalField;',f'value uniform {air["p_Pa"]:.17g};')
        (case/'0'/name).write_text(output)
    mass=math.fsum(a*v*rho for a,v in zip(values,volumes));assert math.isclose(mass,s['mass_kg'],rel_tol=1e-10)
    excess=math.fsum(a*v*(s['E0_J_m3']-ra*cva*ta) for a,v in zip(values,volumes))
    expected=(s['E0_J_m3']-ra*cva*ta)*s['mass_kg']/rho
    assert math.isclose(excess,expected,rel_tol=1e-10)
    record={'cell_count':len(values),'native_source_mass_kg':mass,'source_cells':sum(a>0 for a in values),
      'minimum_T_K':min(temperatures),'maximum_T_K':max(temperatures),'maximum_p_Pa':max(pressures),
      'actual_excess_energy_J':excess,'analytic_excess_energy_J':expected,'energy_convention':s['energy_convention'],
      'hashes':{n:hashlib.sha256((case/'0'/n).read_bytes()).hexdigest() for n in ['e','T','p','alpha.'+phase,'V']},
      'initialization_checks_only_not_full_run_validation':True}
    (package/'source_initialization.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--case',type=Path,required=True);a=p.parse_args();initialize(a.package,a.case)
