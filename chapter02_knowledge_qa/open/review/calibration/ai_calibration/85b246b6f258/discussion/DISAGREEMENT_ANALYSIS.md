# 评分分歧与失败原因逐项分析

2026-11-04；现有结果分析。仅保留原评分、分歧与失败的解释，不列改进待办。表格统一标注“人工参考”，原始评分与来源记录保留。未修改人工评分、题目、Gold、裁判提示或运行协议，未发出模型请求。

主清单按双均值与人工参考的EAS_arith绝对差异排序取12条，平分按原显示序号排序；再补2条“均值掩盖个别裁判差异”的样本。完整60条仍在[逐答表](../DISAGREEMENTS.md)，不将这些挑出的案例用于重新计算总体分数。

|序号|题目|人工参考|GPT|DeepSeek|双均值|均值−人工|两裁判差|
|---:|---|---:|---:|---:|---:|---:|---:|
|13|E28-01|56.25|75.00|81.25|78.12|21.88|6.25|
|3|E53-07|45.83|45.83|12.50|29.17|-16.67|33.33|
|28|E42-03|37.50|20.83|20.83|20.83|-16.67|0.00|
|19|P06-03|33.33|45.83|54.17|50.00|16.67|8.33|
|25|E42-01|62.50|81.25|75.00|78.12|15.62|6.25|
|36|E33-01|81.25|68.75|62.50|65.62|-15.62|6.25|
|37|E28-01|25.00|56.25|25.00|40.62|15.62|31.25|
|31|P09-01|47.22|36.11|27.78|31.94|-15.28|8.33|
|59|N60-03|27.78|47.22|36.11|41.67|13.89|11.11|
|48|P08-01|50.00|38.89|38.89|38.89|-11.11|0.00|
|29|E48-03|25.00|45.83|25.00|35.42|10.42|20.83|
|46|N67-02|37.50|54.17|41.67|47.92|10.42|12.50|
|34|N60-02|100.00|83.33|100.00|91.67|-8.33|16.67|
|47|P08-01|75.00|86.11|69.44|77.78|2.78|16.67|

第13份为双均值误差最大（+21.875分）；第3份为单裁判绝对误差最大（DeepSeek −33.33分），也是两裁判差异最大（33.33分）。第37份的GPT +31.25分为GPT自身最大绝对误差。第28份两AI一致却与人工不同，说明一致不能替代人工参考。重复题目ID保留各自回答，不当作独立知识样本。

## 第13份 · E28-01：正确功能与错误配置层级混在一起

**问题**：在 blastFoam 的 burst 补丁体系中，手册说明所有字段都需要在其字典中额外增加一个条目来指定“破裂前”的边界条件。这个条目的名称是什么，它被用来做什么？同时，手册指出该条目应放在哪个字典层级？

**原回答**：

在 blastFoam 的 burst 补丁体系中，手册说明所有字段都需要在其字典中额外增加一个条目来指定“破裂前”的边界条件。该条目的名称是 "intactField"，它被用来指定字段在破裂前的边界条件。该条目应放在字典的顶层，即在 burstModel 的配置层级下。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E28-01.K1=1、E28-01.K2=0.25|0.6250|0.5|not_applicable|56.25|
|GPT|E28-01.K1=1、E28-01.K2=0.5|0.7500|0.75|not_applicable|75.00|
|DeepSeek|E28-01.K1=1、E28-01.K2=0.75|0.8750|0.75|not_applicable|81.25|

**当前Gold必要点**：

- `E28-01.K1`：该额外条目的名称是 intactField，用于指定字段在破裂之前的边界条件。
- `E28-01.K2`：该条目属于字段字典中的额外条目，而非补丁类型本身的定义。

**分歧观察与解释**：

回答给出intactField与破裂前边界条件，但将“字典顶层”解释为burstModel配置层级。两AI对名称/用途给了较高部分分，对末尾层级错误的事实扣分较人工轻。

Gold的K2与回答包含的层级表述并不完全对应；不得仅看到“字典”一词判满分。此处是错误严重程度及复合必要点的部分分争议，不是两个AI一致即可推翻人工。


**来源依据**：

- [manual/markdown/07_burst_patches.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/07_burst_patches.md:1)，L1—L12；文件SHA256 `1c4fd9c6a681b0f0ad846967ff49ddc2737e234aa01e39536f41f493418c8097`。

<details><summary>已核对原文摘录</summary>

> # Burst patches
>
> The ability to have a "bursting" patch can be used with the burst (external patch), burstCyclic (internal with no AMR), or burstCyclicAMI (general internal). All fields require an additional entry in their dictionaries name "intactField" which is used to specify the boundary condition of the field before bursting. The basic burst patch can be created using any mesh generation technique, however the cyclic variations require using the createBaffles utility, standard to OpenFOAM. See Sec. 20.5 for an example of how to create and use the patches.
>
> ## 7.1 Burst models
>
> The method to calculate where burst occurs is runtime-selectable and the inputs are placed in the constant/polyMesh/boundary file under the corresponding boundary. This can also be added in either the patch entry within blockMeshDict of snappyHexMeshDict.
>
> | Variable | Description |
> |---|---|
> | partialBurst | Can individual face burst (no by default) |
> | useDelta | Us the difference across coupled patches rather than the maximum value (yes by default) |

</details>

**已记录备注**：

人工参考：第13份；F：名称与功能正确，最后关于配置层级的说明存在重要错误。；intactField名称及用途正确。；开头提字段字典，但最后混淆为burstModel配置层级。
GPT：条目名称和用途正确；字典层级的表述存在局部错误。；正确指出是字典中的额外条目，但将其定位为 burstModel 配置层级，未准确表达其应属于各字段字典。
DeepSeek：名称和用途正确；但关于条目所在字典层级的表述不准确，手册并未将其置于 burstModel 配置层级。；正确给出条目名称 intactField，并说明用于指定字段破裂前的边界条件。；表达了该条目是字段字典中的额外条目，但结尾又将其位置表述为 burstModel 配置层级，造成层级归属不够准确。

## 第3份 · E53-07：自相矛盾的回答与“核心结论反向”

**问题**：我给Mie-Grüneisen相准备了初始p、rho、T，没有提供内能场，但在状态方程字典中设了calculateDensity yes。初始化时会先处理rho还是内能？内能计算会直接沿用原rho，还是要等密度重算后再进行？

**原回答**：

在Mie-Grüneisen模型中，初始化时会先处理密度（rho），然后再计算内能。由于没有提供内能场，模型会根据状态方程字典中的设置（calculateDensity yes）计算密度。因此，内能计算会直接沿用初始的rho值，而不是等密度重算后再进行。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E53-07.K1=0.75、E53-07.K2=0|0.3750|0.5|0.5|45.83|
|GPT|E53-07.K1=0.75、E53-07.K2=0|0.3750|0.5|0.5|45.83|
|DeepSeek|E53-07.K1=0.25、E53-07.K2=0|0.1250|0.25|0|12.50|

**当前Gold必要点**：

- `E53-07.K1`：先用p、T计算rho。
- `E53-07.K2`：密度重算后再初始化内能，不跳过前一步沿用原rho；允许准确说明更新后的rho的用途。

**分歧观察与解释**：

前面说先处理rho、后算内能，末尾又说内能沿用初始rho。GPT与人工一致；DeepSeek将A降至0，两个AI相差33.33分。

既有规则“核心结论反向A=0”与“局部错误可给部分分”缺少冲突处理顺序，当前材料不足以断言某一方必然错。


**来源依据**：

- [manual/markdown/05_fluid_solid_thermo.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/05_fluid_solid_thermo.md:1412)，L1412—L1414；文件SHA256 `e8369aa14525d4c3adb639ae6e134af41d6d97d84484f114ef221e63c141f8dc`。

<details><summary>已核对原文摘录</summary>

> ## 5.9 Initialization
>
> The initialization of fields can be handled in several ways, but $\rho_i$, $p$, and $T$ must be given as initial conditions. Some of these fields may be overwritten, but the boundary conditions are used to construct the conserved quantities. For equations of state in the Mie-Grüneisen form, by default the pressure and density are used to initialize the internal energy. Temperature based equations of state initialize the internal energy using the density and temperature. If the "calculateDensity" keyword is defined, and is set to "yes" in the given equation of state dictionary, then the density is calculated from the pressure and temperature prior to the initialization of the internal energy. Each of the initialization methods use a Newton-Raphson root finding method to find the necessary quantities. If the internal energy field is provided in the initial conditions folder, the pressure and temperature fields are calculated directly from the density and internal energy.

</details>

**已记录备注**：

