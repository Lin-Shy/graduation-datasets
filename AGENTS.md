# 各章数据集维护规则

2026-11-05 SSH恢复：负责人授权单卡A100运行两个8B。经三模型接口及双8B的16/32并发合成检查后，已从暂停断点恢复；原35,171份终态文件核验保留。8B经本机18000/18001的SSH回环隧道调用，guidance、BF16、上下文32768；正式查询512、输出2048、题集200＋100及评分规则不变。当前生成入口为`execution_updates/fast_resume_20261105/resume_runner.py`，评分沿用双裁判8／8。SSH中断需要恢复通道；已有尝试次数不清零。以下为此前阶段记录。

2026-11-05当前状态：负责人为调试模型部署与镜像配置，已于北京时间2026-11-05 11:26:57暂停全部第2章实验。三模型生成、双裁判评分、监督和自动恢复进程均已停止，剩余进程0；派发授权关闭，禁止自动恢复。已有回答、评分及请求台账原样保留，题集200＋100、Gold和评分规则不变。须待负责人恢复指令及新服务配置核验后，按原尝试预算从断点继续。详见[暂停记录](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/FORMAL_PAUSE_20261105.md)。以下为此前阶段记录。

2026-11-05解码排查与评分提速：双裁判已从GPT／DeepSeek的2／1提高至8／8，提示、模型参数和评分规则不变。监督及评分活动入口改为`graduation-experiment-results/chapter2_retrieval/execution_updates/throughput_20261105/operations.py`，安全启动用同目录`start.ps1`；生成仍使用ce2155fd55fa补充，当前Qwen／14B／Llama并发16／20／32，8B自动降档与回升继续有效。Qwen延迟已定位到服务端解码，硬关闭思考的合成对照没有消除差距，正式推理请求未改变。本次交接前29,315份终态文件逐一核验未改。详见[最新排查记录](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/REDEPLOYMENT_RESUME_20261105.md)。以下为此前阶段记录。

2026-11-05重新部署后已恢复：两个8B的新URL已通过单步/多轮接口及16/32并发长输入检查，以Qwen3-8B／Qwen3-14B／Llama-3.1-8B并发32／20／32启动，实际并发及临时降档见运行状态。新执行补充ce2155fd55fa沿用原方法协议95a4872aacdd，保留全部旧回答、评分及台账。活动入口为`graduation-experiment-results/chapter2_retrieval/execution_updates/redeploy_20261105/redeploy_runner.py`；安全启动用同目录start.ps1。详见[恢复报告](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/REDEPLOYMENT_RESUME_20261105.md)。下文为此前阶段记录。

2026-11-05暂停：负责人因重新部署两个8B推理服务，要求暂时停止全部实验。三模型生成、双裁判评分和监督进程均已停止，生成与评分授权已关闭，禁止自动恢复。已有回答、评分及请求台账保留；以`release/planning/formal_pause.json`和[暂停记录](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/FORMAL_PAUSE_20261105.md)为当前状态。服务部署完成后，先核验模型、接口及并发并取得恢复指令，再记录执行补充并断点继续。以下为此前运行记录。

2026-11-05执行更新：14B已恢复；两个8B从8提高到16并发，并按成功请求观察自动尝试32，遇连续传输错误会降档。正式方法协议95a4872aacdd、题目、Gold及评分不变；执行补充c0d6407fa327记录传输错误映射和调度变更。当前监督与恢复入口为`graduation-experiment-results/chapter2_retrieval/execution_updates/speedup_20261105/runner.py supervise`，启动环境需包含`PrincipiaBlastFoam-DSH/experiments/retrieval_method`的PYTHONPATH。具体检查和运行状态见[执行更新报告](D:/1/graduation-projects/graduation-experiment-results/chapter2_retrieval/EXECUTION_UPDATE_20261105.md)。以下为原启动记录。

2026-11-04最新决定：额外60份人工验收已取消，以现有60份人工参考及双裁判校准结果采用现有双裁判方法。客观200＋开放100、分类配额和Gold不变；正式协议与技术核验已完成，三模型全量生成及双裁判评分已在后台启动（协议95a4872aacdd）。唯一活动运行入口为`PrincipiaBlastFoam-DSH/experiments/chapter2/formal_experiment.py`，授权与状态见实验`release/planning/formal_experiment.json`及`formal_execution.json`。不重做人工评分或校准，不把旧验收门槛作为派发条件。以下早期阶段说明保留历史身份。

2026-11-04当前进展：开放问答本轮60份人工参考评分已完成（AI建议、真人逐项复核确认、助手转录），客观题200道参考答案已由负责人审核通过。已完成两个AI裁判及逐答均值与人工参考的校准比较；裁判输出失败、人工Unknown及完整分母均保留。这是校准诊断，不是独立人评或验收通过；验收仍锁定，规则尚未为验收冻结，全量未启动。报告见`graduation-datasets/chapter02_knowledge_qa/open/review/calibration/ai_calibration/85b246b6f258/REPORT.md`。

以下生成/准备阶段状态保留其历史身份；当前完成范围以上述进展为准。

## 第2章当前维护约束（2026-11-03）

负责人2026-11-03最新确定：正式题集为同等级的开放问答100题与客观题200题，全量参加评价，不另设开发集或测试留出集。唯一活动入口为 `graduation-datasets/chapter02_knowledge_qa/` 的 `open/` 与 `objective/`。开放题四类各25题，保留69主题、24知识组和42来源文件；客观题填空60、短答60、单选50、判断30。当前Gold、来源、选题和转换记录由tools/rebuild.py离线核验。参数组运行前固定并全部报告，不按正式成绩选优。新实验尚未运行，独立人工复核待完成。

历史200题Dev40/Test160及172题客观题的现存题集原件由实验release/manifests/dataset_before_reconstruction.json按内容哈希保存；不是第二套活动题集，不重建已永久删除的冷备份。既有实验根目录为 `graduation-experiment-results/chapter2_retrieval/`，开放问答结果在 `results/`、原始执行在 `test160_runs/`，客观题统一在 `objective/`。开放问答5120项生成、4989份回答双评闭合；客观题4472项任务、4190份回答、282项失败。失败仍计固定分母。原独立人工审计未达门槛、客观题独立专家审核未完成、8B潜在答案暴露和事后补试边界均保留。

当前源码唯一入口为 `PrincipiaBlastFoam-DSH/experiments/chapter2/`；检索与调用公共模块在 `experiments/retrieval_method/`。8B仅使用超算推理，私有配置为根目录 `.env.supercomputer`，字段为 `QWEN_SUPERCOMPUTER_*`；14B继续使用项目 `config/llm` 的代理配置。两者32K总额度，客户端并发上限分别为8和20。

历史原始证据和已有回答保留真实部署、路径和协议身份，禁止改写为超算运行。负责人已授权删除旧失败尝试、重复版本和第2章临时恢复材料；最终失败状态与统计分母保留。冻结原件通过布局映射和内容哈希解析，不创建旧实验恢复副本。Gold、必要点、证据与人工标签仅限评分侧。本次目录整理不授权新模型调用或新实验；Git历史另行处理。
