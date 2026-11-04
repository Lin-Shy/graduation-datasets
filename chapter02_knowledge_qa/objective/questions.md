# 客观题200题

全量评价，不设开发集或测试留出集。此文件仅含公开题目，答案与证据仅在评分侧。

## OBJ-001 · fill

我希望破裂边界上的面可以分别破裂，而不是只控制整个补丁。应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-002 · fill

耦合破裂边界需要按两侧场值之差判定，而不是按两侧最大值。应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-003 · fill

pressure破裂模型要读取的压力场不叫p，应使用哪个键指定场名？请只填原始键名或选项，区分大小写。

## OBJ-004 · fill

配置pressure破裂模型时，需要设置参考压力，应填写哪个键？请只填原始键名或选项，区分大小写。

## OBJ-005 · fill

我需要给pressure破裂模型设定破裂压力阈值，应填写哪个键？请只填原始键名或选项，区分大小写。

## OBJ-006 · fill

impulse破裂模型要读取自定义名称的冲量场，应使用哪个键指定？请只填原始键名或选项，区分大小写。

## OBJ-007 · fill

我需要给impulse破裂模型填写破裂冲量阈值，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-008 · fill

field破裂模型只使用一组“场名及阈值”，这种单组输入使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-009 · fill

field破裂模型要在同一个列表里填写多组“场名及阈值”，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-010 · fill

我准备把field破裂模型的场名列表和阈值列表分开填写，其中场名列表使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-011 · fill

globalTemperatureCoupled需要读取邻居侧的温度场，指定其名称的键是什么？请只填原始键名或选项，区分大小写。

## OBJ-012 · fill

globalTemperatureCoupled需要指定邻居侧的换热系数字段，使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-013 · fill

globalTemperatureCoupled需要指定本侧的换热系数字段，使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-014 · fill

globalTemperatureCoupled需要读取邻居侧的辐射热流，使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-015 · fill

我需要控制globalTemperatureCoupled是否限制温度梯度，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-016 · fill

耦合边界存在未映射位置，需要为这些位置指定温度，globalTemperatureCoupled使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-017 · fill

我在填写constantMass粒径模型的参考状态，参考密度使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-018 · fill

我在填写constantMass粒径模型的参考状态，参考直径使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-019 · fill

我需要为reacting粒径模型指定反应速率模型，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-020 · fill

pressureBased粒径速率关系需要填写压力幂指数，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-021 · fill

pressureBased粒径速率关系中的压力单位需要缩放，应使用哪个键设置缩放因子？请只填原始键名或选项，区分大小写。

## OBJ-022 · fill

pressureBased粒径速率关系需要设置压力偏置，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-023 · fill

我在填写Arrhenius粒径速率模型的速率常数，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-024 · fill

我在填写Arrhenius粒径速率模型的活化温度，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-025 · fill

我需要在AMR计算中控制是否使用动态负载均衡，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-026 · fill

部分耦合边界不能被细化或粗化，应在哪个键中列出这些patch名称？请只填原始键名或选项，区分大小写。

## OBJ-027 · fill

我需要调整细化区域外增加的缓冲层数，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-028 · fill

我需要调整粗化操作的缓冲层数，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-029 · fill

我需要控制相邻两次细化操作之间间隔多少个时间步，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-030 · fill

我需要控制相邻两次粗化操作之间间隔多少个时间步，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-031 · fill

我需要控制相邻两次负载均衡之间间隔多少个时间步，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-032 · fill

我希望到指定时刻后才允许开始网格细化，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-033 · fill

我希望到指定时刻停止网格细化，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-034 · fill

起爆前初始误差很小，但我希望暂时保留预细化网格，应使用哪个键推迟粗化开始时刻？请只填原始键名或选项，区分大小写。

## OBJ-035 · fill

我希望到指定时刻停止网格粗化，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-036 · fill

我希望到指定时刻后才允许开始动态负载均衡，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-037 · fill