人工参考：第3份；F/A：前述顺序部分正确，随后对新旧rho的选择错误，整答存在直接矛盾。；知道先处理密度，未明确由p、T重算rho。；明确主张沿用初始rho而不等待密度重算，错误。
GPT：回答正确说明了先处理密度及开关触发，但将内能使用初始rho而非更新后rho，反转了条件下的关键结论。；正确表达了先处理/计算密度且calculateDensity设为yes会触发计算，但未明确说明密度是由p、T计算得到。；明确错误地说内能沿用初始rho，而正确关系是密度重算后再初始化内能。
DeepSeek：核心条件结论反向：calculateDensity yes时应先用p、T重算密度，再据此初始化内能；回答称内能沿用原rho。；仅提到先处理密度并按开关计算密度，未明确表达用p、T重算rho，且后文否定重算结果用于内能。；明确称内能直接沿用初始rho、不等密度重算，与要求相反。

## 第28份 · E42-03：关键参数含义写反，但其余描述笼统正确

**问题**：在 blastFoam 的 AMR 中，densityGradient 误差估计器与 beginUnrefine 参数如何共同影响自由场爆炸仿真的网格演化？请结合自由场教程配置说明。

**原回答**：

在 blastFoam 的 AMR 中，densityGradient 误差估计器通过梯度信息识别需要细化的区域，而 beginUnrefine 参数控制细化的起始时间步。两者共同作用使网格在爆炸冲击波传播时自动加密，随后在冲击波衰减时逐步粗化，从而优化计算资源分配。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E42-03.K1=0.5、E42-03.K2=0、E42-03.K3=0.25|0.2500|0.5|not_applicable|37.50|
|GPT|E42-03.K1=0.25、E42-03.K2=0、E42-03.K3=0.25|0.1667|0.25|not_applicable|20.83|
|DeepSeek|E42-03.K1=0.25、E42-03.K2=0、E42-03.K3=0.25|0.1667|0.25|not_applicable|20.83|

**当前Gold必要点**：

- `E42-03.K1`：densityGradient使用总密度定义误差；自由场教程显式errorEstimator densityGradient。
- `E42-03.K2`：自由场教程beginUnrefine=1e-5，而手册将它定义为粗化可以开始的时刻，默认0 s。
- `E42-03.K3`：误差估计用于确定可细化/粗化的单元，beginUnrefine提供粗化时间准入；该实例有密度指标和延后准入两个设置，但1e-5不是已知起爆时刻，也不能单凭静态配置保证整个网格一直细化或特定运行结果。

**分歧观察与解释**：

把beginUnrefine说成细化起始时间，Gold说明它是允许粗化开始的时刻；回答还有自动加密/粗化的笼统叙述。两AI完全一致，比人工低16.67分。

两AI一致只说明共同判断，不是额外人工真值；分歧集中在错误是否已构成整答主要事实错误，而非格式。


**来源依据**：

- [manual/markdown/11_amr.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/11_amr.md:109)，L109—L131；文件SHA256 `26ca1848c6ddee2c65bc94c57a4d6745b0ca7d2412312b63791545e864f058df`。
- [tutorials/blastFoam/freeField/constant/dynamicMeshDict](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/freeField/constant/dynamicMeshDict:17)，L17—L39；文件SHA256 `7684c259e142187b8ca548daf5885292cd660d7f9601c03c85bf4adb75ca1970`。
- [manual/markdown/11_amr.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/11_amr.md:3)，L3—L44；文件SHA256 `26ca1848c6ddee2c65bc94c57a4d6745b0ca7d2412312b63791545e864f058df`。

<details><summary>已核对原文摘录</summary>

> ### 11.1.5 Density gradient (densityGradient)
>
> A modified density gradient was defined by Zheng et al. (2008), and uses an error defined by
>
> $$
> \epsilon_{\nabla\rho} = \max\left( \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{own}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{own}|},\ \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{nei}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{nei}|} \right)^{f}
> $$
> (11.4)
>
> with
>
> $$
> (\nabla\ln\rho)_{C} = \frac{\rho_{nei} - \rho_{own}}{|r_{nei} - r_{own}|}
> $$
> (11.5)
>
> $$
> (\nabla\ln\rho)_{nei,own} = \frac{(\nabla\rho)_{nei,own}(r_{nei} - r_{own})}{|r_{nei} - r_{own}|}
> $$
> (11.6)
>
> $r_{own,nei}$ is the surface normal vector, and $dl = |r_{nei} - r_{own}|$, is the distance between cell centers. This error estimator uses the total density.
> dynamicFvMesh   adaptiveFvMesh;
> errorEstimator  densityGradient;
>
> // When can unrefinement start
> beginUnrefine 1e-5;
>
> // How often to refine
> refineInterval  3;
>
> // Refine field in between lower..upper
> lowerRefineLevel 0.1;
>
> // If value < unrefineLevel unrefine
> unrefineLevel   0.1;
>
> // Have slower than 2:1 refinement
> nBufferLayers   3;
>
> // Refine cells only up to maxRefinement levels
> maxRefinement   3;
>
> // Write the refinement level as a volScalarField
> dumpLevel       true;
> The dynamic mesh classes have been incorporated from the github repository SOFTX_2018_143 and is based on the work of Rettenmaier et al. (2019). This library introduces 2-D, 2-D axisymmetic, and 3-D (present in OpenFOAM-9) all with the option to include dynamic load balancing. The original work (dynamicRefineBalanceFvMesh and dynamicRefineFvMesh) has been used as the base for the adaptiveFvMesh class. This mesh type has been further developed, specifically for compressible flows, and includes modifications for improved stability with meshes created with snappyHexMesh. Additional polyhedral refinement has been ported from foam-extend's and allows for general polygon refinement.
>
> Because the detonation of explosives may not occur when the simulation starts, the option to begin unrefinement at a designated time ("beginUnrefine") has been added. This allows the mesh to remain refined in specific regions even though the error is initially small.
>
> Additionally, the movingAdaptiveFvMesh class is based on adaptiveFvMesh, and has all of the same features, but includes the ability to use mesh motion. It is recommended to use the velocityLaplacian motion solver.
>
> > **NOTE:** Whilst AMR may be used with meshes created using snappyHexMesh, regions can only be cut at level 0 when using either 2-D or axisymmetric refinement. This is due to the fact that snappyHexMesh uses a 3-D refinement, regardless of the number of solution directions. If refinement is used, the simulation will crash when the mesh is refined in these areas.
>
> > **NOTE:** Meshes that have been "snapped" with snappyHexMesh may work, however crashes may occur. Use at your own risk.
>
> | Entry | Description |
> |---|---|
> | balance | Is dynamic load balancing used (default is yes) |
> | protectedPatches | List of patch names that will not be refined or unrefined (default is none) |
> | nRefinementBufferLayers | Number of layers added to refinement (default is 0) |
> | nUnrefinementBufferLayers | number oy layers added to unrefinement (default is 0) |
> | refine | Use refinement (default is yes) |
> | unrefine | Use unrefinement (default is yes) |
> | refineInterval | Number of time steps between refinement (default is 1) |
> | unrefineInterval | Number of time steps between unrefinement (default is 1) |
> | balanceInterval | Number of time steps between balancing (default is 1) |
> | beginRefine | Time when refinement can begin (default is 0 s) |
> | endRefine | Time when refinement stops (default is great s) |
> | beginUnrefine | Time when unrefinement can begin (default is 0 s) |
> | endUnrefine | Time when unrefinement stops (default is great s) |
> | beginBalance | Time when balancing can begin (default is 0 s) |
> | endBalance | Time when balancing stops (default is great s) |
> | dumpLevel | Write the cell and point level as viewable fields (false by default) |
>
> ## 11.1 Error estimators
>
> In order to determine the cells that can be refined or unrefined, error estimators have been added. Generally, this is achieved by looking for a derivative or difference of a specified fields across all the faces a cell and it neighbours. The maximum value of all face errors of a given cell is taken as the cell center-based value, and is used to define the cells that should be refined. Probe locations are automatically refined up to the maximum level of refinement to remove discontinuities in probe sampling.
>
> | Entry | Description |
> |---|---|
> | lowerRefineLevel | Error that mesh is refined at |
> | unrefineLevel | Error that mesh is unrefined |
> | upperRefineLevel | Error that refinement is stopped (default is great) |
> | upperUnrefineLevel | Error that unrefinement begins to occur again (default is great) |
> | maxRefinement | Maximum number of refinement levels |
> | minDx | Minimum cell size |
> | refineProbes | Are probes refined (yes by default) |

</details>

**已记录备注**：

