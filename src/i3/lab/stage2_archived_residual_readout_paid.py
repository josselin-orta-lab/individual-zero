"""No-World modeled-paid laboratory readout of earlier personal forecast errors.

Pre-registered engineering scope: STAGE2_ARCHIVED_RESIDUAL_READOUT_PAID_PREFLIGHT.
This observer cannot deliver information to a living Mind or influence action.
Model allowances are NOT actual World payments or physical CPU joules.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha1, sha256
import json
from math import fsum, isfinite
from pathlib import Path

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork,
    cognitive_cost, validate_body)
from .stage2_posthoc_zero_baseline_analysis import (
    DATASET, GRID, N_PER_UNIT, SOURCE_DIGEST, SOURCE_HEAD, paired_score,
    reduce_dataset)
from .stage2_retrospective_residual_risk import DERIVATIVE_SHA

SCHEMA = "i3-stage2.1-archived-residual-model-paid-readout/v1"
SIDECAR = (DATASET.parent /
           "STAGE2_ARCHIVED_RESIDUAL_READOUT_DECISION_BILLS_2026-11-12.json")
SIDECAR_SCHEMA = "i3-stage2.1-archived-native-decision-body-receipts-sidecar/v1"
SIDECAR_GIT_BLOB_SHA1 = "678c9fbe6d74189f3210734de782e421644c6a95"
MODES = ("VISIBLE", "PAID_DISCARD")


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _paid_receipt_and_body(body, bill):
    """Reconstruct post-original-decision body, never a second World debit."""
    start = validate_body(body)
    if type(bill) is not dict or set(bill) != {"energy", "vigilance"}:
        raise ValueError("missing original native decision bill")
    out = list(start)
    for channel, label in ((0, "energy"), (4, "vigilance")):
        r = bill[label]
        if (type(r) is not dict or set(r) != {"requested", "paid", "unpaid"}
                or any(type(r[k]) not in (float, int) or not isfinite(r[k])
                       for k in r)
                or r["requested"] != r["paid"] or r["unpaid"] != 0
                or r["paid"] < 0 or r["paid"] > start[channel]):
            raise ValueError("forged or unpaid native decision receipt")
        out[channel] -= r["paid"]
    return validate_body(tuple(out))


def _read_prior(prior, action):
    """Actual full scan; caller must already have an admitted ticket."""
    if type(action) is not str or not action:
        raise ValueError("native action required")
    n = len(prior)
    total = 0.
    selected = 0.
    count = 0
    visits = 0
    for label, error in prior:
        visits += 1
        if type(label) is not str or not label or (type(error) not in
                (int, float) or not isfinite(error) or error < 0):
            raise ValueError("invalid personally experienced error record")
        total += error
        if label == action:
            selected += error
            count += 1
    pooled = total/n if n else 0.
    action_risk = (selected + pooled)/(count+1)
    if visits != n or not isfinite(action_risk):
        raise RuntimeError("unexpected prior scan count")
    return {"pooled_risk": pooled, "action_risk": action_risk,
            "scan_visits": visits, "same_action_count": count}


def _ticket(n):
    if type(n) is not int or not 0 <= n < N_PER_UNIT:
        raise ValueError("outside original bounded history")
    return CognitiveWork(cycles=2, simulated_steps=0,
                         memory_items=2*n+2, replays=0)


def _attempt(previous, *, action, body_after_native_choice, mode):
    """Exact matched computation, even on the discarded mode."""
    if mode not in MODES or type(mode) is not str:
        raise ValueError("unknown visibility control")
    # Nothing here opens, clones or reads a World. No source history
    # is scanned/snapshotted before motor-preserving modeled funding.
    allowed = CognitiveBudget(body_after_native_choice, BodyLaws())
    prior_work = allowed.work
    work = _ticket(len(previous))
    e, v = cognitive_cost(allowed.laws, work)
    if (allowed.remaining[0] < e or allowed.remaining[4] < v or
            (action not in ("dormir", None)
             and allowed.remaining[0]-e < ACTION_COSTS[action])):
        if allowed.work != prior_work:
            raise RuntimeError("denied work charged an allowance")
        return {"status": "DENIED_BEFORE_HISTORY_READ",
                "mode": mode, "scan_visits": 0,
                "actual_optional_readout_executed": False,
                "model_work": asdict(allowed.work),
                "modeled_energy": 0., "modeled_vigilance": 0.,
                "observer_visible_action_risk": None,
                "computed_but_discarded": False, "same_action_count": None}
    if not allowed.try_spend(work):
        raise RuntimeError("model-priced optional work unexpectedly refused")
    # This snapshot and scan are the optional operations: only after grant.
    actual = _read_prior(tuple(previous), action)
    return {"status": "MODEL_AUTHORIZED_READOUT",
            "mode": mode, "scan_visits": actual["scan_visits"],
            "actual_optional_readout_executed": True,
            "model_work": asdict(allowed.work),
            "modeled_energy": e, "modeled_vigilance": v,
            "observer_visible_action_risk": (
                actual["action_risk"] if mode == "VISIBLE" else None),
            "computed_but_discarded": mode == "PAID_DISCARD",
            "same_action_count": actual["same_action_count"],
            "computed_pooled_risk": actual["pooled_risk"],
            # The computed estimate is a laboratory custody receipt,
            # never fed into Mind.decide, options or next action.
            "internal_computed_action_risk": actual["action_risk"]}


def reduce_sources(original, sidecar):
    source = reduce_dataset(original)  # strict original 320-event validator
    if source["canonical_source_extract_sha256"] != DERIVATIVE_SHA:
        raise ValueError("not the frozen original derivative")
    if (type(sidecar) is not dict or sidecar.get("schema") != SIDECAR_SCHEMA
            or sidecar.get("source_ci_run") != 43209682555
            or sidecar.get("source_ci_job") != 131153802748
            or sidecar.get("source_head") != SOURCE_HEAD
            or sidecar.get("source_aggregate_sha256") != SOURCE_DIGEST
            or sidecar.get("derivative_source_sha256") != DERIVATIVE_SHA
            or sidecar.get("kind") !=
               "UNPRICED_LAB_DERIVATIVE_NOT_INDEPENDENT_WITNESS"):
        raise ValueError("unrecognized native-decision source receipts")
    if type(sidecar.get("worlds")) is not list or len(sidecar["worlds"]) != 4:
        raise ValueError("incorrect sidecar original population")
    all_rows = []
    summary = {"assigned_events": 0, "arm_attempts": 0,
               "funded_events": 0, "denied_events": 0,
               "prior_records_scanned_per_arm": 0,
               "zero_history_events": 0}
    for unit, bills, pair in zip(original["worlds"], sidecar["worlds"], GRID):
        if (bills.get("world"), bills.get("seed")) != pair:
            raise ValueError("changed source identity")
        if type(bills.get("events")) is not list or len(bills["events"]) != N_PER_UNIT:
            raise ValueError("missing sidecar assigned receipt")
        prior = []
        counts = {"funded": 0, "denied": 0}
        for original_event, native in zip(unit["events"], bills["events"]):
            if (type(native) is not dict
                    or native.get("step") != original_event["step"]
                    or native.get("preoutcome_forecast_sha256") !=
                       original_event["preoutcome_forecast_sha256"]):
                raise ValueError("sidecar not aligned with original forecast")
            after_decision = _paid_receipt_and_body(
                native.get("body_before"), native.get("world_decision_bill"))
            if type(original_event["action"]) is not str:
                raise ValueError("original native action missing")
            if len(prior) != original_event["step"]-1:
                raise RuntimeError("past history includes future or has gaps")
            action = original_event["action"]
            # Two independent modeled tickets: both perform the same
            # real scan only after their own allowance was granted.
            left = _attempt(prior, action=action,
                            body_after_native_choice=after_decision,
                            mode="VISIBLE")
            right = _attempt(prior, action=action,
                             body_after_native_choice=after_decision,
                             mode="PAID_DISCARD")
            equal = ("status", "scan_visits", "model_work", "modeled_energy",
                     "modeled_vigilance", "actual_optional_readout_executed",
                     "same_action_count")
            if any(left[k] != right[k] for k in equal):
                raise RuntimeError("unequal operator work or modeled payment")
            if left["status"] == "MODEL_AUTHORIZED_READOUT":
                if (left["observer_visible_action_risk"] !=
                        right["internal_computed_action_risk"]
                        or left["internal_computed_action_risk"] !=
                           right["internal_computed_action_risk"]
                        or right["observer_visible_action_risk"] is not None
                        or not right["computed_but_discarded"]):
                    raise RuntimeError("paid-discard did not compute same information")
                summary["funded_events"] += 1
                summary["prior_records_scanned_per_arm"] += len(prior)
                counts["funded"] += 1
            else:
                if (left["scan_visits"] or right["scan_visits"]
                        or left["observer_visible_action_risk"] is not None):
                    raise RuntimeError("read denied without complete stop")
                summary["denied_events"] += 1
                counts["denied"] += 1
            if not prior:
                summary["zero_history_events"] += 1
            all_rows.append({
                "world": pair[0], "seed": pair[1],
                "step": original_event["step"], "action": action,
                "prior_records": len(prior),
                "original_post_native_choice_body": after_decision,
                "visible": left, "discard": right,
            })
            # The outcome is read only after both risk readouts for
            # the current step have completed. A past-only error ledger.
            z, _, _ = paired_score(original_event["forecast_delta"],
                                    original_event["actual_delta"])
            prior.append((action, z))
            summary["assigned_events"] += 1
            summary["arm_attempts"] += 2
        if counts["funded"]+counts["denied"] != N_PER_UNIT:
            raise RuntimeError("incomplete engineering unit")
    if summary["assigned_events"] != 320 or summary["arm_attempts"] != 640:
        raise RuntimeError("incomplete frozen denominator")
    concise = [{
        "world": x["world"], "seed": x["seed"], "step": x["step"],
        "action": x["action"], "prior_records": x["prior_records"],
        "status": x["visible"]["status"],
        "scan_visits": x["visible"]["scan_visits"],
        "work": x["visible"]["model_work"],
        "visible_risk": x["visible"]["observer_visible_action_risk"],
        "computed_discarded_risk": x["discard"].get(
            "internal_computed_action_risk"),
    } for x in all_rows]
    return {
        "schema": SCHEMA,
        "status": "ARCHIVED_RESIDUAL_MODEL_PAID_READOUT_PASS",
        "original_source_sha256": SOURCE_DIGEST,
        "derivative_source_sha256": DERIVATIVE_SHA,
        "sidecar_checksum": _hash(sidecar),
        "main_source_read_only": True,
        "optional_source_reads_happen_only_after_model_admission": True,
        "native_Mind_not_modified_or_called": True,
        "worlds_opened": 0, "scientific_lives": 0,
        "actual_native_World_debit": False,
        "full_host_CPU_price_calibrated": False,
        "no_action_mediation_claim": True,
        "scientific_verdict": "NOT_ISSUED",
        **summary,
        "deterministic_aggregate_sha256": _hash(concise),
        "examples": [x for x in concise if x["step"] in (1, 2, 80)],
        "full_rows": concise,
    }


def audit():
    # Pin the complete sidecar bytes to the exact Git blob archived before
    # this readout was implemented, not just labels and event seals.
    raw = SIDECAR.read_bytes()
    git_blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if git_blob != SIDECAR_GIT_BLOB_SHA1:
        raise ValueError("native decision sidecar Git blob changed")
    return reduce_sources(
        json.loads(DATASET.read_text(encoding="utf-8")),
        json.loads(raw.decode("utf-8")))


if __name__ == "__main__":
    print("I3_ARCHIVED_RESIDUAL_MODEL_PAID_READOUT="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":")))
