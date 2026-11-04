"""Offline discussion evidence; never edits labels, questions, Gold or live judging code."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

WORK=Path(__file__).resolve().parents[6]
REVIEW=WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration'
DATA=WORK/'graduation-datasets/chapter02_knowledge_qa'
EXP=WORK/'graduation-experiment-results/chapter2_retrieval'
TRIAL=REVIEW/'ai_calibration/85b246b6f258'
OUT=TRIAL/'discussion'
SOURCE=WORK/'PrincipiaBlastFoam-DSH/experiments/chapter2'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(WORK).as_posix()
def link(p,label=None,line=None):return f'[{label or p.name}]({p.as_posix()}{":"+str(line) if line else ""})'
def fmt(x):return 'Unknown' if x is None else f'{x:.2f}'

NOTES={
 13:('正确功能与错误配置层级混在一起',
     '回答给出intactField与破裂前边界条件，但将“字典顶层”解释为burstModel配置层级。两AI对名称/用途给了较高部分分，对末尾层级错误的事实扣分较人工轻。',
     'Gold的K2与回答包含的层级表述并不完全对应；不得仅看到“字典”一词判满分。此处是错误严重程度及复合必要点的部分分争议，不是两个AI一致即可推翻人工。',
     'K逐个核对名称、用途与层级含义；F依据错误是否会导致配置位置错误来区分重要错误与轻微措辞问题，不按字数投票。'),
 3:('自相矛盾的回答与“核心结论反向”',
    '前面说先处理rho、后算内能，末尾又说内能沿用初始rho。GPT与人工一致；DeepSeek将A降至0，两个AI相差33.33分。',
    '既有规则“核心结论反向A=0”与“局部错误可给部分分”缺少冲突处理顺序，当前材料不足以断言某一方必然错。',
    '区分明确唯一的反向核心结论与未消解的双向矛盾；后者不得挑一句作完整正确答案。建议作为需确认的解释细化，统一后重新校准，不追改本轮A=0.5。'),
 28:('关键参数含义写反，但其余描述笼统正确',
     '把beginUnrefine说成细化起始时间，Gold说明它是允许粗化开始的时刻；回答还有自动加密/粗化的笼统叙述。两AI完全一致，比人工低16.67分。',
     '两AI一致只说明共同判断，不是额外人工真值；分歧集中在错误是否已构成整答主要事实错误，而非格式。',
     'F对直接影响操作的参数语义错误单列为重要错误；泛泛而正确的背景表述不能抵消该错误。仍保留部分分，不建立“一错整题0”的硬门控。'),
 19:('一般结论碰巧正确，实际问答场景已被替换',
     '问题询问DDT燃速物性与初始场，回答改谈fvSchemes与时间离散，只保留“不会自动同步”的一般结论。人工A=0.25，GPT=0.5，DeepSeek=0.75。',
     '可用的一般常识与对题设对象的正确解释不是同一件事。这里还存在把数值格式与燃速配置联系起来的事实/因果问题。',
     '先锁定题设实体与文件作用域，再判K/A；不将“不会同步”当成完整场景结论。F核查实际陈述的事实和因果，避免仅因跑题就在K、F、A重复任意扣分。'),
 25:('公式出现了，但文字解释否认了归一化',
     '回答称使用总密度并列出公式，却又说没有归一化；两AI的F均为0.75，人工为0.5。',
     '公式或关键词可能掩盖后续相反解释；原手册符号解释还有独立未决问题，不能将手册转录一致当作实现已证实。',
     '核对公式与自然语言结论的一致性；只用本题已冻结的专业含义评分，不自行“修正”原文有争议的符号或添加评分要求。'),
 36:('覆盖不足被当成事实错误重复扣分',
     '回答说明跟踪守恒量并使用fields，却没列全体积积分和各类差值输出；人工F=1、两AI均F=0.75。',
     '没有说全与说错应分开；若不能指出具体错误陈述，不宜只因缺少必要点而再降低F。',
     'K处理遗漏；F要求指出可定位的错误断言。专业同义表达应按含义接受，不要求逐字复述Gold。'),
 37:('用途大致正确，但名称和字典层级都错误',
     '将intactField写成preBurst，层级说成boundaryConditions。GPT比人工高31.25分，DeepSeek与人工一致，是GPT自身误差最大的案例。',
     '这是同一题E28-01的另一份回答，不能与第13份合并成一次独立观察，也不能由用途相似推定条目名称正确。',
     'API名、字典键、参数默认值、单位方向和公式运算符按实质性事实核验；名称错误不应被“意思大概类似”自动豁免。'),
 31:('比较说到了一部分，但否认来源差异',
     '回答识别programmedIgnition，却称无需保留差异，且没有说明六点中四点为非零延迟；两AI将A判0，人工A=0.5。',
     '既有“核心反向=0”在混合正确证据与相反结论时如何使用，与第3份构成同一尺度争议。',
     '把模型选择、点数与非零延迟数量分开核对；总结不得抹去来源差异。采用与第3份相同的矛盾处理原则，而非按样本单独决定。'),
 59:('缩放方向与方程项混淆',
     'Gold为k=beta*(p*pScale)^alpha，回答写成除以pScale，还将右端速率含混称为扩散项或源项；GPT的F/A均比人工高0.25。',
     '数值方向、乘除与项的职责影响结论，不能只因出现1e-6和“压力项”就判主要正确。',
     '逐项核对运算符、量纲/缩放方向和方程作用位置；不新增Gold未要求的完整数值推导。'),
 48:('显式启用判断正确，但移动机制解释错误',
     '识别adjustLocations=yes，却把probeLocations的给定坐标等同于自动将网格外探针移入网格；两AI比人工低11.11分。',
     '这里既有遗漏默认值/最近面的K问题，也有对机制的断言，需要区分遗漏与已明确说错。',
     '分别核对显式配置、默认值和移动目标；不由可能处于网格外的坐标推断真实网格包含关系。'),
 29:('读脚本的缺失与错误工具名',
     '识别FSI脚本拆分区域，却没有明确普通building3D不调用splitMeshRegions，并将addEmptyPatch处理误写成coupledGlobalPolyPatch。',
     'GPT给予较多部分分；DeepSeek与人工一致。脚本中未调用和“原文没有提及”含义不同。',
     '对完整脚本范围内的有/无调用及具体参数逐项核验；不拿相关类型名替代实际执行命令。'),
 46:('专业常见公式替换了本版本模型定义',
     'exponential被改写成Arrhenius式，polynomial被缩为三次四系数；Gold要求kappa0*(T/Tref)^n0与8个系数。',
     '同名模型的一般专业知识不能覆盖所给手册的具体实现定义；两AI均给予一定正确方向分，但GPT的F更高。',
     '先以给定模型/版本的定义核验关键公式与参数，不因公式看起来熟悉、专业而增加覆盖；不要求背诵Gold未要求的符号。'),
 34:('均值掩盖单裁判对完整正确回答的扣分',
     '人工与DeepSeek均为100；GPT为83.33。回答明确区分固定直径与固定质量，并给出密度依赖关系。',
     '需查看GPT原备注是否将未声称的跨模型推广强加给回答；不能因为评分差异就认定专业事实存在争议。',
     '先定位回答实际声称了什么；禁止以Gold的防错提醒推定回答已经犯了该错误。'),
 47:('均值接近人工，但两个AI差16.67分',
     '人工75、GPT86.11、DeepSeek69.44，均值77.78。对“可能未启用”的不完整表述，K、F、A采用了不同扣分方式。',
     '均值抵消不能说明维度尺度已统一；省略默认值与明确说反默认值应分开。',
     '在K中处理默认值与最近面的遗漏；F只对确定错误的断言扣分，A依据题设显式启用与实际作用判断。'),
}

def build():
    assert not OUT.exists(),'Discussion artifacts already exist; preserve reviewed material'
    OUT.mkdir(parents=True)
    comparison=read(TRIAL/'comparison.json');rows=read(TRIAL/'per_sample.json')['samples']
    packets={p['sample_id']:p for p in read(REVIEW/'calibration/packets.json')['samples']}
    mapping=read(REVIEW/'administration/sample_mapping.json')
    phase_ids={phase:{x['task']['id'] for x in mapping['samples'] if x['phase']==phase} for phase in ['calibration','acceptance']}
    all_ids={q['id'] for q in read(DATA/'open/model/questions.json')}
    assert len(phase_ids['calibration'])==len(phase_ids['acceptance'])==50
    assert not phase_ids['calibration']&phase_ids['acceptance'] and phase_ids['calibration']|phase_ids['acceptance']==all_ids
    protected=[DATA/'binding.json',*[DATA/part/sub for part in ['open','objective'] for sub in ['model/questions.json','scoring/annotations.json','scoring/authoring/items.json']],
               DATA/'open/scoring/evidence.json',REVIEW/'calibration/calibration_completed_human_labels.json',REVIEW/'calibration/packets.json',
               REVIEW/'acceptance/packets.json',REVIEW/'acceptance/blank_labels.json',REVIEW/'completed_review.html',REVIEW/'administration/sample_mapping.json',
               TRIAL/'comparison.json',TRIAL/'per_sample.json',
               *[SOURCE/n for n in ['judge_prompt.txt','scoring_rules.json','judge_contract.py','judge_api_adapter.py','judge_calibration.py','runner.py','transport_retry.py','models.py']],
               *[WORK/'PrincipiaBlastFoam-DSH/config/llm'/n for n in ['models.yaml','providers.yaml','judging.yaml']],
               *[EXP/'release/planning'/n for n in ['execution.json','judge_calibration_authorization.json','run_protocol.json']]]
    hashes={rel(p):digest(p) for p in protected}
    main=sorted([r for r in rows if r['EAS_arith_differences']['dual_mean'] is not None],key=lambda r:(-abs(r['EAS_arith_differences']['dual_mean']),r['order']))[:12]
    wanted=[r['order'] for r in main]+[34,47]
    cases=[]
    for order in wanted:
        row=next(r for r in rows if r['order']==order);p=packets[row['sample_id']]
        for s in p['sources']:
            file=EXP/'data/resources/corpus'/s['path']
            assert digest(file)==s['file_sha256']
            excerpt='\n'.join(file.read_text(encoding='utf-8-sig').splitlines()[s['line_start']-1:s['line_end']])
            assert excerpt==s['excerpt'] and hashlib.sha256(excerpt.encode()).hexdigest()==s['excerpt_sha256']
        cases.append(dict(order=order,main_top12=order in [r['order'] for r in main],packet=p,metrics={j:row[j] for j in ['human','gpt_sol','deepseek_flash','dual_mean']},
                          records=row['records'],discussion=dict(zip(['issue','observed','interpretation','proposal'],NOTES[order])),
                          human_packet_sha256=hashlib.sha256(json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    failures=[]
    root=EXP/'evaluation/judge_calibration/85b246b6f258'
    for judge,sid in [('gpt_sol','R-150962443949'),('deepseek_flash','R-5204052d62d1'),('gpt_sol','R-9467c32eb158')]:
        folder=root/judge/sid;q=read(folder/'requests/000.json');p=packets[sid]
        attempts=[]
        for path in sorted((folder/'requests/attempts/000').glob('*.json')):
            a=read(path);attempts.append(dict(file=rel(path),file_sha256=digest(path),**{k:a.get(k) for k in ['status','http_status','error_type','seconds','started_utc','ended_utc','transport_attempts','request_sha256']}))
        raw=q.get('raw_response');content=raw['choices'][0]['message']['content'] if raw else None
        failures.append(dict(judge=judge,sample_id=sid,question_id=p['question_id'],question=p['question'],conditional=p['conditional'],
                             expected_criteria=[x['criterion_id'] for x in p['criteria']],result=read(folder/'result.json'),
                             result_file=rel(folder/'result.json'),request_file=rel(folder/'requests/000.json'),request_file_sha256=digest(folder/'requests/000.json'),
                             request_body_sha256=q['request_sha256'],raw_response_sha256=q.get('response_sha256'),
                             raw_content=content,usage=raw.get('usage') if raw else None,finish_reason=raw['choices'][0]['finish_reason'] if raw else None,
                             attempts=attempts))
    evidence=dict(schema='calibration_discussion_evidence_v1',created_utc=datetime.now(timezone.utc).isoformat(),status='discussion_only_no_execution',
                  calibration_protocol_sha256=comparison['protocol_sha256'],human_reference_label='人工参考',
                  source_provenance_record=rel(REVIEW/'calibration/human_review_completion.json'),protected_files=hashes,
                  selection='top12 absolute dual-mean minus human EAS_arith among identified pairs; stable display-order tie break; two additional cancellation diagnostics',
                  top12_orders=[r['order'] for r in main],additional_orders=[34,47],cases=cases,failures=failures,
                  acceptance=dict(calibration_questions=50,acceptance_questions=50,intersection=0,union=100,spare_unseen_question_ids=0,
                                  enabled_for_review=read(REVIEW/'acceptance/packets.json')['enabled_for_review'],answers_bound=sum(p['answer'] is not None for p in read(REVIEW/'acceptance/packets.json')['samples'])),
                  model_calls=0,formal_items_changed=False)
    save(OUT/'evidence.json',evidence)
    lines=['# 评分分歧与失败原因逐项分析','',
           '2026-11-04；讨论材料。表格统一标注“人工参考”，原始评分与来源记录保留。未修改人工评分、题目、Gold、裁判提示或运行协议，未发出模型请求。','',
           '主清单按双均值与人工参考的EAS_arith绝对差异排序取12条，平分按原显示序号排序；再补2条“均值掩盖个别裁判差异”的样本。完整60条仍在[逐答表](../DISAGREEMENTS.md)，不将这些挑出的案例用于重新计算总体分数。','',
           '|序号|题目|人工参考|GPT|DeepSeek|双均值|均值−人工|两裁判差|','|---:|---|---:|---:|---:|---:|---:|---:|']
    for x in cases:
        m=x['metrics'];h=m['human']['EAS_arith'];a=m['gpt_sol']['EAS_arith'];b=m['deepseek_flash']['EAS_arith'];v=m['dual_mean']['EAS_arith']
        lines.append(f"|{x['order']}|{x['packet']['question_id']}|{fmt(h)}|{fmt(a)}|{fmt(b)}|{fmt(v)}|{fmt(v-h)}|{fmt(abs(a-b))}|")
    lines+=['','第13份为双均值误差最大（+21.875分）；第3份为单裁判绝对误差最大（DeepSeek −33.33分），也是两裁判差异最大（33.33分）。第37份的GPT +31.25分为GPT自身最大绝对误差。第28份两AI一致却与人工不同，说明一致不能替代人工参考。重复题目ID保留各自回答，不当作独立知识样本。','']
    for x in cases:
        p=x['packet'];notes=x['discussion'];lines += [f"## 第{x['order']}份 · {p['question_id']}：{notes['issue']}",'',
            '**问题**：'+p['question'],'','**原回答**：','',p['answer'],'',
            '|评分者|逐必要点分值|K|F|A|EAS_arith|','|---|---|---:|---|---|---:|']
        for j,name in [('human','人工参考'),('gpt_sol','GPT'),('deepseek_flash','DeepSeek')]:
            m=x['metrics'][j];pts='、'.join(f"{v['criterion_id']}={v['score']}" for v in x['records'][j]['points'])
            lines.append(f"|{name}|{pts}|{m['K']:.4f}|{m['F']}|{m['A']}|{fmt(m['EAS_arith'])}|")
        lines+=['','**当前Gold必要点**：','']+[f"- `{c['criterion_id']}`：{c['claim']}" for c in p['criteria']]
        lines+=['','**事实、解释与建议**：','',notes['observed'],'',notes['interpretation'],'','拟议处理：'+notes['proposal'],'',
                '**来源依据**：','']
        for s in p['sources']:
            file=EXP/'data/resources/corpus'/s['path']
            lines += [f"- {link(file,s['path'],s['line_start'])}，L{s['line_start']}—L{s['line_end']}；文件SHA256 `{s['file_sha256']}`。"]
        lines += ['', '<details><summary>已核对原文摘录</summary>','',*[('> '+line) if line else '>' for s in p['sources'] for line in s['excerpt'].splitlines()],'','</details>','']
        lines += ['**已记录备注**：','']
        for j,name in [('human','人工参考'),('gpt_sol','GPT'),('deepseek_flash','DeepSeek')]:
            record=x['records'][j];reasons=[record.get('reason','')]+[v.get('reason','') for v in record['points']]
            cleaned=[]
            for text in reasons:
                if text.startswith('AI辅助人工评分：'):text=text[text.find('第'):]
                if text:cleaned.append(text)
            if cleaned:lines.append(name+'：'+'；'.join(cleaned))
        lines+=['']
    lines+=['## 第35份：纯拒答的F为Unknown','',
            'N56-03的人工参考K=0、F=Unknown；两个AI给F=0。回答交付成功，不能冒充“生成失败”。未找到资料的自述、关于资料不存在的断言与可核验的领域事实需要分开。当前人工EAS_arith保留[0,50]界，不填0或1；保持原标签，待确认未来纯拒答规则。其几何EAS上下界均为0，但依现行规则点估计仍标Unknown，不能无说明换算法。','',
            '## 两条输出不合规：并非JSON解析失败或输出截断','']
    for fail in failures[:2]:
        lines += [f"### {fail['judge']} · {fail['question_id']} · {fail['sample_id']}",'',fail['question'],'',
                  f"冻结条件题标记：`{fail['conditional']}`；必要点：`{fail['expected_criteria']}`。HTTP 200，finish_reason=stop。输出tokens={fail['usage']['completion_tokens']}，上限8192，故不是额度耗尽。",'']
        if fail['judge']=='gpt_sol':
            lines += ['实际A=0.75，而本题conditional=false，规范要求not_applicable。题干含“当……时”，模型可能把自然语言条件与维护侧“是否评价条件辨析”标签混同；这是可能解释，记录不能证明模型内部原因。通用Schema又允许A同时取数值和N/A，未将本题标签固化；本地校验正确拒绝整条评分。','',
                      '当前保留失败，不将A自动改成N/A后回填本轮分数。未来可不让模型生成非条件题A，由调用侧按固定标签注入N/A；这属于新接口协议，而非对旧记录的事后修补。','']
        else:
            lines += ['Gold只有K1—K3，实际输出还加入E51-01.K4，内容是整答事实混杂的评价，同时又输出fact_gate=0.5。没有重复已有ID，实际问题是多出一个必要点、并将F说明混入K列表。若只看错误名称“Duplicate/mismatched criteria”会误判为重复字段。','',
                      '通用Schema仅规定points至少1项、criterion_id为任意字符串，未固定本题数量及ID；本地集合校验正确拒绝。当前不删除K4后接收其余分数，否则会改变已执行的首次有效响应标准。未来使用固定槽位和禁止额外属性的题目专属Schema。','']
        lines += ['```json',fail['raw_content'],'```','',f"原件：{link(WORK/fail['result_file'],'结果')}；{link(WORK/fail['request_file'],'请求与响应')}。响应SHA256 `{fail['raw_response_sha256']}`。",'']
    fail=failures[2]
    lines += ['## 一条传输失败：原因只能定位到连接阶段，不能定位服务内部','',
              f"GPT · P04-02 · `{fail['sample_id']}`。三次请求体SHA256均为`{fail['request_body_sha256']}`，没有更换问题、提示、模型或输出额度。",'',
              '|尝试|持续秒数|异常|HTTP状态|','|---:|---:|---|---|']
    for i,a in enumerate(fail['attempts'],1):lines.append(f"|{i}|{a['seconds']:.3f}|{a['error_type']}|未取得|")
    lines += ['', '可确认：三次在26.766—29.265秒间发生RemoteDisconnected，没有完整HTTP状态、模型响应、finish_reason或usage；未达到客户端600秒超时。无法判定模型是否已在服务端执行完成，用量保持未知。退避5/15秒按记录执行，累计三次后停止该任务。', '',
              '可能原因：代理/上游在约30秒前断开、网络链路抖动或上游请求异常。接近30秒只能提示进一步调查，不能证明固定30秒超时；当前客户端只保存异常类型，缺少代理trace-id和服务端日志，不能归因于内容过滤、模型能力或某个确切节点。单纯把600秒再加大没有针对性。','',
              '补充事实：暂停后的10条是从未发送的队列任务，后续已按独立执行补充补齐；它们不是对已收到评分的重复调用。三次耗尽的P04-02未被重置或再提交。', '',
              '拟议诊断：先用不含正式评分的合成请求核对同服务的连接/首字节时序与请求ID；对比非流式与服务实际支持的流式接口，确认完整结束标记和usage后才固定协议。记录脱敏的错误阶段、errno及允许的trace-id；有必要时由服务侧排查。不能将目前一次问题称为已修复。','',
              f"原件：{link(WORK/fail['request_file'],'请求和重试台账')}。三次原始记录位置与哈希均在[evidence.json](evidence.json)中。",'']
    (OUT/'DISAGREEMENT_ANALYSIS.md').write_text('\n'.join(lines),encoding='utf-8')
    score={'enum':[0,.25,.5,.75,1,'unknown']}
    point={'type':'object','properties':{'score':score,'answer_quote':{'type':'string','maxLength':160},'reason':{'type':'string','maxLength':160}},'required':['score','answer_quote','reason'],'additionalProperties':False}
    for conditional in [False,True]:
        props={'points':{'type':'object','properties':{f'p{i}':point for i in range(1,4)},'required':['p1','p2','p3'],'additionalProperties':False},'F':score,'reason':{'type':'string','maxLength':240}}
        if conditional:props['A']=score
        wire={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Discussion-only fixed-three-point '+('conditional' if conditional else 'nonconditional')+' example','type':'object','properties':props,'required':list(props),'additionalProperties':False}
        save(OUT/('wire_schema_conditional.json' if conditional else 'wire_schema_nonconditional.json'),wire)
    save(OUT/'decisions.json',dict(status='pending_discussion',applied=False,live_prompt_or_rules_changed=False,
        items=[dict(id=x,status='pending',owner='负责人',current_scores_changed=False) for x in ['contradictory_core_conclusion','critical_fact_partial_credit','omission_vs_fact_error','pure_refusal_F','fixed_wire_schema','transport_reconciliation_and_unsent_queue','full_denominator_acceptance_decision','calibration_answer_adoption','acceptance_failure_contingency']]))
    return evidence

if __name__=='__main__':
    x=build();print(json.dumps(dict(created=str(OUT),cases=len(x['cases']),failures=len(x['failures']),model_calls=0),ensure_ascii=False))
