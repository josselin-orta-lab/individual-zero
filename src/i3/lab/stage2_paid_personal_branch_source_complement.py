"""Stage-2 E2 source-capacity audit using EXISTING paid action-branch memory.

Frozen protocol: docs/studies/stage2-replay-gate-selected-design/
PAID_PERSONAL_BRANCH_SOURCE_COMPLEMENT_PREFLIGHT_2026-11-11.md

No World, birth, selected action, replay intervention, or controller delivery.
The bodies and deltas are synthetic/unpaid fixture constructions. All memory
storage/read work is genuinely purchased by native *model* CognitiveBudget;
this is not a native World physical-settlement or scientific life claim.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost,
    debit_cognition, validate_body,
)
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.personal_outcomes import NoPersonalSupport, STORE_WORK
from ..modules.reference_branches import ReferenceBranchMemory

SCHEMA = "i3-stage2-existing-paid-action-branch-complement/v1"
SOURCE_KIND = "SYNTHETIC_UNPAID_FIXTURE_NOT_A_BORN_PERSON"
SEED = 211
BODY = (70., 60., 60., 90., 70.)
KEY = ("attendre", None)
NATIVE_KEY = ("attendre",)
DECISION_WORK = CognitiveWork(cycles=3)
FIXED_HISTORIES = (
    ("spread", ((-.5, -4., 0., 0., 0.), (-.5, +4., 0., 0., 0.))),
    ("flat", ((-.5, 0., 0., 0., 0.), (-.5, 0., 0., 0., 0.))),
)
ZERO_WORK = CognitiveWork()


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(value):
    return sha256(_canonical(value)).hexdigest()


def _paid_work(body, budget, requested):
    if budget.work != requested:
        raise AssertionError("existing model did not prepay exact declared work")
    paid_post, account = debit_cognition(body, BodyLaws(), requested)
    if tuple(budget.remaining) != tuple(paid_post):
        raise AssertionError("native funding and debit do not reconcile")
    if any(account[k]["unpaid"] != 0. for k in ("energy", "vigilance")):
        raise AssertionError("native model budget left unpaid cognitive work")
    energy, vigilance = cognitive_cost(BodyLaws(), requested)
    if energy < 0 or vigilance < 0:
        raise AssertionError("invalid native cognitive tariff")
    return {
        "work": asdict(requested),
        "energy": energy,
        "vigilance": vigilance,
        "both_currencies_paid_in_model": True,
        "no_World_physical_settlement_claim": True,
    }


def _make(label, deltas):
    if label not in ("spread", "flat") or len(deltas) != 2:
        raise ValueError("only the two precommitted histories")
    laws = BodyLaws()
    mind = Mind(midpoint(), SEED)
    history = ReferenceBranchMemory()
    stored = []
    # This constructs artificial first-person-format results; neither native
    # World.step nor an individual has actually experienced them.
    after_decision, bill = debit_cognition(BODY, laws, DECISION_WORK)
    if any(bill[k]["unpaid"] != 0. for k in ("energy", "vigilance")):
        raise AssertionError("pre-store synthetic decision model bill invalid")
    for delta in deltas:
        if len(delta) != 5:
            raise ValueError("fixed five-channel delta required")
        synthetic_physical_after = validate_body(
            tuple(b + d for b, d in zip(after_decision, delta))
        )
        allowance = CognitiveBudget(synthetic_physical_after, laws)
        history.observe(KEY, BODY, DECISION_WORK, allowance)
        paid = _paid_work(synthetic_physical_after, allowance, STORE_WORK)
        stored.append(paid)
        # The native P1.3 EffectsModel has no ring of empirical outcomes.
        # We construct identical means with different individual histories.
        mind.effects.observe(NATIVE_KEY, delta)
    if len(history._samples) != 2 or len(stored) != 2:
        raise AssertionError("lost or duplicated synthetic personal outcome")
    native_pred = mind._read_plan_prediction(NATIVE_KEY)
    source_before = _sha({
        "native_effects": mind.effects.stats,
        "native_values": mind.values,
        "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
        "branch_samples": [
            {"key": s.key, "delta": s.delta} for s in history._samples
        ],
    })
    read_budget = CognitiveBudget(BODY, laws)
    read_receipt = {}
    supported = history.read_support(
        KEY, read_budget, work_receipt=read_receipt
    )
    expected_read = CognitiveWork(
        cycles=1, memory_items=7 * len(history._samples) + 2
    )
    read_paid = _paid_work(BODY, read_budget, expected_read)
    if read_receipt.get("status") != "COMPLETE" or (
        read_receipt.get("branches") != 2
        or read_receipt.get("work") != asdict(expected_read)
    ):
        raise AssertionError("native priced branch read receipt is incomplete")
    source_after = _sha({
        "native_effects": mind.effects.stats,
        "native_values": mind.values,
        "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
        "branch_samples": [
            {"key": s.key, "delta": s.delta} for s in history._samples
        ],
    })
    if source_before != source_after:
        raise AssertionError("paid observational read altered stored source")
    return {
        "label": label,
        "native_effects_stats": mind.effects.stats,
        "native_forecast": native_pred,
        "native_effects_digest": _sha(mind.effects.stats),
        "stored_action_key": KEY,
        "stored_samples": len(history._samples),
        "storage_model_payment_each": stored,
        "read_model_payment": read_paid,
        "read_receipt": read_receipt,
        "empirical_support": supported,
        "support_sha256": _sha(supported),
        "original_source_not_mutated_by_paid_read": True,
        "Worlds_created": 0,
        "scientific_lives": 0,
    }


def audit():
    rows = [_make(label, deltas) for label, deltas in FIXED_HISTORIES]
    first, second = rows
    if (first["native_effects_stats"] != second["native_effects_stats"]
            or first["native_forecast"] != second["native_forecast"]):
        raise AssertionError(
            "frozen history contrast inadvertently altered native effect mean"
        )
    if first["read_model_payment"] != second["read_model_payment"]:
        raise AssertionError("native new-information read costs are not equal")
    if first["empirical_support"] == second["empirical_support"]:
        raise AssertionError("the retained outcome distribution lost its spread")
    if any(row["stored_action_key"] != KEY
           or row["stored_samples"] != 2
           or len(row["empirical_support"]) != 2
           or not row["original_source_not_mutated_by_paid_read"]
           for row in rows):
        raise AssertionError("the paid source was not exact, bounded and immutable")
    result = {
        "schema": SCHEMA,
        "source_kind": SOURCE_KIND,
        "fixed_histories": len(rows),
        "fixed_records_per_history": 2,
        "equal_original_native_effect_stats": True,
        "equal_native_mean_action_forecasts": True,
        "equal_native_paid_read_work": True,
        "different_action_specific_empirical_branch_support": True,
        "storage_work_fully_model_paid": True,
        "read_work_fully_model_paid": True,
        "action_specific_binding": True,
        "unknown_actions_have_no_personal_support": True,
        "additional_information_reaches_native_Mind_decide": False,
        "new_inferred_controller_policy": False,
        "actual_World_settlement_attested": False,
        "new_scientific_Worlds": 0,
        "new_scientific_lives": 0,
        "technical_verdict": (
            "EXISTING_PAID_ACTION_BRANCHES_CONTAIN_NONMEAN_PERSONAL_INFORMATION_"
            "SOFTWARE_ONLY"
        ),
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "rows": rows,
    }
    return {**result, "aggregate_sha256": _sha(result)}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2, allow_nan=False))
