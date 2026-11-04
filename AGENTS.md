# 各章数据集维护规则

2026-11-04最新决定：额外60份人工验收已取消，以现有60份人工参考及双裁判校准结果采用现有双裁判方法。客观200＋开放100、分类配额和Gold不变；已授权完成正式协议冻结与技术核验后直接启动三模型全量。唯一活动运行入口为`PrincipiaBlastFoam-DSH/experiments/chapter2/formal_experiment.py`，授权与状态见实验`release/planning/formal_experiment.json`及`formal_execution.json`。不重做人工评分或校准，不把旧验收门槛作为派发条件。以下早期阶段说明保留历史身份。

2026-11-04当前进展：开放问答本轮60份人工参考评分已完成（AI建议、真人逐项复核确认、助手转录），客观题200道参考答案已由负责人审核通过。已完成两个AI裁判及逐答均值与人工参考的校准比较；裁判输出失败、人工Unknown及完整分母均保留。这是校准诊断，不是独立人评或验收通过；验收仍锁定，规则尚未为验收冻结，全量未启动。报告见`graduation-datasets/chapter02_knowledge_qa/open/review/calibration/ai_calibration/85b246b6f258/REPORT.md`。

以下生成/准备阶段状态保留其历史身份；当前完成范围以上述进展为准。

## 第2章当前维护约束（2026-11-03）

负责人2026-11-03最新确定：正式题集为同等级的开放问答100题与客观题200题，全量参加评价，不另设开发集或测试留出集。唯一活动入口为 `graduation-datasets/chapter02_knowledge_qa/` 的 `open/` 与 `objective/`。开放题四类各25题，保留69主题、24知识组和42来源文件；客观题填空60、短答60、单选50、判断30。当前Gold、来源、选题和转换记录由tools/rebuild.py离线核验。参数组运行前固定并全部报告，不按正式成绩选优。新实验尚未运行，独立人工复核待完成。

历史200题Dev40/Test160及172题客观题的现存题集原件由实验release/manifests/dataset_before_reconstruction.json按内容哈希保存；不是第二套活动题集，不重建已永久删除的冷备份。既有实验根目录为 `graduation-experiment-results/chapter2_retrieval/`，开放问答结果在 `results/`、原始执行在 `test160_runs/`，客观题统一在 `objective/`。开放问答5120项生成、4989份回答双评闭合；客观题4472项任务、4190份回答、282项失败。失败仍计固定分母。原独立人工审计未达门槛、客观题独立专家审核未完成、8B潜在答案暴露和事后补试边界均保留。

当前源码唯一入口为 `PrincipiaBlastFoam-DSH/experiments/chapter2/`；检索与调用公共模块在 `experiments/retrieval_method/`。8B仅使用超算推理，私有配置为根目录 `.env.supercomputer`，字段为 `QWEN_SUPERCOMPUTER_*`；14B继续使用项目 `config/llm` 的代理配置。两者32K总额度，客户端并发上限分别为8和20。

历史原始证据和已有回答保留真实部署、路径和协议身份，禁止改写为超算运行。负责人已授权删除旧失败尝试、重复版本和第2章临时恢复材料；最终失败状态与统计分母保留。冻结原件通过布局映射和内容哈希解析，不创建旧实验恢复副本。Gold、必要点、证据与人工标签仅限评分侧。本次目录整理不授权新模型调用或新实验；Git历史另行处理。