我希望到指定时刻停止动态负载均衡，应设置哪个键？请只填原始键名或选项，区分大小写。

## OBJ-038 · fill

我想把单元和点的细化等级写成场进行可视化，应打开哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-039 · fill

我需要给误差估计器设置开始细化的误差下限，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-040 · fill

我需要给误差估计器设置停止细化的误差上限，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-041 · fill

我需要设置误差较高时重新允许粗化的上限阈值，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-042 · fill

我需要控制包含探针位置的网格是否允许细化，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-043 · fill

我在配置blastProbes采样点，需要列出探针坐标，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-044 · fill

重启动后希望把采样结果追加到已有blastProbes文件，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-045 · fill

blastProbes探针未落在网格内，我希望允许调整其位置，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-046 · fill

我想检查blastProbes实际采样点的位置，并将它们输出成VTK文件，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-047 · fill

我需要为blastProbes选择采样插值方法，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-048 · fill

我需要控制重启动时是否重置fieldMinMax累计的极值，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-049 · fill

我需要指定fieldMinMax记录最小值还是最大值，应使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-050 · fill

我希望在常规输出之外的若干指定时刻写出场，writeTimeList中的时刻列表使用哪个键？请只填原始键名或选项，区分大小写。

## OBJ-051 · fill

我想让blastMachNo针对指定相计算马赫数，使用哪个键指定相名？请只填原始键名或选项，区分大小写。

## OBJ-052 · fill

dynamicPressure需要使用自定义名称的密度场，应使用哪个键指定？请只填原始键名或选项，区分大小写。

## OBJ-053 · fill

我希望overpressure函数对象把超压场保存在仿真中供后续采样，应设置哪个开关？请只填原始键名或选项，区分大小写。

## OBJ-054 · fill

我用setRefinedFields准备网格，需强制三维细化以便标准OpenFOAM求解器使用，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-055 · fill

这次运行setRefinedFields只想设置场而不细化网格，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-056 · fill

运行setRefinedFields时不想写出细化历史，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-057 · fill

运行setRefinedFields时不想写出场文件，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-058 · fill

setRefinedFields需要更新当前时刻所有场的尺寸，使场的大小与网格对应，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-059 · fill

setRefinedFields完成赋值后需要评估并修正边界条件，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-060 · fill

setRefinedFields本次不应设置单元内部值，应加哪个选项？请只填原始键名或选项，区分大小写。

## OBJ-061 · short

我想参照axisymmetricCharge配置C4材料，它的未反应物用了什么输运模型？只填模型名。

## OBJ-062 · short

热力学计算里，控制温度正值限制的是哪个开关？只填键名。

## OBJ-063 · short

reacting这个例子的气体输运模型是什么？只填模型名。

## OBJ-064 · short

axisymmetricCharge这个例子用了哪种网格类？只填类名。

## OBJ-065 · short

axisymmetricCharge设定算到什么时刻？只填控制文件中的数值。

## OBJ-066 · short

我想确认axisymmetricCharge的数值方法，它用的通量格式叫什么？只填名称。

## OBJ-067 · short

axisymmetricCharge里，C4未反应物选了什么热量模型？只填模型名。

## OBJ-068 · short

热力学动态编译想用自己改过的模板，该用哪个条目指定模板目录？只填键名。

## OBJ-069 · short

reacting例子用的热量模型是什么？只填模型名。

## OBJ-070 · short

axisymmetricCharge是用什么误差估计器决定细化的？只填名称。

## OBJ-071 · short

axisymmetricCharge的常规写出间隔设了多少？只填控制文件中的数值。

## OBJ-072 · short

building3D例子里deltaT设了多少？只填配置数值。

## OBJ-073 · short

axisymmetricCharge用什么时间推进方法？只填名称。

## OBJ-074 · short

axisymmetricCharge里，C4未反应物用的状态方程是什么？只填模型名。

## OBJ-075 · short

