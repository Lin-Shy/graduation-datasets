"""Record the 60 chat recommendations explicitly confirmed by the human reviewer.

Offline score-side transcription only. Never generates answers, changes scoring
rules, unlocks acceptance, or loads model identities into the output artifacts.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parents[4]
CODE = WORK / 'PrincipiaBlastFoam-DSH/experiments/chapter2'
sys.path.insert(0, str(CODE))
from judge_contract import validate, joint_metrics

REVIEWER = 'blastfoam专家'
DISCLOSURE = 'AI辅助人工评分：AI提出推荐及依据，评审人逐项查看后明确确认；由助手代为转录。此记录不是无AI建议的独立人评。'
CONFIRMATION = '上述你的推荐评分和具体内容我都已经一一查看没有问题和错误。接下来你帮我把评分填进去，完成这个人工工作。'

# Display order, anonymous sample ID, question ID, K scores, F, A, K reasons,
# whole-answer F/A explanation. None in A means the question is nonconditional.
DECISIONS = [
('R-22fc0a271924','E14-03',[.75,.75,.5],.75,None,
 ['标量及各向同性正确，遗漏常数属性且同质性用词不准。','矢量及各向异性正确，遗漏常数属性且异质性用词不准。','正确说明标量与矢量区别，遗漏共同单位W/m/K。'],
 'F：核心区别正确，但同质性/异质性与各向同性/各向异性混用。'),
('R-150962443949','E16-02',[0,0,0],.25,None,
 ['未给温度型分支的Gamma定义。','用内能型声速公式代替温度型关系。','未说明除非另有指定的默认适用条件。'],
 'F：所抄公式有来源，但将内能型关系用于题设温度型分支，核心适用关系错误。'),
('R-235d4357f6f9','E53-07',[.75,0],.5,.5,
 ['知道先处理密度，未明确由p、T重算rho。','明确主张沿用初始rho而不等待密度重算，错误。'],
 'F/A：前述顺序部分正确，随后对新旧rho的选择错误，整答存在直接矛盾。'),
('R-a4d15ed2fed1','E47-03',[1,1,1],1,1,
 ['条件前作为wall正确。','条件满足后burst正确。','burstCyclicAMI类型正确。'],
 'F/A：条件前后行为及类型完整正确，未要求具体阈值。'),
('R-0f32329417ab','E25-07',[.75,1,.5],.75,.75,
 ['最大值改为差值方向正确，但将耦合patch写成相邻patch、单个patch最大值。','正确对应no到yes的改动。','压力差体现压力判据，但未明确burstModel仍为pressure，范围说明笼统。'],
 'F/A：主要改动判断正确，耦合关系表述不准，未充分限定其余配置保持不变。'),
('R-961e29e7b822','P02-03',[0,1],1,1,
 ['未说明题设中首次明显响应与最大压力时刻可以重合。','最大压力时刻定义及单例不能泛化的结论正确。'],
 'F/A：已有事实与不可泛化结论正确；遗漏重合说明属于完整性问题。'),
('R-68d99d07ca65','N66-03',[.75,.25,0],.25,None,
 ['以T查mu和kappa正确，未明确两个一维表。','涉及二维及rho、T组合，但混同EOS查表，未正确给出mu/kappa输出。','未给一阶、二阶、纯导数及混合导数。'],
 'F：第一部分基本正确，后续存在输运与EOS混淆及缺乏依据的导数描述。'),
('R-ea296aac041f','E37-03',[.25,0,.75],.25,.25,
 ['知道字段选择目的，但正确选项应为-probeNames而非-select。','未答出-force覆盖已有合并结果，解释错误。','默认全部字段正确，遗漏起始时间文件夹范围。'],
 'F/A：默认行为部分正确，两个关键选项均解释错误，无法据此正确完成筛选。'),
('R-dcab767cce7f','P07-04',[1,.5,1],1,None,
 ['各mod取值正确。','给出按变量独立配置的概念，未清楚区分输入轴与输出及子字典前缀规则。','不能将一个mod套到全部量的结论正确。'],
 'F：已有陈述基本正确，主要问题是作用域解释不完整。'),
('R-1f44efb07946','E49-01',[1,1,1],1,None,
 ['FSI能力演示正确。','二维小型C4装药靠近墙壁起爆正确。','挡板变形及影响波传播正确。'],
 'F：覆盖全部必要点，无实质性错误；不因未提开发状态扣分。'),
('R-175dcf3ef079','E15-03',[1,1],1,None,
 ['参考密度处零压力的偏移能量及pRef用途正确。','固体分支不考虑热能正确。'],
 'F：完整符合solidJWL未反应分支说明。'),
('R-cfc0ed22da7f','E17-02',[.5,1,.5],.5,None,
 ['Gamma和delta正确，Pi误写为gamma*(b-a)，应为gamma*a。','idealGas三参数正确。','识别差别集中在Pi，但具体差别写错。'],
 'F：正确参数与直接影响比较的关键Pi错误混杂。'),
('R-fbb64ddc54d5','E28-01',[1,.25],.5,None,
 ['intactField名称及用途正确。','开头提字段字典，但最后混淆为burstModel配置层级。'],
 'F：名称与功能正确，最后关于配置层级的说明存在重要错误。'),
('R-05d7618f80f0','E38-02',[1,1],1,None,
 ['正确说明-outputDir指定series文件写入位置。','正确说明-absolute控制文件路径表示方式。'],
 'F：两个选项的对象与作用层面均正确。'),
('R-7cc108391aa2','N64-03',[1,0,.75],.75,.75,
 ['正确限制CarnahanStarling为单分散。','遗漏大小颗粒填隙使局部堆积限变化的机制。','拒绝断言多分散堆积限不变，但未联系单分散常数建议的适用范围。'],
 'F/A：主要结论方向正确，但手册已有堆积限变化说明，不能归为资料未明确。'),
('R-f7293acb12b5','N59-02',[1,1,1],1,None,
 ['volumeAveraged压力的体积分数平均正确。','totalPressure中两种压力及不同权重正确。','massAveraged速度的相质量平均及比较正确。'],
 'F：对象、权重与不能混称一种平均的解释完整正确。'),
('R-0e43fccfa926','P07-01',[.25,0,.25],.25,None,
 ['仅rho输入正确，专用组合应以rho、e查p/T。','未说明给定p、rho反查初始化内能。','一般段的变量出现，但直接套入专用组合，未做正确区分。'],
 'F：将一般eTabulated映射套用于专用组合，核心关系大多错误。'),
('R-48d679ae4f9c','P04-03',[.5,.75,1],1,.75,
 ['说明查表后修正，但未指出静水校正。','识别true启用后续修正，未清楚对照原false。','正确说明修正可能调整场且最终压力不保证等于表值。'],
 'F：未发现明确实质性错误，可能性举例不作为已验证结论。A：主要条件正确，具体流程不完整。'),
('R-082de350f0cf','P06-03',[0,.5],.5,.25,
 ['未定位combustionProperties中的Su与0/Su，转而讨论fvSchemes。','不能自动同步、另行修改初始场的方向正确，但未针对实际Su输入且遗漏边界。'],
 'F/A：把燃速物性问题转为数值格式问题，只有不能自动同步的部分判断有用。'),
('R-9b6416d2dbc2','P06-02',[.5,.5,1],1,1,
 ['明确物性改0.6m/s，缺少文件、Su条目和量纲写法。','明确内部场改0.6m/s，缺少0/Su和uniform配置写法。','明确墙面和空方向边界保持原样。'],
 'F/A：三个约束的处理方向正确，没有实质性错误，操作细节不足通过K反映。'),
('R-17351f869755','E49-01',[1,.75,1],1,None,
 ['FSI演示目的正确。','二维、小型C4及壁面正确，未明确装药靠近墙壁的位置关系。','挡板变形影响波传播正确。'],
 'F：主要事实正确；扇叶译法不规范但未声称旋转，不据此判实质性错误。'),
('R-f298e6a7dd65','E27-02',[1,1],.75,None,
 ['fields与values列表写法有效。','p、impulse及阈值顺序对应正确。'],
 'F：额外将field小节未确认的OR触发逻辑写成确定事实；不等于已核实OR本身错误。'),
('R-22468dd2c615','P05-03',[0,0],.25,0,
 ['未识别明确solid类的常密度EOS限制。','错误地因RDX案例采用Murnaghan就判断可直接照搬。'],
 'F：案例中Murnaghan的观察正确，主要兼容性判断错误。A：题设明确solid类时给出反向结论。'),
('R-e7f9c4154a66','N68-01',[1,1],1,1,
 ['目前仅实现particle-to-fluid正确。','fluid-fluid当前不支持及范围区分正确。'],
 'F/A：固定版本的支持范围与交换对象完整正确。'),
('R-cf56a2b952e5','E42-01',[1,.5],.5,None,
 ['使用总密度正确。','公式主体有梯度差、分母尺度、最大值及f指数，但文字否认归一化，与比值结构矛盾。'],
 'F：总密度与公式主体正确，解释存在矛盾；不把有疑点的符号解释当作已核验实现。'),
('R-28a6dd388a39','E39-03',[.75,.5],.75,None,
 ['非守恒方向正确，但通常不保证、依算法而定弱化当前明确特性。','提到流场偏差，但遗漏最近单元值及特征过度或不足强调的机制。'],
 'F：核心风险基本正确，实现差异及稳定性等说明超出原文直接证据。'),
('R-fdb7ecb35617','E20-01',[1,1,1],1,1,
 ['缺少关键字采用none且不加额外能量正确。','按题设语境正确表达不因后燃额外升高p、T。','直接回答关键字缺失场景下的默认选择。'],
 'F/A：不将没有后燃直接后果扩大解释为整个流场压力温度恒定。'),
('R-29dfa00d1883','E42-03',[.5,0,.25],.5,None,
 ['知道梯度识别细化区域，遗漏总密度及教程明确配置。','误把beginUnrefine解释为细化起始时间步，应为粗化准入物理时刻。','泛泛说先加密后粗化，未解释误差判据与粗化时间准入分工。'],
 'F：梯度方向正确，关键时间参数错误，且由静态配置保证特定演化。'),
('R-da938412101c','E48-03',[0,.75,0],.25,None,
 ['未识别blastFoam脚本没有区域拆分调用的实际流程。','正确识别FSI调用splitMeshRegions，遗漏顺序及参数。','未答两者addEmptyPatch，额外引入无依据的coupledGlobalPolyPatch。'],
 'F：少量FSI区域拆分内容正确，关键内部patch说明失实。'),
('R-2be92336740e','E48-03',[.75,.75,.25],.5,None,
 ['blastFoam不拆分区域的主结论正确，未给对应流程细节。','FSI拆分区域的主结论正确，未给对应流程细节。','仅FSI添加patch正确；误称blastFoam不添加，遗漏air限定。'],
 'F：拆分结论正确，内部patch比较部分错误；两份脚本都添加，FSI指定air。'),
('R-34d9eabf96e5','P09-01',[.5,.5,.25],.5,.5,
 ['涉及linear差异和六点，未说明README所称四点延迟。','当前programmedIgnition及六点正确，未核对四个非零、两个零及延迟序列。','开头承认名称差异，最后又称无需保留差异，矛盾。'],
 'F/A：模型名称有差异应保留，六点与四点非零延迟可相符；比较部分正确但结论矛盾。'),
('R-b6cec0b1c437','E29-06',[0,0,0],.25,0,
 ['未答超压p-pRef定义。','未答固定数据下参考压力增加Delta p使峰值减Delta p，反而说可能不变。','未说明fieldMinMax输出每单元极值场。'],
 'F：保留一般后处理描述的少量正确性。A：固定数据条件下的核心判断错误。'),
('R-e688146d2842','P06-02',[0,1,1],1,.5,
 ['完全漏改combustionProperties中的Su。','0/Su的internalField uniform 0.6正确。','walls zeroGradient与defaultFaces empty正确。'],
 'F：已有陈述无实质性错误。A：仅落实三个约束中的两个，未同时满足全部约束。'),
('R-331fe77a13cb','N60-02',[1,1,1],1,None,
 ['constant固定直径及不写场说明正确。','constantMass由rho0、d0定义M并按当前rho计算d正确。','正确区分恒质量与恒直径，未推广不写场说明。'],
 'F：模型职责、参数与公式完整正确。'),
('R-98886a357967','N56-03',[0,0,0,0],'unknown',None,
 ['未回答单流体多相共享速度、内能与温度。','未回答blastEulerFoam的Euler-Euler变体及相模型。','未回答各流体相独立质量、动量、能量及相间传递。','未回答EOS数量与独立速度数量并非同一维度。'],
 'F保留Unknown：只有检索未果自述，无可评价领域事实，匿名材料无法核实其检索经历；纯拒答F尺度列为校准争议。此项有最终回答，不套生成失败归零规则。'),
('R-f4bede873d54','E33-01',[.25,1],1,None,
 ['仅笼统跟踪守恒量，遗漏体积积分、初始/当前值、总差值与相对差值。','fields配置正确。'],
 'F：已有陈述没有明确实质性错误，覆盖不足由K反映。'),
('R-3f18ac0bff71','E28-01',[.25,.25],.25,None,
 ['用途正确，但名称应intactField而非preBurst。','只有边界配置方向的少量正确内容，boundaryConditions层级无原文支持。'],
 'F：关键名称和配置层级失实，仅用途部分正确。'),
('R-2c7b5589f53f','N66-01',[.25,0],.25,None,
 ['仅拟合mu、kappa自然对数正确；自变量应ln(T)，不是Re/Pr。','两组均为8个系数，不是3个与2个。'],
 'F：主要自变量与参数数量错误。'),
('R-40ad04c05441','N65-01',[1,.75],1,1,
 ['最大黏度为0可省略字典正确。','黏性时需字典和合适模型正确，未补充laminar不等于省略黏性配置。'],
 'F/A：两主要分支正确，遗漏laminar澄清通过K反映。'),
('R-26e923f25df8','N61-02',[1,1,1],1,None,
 ['duct公式正确且无显式alpha_c。','Gunn完整关联式正确。','显式体积分数依赖及公式中不同Re/Pr幂结构均体现。'],
 'F：公式与比较完整正确，不强制再用文字复述公式差别。'),
('R-7b677bd47600','E53-07',[1,1],.75,1,
 ['先以p、T重算rho正确。','使用重算rho而非原rho且先后关系正确。'],
 'F：局部将原始T也列为随后初始化内能的直接依据；题设Mie-Gruneisen分支明确用p、rho初始化e。A：先后与新旧rho判断正确。'),
('R-e45115863a24','N59-02',[.5,.25,.75],.5,None,
 ['体积加权方向部分正确，但误释为每个单元体积而非两相体积分数。','未分开热力学压力体积分数平均与动态压力质量平均。','速度质量平均主结论正确，但每单元质量解释不准确。'],
 'F：正确权重名称与错误平均对象、totalPressure解释混杂。'),
('R-e016f1e548e9','E26-02',[1,1,.75],1,None,
 ['冲量模型所需场名与阈值正确。','impulseName默认值及impulseBurst作用正确。','说明自动计算，但未强调运行时必须有可用冲量场。'],
 'F：已有输入与计算方法陈述正确，必要条件强调不足由K反映。'),
('R-f34c62b0d4e1','E44-03',[.75,1,0],.5,.5,
 ['区间方向正确，但将原文严格不等式误写为包含端点。','加密与解加密阈值区分正确。','maxRefinement=1是最多1级，不是整个仿真只允许一次操作。'],
 'F/A：阈值部分正确，对加密层级与操作次数存在重要混淆。'),
('R-5809ba6709ff','E53-03',[0,0],.25,0,
 ['已提供e应由rho、e算p、T，回答反向。','未正确说明无e时p、rho初始化e的默认分支。'],
 'F：仅附带calculateDensity=yes时由p、T算rho正确。A：题设分支及变量角色错误。'),
('R-6dee51e8518d','N67-02',[.25,.25,1],.25,None,
 ['仅参考导热量等少量概念正确，误用Arrhenius式及参数。','仅温度多项式概念正确，应0到7次、8系数而非固定三次四参数。','始终讨论固体导热，没有加入muCoeffs。'],
 'F：两个模型主要公式与参数组织错误。'),
('R-c5e196c041d7','P08-01',[.5,.25,.75],1,.75,
 ['说明yes时允许调整，未明确实例已启用及blastProbes类型。','默认仅模糊写可能未启用，遗漏最近面。','知道需要显式设置，未把yes当普遍默认，但区分不完整。'],
 'F：无明确反向事实，主要是遗漏与模糊表述。A：条件方向正确，实例判断不够完整。'),
('R-c972eef4bd61','P08-01',[.75,0,0],.75,.5,
 ['正确读取实例adjustLocations=yes，遗漏blastProbes类型。','未说明默认no及最近面。','未区分实例显式启用与通用默认。'],
 'F/A：启用判断正确，最后混淆probeLocations给定位置与自动调整到最近面的机制。'),
('R-b4b3db33fb3d','N66-03',[0,0,0],0,None,
 ['completion_truncated，未交付有效最终回答。','completion_truncated，未交付有效最终回答。','completion_truncated，未交付有效最终回答。'],
 '生成失败：completion_truncated。按冻结规则EAS与Strict固定为0；失败占位文本不作为答案，不进行内容重试。'),
('R-9467c32eb158','P04-02',[.75,1,.75],1,1,
 ['按高度p、T确定rho正确，未说明表模式可选后续静水校正。','在题设correct=false下不要求后续校正正确。','动态求静水压力梯度正确，未明确随后调整密度。'],
 'F/A：按题设false配置理解，事实及分支正确；不扩大为任何查表模式都不能校正。'),
('R-c80c58dd1b5c','E19-04',[.5,.75,.25,1],.5,.5,
 ['知道pScale缩放p，遗漏压力指数n和默认值1。','最低压力门槛意义正确，遗漏教程1e5Pa。','仅原始缩放p扩大1e6正确；压力幂因子倍率应10^(6n)，本例约10。','门槛与缩放职责区分正确，未编造执行顺序。'],
 'F/A：核心倍率分析遗漏n；同一p、n及其他输入下只比较压力因子，不保证整场结果同比变化。'),
('R-343bd92380f4','P05-02',[0,.25],.25,0,
 ['未区分物理固体材料名称与特定solid模型类。','识别案例用Murnaghan，但据此怀疑配置错误，推断不成立。'],
 'F：关于Murnaghan通常用于气体缺乏资料依据。A：不能仅凭RDX为固体判定该案例违反solid类约束。'),
('R-900601bb50b8','E34-01',[.5,1,1],1,1,
 ['使用Schlieren标题名，但未明确实际grad对象及梯度计算作用。','标量/向量限制正确。','默认结果名Schlieren/grad(field)正确。'],
 'F/A：文档标题即Schlieren(grad)，回答未给明确错误type配置，不将标题名使用直接判实质性错误。'),
('R-05fe8aa0dce8','E53-03',[0,0],0,0,
 ['已提供e的分支方向颠倒。','无e默认分支方向也错误，泛称方向变化不能得分。'],
 'F/A：应有e时rho、e算p/T，无e时p、rho算e；回答两个分支均反向。'),
('R-520ce5f2523e','N61-03',[0,0,0],1,None,
 ['未给sphere与RanzMarschall两个Nu公式。','未给Nu差0.2*Re^(1/2)*Pr^(1/3)。','未给共同前因子6*alpha_d*kappa_c/d_d^2乘以上述差。'],
 'F：已有一般背景及可能性表述无明确实质性错误；没有回答定量差别，覆盖不足由三个K=0体现。'),
('R-db0305de9868','E15-03',[1,1],1,None,
 ['参考密度零压力偏移及pRef偏压用途正确。','solidJWL固体分支不考虑热能正确。'],
 'F：与第11份同尺度，完整符合题设分支。'),
('R-6529c9e34ec5','E54-01',[.5,0,0],.5,.25,
 ['divSchemes使用Riemann方向正确，但未明确为实际附加场配置限制器。','漏掉reconstruct(rho)默认回退，并将缺少单独限制器直接列为失效。','遗漏刚性隐式源项压倒显式对流的关键限制及隐式散度建议。'],
 'F/A：配置部分正确，核心失效机制未答出，且无依据暗示须使用Kurganov。'),
('R-5204052d62d1','E51-01',[.25,.5,.75],.5,.75,
 ['仅邻居温度正确，遗漏传热系数与辐射热流。','unmappedT用途基本正确，默认值应293.15而非0。','正确拒绝保证整个补丁同温，但未说明资料缺少逐面映射细则。'],
 'F：正确内容与错误默认值混杂。A：主要范围判断正确，参数理解有问题。'),
('R-0849ab52ed58','N60-03',[.25,.25,.5],.25,.25,
 ['未准确定位右端反应率k源项，混称扩散或源项。','知道1e-6，但乘法缩放误写除法且给pScale加MPa单位。','知道压力相关项受影响，未清楚落实右端k。'],
 'F/A：正确式为partial_t d+u.grad d=k，k=beta*(p*pScale)^alpha；关键公式及缩放方向错误。'),
('R-a021a4d085b9','E55-01',[.75,.5,1],1,.75,
 ['foamGet probes正确，遗漏探针文件与输出时间配置的交互选择。','system目录正确，未明确编辑生成文件以设置实际目标位置。','在functions中用#includeFunc加载probes正确。'],
 'F：给出的接入及直接配置方式符合教程。A：缺少将示例位置调整为实际目标位置的条件。'),
]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def main():
    packet_path = ROOT / 'calibration/packets.json'
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    template = json.loads((ROOT / 'calibration/blank_labels.json').read_text(encoding='utf-8'))
    assert packet['phase'] == 'calibration' and packet['enabled_for_review']
    assert len(packet['samples']) == len(DECISIONS) == len(template['labels']) == 60
    assert len({d[0] for d in DECISIONS}) == 60
    paths = {
        'labels': ROOT / 'calibration/calibration_completed_human_labels.json',
        'page': ROOT / 'completed_review.html',
        'receipt': ROOT / 'calibration/human_review_completion.json',
    }
    if any(p.exists() for p in paths.values()):
        raise FileExistsError('Preserve existing human-review artifacts; do not overwrite')
    protected = [packet_path, ROOT/'acceptance/packets.json',
                 ROOT/'calibration/blank_labels.json', ROOT/'acceptance/blank_labels.json',
                 ROOT/'index.html', CODE/'scoring_rules.json', CODE/'judge_prompt.txt',
                 WORK/'graduation-datasets/chapter02_knowledge_qa/binding.json',
                 WORK/'graduation-datasets/chapter02_knowledge_qa/open/scoring/annotations.json']
    before = {p.relative_to(WORK).as_posix(): filehash(p) for p in protected}
    timestamp = datetime.now(timezone.utc).isoformat()
    labels, metrics = [], []
    by_template = {r['sample_id']: r for r in template['labels']}
    for ordinal, (sample, decision) in enumerate(zip(packet['samples'], DECISIONS), 1):
        sid, qid, scores, f, a, reasons, explanation = decision
        assert sample['sample_id'] == sid and sample['question_id'] == qid, ordinal
        assert sample['binding_status'] == 'bound' and sample['answer_sha256']
        assert hashlib.sha256(sample['answer'].encode('utf-8')).hexdigest() == sample['answer_sha256']
        assert len(scores) == len(reasons) == len(sample['criteria']), ordinal
        assert sample['conditional'] == (a is not None), ordinal
        row = deepcopy(by_template[sid])
        row.update(reviewer=REVIEWER, reviewed_utc=timestamp, packet_sha256=digest(sample))
        record = row['record']
        record.update(status='complete', fact_gate=f,
                      applicability_gate='not_applicable' if a is None else a,
                      reason=f'{DISCLOSURE}\n第{ordinal}份；{explanation}')
        assert [p['criterion_id'] for p in record['points']] == [c['criterion_id'] for c in sample['criteria']]
        for point, score, reason in zip(record['points'], scores, reasons):
            point.update(score=score, reason=reason, answer_quote='')
        validate(record, expected=[c['criterion_id'] for c in sample['criteria']], conditional=sample['conditional'])
        metrics.append(joint_metrics(record, [c['criterion_id'] for c in sample['criteria']],
                                     sample['conditional'], sample['generation_failed']))
        labels.append(row)
    assert sum(m['unknown_items'] for m in metrics) == 1
    assert sum(m['missing_items'] for m in metrics) == 0
    assert labels[34]['record']['fact_gate'] == 'unknown'
    assert packet['samples'][48]['generation_failed'] and metrics[48]['EAS_arith'] == 0
    provenance = dict(
        review_method='ai_assisted_human_confirmed', reviewer_signature=REVIEWER,
        reviewer_signature_source='User-supplied signature: blastfoam专家',
        human_confirmation=CONFIRMATION, recorded_utc=timestamp,
        timestamp_meaning='Time of recording the human-confirmed batch; not invented per-item review times.',
        disclosure=DISCLOSURE, packet_file_sha256=filehash(packet_path),
        independent_unassisted_human_review=False,
        acceptance_review_completed=False, ai_judge_calibration_completed=False,
    )
    document = dict(schema='human_review_labels_v1', phase='calibration',
                    labels=labels, review_provenance=provenance)
    # Use the existing file-load and restore handlers, including their hash checks.
    # Escape HTML delimiters in the JSON so answer text cannot become executable.
    bundle = json.dumps(dict(packet=packet, labels=document), ensure_ascii=False,
                        separators=(',', ':')).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    boot = '''
<script id="confirmed-review-bundle" type="application/json">BUNDLE</script>
<script>
(async()=>{
  try {
    const b=JSON.parse(document.getElementById('confirmed-review-bundle').textContent);
    await $('packets').onchange({target:{files:[{text:async()=>JSON.stringify(b.packet)}]}});
    await $('restore').onchange({target:{files:[{text:async()=>JSON.stringify(b.labels)}]}});
    if(!packet || labels.length!==60 || packet.samples.some((p,i)=>!complete(p,labels[i]))) throw Error('恢复后评分未达到60份完整状态');
    $('message').textContent='已恢复60份人工确认评分；评审署名：blastfoam专家。AI提出建议，真人逐项复核确认。第35份F保留Unknown，第49份为生成失败。可逐份查看或导出。';
    document.title='已完成 · 第2章校准人工评分';
  } catch(e) { $('message').textContent='恢复失败：'+e.message; }
})();
</script>
'''.replace('BUNDLE', bundle)
    html = (ROOT/'index.html').read_text(encoding='utf-8')
    assert html.count('</html>') == 1
    html = html.replace('</html>', boot + '</html>')
    receipt = dict(
        schema='human_review_completion_v1', phase='calibration', reviewer=REVIEWER,
        recorded_utc=timestamp, completed_records=60,
        necessary_point_scores=sum(len(r['record']['points']) for r in labels),
        missing_items=0, unknown_items=1,
        unknown_sample=dict(display_number=35, sample_id=labels[34]['sample_id'], item='F', value='unknown'),
        generation_failures=1, failed_sample=dict(display_number=49, sample_id=labels[48]['sample_id'], EAS=0, Strict=0),
        formal_validator_passed=False,
        disclosure=DISCLOSURE, provenance=provenance,
        protected_files_sha256=before,
        labels_path=paths['labels'].relative_to(WORK).as_posix(),
        completed_page_path=paths['page'].relative_to(WORK).as_posix(),
    )
    raw_labels, raw_html = encoded(document), html.encode('utf-8')
    receipt['labels_sha256'] = hashlib.sha256(raw_labels).hexdigest()
    receipt['completed_page_sha256'] = hashlib.sha256(raw_html).hexdigest()
    for path, content in [(paths['labels'], raw_labels), (paths['page'], raw_html),
                          (paths['receipt'], encoded(receipt))]:
        with path.open('xb') as stream:
            stream.write(content)
    assert before == {p.relative_to(WORK).as_posix(): filehash(p) for p in protected}
    print(json.dumps(dict(completed=60, reviewer=REVIEWER, missing=0, unknown=1,
                          generation_failures=1, outputs=[p.relative_to(WORK).as_posix() for p in paths.values()]), ensure_ascii=False))


if __name__ == '__main__':
    main()
