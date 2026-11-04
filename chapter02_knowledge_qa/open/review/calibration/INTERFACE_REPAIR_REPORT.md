# 三模型完整合成验证结果

后续状态（2026-11-04）：已完成自动传输重试实现，当前60任务为59完整回答、1模型失败、0传输未解决。下文为原阶段历史分析，不改判原失败。当前见[生成报告](GENERATION_REPORT.md)及[重试报告](TRANSPORT_RETRY_REPORT.md)。


更新：2026年11月4日。本轮已按负责人要求完成三模型全部合成检查，查询上限512字符、输出上限2048 tokens、temperature=0不变。每模型12用例、14请求，合计36用例、42请求；逐字比较标准不变。**整套检查已完成，但未全部通过：Qwen3-8B为12/12，Qwen3-14B为11/12，Llama-3.1-8B为9/12。** 新60任务、验收、全量及AI裁判均未启动。

## 本轮改动与执行范围

换行用例改为在明确起止标记之间直接展示原始两行文本，不再先给一个需要反转义的JSON字符串。预期答案仍为第一行、真实换行、两个空格、第二行、真实制表符、末尾；不包括标记及首尾额外换行。没有对返回答案执行strip、二次反转义、替换或人工修补。

离线回归确认其余11个用例、全部Schema和预期输出与上一轮一致，32项运行器／接口测试通过。生产runtime.py、models.py、structured_actions.py及分词器本轮未改，只调整合成输入呈现及检查／留证工具。上一轮bundle、profile及MCP集成检查通过记录保留，本轮未改这些组件或重复启动其服务。

新检查先提交20次请求，Llama换行用例失败时原运行器暂停。为完成负责人本轮要求的整套检查，续检只提交未发送用例的22次请求；没有重发已经提交的用例，没有重新运行失败回答。续检允许已知内容不一致如实记失败后继续其他未发用例，未知传输仍暂停。两个执行段使用同一份冻结用例及相同的核心接口实现，原分段summary和结果不覆盖，完整汇总通过(model, case, turn)去重核验。

本轮两个执行段分别是实验technical下的`compact_actions_multiline_20261104/`与`compact_actions_multiline_completion_20261104/`；本轮42请求不混入上一轮`compact_actions_20261104/`的22请求。

## 结果与失败分类

|模型|用例通过|请求闭合|JSON与预算检查|结果|
|---|---:|---:|---|---|
|Qwen3-8B|12/12|14/14|全部通过|本轮合成用例全部通过|
|Qwen3-14B|11/12|14/14|全部通过|外部空白诱导用例交付纯空格答案|
|Llama-3.1-8B|9/12|14/14|全部通过|换行逐字不一致、客观题说明不一致、外部空白诱导交付纯空格答案|

42次请求全部HTTP 200、正常stop，模型身份、输入分词、32768输入加预留输出和2048输出上限一致；没有截断、连续空白输出循环、未知结果或自动重发。输入合计14,889 tokens，输出861 tokens，单次输出最多32 tokens。原始HTTP响应体哈希与保存的解码结果42份逐一一致，查询交付均未超过512字符。

**JSON/Schema通过不等于有效作答通过。** 本轮动作Schema允许非空长度的字符串，单个空格能满足该Schema；正式运行器随后调用的parse_action会拒绝纯空白answer。离线按正式解析器重放后，40/42动作通过，以下两条纯空格动作被拒绝。不能将它们作为有效回答计数。

|模型与用例|预期与实际差异|判定与含义|
|---|---|---|
|Llama · newlines|内部中文、换行、两个缩进空格及制表符均保留，但实际answer比预期多了首、尾各一个换行。|逐字比较失败；保留差异，不裁剪后计通过。本地解析没有添加这些换行。|
|Llama · objective|answer预期为“合成客观题”，实际为“42”；final_answer实际为“42”，与预期一致。|说明字段的逐字要求失败；唯一客观答案字段本身正确，不能据此称客观题答案错误。|
|Llama · external_whitespace|answer预期为“空白约束验证”，实际为单个空格。|失败；正式动作解析器拒绝空白答案。JSON字段外未产生额外空白，但有效作答约束未达到。|
|Qwen 14B · external_whitespace|同上，answer实际为单个空格。|失败；正式动作解析器同样拒绝，不视作有效final。|

三模型均通过带双引号代码、反斜杠公式、空catalog、read_source、search→final及read_source→final多轮用例。Qwen 8B与14B通过新的原始多行文本逐字测试。以上只说明本轮合成情形的表现，不是正式300题准确率或裁判校准结果。

## 保留材料与离线核验

上一轮22请求中的Llama字面量转义失败保持原样，其全部71份技术文件及对应5份实现快照均保留。原60任务的238份文件、100＋200题目、Gold、来源、binding、人工材料、空白标签和关闭的派发授权均未改。

本轮完整汇总见`administration/multiline_interface_check.json`，正式动作解析器重放见`administration/multiline_action_contract_check.json`。原`administration/interface_repair_check.json`仍记录上一轮暂停状态，不覆写为通过。原失败目录及两段新检查均可按保存哈希核验。

从工作区根目录执行以下命令，仅查本地文件：

```powershell
& .\PrincipiaBlastFoam-DSH\.local\knowledge-qa-venv\Scripts\python.exe -X utf8 graduation-datasets/chapter02_knowledge_qa/open/review/calibration/tools/verify_interface_repair.py
& .\PrincipiaBlastFoam-DSH\.local\knowledge-qa-venv\Scripts\python.exe -X utf8 graduation-datasets/chapter02_knowledge_qa/open/review/calibration/tools/verify_interface_repair.py --run-id compact_actions_20261104
& .\PrincipiaBlastFoam-DSH\.local\knowledge-qa-venv\Scripts\python.exe -X utf8 graduation-datasets/chapter02_knowledge_qa/open/review/calibration/tools/verify_generation.py --binding
```

完整性核验通过不等于接口验收通过。旧失败、严格逐字要求和无效答案判定均未改变；当前仍不能声明整套三模型接口验收通过。

## 后续处理边界

本轮只完成检查及汇总，不再追加模型请求。下一步应先讨论纯空白答案的生成约束，以及换行复制和客观题说明是否属于正式接口必须满足的要求。若调整这些约束，需事前明确新检查标准并保留本轮失败，不能事后将本轮改判通过。当前正式运行器已经拒绝纯空白答案，该保护不应移除。

负责人已选择未来原60任务全部采用同一新协议重新生成，不采用旧55＋新5。当前尚未重新prepare或冻结新正式运行协议，execution.json保持关闭；不会因本次检查完成而派发新60、验收、全量或AI裁判。