物性查表想用线性插值，表外也继续外推，应该选哪种格式？只填格式名。

## OBJ-076 · short

reacting例子用的状态方程是什么？只填模型名。

## OBJ-077 · short

axisymmetricCharge最多允许细化几级？只填配置数值。

## OBJ-078 · short

delayedDetonation例子设定从什么时候开始允许粗化？只填配置数值。

## OBJ-079 · short

axisymmetricCharge里，C4未反应物的参考密度是多少？只填原文件单位下的数值。

## OBJ-080 · short

building3DWorkshop里，C4未反应物状态方程的参考压力是多少？只填原文件单位下的数值。

## OBJ-081 · short

delayedDetonation里，RDX未反应物的参考密度是多少？只填原文件单位下的数值。

## OBJ-082 · short

axisymmetricCharge把最大Courant数设成多少？只填配置数值。

## OBJ-083 · short

我想通过fvModels加源项，这个字典应该放在算例的哪个目录？只填目录名。

## OBJ-084 · short

axisymmetricCharge里算压力冲量时，参考压力设成多少？只填原文件单位下的数值。

## OBJ-085 · short

axisymmetricCharge里，C4未反应物的定容比热是多少？只填原文件单位下的数值。

## OBJ-086 · short

delayedDetonation里，RDX未反应物的定容比热是多少？只填原文件单位下的数值。

## OBJ-087 · short

我想统计边界上的压力和黏性作用力，需要加载哪个库？只填带扩展名的库名。

## OBJ-088 · short

初始压力想按位置函数赋值，setRefinedFields该选哪种赋值类型？只填类型名。

## OBJ-089 · short

动态负载均衡后的并行结果，blastFoam该用哪个工具重构？只填工具名。

## OBJ-090 · short

building3DWorkshop的表面采样写出间隔设了多少？只填配置数值。

## OBJ-091 · short

拉格朗日粒子的位置数据想转成ParaView能读的格式，该用哪个工具？只填工具名。

## OBJ-092 · short

气—颗粒流的single界面速度模型应该取哪一相的速度？只填相的类型。

## OBJ-093 · single

pressureAndImpulse里，压力和冲量需要都达到阈值才破裂吗？请选择手册支持的触发关系。

A. 只检查压力，忽略冲量阈值
B. 只检查冲量，忽略压力阈值
C. 压力与冲量必须同时满足
D. 压力或冲量任一判据满足

## OBJ-094 · single

使用burst系列边界时，哪个条目指定破裂前的场边界条件？

A. brokenField
B. initialPatch
C. finalCondition
D. intactField

## OBJ-095 · single

按手册构造cyclic系列破裂边界时，应使用哪个工具？

A. createBaffles
B. decomposePar
C. postProcess
D. setFields

## OBJ-096 · single

我给边界用了冲量破裂判据，还需要怎样提供冲量场？

A. 只要填写名称，破裂模型就必然自行生成冲量场
B. 运行中必须有冲量场，可由impulse函数对象或其他计算途径提供
C. 仅在初始时刻写一次压力场即可替代冲量
D. 把压力p直接用作冲量而无需积分

## OBJ-097 · single

我直接改boundary文件设置破裂边界，模型参数应该放在哪儿？

A. 与各patch并列的全局burstModel字典内
B. FoamFile头字典的object条目内
C. 只写进0/p的boundaryField，不需要边界patch中的模型设置
D. 对应的patch条目内

## OBJ-098 · single

constant粒径模型对直径场输出的规定是什么？

A. 只写压力场并改名为直径
B. 不写出直径场
C. 每步必写直径场
D. 仅并行时写直径场

## OBJ-099 · single

要根据参考密度、参考直径保持颗粒质量确定当前直径，应选哪个模型？

A. fieldValue
B. constantMass
C. constant
D. reacting

## OBJ-100 · single

reacting粒径模型如何表示局部粒径变化？

A. 只修改网格单元体积
B. 把压力场直接作为直径场
C. 在粒径输运方程中加入反应速率源项
D. 始终固定为初始直径

