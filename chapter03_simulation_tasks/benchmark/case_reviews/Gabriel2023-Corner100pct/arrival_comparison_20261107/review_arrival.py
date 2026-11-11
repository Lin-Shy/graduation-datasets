"""Compute 100% arrival diagnostics with the prebound source-tested rule."""

import argparse
import csv
from decimal import Decimal
from hashlib import file_digest, sha256
import json
from pathlib import Path
from statistics import fmean
import sys

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt


HERE = Path(__file__).resolve().parent
CASE = HERE.parent
sys.path.insert(0, str(CASE / "native_c_20261107"))
from audit_arrival_reference import first_arrival_ms
from review_collected import trace


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def reference_rows(binding):
    measured, published = {}, {}
    missing = []
    for row in csv_rows(CASE / "reference_comparison.csv"):
        gauge = row["gauge"]
        trial = int(row["trial"])
        if row["experimental_first_arrival_ms"]:
            measured[trial, gauge] = float(row["experimental_first_arrival_ms"])
        else:
            missing.append([trial, gauge])
        value = float(row["viper_first_arrival_ms"])
        assert published.setdefault(("same scale", gauge), value) == value
    assert missing == binding["source_missing_experimental_rows"]
    assert set(published) == {("same scale", gauge) for gauge in binding["required_gauges"]}
    recovered = csv_rows(CASE / "arrival_reference_audit.csv")
    assert len(recovered) == 16
    assert {(int(row["trial"]), row["gauge"]): float(row["published_arrival_ms"])
            for row in recovered if row["published_arrival_ms"] and row["within_source_tolerance"] == "True"} == measured
    return {"experiment": measured, "published_Viper": published}


def load_predictions(case, binding, baseline):
    job = case.name.removeprefix("job-")
    receipt = read(case / "collection_receipt.json")
    existing = read(case / "independent_recalculation.json")
    spec = read(case / "evidence/specification.json")
    archive_sha = receipt["archive"]["sha256"]
    assert receipt["all_original_archive_members_verified"] and receipt["scheduler_job_id"] == job == existing["job_id"]
    assert sha(case / "scale100-terminal.tar.gz") == archive_sha == existing["archive_sha256"]
    assert existing["task_completion_pass"]
    assert spec["comparison"]["required_sensors"] == binding["required_gauges"]
    assert spec["comparison"]["window_s"] == binding["required_native_window_s"]
    assert spec["comparison"]["pressure_baseline_Pa"] == baseline
    predictions = {}
    for gauge, gate in binding["fixed_gate_end_ms"].items():
        assert 1000 * Decimal(str(spec["comparison"]["peak_gate_end_s"][gauge])) == Decimal(str(gate))
        files = list((case / f"evidence/run-case/postProcessing/{gauge}").glob("*/p"))
        assert len(files) == 1
        trace_sha = sha(files[0])
        assert trace_sha == existing["gauges"][gauge]["trace_sha256"]
        history = trace(files[0], Decimal(str(baseline)))
        assert history[0][0] == 0 and history[-1][0] >= Decimal("0.005")
        assert len(history) == existing["gauges"][gauge]["sample_count"]
        signal = [(float(time * 1000), float(pressure)) for time, pressure in history]
        predictions[gauge] = {
            "arrival_ms": first_arrival_ms(signal, gate),
            "samples": len(history),
            "trace_sha256": trace_sha,
        }
    return archive_sha, predictions


def chart(binding, rows, attempts, output):
    fig, grid = plt.subplots(1, len(attempts), figsize=(5 * len(attempts), 4.6), layout="constrained",
                            sharey=True, squeeze=False)
    axes = grid[0]
    for axis, (job, attempt) in zip(axes, attempts.items(), strict=True):
        for position, gauge in enumerate(binding["required_gauges"]):
            refs = [r for r in rows if r["job_id"] == job and r["gauge"] == gauge]
            measured = [r["reference_arrival_ms"] for r in refs if r["group"] == "experiment"]
            published, = [r["reference_arrival_ms"] for r in refs if r["group"] == "published_Viper"]
            native = attempt["gauges"][gauge]["arrival_ms"]
            axis.scatter(measured, [position + .10] * len(measured), marker="|", s=165,
                         color="#166d86", label="Experiment" if position == 0 else None)
            axis.scatter(published, position - .10, marker="D", s=36, color="#8a62ad",
                         label="Viper" if position == 0 else None)
            if native is not None:
                axis.scatter(native, position, marker="x", s=56, color="#b8531d",
                             label="blastFoam" if position == 0 else None)
            else:
                axis.text(binding["fixed_gate_end_ms"][gauge], position, "unresolved",
                          ha="left", va="center", color="#b8531d", fontsize=8)
        axis.set(title=f'{binding["transport_mesh_mm"][job]} mm mesh · job {job}',
                 xlabel="First arrival after detonation (ms)", xlim=(.22, 2.15),
                 yticks=range(4), yticklabels=binding["required_gauges"])
        axis.grid(alpha=.2)
        axis.legend(frameon=False, loc="upper right")
    axes[0].invert_yaxis()
    fig.savefig(output / "arrival_comparison.png", dpi=150)
    plt.close(fig)


