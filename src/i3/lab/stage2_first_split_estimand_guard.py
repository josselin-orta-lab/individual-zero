"""Pure first-split causal-estimand guard; no World, Mind, or life exposure.

Checks the internal consistency of supplied model receipts, NOT provenance
authenticity, experimental independence, or a scientific value-of-thinking GO.
The older four-pair input has ALREADY been inspected; reading it is post-hoc.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite

from ..modules.body import BodyLaws, CognitiveWork, cognitive_cost
from . import stage2_first_native_cost_split_decomposition as ORIGINAL

SCHEMA = "i3-stage2.1-first-split-estimand-guard/v1"
NO_EXPOSURE = ("NO_INFORMATION", "DENIED", "TERMINAL_BEFORE_OPPORTUNITY",
               "CENSORED_BEFORE_OPPORTUNITY")
EXPOSURES = ("EXPOSED",) + NO_EXPOSURE
MOTORS = ("se_deplacer", "collecter", "manger", "boire", "dormir", "attendre")
WORK_FIELDS = {"cycles", "memory_items", "simulated_steps", "replays"}
TOL = 1e-10


def _body(x):
    if type(x) is not list or len(x) != 5 or any(
            type(v) not in (int, float) or not isfinite(v) or not 0 <= v <= 100
            for v in x):
        raise ValueError("actual five-channel body receipt required")
    return tuple(float(v) for v in x)


def _work(x):
    if type(x) is not dict or set(x) != WORK_FIELDS:
        raise ValueError("complete native decision CognitiveWork required")
    return CognitiveWork(**x)


def _motor(x):
    if (type(x) is not list or len(x) != 2 or x[0] not in MOTORS
            or (x[0] != "se_deplacer" and x[1] is not None)
            or (x[0] == "se_deplacer" and x[1] not in ("N", "S", "E", "W"))):
        raise ValueError("actual admissible native motor receipt required")
    return tuple(x)


def classify_receipt(receipt):
    """Classify exactly the first deviation after an equal paid source read.

    BODY parity is required at the *first same-motor cost split*, not after
    later downstream life evolution. Downstream endogenous cost differences
    are preserved as natural total-effect mediators.
    """
    if type(receipt) is not dict or set(receipt) != {
            "pair_id", "exposure", "initial_matched", "source_matched",
            "exogenous_computed_paid_equal", "visible", "discard"}:
        raise ValueError("complete one-pair receipt required")
    pair_id = receipt["pair_id"]
    if type(pair_id) is not str or not pair_id.strip() or len(pair_id) > 128:
        raise ValueError("invalid assigned pair identity")
    exposure = receipt["exposure"]
    if exposure not in EXPOSURES:
        raise ValueError("unsupported exposure category")
    if receipt["initial_matched"] is not True:
        raise ValueError("initial assignment mismatch")
    if exposure != "EXPOSED":
        if receipt["source_matched"] is not None or (
                receipt["exogenous_computed_paid_equal"] is not None):
            raise ValueError("nonexposure cannot assert computed source parity")
        if receipt["visible"] is not None or receipt["discard"] is not None:
            raise ValueError("nonexposure must not invent a first motor")
        return {"pair_id": pair_id, "exposure": exposure,
                "classification": "NO_EXPOSURE",
                "natural_total_effect_eligible": True,
                "controlled_direct_motor_eligible": False}
    if receipt["source_matched"] is not True or (
            receipt["exogenous_computed_paid_equal"] is not True):
        raise ValueError("equal first-person source and actually paid work required")
    v, d = receipt["visible"], receipt["discard"]
    if type(v) is not dict or type(d) is not dict or (
            set(v) != {"motor", "decision_work", "after_payment_body"} or
            set(d) != {"motor", "decision_work", "after_payment_body"}):
        raise ValueError("incomplete first factual decision receipts")
    motor_v, motor_d = _motor(v["motor"]), _motor(d["motor"])
    work_v, work_d = _work(v["decision_work"]), _work(d["decision_work"])
    body_v, body_d = _body(v["after_payment_body"]), _body(d["after_payment_body"])
    motor_split = motor_v != motor_d
    work_split = work_v != work_d
    delta_e, delta_v = cognitive_cost(BodyLaws(), work_v)
    cost_e, cost_v = cognitive_cost(BodyLaws(), work_d)
    cost_e = delta_e - cost_e
    cost_v = delta_v - cost_v
    residual = None
    if not motor_split:
        expected = (-cost_e, 0., 0., 0., -cost_v)
        residual = max(abs((a-b)-e) for a,b,e in zip(body_v, body_d, expected))
        if residual > TOL:
            raise ValueError("unexplained body difference at same native motor")
    if motor_split and work_split:
        classification = "MOTOR_AND_NATIVE_COST"
    elif motor_split:
        classification = "MOTOR_ONLY"
    elif work_split:
        classification = "NATIVE_COST_ONLY"
    else:
        classification = "NO_OBSERVED_SPLIT"
    return {
        "pair_id": pair_id, "exposure": exposure,
        "classification": classification,
        "native_motor_different": motor_split,
        "native_decision_work_different": work_split,
        "extra_visible_model_energy": cost_e,
        "extra_visible_model_vigilance": cost_v,
        "same_motor_cost_body_residual": residual,
        "natural_total_effect_eligible": True,
        "controlled_direct_motor_eligible": motor_split and not work_split,
    }


def reduce_assigned(receipts, expected_pair_ids):
    """Keep every preassigned independent *identifier*, not just exposed pairs.

    Expected IDs are a completeness contract only, not verification that
    any two assignments are independent, born, or ecologically novel.
    """
    if type(receipts) is not list or type(expected_pair_ids) not in (tuple, list):
        raise ValueError("fixed assignment sequence required")
    if any(type(x) is not str or not x.strip() for x in expected_pair_ids):
        raise ValueError("invalid expected assignment")
    if len(set(expected_pair_ids)) != len(expected_pair_ids) or not expected_pair_ids:
        raise ValueError("expected assignments must be unique and nonempty")
    rows = [classify_receipt(x) for x in receipts]
    ids = [x["pair_id"] for x in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_pair_ids):
        raise ValueError("duplicate, missing or extra assigned unit")
    rows.sort(key=lambda x: expected_pair_ids.index(x["pair_id"]))
    categories = ("NO_EXPOSURE", "NO_OBSERVED_SPLIT", "NATIVE_COST_ONLY",
                  "MOTOR_ONLY", "MOTOR_AND_NATIVE_COST")
    counts = {k: sum(x["classification"] == k for x in rows) for k in categories}
    if sum(counts.values()) != len(expected_pair_ids):
        raise AssertionError("all-assigned denominator lost")
    return {
        "schema": SCHEMA, "status": "METHODS_RECEIPT_CLASSIFICATION_PASS",
        "total_assigned": len(expected_pair_ids),
        "exposed": len(expected_pair_ids)-counts["NO_EXPOSURE"],
        "counts": counts, "rows": rows,
        "effect_size_inferred": False,
        "independent_ecology_attested": False,
        "autonomous_compute_purchase_demonstrated": False,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
    }


def audit_archived_first_splits():
    """Posthoc READ ONLY: reuse pinned original source and its own validators."""
    original = ORIGINAL.audit()
    if (original["status"] != "FIRST_NATIVE_COST_SPLIT_ACCOUNTING_PASS" or
            original["technical_paired_units"] != 4 or
            original["clean_first_motor_mediations"] != 0 or
            original["new_worlds"] != 0 or original["new_scientific_lives"] != 0):
        raise ValueError("wrong existing source boundary")
    rows = []
    for o in original["rows"]:
        key = o["world"] + "/" + str(o["seed"])
        if o["classification"] == "NO_OBSERVED_FIRST_COST_SPLIT":
            if (o["first_split_step"] is not None or
                    o["original_end_bodies_equal"] is not True):
                raise ValueError("invalid archived no-split record")
            classification = "NO_OBSERVED_SPLIT"
        elif o["classification"] == "FIRST_NATIVE_CYCLE_COST_SPLIT_RECONCILED":
            if (o["first_split_step"] is None or
                    o["additional_competition_cycles"] <= 0 or
                    o["max_body_bill_residual"] > TOL):
                raise ValueError("invalid archived cost-split record")
            classification = "NATIVE_COST_ONLY"
        else:
            raise ValueError("unknown original archived class")
        rows.append({"pair_id": key, "classification": classification,
                     "controlled_direct_motor_eligible": False})
    counts = {c: sum(r["classification"] == c for r in rows) for c in (
        "NO_EXPOSURE", "NO_OBSERVED_SPLIT", "NATIVE_COST_ONLY",
        "MOTOR_ONLY", "MOTOR_AND_NATIVE_COST")}
    if counts["NATIVE_COST_ONLY"] != 3 or counts["NO_OBSERVED_SPLIT"] != 1:
        raise ValueError("changed original first-split denominator")
    record = {
        "schema": SCHEMA, "status": "ARCHIVED_FIRST_SPLIT_METHODS_GUARD_PASS",
        "timing": "POSTHOC_ALREADY_EXPOSED_FOUR_TECHNICAL_UNITS",
        "upstream_status_unchanged": "PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND",
        "upstream_original_aggregate_sha256": original["original_aggregate_sha256"],
        "assigned": 4, "counts": counts, "rows": rows,
        "controlled_direct_motor_examples": 0,
        "natural_total_effect_estimand_is_proposed_not_estimated": True,
        "independent_original_authentication": False,
        "physical_cpu_joules_calibrated": False,
        "new_worlds": 0, "new_scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
    }
    record["deterministic_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()
    return record
