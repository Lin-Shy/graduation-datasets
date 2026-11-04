"""Derive descriptive writing materials from the unchanged published calibration."""
from pathlib import Path
import hashlib
import json
import statistics

WORK = Path(__file__).resolve().parents[6]
TRIAL = WORK/'graduation-datasets/chapter02_knowledge_qa/open/review/calibration/ai_calibration/85b246b6f258'
OUT = TRIAL/'discussion'
JUDGES = ('gpt_sol', 'deepseek_flash', 'dual_mean')
NAMES = dict(gpt_sol='GPT-6-sol', deepseek_flash='DeepSeek-v4.1-flash', dual_mean='双裁判逐答均值')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ranks(values):
    return [sum(x < value for x in values) + (sum(x == value for x in values)+1)/2 for value in values]


def descriptive(rows, judge):
    human = [r['human']['EAS_arith'] for r in rows]
    ai = [r[judge]['EAS_arith'] for r in rows]
    error = [abs(a-h) for a,h in zip(ai, human)]
    return dict(n=len(rows), unique_questions=len({r['question_id'] for r in rows}),
                mae=statistics.mean(error), bias=statistics.mean(a-h for a,h in zip(ai,human)),
                median_absolute_error=statistics.median(error), max_absolute_error=max(error),
                within_points={str(t):dict(count=sum(e <= t+1e-9 for e in error), denominator=len(rows),
                                          rate=sum(e <= t+1e-9 for e in error)/len(rows)) for t in (0,5,10,15,20)},
                pearson_r=statistics.correlation(human, ai), spearman_rho=statistics.correlation(ranks(human), ranks(ai)))