人工参考：第28份；F：梯度方向正确，关键时间参数错误，且由静态配置保证特定演化。；知道梯度识别细化区域，遗漏总密度及教程明确配置。；误把beginUnrefine解释为细化起始时间步，应为粗化准入物理时刻。；泛泛说先加密后粗化，未解释误差判据与粗化时间准入分工。
DeepSeek：回答将beginUnrefine错误解释为控制细化起始时间；关键参数语义错误且未结合自由场教程配置。；仅泛泛提到通过梯度信息识别细化区域，未说明使用总密度，也未说明自由场教程显式设置errorEstimator densityGradient。；将beginUnrefine误作细化的起始时间步，且未给出自由场教程值1e-5或手册定义的粗化可开始时刻。；包含误差估计器用于识别细化区域及后续粗化的部分正确概念，但beginUnrefine作用判断错误，且未说明静态配置不能保证特定演化结果。

## 第19份 · P06-03：一般结论碰巧正确，实际问答场景已被替换

**问题**：我在DDT算例里改了燃速参数，初始场文件里怎么还是原来的值？这两个设置会自动同步吗？

**原回答**：

在OpenFOAM中，初始场文件（如`0/U`、`0/p`等）中的值不会自动与`fvSchemes`文件中的设置同步。`fvSchemes`文件定义了求解器使用的数值方法，如时间离散化（`ddtSchemes`）、梯度计算（`gradSchemes`）、通量计算（`fluxScheme`）等，但这些设置不会影响初始场文件中的物理参数值，如燃速参数。因此，如果你在`fvSchemes`中修改了时间离散化方法（如从`Euler`改为`RK1SSP`或`RK2`），这不会改变初始场文件中的值。你需要手动在初始场文件中更新燃速参数的值。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|P06-03.K1=0、P06-03.K2=0.5|0.2500|0.5|0.25|33.33|
|GPT|P06-03.K1=0.25、P06-03.K2=0.5|0.3750|0.5|0.5|45.83|
|DeepSeek|P06-03.K1=0.25、P06-03.K2=0.5|0.3750|0.5|0.75|54.17|

**当前Gold必要点**：

- `P06-03.K1`：物性Su和初始场Su是两个输入位置，分别在combustionProperties和0/Su，应分别核对。
- `P06-03.K2`：只改燃速参数不能假定初始场文件自动同步；边界也应核对，不从静态文件关系保证运行初始化顺序或全程燃速。

**分歧观察与解释**：

问题询问DDT燃速物性与初始场，回答改谈fvSchemes与时间离散，只保留“不会自动同步”的一般结论。人工A=0.25，GPT=0.5，DeepSeek=0.75。

可用的一般常识与对题设对象的正确解释不是同一件事。这里还存在把数值格式与燃速配置联系起来的事实/因果问题。


**来源依据**：

- [tutorials/blastXiFoam/deflagrationToDetonationTransition/constant/combustionProperties](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastXiFoam/deflagrationToDetonationTransition/constant/combustionProperties:18)，L18—L28；文件SHA256 `40070021b268bd556c1d3f1fe858fef413799134fbdec559a271d5e93ae17cc2`。
- [tutorials/blastXiFoam/deflagrationToDetonationTransition/0/Su](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastXiFoam/deflagrationToDetonationTransition/0/Su:17)，L17—L31；文件SHA256 `869812b3fbb0c6735e5e69ad5181b5f464ee88e296ae9a4ce01cfa5871671cb0`。

<details><summary>已核对原文摘录</summary>

> laminarFlameSpeedCorrelation RaviPetersen;
>
> fuel            HydrogenInAir;
>
> Su              Su [0 1 -1 0 0 0 0] 0.434;
>
> SuModel         unstrained;
>
> equivalenceRatio equivalenceRatio [0 0 0 0 0 0 0] 1;
>
> sigmaExt        sigmaExt [0 0 -1 0 0 0 0] 100000;
> dimensions      [0 1 -1 0 0 0 0];
>
> internalField   uniform 0.434;
>
> boundaryField
> {
>     walls
>     {
>         type            zeroGradient;
>     }
>     defaultFaces
>     {
>         type            empty;
>     }
> }

</details>

**已记录备注**：

人工参考：第19份；F/A：把燃速物性问题转为数值格式问题，只有不能自动同步的部分判断有用。；未定位combustionProperties中的Su与0/Su，转而讨论fvSchemes。；不能自动同步、另行修改初始场的方向正确，但未针对实际Su输入且遗漏边界。
DeepSeek：核心条件结论“不会自动同步、需手动更新”方向正确，但回答错误地将燃速参数与 fvSchemes 关联，遗漏 combustionProperties 和 0/Su 两个输入位置及边界核对。；仅提到初始场文件需手动更新，未指出 combustionProperties 与 0/Su 是两个需分别核对的输入位置，且将燃速设置与 fvSchemes 混淆。；正确说明不会自动同步、需手动更新初始场，但未涉及边界核对，也未说明静态文件关系不能保证初始化顺序或全程燃速。

## 第25份 · E42-01：公式出现了，但文字解释否认了归一化

**问题**：densityGradient看的是总密度还是某一相的密度？它怎样衡量哪里变化大，有做归一化吗？

**原回答**：

densityGradient衡量的是总密度的变化。它通过计算相邻单元格之间的密度梯度（即密度的自然对数的梯度）来评估误差，具体公式为：$$\epsilon_{\nabla\rho} = \max\left( \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{own}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{own}|},\ \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{nei}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{nei}|} \right)^{f}$$。该误差估计器并未提及归一化操作，而是直接使用总密度进行计算。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E42-01.K1=1、E42-01.K2=0.5|0.7500|0.5|not_applicable|62.50|
|GPT|E42-01.K1=1、E42-01.K2=0.75|0.8750|0.75|not_applicable|81.25|
|DeepSeek|E42-01.K1=1、E42-01.K2=0.5|0.7500|0.75|not_applicable|75.00|

**当前Gold必要点**：

- `E42-01.K1`：densityGradient使用总密度，不是只取某个炸药相的密度。
- `E42-01.K2`：按式(11.4)比较中心与两侧梯度量偏差，构造含梯度与尺度项的归一化比值，取较大者并带f指数；不强制背全部符号或原文矛盾定义。

**分歧观察与解释**：

回答称使用总密度并列出公式，却又说没有归一化；两AI的F均为0.75，人工为0.5。

公式或关键词可能掩盖后续相反解释；原手册符号解释还有独立未决问题，不能将手册转录一致当作实现已证实。


**来源依据**：

- [manual/markdown/11_amr.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/11_amr.md:109)，L109—L131；文件SHA256 `26ca1848c6ddee2c65bc94c57a4d6745b0ca7d2412312b63791545e864f058df`。

<details><summary>已核对原文摘录</summary>

> ### 11.1.5 Density gradient (densityGradient)
>
> A modified density gradient was defined by Zheng et al. (2008), and uses an error defined by
>
> $$
> \epsilon_{\nabla\rho} = \max\left( \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{own}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{own}|},\ \frac{|(\nabla\ln\rho)_{C} - (\nabla\ln\rho)_{nei}|}{\alpha f \rho_{C}/dl + |(\nabla\ln\rho)_{nei}|} \right)^{f}
> $$
> (11.4)
>
> with
>
> $$
> (\nabla\ln\rho)_{C} = \frac{\rho_{nei} - \rho_{own}}{|r_{nei} - r_{own}|}
> $$
> (11.5)
>
> $$
> (\nabla\ln\rho)_{nei,own} = \frac{(\nabla\rho)_{nei,own}(r_{nei} - r_{own})}{|r_{nei} - r_{own}|}
> $$
> (11.6)
>
> $r_{own,nei}$ is the surface normal vector, and $dl = |r_{nei} - r_{own}|$, is the distance between cell centers. This error estimator uses the total density.

</details>

**已记录备注**：

人工参考：第25份；F：总密度与公式主体正确，解释存在矛盾；不把有疑点的符号解释当作已核验实现。；使用总密度正确。；公式主体有梯度差、分母尺度、最大值及f指数，但文字否认归一化，与比值结构矛盾。
GPT：公式表达了比较两侧梯度偏差的比值、取最大值并带 f 指数；但文字称未做归一化，与公式中的分母归一化相矛盾。
DeepSeek：总密度判断正确，公式大体正确；但否认公式中分母尺度项构成归一化比值，属局部实质性错误。；明确说明使用总密度，不是单相密度。；给出式(11.4)的max、梯度差、分母尺度项和f指数，但又称“并未提及归一化操作”，与公式含归一化比值的实质相矛盾，仅部分满足。

## 第36份 · E33-01：覆盖不足被当成事实错误重复扣分

**问题**：在 blastFoam 的 function objects 配置中，conservedQuantities 功能对象用于做什么？它输出哪些量，以及通过什么字典条目指定要跟踪的场？

**原回答**：

