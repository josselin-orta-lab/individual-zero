"""Paid action-agnostic empirical prior for an unsupported action effect.

The prior uses only recently retained personal bodily deltas from the existing
ReferenceBranchMemory. Action and token identities are deliberately discarded.

At most three recent deltas are compressed into exactly two uncertainty
branches so a target-specific Stage-1 tree can still fit:
    no-target + effect-A + effect-B = three leaves.

This is not the failed P5b global point prior. Two explicit consequence
hypotheses remain, and supported actions continue to use their own learned
predictions.
"""
from __future__ import annotations

from math import fsum, isfinite

from .body import CognitiveBudget, CognitiveWork
from .information_value import WORK_KEYS
from .plan_information import PlanSubjectiveOutcome
from .reference_branches import ReferenceBranchMemory

SCHEMA = "i3-recent-generic-effect-prior/v1"
SIGNAL = "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"


def _delta(value):
    if (type(value) is not tuple or len(value) != 5 or
            any(type(x) not in (int, float) or not isfinite(x) or
                not -100.0 <= x <= 100.0 for x in value)):
        raise ValueError("five finite empirical deltas in [-100,100] required")
    return tuple(float(x) for x in value)


def _mean(rows):
    n = len(rows)
    return tuple(fsum(row[c] for row in rows) / n for c in range(5))


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS
    }


def paid_recent_generic_effect_prior(
        memory: ReferenceBranchMemory, budget: CognitiveBudget, *,
        work_receipt: dict | None = None) -> dict:
    """Compress the last 2-3 generic personal effects into two branches.

    Two samples are retained directly at p=.5/.5.

    With three samples, the closest pair in five-dimensional squared Euclidean
    effect space is averaged into one branch with probability 2/3; the remaining
    sample is the other branch with probability 1/3. Pair ties resolve by
    chronological pair index. This exactly preserves the three-sample empirical
    mean without reading any action identity.
    """
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    read_receipt = {}
    samples = tuple(
        _delta(row) for row in memory.recent_generic_effects(
            budget, work_receipt=read_receipt))
    after_read = budget.work

    if len(samples) < 2:
        budget.spend(CognitiveWork(cycles=1, memory_items=2))
        outcomes = ()
        status = "INSUFFICIENT_GENERIC_SUPPORT"
        empirical_mean = _mean(samples) if samples else (0.0,) * 5
        compression = "NONE"
    elif len(samples) == 2:
        budget.spend(CognitiveWork(cycles=1, memory_items=12))
        empirical_mean = _mean(samples)
        if samples[0] == samples[1]:
            outcomes = ()
            status = "NO_EMPIRICAL_DIVERSITY"
            compression = "TWO_IDENTICAL_RECENT_EFFECTS"
        else:
            outcomes = (
                PlanSubjectiveOutcome(.5, SIGNAL, samples[0]),
                PlanSubjectiveOutcome(.5, SIGNAL, samples[1]),
            )
            status = "COMPLETE_TWO_BRANCH_EMPIRICAL_PRIOR"
            compression = "TWO_RECENT_EFFECTS"
    elif len(samples) == 3:
        budget.spend(CognitiveWork(cycles=4, memory_items=27))
        empirical_mean = _mean(samples)
        pairs = ((0, 1), (0, 2), (1, 2))

        def distance(pair):
            a, b = pair
            return fsum(
                (samples[a][c] - samples[b][c]) ** 2
                for c in range(5))

        pair = min(pairs, key=lambda p: (distance(p), pairs.index(p)))
        other = next(i for i in range(3) if i not in pair)
        pair_mean = _mean((samples[pair[0]], samples[pair[1]]))
        singleton = samples[other]
        if pair_mean == singleton:
            outcomes = ()
            status = "NO_EMPIRICAL_DIVERSITY"
            compression = "CLOSEST_PAIR_COLLAPSED_TO_SINGLETON"
        else:
            outcomes = (
                PlanSubjectiveOutcome(2.0 / 3.0, SIGNAL, pair_mean),
                PlanSubjectiveOutcome(1.0 / 3.0, SIGNAL, singleton),
            )
            status = "COMPLETE_TWO_BRANCH_EMPIRICAL_PRIOR"
            compression = "CLOSEST_PAIR_MEAN_PLUS_SINGLETON"
    else:
        raise RuntimeError("recent generic read exceeded WINDOW=3")

    if outcomes:
        expected = tuple(
            fsum(out.probability * out.probe_delta[c] for out in outcomes)
            for c in range(5))
        if any(abs(a - b) > 1e-12
               for a, b in zip(expected, empirical_mean)):
            raise RuntimeError("empirical compression failed to preserve mean")
    else:
        expected = tuple(empirical_mean)

    result = {
        "schema": SCHEMA,
        "status": status,
        "outcomes": outcomes,
        "support_records": len(samples),
        "raw_recent_deltas": samples,
        "empirical_mean": tuple(empirical_mean),
        "expected_external_delta": tuple(expected),
        "compression": compression,
        "branch_count": len(outcomes),
        "source": "RECENT_ACTION_AGNOSTIC_PERSONAL_BRANCH_MEMORY",
        "action_identity_used": False,
        "token_identity_used": False,
        "body_need_used": False,
        "world_access": False,
        "point_prior": False,
        "work": _work_delta(budget.work, start),
        "work_breakdown": {
            "memory_read": _work_delta(after_read, start),
            "compression": _work_delta(budget.work, after_read),
            "total": _work_delta(budget.work, start),
        },
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-recent-generic-effect-prior-work/v1",
            "status": status,
            "work": dict(result["work"]),
            "support_records": len(samples),
            "branches": len(outcomes),
        })
    return result


__all__ = ["SCHEMA", "SIGNAL", "paid_recent_generic_effect_prior"]
