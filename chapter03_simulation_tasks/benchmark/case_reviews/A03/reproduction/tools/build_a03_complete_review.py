"""Analyse existing A03 evidence for a complete human review; never run CFD/LLMs.

Derived errors are conditional diagnostics, not frozen benchmark scores.
"""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'references/review/feature_mape_20261105/human_review/A03'
RUN = ROOT / 'references/runs/20261022-a03'
EXP = ROOT / 'references/experiments/mendeley-zv7y78twd9-v2'
FONT = FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
COLORS = ['#326CAC', '#BD6A32', '#408779']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipt = load(RUN / 'A03-run.json')
    native_file = RUN / 'A03/postProcessing/probes/0/p'
    binding = next(r for r in receipt['output_files'] if r['path'] == 'postProcessing/probes/0/p')
    assert sha(native_file) == binding['sha256']
    lines = native_file.read_text(encoding='utf-8').splitlines()
    native = np.array([[float(v) for v in s.split()] for s in lines if s.strip() and not s.startswith('#')])
    assert native.shape[1] == 4 and native[0, 0] == 0 and native[-1, 0] == .004
    times = native[:, 0]
    gauge = native[:, 1:] - 101300.
    exported = list(csv.DictReader((RUN / 'A03-pressure.csv').open(encoding='utf-8-sig')))
    for j in range(3):
        data = [r for r in exported if r['sensor_id'] == f'P{j+1}']
        assert np.allclose([float(r['time_s']) for r in data], times, rtol=1e-12, atol=1e-15)
        assert np.allclose([float(r['overpressure_pa']) for r in data], gauge[:, j], rtol=1e-12, atol=1e-7)
    peaks = np.max(gauge, axis=0) / 1000
    peak_times = times[np.argmax(gauge, axis=0)]
    reference_rows = list(csv.DictReader((OUT / 'table1_peak_candidates.csv').open(encoding='utf-8-sig')))
    errors = []
    trials = []
    raw_data = {}
    for trial in [1, 2, 4]:
        refs = [r for r in reference_rows if int(r['trial']) == trial]
        ref = np.array([float(r['published_peak_pressure_kpa']) for r in refs])
        assert len(ref) == 3 and np.all(ref > 0)
        ape = np.abs(peaks-ref) / np.abs(ref) * 100
        trials.append({'trial': trial, 'n_expected': 3, 'n_compared': 3,
            'reference_peaks_kpa': ref.tolist(), 'ape_percent': ape.tolist(),
            'diagnostic_peak_mape_percent': float(np.mean(ape)),
            'conditional_numerical_band': 'higher_accuracy' if np.mean(ape) <= 15 else 'qualified' if np.mean(ape) <= 30 else 'not_qualified',
            'formal_pass': None})
        for j in range(3):
            errors.append({'trial': trial, 'experiment_sensor': f'Pi0{j+2}', 'numerical_sensor': f'P{j+1}',
                'reference_table1_kpa': ref[j], 'simulation_peak_overpressure_kpa': peaks[j],
                'signed_error_kpa': peaks[j]-ref[j], 'ape_percent': ape[j],
                'assessment': 'conditional_diagnostic_not_formal_score'})
        raw = EXP / f'raw/C4_20g00{trial}.txt'
        text = raw.read_text(encoding='utf-8-sig').splitlines()
        start = next(i for i, s in enumerate(text) if s.startswith('Time\t'))
        names = text[start].split()
        a = np.array([[float(v) for v in s.split()] for s in text[start+2:] if s.strip()])
        raw_data[trial] = (a[:, 0], np.stack([a[:, names.index(s)]*100 for s in ['Pi02', 'Pi03', 'Pi04']], axis=1))
    with (OUT / 'peak_comparison_diagnostic.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(errors[0]));w.writeheader();w.writerows(errors)
    audit = load(RUN / 'A03-audit.json')
    mass = load(ROOT / 'references/review/round6/source-mass-energy/A03.json')
    thermal = load(ROOT / 'references/review/round6/temperature/A03.json')
    result = {
        'task_id': 'A03', 'date': '2026-11-05', 'status': 'complete_evidence_for_human_review',
        'comparison_kind': 'existing_operator_numerical_candidate_vs_published_experimental_features',
        'not_an_agent_e2e_run': True,
        'conditional_assumptions': [
            'Treat Table1 first-series Ppeak as the comparable overpressure feature; pressure-definition approval remains pending.',
            'Use the existing numerical gauge definition p_absolute-101300Pa and native full0..4ms peaks.',
            'Use Pi02/Pi03/Pi04 mapped to P1/P2/P3 without sensor removal.',
            'Report every retained experimental trial1/2/4 separately; trial3 is excluded by the paper, not by prediction error.',
            'No fitted time shift, smoothing, amplitude scaling, or candidate-result-driven reference selection.'
        ],
        'formal_eligibility': 'pending_condition_pressure_clock_and_model_review',
        'numerical_result': {'peak_overpressure_kpa': peaks.tolist(), 'peak_clock_ms': (peak_times*1000).tolist(),
            'sample_count_each_sensor': len(times), 'window_s': [float(times[0]), float(times[-1])],
            'native_and_exported_series_match': True,
            'wall_seconds_solver': receipt['commands'][-1]['wall_seconds'],
            'wall_seconds_all_commands': sum(r['wall_seconds'] for r in receipt['commands']),
            'solver_completed': receipt['solver_completed'], 'mesh_ok': audit['mesh_ok'],
            'all_command_exit_codes': [r['exit_code'] for r in receipt['commands']],
            'operator_reference_delivery_complete_is_not_agent_task_success': True},
        'trials': trials, 'pointwise_errors': errors,
        'arrival_time_mape': {'value': None, 'reason': 'No independently verified experimental time zero and arrival definition. Peak clock is not arrival time.'},
        'history_error': {'value': None, 'reason': 'Raw recording clock and solver start are not independently aligned; displayed curves are unshifted diagnostics only.'},
        'mass_diagnostics': mass['actual_source'],
        'temperature_evidence': {k: thermal[k] for k in ['nonpositive_T_observed_in_saved_states', 'early_step_temperature_evidence', 'maximum_saved_T_K', 'scope']},
        'per_task_approval': False, 'gold_approved': False, 'ready': False,
        'new_solver_runs': 0, 'solver_changes': 0,
        'source_snapshot': []
    }
    paths = [native_file, RUN/'A03-pressure.csv', RUN/'A03-run.json', RUN/'A03-audit.json', RUN/'A03-build.json',
        ROOT/'references/review/round6/source-mass-energy/A03.json', ROOT/'references/review/round6/temperature/A03.json',
        OUT/'table1_peak_candidates.csv', EXP/'raw/Kristoffersen et al - 2024 SW - Semi-confined blast loading.pdf']
    paths += [EXP/f'raw/C4_20g00{i}.txt' for i in [1, 2, 3, 4]]
    result['source_snapshot'] = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in paths]
    (OUT/'complete_review_metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    fig, ax = plt.subplots(figsize=(8.8, 3.8), dpi=150)
    vals = [t['diagnostic_peak_mape_percent'] for t in trials]
    ax.barh([2,1,0], vals, color=COLORS, height=.52)
    for y, v in zip([2,1,0], vals):ax.text(v+.35, y, f'{v:.2f}%', va='center', fontsize=12)
    for v,label in [(15,'15% 较高精度线'),(30,'30% 合格线')]:
        ax.axvline(v, color='#8A929C', ls='--', lw=1);ax.text(v+.25, 2.6, label, fontproperties=FONT, fontsize=9)
    ax.set_yticks([2,1,0],['试次1* / 三点','试次2* / 三点','试次4* / 三点'],fontproperties=FONT)
    ax.set_xlim(0,35);ax.set_ylim(-.6,3);ax.set_xlabel('诊断性峰值 MAPE (%)',fontproperties=FONT)
    ax.set_title('固定三点、全部保留试次：7.11% / 13.78% / 6.78%',fontproperties=FONT,pad=17)
    ax.spines[['top','right','left']].set_visible(False);ax.grid(axis='x',alpha=.12);fig.tight_layout();fig.savefig(OUT/'diagnostic-mape.png',facecolor='white');plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.8,4.4),dpi=150)
    for k,t in enumerate(trials):
        ax.scatter(np.arange(3)+(k-1)*.18,t['reference_peaks_kpa'],s=48,marker=['o','s','^'][k],c=COLORS[k],label=f'实验试次{t["trial"]}*')
    ax.scatter(np.arange(3),peaks,s=82,marker='D',facecolors='none',edgecolors='#202936',linewidths=1.7,label='现有A03仿真')
    for j,v in enumerate(peaks):ax.annotate(f'{v:.2f}',(j,v),xytext=(0,-22),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xticks([0,1,2],['Pi02 / P1','Pi03 / P2','Pi04 / P3']);ax.set_xlim(-.5,2.5);ax.set_ylim(650,2900)
    ax.set_ylabel('峰值 (kPa；实验压力定义待核)',fontproperties=FONT);ax.set_title('出版实验峰值与已有仿真峰值',fontproperties=FONT,pad=14)
    ax.legend(prop=FONT,frameon=False,ncol=2);ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(OUT/'peaks-simulation-comparison.png',facecolor='white');plt.close(fig)

    fig, axes = plt.subplots(3,1,figsize=(8.8,8),dpi=150,sharex=True)
    for j,ax in enumerate(axes):
        for k,(trial,(rt,rp)) in enumerate(raw_data.items()):
            keep=(rt>=0)&(rt<=.004)
            ax.plot(rt[keep]*1000,rp[keep,j],lw=.8,alpha=.7,c=COLORS[k],label=f'实验{trial}* 原记录时钟')
        ax.plot(times*1000,gauge[:,j]/1000,c='#202936',lw=1.35,label='A03 求解起始时钟')
        ax.set_ylabel(f'Pi0{j+2} / P{j+1}\n压力 (kPa)',fontproperties=FONT);ax.grid(alpha=.14);ax.spines[['top','right']].set_visible(False)
    axes[0].set_title('未经平移的原始压力曲线：时钟未校准，不计算到达/时程误差',fontproperties=FONT,pad=16)
    axes[0].legend(prop=FontProperties(fname='C:/Windows/Fonts/msyh.ttc',size=8),frameon=False,ncol=2)
    axes[-1].set_xlim(0,4);axes[-1].set_xlabel('各自记录的时间 (ms)',fontproperties=FONT)
    fig.tight_layout();fig.savefig(OUT/'pressure-curves-unshifted.png',facecolor='white');plt.close(fig)

    fig,ax=plt.subplots(figsize=(8.8,3.1),dpi=150)
    a=np.array([t['ape_percent'] for t in trials]);im=ax.imshow(a,cmap='YlOrRd',vmin=0,vmax=40,aspect='auto')
    for y in range(3):
        for x in range(3):ax.text(x,y,f'{a[y,x]:.2f}%',ha='center',va='center',fontsize=13,color='white' if a[y,x]>25 else '#202936')
    ax.set_xticks([0,1,2],['Pi02/P1','Pi03/P2','Pi04/P3']);ax.set_yticks([0,1,2],['试次1*','试次2*','试次4*'],fontproperties=FONT)
    ax.set_title('逐点APE：全部九个比较值均显示',fontproperties=FONT,pad=14)
    fig.colorbar(im,ax=ax,label='APE (%)');fig.tight_layout();fig.savefig(OUT/'pointwise-ape.png',facecolor='white');plt.close(fig)
    Image.open(OUT/'paper-page-09.png').crop((100,118,1180,650)).save(OUT/'source-table-2.png')
    print(json.dumps({'trials':[{'trial':t['trial'],'mape':t['diagnostic_peak_mape_percent']} for t in trials],
        'native_rows':len(times),'new_solver_runs':0,'formal_pass':None},ensure_ascii=False))


if __name__ == '__main__':main()