## OBJ-101 · single

当pressureBased粒径反应关系使用MPa而原压力用Pa时，pScale应取多少？

A. 1e6
B. 1e-6
C. 1
D. 1e-3

## OBJ-102 · single

reacting粒径方程右端的k代表什么？

A. 指定的反应速率
B. 热导率
C. 网格细化等级
D. 湍动能初值

## OBJ-103 · single

爆轰尚未开始且初始误差很小，需要暂时保留预细化网格，应主要设置哪个时间控制？

A. beginBalance
B. beginUnrefine
C. writeInterval
D. endRefine

## OBJ-104 · single

movingAdaptiveFvMesh推荐用哪种网格运动求解器？

A. displacementLaplacian
B. displacementSBRStress
C. velocityLaplacian
D. velocityComponentLaplacian

## OBJ-105 · single

对snappyHexMesh网格使用二维或轴对称AMR，手册对切割区域原细化级别提出什么限制？

A. 所有级别均无条件支持
B. 必须至少level 3
C. 只能使用负数级别
D. 只能在level 0切割

## OBJ-106 · single

从面误差得到单元中心误差时，手册采用哪种汇总？

A. 随机选一个面
B. 各面误差最小值
C. 各面误差最大值
D. 各面误差的带符号和

## OBJ-107 · single

fieldValue选压力p时，其误差量直接对应什么？

A. 相邻压力差的平方
B. 求解器迭代残差
C. 压力场本身的值
D. 压力相对实验真值的误差

## OBJ-108 · single

相邻单元的标量值完全相同时，delta误差是多少？

A. 无穷大
B. 该标量的绝对值
C. 0
D. 1

## OBJ-109 · single

scaledDelta里的minValue主要起什么作用？

A. 限制原始场值的最大值
B. 为缩放分母设置下限
C. 作为固定值替代所有相邻差值
D. 规定相邻场值必须大于该值才计算误差

## OBJ-110 · single

densityGradient误差估计使用哪一种密度？

A. 仅炸药未反应物密度
B. 总密度
C. 固定为环境密度
D. 任意指定的温度场

## OBJ-111 · single

手册中Lohner误差估计的设计取值范围是什么？

A. 0到1
B. 负1到0
C. 1到无穷大
D. 任意带量纲压力

## OBJ-112 · single

我用multiComponent同时看压力和体积分数，它们允许的最大细化级别必须一样吗？

A. 可以在各子估计器字典中分别设置
B. 只能设置一个全局级别，子字典不能设置
C. 只有列表中第一个子估计器的设置有效
D. 两个指标的最大级别必须都等于1

## OBJ-113 · single

大算例开动态负载均衡后崩了，手册提醒过哪种数据传输风险？

A. 处理器间传输超过MPI缓冲限制
B. 只要达到两进程就必定超过限制
C. 仅修改writeInterval即可保证避免所有传输问题
D. 所有标准blastFoam场在任何规模下均保证传输稳定

## OBJ-114 · single

blastProbes的append设置主要解决什么使用问题？

A. 重启时自动删除原采样
B. 把两个不同物理探针的坐标自动合并
C. 让重启动后的采样继续使用同一探针文件
D. 把已有压力值重新计算成新时间步的求解结果

## OBJ-115 · single

曲面附近有些blastProbes探针找不到，允许调整位置后会怎么处理？

A. 保持原坐标并把缺失样本作为已验证压力
B. 将未找到的探针移到最近的面以便采样
C. 自动把任意外部坐标镜像到域中心
D. 自动修改计算域使原坐标变成内部点

## OBJ-116 · single

AMR细化或粗化后探针曲线有跳动，手册建议检查哪个设置？

A. 只增加探针写出频率，不调整网格处理
B. 只开启append以连接重启文件
C. 只开启adjustLocations以处理域外采样点
D. 允许包含探针位置的网格细化，即refineProbes

