"""Inert I2 temporal eligibility study. Association is NOT causal proof.

No living first-person attestor, UC scheduler, Q publication, motor authority
or WorldBody access. Do not treat these scores as a live decision policy.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol

SCHEMA = "i2-delayed-subjective-credit-study-v1"

def _ref(value: object, name: str) -> str:
    if (type(value) is not str or not 1 <= len(value) <= 256 or
            any(c.isspace() or not c.isprintable() for c in value)):
        raise ValueError(f"invalid {name}")
    return value

@dataclass(frozen=True, slots=True)
class ClaimedLivedStep:
    life_ref: str
    physical_step: int
    capture_ref: str
    goal_ref: str
    action_semantic_ref: str
    admission_ref: str
    subjective_evidence_ref: str
    outcome_ref: str | None
    lived_delta: int | None

    def validate(self) -> None:
        for name in ("life_ref", "capture_ref", "goal_ref", "action_semantic_ref",
                     "admission_ref", "subjective_evidence_ref"):
            _ref(getattr(self, name), name)
        if type(self.physical_step) is not int or self.physical_step < 0:
            raise ValueError("invalid physical step")
        if self.lived_delta is None:
            if self.outcome_ref is not None:
                raise ValueError("unobserved outcome has unexpected reference")
        else:
            if (type(self.lived_delta) is not int or
                    not -100 <= self.lived_delta <= 100):
                raise ValueError("invalid lived delta")
            _ref(self.outcome_ref, "outcome reference")

class LivedEvidenceSource(Protocol):
    def verify_lived(self, *, event: ClaimedLivedStep) -> bool: ...

@dataclass(frozen=True, slots=True)
class TemporalContribution:
    semantic_ref: str
    action_capture_ref: str
    outcome_capture_ref: str
    outcome_ref: str
    lag: int
    weight: Fraction
    lived_delta: int
    attributed: Fraction

@dataclass(frozen=True, slots=True)
class DelayedCreditStudy:
    life_ref: str
    observed_steps: int
    outcome_count: int
    credits: tuple[tuple[str, Fraction], ...]
    contributions: tuple[TemporalContribution, ...]
    schema: str = SCHEMA
    interpretation: str = "TEMPORAL_ASSOCIATION_NOT_CAUSAL_PROOF"
    motor_authority: str = "NONE"
    scheduler_uc_authenticated: bool = False
    m11_authenticated: bool = False

def study_delayed_credit(*, events: tuple[ClaimedLivedStep, ...],
                         source: LivedEvidenceSource, horizon: int = 8,
                         decay_numerator: int = 1,
                         decay_denominator: int = 2) -> DelayedCreditStudy:
    """All actions in a same-goal bounded history may receive future credit.

    Incidental actions receive credit too. These are inspectable hypotheses,
    neither Q values nor evidence that an action caused an outcome.
    """
    if type(events) is not tuple or not events or len(events) > 128:
        raise ValueError("bounded nonempty immutable events required")
    if (type(horizon) is not int or not 1 <= horizon <= 32 or
            type(decay_denominator) is not int or not 1 <= decay_denominator <= 16 or
            type(decay_numerator) is not int or
            not 0 <= decay_numerator < decay_denominator):
        raise ValueError("invalid eligibility parameters")
    if isinstance(source, type) or not callable(getattr(source, "verify_lived", None)):
        raise ValueError("missing evidence authority")
    seen_captures, seen_admissions, seen_outcomes = set(), set(), set()
    last_step, life = -1, None
    for event in events:
        if type(event) is not ClaimedLivedStep:
            raise ValueError("wrong event type")
        event.validate()
        if life is None:
            life = event.life_ref
        if (event.life_ref != life or event.physical_step <= last_step or
                event.capture_ref in seen_captures or
                event.admission_ref in seen_admissions or
                (event.outcome_ref is not None and event.outcome_ref in seen_outcomes)):
            raise ValueError("foreign, stale or replayed evidence")
        last_step = event.physical_step
        seen_captures.add(event.capture_ref)
        seen_admissions.add(event.admission_ref)
        if event.outcome_ref is not None:
            seen_outcomes.add(event.outcome_ref)
        if source.verify_lived(event=event) is not True:
            raise ValueError("first-person evidence not attested")

    decay = Fraction(decay_numerator, decay_denominator)
    pending: list[ClaimedLivedStep] = []
    credits: dict[str, Fraction] = {}
    contributions: list[TemporalContribution] = []
    prior_goal, outcomes = None, 0
    for event in events:
        if event.goal_ref != prior_goal:
            pending = []
        pending = [p for p in pending if event.physical_step - p.physical_step <= horizon]
        pending.append(event)
        credits.setdefault(event.action_semantic_ref, Fraction(0))
        if event.lived_delta is not None:
            outcomes += 1
            for earlier in pending:
                lag = event.physical_step - earlier.physical_step
                weight = decay ** lag
                attributed = event.lived_delta * weight
                credits[earlier.action_semantic_ref] += attributed
                contributions.append(TemporalContribution(
                    earlier.action_semantic_ref, earlier.capture_ref,
                    event.capture_ref, event.outcome_ref, lag, weight,
                    event.lived_delta, attributed))
        prior_goal = event.goal_ref
    return DelayedCreditStudy(life, len(events), outcomes,
                              tuple(sorted(credits.items())), tuple(contributions))