def source_partition_contract(case, binding):
    """Confirm that the terminal evidence is the job and input already reviewed in flight."""
    supplement = CASE / "source_partition_20261108"
    preflight = read(supplement / "preflight_verified.json")
    reference = supplement / "first_B3_gate_20261108"
    prefix = read(reference / "summary.json")
    arrival_path = supplement / "arrival_prefix_20261108/summary.json"
    arrivals = read(arrival_path)
    job = case.name.removeprefix("job-")
    assert job == preflight["job_id"] == prefix["job_id"] == "8958868"
    assert preflight["mesh_OK"] and preflight["fixed_full_reference_denominators"] == {
        "experimental_repeats": binding["fixed_reference_groups"]["experiment"],
        "published_viper": binding["fixed_reference_groups"]["published_Viper"],
    }
    assert arrivals["source_summary_sha256"] == sha(reference / "summary.json")
    assert arrivals["fixed_binding_sha256"] == sha(HERE / "binding.json")
    assert not arrivals["final_arrival_score_available"]
    spec = case / "evidence/specification.json"
    assert sha(spec) == preflight["sha256"]["specification.json"]
    assert read(spec)["mesh"]["cells"] == preflight["cells"]
    assert sha(case / "evidence/refinement_binding.json") == (
        "1b51a4ad68ba478629028bc10d1d104e46bb62bbd85dee200f14dc76ec15cd4b")
    traces = {}
    for gauge in binding["required_gauges"]:
        raw = (reference / f"{gauge}-native-prefix.txt").read_bytes()
        whole_lines = raw[:raw.rfind(b"\n") + 1]
        expected = prefix["gauges"][gauge]["prefix_sha256"]
        assert sha256(whole_lines).hexdigest() == expected
        terminal, = (case / "evidence/run-case/postProcessing" / gauge).glob("*/p")
        with terminal.open("rb") as stream:
            assert stream.read(len(whole_lines)) == whole_lines
        traces[gauge] = expected
    return {"in_flight_summary_sha256": sha(arrival_path), "prefix_sha256": traces,
            "in_flight_gauges": arrivals["attempts"][job]["gauges"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--include-7mm", action="store_true")
    modes.add_argument("--source-partition", action="store_true")
    args = parser.parse_args()
    binding_path = HERE / "binding.json"
    binding = read(binding_path)
    jobs = list(binding["complete_jobs_to_report"])
    output = HERE
    continuity = None
    if args.include_7mm:
        job = "8953046"
        output = CASE / f"job-{job}/arrival"
        conditions = read(output.parent / "evidence/sources/conditions.json")
        refinement = read(output.parent / "evidence/refinement_binding.json")
        assert conditions["numerics"]["transport_target_step_m_100_pct"] == refinement["transport_target_step_m"]["current"] == .007
        binding["transport_mesh_mm"][job] = 7
        jobs.append(job)
    elif args.source_partition:
        job = "8958868"
        output = CASE / f"job-{job}/arrival"
        continuity = source_partition_contract(output.parent, binding)
        binding["transport_mesh_mm"][job] = 7
        jobs = [job]
    for path, expected in binding["source_bindings"].items():
        assert sha(CASE / path) == expected
    conditions = read(CASE / "native_c_20261107/conditions.json")
    baseline = conditions["air"]["p_Pa"]
    source = read(CASE / "native_c_20261107/arrival_reference_audit.json")
    assert source["scales"]["100"]["within_tolerance"] == source["scales"]["100"]["matched_reference_rows"] == 14
    assert not source["source_gate_pass"]
    refs = reference_rows(binding)
    assert {group: len(values) for group, values in refs.items()} == binding["fixed_reference_groups"]
    rows, attempts = [], {}
    for job in jobs:
        archive_sha, predictions = load_predictions(CASE / f"job-{job}", binding, baseline)
        if continuity:
            for gauge, prediction in predictions.items():
                assert prediction["arrival_ms"] == continuity["in_flight_gauges"][gauge]["arrival_ms"]
        available = all(row["arrival_ms"] is not None for row in predictions.values())
        groups = {}
        for group, references in refs.items():
            errors = []
            for (trial, gauge), reference in references.items():
                assert reference > 0
                prediction = predictions[gauge]["arrival_ms"]
                ape = None if prediction is None else 100 * abs(prediction - reference) / reference
                if ape is not None:
                    errors.append(ape)
                rows.append({"job_id": job, "group": group, "trial": trial, "gauge": gauge,
                             "reference_arrival_ms": reference, "simulation_arrival_ms": prediction, "APE_percent": ape})
            groups[group] = {"compared": len(errors), "expected": len(references),
                             "MAPE_percent": fmean(errors) if available else None}
            if args.include_7mm or args.source_partition:
                groups[group].update(APE_at_most_30=sum(ape <= 30 for ape in errors),
                                     APE_at_most_15=sum(ape <= 15 for ape in errors))
        attempts[job] = {"native_task_completion_pass": True, "arrival_comparison_complete": available,
                         "gauges": predictions, "groups": groups, "archive_sha256": archive_sha}
    output.mkdir(exist_ok=True)
    with (output / "comparison.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    chart(binding, rows, attempts, output)
    result = {"binding_sha256": sha(binding_path), "reference_group_sizes": binding["fixed_reference_groups"],
              "attempts": attempts}
    if continuity:
        result["verified_prefix_continuity"] = continuity
    (output / "independent_recalculation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({job: attempt["groups"] for job, attempt in attempts.items()}, indent=2))


if __name__ == "__main__":
    main()
