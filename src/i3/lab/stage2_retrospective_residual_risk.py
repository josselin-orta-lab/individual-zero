"""Past-only retrospective action-conditional prediction-error diagnostic.

No model, policy, world or learner is changed. This compares two observer
risk estimates against the *already archived* outcome errors of native
EffectsModel forecasts. It is NOT a prospective scientific experiment.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from math import fsum, isfinite

from .stage2_posthoc_zero_baseline_analysis import (
    DATASET, GRID, N_PER_UNIT, SOURCE_HEAD, SOURCE_DIGEST, _canonical_hash,
    reduce_dataset, paired_score,
)

SCHEMA = "i3-stage2.1-retrospective-online-forecast-residual-risk/v1"
DERIVATIVE_SHA = "09c09804f5100edd5664d649cd5f3c0234dd4c182e1c89d8e2761b34a0b9a5b4"


def risk_before_outcome(pooled_count, pooled_sum, prior_for_action):
    """Frozen G and A from past z only; never accept current event target."""
    if type(pooled_count) is not int or pooled_count < 0:
        raise ValueError("invalid previous-event count")
    if not isfinite(pooled_sum) or pooled_sum < 0:
        raise ValueError("invalid previous-event total error")
    count, subtotal = prior_for_action
    if (type(count) is not int or count < 0
            or count > pooled_count
            or not isfinite(subtotal) or subtotal < 0):
        raise ValueError("invalid past action-only record")
    g = pooled_sum / pooled_count if pooled_count else 0.0
    a = (subtotal + g) / (count + 1)
    return g, a


def _means(events):
    n = len(events)
    vals = {
        key: fsum(e[key] for e in events) / n if n else None
        for key in ("pooled_squared_risk_loss", "action_squared_risk_loss",
                    "pooled_absolute_risk_loss", "action_absolute_risk_loss")
    }
    if n:
        vals["squared_gain_control_minus_action"] = (
            vals["pooled_squared_risk_loss"] -
            vals["action_squared_risk_loss"])
        vals["absolute_gain_control_minus_action"] = (
            vals["pooled_absolute_risk_loss"] -
            vals["action_absolute_risk_loss"])
    else:
        vals["squared_gain_control_minus_action"] = None
        vals["absolute_gain_control_minus_action"] = None
    vals["n"] = n
    vals["prior_action_available"] = sum(e["prior_action_count"] > 0
                                          for e in events)
    vals["no_prior_action"] = n - vals["prior_action_available"]
    return vals


def reduce_dataset_risk(source):
    # Reuse earlier fail-closed 320-event source verification.
    base = reduce_dataset(source)
    if base["canonical_source_extract_sha256"] != DERIVATIVE_SHA:
        raise ValueError("archived derivative source has changed")
    rows = []
    all_events = []
    for unit, pair in zip(source["worlds"], GRID):
        pool_count, pool_sum = 0, 0.0
        by_action = defaultdict(lambda: [0, 0.0])
        events = []
        for original in unit["events"]:
            action = original["action"]
            action_count, action_sum = by_action[action]
            g, a = risk_before_outcome(
                pool_count, pool_sum, (action_count, action_sum))
            # Only here read the archived factual actual delta.
            native_loss, _, _ = paired_score(
                original["forecast_delta"], original["actual_delta"])
            z = native_loss
            event = {
                "step": original["step"],
                "action": action,
                "prior_action_count": action_count,
                "prior_total_count": pool_count,
                "actual_native_prediction_squared_error": z,
                "pooled_risk_before_actual": g,
                "action_risk_before_actual": a,
                "pooled_squared_risk_loss": (z-g)**2,
                "action_squared_risk_loss": (z-a)**2,
                "pooled_absolute_risk_loss": abs(z-g),
                "action_absolute_risk_loss": abs(z-a),
            }
            if any(type(v) is float and not isfinite(v)
                   for v in event.values()):
                raise RuntimeError("nonfinite online risk result")
            events.append(event)
            pool_count += 1
            pool_sum += z
            by_action[action][0] += 1
            by_action[action][1] += z
        if len(events) != N_PER_UNIT or pool_count != N_PER_UNIT:
            raise RuntimeError("not all original events were scored")
        all_events.extend(events)
        rows.append({"world": pair[0], "seed": pair[1], **_means(events),
                     "events": events})
    if len(all_events) != 320:
        raise RuntimeError("original 320-event denominator changed")
    summaries = [{k:v for k,v in row.items() if k!="events"} for row in rows]
    sq_good = sum(r["squared_gain_control_minus_action"] > 0 for r in rows)
    abs_good = sum(r["absolute_gain_control_minus_action"] > 0 for r in rows)
    summary = {
        "schema": SCHEMA,
        "status": "RETROSPECTIVE_RISK_EVALUATION_PASS",
        "source_ci_sha256": SOURCE_DIGEST,
        "source_extract_sha256": DERIVATIVE_SHA,
        "original_source_head": SOURCE_HEAD,
        "retrospective_not_independent_validation": True,
        "past_only_online_estimators": True,
        "method": "one_pooled_mean_pseudorecord_for_action_error_risk",
        "action_is_already_chosen_no_optional_funding": True,
        "technical_units": len(rows),
        "all_assigned_events": len(all_events),
        "worlds_opened": 0, "scientific_lives": 0,
        "unit_positive_squared_risk": sq_good,
        "unit_positive_absolute_risk": abs_good,
        "merit_gate_met": sq_good >= 3 and abs_good >= 3,
        "scientific_verdict": "NOT_ISSUED",
        "aggregate": _means(all_events),
        "rows": summaries,
    }
    summary["deterministic_digest"] = _canonical_hash(summary)
    return summary


def audit():
    return reduce_dataset_risk(json.loads(DATASET.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print("I3_STAGE2_RETROSPECTIVE_RESIDUAL_RISK="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":")))