## OBJ-117 · single

fieldMinMax输出的是整个域的一个极值，还是分布在网格上的极值？请选择其空间含义。

A. 整个域只输出一个标量
B. 域中每个单元的极值场
C. 只在每个patch上输出一个汇总值
D. 只在每个处理器子域输出一个汇总值

## OBJ-118 · single

需要在常规输出间隔之外的指定时刻保存场，应使用什么函数对象？

A. dynamicPressure
B. blastMachNo
C. impulse
D. writeTimeList

## OBJ-119 · single

我想检查场的整体量有没有变化，conservedQuantities给的是什么统计？

A. 边界面通量的面积积分及全部注入修正
B. 所选场在单个探针点的时间积分
C. 场的体积积分及初始/当前值和差值
D. 每个单元残差的最大值与最小值

## OBJ-120 · single

有流入流出时，用conservedQuantities检查守恒要注意什么？

A. 自动根据全部边界条件修正净注入量
B. 只计算边界通量而不计算体积积分
C. 已自动精确计入域内所有移除和注入
D. 当前未把从域中移除和向域中注入的量纳入核算

## OBJ-121 · single

VTK表面输出旁边的.series文件有什么用？

A. 把各时刻场做时间平均
B. 让ParaView按正确时间顺序读取表面文件
C. 把离散时刻重算为新的仿真状态
D. 将表面场自动转为全域体积场

## OBJ-122 · single

Schlieren/grad可以处理哪些类型的场？

A. 标量场和向量场
B. 仅标量场，不支持向量场
C. 仅向量场，不支持标量场
D. 任意阶张量场均可直接输入

## OBJ-123 · single

shadowgraph/laplacian函数对象计算什么？

A. 给定场的时间积分
B. 给定场的拉普拉斯
C. 仅场的初始值
D. 仅场的最大值

## OBJ-124 · single

blastMachNo使用哪一类声速计算马赫数？

A. 压力与时间的乘积
B. 固定取340且不看模型
C. blastFoam专用热力学模型计算的声速
D. 网格运动速度的最大值

## OBJ-125 · single

dynamicPressure为什么输出一个向量，它的模对应什么量？

A. 输出标量，值等于p-pRef
B. 输出向量，其模等于rho*|U|而不含速度平方
C. 输出向量，其模等于常规定义的动压
D. 输出标量，值等于压力的时间积分

## OBJ-126 · single

overpressure与压力p、参考压力pRef是什么关系？

A. pRef-p
B. p+pRef
C. p-pRef
D. p/pRef

## OBJ-127 · single

impulse到底对什么压力作时间积分？

A. 包含参考压力的绝对压力p
B. 相对pRef的超压
C. rho*|U|^2/2的动压
D. 未减参考值的总能量密度

## OBJ-128 · single

按该版手册，timeOfArrival记录哪个时刻？

A. 计算开始的时刻
B. 必然是首个非零压力时刻
C. 所有峰值时刻的算术平均
D. 最大压力达到的时刻

## OBJ-129 · single

setRefinedFields的细化选项应写在哪个字典？

A. dynamicMeshDict
B. setFieldsDict
C. transportProperties
D. decomposeParDict

## OBJ-130 · single

setRefinedFields迭代细化到什么条件才会停？

A. 第一次设置场后无条件停止
B. 只要还有任意非零梯度就永不停止
C. 网格不再变化或达到最大迭代次数
D. 只能达到最大迭代次数才停止，网格稳定也继续

## OBJ-131 · single

setRefinedFields没选误差估计器时，靠什么决定细化？

A. 默认对每个场使用Lohner误差估计器
B. 默认只有指定误差估计器后才允许细化
C. 默认按原网格层级作均匀细化，不查看所设场
D. 所跟踪场存在局部变化时即可触发细化

## OBJ-132 · single

细化后想用回原来的场值，InitialValue具体做了什么？