在 blastFoam 的 function objects 配置中，conservedQuantities 功能对象用于跟踪和输出守恒量。它输出的量包括质量、动量和能量等守恒量。要跟踪的场通过字典条目中的 'fields' 指定。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E33-01.K1=0.25、E33-01.K2=1|0.6250|1|not_applicable|81.25|
|GPT|E33-01.K1=0.25、E33-01.K2=1|0.6250|0.75|not_applicable|68.75|
|DeepSeek|E33-01.K1=0、E33-01.K2=1|0.5000|0.75|not_applicable|62.50|

**当前Gold必要点**：

- `E33-01.K1`：conservedQuantities 计算并打印场的体积积分值，输出初始值、当前值、总差值和相对差值。
- `E33-01.K2`：通过 fields 条目指定要跟踪的场。

**分歧观察与解释**：

回答说明跟踪守恒量并使用fields，却没列全体积积分和各类差值输出；人工F=1、两AI均F=0.75。

没有说全与说错应分开；若不能指出具体错误陈述，不宜只因缺少必要点而再降低F。


**来源依据**：

- [manual/markdown/15_function_objects.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/15_function_objects.md:64)，L64—L72；文件SHA256 `f22133da89f48be2d66a63873d227b9fb6be40321075cb6634a5cf2f35168bbe`。

<details><summary>已核对原文摘录</summary>

> ## 15.4 conservedQuantities
>
> The volume integrated value of fields can be computed and printed in the output of the solver. The initial, current, total difference, and relative difference is printed. Any fields can be tracked by specifying the names of the fields in the dictionary.
>
> | Entry | Description |
> |---|---|
> | fields | Fields to track |
>
> > **NOTE:** Currently, the removal and injection of values into a domain is not considered.

</details>

**已记录备注**：

人工参考：第36份；F：已有陈述没有明确实质性错误，覆盖不足由K反映。；仅笼统跟踪守恒量，遗漏体积积分、初始/当前值、总差值与相对差值。；fields配置正确。
GPT：仅概括说明跟踪并输出守恒量，未说明体积积分以及初始值、当前值、总差值和相对差值。
DeepSeek：核心配置入口正确；对输出内容的表述不完整，未涵盖体积积分值和差值输出等关键事实。；未说明计算/打印场的体积积分值，也未提及初始值、当前值、总差值和相对差值。；明确指出通过 fields 字典条目指定要跟踪的场。

## 第37份 · E28-01：用途大致正确，但名称和字典层级都错误

**问题**：在 blastFoam 的 burst 补丁体系中，手册说明所有字段都需要在其字典中额外增加一个条目来指定“破裂前”的边界条件。这个条目的名称是什么，它被用来做什么？同时，手册指出该条目应放在哪个字典层级？

**原回答**：

在 blastFoam 的 burst 补丁体系中，手册说明所有字段都需要在其字典中额外增加一个条目来指定“破裂前”的边界条件，这个条目的名称是 "preBurst"，它被用来指定破裂前边界条件。该条目应放在 "boundaryConditions" 字典层级。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E28-01.K1=0.25、E28-01.K2=0.25|0.2500|0.25|not_applicable|25.00|
|GPT|E28-01.K1=0.5、E28-01.K2=0.75|0.6250|0.5|not_applicable|56.25|
|DeepSeek|E28-01.K1=0.5、E28-01.K2=0|0.2500|0.25|not_applicable|25.00|

**当前Gold必要点**：

- `E28-01.K1`：该额外条目的名称是 intactField，用于指定字段在破裂之前的边界条件。
- `E28-01.K2`：该条目属于字段字典中的额外条目，而非补丁类型本身的定义。

**分歧观察与解释**：

将intactField写成preBurst，层级说成boundaryConditions。GPT比人工高31.25分，DeepSeek与人工一致，是GPT自身误差最大的案例。

这是同一题E28-01的另一份回答，不能与第13份合并成一次独立观察，也不能由用途相似推定条目名称正确。


**来源依据**：

- [manual/markdown/07_burst_patches.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/07_burst_patches.md:1)，L1—L12；文件SHA256 `1c4fd9c6a681b0f0ad846967ff49ddc2737e234aa01e39536f41f493418c8097`。

<details><summary>已核对原文摘录</summary>

> # Burst patches
>
> The ability to have a "bursting" patch can be used with the burst (external patch), burstCyclic (internal with no AMR), or burstCyclicAMI (general internal). All fields require an additional entry in their dictionaries name "intactField" which is used to specify the boundary condition of the field before bursting. The basic burst patch can be created using any mesh generation technique, however the cyclic variations require using the createBaffles utility, standard to OpenFOAM. See Sec. 20.5 for an example of how to create and use the patches.
>
> ## 7.1 Burst models
>
> The method to calculate where burst occurs is runtime-selectable and the inputs are placed in the constant/polyMesh/boundary file under the corresponding boundary. This can also be added in either the patch entry within blockMeshDict of snappyHexMeshDict.
>
> | Variable | Description |
> |---|---|
> | partialBurst | Can individual face burst (no by default) |
> | useDelta | Us the difference across coupled patches rather than the maximum value (yes by default) |

</details>

**已记录备注**：

人工参考：第37份；F：关键名称和配置层级失实，仅用途部分正确。；用途正确，但名称应intactField而非preBurst。；只有边界配置方向的少量正确内容，boundaryConditions层级无原文支持。
GPT：用途正确，但条目名称错误。；指出这是字段字典中的额外条目；所称 boundaryConditions 层级与资料不符。

## 第31份 · P09-01：比较说到了一部分，但否认来源差异

**问题**：delayedDetonation说明说用了linear，但当前phaseProperties选了什么？两处对六个点和延迟数量的说法怎样核对，哪些结论需要保留差异？

**原回答**：

在delayedDetonation案例中，phaseProperties中选用了activationModel programmedIgnition，而非linear。关于六个点和延迟数量的说法，案例中明确列出了六个点，且每个点对应一个延迟值，因此两者一致。由于资料中未提及需要保留差异的情况，因此无需保留差异。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|P09-01.K1=0.5、P09-01.K2=0.5、P09-01.K3=0.25|0.4167|0.5|0.5|47.22|
|GPT|P09-01.K1=0.75、P09-01.K2=0.5、P09-01.K3=0.5|0.5833|0.5|0|36.11|
|DeepSeek|P09-01.K1=0.25、P09-01.K2=0.5、P09-01.K3=0.25|0.3333|0.5|0|27.78|

**当前Gold必要点**：

- `P09-01.K1`：说明称linear、六点且四点延迟。
- `P09-01.K2`：当前选择programmedIgnition，六点延迟序列0、5e-6、10e-6、5e-6、10e-6、0，四点非零。
- `P09-01.K3`：六点/四延迟可相符，模型名称有差异；描述当前字典用显式选择，不假造二者一致或已验证实际运行。

**分歧观察与解释**：

回答识别programmedIgnition，却称无需保留差异，且没有说明六点中四点为非零延迟；两AI将A判0，人工A=0.5。

既有“核心反向=0”在混合正确证据与相反结论时如何使用，与第3份构成同一尺度争议。


**来源依据**：

- [tutorials/blastFoam/delayedDetonation/README.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/delayedDetonation/README.md:1)，L1—L7；文件SHA256 `e72458fa768a62c0f2a43b295824ff987b7de0dad05cbd73ac87b5bf83b4d56b`。
- [tutorials/blastFoam/delayedDetonation/constant/phaseProperties](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/delayedDetonation/constant/phaseProperties:88)，L88—L138；文件SHA256 `f0952d89be85b5c9ebe7e04ffe27508bd3a58799a9ffa5abaf8cf83d061bf8df`。

<details><summary>已核对原文摘录</summary>

> # Delayed detonation tutorial
>
> ## Notes
>
> This is a simple case to show how to setup a case using delayed activation of points. A RDX charge is used with six activation point, with four of the six using a delayed start. A linear activation model is used, but the same setup of the detonation points can be applied to any of the other available models.
>
> This case takes approximately 2.5 min to run on a single core desktop.
>     activationModel programmedIgnition;
>     initiation
>     {
>         // Detonation energy
>         E0              4.0e9;
>
>         // Detonation points
>         points
>         (
>             (0 0.02 0)
>             (0 0.1 0)
>             (0 0.2 0)
>             (0 0.3 0)
>             (0 0.4 0)
>             (0 0.5 0)
>         );
>
>         // Delays
>         delays
>         (
>             0.0
>             5e-6
>             10e-6
>             5e-6
>             10e-6
>             0.0
>         );
>
>         // Radii to set (for each point)
>         radius 0.01; // Radius of activation (overridden by radii entry)
>         radii
>         (
>             0   // use the closest cell
>             0.02
>             0.03
>             0.015
>             0.025
>             0.01
>         );
>
>         // Detonation velocity
>         vDet    7850;
>
>         // Chapman-Jouguet pressure
>         Pcj     0.1017e11;
>
>         // Linear and compression activation
>         burnModel programmedBeta;
>
>         pMin 1.1e5;
>     }

