"""Three-leaf target prior using recent generic personal effect experience.

Software primitive only. It combines the first-person frontier modality prior
with the two-branch action-agnostic empirical prior from recent branch memory.

For target modality m:
    NO_TARGET                     P = 1 - p(m)
    TARGET + empirical effect A   P = p(m) * p(A)
    TARGET + empirical effect B   P = p(m) * p(B)

The whole-tree expected external effect may be nonzero because it is inherited
from personally lived recent effects, never from a designer-selected magnitude.
"""
from __future__ import annotations

from math import fsum

from .body import CognitiveBudget, CognitiveWork, VITAL
from .frontier_modality_prior import paid_frontier_modality_prior
from .recent_generic_effect_prior import paid_recent_generic_effect_prior
from .reference_branches import ReferenceBranchMemory

SCHEMA = "i3-empirical-three-leaf-target-prior/v1"
TARGETS = ("water", "token")
COMPOSE_WORK = CognitiveWork(cycles=1, memory_items=18)
ZERO = (0.0,) * 5


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in ("cycles", "simulated_steps", "memory_items", "replays")
    }


def paid_empirical_three_leaf_target_prior(
        personal_map, memory: ReferenceBranchMemory, target_modality,
        budget: CognitiveBudget, *, work_receipt: dict | None = None) -> dict:
    if target_modality not in TARGETS:
        raise ValueError("target_modality must be 'water' or 'token'")
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no empirical target-prior cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    modality = paid_frontier_modality_prior(personal_map, budget)
    after_modality = budget.work
    effect = paid_recent_generic_effect_prior(memory, budget)
    after_effect = budget.work
    budget.spend(COMPOSE_WORK)

    signal = (
        "WATER_MODALITY" if target_modality == "water"
        else "TOKEN_MODALITY")
    target_probability = next(
        row["probability"] for row in modality["branches"]
        if row["signal"] == signal)
    non_target = {
        row["signal"]: row["probability"]
        for row in modality["branches"]
        if row["signal"] != signal
    }
    if abs(fsum(non_target.values()) - (1.0 - target_probability)) > 1e-12:
        raise RuntimeError("non-target modality mass does not close")

    if not effect["outcomes"]:
        leaves = ()
        status = effect["status"]
    else:
        if len(effect["outcomes"]) != 2:
            raise RuntimeError("empirical unsupported-effect prior must have two outcomes")
        first, second = effect["outcomes"]
        leaves = (
            {
                "leaf": "NO_TARGET_MODALITY",
                "probability": 1.0 - target_probability,
                "observation_sequence": ("NO_TARGET_MODALITY",),
                "effect_delta": ZERO,
            },
            {
                "leaf": "TARGET_MODALITY_EMPIRICAL_EFFECT_A",
                "probability": target_probability * first.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(first.probe_delta),
            },
            {
                "leaf": "TARGET_MODALITY_EMPIRICAL_EFFECT_B",
                "probability": target_probability * second.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(second.probe_delta),
            },
        )
        if len(leaves) != 3:
            raise RuntimeError("empirical target prior must have exactly three leaves")
        if abs(fsum(row["probability"] for row in leaves) - 1.0) > 1e-12:
            raise RuntimeError("empirical target prior does not normalize")
        status = "COMPLETE_EMPIRICAL_THREE_LEAF_TARGET_PRIOR"

    expected = tuple(
        fsum(row["probability"] * row["effect_delta"][c] for row in leaves)
        for c in range(5)) if leaves else ZERO
    expected_from_personal_mean = tuple(
        target_probability * value
        for value in effect["empirical_mean"])
    if outcomes := effect["outcomes"]:
        if any(abs(a - b) > 1e-12
               for a, b in zip(expected, expected_from_personal_mean)):
            raise RuntimeError(
                "whole-tree effect does not match target-weighted personal mean")

    work = _work_delta(budget.work, start)
    result = {
        "schema": SCHEMA,
        "status": status,
        "target_modality": target_modality,
        "target_probability": target_probability,
        "non_target_probability_breakdown": non_target,
        "leaves": leaves,
        "leaf_count": len(leaves),
        "expected_external_delta": expected,
        "target_weighted_personal_mean": expected_from_personal_mean,
        "effect_prior_status": effect["status"],
        "effect_support_records": effect["support_records"],
        "effect_empirical_mean": tuple(effect["empirical_mean"]),
        "effect_compression": effect["compression"],
        "modality_prior": {
            "resource_base_rate": modality["resource_base_rate"],
            "conditional_modality": dict(modality["conditional_modality"]),
            "personal_counts": dict(modality["personal_counts"]),
        },
        "aggregation_semantics": (
            "NON_TARGET_OBSERVATIONS_RETAIN_PROBABILITY_BUT_RECEIVE_NO_"
            "TARGET_SPECIFIC_INFORMATION_CREDIT"),
        "branch_envelope": "EXACTLY_THREE_WHEN_EMPIRICAL_EFFECT_PRIOR_COMPLETE",
        "action_identity_used": False,
        "token_identity_used": False,
        "body_need_used": False,
        "world_access": False,
        "work": work,
        "work_breakdown": {
            "modality_prior": _work_delta(after_modality, start),
            "empirical_effect_prior": _work_delta(after_effect, after_modality),
            "composition": _work_delta(budget.work, after_effect),
            "total": dict(work),
        },
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-empirical-three-leaf-target-prior-work/v1",
            "status": status,
            "work": dict(work),
            "branches": len(leaves),
        })
    return result


__all__ = [
    "COMPOSE_WORK", "SCHEMA", "TARGETS",
    "paid_empirical_three_leaf_target_prior",
]