A. 从最近的已存在时间目录做线性时间插值
B. 将原场替换成统一初值
C. 读取并保存当前场，在细化后使用原值
D. 只保存网格的细化级别而不读取场

## OBJ-133 · single

blastToVTK默认输出什么编码的文件？

A. 二进制VTK
B. ASCII VTK
C. 分别沿用每个输入场的编码作为默认规则
D. 必须显式选择编码才会输出

## OBJ-134 · single

我想导出更密的VTK动画帧，blastToVTK的-dt会怎样处理？

A. 重新求解原案例并改写原始时间步
B. 按指定间隔输出插值的中间时刻
C. 只选择已有时刻且绝不插值
D. 只改变VTK文件名，不影响输出时刻

## OBJ-135 · single

blastFoam的phaseProperties未给出phases关键字时，选择什么模式？

A. 强制拉格朗日颗粒求解
B. 单相求解
C. 自动三相求解
D. 必然只求固体变形

## OBJ-136 · single

按配套手册，blastEulerFoam正式支持哪类模拟？

A. 仅流体—流体多流体模拟
B. 当前正式支持流体—固体模拟
C. 已正式验证流体—流体和流体—固体全部组合
D. 仅单流体多相，共享唯一速度而无多流体相模型

## OBJ-137 · single

我想把不同颗粒组分别建相，blastEulerFoam对颗粒相数量怎么规定？

A. 必须把所有颗粒合为同一个相
B. 可使用任意数量的颗粒相
C. 只能在无气体相时增加颗粒相
D. 颗粒相只能有两个且不能扩展

## OBJ-138 · single

blastEulerFoam中描述固体相的相模型名称是什么？

A. granular
B. fluid
C. singleGas
D. multiphase

## OBJ-139 · single

blastFSIFoam在耦合边界间传信息，用的底层补丁机制叫什么？

A. globalTemperatureCoupled
B. cyclicAMI
C. processor
D. coupledGlobalPolyPatch

## OBJ-140 · single

blastReactingFoam的热物性要按哪套热力学类配置？

A. 标准OpenFOAM热力学类
B. 只支持blastFoam的JWL热力学类
C. blastFoam专用类与标准类可不经核对任意混用
D. 只支持blastFoam的Murnaghan热力学类

## OBJ-141 · single

blastParcelFoam能同时开AMR和动态负载均衡吗？

A. AMR和动态负载均衡均支持
B. AMR和动态负载均衡均不支持
C. 只支持动态负载均衡，不支持AMR
D. 支持AMR，但不支持动态负载均衡

## OBJ-142 · single

blastMultiRegionFoam里，固体热传输是怎样求解的？

A. 与流体完全相同，所有项均显式推进
B. 只对固体温度施加固定边界，不求固体内部传输
C. 用颗粒碰撞闭合替代固体传热方程
D. 仍以矩阵求解方式隐式处理

## OBJ-148 · judge

在GidaspowErgunWenYu模型中，连续相体积分数降到0.80后，我仍按WenYu分支计算阻力，认为这符合切换规则。这个处理正确吗？

## OBJ-149 · judge

某个其他模型仍要用Nusselt数，但这次计算准备忽略相间传热。我选择noneNu来处理这种需求，是否符合它的用途？

## OBJ-163 · judge

用了constant升力模型后，我只把Cl保持为常数，仍在计算中使用局部速度差、旋度等量更新升力传递项。这样理解constant是否正确？

## OBJ-166 · judge

我用initializeAtmosphere的tabulated方式按高度给定压力和温度后，还希望做一次静水平衡修正，认为这个工具仍允许这一步。这个判断正确吗？

## OBJ-144 · judge

我想计算两种流体之间的传质，认为随附版本列出的相间质量传递模型已经支持流体到流体，可以直接按这个能力来选型。这一判断正确吗？

## OBJ-164 · judge

体系只有一种颗粒相，我认为不需要为多个颗粒相之间再配置第4.7节所说的颗粒相间拖曳闭合。这个判断正确吗？