</details>

**已记录备注**：

人工参考：第31份；F/A：模型名称有差异应保留，六点与四点非零延迟可相符；比较部分正确但结论矛盾。；涉及linear差异和六点，未说明README所称四点延迟。；当前programmedIgnition及六点正确，未核对四个非零、两个零及延迟序列。；开头承认名称差异，最后又称无需保留差异，矛盾。
DeepSeek：核心配置选择正确，但“无需保留差异”与应保留模型名称差异的核心条件结论相反。；仅提到说明中的linear与当前选择不同，未说明六点及四点延迟。；正确指出programmedIgnition和六个点，但未列出延迟序列，也未点明四个非零延迟。；指出模型名称不同，但错误地认为无需保留差异，且未说明六点与四延迟可相符。

## 第59份 · N60-03：缩放方向与方程项混淆

**问题**：reacting粒径模型选用pressureBased反应率，关系中的压力按MPa表示。若误把pScale设为1而不是1e-6，粒径输运方程的哪一项受到影响？请说明正确缩放和k的压力幂形式。

**原回答**：

粒径输运方程中的压力项（通常为扩散项或源项）受到影响。正确缩放应为pScale=1e-6 MPa，k的压力幂形式为k*(p/pScale)^n，其中n为幂指数。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|N60-03.K1=0.25、N60-03.K2=0.25、N60-03.K3=0.5|0.3333|0.25|0.25|27.78|
|GPT|N60-03.K1=0.25、N60-03.K2=0.5、N60-03.K3=0.5|0.4167|0.5|0.5|47.22|
|DeepSeek|N60-03.K1=0.25、N60-03.K2=0.25、N60-03.K3=0.5|0.3333|0.25|0.5|36.11|

**当前Gold必要点**：

- `N60-03.K1`：reacting方程为partial_t d_i+u_i·grad d_i=k，k是源项。
- `N60-03.K2`：该速率为k=beta*(p*pScale)^alpha；手册给MPa示例pScale=1e-6。
- `N60-03.K3`：误设缩放改变方程右端k中的压力幂项，不能仅说改变输出单位而不影响速率。

**分歧观察与解释**：

Gold为k=beta*(p*pScale)^alpha，回答写成除以pScale，还将右端速率含混称为扩散项或源项；GPT的F/A均比人工高0.25。

数值方向、乘除与项的职责影响结论，不能只因出现1e-6和“压力项”就判主要正确。


**来源依据**：

- [manual/markdown/09_diameter_models.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/09_diameter_models.md:38)，L38—L53；文件SHA256 `a62ec6a288149422b050fa333dc00d356e2d126d7b959bf3403499819be3c8a1`。
- [manual/markdown/09_diameter_models.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/09_diameter_models.md:59)，L59—L76；文件SHA256 `a62ec6a288149422b050fa333dc00d356e2d126d7b959bf3403499819be3c8a1`。

<details><summary>已核对原文摘录</summary>

> ## reacting
>
> The reacting diameter model adds an additional source term in the transport equation for the diameter to increase/decrease the local diameter based on the given reaction rate
>
> $$
> \frac{\partial d_i}{\partial t} + u_i \cdot \nabla d_i = k
> $$
>
> (9.3)
>
> where k is the specified reaction rate (see Sec. 9.4)
>
> | Entry | Description |
> |---|---|
> | d | Initial diameter [m] |
> | reactionRate | Reaction rate model |
> ### pressureBased
>
> The pressureBased reaction rate uses a coefficient, pressure scale, pressure offset (in scaled units) and pressure exponent to compute the rate
>
> $$
> k = \beta (\bar{p})^\alpha
> $$
>
> (9.4)
>
> and $\bar{p} = p \times p_{scale}$. For example, if the pressure relation is in MPa, $p_{scale} = 1e^{-6}$.
>
> | Entry | Description |
> |---|---|
> | alpha | Pressure exponent [ ] |
> | beta | Coefficient [Pa−α] |
> | pScale | Pressure scale [ ] |
> | offset | Pressure offset [Pa/pScale] |

</details>

**已记录备注**：

人工参考：第59份；F/A：正确式为partial_t d+u.grad d=k，k=beta*(p*pScale)^alpha；关键公式及缩放方向错误。；未准确定位右端反应率k源项，混称扩散或源项。；知道1e-6，但乘法缩放误写除法且给pScale加MPa单位。；知道压力相关项受影响，未清楚落实右端k。
GPT：核心影响方向和pScale数值部分正确，但压力幂的代数形式反向，且受影响项表述不准确。；未明确给出粒径输运方程及k为右端源项，且将影响项说成可能是扩散项或源项。；正确给出pScale=1e-6并提及压力幂，但压力形式写成了(p/pScale)^n，原文应为k=beta*(p*pScale)^alpha。；认识到缩放错误会影响压力相关速率，但未明确指出是方程右端k中的压力幂项，并混入扩散项表述。
DeepSeek：缩放数值正确，但压力幂形式反向且影响项表述不准确，整体事实混杂。；仅暗示输运方程和源项，未给出reacting方程形式，也未明确k为源项。；给出pScale=1e-6，但速率公式写成k*(p/pScale)^n，与原文k=beta*(p*pScale)^alpha相反。；指出缩放会影响源项/压力项，但未准确定位到右端k中的压力幂项，且误称可能为扩散项。

## 第48份 · P08-01：显式启用判断正确，但移动机制解释错误

**问题**：轴对称装药教程的pressureProbes是否允许把网格外探针移到网格内？结合手册解释显式选择、默认值和移动目标。

**原回答**：

根据控制字典文件中的设置，pressureProbes允许把网格外探针移到网格内。具体来说，adjustLocations选项被设置为yes，这意味着探针位置可以被调整。probeLocations选项中列出的探针位置包括(1 0 0)、(2 0 0)、(5 0 0)、(10 0 0)、(15 0 0)和(20 0 0)，这些位置可能位于网格外部。因此，可以通过设置适当的probeLocations选项来将网格外探针移到网格内。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|P08-01.K1=0.75、P08-01.K2=0、P08-01.K3=0|0.2500|0.75|0.5|50.00|
|GPT|P08-01.K1=0.5、P08-01.K2=0、P08-01.K3=0|0.1667|0.5|0.5|38.89|
|DeepSeek|P08-01.K1=0.5、P08-01.K2=0、P08-01.K3=0|0.1667|0.5|0.5|38.89|

**当前Gold必要点**：

- `P08-01.K1`：实例type blastProbes并adjustLocations yes。
- `P08-01.K2`：手册默认adjustLocations no；可把网格中找不到的探针移到最近面。
- `P08-01.K3`：实例显式启用不能当作所有blastProbes的默认。

**分歧观察与解释**：

识别adjustLocations=yes，却把probeLocations的给定坐标等同于自动将网格外探针移入网格；两AI比人工低11.11分。

这里既有遗漏默认值/最近面的K问题，也有对机制的断言，需要区分遗漏与已明确说错。


**来源依据**：

- [tutorials/blastFoam/axisymmetricCharge/system/controlDict](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/axisymmetricCharge/system/controlDict:94)，L94—L116；文件SHA256 `f61a38eeaf9eae3273ca7b0ebcd7bab4132447a890a892f7983d6c9e82872359`。
- [manual/markdown/15_function_objects.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/15_function_objects.md:29)，L29—L43；文件SHA256 `f22133da89f48be2d66a63873d227b9fb6be40321075cb6634a5cf2f35168bbe`。

<details><summary>已核对原文摘录</summary>

>     pressureProbes
>     {
>         type           blastProbes;
>         writeControl   timeStep;
>         writeInterval  1;
>         adjustLocations yes;
>
>         probeLocations
>         (
>             (1 0 0)
>             (2 0 0)
>             (5 0 0)
>             (10 0 0)
>             (15 0 0)
>             (20 0 0)
>         );
>         fields
>         (
>             p
>             impulse
>             dynamicP
>         );
>     }
> ## 15.1 blastProbes
>
> A modified version of the standard OpenFOAM probe utility is also available, where the basic functionality remains the same, with several key additions. First, the ability to append to exiting probe files is now possible, allowing for a single probe file to be used even if a simulation is restarted from a later time. Second, probes that are not found within the mesh can be moved to the nearest face so they can produce valid results. This can be very useful if a probe is needed on a curved face. Lastly, the warning of probes existing on multiple processors has been removed by selecting a single processor on which to probe.
>
> > **NOTE:** When refinement and unrefinement occurs, the probe locations will "jump" to the nearest cell resulting in fluctuations when plotted. This can be eliminated by allowing refinement of probes in dynamicMeshDict ("refineProbes") (this is the default option).
>
> | Entry | Description |
> |---|---|
> | probeLocations | List of locations to probe |
> | fields | Fields to probe at the given points |
> | append | Are probes appended to and existing file (default no) |
> | fixLocation | Probes follow cell motion (not stationary) |
> | adjustLocations | Can probes be moved into the mesh (default no) |
> | writeVTK | Probed points are written to a VTK file (default no) |
> | interpolationScheme | Method to interpolate probe. Options are cell, cellPoint, cellPointFace, cellPatchConstrained, cellPointWallModified, and pointMVC (default is cell) |

