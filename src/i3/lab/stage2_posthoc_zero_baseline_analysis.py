"""Read-only post-hoc proper score comparator on archived exact-CI events.

No World, run_life, genotype, motor, learning, or new-source generation.
The zero-change baseline was selected AFTER the original prequential
outcomes were known: descriptive diagnostic ONLY, not prospective science.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from math import fsum, isfinite
from pathlib import Path

SCHEMA = "i3-stage2.1-posthoc-zero-change-paired-score/v1"
DATASET = (Path(__file__).resolve().parents[1] / "docs" / "studies"
           / "stage2-replay-gate-selected-design"
           / "STAGE2_POSTHOC_ZERO_BASELINE_SOURCE_EXTRACT_2026-11-12.json")
SOURCE_HEAD = "7f32f33172c4773bf4c5630ff945f0b1df6dbb8e"
SOURCE_DIGEST = "86f7db8524783a249ec2e1363c3f149f94af1eed1dc09ba32724a9c9bade8373"
GRID = (("dev-open-field", 840061), ("dev-open-field", 840062),
        ("dev-failing-well", 840061), ("dev-failing-well", 840062))
N_PER_UNIT = 80
EPS = 1e-12


def _canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _vector(values, label):
    if type(values) is not list or len(values) != 5:
        raise ValueError(label + " must be exactly five body channels")
    if any(type(x) not in (float, int) or not isfinite(x) for x in values):
        raise ValueError(label + " contains nonfinite or nonnumeric body data")
    return values


def paired_score(forecast, actual):
    """One exact same-outcome, equal-target comparison, no state update."""
    p = _vector(forecast, "preoutcome forecast")
    y = _vector(actual, "factual post-paid-learning delta")
    native = fsum((x-z)**2 for x, z in zip(y, p)) / 5.0
    zero = fsum(x*x for x in y) / 5.0
    delta = zero-native
    if not all(isfinite(v) and v >= 0 for v in (native, zero)):
        raise ValueError("invalid proper squared-loss arithmetic")
    return native, zero, delta


def _aggregate(events):
    native = fsum(e["native_squared_loss"] for e in events)
    zero = fsum(e["zero_squared_loss"] for e in events)
    n = len(events)
    return {
        "events": n,
        "mean_native_squared_loss": native/n if n else None,
        "mean_zero_change_squared_loss": zero/n if n else None,
        "mean_paired_gain_zero_minus_native": (zero-native)/n if n else None,
        "native_better_event_count": sum(e["paired_gain"] > EPS for e in events),
        "zero_better_event_count": sum(e["paired_gain"] < -EPS for e in events),
        "tie_event_count": sum(abs(e["paired_gain"]) <= EPS for e in events),
    }


def reduce_dataset(source):
    """A fail-closed reduction of the archived full 320-event record."""
    if (type(source) is not dict or
            source.get("schema") !=
            "i3-stage2.1-posthoc-zero-change-forecast-source-extract/v1" or
            source.get("scientific_lives") != 0):
        raise ValueError("unrecognized read-only source extract")
    ref = source.get("source_ref")
    if (type(ref) is not dict or ref.get("head_sha") != SOURCE_HEAD
            or ref.get("original_aggregate_sha256") != SOURCE_DIGEST
            or ref.get("run_id") != 43209682555
            or ref.get("job_id") != 131153802748
            or ref.get("kind") != "EXTRACT_FROM_CI_RECEIPT_NOT_INDEPENDENT"):
        raise ValueError("source not pinned to exact original CI receipt")
    worlds = source.get("worlds")
    if type(worlds) is not list or len(worlds) != len(GRID):
        raise ValueError("incorrect original four-unit denominator")
    rows, combined = [], []
    for original, pair in zip(worlds, GRID):
        if (type(original) is not dict or
                (original.get("world"), original.get("seed")) != pair):
            raise ValueError("unregistered original world or seed")
        entries = original.get("events")
        if type(entries) is not list or len(entries) != N_PER_UNIT:
            raise ValueError("missing or duplicated original assigned event")
        scored = []
        for step, e in enumerate(entries, 1):
            if (type(e) is not dict or e.get("step") != step
                    or type(e.get("action")) is not str
                    or not e["action"]
                    or type(e.get("source_count_exact")) not in (int, float)
                    or not isfinite(e["source_count_exact"])
                    or e["source_count_exact"] < 0
                    or e.get("learning_status") != "PAID_LEARNING"
                    or e.get("terminal") is not False):
                raise ValueError("missing, invalid or censored fixed event")
            seal = e.get("preoutcome_forecast_sha256")
            if (type(seal) is not str or len(seal) != 64
                    or any(ch not in "0123456789abcdef" for ch in seal)):
                raise ValueError("original preoutcome forecast seal missing")
            a, b, gain = paired_score(e.get("forecast_delta"),
                                      e.get("actual_delta"))
            scored.append({
                "step": step, "n_exact": e["source_count_exact"],
                "native_squared_loss": a, "zero_squared_loss": b,
                "paired_gain": gain,
            })
        by_count = {}
        for k, want_seen in (("unseen_exact", False), ("seen_exact", True)):
            by_count[k] = _aggregate([v for v in scored
                                      if (v["n_exact"] > 0) == want_seen])
        rows.append({
            "world": pair[0], "seed": pair[1],
            **_aggregate(scored),
            "source_count_bins": by_count,
        })
        combined.extend(scored)
    if len(combined) != 320:
        raise RuntimeError("original assigned event count changed")
    unit_differences = [r["mean_paired_gain_zero_minus_native"] for r in rows]
    summary = _aggregate(combined)
    return {
        "schema": SCHEMA,
        "status": "POSTHOC_PAIRED_SCORE_INTEGRITY_PASS",
        "source_sha256": SOURCE_DIGEST,
        "source_ci_run": 43209682555,
        "comparator_selection_timing": "POSTHOC_AFTER_ORIGINAL_OUTCOMES",
        "all_assigned_technical_units": 4,
        "all_assigned_actual_steps": 320,
        "original_engineering_lives_rerun": 0,
        "worlds_opened_for_this_reanalysis": 0,
        "scientific_lives": 0,
        "unit_mean_gain_positive": sum(v > EPS for v in unit_differences),
        "unit_mean_gain_negative": sum(v < -EPS for v in unit_differences),
        "unit_mean_gain_tied": sum(abs(v) <= EPS for v in unit_differences),
        "unit_heterogeneity_prevents_generalization": True,
        "within_trajectory_steps_are_not_independent_units": True,
        "baseline_was_not_equal_work_or_action_mediation_control": True,
        "scientific_verdict": "NOT_ISSUED",
        "rows": rows,
        "all_events": summary,
        "canonical_source_extract_sha256": _canonical_hash(source),
    }


def audit():
    return reduce_dataset(json.loads(DATASET.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print("I3_STAGE2_POSTHOC_ZERO_BASELINE="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":")))
