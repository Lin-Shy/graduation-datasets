# 原60项人工参考与最终裁判评分

更新：2026-11-13。原60项人工参考已完成，162个必要点；两路最终裁判各60/60有效。EAS、K、F完整60项可比较，A为30项条件题。第35项（R-98886a357967，N56-03）经评审人确认F=0.25，K=0/0/0/0、A不适用，算术EAS=12.5、几何EAS=0。第49项模型输出失败按原规则固定零分，并纳入分母。

## 当前唯一入口

- [最新人工JSON](calibration/calibration_completed_human_labels.json)与[已填写页面](completed_review.html)。
- [人工完成记录](calibration/human_review_completion.json)、[标签校验](calibration/human_labels_validation.json)、[第35项复核依据](calibration/item35_review_revision_20261112.json)。
- [最终评分比较报告](final_comparison_20261112/REPORT.md)、[比较JSON](final_comparison_20261112/comparison.json)、[逐项结果](final_comparison_20261112/per_sample.json)。
- [当前任务来源映射](final_comparison_20261112/source_mapping.json)与[哈希清单](final_comparison_20261112/manifest.json)。

双裁判均值EAS MAE=5.88、偏差−0.08，Pearson与Spearman均0.968。经负责人确认，第一阶段60份人工参考由领域专家独立逐项评分形成。第35项由评审人重新定档。历史归档中的过程描述以本次勘误为准，详见[稿件来源说明](../../../../../graduation-thesis-materials/graduation-manuscript/CHAPTER2_SOURCES.md)。

另一次[新增60份修订人工参考](../validation_20261112/README.md)已完成，单独统计，双均值MAE=9.86、偏差−7.19。两批问题ID不重叠，但共享领域来源，不构成外部未见测试集。

## 评分与复现

K为必要点等权平均，F为整答事实，A为条件适用性；非条件题A不参与分母。两路裁判独立计算后取逐答均值，不择优。数据、回答、Gold和规则不因文稿维护改变。

当前统计从实验current/index.json解析最终有效回答与评分；制图目录refresh_calibration_final.py读取本目录最新人工标签重新比较。旧ai_calibration/85b246b6f258及生成/恢复报告仅为历史协议与调用证据，不读取其中的旧人工评分副本来生成当前统计。冻结文件保持不变。