</details>

**已记录备注**：

人工参考：第48份；F/A：启用判断正确，最后混淆probeLocations给定位置与自动调整到最近面的机制。；正确读取实例adjustLocations=yes，遗漏blastProbes类型。；未说明默认no及最近面。；未区分实例显式启用与通用默认。
GPT：实例中adjustLocations为yes这一核心事实正确，但遗漏默认值和最近面目标，并将移动效果归因于probeLocations设置，条件解释不完整。；写明了实例中adjustLocations为yes，但未说明type为blastProbes。；未说明手册默认值为no，也未说明探针会移到最近面。；未区分该实例的显式启用与blastProbes的通用默认设置。
DeepSeek：核心允许移动的结论及实例显式yes正确，但移动机制/目标表述错误，且遗漏默认no和最近面，实例与默认的区分未表达。；仅表达adjustLocations yes，未明确说明实例type为blastProbes。；未说明默认adjustLocations为no，也未说明移动目标是最近面。；未区分实例显式启用与blastProbes默认值，未表达不能当作所有默认。

## 第29份 · E48-03：读脚本的缺失与错误工具名

**问题**：对比 blastFoam building3D 与 blastFSIFoam building3D 两个 Allrun 脚本：在网格准备阶段，前者是否拆分区域？后者是否拆分区域？两者在运行求解器前对内部 patch 的处理分别是什么？

**原回答**：

blastFoam building3D 在网格准备阶段是否拆分区域未明确提及，而 blastFSIFoam building3D 在网格准备阶段使用 splitMeshRegions 工具拆分区域。两者在运行求解器前对内部 patch 的处理分别为：blastFoam 未提及具体处理，而 blastFSIFoam 使用 coupledGlobalPolyPatch 进行处理，且需修改 patch 名称和类型。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|E48-03.K1=0、E48-03.K2=0.75、E48-03.K3=0|0.2500|0.25|not_applicable|25.00|
|GPT|E48-03.K1=0.25、E48-03.K2=0.75、E48-03.K3=0.25|0.4167|0.5|not_applicable|45.83|
|DeepSeek|E48-03.K1=0、E48-03.K2=0.75、E48-03.K3=0|0.2500|0.25|not_applicable|25.00|

**当前Gold必要点**：

- `E48-03.K1`：blastFoam building3D 脚本没有 splitMeshRegions 调用，而是直接 blockMesh 后 decomposePar -copyZero。
- `E48-03.K2`：blastFSIFoam building3D 脚本在 blockMesh 后调用 splitMeshRegions -cellZones -overwrite 拆分区域。
- `E48-03.K3`：blastFoam building3D 脚本用 addEmptyPatch internalPatch internal -overwrite 添加内部 patch；blastFSIFoam building3D 脚本用 addEmptyPatch internalPatch internal -region air -overwrite 仅在 air 区域添加。

**分歧观察与解释**：

识别FSI脚本拆分区域，却没有明确普通building3D不调用splitMeshRegions，并将addEmptyPatch处理误写成coupledGlobalPolyPatch。

GPT给予较多部分分；DeepSeek与人工一致。脚本中未调用和“原文没有提及”含义不同。


**来源依据**：

- [tutorials/blastFoam/building3D/Allrun](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/building3D/Allrun:10)，L10—L29；文件SHA256 `4adcdd258aa089741dcd2cf47a1cd8974b1a679734b9df8b4e18f5a2eb92ad0e`。
- [tutorials/blastFSIFoam/building3D/Allrun](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFSIFoam/building3D/Allrun:10)，L10—L37；文件SHA256 `04da519c126178e7eb5622631f4c82453290c7f75d404e003c5ed8d58b14f323`。

<details><summary>已核对原文摘录</summary>

> # -- Pre-process the stl
> runApplication surfaceFeatures
>
> # -- Create the mesh for the fluid
> runApplication blockMesh
>
> # -- Decompose the mesh
> runApplication decomposePar -copyZero
>
> # -- Cut out the stl
> runParallel snappyHexMesh -overwrite
>
> # -- Add internal patch
> runParallel addEmptyPatch internalPatch internal -overwrite
>
> # -- Set the initial conditions for the fluid
> runParallel setRefinedFields
>
> #- Run the calc
> runParallel $(getApplication)
> # -- Create the mesh
> runApplication blockMesh
>
> # -- Split the mesh into regions
> runApplication splitMeshRegions -cellZones -overwrite
>
> # -- Remove the original mesh
> rm -rf constant/polyMesh
>
> # -- Change patch types
> foamDictionary constant/air/polyMesh/boundary -entry entry0/air_to_building/type -set 'mappedMovingWall'
> foamDictionary constant/building/polyMesh/boundary -entry entry0/building_to_air/type -set 'mappedMovingWall'
>
> # -- Decompose the mesh
> runApplication decomposePar -allRegions
>
> # -- Add internal patch
> runParallel addEmptyPatch internalPatch internal -region air -overwrite
>
> # -- Set initial conditions in the air region
> runParallel setRefinedFields -region air
>
> # -- Refine the building region
> runParallel -s 1 refineMesh -region building -overwrite
> runParallel -s 2 refineMesh -region building -overwrite
>
> # -- Run the calc
> runParallel $(getApplication)

</details>

**已记录备注**：

人工参考：第29份；F：少量FSI区域拆分内容正确，关键内部patch说明失实。；未识别blastFoam脚本没有区域拆分调用的实际流程。；正确识别FSI调用splitMeshRegions，遗漏顺序及参数。；未答两者addEmptyPatch，额外引入无依据的coupledGlobalPolyPatch。
DeepSeek：仅 blastFSIFoam 拆分区域这一核心事实正确；内部 patch 处理的关键事实缺失且有关键误述。；未说明 blastFoam building3D 不拆分区域，也未提及直接 blockMesh 后 decomposePar -copyZero。；正确指出 blastFSIFoam 使用 splitMeshRegions 拆分，但未说明其在 blockMesh 后及 -cellZones -overwrite 参数。；未提及 addEmptyPatch internalPatch 及 -region air；反而误述为 coupledGlobalPolyPatch 和 patch 名称/类型修改。

## 第46份 · N67-02：专业常见公式替换了本版本模型定义

**问题**：固体exponential与polynomial模型怎样分别描述温度相关导热？请比较参考温度的使用和参数组织，不要把流体黏度系数加入固体模型。

**原回答**：

固体的exponential模型通常描述为:δ = δ₀ · exp(-E₀ / (R · T))，其中δ是导热系数，δ₀是参考导热系数，E₀是参考能量，R是气体常数，T是温度。

而polynomial模型则描述为:δ = a + b · T + c · T² + d · T³，
其中a、b、c和d是参数。

两种模型的主要区别在于exponential模型使用了参考温度和能量，而polynomial模型使用了多项式函数来描述温度的变化。

在参考温度的使用上，exponential模型使用了一个固定的参考温度（通常是某个特定温度的导热系数），而polynomial模型没有使用参考温度。

在参数组织上，exponential模型使用了三个参数（δ₀、E₀和R），而polynomial模型使用了四个参数（a、b、c和d）。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|N67-02.K1=0.25、N67-02.K2=0.25、N67-02.K3=1|0.5000|0.25|not_applicable|37.50|
|GPT|N67-02.K1=0.25、N67-02.K2=0.5、N67-02.K3=1|0.5833|0.5|not_applicable|54.17|
|DeepSeek|N67-02.K1=0.25、N67-02.K2=0.5、N67-02.K3=1|0.5833|0.25|not_applicable|41.67|

**当前Gold必要点**：

- `N67-02.K1`：exponential用kappa0、Tref、n0给出kappa0*(T/Tref)^n0。
- `N67-02.K2`：polynomial用kappaCoeffs<8>给出sum(i=0..7) kappa_i*T^i，没有该段定义的参考温度归一化。
- `N67-02.K3`：两者此处只描述固体导热系数，原片段没有要求muCoeffs。

**分歧观察与解释**：

exponential被改写成Arrhenius式，polynomial被缩为三次四系数；Gold要求kappa0*(T/Tref)^n0与8个系数。

同名模型的一般专业知识不能覆盖所给手册的具体实现定义；两AI均给予一定正确方向分，但GPT的F更高。


**来源依据**：