def build():
    destination = OUT/'descriptive_results.json'
    if destination.exists():
        raise FileExistsError('Published writing materials already exist; verify instead of overwriting')
    report = read(TRIAL/'comparison.json')
    rows = read(TRIAL/'per_sample.json')['samples']
    common = [r for r in rows if all(isinstance(r[j]['EAS_arith'], (float,int)) for j in ('human', *JUDGES))]
    point = {}
    for judge in JUDGES[:2]:
        p = report['point_agreement'][judge]
        exact = sum(cell['count'] for cell in p['confusion'] if cell['left'] == cell['right'])
        within = sum(cell['count'] for cell in p['confusion'] if abs(cell['left']-cell['right']) <= .25+1e-9)
        point[judge] = dict(identified_pairs=p['n'], full_points=162, unknown_or_missing=p['unknown_pairs'],
                            exact_count=exact, exact_rate=exact/p['n'], within_one_count=within, within_one_rate=within/p['n'],
                            mae=p['mae'], quadratic_weighted_kappa=p['quadratic_kappa'])
    maximum = {}
    for judge in JUDGES:
        row = max((r for r in rows if r['EAS_arith_differences'][judge] is not None), key=lambda r:abs(r['EAS_arith_differences'][judge]))
        maximum[judge] = dict(order=row['order'], question_id=row['question_id'], difference=row['EAS_arith_differences'][judge])
    derived = dict(schema='calibration_descriptive_writing_materials_v1', status='descriptive_only_no_rule_changes',
                   protocol_sha256=report['protocol_sha256'], human_reference_display_label='人工参考',
                   source_files={str(p.relative_to(WORK).as_posix()):digest(p) for p in (TRIAL/'comparison.json',TRIAL/'per_sample.json')},
                   common_cohort={j:descriptive(common,j) for j in JUDGES},
                   common_valid_answers_only={j:descriptive([r for r in common if not r['generation_failed']],j) for j in JUDGES},
                   point_agreement=point, maximum_errors=maximum,
                   correlation_scope='Descriptive on the same identifiable cohort; not an agreement certificate; ties use average ranks; no independence or significance claim',
                   new_model_calls=0, human_labels_questions_Gold_or_live_rules_changed=False)
    for judge in JUDGES:
        prior = report['common_pair_comparisons'][judge]['EAS_arith']
        assert abs(derived['common_cohort'][judge]['mae']-prior['mae']) < 1e-10
        assert abs(derived['common_cohort'][judge]['bias']-prior['bias_AI_minus_human']) < 1e-10
    destination.write_text(json.dumps(derived,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines = ['# 现有AI裁判与人工参考的校准结果及分析','',
        '2026-11-04。按负责人最新要求，仅描述现有校准结果，不提出规则、提示或接口改进，不安排重新校准。人工参考、题目、Gold、回答及原始裁判结果均保持不变。','',
        '## 结论应怎样表述','',
        '**在本轮可比较样本上，AI裁判与人工参考总体接近，必要点评分具有较高的一致程度；双裁判均值的总体有符号偏差较小，但仍有少量回答存在较大分歧。** 这里的“总体接近/基本一致”是对实际误差和一致性指标的描述，不等于每份回答相同，也不改写此前的数值目标或未开展的验收状态。','',
        '## 样本和评分口径','',
        '校准共60项回答任务，涉及50个题目ID，三模型各20项；59份完整回答、1项模型输出失败。人工参考60条、必要点162个；第35份F为Unknown。两个裁判分别评分，再按逐答EAS取均值。K为必要点均值，F为整答事实，A只用于30项条件题。指标的详细定义见[论文参考材料](THESIS_REFERENCE.md)。','',
        '生成失败按既定规则固定EAS/Strict=0；裁判输出不合规与传输未解决记缺失，不将其当作原回答0分。Unknown不插补。以下主结果保留原固定分母，点估计注明可识别配对数量。','',
        '## 综合分数与人工参考的接近程度','',
        '|方案|可比较/60|EAS_arith MAE|AI−人工平均偏差|完整60项MAE界|',
        '|---|---:|---:|---:|---|']
    for judge in JUDGES:
        p=report['comparisons'][judge]['EAS_arith']; low,high=p['fixed_denominator_mae_bounds']
        lines.append(f"|{NAMES[judge]}|{p['identified_pairs']}|{p['mae']:.2f}|{p['bias_AI_minus_human']:+.2f}|[{low:.2f}, {high:.2f}]|")
    lines += ['', 'MAE表示平均每份回答偏离人工参考的绝对分数，不会正负抵消；平均偏差则反映整体偏宽或偏严。均值偏差约+0.55分，说明总体没有明显单向漂移；其MAE仍为5.67分，不能把偏差小解释成逐答几乎没有误差。','',
        '### 相同56项上的横向比较','',
        '|方案|MAE|偏差|误差中位数|Pearson r|Spearman ρ|',
        '|---|---:|---:|---:|---:|---:|']
    for judge in JUDGES:
        p=derived['common_cohort'][judge]
        lines.append(f"|{NAMES[judge]}|{p['mae']:.2f}|{p['bias']:+.2f}|{p['median_absolute_error']:.2f}|{p['pearson_r']:.3f}|{p['spearman_rho']:.3f}|")
    lines += ['', '三个方案使用相同的56项、46个题目ID。相关系数仅描述分数变化和排序关系；高相关不能单独证明绝对分数一致，应与MAE、偏差及分歧案例合看。双均值的相关系数较高、有符号偏差最小，但MAE未优于DeepSeek，不能宣称均值在所有指标上都最好。','',
        '|双均值与人工的绝对差|数量/56|比例|','|---|---:|---:|']
    for t in (0,5,10,15,20):
        p=derived['common_cohort']['dual_mean']['within_points'][str(t)]
        lines.append(f"|{'相同' if t==0 else f'≤{t}分'}|{p['count']}/56|{100*p['rate']:.1f}%|")
    lines += ['', '这些是描述性的误差区间，不是新增验收阈值。44/56项误差不超过10分，55/56项不超过20分；剩余较大的误差不能用总体平均掩盖。完整60项还含4项无法给出均值与人工的EAS差值，因此不能把上述比例写成全60项的比例。','',
        '## K/F/A维度与必要点的一致性','',
        '|方案|维度|可比较/适用数|维度MAE|差≤0.25数量/可比较数|比例|',
        '|---|---|---:|---:|---:|---:|']
    for judge in JUDGES:
        for dim in ('K','F','A'):
            p=report['comparisons'][judge][dim]; count=round(p['within_025_rate']*p['identified_pairs'])
            lines.append(f"|{NAMES[judge]}|{dim}|{p['identified_pairs']}/{p['full_denominator']}|{p['mae']:.3f}|{count}/{p['identified_pairs']}|{100*p['within_025_rate']:.1f}%|")
    lines += ['', '一档指0.25的差值容差。K为必要点均分，双裁判维度均值也可能落在原五档之间；不是把所有值重新离散为五档。可识别配对中，双均值K/F全部处于一档内，A为26/28。条件判断比必要点覆盖和事实维度更容易出现较大尺度差异。','',
        '|单裁判逐必要点比较|已知/162|完全相同|差≤0.25|二次加权κ|',
        '|---|---:|---:|---:|---:|']
    for judge in JUDGES[:2]:
        p=point[judge]
        lines.append(f"|{NAMES[judge]}|{p['identified_pairs']}|{p['exact_count']}/{p['identified_pairs']}（{100*p['exact_rate']:.1f}%）|{p['within_one_count']}/{p['identified_pairs']}（{100*p['within_one_rate']:.1f}%）|{p['quadratic_weighted_kappa']:.3f}|")
    lines += ['', 'κ与逐点完全相同率来自原comparison.json，而非新增评分。必要点同属回答、同题及相近知识，不能视为156或159个独立专业问题；这些统计说明本轮评分接近程度，不作总体显著性或评审者间一致性推断。','',
        '## 分歧集中在哪里','',
        '- 关键名称、配置层级、公式运算方向：回答有正确用途或背景，但操作细节错误时，对错误严重程度的权衡不同。第13份均值比人工高21.875分，为均值绝对误差最大项。',
        '- 前后矛盾与条件结论：第3份GPT与人工同为45.83，DeepSeek为12.50，低33.33分。这是两个单裁判合计范围内的最大绝对误差；第37份GPT高31.25分是GPT自身最大误差。',
        '- 遗漏与事实错误：第36份人工F=1，两AI为0.75，主要差异是未覆盖内容是否连带影响整答事实评价。',
        '- 场景适用性与纯拒答：第19份泛化结论与具体题设的对应程度不同；第35份人工F为Unknown，保留这一事实，不为了闭合均值而补分。','',
        '这些案例说明分歧主要发生在部分正确、关键局部错误及混合条件判断的边界。它们是误差分析，不是本轮修改规则的待办，也不能由两AI一致推翻人工参考。完整原件见[案例分析](DISAGREEMENT_ANALYSIS.md)。','',
        '## 完成情况与结果边界','',
        'GPT为58项complete、1项输出不合规、1项传输未解决；DeepSeek为59项complete、1项输出不合规。各自complete中包含1项生成失败固定0，因此真实有效模型评分响应为57与58份。输出不合规分别为非条件题数值A与额外K4；传输失败三次约27—29秒连接中断，根因未确定。上述记录保持原状态，不事后修补。','',
        '均值EAS_arith MAE的题目聚类bootstrap 95%区间为[4.04,7.32]，偏差区间为[−1.50,2.70]，2000次重采样。去掉生成失败固定0后，均值已知配对55份、MAE=5.77、偏差=+0.56，整体解释没有明显改变；主口径仍保留该失败。','',
        '此前记录的MAE≤5、绝对偏差≤3、K/F/A一档内≥90%目标继续如实保留。当前MAE略高于5；完整分母下均值MAE界为[5.31,8.04]，A一档内比例界为86.7%—93.3%，因此“总体接近”不等于所有原目标已达到。这里不新增改进或重跑要求，也不把描述性结论写成尚未发生的验收通过。','',
        '人工参考沿用原60条，单人记录的取得过程及来源回执保留；不能据此声称双人人评一致性或无AI建议的独立人评。本轮仅校准裁判，不给出检索方法优劣结论。验收、全量均未启动。','',
        '## 写作与追溯入口','',
        '- [论文写作参考](THESIS_REFERENCE.md)：方法、结果、分析与局限的可复用段落。',
        '- [描述性统计](descriptive_results.json)：新增误差区间、相关系数与原始统计的绑定；不修改comparison.json。',
        '- [原始汇总](../comparison.json)、[逐答记录](../per_sample.json)、[证据索引](evidence.json)：全部原评分、来源和失败原件。','']
    (OUT/'CALIBRATION_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(common_pairs=len(common), point_agreement=point, largest_errors=maximum, model_calls=0),ensure_ascii=False))


if __name__ == '__main__':
    build()
