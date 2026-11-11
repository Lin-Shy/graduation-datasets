"""Compare identical positive-phase pickoff on the two archived reconstruction variants."""

import io
import json
import tarfile

import numpy as np

from audit import CASE, HERE, TRACE, ape, positive_phase, read, sha


def pressure_record(collection, job):
    receipt = read(collection / "collection_receipt.json")
    raw = (collection / "evidence" / TRACE).read_bytes()
    archive = collection / "native-evidence.tar"
    assert receipt["job_id"] == job and sha(archive.read_bytes()) == receipt["original_archive_sha256"]
    with tarfile.open(archive) as tar:
        assert tar.extractfile(TRACE).read() == raw
    return np.loadtxt(io.BytesIO(raw), unpack=True), sha(raw)


def main():
    plan = read(HERE / "protocol.json")
    reviewed = read(HERE / "impulse_review.json")
    old_job = CASE / "job-8952323/collection-2kzubwzy"
    new_job = CASE / "job-8953576/collection-pyxz4uv3"
    old, old_sha = pressure_record(old_job, "8952323")
    new, new_sha = pressure_record(new_job, "8953576")
    assert new_sha == reviewed["trace_sha256"]
    end = min(old[0, -1], new[0, -1], plan["native_window_s"][1])
    assert end < plan["native_window_s"][1]
    metrics = []
    for index, row in enumerate(reviewed["rows"], 1):
        sample = {"radius_m": row["radius_m"], "experiment_Pa_s": row["experiment_Pa_s"]}
        for label, wave in (("upwind", old), ("vanLeer", new)):
            assert wave[index, 0] == plan["ambient_pressure_Pa"]
            t = wave[0]
            p = wave[index] - plan["ambient_pressure_Pa"]
            inside = t <= end
            peak_t = t[inside][np.argmax(p[inside])]
            phase = positive_phase(t, p, plan["seed_kPa"] * 1000, peak_t, end)
            sample[label] = None if phase is None else {
                "first_lobe_s": phase[:2], "duration_ms": (phase[1] - phase[0]) * 1000,
                "impulse_Pa_s": phase[2], "experimental_APE_pct": ape(phase[2], row["experiment_Pa_s"]),
            }
        metrics.append(sample)
    result = {"scope": "Closed first positive phase within shared archived prefix; baseline delivery incomplete",
              "common_end_s": end, "trace_sha256": {"upwind": old_sha, "vanLeer": new_sha}, "pointwise": metrics}
    for name in ("upwind", "vanLeer"):
        error = [r[name]["experimental_APE_pct"] for r in metrics if r[name] is not None]
        result[name + "_experimental_MAPE_pct"] = sum(error) / len(error) if len(error) == len(metrics) else None
    (HERE / "reconstruction_impulse_diagnostic.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