- [manual/markdown/05_fluid_solid_thermo.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/05_fluid_solid_thermo.md:1029)，L1029—L1042；文件SHA256 `e8369aa14525d4c3adb639ae6e134af41d6d97d84484f114ef221e63c141f8dc`。
- [manual/markdown/05_fluid_solid_thermo.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/05_fluid_solid_thermo.md:1044)，L1044—L1055；文件SHA256 `e8369aa14525d4c3adb639ae6e134af41d6d97d84484f114ef221e63c141f8dc`。

<details><summary>已核对原文摘录</summary>

> ### 5.4.3 exponential
>
> Thermal conductivity is calculated using an exponential function
>
> $$
> \kappa(T) = \kappa_0\left( \frac{T}{T_{ref}} \right)^{n_0}
> $$
> (5.84)
>
> | Variable | Description |
> |---|---|
> | `kappa0` | Reference thermal conductivity [W/m/K] |
> | $n_0$ | Exponential coefficient [ ] |
> | $T_{ref}$ | Reference temperature [K] |
> ### 5.4.4 polynomial
>
> Thermal conductivity is calculated using polynomial functions of temperature.
>
> $$
> \kappa(T) = \sum_{i=0}^{7} \kappa_iT^i
> $$
> (5.85)
>
> | Variable | Description |
> |---|---|
> | `kappaCoeffs<8>` | Conductivity coefficients |

</details>

**已记录备注**：

人工参考：第46份；F：两个模型主要公式与参数组织错误。；仅参考导热量等少量概念正确，误用Arrhenius式及参数。；仅温度多项式概念正确，应0到7次、8系数而非固定三次四参数。；始终讨论固体导热，没有加入muCoeffs。
DeepSeek：exponential模型公式与参数严重错误；polynomial部分正确但阶数和参数组织错误；未加入黏度系数。；回答误用Arrhenius型指数式且参数不符，仅提及exponential与参考温度，核心公式未正确表达。；正确指出polynomial无参考温度归一化，但系数个数与阶数不完整，仅列到三次且未用8个系数。；回答只在固体导热系数语境下讨论，未混入muCoeffs或流体黏度系数。

## 第34份 · N60-02：均值掩盖单裁判对完整正确回答的扣分

**问题**：constant和constantMass两种粒径模型中，“constant”分别约束什么？对照它们的输入条目和直径场写出说明，不能把恒质量直接解释为恒直径。

**原回答**：

在BlastFoam中，`constant`和`constantMass`是两种不同的粒径模型，它们分别约束以下内容：

1. `constant`模型：
   - 该模型使用一个常数直径。直径场不会被写入，因此直径在整个模拟过程中保持不变。输入条目为`d`，表示相的初始直径（单位：米）。

2. `constantMass`模型：
   - 该模型通过参考直径和参考密度计算质量，然后根据当前密度计算真实的直径。输入条目为`rho0`（参考密度，单位：kg/m³）和`d0`（参考直径，单位：米）。直径场根据公式 $d = \left( \frac{6M}{\rho\pi} \right)^{1/3}$ 动态计算，其中 $M$ 是质量，$\rho$ 是当前密度。

因此，`constant`模型约束的是直径的固定值，而`constantMass`模型约束的是质量的恒定，直径则根据密度变化动态调整。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|N60-02.K1=1、N60-02.K2=1、N60-02.K3=1|1.0000|1|not_applicable|100.00|
|GPT|N60-02.K1=0.75、N60-02.K2=1、N60-02.K3=1|0.9167|0.75|not_applicable|83.33|
|DeepSeek|N60-02.K1=1、N60-02.K2=1、N60-02.K3=1|1.0000|1|not_applicable|100.00|

**当前Gold必要点**：

- `N60-02.K1`：constant直接指定固定直径d，手册明确该直径场不写出。
- `N60-02.K2`：constantMass由rho0、d0定义固定M，再按当前rho计算d。
- `N60-02.K3`：恒质量模型的d具有rho依赖，不等于固定直径；不能把constant的明确不写场说明推广给另一模型。

**分歧观察与解释**：

人工与DeepSeek均为100；GPT为83.33。回答明确区分固定直径与固定质量，并给出密度依赖关系。

需查看GPT原备注是否将未声称的跨模型推广强加给回答；不能因为评分差异就认定专业事实存在争议。


**来源依据**：

- [manual/markdown/09_diameter_models.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/09_diameter_models.md:5)，L5—L13；文件SHA256 `a62ec6a288149422b050fa333dc00d356e2d126d7b959bf3403499819be3c8a1`。
- [manual/markdown/09_diameter_models.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/09_diameter_models.md:15)，L15—L36；文件SHA256 `a62ec6a288149422b050fa333dc00d356e2d126d7b959bf3403499819be3c8a1`。

<details><summary>已核对原文摘录</summary>

> ## constant
>
> A constant diameter is used.
>
> > **NOTE:** The diameter field is not written
>
> | Entry | Description |
> |---|---|
> | d | Diameter of the phase [m] |
> ## constantMass
>
> The diameter is determined using a reference diameter at a reference density. The mass is defined as
>
> $$
> M = \frac{\pi d_0^3 \rho_0}{6}
> $$
>
> (9.1)
>
> and the true diameter is calculated using
>
> $$
> d = \left( \frac{6M}{\rho\pi} \right)^{1/3}
> $$
>
> (9.2)
>
> | Entry | Description |
> |---|---|
> | rho0 | Reference density [kg/m3] |
> | d0 | Reference diameter [m] |

</details>

**已记录备注**：

人工参考：第34份；F：模型职责、参数与公式完整正确。；constant固定直径及不写场说明正确。；constantMass由rho0、d0定义M并按当前rho计算d正确。；正确区分恒质量与恒直径，未推广不写场说明。
GPT：核心说明正确；将 d 额外称为“初始直径”超出所给手册表述。
DeepSeek：非条件题，A不适用；回答与手册实质事实一致。；正确说明constant使用固定直径d且直径场不写出。；正确说明constantMass由rho0、d0定义固定质量M，并按当前rho计算d，输入条目和公式均正确。；明确区分恒直径与恒质量，指出constantMass的直径随密度变化动态调整，未将constant的不写场说明错误推广。

## 第47份 · P08-01：均值接近人工，但两个AI差16.67分

**问题**：轴对称装药教程的pressureProbes是否允许把网格外探针移到网格内？结合手册解释显式选择、默认值和移动目标。

**原回答**：

根据手册，pressureProbes的adjustLocations参数设置为yes时，允许将网格外探针移到网格内。默认情况下，该参数可能未启用，需显式设置。移动目标是确保探针位于计算域内以获取有效数据。

|评分者|逐必要点分值|K|F|A|EAS_arith|
|---|---|---:|---|---|---:|
|人工参考|P08-01.K1=0.5、P08-01.K2=0.25、P08-01.K3=0.75|0.5000|1|0.75|75.00|
|GPT|P08-01.K1=0.5、P08-01.K2=0.5、P08-01.K3=0.75|0.5833|1|1|86.11|
|DeepSeek|P08-01.K1=0.5、P08-01.K2=0.5、P08-01.K3=0.75|0.5833|0.75|0.75|69.44|

**当前Gold必要点**：

- `P08-01.K1`：实例type blastProbes并adjustLocations yes。
- `P08-01.K2`：手册默认adjustLocations no；可把网格中找不到的探针移到最近面。
- `P08-01.K3`：实例显式启用不能当作所有blastProbes的默认。

**分歧观察与解释**：

人工75、GPT86.11、DeepSeek69.44，均值77.78。对“可能未启用”的不完整表述，K、F、A采用了不同扣分方式。

均值抵消不能说明维度尺度已统一；省略默认值与明确说反默认值应分开。


**来源依据**：

- [tutorials/blastFoam/axisymmetricCharge/system/controlDict](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/tutorials/blastFoam/axisymmetricCharge/system/controlDict:94)，L94—L116；文件SHA256 `f61a38eeaf9eae3273ca7b0ebcd7bab4132447a890a892f7983d6c9e82872359`。
- [manual/markdown/15_function_objects.md](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/data/resources/corpus/manual/markdown/15_function_objects.md:29)，L29—L43；文件SHA256 `f22133da89f48be2d66a63873d227b9fb6be40321075cb6634a5cf2f35168bbe`。

<details><summary>已核对原文摘录</summary>

