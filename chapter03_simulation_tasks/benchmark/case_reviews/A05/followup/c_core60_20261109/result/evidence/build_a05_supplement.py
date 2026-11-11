"""Build a versioned A05 paper-model reproduction, never overwrite the old task/Gold.

PETN1770 is the published numerical approximation, not exact experimental m/46.
Mesh/EOS choices are fixed before any new result is inspected.
"""
import argparse
import hashlib
import itertools
import json
import math
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.conservative_source import sphere_fraction
OUT=ROOT/'supplementary_simulations/20261105/A05-paper-PETN-v1'
SOURCE_MASS_KG=.4


def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def vec(v):return '('+' '.join(f'{x:.14g}' for x in v)+')'
def header(obj,kind='dictionary'):
    return f'FoamFile {{ version 2.0; format ascii; class {kind}; object {obj}; }}\n'


def main():
    if (OUT/'case').exists():raise SystemExit('Existing version refused. Create a new version for changes.')
    t=json.loads((ROOT/'tasks/A05/task.yaml').read_text(encoding='utf8'))['agent_input']['target_conditions']
    ref=json.loads((ROOT/'case_reviews/A05/evidence/comparison_and_findings.json').read_text(encoding='utf8'))
    c=OUT/'case'
    for folder in ['0','system','constant']:(c/folder).mkdir(parents=True,exist_ok=True)
    a=[-16.1,-8.05,-3.45,-1.15,-.12,-.06,0,.06,.12,1.15,3.45,8.05,16.1]
    axes=[a,a,[0,.08,.14,.2,.26,.32,1.15,2.3,8.05,16.1]]
    ns=[]
    for q,ax in enumerate(axes):
        ns.append([max(1,math.ceil(round((hi-lo)/(.02 if (q<2 and abs((lo+hi)/2)<.121) or (q==2 and .079<(lo+hi)/2<.321) else .46 if abs((lo+hi)/2)>8.05 else .23),10))) for lo,hi in zip(ax,ax[1:])])
    vertices=list(itertools.product(*axes));ids={v:i for i,v in enumerate(vertices)}
    def occupied(mid):
        for box in t['boxes']:
            if all(lo-1e-10<x<hi+1e-10 for x,lo,hi in zip(mid,box['min_m'],box['max_m'])):return box['id']
    shape=[len(ax)-1 for ax in axes]
    boxes={idx:occupied([(axes[q][idx[q]]+axes[q][idx[q]+1])/2 for q in range(3)]) for idx in itertools.product(*[range(n) for n in shape])}
    boundary={'ground':[],'outlet':[]}
    faces=[(0,-1,[0,4,7,3]),(0,1,[1,2,6,5]),(1,-1,[0,1,5,4]),(1,1,[3,7,6,2]),(2,-1,[0,3,2,1]),(2,1,[4,5,6,7])]
    block_lines=[];cell_count=0
    for idx,solid in boxes.items():
        if solid:continue
        lo=[axes[q][idx[q]] for q in range(3)];hi=[axes[q][idx[q]+1] for q in range(3)]
        vv=[(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),(lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]
        vi=[ids[v] for v in vv];nn=[ns[q][idx[q]] for q in range(3)];cell_count+=math.prod(nn)
        block_lines.append('hex ('+' '.join(map(str,vi))+') ('+' '.join(map(str,nn))+') simpleGrading (1 1 1)')
        for q,d,face in faces:
            neighbor=list(idx);neighbor[q]+=d;neighbor=tuple(neighbor)
            if not 0<=neighbor[q]<shape[q]:patch='ground' if q==2 and d==-1 else 'outlet'
            elif boxes[neighbor]:patch=boxes[neighbor]+'_'+'xyz'[q]+('plus' if d==-1 else 'minus')
            else:continue
            boundary.setdefault(patch,[]).append('('+' '.join(str(vi[v]) for v in face)+')')
    mesh=header('blockMeshDict')+'convertToMeters 1;\nvertices (\n'+'\n'.join(vec(v) for v in vertices)+'\n);\nblocks (\n'+'\n'.join(block_lines)+'\n);\nedges ();\nboundary (\n'
    for name,ff in boundary.items():mesh+=name+' { type '+('patch' if name=='outlet' else 'wall')+'; faces (\n'+'\n'.join(ff)+'\n); }\n'
    mesh+=');\nmergePatchPairs ();\n';(c/'system/blockMeshDict').write_text(mesh)
    # Actual subcell lattice of the multi-block mesh, not nominal sourceToCell mass.
    expanded=[]
    for q,ax in enumerate(axes):
        ex=[]
        for j,n in enumerate(ns[q]):ex.extend(ax[j]+(ax[j+1]-ax[j])*i/n for i in range(n))
        ex.append(ax[-1]);expanded.append(ex)
    rho=1770.;mass=SOURCE_MASS_KG;radius=(3*mass/(4*math.pi*rho))**(1/3);centre=[0,0,.2]
    near=[]
    for q,ax in enumerate(expanded):near.append([(lo,hi) for lo,hi in zip(ax,ax[1:]) if hi>centre[q]-radius and lo<centre[q]+radius])
    source=[]
    for xyz in itertools.product(*near):
        lo=[x[0] for x in xyz];hi=[x[1] for x in xyz]
        alpha=sphere_fraction(lo,hi,centre,radius)
        if alpha:source.append([lo,hi,alpha,math.prod(b-a for a,b in xyz)])
    target=mass/rho;initial=sum(r[2]*r[3] for r in source);delta=target-initial
    capacity=sum((1-r[2] if delta>0 else r[2])*r[3] for r in source if r[2]<1)
    assert capacity>=abs(delta)
    for r in source:
        if r[2]<1:r[2]+=delta*(1-r[2] if delta>0 else r[2])/capacity
        assert 0<=r[2]<=1
    actual=sum(r[2]*r[3]*rho for r in source);assert math.isclose(actual,mass,rel_tol=1e-12)
    regions=[]
    for lo,hi,alpha,vol in source:
        shrinklo=[a+(b-a)*1e-6 for a,b in zip(lo,hi)];shrinkhi=[b-(b-a)*1e-6 for a,b in zip(lo,hi)]
        regions.append('boxToCell { box '+vec(shrinklo)+' '+vec(shrinkhi)+f'; fieldValues (volScalarFieldValue alpha.petn {alpha:.17g}); }}')
    (c/'system/setFieldsDict').write_text(header('setFieldsDict')+'defaultFieldValues (volScalarFieldValue alpha.petn 0);\nregions (\n'+'\n'.join(regions)+'\n);\n')
    phase=(ROOT/'references/construction/20261022-conservative/A01/constant/phaseProperties').read_text()
    for old,new in [('c4','petn'),('1601','1770'),('609.77e9','617.1e9'),('12.95e9','16.93e9'),('4.50','4.40'),('R2        1.4','R2        1.2'),('9.0e9','10.10e9'),('7850','8300'),('0.0 0.0 0.3','0.0 0.0 0.2'),('101298','101300'),('815;','1000;'),('1400;','1000;')]:phase=phase.replace(old,new)
    (c/'constant/phaseProperties').write_text(phase)
    p0=101300.;rhoair=1.226;temperature=p0/(.4*718*rhoair)
    for field,dimensions,val,kind in [('p','[1 -1 -2 0 0 0 0]','101300','volScalarField'),('T','[0 0 0 1 0 0 0]',f'{temperature:.14g}','volScalarField'),('rho.air','[1 -3 0 0 0 0 0]','1.226','volScalarField'),('rho.petn','[1 -3 0 0 0 0 0]','1770','volScalarField'),('alpha.petn','[0 0 0 0 0 0 0]','0','volScalarField'),('U','[0 1 -1 0 0 0 0]','(0 0 0)','volVectorField')]:
        text=header(field,kind)+f'dimensions {dimensions};\ninternalField uniform {val};\nboundaryField {{\n'
        for patch in boundary:
            bc='type zeroGradient;'
            if field=='U':bc='type pressureInletOutletVelocity; value $internalField;' if patch=='outlet' else 'type slip;'
            if field=='p' and patch=='outlet':bc='type pressureWaveTransmissive; value $internalField;'
            text+=patch+' { '+bc+' }\n'
        (c/'0'/field).write_text(text+'}\n')
    old=ROOT/'references/construction/20261022-conservative/A01'
    for f in ['fvSchemes','fvSolution']:(c/'system'/f).write_text((old/'system'/f).read_text().replace('c4','petn'))
    shutil.copyfile(old/'constant/dynamicMeshDict',c/'constant/dynamicMeshDict')
    funcs=(ROOT/'references/review/round6/surface-mapping-v2/A05-surface-labels/system/controlDict').read_text().split('functions {',1)[1]
    for r in ref['rows']:assert r['patch'] in boundary
    control=header('controlDict')+'application blastFoam;\nstartFrom startTime; startTime 0; stopAt endTime; endTime 0.05;\ndeltaT 1e-8; adjustTimeStep yes; maxCo 0.3; maxDeltaT 1e-5;\nwriteControl adjustableRunTime; writeInterval 0.005; purgeWrite 0;\nwriteFormat binary; writePrecision 12; writeCompression off; timePrecision 14; runTimeModifiable false;\nfunctions {\n'+funcs
    (c/'system/controlDict').write_text(control)
    (c/'system/decomposeParDict').write_text(header('decomposeParDict')+'numberOfSubdomains 8; method scotch;\n')
    # Source/pressure metadata locked before the first run.
    model={'case_id':OUT.name,'task_id':'A05','date':'2026-11-05','status':'built_locally_remote_validation_pending',
      'authority':'user explicitly authorized supplement simulations and SSH standard case construction',
      'tier':'published_paper_model_approximation_compared_to_experiment_not_exact_m46_replication',
      'source':{'mass_kg':mass,'density_kg_m3':rho,'radius_m':radius,'centre_m':centre,'initial_actual_mass_kg':actual,'source_cells':len(source),'E0_J_m3':10.10e9,'vDet_m_s':8300,
        'JWL':{'A_Pa':617.1e9,'B_Pa':16.93e9,'R1':4.4,'R2':1.2,'omega':.25},'JWL_source':'Kim2003 PDFpage4/printed244/Table2 PETNrow'},
      'mesh':{'domain_m':[[-16.1,-16.1,0],[16.1,16.1,16.1]],'cells':cell_count,'blocks':len(block_lines),'source_spacing_m':.02,'street_spacing_target_m':.23,'far_spacing_target_m':.46,'actual_geometry_conformal':True,'native_checkMesh':'pending_remote'},
      'initial_air':{'p_Pa':p0,'rho_kg_m3':rhoair,'Cv_J_kgK':718,'gamma':1.4,'EOS_consistent_T_K':temperature},
      'predeclared_approximations':['Experimental m46 is not purePETN; use published paper PETN1770 approximation, not experimental material equivalence.',
        f'Spherical charge at paper centre, {mass}kg total purePETN model; experimental material equivalence unapproved.',
        'Reactant Murnaghan parameters inherited structural model; Cv reactants/products1000 J/kg/K is an explicit modeling assumption, not a measured m46 value.',
        'Linear activation8300m/s; retains JWL products throughout; does not implement AUTODYN JWL-to-idealGas or explosive-to-air remapping.',
        'Ambient Cv718 uses existing blastFoam configuration; effective temperature derived consistently from paper p/rho/gamma.',
        'Mesh and domain are initial standard-case settings; convergence and boundary independence are not yet established.',
        'Known common activation/thermal model risk remains. Stop and record numerical failure; no solver repair.'],
      'comparison':{'reference':'MSB450/TableB.2/shot10/location4','required_prediction_count':25,'fixed_peak_APE_count':24,'excluded_unreliable_reference':['BA3C'],'pressure':'native absolute static pressure minus101300Pa','window_s':[0,.05],'peak_method':'native all-sample maximum over complete window','mape_thresholds_percent':[15,30],'arrival_accuracy':'not_scored_without_matched_time_origin_and_definition'},
      'reference_rows':ref['rows'],'agent_score':None,'validated_Gold':False,'human_admission':False,
      'runtime':{'mpi_ranks':8,'wall_budget_s':86400,'memory_budget_GiB':6,'disk_reserve_GiB':10,'parallel_cfd_jobs':1},
      'input_files':[{'path':p.relative_to(c).as_posix(),'sha256':sha(p)} for p in sorted(c.rglob('*')) if p.is_file()]}
    model['input_manifest_sha256']=hashlib.sha256(json.dumps(model['input_files'],sort_keys=True).encode()).hexdigest()
    save(OUT/'specification.json',model)
    for src in [ROOT/'sources/downloaded/johansson-pdf-20261022.txt',ROOT/'references/experiments/round5-johansson-msb450-shot10/source-and-applicability.json',ROOT/'case_reviews/A05/evidence/comparison_and_findings.json']:
        dst=OUT/'sources'/src.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(src,dst)
    print(json.dumps({'case':str(OUT),'cells':cell_count,'blocks':len(block_lines),'source_mass_kg':actual,'source_cells':len(source),'remote_solver_runs':0}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case-id',default=OUT.name);parser.add_argument('--mass-kg',type=float,default=.4);args=parser.parse_args()
    assert args.case_id.replace('-','').replace('.','').isalnum() and args.mass_kg>0
    OUT=OUT.parent/args.case_id;SOURCE_MASS_KG=args.mass_kg;main()
