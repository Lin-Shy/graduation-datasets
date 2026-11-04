# 第2章正式题集

2026-11-04最新决定：额外60份人工验收已取消，以现有60份人工参考及双裁判校准结果采用现有双裁判方法。客观200＋开放100、分类配额和Gold不变；已授权完成正式协议冻结与技术核验后直接启动三模型全量。唯一活动运行入口为`PrincipiaBlastFoam-DSH/experiments/chapter2/formal_experiment.py`，授权与状态见实验`release/planning/formal_experiment.json`及`formal_execution.json`。不重做人工评分或校准，不把旧验收门槛作为派发条件。以下早期阶段说明保留历史身份。

客观题200道与开放问答100道为同等级的两个部分，全量参加评价，不另设开发集或测试留出集。客观题fill60/short60/single50/judge30，开放S0/S1/M0/M1各25；开放覆盖69主题、24知识组、42来源文件与8组成对条件题。

论文与实验先介绍objective/，再介绍open/。公开输入在各自model/questions.json；评分标注在scoring/annotations.json，当前完整维护输入为scoring/authoring/items.json。开放证据在open/scoring/evidence.json。工具只从当前维护输入及原始语料重建，不依赖旧题集或实验结果。

`python tools/rebuild.py`离线检查；`python tools/rebuild.py --write`按当前维护输入重建派生文件。逐题有效内容等价基准在实验release/validation/current_dataset_equivalence.json，当前binding为`d683a5b65a536797fc468a85d6aa7420625ba9e01c2b99e35aaf8450d87c48f6`。

review/保留当前人工records.json、当前selection.json和未决问题current_issues.json；objective/review/overlap.json登记当前来源重叠。2026-11-04，负责人确认客观题200道参考答案全部审核通过，见objective/review/reference_answer_confirmation.json。开放问答本轮60份回答的人工参考评分已完成（AI提出建议、真人逐项确认、助手转录），见open/review/calibration/；这不是对100道开放题全部逐题评分，也不将尚未完成的题干或来源资料复核改为已完成。

当前尚无新正式实验成绩；参数、裁判与校准仍待冻结；负责人已确认资源充足，不设置费用审批或费用上限。当前题集有方法开发使用经历，不能宣称为历史未见的独立测试。Gold、authoring、review和人工记录仅限评分或维护侧。
