"""Reject an unreliable draft reading and retain a non-runnable numerical-source lead."""
import copy,csv,datetime,hashlib,html,json,shutil
from pathlib import Path
ROOT=Path('D:/1/graduation-projects');B=ROOT/'graduation-datasets/chapter03_simulation_tasks/benchmark'
O=B/'case_reviews/VanDorsselaer2018-TNT1kg/reference_preparation_20261107'
L=ROOT/'graduation-thesis-materials/graduation-literature';P=B/'supplementary_simulations/20261105';E=P/'runtime_execution'
X=ROOT/'graduation-experiment-results/chapter3_end_to_end_evaluation/supplement_20261105'
ID='van-dorsselaer-convex-blast-2018'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert not (O/'quality_review.json').exists()
draft=read(O/'reference_extraction.json');assert len(draft['all_rows'])==26
bad=next(r for r in draft['all_rows'] if r['reference_group']=='OURANOS' and r['radius_m']==.25)
assert bad['color_pixel_count']==1
shutil.copyfile(O/'reference_extraction.json',O/'reference_extraction_initial.json')
source_csv=O/'published_numerical_peaks.csv';target_csv=O/'DRAFT_NOT_APPROVED_numerical_peak_readings.csv'
assert source_csv.resolve().is_relative_to(O.resolve()) and target_csv.resolve().is_relative_to(O.resolve()) and not target_csv.exists()
source_csv.rename(target_csv)
for key in ['reference_groups','radius_count','reference_row_count']:
 draft['proposed_'+key]=draft.pop('fixed_'+key)
draft.update(comparison_set_frozen=False,all_rows_reference_approved=False,simulation_dispatch_allowed=False,
             draft_readings_csv=target_csv.name,unreliable_candidate_rows=[{'reference_group':'OURANOS','radius_m':.25,'reason':'Only one color pixel found; no reliable local marker-center reading.'}])
save(O/'reference_extraction.json',draft)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
review={'at_UTC':now,'classification':'published_numerical_source_lead_not_comparison_ready',
 'source_scope':'Paper preliminary1kg full-sphere TNT free-field calculation; explicitly not an experimental test. It is distinct from A02 Hexomax.',
 'source_identity':{'PDF_page':4,'conditions':'10m by10m domain,4mm square mesh, air101325Pa,2D axisymmetric MMALE, X-axis sampling.'},
 'source_plot':{'PDF_page':5,'figure':5,'ordinate':'maximum positive overpressure, bar, logarithmic','abscissa':'distance from charge center, m/kg^(1/3)'},
 'all26_candidate_readings_preserved_as_draft':True,'trusted_or_frozen_reference_rows':0,
 'unreliable_first_OURANOS_reading':{'radius_m':.25,'color_pixels':1,'adopted':False},
 'remaining':['Complete original TNT JWL/energy and ambient density/temperature not reported. External TNT parameters would be explicit model assumptions, not verified exact reproduction.','Define native geometry, boundary placement, source representation, axis mapping and full peak window before dispatch.','Visually verify every adopted digitized reference and reading interval; fix reference groups and denominator before any predictions.'],
 'original_paper_mesh_versus_native_mesh_not_silently_equated':True,
 'original_Hexomax_best2of3_reference_selection_not_adopted':True,
 'simulation_dispatch_allowed':False,'native_input_package_created':False,'APE_MAPE_available':False,
 'A02_replaced':False,'human_admission_or_Gold_changed':False}
