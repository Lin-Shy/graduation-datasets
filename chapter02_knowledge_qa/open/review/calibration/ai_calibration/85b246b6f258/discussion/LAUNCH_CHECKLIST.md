# 正式全量实验启动检查单

2026-11-04更新：额外60份验收已取消。负责人采用现有60份人工参考和双裁判校准，授权完成技术核验后直接启动三模型全量；当前已启动。本文替代此前的验收准备建议，不再将额外人评、改提示、复校准或原数值目标作为派发条件。

|项目|本次完成情况|证据入口|
|---|---|---|
|题集及Gold|客观200＋开放100，各分类配额不变；300题和50个来源文件离线核验通过|数据集binding；正式preflight离线回执|
|现有校准|60条人工参考、两个裁判及均值沿用，原分歧、失败和未知不变|人工参考JSON、comparison.json、CALIBRATION_RESULTS.md|
|额外验收|已取消，旧锁定入口禁止派发；原样本回归全量普通任务|review_workflow.json；旧入口取消保护|
|正式协议冻结|171配置、51,300项任务；源码、环境、题目、Gold、人工参考、图和索引、模型、分词器、裁判提示/Schema均绑定|formal_experiment.json指向的manifest.json|
|现有60项采用|实际推理依赖、分词器、模型和资源等价性核验通过，全部采用，剩余51,240项生成|正式协议adoption_proof及adoptions|
|评分入口|客观34,200项按显式final_answer确定性评分；开放17,100项由两裁判独立评分并取均值|formal_experiment.py scoring；objective_scoring.py|
|自动重试和恢复|超时/连接中断、408/429/5xx等最多3次；600秒，退避5/15秒；恢复重放、完成跳过、耗尽不清零、不重试内容|58项Python测试及正式冻结retry字段|
|离线工程检查|58项Python测试、3项bundle测试、profile导出、21工具MCP状态冒烟、57组检索功能核验通过|release/validation/formal_offline_checks.json及resource_checks.json|
|三模型合成核验|单步/多步接口、身份、分词器计量、预算核验通过；能力导致的截断/答错如实保留|technical/formal_full_preflight_20261104/summary.json|
|双裁判合成核验|两个裁判均完成，保持原提示、规则、输入及输出上限|同一preflight回执|
|授权与实际启动|新正式授权已启用；三个生成进程和一个评分进程后台并行|formal_execution.json；supervisor.json及FORMAL_RUN_REPORT.md|

题目、Gold和人工评分保持不变；查询512字符、生成输出2048 tokens、证据6k/12k/24k；两个8B各8并发，14B为20。裁判输入24576、输出8192（含思考）。不把合成用例的能力失败强制修到100%，不依据全量分数调提示或择优更换回答。

报告仍区分模型失败、传输未知、裁判不合规、未运行；固定完整分母，客观准确率与开放EAS分开，全部预算和配置完整报告。当前只有启动及早期运行状态，完整方法对比成绩将在全量结束和结果核验后形成。原校准结果分析仍可用于论文，其实测统计不因取消额外验收而改变。

活动入口：[正式实验README](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/README.md)。本页不再保留额外验收的待办限制。
