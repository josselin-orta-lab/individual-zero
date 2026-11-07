"""Three-leaf target prior using recent personal RMS uncertainty scale.

Software primitive only. It combines the first-person frontier modality prior
with the zero-mean RMS unsupported-effect prior.

For target modality m:
    NO_TARGET                    P = 1 - p(m)
    TARGET + RMS positive effect P = p(m) * 0.5
    TARGET + RMS negative effect P = p(m) * 0.5

The whole-tree expected external effect is exactly zero, unless an innate
expectation omega is passed: then it is p(m) * omega * s (see
recent_rms_effect_prior).
"""
from __future__ import annotations

from math import fsum

from .body import CognitiveBudget, CognitiveWork, VITAL
from .frontier_modality_prior import paid_frontier_modality_prior
from .recent_rms_effect_prior import paid_recent_rms_zero_mean_effect_prior
from .reference_branches import ReferenceBranchMemory

SCHEMA = "i3-rms-three-leaf-target-prior/v1"
TARGETS = ("water", "token")
COMPOSE_WORK = CognitiveWork(cycles=1, memory_items=18)
ZERO = (0.0,) * 5


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in ("cycles", "simulated_steps", "memory_items", "replays")
    }


def rms_three_leaf_target_prior_work_ceiling(
        personal_map, memory: ReferenceBranchMemory) -> CognitiveWork:
    """Exact structural work quote without reading empirical sample values.

    This is a funding formula, not cognition. The paid implementation below
    still performs every map/memory read. The quote depends only on container
    sizes and therefore cannot leak sample signs, effects or World facts.
    """
    if type(personal_map) is not dict:
        raise ValueError("plain first-person map required")
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    retained = len(memory._samples)
    support = min(retained, 3)

    # paid_frontier_modality_prior
    cycles = 1
    memory_items = 2 * len(personal_map) + 8

    # ReferenceBranchMemory.recent_generic_effects
    cycles += 1
    memory_items += 7 * retained + 2

    # paid_recent_rms_zero_mean_effect_prior construction
    if support < 2:
        cycles += 1
        memory_items += 2
    else:
        cycles += 2
        memory_items += 5 * support + 12

    # RMS target composition
    cycles += COMPOSE_WORK.cycles
    memory_items += COMPOSE_WORK.memory_items
    return CognitiveWork(cycles=cycles, memory_items=memory_items)


def paid_rms_three_leaf_target_prior(
        personal_map, memory: ReferenceBranchMemory, target_modality,
        budget: CognitiveBudget, *, work_receipt: dict | None = None,
        omega: float = 0.0) -> dict:
    """Compose target observation probability with symmetric personal RMS scale."""
    if target_modality not in TARGETS:
        raise ValueError("target_modality must be 'water' or 'token'")
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no RMS target-prior cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    modality = paid_frontier_modality_prior(personal_map, budget)
    after_modality = budget.work
    effect = paid_recent_rms_zero_mean_effect_prior(memory, budget, omega=omega)
    omega = effect["innate_mean_shift_omega"]
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
            raise RuntimeError("RMS effect prior must have exactly two outcomes")
        plus, minus = effect["outcomes"]
        leaves = (
            {
                "leaf": "NO_TARGET_MODALITY",
                "probability": 1.0 - target_probability,
                "observation_sequence": ("NO_TARGET_MODALITY",),
                "effect_delta": ZERO,
            },
            {
                "leaf": "TARGET_MODALITY_RMS_POSITIVE",
                "probability": target_probability * plus.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(plus.probe_delta),
            },
            {
                "leaf": "TARGET_MODALITY_RMS_NEGATIVE",
                "probability": target_probability * minus.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(minus.probe_delta),
            },
        )
        if len(leaves) != 3:
            raise RuntimeError("RMS target prior must have exactly three leaves")
        if abs(fsum(row["probability"] for row in leaves) - 1.0) > 1e-12:
            raise RuntimeError("RMS target prior does not normalize")
        status = "COMPLETE_RMS_THREE_LEAF_TARGET_PRIOR"

    expected = tuple(
        fsum(row["probability"] * row["effect_delta"][c] for row in leaves)
        for c in range(5)) if leaves else ZERO
    intended = tuple(
        target_probability * omega * scale_c
        for scale_c in effect["rms_scale"]) if leaves else ZERO
    if any(abs(value - want) > 1e-12 for value, want in zip(expected, intended)):
        raise RuntimeError("RMS target prior mean differs from p * omega * s")

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
        "innate_mean_shift_omega": omega,
        "effect_prior_status": effect["status"],
        "effect_support_records": effect["support_records"],
        "rms_scale": tuple(effect["rms_scale"]),
        "recent_raw_second_moment": tuple(
            effect["recent_raw_second_moment"]),
        "branch_second_moment": tuple(effect["branch_second_moment"]),
        "modality_prior": {
            "resource_base_rate": modality["resource_base_rate"],
            "conditional_modality": dict(modality["conditional_modality"]),
            "personal_counts": dict(modality["personal_counts"]),
        },
        "aggregation_semantics": (
            "NON_TARGET_OBSERVATIONS_RETAIN_PROBABILITY_BUT_RECEIVE_NO_"
            "TARGET_SPECIFIC_INFORMATION_CREDIT"),
        "branch_envelope": "EXACTLY_THREE_WHEN_RMS_EFFECT_PRIOR_COMPLETE",
        "cross_channel_approximation": (
            "SYMMETRIC_PLUS_MINUS_RMS_IMPOSES_RANK_ONE_COMMON_SIGN_STRUCTURE"),
        "action_identity_used": False,
        "token_identity_used": False,
        "body_need_used": False,
        "world_access": False,
        "work": work,
        "work_breakdown": {
            "modality_prior": _work_delta(after_modality, start),
            "rms_effect_prior": _work_delta(after_effect, after_modality),
            "composition": _work_delta(budget.work, after_effect),
            "total": dict(work),
        },
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-rms-three-leaf-target-prior-work/v1",
            "status": status,
            "branches": len(leaves),
            "work": dict(work),
        })
    return result


__all__ = [
    "COMPOSE_WORK", "SCHEMA", "TARGETS",
    "paid_rms_three_leaf_target_prior",
    "rms_three_leaf_target_prior_work_ceiling",
]