## OBJ-145 · judge

准备用YuStandish计算堆积极限，我先把颗粒相按粒径从小到大排序，再按这一顺序组织模型输入。这种准备方式符合模型假设吗？

## OBJ-165 · judge

让calculateImpulse处理超压探针文件时，我没有手动覆盖参考压力，认为它默认按pRef=0积分，不会再扣一遍环境压强。这个理解正确吗？

## OBJ-151 · judge

配置气—颗粒流的single相间压力模型时，我把phase指向气相，让界面压力使用气相压力。这个选择符合手册建议吗？

## OBJ-169 · judge

准备把createTimeSeries生成的.series交给另一目录使用时，我认为默认写入的已经是绝对路径，因此不用因为路径类型而额外处理。这个前提正确吗？

## OBJ-152 · judge

一个温度型状态方程相已经给了初始p、rho、T，未提供e，也未定义calculateDensity。我认为它默认会用p和rho初始化e，这个判断正确吗？

## OBJ-155 · judge

初始条件中除了rho、p、T，还提供了e。我认为初始化会由rho和e直接计算p、T，而不是保证p、T内部值原样保留。这个理解正确吗？

## OBJ-150 · judge

配置颗粒应力模型时，我认为既然已经选了颗粒黏性模型，摩擦模型描述的多次碰撞贡献就已经算在里面，无需再区分。这个判断正确吗？

## OBJ-157 · judge

后处理时已有h、p和rho，我打算按e=h+p/rho换算内能。这个换算正确吗？

## OBJ-158 · judge

检查两/多相混合物初始化时，我没有另外指定求根算法，认为初始内能和温度默认用Newton-Raphson求解。这个理解正确吗？

## OBJ-171 · judge

多区域传热研究希望引入ODE时间积分与Riemann通量，我把blastMultiRegionFoam作为候选，认为这两点与其说明的数值路线一致。这个选型依据成立吗？

## OBJ-156 · judge

为包含不同粒径颗粒相的体系选择Princeton颗粒黏性模型时，我认为它的适用范围包含多分散流。这一选型依据成立吗？

## OBJ-153 · judge

只需要一个起爆点，又不想手工估算装药中心坐标，我准备使用useCOM取单个装药的质心作为起爆点。这样使用符合说明吗？

## OBJ-159 · judge

我把linear后燃的总能量Q0保持不变，把tEnd-tStart加倍，并认为各自有效时间窗口内的单位时间加能率仍保持原值。这个判断正确吗？

## OBJ-146 · judge

某相不需要额外后燃能量，我没有在相字典里写afterburnModel，认为会默认使用none而不添加额外后燃能量。这个理解正确吗？

## OBJ-143 · judge

准备ePolynomial输入时，我按常数项到T的7次幂依次给了8个多项式系数。只就系数数量而言，这样填写符合模型定义吗？

## OBJ-160 · judge

我在核对颗粒应力计算，当前速度场的div(u)不为0，准备直接用对称速度梯度D代替式(4.1)的S，认为二者相同。这个替换正确吗？

## OBJ-162 · judge

准备eTabulated内能表时，我只写热学部分，打算让模型自动补上状态方程的内能贡献，认为这样不会漏项。这个做法正确吗？

## OBJ-167 · judge

配置一个multicomponent流体热力学模型时，我准备让每个species分别选择不同的状态方程类型，认为该模型可以直接这样组合。这一理解正确吗？

## OBJ-170 · judge

准备blastFSIFoam算例时，我把流体区域按固定网格的求解方式理解，理由是该求解器的流体相采用静止网格。这个理解符合说明吗？

## OBJ-147 · judge

我想降低拖曳松弛的计算开销，准备把解析解换成ODE求解，理由是手册认为ODE更省计算。这个选择理由成立吗？

## OBJ-154 · judge

两相密度不同，我选择massAveraged界面速度模型，却按两相体积分数加权计算速度，认为这就是该模型的平均方式。这个理解正确吗？