>     pressureProbes
>     {
>         type           blastProbes;
>         writeControl   timeStep;
>         writeInterval  1;
>         adjustLocations yes;
>
>         probeLocations
>         (
>             (1 0 0)
>             (2 0 0)
>             (5 0 0)
>             (10 0 0)
>             (15 0 0)
>             (20 0 0)
>         );
>         fields
>         (
>             p
>             impulse
>             dynamicP
>         );
>     }
> ## 15.1 blastProbes
>
> A modified version of the standard OpenFOAM probe utility is also available, where the basic functionality remains the same, with several key additions. First, the ability to append to exiting probe files is now possible, allowing for a single probe file to be used even if a simulation is restarted from a later time. Second, probes that are not found within the mesh can be moved to the nearest face so they can produce valid results. This can be very useful if a probe is needed on a curved face. Lastly, the warning of probes existing on multiple processors has been removed by selecting a single processor on which to probe.
>
> > **NOTE:** When refinement and unrefinement occurs, the probe locations will "jump" to the nearest cell resulting in fluctuations when plotted. This can be eliminated by allowing refinement of probes in dynamicMeshDict ("refineProbes") (this is the default option).
>
> | Entry | Description |
> |---|---|
> | probeLocations | List of locations to probe |
> | fields | Fields to probe at the given points |
> | append | Are probes appended to and existing file (default no) |
> | fixLocation | Probes follow cell motion (not stationary) |
> | adjustLocations | Can probes be moved into the mesh (default no) |
> | writeVTK | Probed points are written to a VTK file (default no) |
> | interpolationScheme | Method to interpolate probe. Options are cell, cellPoint, cellPointFace, cellPatchConstrained, cellPointWallModified, and pointMVC (default is cell) |

</details>

**已记录备注**：

人工参考：第47份；F：无明确反向事实，主要是遗漏与模糊表述。A：条件方向正确，实例判断不够完整。；说明yes时允许调整，未明确实例已启用及blastProbes类型。；默认仅模糊写可能未启用，遗漏最近面。；知道需要显式设置，未把yes当普遍默认，但区分不完整。
DeepSeek：核心结论正确，但缺 blastProbes 类型、默认 no 的明确表述及“最近面”移动目标。；仅表达 adjustLocations yes 可移动探针，未说明实例 type 为 blastProbes。；提到默认可能未启用，但未明确默认 no，也未说明移动到最近面。；表达了默认未启用、需显式设置，间接满足不能把实例配置当默认，但措辞不确定。

## 第35份：纯拒答的F为Unknown

N56-03的人工参考K=0、F=Unknown；两个AI给F=0。回答交付成功，不能冒充“生成失败”。未找到资料的自述、关于资料不存在的断言与可核验的领域事实需要分开。当前人工EAS_arith保留[0,50]界，不填0或1；保持原标签，不另行补分。其几何EAS上下界均为0，但依现行规则点估计仍标Unknown，不能无说明换算法。

## 两条输出不合规：并非JSON解析失败或输出截断

### gpt_sol · E16-02 · R-150962443949

原文在 5.2.3 节说明，当某些状态方程无法转换为基于内能的形式时，会改用局部温度定义热力学压力。此时 Grüneisen 系数 Γ_i 与声速 c_i^2 分别按什么关系计算？

冻结条件题标记：`False`；必要点：`['E16-02.K1', 'E16-02.K2', 'E16-02.K3']`。HTTP 200，finish_reason=stop。输出tokens=1066，上限8192，故不是额度耗尽。

实际A=0.75，而本题conditional=false，规范要求not_applicable。题干含“当……时”，模型可能把自然语言条件与维护侧“是否评价条件辨析”标签混同；这是可能解释，记录不能证明模型内部原因。通用Schema又允许A同时取数值和N/A，未将本题标签固化；本地校验正确拒绝整条评分。

当前保留失败，不将A自动改成N/A后回填本轮分数。本轮按实际不合规状态保留，不补成有效评分。

```json
 {"schema_version":"ch2_five_level_dual_eas","sample_id":"R-150962443949","judge_id":"gpt_sol","judge_version":"current-calibration-candidate","status":"complete","points":[{"criterion_id":"E16-02.K1","score":0,"reason":"未给出 Γ_i=(v_i/C_v)(∂p/∂T)。"},{"criterion_id":"E16-02.K2","score":0,"reason":"所述声速公式与原文公式不符。"},{"criterion_id":"E16-02.K3","score":0,"reason":"未表达“除非另有指定”的限定。"}],"fact_gate":0.25,"applicability_gate":0.75}
```

原件：[结果](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/evaluation/judge_calibration/85b246b6f258/gpt_sol/R-150962443949/result.json)；[请求与响应](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/evaluation/judge_calibration/85b246b6f258/gpt_sol/R-150962443949/requests/000.json)。响应SHA256 `c958f6f3b663d069a7f7db1e247215a8ce032ffbc5d54d77e14555be0cd4e170`。

### deepseek_flash · E51-01 · R-5204052d62d1

在blastFoam多区域温度耦合中，globalTemperatureCoupled计算补丁温度时依据哪些邻居量？若边界只有部分与邻居补丁重叠，说明unmappedT的用途与默认值，并判断这些说明是否足以保证整个补丁最终都处于该默认温度。

冻结条件题标记：`True`；必要点：`['E51-01.K1', 'E51-01.K2', 'E51-01.K3']`。HTTP 200，finish_reason=stop。输出tokens=2395，上限8192，故不是额度耗尽。

Gold只有K1—K3，实际输出还加入E51-01.K4，内容是整答事实混杂的评价，同时又输出fact_gate=0.5。没有重复已有ID，实际问题是多出一个必要点、并将F说明混入K列表。若只看错误名称“Duplicate/mismatched criteria”会误判为重复字段。

通用Schema仅规定points至少1项、criterion_id为任意字符串，未固定本题数量及ID；本地集合校验正确拒绝。当前不删除K4后接收其余分数，否则会改变已执行的首次有效响应标准。

```json
{"schema_version":"ch2_five_level_dual_eas","sample_id":"R-5204052d62d1","judge_id":"deepseek_flash","judge_version":"current-calibration-candidate","status":"complete","points":[{"criterion_id":"E51-01.K1","score":0.25,"reason":"仅提到依据邻居区域温度场，遗漏传热系数和辐射热流两项必要作用量。","answer_quote":"依据邻居区域的温度场"},{"criterion_id":"E51-01.K2","score":0.25,"reason":"unmappedT用途方向基本正确，但默认值错误（说0，原文293.15），且未澄清不应视为统一温度设置。","answer_quote":"默认值为0"},{"criterion_id":"E51-01.K3","score":0.5,"reason":"核心“不足以保证整个补丁处于默认温度”方向正确，但默认温度指错，也未说明逐面规则及实际结果不保证。","answer_quote":"不足以保证整个补丁最终处于该默认温度"},{"criterion_id":"E51-01.K4","score":0.5,"reason":"部分事实正确但关键默认值错误，整体事实正确与错误混杂。","answer_quote":"unmappedT用于处理未映射的温度值，默认值为0"}],"fact_gate":0.5,"applicability_gate":0.5,"reason":"默认值0与原文293.15冲突；核心不保证结论正确但条件参数和部分重叠表述有误。"}
```

原件：[结果](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/evaluation/judge_calibration/85b246b6f258/deepseek_flash/R-5204052d62d1/result.json)；[请求与响应](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/evaluation/judge_calibration/85b246b6f258/deepseek_flash/R-5204052d62d1/requests/000.json)。响应SHA256 `4014eee863de0e8a31d99cb0d25d674a6498c3cc20d67a99b20e4a79bdc130c8`。

## 一条传输失败：原因只能定位到连接阶段，不能定位服务内部

GPT · P04-02 · `R-9467c32eb158`。三次请求体SHA256均为`baaa8700f832cad49e8af4d4b1e179ed161a22f0ddce4671bc4e3abdfa1c1dd8`，没有更换问题、提示、模型或输出额度。

|尝试|持续秒数|异常|HTTP状态|
|---:|---:|---|---|
|1|27.437|RemoteDisconnected|未取得|
|2|29.265|RemoteDisconnected|未取得|
|3|26.766|RemoteDisconnected|未取得|

可确认：三次在26.766—29.265秒间发生RemoteDisconnected，没有完整HTTP状态、模型响应、finish_reason或usage；未达到客户端600秒超时。无法判定模型是否已在服务端执行完成，用量保持未知。退避5/15秒按记录执行，累计三次后停止该任务。

可能原因：代理/上游在约30秒前断开、网络链路抖动或上游请求异常。接近30秒只能提示进一步调查，不能证明固定30秒超时；当前客户端只保存异常类型，缺少代理trace-id和服务端日志，不能归因于内容过滤、模型能力或某个确切节点。单纯把600秒再加大没有针对性。

补充事实：暂停后的10条是从未发送的队列任务，后续已按独立执行补充补齐；它们不是对已收到评分的重复调用。三次耗尽的P04-02未被重置或再提交。


原件：[请求和重试台账](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/evaluation/judge_calibration/85b246b6f258/gpt_sol/R-9467c32eb158/requests/000.json)。三次原始记录位置与哈希均在[evidence.json](evidence.json)中。
