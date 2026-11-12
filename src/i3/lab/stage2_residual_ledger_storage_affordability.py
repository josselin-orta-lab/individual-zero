"""No-World, retrospective modeled affordability of a retained error ledger.

Source-precommitted design: STAGE2_RESIDUAL_LEDGER_STORAGE_AFFORDABILITY_PREFLIGHT.
The original individual never paid this hypothetical extra storage work. All
World/body outcomes are immutable original engineering evidence, not a new life.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha1, sha256
import json
from math import isclose
from pathlib import Path

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork, validate_body
from .stage2_posthoc_zero_baseline_analysis import (
    DATASET, GRID, N_PER_UNIT, SOURCE_DIGEST, SOURCE_HEAD, paired_score)
from .stage2_archived_residual_readout_paid import (
    SIDECAR as DECISION_BILLS, reduce_sources)

SCHEMA = "i3-stage2.1-residual-ledger-storage-model-affordability/v1"
POST_BODY = DATASET.parent / "STAGE2_RESIDUAL_LEDGER_POST_PAID_BODY_SIDECAR_2026-11-12.json"
POST_BODY_SCHEMA = "i3-stage2.1-archived-post-paid-learning-body-sidecar/v1"
POST_BODY_BLOB_SHA1 = "48ccdfa0a28db7ae230049ad24b68bfa6bff5d61"
WORK = CognitiveWork(cycles=2, memory_items=12)
MODES = ("RETAIN", "PAID_DISCARD")


def _sha(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _attempt(*, body, action, prediction, actual, mode, records):
    """Do not access original error or copy a record until work is funded."""
    if type(mode) is not str or mode not in MODES:
        raise ValueError("invalid source-frozen retention control")
    if type(records) is not list:
        raise TypeError("laboratory records must be a list")
    allowance = CognitiveBudget(validate_body(body), BodyLaws())
    before = allowance.work
    if not allowance.try_spend(WORK):
        if allowance.work != before:
            raise RuntimeError("denied write incurred phantom work")
        return {
            "status": "DENIED_BEFORE_RESIDUAL_READ",
            "mode": mode, "computed": 0, "appended": 0, "retained": 0,
            "modeled_work": asdict(allowance.work),
            "records_after": len(records),
            "computed_error": None,
        }
    if type(action) is not str or not action:
        raise ValueError("native factual action label required")
    # Both comparator arms actually run this residual calculation,
    # including the arm that discards its newly appended record.
    error, _, _ = paired_score(prediction, actual)
    records.append((action, error))
    appended = 1
    if mode == "PAID_DISCARD":
        discarded = records.pop()
        if discarded != (action, error):
            raise RuntimeError("wrong just-appended laboratory record erased")
    return {
        "status": "MODEL_AUTHORIZED_RECORD",
        "mode": mode,
        "computed": 1, "appended": appended,
        "retained": 1 if mode == "RETAIN" else 0,
        "modeled_work": asdict(allowance.work),
        "records_after": len(records),
        "computed_error": error,
    }


def reduce_sources_with_storage(source, bills, post):
    # Check full original 320-event derivative and paid-decision custody,
    # including the existing, pinned prior source sidecar.
    verified = reduce_sources(source, bills)
    if verified["assigned_events"] != 320:
        raise ValueError("original 320-event sequence changed")
    if (type(post) is not dict or post.get("schema") != POST_BODY_SCHEMA
            or post.get("source_kind") !=
               "HISTORICAL_UNPAID_LAB_DERIVATIVE_NOT_NEW_WORLD"
            or post.get("source_ci_run") != 43209682555
            or post.get("source_ci_job") != 131153802748
            or post.get("source_head") != SOURCE_HEAD
            or post.get("source_aggregate_sha256") != SOURCE_DIGEST
            or post.get("derivative_source_sha256") !=
               verified["derivative_source_sha256"]):
        raise ValueError("unrecognized postpaid body source")
    if type(post.get("worlds")) is not list or len(post["worlds"]) != 4:
        raise ValueError("incomplete original postpaid population")
    rows = []
    summary = {"events": 0, "arm_attempts": 0, "funded": 0, "denied": 0,
               "computed_each_arm": 0, "initial_append_each_arm": 0,
               "retained_final": 0, "four_empty_initial_ledgers": 0}
    for original, bills_unit, post_unit, pair in zip(
            source["worlds"], bills["worlds"], post["worlds"], GRID):
        if ((original["world"], original["seed"]) != pair
                or (bills_unit["world"], bills_unit["seed"]) != pair
                or (post_unit.get("world"), post_unit.get("seed")) != pair):
            raise ValueError("misaligned engineering unit")
        b_events = bills_unit["events"]
        p_events = post_unit.get("events")
        if type(p_events) is not list or len(p_events) != N_PER_UNIT:
            raise ValueError("incomplete 80-step postpaid body sidecar")
        retained = []
        discarded = []
        summary["four_empty_initial_ledgers"] += int(
            len(retained) == 0 and len(discarded) == 0)
        for old, bill, current in zip(original["events"], b_events, p_events):
            if (type(current) is not dict
                    or current.get("step") != old["step"]
                    or current.get("preoutcome_forecast_sha256") !=
                       old["preoutcome_forecast_sha256"]):
                raise ValueError("postpaid source seal/step mismatch")
            if bill.get("step") != old["step"]:
                raise ValueError("decision bill no longer matches original")
            body = validate_body(current.get("post_paid_learning_body"))
            before = validate_body(bill.get("body_before"))
            delta = old["actual_delta"]
            if any(not isclose(b-a, d, rel_tol=0, abs_tol=1e-10)
                   for a,b,d in zip(before,body,delta)):
                raise ValueError("postpaid body is not the original factual delta")
            left = _attempt(
                body=body, action=old["action"],
                prediction=old["forecast_delta"], actual=delta,
                mode="RETAIN", records=retained)
            right = _attempt(
                body=body, action=old["action"],
                prediction=old["forecast_delta"], actual=delta,
                mode="PAID_DISCARD", records=discarded)
            for k in ("status","computed","appended","modeled_work",
                      "computed_error"):
                if left[k] != right[k]:
                    raise RuntimeError("model-cost or host-operator asymmetry")
            admitted = left["status"] == "MODEL_AUTHORIZED_RECORD"
            summary["funded" if admitted else "denied"] += 1
            summary["computed_each_arm"] += left["computed"]
            summary["initial_append_each_arm"] += left["appended"]
            summary["events"] += 1
            summary["arm_attempts"] += 2
            if (len(discarded) or len(retained) > N_PER_UNIT
                    or left["records_after"] != len(retained)
                    or right["records_after"] != 0):
                raise RuntimeError("laboratory record retention defect")
            rows.append({
                "world":pair[0], "seed":pair[1], "step":old["step"],
                "status":left["status"], "modeled_work":left["modeled_work"],
                "pre_existing_source_count":len(retained)-int(admitted),
                "post_model_storage_count":len(retained),
                "residual_computations_per_arm":left["computed"],
                "record_append_calls_per_arm":left["appended"],
                "historical_post_paid_learning_body":body,
            })
        summary["retained_final"] += len(retained)
    if (summary["events"] != 320 or summary["arm_attempts"] != 640
            or summary["funded"]+summary["denied"] != 320
            or summary["four_empty_initial_ledgers"] != 4
            or summary["computed_each_arm"] != summary["funded"]
            or summary["initial_append_each_arm"] != summary["funded"]):
        raise RuntimeError("predeclared denominator or accounting mismatch")
    return {
        "schema": SCHEMA,
        "status": "RESIDUAL_LEDGER_STORAGE_MODEL_AFFORDABILITY_PASS",
        "scientific_verdict": "NOT_ISSUED",
        "historical_source_original_sha": SOURCE_DIGEST,
        "postpaid_source_blob_sha1": POST_BODY_BLOB_SHA1,
        "model_tariff_provisional": True,
        "native_World_step_executed_here": False,
        "new_actual_World_debit_executed_here": False,
        "model_storage_not_originally_paid_by_individual": True,
        "host_CPU_joules_calibrated": False,
        "scientific_lives": 0, "worlds_opened": 0,
        **summary,
        "structural_digest": _sha(rows),
        "rows": rows,
    }


def audit():
    # Pin the raw historical derivative to an immutable Git content hash.
    raw = POST_BODY.read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if blob != POST_BODY_BLOB_SHA1:
        raise ValueError("original postpaid body sidecar bytes changed")
    return reduce_sources_with_storage(
        json.loads(DATASET.read_text(encoding="utf-8")),
        json.loads(DECISION_BILLS.read_text(encoding="utf-8")),
        json.loads(raw.decode("utf-8")))


if __name__ == "__main__":
    a = audit()
    print("I3_STAGE2_RESIDUAL_STORAGE=" + json.dumps(
        {k:v for k,v in a.items() if k!="rows"}, sort_keys=True))