## OBJ-168 · judge

重启后我只想合并p这个探针字段，准备使用mergeProbes的-force来完成字段筛选。这个选项用法正确吗？

## OBJ-161 · judge

想为RanzMarshall传热更换Nu关联式，但有人说一旦选了RanzMarshall，Nu就固定为2，不能再选择其他Nu模型。这个说法正确吗？

## OBJ-172 · judge

给多个颗粒相整理碰撞模型时，我计划分别考虑同类和不同类颗粒相之间的径向分布关系，而不只准备同类项。这个区分有模型依据吗？

## OBJ-173 · short

eConst的参考温度不填时，默认是多少K？只填数值。

## OBJ-174 · short

固体导热各向同性、导热系数又是常量，应该用哪个固体输运模型？只填模型名。

## OBJ-175 · short

JWL里，当前密度是参考密度的两倍时，相对体积V是多少？只填数值。

## OBJ-176 · short

idealGas的比热比用哪个键设置？只填键名。

## OBJ-177 · short

BirchMurnaghan3中，体积模量随压力的变化率用哪个键设置？只填键名。

## OBJ-178 · short

基础internalDetonation例子里，C4用了哪个后燃模型？只填模型名。

## OBJ-179 · short

后燃进度ci的对流格式和限制器应该在哪个文件设置？只填文件名。

## OBJ-180 · short

ArrheniusRate低温反应分支里，粒径项的幂指数是多少？只填数值。

## OBJ-181 · short

反应物和产物性质混合时，lambdaPow不设置默认是多少？只填数值。

## OBJ-182 · short

pressureBased里，限制点火项可用的最大反应进度应设置哪个键？只填键名。

## OBJ-183 · short

我不想输运反应进度，希望一开始就全部激活，应该用哪个激活模型？只填模型名。

## OBJ-184 · short

我想把已有流场旋转后映射到另一套网格，向量和张量也要跟着旋转，应使用哪个工具？只填工具名。

## OBJ-185 · short

cellSize按分量控制最小尺寸时，应该用哪个键填写最小尺寸向量？只填键名，保留大小写。

## OBJ-186 · short

scaledDelta的offset不填，默认是多少？只填数值。

## OBJ-187 · short

我想按质量设置一个盒状区域，setRefinedFields里用哪种单元集合？只填类型名。

## OBJ-188 · short

带障碍物和玻璃的internalDetonation例子里，窗户用了哪种破裂patch？只填类型名。

## OBJ-189 · short

building3D例子里，切割STL几何那一步用的是什么工具？只填程序名。

## OBJ-190 · short

哪个实验性求解器是在Xi-Foam基础上扩展，用来描述爆燃向爆轰转捩的？只填名称。

## OBJ-191 · short

globalTemperatureCoupled的未映射温度unmappedT，默认数值是多少？只填数值。

## OBJ-192 · short

我在填写相属性，molWeight应该放在哪个子字典？只填子字典名。

## OBJ-193 · short

building3DWorkshop的手写探针示例要加载哪个共享库？只填带扩展名的文件名。

## OBJ-194 · short

除了拖曳和传热，其余相间模型一般用什么显式时间积分方法？只填英文姓氏。

## OBJ-195 · short

按SchillerNaumann关系，Reij=1000时CD乘Reij是多少？只填数值。

## OBJ-196 · short

RanzMarshall换热项里的粒径是以几次方出现在分母中的？只填指数数值。

## OBJ-197 · short

duct关联式里Pr的幂指数是多少？只填数值。

## OBJ-198 · short

CarnahanStarling径向分布模型仅适用于什么粒径分布的颗粒流？只填类型名称，可用中文或英文。

## OBJ-199 · short

FedorsLandel堆积模型针对几个组分的混合物？只填组分数。

## OBJ-200 · short

exponential固体导热模型在参考温度下的导热系数由哪个参数给出？只填键名。

