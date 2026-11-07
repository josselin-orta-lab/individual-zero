"""Three-leaf composition of frontier modality and unsupported-effect priors.

Software primitive only. It keeps the Stage-1 owner-specified uncertainty
envelope at at most three leaves by valuing one target modality at a time.

For a target modality m:
    NO_TARGET                         P = 1 - p(m)
    TARGET then positive trial effect P = p(m) * 0.5
    TARGET then negative trial effect P = p(m) * 0.5

All non-target observation mass remains explicitly reported. Aggregation means
"not credited in this target-specific valuation", never "perceptually identical".
"""
from __future__ import annotations

from math import fsum

from .body import CognitiveBudget, CognitiveWork, VITAL
from .frontier_modality_prior import paid_frontier_modality_prior
from .unknown_effect_prior import paid_zero_mean_stake_prior

SCHEMA = "i3-three-leaf-target-prior/v1"
TARGETS = ("water", "token")
COMPOSE_WORK = CognitiveWork(cycles=1, memory_items=18)
ZERO = (0.0,) * 5


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in ("cycles", "simulated_steps", "memory_items", "replays")
    }


def paid_three_leaf_target_prior(
        personal_map, body, theta, powers, weights, target_modality,
        budget: CognitiveBudget, *, work_receipt: dict | None = None) -> dict:
    """Compose one modality prior with one zero-mean unknown-effect prior.

    The modality probability is first-person and utility-free. The effect
    direction is stake-projected and modality-free. This separation prevents a
    target name such as water from injecting a favorable bodily consequence.
    """
    if target_modality not in TARGETS:
        raise ValueError("target_modality must be 'water' or 'token'")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if tuple(body) != tuple(budget.body):
        raise ValueError("composition body must match cognitive allowance body")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no target-prior cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work

    modality = paid_frontier_modality_prior(personal_map, budget)
    after_modality = budget.work

    # The zero-mean prior intentionally requires a fresh allowance. Quote and
    # compute it on a same-body suballowance, then buy exactly that declared
    # work from the real cumulative allowance before composition continues.
    effect_allowance = CognitiveBudget(budget.body, budget.laws)
    effect = paid_zero_mean_stake_prior(
        tuple(body), tuple(theta), tuple(powers), tuple(weights),
        effect_allowance)
    budget.spend(effect_allowance.work)
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
        status = "NO_STAKE_RELEVANT_UNCERTAINTY"
    else:
        if len(effect["outcomes"]) != 2:
            raise RuntimeError("zero-mean effect prior must have exactly two outcomes")
        plus, minus = effect["outcomes"]
        leaves = (
            {
                "leaf": "NO_TARGET_MODALITY",
                "probability": 1.0 - target_probability,
                "observation_sequence": ("NO_TARGET_MODALITY",),
                "effect_delta": ZERO,
            },
            {
                "leaf": "TARGET_MODALITY_TRIAL_POSITIVE",
                "probability": target_probability * plus.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(plus.probe_delta),
            },
            {
                "leaf": "TARGET_MODALITY_TRIAL_NEGATIVE",
                "probability": target_probability * minus.probability,
                "observation_sequence": (
                    signal, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"),
                "effect_delta": tuple(minus.probe_delta),
            },
        )
        if len(leaves) > 3:
            raise RuntimeError("Stage-1 branch envelope exceeded")
        total = fsum(row["probability"] for row in leaves)
        if abs(total - 1.0) > 1e-12:
            raise RuntimeError("three-leaf target prior does not normalize")
        status = "COMPLETE_THREE_LEAF_TARGET_PRIOR"

    expected = tuple(
        fsum(row["probability"] * row["effect_delta"][c] for row in leaves)
        for c in range(5)) if leaves else ZERO
    if any(abs(x) > 1e-12 for x in expected):
        raise RuntimeError("composed unsupported effect acquired a nonzero mean")

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
        "modality_prior": {
            "resource_base_rate": modality["resource_base_rate"],
            "conditional_modality": dict(modality["conditional_modality"]),
            "personal_counts": dict(modality["personal_counts"]),
        },
        "effect_prior_status": effect["status"],
        "effect_direction": tuple(effect["distress_direction"]),
        "aggregation_semantics": (
            "NON_TARGET_OBSERVATIONS_RETAIN_PROBABILITY_BUT_RECEIVE_NO_"
            "TARGET_SPECIFIC_INFORMATION_CREDIT"),
        "branch_envelope": "AT_MOST_THREE_STAGE1_LEAVES",
        "work": work,
        "work_breakdown": {
            "modality_prior": _work_delta(after_modality, start),
            "effect_prior": _work_delta(after_effect, after_modality),
            "composition": _work_delta(budget.work, after_effect),
            "total": dict(work),
        },
        "action_input": False,
        "world_access": False,
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-three-leaf-target-prior-work/v1",
            "status": status,
            "work": dict(work),
        })
    return result


__all__ = [
    "COMPOSE_WORK", "SCHEMA", "TARGETS", "paid_three_leaf_target_prior",
]
