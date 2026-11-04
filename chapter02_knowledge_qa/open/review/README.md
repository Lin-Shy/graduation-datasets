# 当前复核工作区

2026-11-04最新决定：额外60份人工验收已取消，以现有60份人工参考及双裁判校准结果采用现有双裁判方法。客观200＋开放100、分类配额和Gold不变；已授权完成正式协议冻结与技术核验后直接启动三模型全量。唯一活动运行入口为`PrincipiaBlastFoam-DSH/experiments/chapter2/formal_experiment.py`，授权与状态见实验`release/planning/formal_experiment.json`及`formal_execution.json`。不重做人工评分或校准，不把旧验收门槛作为派发条件。以下早期阶段说明保留历史身份。

records.json：当前逐题人工审核及问题/Gold绑定，真实状态保留。current_issues.json：当前仍适用的未决问题。selection.json：当前正式题位与配额。开放题source_pages/保留当前原文公式复核页面。客观题overlap.json登记当前来源事实重叠。新增人工校准、资料复核及结果可在此维护；生成和检索禁止读取本目录。

回答裁判校准现位于[calibration/README.md](calibration/README.md)：单人60份校准＋60份锁定验收，匿名评分表为[calibration/index.html](calibration/index.html)。2026-11-04已绑定校准60任务：55份有效回答＋5条生成失败，真人评分仍为空白；验收60份尚未生成或解锁。运行与绑定核验见[calibration/GENERATION_REPORT.md](calibration/GENERATION_REPORT.md)。
