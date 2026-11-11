"""Initialize a sphere on actual native wedge cell volumes, no pressure fitting."""
import argparse, bisect, hashlib, json, math, re
from pathlib import Path
from foam_mesh_snapshot import read_mesh

def initialize(package,case):
    spec=json.loads((package/'specification.json').read_text())
    mesh=read_mesh(case/'constant/polyMesh',{'byte_order':'little','scalar_bits':64,'label_bits':32})
    assert mesh['cell_count'] == spec['geometry']['cells']
    s=spec['source'];xc=s['centre_m'][0];radius=s['radius_m'];rho=s['density_kg_m3']
    theta=math.radians(spec['geometry']['angular_wedge_degrees']/2)
    xn=spec['geometry']['axial_cell_edges_m']
    rn=spec['geometry']['radial_cell_edges_m']
    rc=[2/3*math.cos(theta)*(h**3-l**3)/(h*h-l*l) for l,h in zip(rn,rn[1:])]
    alpha=[0.]*mesh['cell_count']
    for k,(centre,v) in enumerate(zip(mesh['cell_centres_m'],mesh['cell_volumes_m3'])):
        x,y,_=centre
        if abs(x-xc)>radius+.006 or y>radius+.006:continue
        ix=bisect.bisect_right(xn,x)-1
        ir=min(range(len(rc)),key=lambda j:abs(rc[j]-y))
        lo,hi=xn[ix:ix+2];rl,rh=rn[ir:ir+2]
        assert math.isclose(v,(hi-lo)*math.sin(theta)*math.cos(theta)*(rh*rh-rl*rl),rel_tol=1e-7)
        vol=0.;nx=64;nt=32
        for i in range(nx):
            xx=lo+(i+.5)*(hi-lo)/nx
            cap=radius**2-(xx-xc)**2
            if cap<=0:continue
            for j in range(nt):
                phi=-theta+(j+.5)*2*theta/nt
                fac=math.cos(theta)/math.cos(phi)
                radial=max(0.,min((rh*fac)**2,cap)-(rl*fac)**2)
                vol+=.5*radial*(hi-lo)/nx*2*theta/nt
        alpha[k]=min(1.,max(0.,vol/v))
    target=s['mass_kg']/rho*spec['geometry']['angular_wedge_degrees']/360
    before=math.fsum(a*v for a,v in zip(alpha,mesh['cell_volumes_m3']))
    correction=target-before
    partial=[k for k,a in enumerate(alpha) if 0<a<1]
    room=math.fsum(((1-alpha[k]) if correction>0 else alpha[k])*mesh['cell_volumes_m3'][k] for k in partial)
    assert room>abs(correction) and partial,'insufficient bounded correction capacity'
    for k in partial:alpha[k]+=correction*((1-alpha[k]) if correction>0 else alpha[k])/room
    actual=math.fsum(a*v*rho for a,v in zip(alpha,mesh['cell_volumes_m3']))*360/spec['geometry']['angular_wedge_degrees']
    assert all(0<=a<=1 for a in alpha) and math.isclose(actual,s['mass_kg'],rel_tol=1e-12)
    f=case/'0/alpha.c4'
    f.write_text('FoamFile { version 2.0; format ascii; class volScalarField; object alpha.c4; }\n'
      'dimensions [0 0 0 0 0 0 0];\ninternalField nonuniform List<scalar>\n'+str(len(alpha))+'\n(\n'+
      '\n'.join(format(a,'.17g') for a in alpha)+'\n);\n'
      'boundaryField { walls { type zeroGradient; } outlet { type zeroGradient; } front { type wedge; } back { type wedge; } }\n')
    r={'method':'actual_native_wedge_mesh_64x32_midpoint_quadrature_bounded_mass_correction',
       'cell_count':len(alpha),'source_cells':sum(a>0 for a in alpha),'partial_cells':len(partial),
       'uncorrected_wedge_source_volume_m3':before,'target_wedge_source_volume_m3':target,
       'correction_relative':correction/target,'actual_scaled_FV_mass_kg':actual,
       'wedge_mass_kg':actual*spec['geometry']['angular_wedge_degrees']/360,
       'alpha_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
       'model_initialization_only_not_source_validation':True}
    if spec.get('source_model')=='instantaneous_products':
        # Native JWL E(rho)=cold energy and p=omega*rho*e-Pi(rho).
        # twoPhaseFluidBlastThermo uses common mixture e and pressure weights
        # Xi_i=alpha_i/(Gamma_i-1). Supply e explicitly, as supported by its
        # initializeFields(), to avoid inferring cold product energy from p0.
        j=s['JWL'];omega=j['omega'];cv=1400.;ra=spec['initial_air']['rho_kg_m3']
        cva=spec['initial_air']['Cv_J_kgK'];ta=spec['initial_air']['T_K'];ga=.4
        cold=(j['A_Pa']/j['R1']*math.exp(-j['R1'])+j['B_Pa']/j['R2']*math.exp(-j['R2']))/rho
        pi=j['A_Pa']*(omega/j['R1']-1)*math.exp(-j['R1'])+j['B_Pa']*(omega/j['R2']-1)*math.exp(-j['R2'])
        energies=[];temperatures=[];pressures=[];target=[]
        for a in alpha:
            density=a*rho+(1-a)*ra
            ev=a*s['E0_J_m3']+(1-a)*ra*cva*ta
            e=ev/density
            t=(ev-a*rho*cold)/(a*rho*cv+(1-a)*ra*cva)
            pressure=(ev-a*pi/omega)/(a/omega+(1-a)/ga)
            assert e>0 and t>0 and pressure>0
            energies.append(e);temperatures.append(t);pressures.append(pressure);target.append(ev)
        boundary='boundaryField { walls { type zeroGradient; } outlet { type zeroGradient; } front { type wedge; } back { type wedge; } }\n'
        for name,values,dimensions in [('e',energies,'[0 2 -2 0 0 0 0]'),('T',temperatures,'[0 0 0 1 0 0 0]'),('p',pressures,'[1 -1 -2 0 0 0 0]')]:
            path=case/'0'/name
            if path.exists():
                text=path.read_text();text=re.sub(r'internalField\s+uniform\s+[^;]+;',
                    'internalField nonuniform List<scalar>\n'+str(len(values))+'\n(\n'+'\n'.join(format(v,'.17g') for v in values)+'\n);',text)
            else:text=f'FoamFile {{ version 2.0; format ascii; class volScalarField; object {name}; }}\ndimensions {dimensions};\ninternalField nonuniform List<scalar>\n'+str(len(values))+'\n(\n'+'\n'.join(format(v,'.17g') for v in values)+'\n);\n'+boundary
            path.write_text(text)
        excess=math.fsum((ev-ra*cva*ta)*v for ev,v in zip(target,mesh['cell_volumes_m3']))*360/spec['geometry']['angular_wedge_degrees']
        expected=(s['E0_J_m3']-ra*cva*ta)*s['mass_kg']/rho
        assert math.isclose(excess,expected,rel_tol=1e-10)
        r['initial_products']={'energy_convention':s['energy_convention'],'cold_energy_J_kg':cold,
            'minimum_T_K':min(temperatures),'maximum_T_K':max(temperatures),
            'maximum_p_Pa':max(pressures),'actual_scaled_excess_energy_J':excess,
            'analytic_excess_energy_J':expected,'explicit_e_input':True,
            'field_hashes':{n:hashlib.sha256((case/'0'/n).read_bytes()).hexdigest() for n in ['e','T','p']}}
    (package/'source_initialization.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--case',type=Path,required=True);a=p.parse_args();initialize(a.package,a.case)
