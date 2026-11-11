# 单人人工参考与双裁判校准

2026-11-04：负责人采用现有60份人工参考及双裁判校准结果，取消额外60份验收。正式协议已冻结，三模型全量生成和评分已启动；不再另行抽样人评或重新校准。当前运行见[正式实验入口](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/README.md)及[启动记录](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/FORMAL_RUN_REPORT.md)。

## 现有校准资料

本轮60条人工参考已填写并通过离线校验：59份完整回答、1项模型输出失败；162个必要点评分无漏填。第35份F保留Unknown，第49份生成失败按既定规则记0。评分记录与原过程记录保持不变。

- [已填写页面](completed_review.html)、[人工参考JSON](calibration/calibration_completed_human_labels.json)。
- [完成记录](calibration/human_review_completion.json)、[离线校验与逐样本指标](calibration/human_labels_validation.json)。
- [校准报告](ai_calibration/85b246b6f258/REPORT.md)、[逐答差异](ai_calibration/85b246b6f258/DISAGREEMENTS.md)。
- [结果分析与论文资料](ai_calibration/85b246b6f258/discussion/README.md)，包含总体差异、维度及必要点一致性、分歧、失败和写作参考。
- [正式全量启动检查单](ai_calibration/85b246b6f258/discussion/LAUNCH_CHECKLIST.md)。

两个裁判及逐答均值与人工参考的比较已完成。负责人据此决定沿用现有提示、模型配置、规则及双裁判均值进行全量；校准的实测数字、未知项和失败记录均原样保留。客观题200道参考答案已审核通过，正式题集继续为客观200＋开放100及现有配额。

## 评分与采用规则

K为必要点等权平均，F为整答事实，A为适用条件；分值为0/0.25/0.5/0.75/1，非条件题A为N/A。条件题EAS_arith=100×(K+F+A)/3，非条件题=100×(K+F)/2，另报EAS_geo和Strict。两个裁判各自独立计算，再取恰好两者的均值；一方未知时不退回单裁判冒充双均值。

模型生成失败按固定分母保留并记0；传输未知、裁判不合规与未运行分别记录，不补造分值。原60项校准任务经生成依赖、分词器、服务与资源等价性核验后全部纳入正式矩阵，包括1项生成失败及既有裁判失败，不择优重跑或替换。

本轮校准每模型20项，阶段内50个题目ID；属于回答评分抽样，不是问答题集开发/测试划分。原额外验收任务已回归普通全量任务，不再要求独立人工标签。原空白验收材料仅为历史记录，旧freeze-acceptance及旧分阶段派发入口已禁止重新打开。

## 只读核验与恢复

`tools/verify_ai_calibration.py`核对已执行校准快照、原始响应和人工参考；历史生成恢复见[生成报告](GENERATION_REPORT.md)、[自动重试报告](TRANSPORT_RETRY_REPORT.md)及`tools/verify_transport_recovery.py --binding`。原校准调用队列保持关闭。

全量的活动入口为`PrincipiaBlastFoam-DSH/experiments/chapter2/formal_experiment.py`，由新正式协议和独立授权控制。`verify`核对冻结，`status`读取进度，`supervise`恢复同一协议。每请求最多3次传输尝试、600秒、退避5/15秒；已保存响应恢复重放，已完成项跳过，计数不清零，不按内容重试。生成端禁止访问Gold、review和人工记录。
