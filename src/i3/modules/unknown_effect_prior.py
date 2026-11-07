"""Paid zero-mean ignorance projected onto the individual's current stakes.

This module is a software primitive, not a decision policy. It knows no action,
token, map, World or resource type. For a personally unsupported consequence it
constructs exactly two opposite bodily-effect hypotheses along the local
steepest-reduction direction of the individual's own distress D.

The pair has equal probability and exact zero expected external delta. Any
preference between the branches can therefore arise only when the existing
body/distress model evaluates them.
"""
from __future__ import annotations

from math import isfinite, sqrt

from .body import CognitiveBudget, CognitiveWork, VITAL
from .plan_information import PlanSubjectiveOutcome

SCHEMA = "i3-zero-mean-stake-prior/v1"
DELTA_RADIUS = 100.0

# Explicit model-work accounting:
# read body/theta/p/w = 20 scalar items;
# write two five-channel deltas + two probabilities = 12 items.
PRIOR_WORK = CognitiveWork(cycles=1, memory_items=32)


def _vector(value, name, *, low=None, strictly_positive=False):
    if type(value) is not tuple or len(value) != 5:
        raise ValueError(f"{name} must be an immutable five-channel tuple")
    for x in value:
        if type(x) not in (int, float) or not isfinite(x):
            raise ValueError(f"{name} must contain finite numeric values")
        if low is not None and x < low:
            raise ValueError(f"{name} below admissible bound")
        if strictly_positive and x <= 0:
            raise ValueError(f"{name} must be strictly positive")
    return tuple(float(x) for x in value)


def paid_zero_mean_stake_prior(body, theta, powers, weights,
                               budget: CognitiveBudget, *,
                               work_receipt: dict | None = None) -> dict:
    """Construct a two-point unsupported-effect quadrature.

    body is the current first-person bodily state. theta, powers and weights
    are the individual's inherited distress parameters.

    On each currently distressed channel (body < theta), the beneficial local
    direction magnitude is the analytic negative derivative of D with respect
    to that body channel:

        w * p/theta * ((theta-body)/theta)**(p-1)

    The resulting five-vector is L2-normalized and scaled to the existing
    maximum admissible effect-delta radius 100. The second hypothesis is its
    exact negative. Both receive probability 0.5 and the same generic
    directly-sensed-body signal.

    If D is locally flat, the calculation returns no hypotheses rather than
    inventing an exploration motive.
    """
    b = _vector(body, "body", low=0.0)
    if any(x > 100.0 for x in b):
        raise ValueError("body above physical channel bound")
    th = _vector(theta, "theta", strictly_positive=True)
    p = _vector(powers, "powers", strictly_positive=True)
    w = _vector(weights, "weights", strictly_positive=True)
    if any(x < 1.0 for x in p):
        raise ValueError("distress powers below supported convex range")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if tuple(budget.body) != b or budget.work != CognitiveWork():
        raise ValueError("fresh allowance must match current body")
    if any(b[c] <= 0.0 for c in VITAL):
        raise ValueError("no unsupported-effect cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    budget.spend(PRIOR_WORK)

    gradient = []
    for bc, tc, pc, wc in zip(b, th, p, w):
        if bc >= tc:
            gradient.append(0.0)
            continue
        x = (tc - bc) / tc
        gradient.append(wc * pc / tc * (x ** (pc - 1.0)))

    norm = sqrt(sum(x * x for x in gradient))
    if norm <= 1e-15:
        outcomes = ()
        status = "NO_STAKE_RELEVANT_UNCERTAINTY"
        direction = (0.0,) * 5
    else:
        direction = tuple(x / norm for x in gradient)
        positive = tuple(DELTA_RADIUS * x for x in direction)
        negative = tuple(-x for x in positive)
        outcomes = (
            PlanSubjectiveOutcome(
                .5, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT", positive),
            PlanSubjectiveOutcome(
                .5, "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT", negative),
        )
        status = "COMPLETE_ZERO_MEAN_STAKE_PRIOR"

    work = {
        k: getattr(budget.work, k) - getattr(start, k)
        for k in ("cycles", "simulated_steps", "memory_items", "replays")
    }
    result = {
        "schema": SCHEMA,
        "status": status,
        "outcomes": outcomes,
        "distress_direction": direction,
        "delta_radius": DELTA_RADIUS,
        "expected_external_delta": tuple(
            sum(o.probability * o.probe_delta[c] for o in outcomes)
            for c in range(5)) if outcomes else (0.0,) * 5,
        "work": work,
        "cost_is_physical_settlement_receipt": False,
        "action_input": False,
        "token_input": False,
        "world_access": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-zero-mean-stake-prior-work/v1",
            "status": status,
            "work": dict(work),
        })
    return result


__all__ = [
    "DELTA_RADIUS", "PRIOR_WORK", "SCHEMA", "paid_zero_mean_stake_prior",
]
