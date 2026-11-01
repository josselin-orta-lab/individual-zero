"""I2 unstable-world *reappraisal* composition contract (research only).

This is a pure, inspectable boundary, NOT an instability detector, survival
reflex, new H2 owner, decision policy, UC ledger, motor authority or M11.
Its only inputs are the current first-person claim, already observed chosen
consequences, and separately sourced current survival/need assessments.
No hidden world regime, future outcomes or automatically stale-time bonus.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .chosen_outcome_study import (
    MAX_RECORDED_CHOICES, ChosenResultEvidence, ObservedChosenResult,
)
from .intention_continuity import _ref
from .intention_ingress import ObservationAuthority, ObservationClaim

CONTRACT = "i2-unstable-world-reappraisal-contract-v1"
REFLEX_STATES = frozenset({
    "PREEMPT", "CONSTRAIN", "NO_PREEMPTION", "UNKNOWN",
})
NEED_STATES = frozenset({"CRITICAL", "ELEVATED", "NONE", "UNKNOWN"})
MAX_CONTEXT_CUES = 8


@dataclass(frozen=True, slots=True)
class SurvivalReflexSnapshot:
    """Bound report by a future I2-owned survival-reflex source.

    NO_PREEMPTION means the reflex reports no immediate preemption. It is
    NOT proof that eating, probing or any other action is safe.
    """

    life_ref: str
    capture_ref: str
    claim_digest: str
    evidence_ref: str
    state: str

    def validate(self, claim: ObservationClaim) -> None:
        for value, label in (
            (self.life_ref, "reflex life"),
            (self.capture_ref, "reflex capture"),
            (self.evidence_ref, "reflex evidence"),
        ):
            _ref(value, label)
        if (self.life_ref != claim.life_ref or
                self.capture_ref != claim.capture.ref or
                self.claim_digest != claim.digest() or
                self.evidence_ref not in claim.subjective_evidence_refs or
                self.state not in REFLEX_STATES):
            raise ValueError("survival reflex is stale, foreign or unbound")


class SurvivalReflexAuthority(Protocol):
    """Unimplemented external I2-owned port; tests provide inert doubles."""

    def verify_survival_reflex(
        self, *, claim: ObservationClaim, snapshot: SurvivalReflexSnapshot,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class NeedSnapshot:
    """First-person physiological pressure, not researcher-known rewards."""

    life_ref: str
    capture_ref: str
    claim_digest: str
    evidence_ref: str
    state: str

    def validate(self, claim: ObservationClaim) -> None:
        for value, label in (
            (self.life_ref, "need life"),
            (self.capture_ref, "need capture"),
            (self.evidence_ref, "need evidence"),
        ):
            _ref(value, label)
        if (self.life_ref != claim.life_ref or
                self.capture_ref != claim.capture.ref or
                self.claim_digest != claim.digest() or
                self.evidence_ref not in claim.subjective_evidence_refs or
                self.state not in NEED_STATES):
            raise ValueError("physiological need is stale, foreign or unbound")


class NeedAuthority(Protocol):
    """Unimplemented I2 interoception port; never infer need from lab truth."""

    def verify_need(
        self, *, claim: ObservationClaim, snapshot: NeedSnapshot,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class ReappraisalAdvice:
    """Non-motor explanation only. Even CONSIDER requires paid cognition."""

    contract: str
    life_ref: str
    capture_ref: str
    target_semantic_ref: str
    evidence_state: str
    review_status: str
    provenance_refs: tuple[str, ...]
    hidden_regime_identified: bool = False
    motor_authority: str = "NONE"
    requires_paid_competition: bool = True
    requires_fresh_action_control: bool = True
    m11_authenticated: bool = False


def review_reappraisal(
    *, claim: ObservationClaim, target_semantic_ref: str,
    chosen_results: tuple[ObservedChosenResult, ...],
    observation_source: ObservationAuthority,
    chosen_source: ChosenResultEvidence,
    reflex: SurvivalReflexSnapshot | None = None,
    reflex_source: SurvivalReflexAuthority | None = None,
    need: NeedSnapshot | None = None,
    need_source: NeedAuthority | None = None,
    new_context_refs: tuple[str, ...] = (),
) -> ReappraisalAdvice:
    """Classify a possible *reason to reconsider*, not a world transition.

    No action is selected and no UC is charged here. An integration MUST
    place any review inside the paid I2 owner cycle and retain Competition,
    fresh safety veto, terminal and anti-rollback boundaries. Until a
    real independently sourced reflex exists, REFLEX_UNAVAILABLE is the
    fail-closed result.
    """
    if type(claim) is not ObservationClaim:
        raise ValueError("exact current first-person claim required")
    claim.validate()
    _ref(target_semantic_ref, "reappraisal target")
    if (not callable(getattr(observation_source, "verify", None)) or
            observation_source.verify(
                life_ref=claim.life_ref, claim=claim,
                digest=claim.digest()) is not True):
        raise ValueError("current first-person observation was not verified")
    if (type(chosen_results) is not tuple or
            len(chosen_results) > MAX_RECORDED_CHOICES or
            not callable(getattr(chosen_source, "verify_chosen_result", None))):
        raise ValueError("invalid bounded chosen evidence/source")
    if (type(new_context_refs) is not tuple or
            len(new_context_refs) > MAX_CONTEXT_CUES or
            new_context_refs != tuple(sorted(set(new_context_refs)))):
        raise ValueError("context cues must be bounded, canonical and distinct")

    seen_issues: set[str] = set()
    seen_results: set[str] = set()
    previous_step = -1
    target_outcomes: list[int] = []
    for result in chosen_results:
        if type(result) is not ObservedChosenResult:
            raise ValueError("exact observed chosen result required")
        result.validate()
        if (result.life_ref != claim.life_ref or
                result.issue_capture_ref == claim.capture.ref or
                result.issue_capture_ref in seen_issues or
                result.evidence_ref in seen_results or
                result.evidence_ref not in claim.subjective_evidence_refs or
                result.observed_step <= previous_step or
                result.observed_step >= claim.capture.step or
                chosen_source.verify_chosen_result(result=result) is not True):
            raise ValueError("future, foreign, duplicate or unobserved chosen evidence")
        seen_issues.add(result.issue_capture_ref)
        seen_results.add(result.evidence_ref)
        previous_step = result.observed_step
        if result.chosen_action_ref == target_semantic_ref:
            target_outcomes.append(result.observed_net)
    for ref in new_context_refs:
        _ref(ref, "context cue")
        if (ref not in claim.subjective_evidence_refs or
                ref in seen_results):
            raise ValueError("context cue not in current subjective evidence")

    contradiction = any(x < 0 for x in target_outcomes) and any(
        x > 0 for x in target_outcomes
    )
    evidence_state = (
        "PERSONAL_OUTCOME_CONTRADICTION" if contradiction else
        "NEW_CONTEXT_CUE_NOT_PAYOFF_PROOF" if new_context_refs else
        "LATENT_CHANGE_NOT_IDENTIFIABLE"
    )
    provenance = tuple(sorted(set(
        (*seen_results, *new_context_refs,
         *((reflex.evidence_ref,) if type(reflex) is SurvivalReflexSnapshot else ()),
         *((need.evidence_ref,) if type(need) is NeedSnapshot else ())),
    )))
    def advice(status: str) -> ReappraisalAdvice:
        return ReappraisalAdvice(
            CONTRACT, claim.life_ref, claim.capture.ref, target_semantic_ref,
            evidence_state, status, provenance,
        )

    if reflex is None and reflex_source is None:
        return advice("REFLEX_UNAVAILABLE")
    if type(reflex) is not SurvivalReflexSnapshot or not callable(
            getattr(reflex_source, "verify_survival_reflex", None)):
        raise ValueError("survival reflex report and verified port are both required")
    reflex.validate(claim)
    if reflex_source.verify_survival_reflex(
            claim=claim, snapshot=reflex) is not True:
        raise ValueError("survival reflex source refused current evidence")
    if need is not None or need_source is not None:
        if type(need) is not NeedSnapshot or not callable(
                getattr(need_source, "verify_need", None)):
            raise ValueError("need report and verified port are both required")
        need.validate(claim)
        if need_source.verify_need(claim=claim, snapshot=need) is not True:
            raise ValueError("need source refused current evidence")

    if reflex.state == "PREEMPT":
        return advice("REFLEX_PREEMPTED")
    if reflex.state == "CONSTRAIN":
        return advice("REFLEX_CONSTRAINED")
    if reflex.state == "UNKNOWN":
        return advice("REFLEX_UNKNOWN_DEFER")
    if target_semantic_ref not in claim.capture.accessible_semantics:
        return advice("TARGET_NOT_AVAILABLE")
    if not any(x < 0 for x in target_outcomes):
        return advice("NO_PERSONALLY_LEARNED_AVERSION")
    if contradiction or new_context_refs:
        return advice("EVIDENCE_BASED_RECONSIDERATION_HYPOTHESIS")
    if need is not None and need.state == "CRITICAL":
        return advice("NEED_BASED_RISK_RECONSIDERATION_HYPOTHESIS")
    return advice("LATENT_CHANGE_UNIDENTIFIABLE_DEFER")
