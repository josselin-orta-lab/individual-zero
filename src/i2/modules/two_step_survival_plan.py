"""Bounded I2 two-step survival plans, without an outcome oracle.

This is a planning hypothesis only: legal ordered affordances and certain
physical action costs, not a promise of nutrition or an actuator.
"""
from __future__ import annotations
from dataclasses import dataclass

from .intention_ingress import ObservationClaim

COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"
STEP_COST = 2
CONTRACT = "i2-two-step-survival-plan-v1"


@dataclass(frozen=True, slots=True)
class TwoStepPlan:
    actions: tuple[str, str]
    status: str
    guaranteed_pre_food_energy: int | None
    food_outcome: str = "UNKNOWN"
    motor_authority: str = "NONE"


def assess_collect_then_eat(*, claim: ObservationClaim, energy: int,
                            inventory: int, resources: int) -> TwoStepPlan:
    """Check physical feasibility, not viability or the hidden food payoff.

    Collect may be available now; EAT becomes available only after a
    successful collect, and its payoff remains unknown until chosen.
    The worst known two-step action cost is four energy units. There is no
    secret-food lookup, UC discount, free pre-execution or guaranteed rescue.
    """
    if type(claim) is not ObservationClaim:
        raise ValueError("current first-person observation required")
    claim.validate()
    if (type(energy) is not int or not 1 <= energy <= 100 or
            type(inventory) is not int or not 0 <= inventory <= 32 or
            type(resources) is not int or not 0 <= resources <= 32):
        raise ValueError("invalid bounded body state")
    if f"evidence:i2:energy:{energy}" not in claim.subjective_evidence_refs:
        raise ValueError("energy not bound to current capture")
    if COLLECT not in claim.capture.accessible_semantics or resources == 0:
        return TwoStepPlan((COLLECT, EAT), "FIRST_STEP_UNAVAILABLE", None)
    # If the body reaches zero energy at collect, the second step cannot act.
    if energy <= STEP_COST:
        return TwoStepPlan((COLLECT, EAT), "INSUFFICIENT_ENERGY_TO_COLLECT", None)
    after_collect = energy - STEP_COST
    if after_collect <= STEP_COST:
        return TwoStepPlan((COLLECT, EAT), "FOOD_ATTEMPT_MAY_BE_TERMINAL", after_collect)
    return TwoStepPlan((COLLECT, EAT), "PHYSICALLY_SEQUENCEABLE_OUTCOME_UNKNOWN",
                       after_collect)
