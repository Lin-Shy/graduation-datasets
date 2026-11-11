"""Integrate the first positive pressure phase on the sealed S10 records."""

import csv
import hashlib
import io
import json
from pathlib import Path
import re
from statistics import mean
import tarfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
CASE = HERE.parent
JOB = CASE / "job-8953576"
COLLECTION = JOB / "collection-pyxz4uv3"
TRACE = "case/postProcessing/groundPressure/0/p"


def read(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def positive_phase(time, pressure, seed_pa, peak_time, end):
    seeds = np.flatnonzero((time <= end) & (pressure >= seed_pa))
    if not len(seeds):
        return None
    start = int(seeds[0])
    positive = start
    while positive > 0 and pressure[positive - 1] > 0:
        positive -= 1
    left = positive - 1
    ending = start
    while ending + 1 < len(time) and pressure[ending + 1] > 0:
        ending += 1
    right = ending + 1
    if left < 0 or right == len(time):
        return None
    begin = time[left] - pressure[left] * (time[positive] - time[left]) / (pressure[positive] - pressure[left])
    finish = time[ending] + pressure[ending] * (time[right] - time[ending]) / (pressure[ending] - pressure[right])
    if not 0 <= begin <= peak_time <= finish <= end:
        return None
    integration_times = np.r_[begin, time[positive:right], finish]
    integration_pressure = np.r_[0, pressure[positive:right], 0]
    impulse = np.sum((integration_pressure[1:] + integration_pressure[:-1]) / 2 * np.diff(integration_times))
    return float(begin), float(finish), float(impulse)


def ape(prediction, reference):
    assert reference > 0
    return abs(prediction - reference) / reference * 100


def error_range(prediction, reference):
    lo, hi = reference
    endpoints = sorted([ape(prediction, lo), ape(prediction, hi)])
    return [0 if lo <= prediction <= hi else endpoints[0], endpoints[1]]


def main(figure_path=None):
    if figure_path is not None:
        from plot_pressure_review_20261110 import NATIVE_STYLE
    plan = read(HERE / "protocol.json")
    peaks = read(JOB / "peak_score.json")
    ref_path = CASE / "reference_repeatability_20261107/comparison.json"
    reference = read(ref_path)
    assert peaks["completed"] and peaks["delivery_complete"]
    assert peaks["native_run"]["job_id"] == plan["job_id"]
    assert peaks["window_s"] == plan["native_window_s"] == [0, .003]
    assert sha((CASE / "figure6-7-000.png").read_bytes()) == reference["source_sha256"]["figure6-7-000.png"]
    raw = (COLLECTION / "evidence" / TRACE).read_bytes()
    archive = COLLECTION / "native-evidence.tar"
    assert sha(archive.read_bytes()) == read(COLLECTION / "collection_receipt.json")["original_archive_sha256"]
    with tarfile.open(archive) as tar:
        assert tar.extractfile(TRACE).read() == raw
    header_radii = [float(v) for v in re.findall(rb"^# Probe \d+ \(0 ([\d.]+) 0\)$", raw, re.M)]
    assert header_radii == plan["radii_m"]
    time, *pressures = np.loadtxt(io.BytesIO(raw), unpack=True)
    assert time[0] == 0 and time[-1] >= plan["native_window_s"][1] and np.all(np.diff(time) > 0)
    rows = []
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 6.6), layout="constrained")
    fig.suptitle("S10 RP80 | First positive phase and published impulse references", fontweight="bold")
    for ax, radius, pressure_abs, peak, ref in zip(axes.flat[:3], plan["radii_m"], pressures,
                                                  peaks["rows"], reference["rows"], strict=True):
        assert radius == peak["radius_m"] == ref["radius_m"]
        assert pressure_abs[0] == plan["ambient_pressure_Pa"]
        assert np.all(np.isfinite(pressure_abs)) and np.all(pressure_abs > 0)
        pressure = pressure_abs - plan["ambient_pressure_Pa"]
        seed = plan["seed_kPa"]
        end = plan["native_window_s"][1]
        phase = positive_phase(time, pressure, seed * 1000, peak["peak_time_s"], end)
        other = {str(s): positive_phase(time, pressure, s * 1000, peak["peak_time_s"], end)
                 for s in plan["sensitivity_seed_kPa"]}
        impulse = phase[2] if phase else None
        measurement = ref["positive_impulse_Pas"]
        experimental = measurement["figure_6_7_experimental"]
        numerical = measurement["figure_6_7_published_OpenFOAM"]
        center = measurement["figure_6_1_center"]
        rows.append({"radius_m": radius, "native_impulse_Pa_s": impulse, "closed_first_lobe_s": phase[:2] if phase else None,
                     "seed_sensitivity": other, "experiment_Pa_s": experimental, "published_OpenFOAM_Pa_s": numerical,
                     "experimental_APE_pct": ape(impulse, experimental) if phase else None,
                     "published_OpenFOAM_APE_pct": ape(impulse, numerical) if phase else None,
                     "Fig_6_1_experimental_center_APE_pct": ape(impulse, center) if phase else None,
                     "Fig_6_1_peak_center_APE_pct": ape(peak["peak_kPa"], ref["peak_kPa"]["figure_6_1_center"]),
                     "Fig_6_7_peak_APE_pct": peak["APE_percent"]["experiment"],
                     "experimental_APE_range_3px_pct": error_range(impulse, measurement["figure_6_7_digitization_range_3px"])
                     if phase else None})
        plotted = time <= end
        ax.plot(time[plotted] * 1000, pressure[plotted] / 1000, **(NATIVE_STYLE if figure_path else {"lw": 1.25, "color": "#1d746a"}))
        if phase:
            in_phase = (phase[0] <= time) & (time <= phase[1])
            ax.fill_between(time[in_phase] * 1000, 0, pressure[in_phase] / 1000, color="#a0c9bd")
            title = f"r = {radius:.3f} m   |   I+ = {impulse:.3f} Pa·s"
        else:
            title = f"r = {radius:.3f} m   |   positive phase unresolved"
        ax.axhline(0, color="0.45", lw=.6)
        ax.set(title=title, xlabel="仿真时间（ms）" if figure_path else "Native time (ms)",
               ylabel="超压（kPa）" if figure_path else "Overpressure (kPa)", xlim=(0, end * 1000))

    assert len(rows) == len(plan["radii_m"]) == 3
    ax = axes[1, 1]
    for shift, key, color, label in (
        (-.22, "native_impulse_Pa_s", "#197267", "Native"),
        (0, "experiment_Pa_s", "#9a5638", "Measured"),
        (.22, "published_OpenFOAM_Pa_s", "#6c7f98", "Published OpenFOAM"),
    ):
        ax.bar(np.arange(3) + shift, [row[key] if row[key] is not None else np.nan for row in rows],
               width=.21, color=color, label=label)
    ax.set(title="固定半径的首正相冲量" if figure_path else "Positive impulse by fixed radius", ylabel="Pa·s", xticks=range(3),
           xticklabels=[f"{row['radius_m']:.3f} m" for row in rows])
    ax.legend(fontsize=8)
    for axis in axes.flat:
        axis.grid(axis="y", alpha=.15)
    if figure_path is not None:
        fig.savefig(figure_path, dpi=165, facecolor="white")
        plt.close(fig)
        return
    fig.savefig(HERE / "positive_impulse.png", dpi=170)
    plt.close(fig)

    metrics = {}
    for group in ("experimental", "published_OpenFOAM", "Fig_6_1_experimental_center"):
        errors = [row[group + "_APE_pct"] for row in rows]
        metrics[group] = {"denominator": len(errors), "resolved": sum(e is not None for e in errors),
                          "MAPE_pct": mean(errors) if all(e is not None for e in errors) else None}
    bounds = [row["experimental_APE_range_3px_pct"] for row in rows]
    variation = [mean(column) for column in zip(*bounds)] if all(b is not None for b in bounds) else None
    metrics["experimental"]["MAPE_range_3px_pct"] = variation
    peak_comparison = {"Fig_6_1_experimental_center_MAPE_pct": mean(row["Fig_6_1_peak_center_APE_pct"] for row in rows),
                       "Fig_6_7_experimental_MAPE_pct": peaks["MAPE_percent"]["experiment"]}
    (HERE / "impulse_review.json").write_text(json.dumps({
        "job_id": plan["job_id"], "trace_sha256": sha(raw), "references_sha256": sha(ref_path.read_bytes()),
        "protocol_sha256": sha((HERE / "protocol.json").read_bytes()), "metrics": metrics,
        "peak_comparison": peak_comparison, "rows": rows},
        indent=2) + "\n", encoding="utf-8")
    with (HERE / "impulse_pointwise.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"impulse": metrics, "peak": peak_comparison}, indent=2))


if __name__ == "__main__":
    main()
