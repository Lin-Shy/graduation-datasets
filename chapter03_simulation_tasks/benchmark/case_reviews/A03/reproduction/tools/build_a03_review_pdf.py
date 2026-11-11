"""Render the complete A03 review PDF from the separately verified analysis outputs."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'references/review/feature_mape_20261105/human_review/A03'
OUT=DATA/'output/pdf/A03_complete_review.pdf'
pdfmetrics.registerFont(TTFont('MSYH','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
styles={
 'title':ParagraphStyle('title',fontName='MSYH',fontSize=19,leading=27,textColor=colors.HexColor('#173C5B'),spaceAfter=12),
 'h':ParagraphStyle('h',fontName='MSYH',fontSize=13,leading=20,spaceBefore=10,spaceAfter=7,textColor=colors.HexColor('#173C5B')),
 'body':ParagraphStyle('body',fontName='MSYH',fontSize=9.5,leading=16,spaceAfter=8,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='MSYH',fontSize=8,leading=12,spaceAfter=6,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='MSYH',fontSize=8.2,leading=12,wordWrap='CJK'),
}
story=[]
def text(s,kind='body'):story.append(Paragraph(s,styles[kind]))
def table(rows,widths):
 cells=[[Paragraph(escape(str(c)),styles['cell']) for c in row] for row in rows]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#9CAEBB')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#D8E0E6')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 story.append(t);story.append(Spacer(1,8))
def picture(name,width=515):
 from PIL import Image as PILImage
 w,h=PILImage.open(DATA/name).size;story.append(Image(str(DATA/name),width=width,height=width*h/w));story.append(Spacer(1,8))
def page(title):
 if story:story.append(PageBreak())
 text(title,'title')
def footer(c,doc):
 c.setFont('MSYH',8);c.setFillColor(colors.HexColor('#637584'))
 c.drawString(38,23,'A03完整审核包 | 2026-11-05 | 已有操作员参考算例；未新增求解')
 c.drawRightString(A4[0]-38,23,str(doc.page))

def main():
 m=json.loads((DATA/'complete_review_metrics.json').read_text(encoding='utf-8'))
 peaks=m['numerical_result']['peak_overpressure_kpa'];trials=m['trials']
 page('A03完整审核包：结果与判断')
 text('对象：200 mm刚性钢筒内部爆炸，第一组名义20 g C4，Pi02/Pi03/Pi04三点。此次提供完整资料，由负责人看完后在当前会话给意见，不再拆成逐项确认。')
 text('已有A03参考算例完成0-4 ms，三个测点各6015条采样。条件性峰值MAPE分别为7.11%、13.78%、6.78%，数值均落入拟定的≤15%档；但压力定义、试次聚合、物理匹配和模型健康尚未批准，不能转换成Gold或端到端任务合格结论。')
 picture('diagnostic-mape.png')
 table([['固定映射','已有仿真峰值kPa','表1试次1*','表1试次2*','表1试次4*']]+[[f'Pi0{j+2} / P{j+1}',f'{peaks[j]:.2f}']+[f'{t["reference_peaks_kpa"][j]:.1f}' for t in trials] for j in range(3)],[105,110,100,100,100])
 picture('pointwise-ape.png',460)
 text('注意：试次2的Pi02单点APE为32.14%，三点MAPE仍为13.78%。这里严格按均值指标报告，不删该点，也没有另设未授权的单点通过限。','small')

 page('原文工况与测点映射')
 text('原文依据：Kristoffersen等，2024，DOI 10.1007/s00193-024-01161-w；PDF第2-3页§2.1、图2和§2.2。图2上方为400 mm筒，下方200 mm筒才是本题，实物照片图1不能替代本题尺寸。')
 picture('source-figure-2.png')
 table([['条件','原文/实验','现有A03与边界'],['钢筒','内径200 mm；外径250 mm；长3 m','刚性筒；两端开放；外部环境域已建'],['源位置','轴向中心、截面中心；球形C4','中心球源，半径0.0148587 m'],['名义装药','20 g C4；雷管约增加2 g等效','固定数值总量22 g；等效假设待审'],['比较测点','第一组Pi02、Pi03、Pi04','P1、P2、P3；不混入后续Pr测点组'],['观测窗口','原文4 ms用于冲量比较，不等于所有指标均已定义','既有求解固定0-4 ms；峰值搜索窗口采用该数值窗口'],['采样','内壁齐平压力计；0.5 MHz','patchProbes；壁面静压；三点位置见下']],[85,207,223])
 table([['对应','距源轴向m','数值位置m','核对状态'],['Pi02→P1','0.600','(0.6,0.099904822,0)','轴向匹配；法向待核'],['Pi03→P2','1.300','(1.3,0.099904822,0)','轴向匹配；法向待核'],['Pi04→P3','1.400','(1.4,0.099904822,0)','轴向匹配；法向待核']],[86,80,170,179])
 text('坐标约定：爆源为原点，正x指向测点侧出口。径向0.099904822=0.1×cos(2.5°)，与5°楔面投影一致，差约0.09518 mm；它不是壁面/法向已获物理匹配批准的证明。后续Pr01/Pr02/Pr03距源0.4/1.2/1.3 m，不作为可互换测点。','small')

 page('已有仿真结果与实验曲线')
 picture('pressure-curves-unshifted.png')
 text('实验为原始仪器Bar×100得到kPa，不减经验基线、不平移。数值为原生绝对压力减101300 Pa。两种时钟尚未独立校准，因此叠图用于幅值与形状审阅，不据此计算时程NRMSE或到达时间MAPE。','small')
 table([['测点','数值峰时ms（不是到达）','数值峰值kPa'],*[[f'P{j+1}',f'{v:.6f}',f'{peaks[j]:.2f}'] for j,v in enumerate(m['numerical_result']['peak_clock_ms'])]],[100,245,170])
 text('图中压力信号可出现负超压；未做裁零、平滑、最佳时间平移或幅值缩放。峰值取原生采样全窗口最大值，不从重采样曲线寻峰。','small')

 page('关键特征参考及计算口径')
 picture('source-table-1-selected.png')
 text('表1（PDF第6页）带星号的试次1、2、4属于第一组；试次3由作者因异常排除。出版数值与各原始通道的9个峰值仅做单位转换后，全部在表1舍入范围内，最大差0.05 kPa。参考主试次或聚合尚未冻结；本包三个试次全部列出，不选误差最小者。')
 picture('peaks-simulation-comparison.png')
 text('逐点APE=100×|数值峰值-参考峰值|/|参考峰值|；每个试次固定三点的MAPE为三个APE等权均值。全部9个参考值为正，最小1001.8 kPa，未使用epsilon或删除近零点。本轮计算以表1峰值可对应超压为条件，压力定义仍待批准。','small')
 text('30%/15%作为拟定分档，仅作用于每个指标的MAPE；不混合峰值与到达，不把部分测点低误差当完整成功。到达时间没有经独立时钟核对的参考，不拿“采样峰时”冒充到达。实验完整时程不是本题入选必需项。','small')

 page('材料差异、运行与健康证据')
 text('原文表2实际位于PDF第9页。旧建设记录将它标为第6页，本包校正引用位置，保留旧记录身份。参数相同不表示模型形式相同。','small')
 picture('source-table-2.png')
 table([['项目','原文数值方案','已有A03'],['模型','EPX单组分JWLS，1/8对称域','blastFoam两相Murnaghan/JWL；5°楔形'],['材料常数','A=6.0977e11 Pa；B=1.295e10 Pa；R1=4.5；R2=1.4','对应JWL常数一致；激活/热力学更新形式不同'],['空气与能量','ρair=1.225；p0=101300 Pa；γair=1.4；E0=9e9 J/m³','相关输入数值一致；适用性仍待核'],['离散质量','目标22 g的数值等效源','按360/角度缩放为22.29093 g（+1.3224%）；轴对称旋转定义22.31925 g'],['网格与运行','文献网格/环境不同，不能直接比较耗时','19020单元；全流程7006.26 s；求解6814.05 s'],['完成与健康','实验与文献结果不替代本算例检查','建网检查通过、退出0、到4 ms；保存场无非正温度，但无全过程/RK健康证明']],[76,220,219])
 text('公共Kurganov/Riemann激活路径风险仍在；A03没有本题已证实的早期0 K记录，也没有排除该风险的全过程验证。当前不把其他题的压力误差直接归给A03；不启动修复或新求解。','small')

 page('审核结论与全部证据入口')
 table([['审核维度','本包技术结论','负责人意见'],['参考来源','表1九个峰值可追溯，原文与原始数据一致到舍入；不是缺时程阻塞','待你在会话反馈'],['数值误差','三个试次的条件性峰值MAPE为7.11%、13.78%、6.78%；试次2 Pi02单点32.14%完整保留','待确认比较口径与试次政策'],['几何与测点','主要尺寸和三点轴向距离对应；楔面采样、周向/法向待核','待确认可接受匹配范围'],['源与材料','20g+约2g等效源及JWLS→两相JWL差异明列，未据低MAPE批准','待确认适用性或暂缓'],['时间与到达','没有独立起爆零点；不报告到达MAPE或拟合时程误差','可先仅采用峰值指标，待你判断'],['任务完成','已有操作员参考求解完成4ms和三点输出；不是无人干预Agent端到端成功','不能直接作为Agent成绩'],['Gold与题目资格','仍待条件、参考与模型健康审查；当前ready=false、Gold未批准','可接受/补证/暂缓，请直接反馈']],[74,317,124])
 text('你可以一次性给出整题意见，包括采用哪些参考试次/聚合方式、峰值是否作为首版必需指标，以及哪些条件必须补证。任何认可只按你实际表述记录，不从“MAPE较低”推断科学批准。')
 text('原始与派生资料','h')
 assets=[('原文完整PDF，含图2、表1、表2及时间对齐说明',ROOT/'references/experiments/mendeley-zv7y78twd9-v2/raw/Kristoffersen et al - 2024 SW - Semi-confined blast loading.pdf'),('逐点误差与全部MAPE、来源SHA256',DATA/'complete_review_metrics.json'),('9个逐点对比，便于复算',DATA/'peak_comparison_diagnostic.csv'),('实际运行收据：命令、退出码、耗时',ROOT/'references/runs/20261022-a03/A03-run.json'),('原生三测点绝对压力',ROOT/'references/runs/20261022-a03/A03/postProcessing/probes/0/p'),('原始仪器数据001/002/003/004及下载血缘',ROOT/'references/experiments/mendeley-zv7y78twd9-v2/download_manifest.json'),('源质量与材料诊断',ROOT/'references/review/round6/source-mass-energy/A03.json'),('保存场温度证据及其边界',ROOT/'references/review/round6/temperature/A03.json')]
 for label,p in assets:
  text(f'<link href="{p.resolve().as_uri()}" color="#245D8D">{escape(label)}</link>','small')
 text('复算脚本：tools/build_a03_complete_review.py；读取已有原生数据，不访问模型或求解器。PDF由tools/build_a03_review_pdf.py生成。A05/A02继续按完整资料包逐题提供，本包不提前批准它们。','small')
 OUT.parent.mkdir(parents=True,exist_ok=True)
 SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=35,bottomMargin=38,title='A03完整人工审核资料',author='研究辅助整理').build(story,onFirstPage=footer,onLaterPages=footer)
 print(OUT)

if __name__=='__main__':main()