save(O/'quality_review.json',review)
table=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['reference_group'],r['radius_m'],f"{r['peak_overpressure_Pa']/1000:.4g}",r['color_pixel_count'],'不可靠，禁止采用' if r['reference_group']=='OURANOS' and r['radius_m']==.25 else '候选草稿，未批准'])+'</tr>' for r in draft['all_rows'])
(O/'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1kg TNT论文数值线索：未具备运行条件</title><style>body{font:17px/1.65 system-ui;max-width:1100px;margin:30px auto;padding:0 20px;color:#17304a}.note{padding:18px;background:#fff2d8;border-left:5px solid #bf8426}table{border-collapse:collapse;width:100%}td,th{padding:8px;border:1px solid #bdcbd8;text-align:left}img{max-width:100%;height:auto}a{color:#065ea7}</style><h1>2018论文1kg TNT自由场：数值参考线索</h1><p class="note">不是实验数据，不替代A02。条件与读数尚未闭合，未建原生输入、未启动仿真、没有APE/MAPE。下表全部为待核对草稿，不能直接用于评分。</p><p><a href="sources/VanDorsselaer2018_convex.pdf">完整原始PDF</a> · <a href="sources/VanDorsselaer2018_convex.txt">全文</a> · <a href="quality_review.json">未具备运行条件的依据</a> · <a href="DRAFT_NOT_APPROVED_numerical_peak_readings.csv">全部候选读数草稿</a></p><p>原文PDF4说明：1kg完整TNT球、10×10m域、4mm方形网格、2D轴对称MMALE、空气初压101325Pa、沿X轴取峰值超压；本次没有原文完整TNT JWL／能量参数，也没有原生几何、源表示、轴映射和全窗口契约。图5两条数值曲线分别来自OURANOS和LS-DYNA。</p><p>原始内嵌图仅515×480像素。OURANOS的0.25m候选读数只找到1个颜色像素，不能认定是可信标记中心；其余读数也尚未逐项批准。保留全部草稿以便复核，不据此派发或产生误差成绩。</p><img src="sources/figure5-pressure-original.png" alt="图5原始内嵌压力图"><table><tr><th>数值来源</th><th>半径m</th><th>候选读数kPa，未批准</th><th>颜色像素数</th><th>状态</th></tr>'''+table+'''</table><h2>原文方法与完整图页</h2><img src="sources/pdf-page-04.png" alt="原文PDF4"><img src="sources/pdf-page-05.png" alt="原文PDF5"></html>''',encoding='utf8')
source=O/'sources/VanDorsselaer2018_convex.pdf';source_text=O/'sources/VanDorsselaer2018_convex.txt'
assert sha(source)=='43cd5f7364803026978c8fed6b323210cfba45772d7d677351e5af650de87572'
cat=read(L/'catalog.json');old=copy.deepcopy(cat['papers']);assert len(old)==44 and all(r['id']!=ID for r in old)
old_notes={p:sha(p) for p in (L/'notes').glob('*.md')};index_before=(L/'INDEX.md').read_bytes();bib_before=(L/'references.bib').read_bytes()
pdf=L/f'papers/{ID}.pdf';txt=L/f'texts/{ID}.txt';assert not pdf.exists() and not txt.exists()
shutil.copyfile(source,pdf);shutil.copyfile(source_text,txt)
source_record=L/f'sources/{ID}-archive_20261107.json'
assert not source_record.exists()
save(source_record,{'at_UTC':now,'acquisition':'Byte-identical import from existing case archive, no repeat network download.',
 'primary_url':'https://lsdyna.ansys.com/wp-content/uploads/2022/11/experiments-and-simulations-of-explosives-shock-wave-propagation-around-a-convex-structure.pdf',
 'pdf_sha256':sha(pdf),'text_sha256':sha(txt),'source_case':str(source),'reading_scope':'PDF4text and PDF5figure checked now; earlier A02 source audit separately retained.',
 'A02_EOS_closed':False,'TNT_numerical_lead_run_ready':False,'source_quality_review':str(O/'quality_review.json'),'source_quality_review_sha256':sha(O/'quality_review.json')})
entry={'id':ID,'number':45,'label':'Van Dorsselaer 凸面爆炸实验与数值','display_year':2018,'topic':'evaluation',
 'title':'Experiments and Simulations of Explosives: Shock Wave Propagation around a Convex Structure',
 'authors':['Van Dorsselaer, N.','Eveillard, S.','Trélat, S.'],'source_url':read(source_record)['primary_url'],'pdf_url':read(source_record)['primary_url'],'arxiv_version':None,
 'summary_zh':'报告IRSN半圆柱附近Hexomax实验及LS-DYNA／OURANOS数值比较，另有未经实验检验的1kg TNT自由场数值预备算例。',
 'boundary_zh':'原文未列完整Hexomax或TNT JWL常数。障碍物距离0.4／0.6m不直接对应A02的0.27m；原文Hexomax自由场择两次的策略不继承。图5仅为论文数值参考，草稿数字化尚未批准。',
 'review_level':'原A02页码核验保留；本轮补核PDF4方法文字和PDF5数值图，非全文精读。','used_in':{'chapters':[3]},'verified_on':'2026-11-07',
 'metadata_title':'Experiments and Simulations of Explosives: Shock Wave Propagation around a Convex Structure','metadata_date':'2018',
 'booktitle':'15th International LS-DYNA Users Conference',
 'archive':{'status':'archived','source_file':source_record.relative_to(L).as_posix(),'source_sha256':sha(source_record),'pdf':pdf.relative_to(L).as_posix(),'pdf_sha256':sha(pdf),'text':txt.relative_to(L).as_posix(),'text_sha256':sha(txt),'text_kind':'existing_case_PDF_extracted_text_not_manually_corrected','checked_on':'2026-11-07','errors':[]},
 'annotation':f'annotations/{ID}.md'}
