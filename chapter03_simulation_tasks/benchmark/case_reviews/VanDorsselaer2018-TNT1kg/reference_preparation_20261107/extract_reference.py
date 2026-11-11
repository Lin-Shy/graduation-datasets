"""Extract the two published numerical peak curves before any new simulation exists."""
import csv
import datetime
import hashlib
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image

R=Path('D:/1/graduation-projects')
B=R/'graduation-datasets/chapter03_simulation_tasks/benchmark'
O=B/'case_reviews/VanDorsselaer2018-TNT1kg/reference_preparation_20261107'
SRC=B/'case_reviews/A02/followup/source_audit_20261106'
ASSET=R/'.codex_tmp/a02-tnt-numerical-lead-20261107/figure5-pressure-original.png'
assert not O.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC/'VanDorsselaer2018_convex.pdf')=='43cd5f7364803026978c8fed6b323210cfba45772d7d677351e5af650de87572'
assert sha(ASSET)=='93bb1a4a505e03ebe04e8591ca916c675f4cff915c1b62f0a2af127da5625d92'
a=np.asarray(Image.open(ASSET).convert('RGB')).astype(float)
red,green,blue=a[:,:,0],a[:,:,1],a[:,:,2]
masks={'OURANOS':(red>190)&(green>70)&(green<210)&(blue<130)&(red>green*1.1),
       'LS-DYNA':(green>65)&(green>red*1.3)&(green>blue*1.3)&(red<160)&(blue<160)}
radii=[.25,.5,.75,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5]
rough_y=[30,86,127,160,215,255,284,304,321,334,345,356,365]
def pressure(y):return 100000*10**(2-(y-20)/133)
rows=[]
for code,mask in masks.items():
 for radius,coarse in zip(radii,rough_y):
  x=round(64+431*radius/6)
  yy,xx=np.where(mask[max(20,coarse-12):min(420,coarse+13),x-1:x+2])
  assert len(yy)>0,(code,radius,x)
  yy=yy+max(20,coarse-12)
  y=float(np.median(yy))
  rows.append({'reference_group':code,'radius_m':radius,'scaled_distance_m_kg_minus1over3':radius,
               'pixel_x_column':x,'nominal_pixel_y':y,'color_pixel_count':len(yy),
               'peak_overpressure_Pa':pressure(y),
               'reading_lower_Pa':pressure(float(max(yy))+2),
               'reading_upper_Pa':pressure(float(min(yy))-2)})
assert len(rows)==26 and all(0<r['reading_lower_Pa']<=r['peak_overpressure_Pa']<=r['reading_upper_Pa'] for r in rows)
O.mkdir(parents=True);(O/'sources').mkdir()
for p in [SRC/'VanDorsselaer2018_convex.pdf',SRC/'VanDorsselaer2018_convex.txt',ASSET]:shutil.copyfile(p,O/'sources'/p.name)
for n in [4,5]:shutil.copyfile(R/f'.codex_tmp/a02-tnt-numerical-lead-20261107/pdf-page-{n:02}.png',O/'sources'/f'pdf-page-{n:02}.png')
with (O/'published_numerical_peaks.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
proof={'at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'classification':'reference_extraction_draft_requires_visual_check_and_condition_closure_not_run_ready',
 'source_PDF_sha256':sha(SRC/'VanDorsselaer2018_convex.pdf'),'source_PDF_page':5,'source_figure':5,
 'source_asset_sha256':sha(ASSET),'source_asset_size_pixels':[515,480],
 'reference_kind':'published_numerical_only_not_experimental',
 'fixed_reference_groups':['OURANOS','LS-DYNA'],'fixed_radius_count':13,'fixed_reference_row_count':26,
 'calibration':{'x_pixels':[64,495],'scaled_distance_values':[0,6],'y_pixels':[20,419],'pressure_bar_values':[100,.1],'y_scale':'log10','one_bar_Pa':100000},
 'extraction':'At each predeclared radius take median curve-color pixel y in expected column +/-1 and visually located local ROI; no simulation outputs used.',
 'reading_interval':'Envelope of selected pixels with additional +/-2 vertical pixels. This is a digitization reading interval, not a statistical confidence interval.',
 'radius_policy':'All thirteen fully visible numerical marker locations0.25 through5.5m are included in each code group. The6m right-edge curves are clipped at the plotting boundary, so no6m marker value is adopted before any simulation exists.',
 'paper_conditions':{'TNT_full_sphere_mass_kg':1,'domain_description_m':[10,10],'reported_square_mesh_spacing_m':.004,'initial_air_pressure_Pa':101325,'sampling':'X-axis in paper axisymmetric diagram','metric':'maximum positive overpressure'},
 'remaining':['Original paper does not report its complete TNT JWL/energy parameter set or ambient density/temperature.','Native source representation, geometry/boundaries, sample mapping and full metric window must be fixed and justified before dispatch.','Visual verification of digitized curves and row values is still required.'],
 'A02_Hexomax_condition_replaced':False,'simulation_started':False,'APE_MAPE_available':False,
 'model_match_approved':False,'Gold_approved':False,'all_rows':rows}
(O/'reference_extraction.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
shutil.copyfile(Path(__file__),O/'extract_reference.py')
print(json.dumps({'output':str(O),'state':proof['classification'],'rows':rows},ensure_ascii=False))
