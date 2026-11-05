"""Pure I2 survival-plan viability gate: bounded, subjective, nonmotor.

Last resort means *no currently accessible, source-verified alternative*
energy-restoring plan. Never infer that an unseen plan does not exist, or
that toxic food has recovered. This module does not choose or admit an action,
pay UC, override safety, access hidden payoff, or authenticate M11.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .intention_ingress import ObservationClaim, ObservationAuthority
from .unstable_world_reappraisal_contract import (
    SurvivalReflexSnapshot, SurvivalReflexAuthority,
)

CONTRACT = "i2-survival-plan-viability-v1"
STATES = frozenset({"VIABLE", "NOT_VIABLE", "UNKNOWN"})
MAX_PLANS = 32


@dataclass(frozen=True, slots=True)
class PlanAssessment:
    semantic_ref: str
    state: str
    evidence_ref: str


class PlanEvidenceAuthority(Protocol):
    def verify_plan(self, *, claim: ObservationClaim,
                    plan: PlanAssessment) -> bool: ...


@dataclass(frozen=True, slots=True)
class LastResortAssessment:
    status: str
    target_semantic_ref: str
    alternative_semantics: tuple[str, ...]
    unresolved_semantics: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    motor_authority: str = "NONE"
    paid_competition_required: bool = True
    fresh_action_control_required: bool = True
    hidden_food_payoff_known: bool = False
    m11_authenticated: bool = False


def assess_last_resort(
    *, claim: ObservationClaim,
    reflex: SurvivalReflexSnapshot,
    reflex_source: SurvivalReflexAuthority,
    observation_source: ObservationAuthority,
    plan_source: PlanEvidenceAuthority,
    food_semantic_ref: str,
    plans: tuple[PlanAssessment, ...],
) -> LastResortAssessment:
    """Classify relative to *all currently offered* plans, not world truth."""
    if type(claim) is not ObservationClaim:
        raise ValueError("exact capture required")
    claim.validate()
    if (not callable(getattr(observation_source, "verify", None)) or
            observation_source.verify(life_ref=claim.life_ref, claim=claim,
                                      digest=claim.digest()) is not True):
        raise ValueError("current observation source rejected")
    if (type(reflex) is not SurvivalReflexSnapshot or
            not callable(getattr(reflex_source, "verify_survival_reflex", None))):
        raise ValueError("verified reflex required")
    reflex.validate(claim)
    if reflex_source.verify_survival_reflex(claim=claim, snapshot=reflex) is not True:
        raise ValueError("reflex source rejected")
    if (type(food_semantic_ref) is not str or
            food_semantic_ref not in claim.capture.accessible_semantics):
        raise ValueError("target food not offered")
    offered = claim.capture.accessible_semantics
    expected = tuple(x for x in offered if x != food_semantic_ref)
    if (type(plans) is not tuple or len(plans) > MAX_PLANS or
            len(plans) != len(expected) or
            not callable(getattr(plan_source, "verify_plan", None))):
        raise ValueError("complete bounded plan assessment required")
    seen: set[str] = set()
    evidence: list[str] = [reflex.evidence_ref]
    alternatives: list[str] = []
    unresolved: list[str] = []
    for p in plans:
        if (type(p) is not PlanAssessment or p.semantic_ref not in expected or
                p.semantic_ref in seen or p.state not in STATES or
                p.evidence_ref not in claim.subjective_evidence_refs or
                plan_source.verify_plan(claim=claim, plan=p) is not True):
            raise ValueError("missing, foreign or unverified plan evidence")
        seen.add(p.semantic_ref)
        evidence.append(p.evidence_ref)
        if p.state == "VIABLE":
            alternatives.append(p.semantic_ref)
        elif p.state == "UNKNOWN":
            unresolved.append(p.semantic_ref)
    if seen != set(expected):
        raise ValueError("incomplete accessible alternatives")
    if reflex.state in ("UNKNOWN", "NO_PREEMPTION"):
        status = "NO_EMERGENCY_PRIORITY"
    elif alternatives:
        status = "ALTERNATIVE_VIABLE"
    elif unresolved:
        status = "ALTERNATIVE_UNRESOLVED"
    else:
        status = "LAST_RESORT_RISK_RECONSIDERATION"
    return LastResortAssessment(
        status, food_semantic_ref, tuple(sorted(alternatives)),
        tuple(sorted(unresolved)), tuple(sorted(set(evidence))),
    )