cat['papers'].append(entry);cat['updated_on']='2026-11-07';save(L/'catalog.json',cat)
note='''# Van Dorsselaer 凸面爆炸实验与数值（2018）

Experiments and Simulations of Explosives: Shock Wave Propagation around a Convex Structure，15th International LS-DYNA Users Conference，2018。作者在原文署名N. Van Dorsselaer、S. Eveillard、S. Trélat。

[完整原始PDF](../papers/van-dorsselaer-convex-blast-2018.pdf)及[归档回执](../sources/van-dorsselaer-convex-blast-2018-archive_20261107.json)从已有case原件按字节导入，无重复下载。

PDF4的预备数值条件为1kg完整TNT球、10×10m域、4mm方形网格、空气初压101325Pa、2D轴对称MMALE，沿X轴提取峰值超压；PDF5图5给出OURANOS和LS-DYNA的数值曲线。这不是实验试次。原文没有提供本次可用的完整TNT JWL／能量参数；图的自动候选读数仍为草稿，其中最近OURANOS点只有1个颜色像素，不可作为可信标记中心。未构建原生输入、未启动该数值线索的仿真、无APE/MAPE。

原A02核验另记录：Hexomax材料常数由ArianeGroup用Cheetah提供而未列出；障碍物距离0.4／0.6m不等于选定0.27m。论文对Hexomax自由场三次取两次的策略不在本benchmark继承。不得把TNT数值线索替代A02实验或用误差容限批准材料匹配。

本轮仅补核PDF4方法文字及PDF5图，取得原件和局部核验不表示全文精读或Gold批准。
'''
for p in [L/f'notes/{ID}.md',L/f'annotations/{ID}.md']:assert not p.exists();p.write_text(note,encoding='utf8')
with (L/'INDEX.md').open('ab') as f:f.write(('\n| [45] | [Van Dorsselaer 凸面爆炸实验与数值 (2018)](notes/'+ID+'.md) | evaluation | [PDF](papers/'+ID+'.pdf)（相关页核对） |\n').encode('utf8'))
bib='\n@inproceedings{'+ID+',\n  title = {'+entry['title']+'},\n  author = {Van Dorsselaer, N. and Eveillard, S. and Trélat, S.},\n  year = {2018},\n  booktitle = {15th International LS-DYNA Users Conference},\n  url = {'+entry['source_url']+'}\n}\n'
with (L/'references.bib').open('ab') as f:f.write(bib.encode('utf8'))
with (L/'README.md').open('ab') as f:f.write(('\n2026-11-07：将已有case的[Van Dorsselaer2018原文](notes/'+ID+'.md)按字节导入，当前45条目录／笔记、42篇PDF，无重复下载。1kg TNT数值线索因条件和读数缺项未具备运行条件，不替代A02；原44条目录与既有笔记保留。\n').encode('utf8'))
assert read(L/'catalog.json')['papers'][:-1]==old and all(sha(p)==h for p,h in old_notes.items())
assert (L/'INDEX.md').read_bytes().startswith(index_before) and (L/'references.bib').read_bytes().startswith(bib_before)
assert len(list((L/'papers').glob('*.pdf')))==42 and len(list((L/'notes').glob('*.md')))==45
shutil.copyfile(Path(__file__),O/'review_reference.py')
save(O/'manifest.json',{'scope':'Primary-source numerical lead and explicitly unapproved candidate readings, no native input or score',
 'files':[{'path':p.relative_to(O).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(O.rglob('*')) if p.is_file()]})
q=read(P/'all_case_simulation_queue.json');original=copy.deepcopy(q['registered_cases']);assert len(original)==30
record={'at_UTC':now,'classification':review['classification'],'reference_kind':'published_numerical_only_not_experimental','review_html':str(O/'index.html'),'review':str(O/'quality_review.json'),'manifest_sha256':sha(O/'manifest.json'),'trusted_reference_rows':0,'new_native_simulation_dispatched':False,'new_APE_MAPE':False,'A02_replaced':False,'all30_registered_conditions_unchanged':True,'library_records':45,'library_PDFs':42,'goal_complete':False}
for p in [P/'campaign_status.json',P/'all_case_simulation_queue.json']:
 d=read(p);d.setdefault('supplementary_source_access_checks',{})['A02_related_TNT_numerical_lead_20261107']=record;save(p,d)
assert read(P/'all_case_simulation_queue.json')['registered_cases']==original
for p in [E/'tnt1kg_numerical_source_lead_20261107.json',X/'tnt1kg_numerical_source_lead_20261107.json']:assert not p.exists();save(p,record)
print(json.dumps(record,ensure_ascii=False))
