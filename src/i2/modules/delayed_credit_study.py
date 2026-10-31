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


@dataclass(frozen=True, slots=True)
class MatchedLivedEpisode:
    """An asserted complete, contiguous first-person segment, not a trial oracle."""

    episode_ref: str
    context_signature: tuple[str, ...]
    events: tuple[ClaimedLivedStep, ...]

    def validate(self) -> None:
        _ref(self.episode_ref, "episode reference")
        if (type(self.context_signature) is not tuple or
                not 1 <= len(self.context_signature) <= 16):
            raise ValueError("bounded subjective context signature required")
        for ref in self.context_signature:
            _ref(ref, "subjective context feature")
        if self.context_signature != tuple(sorted(set(self.context_signature))):
            raise ValueError("subjective context must be canonical and unique")
        if (type(self.events) is not tuple or not 2 <= len(self.events) <= 32 or
                any(type(event) is not ClaimedLivedStep for event in self.events)):
            raise ValueError("complete bounded episode events required")
        for event in self.events:
            event.validate()
        first = self.events[0]
        if any(event.life_ref != first.life_ref or
               event.goal_ref != first.goal_ref or
               event.physical_step != first.physical_step + i
               for i, event in enumerate(self.events)):
            raise ValueError("noncontiguous, foreign or goal-changing episode")


class MatchedLivedSource(LivedEvidenceSource, Protocol):
    def verify_complete_episode(self, *, episode: MatchedLivedEpisode) -> bool: ...


@dataclass(frozen=True, slots=True)
class MatchedOutcomeContrast:
    """Observed within-life comparison, NEVER inferred physical causation."""

    life_ref: str
    goal_ref: str
    context_signature: tuple[str, ...]
    prepared_episode_ref: str
    control_episode_ref: str
    preparatory_action_ref: str
    alternative_action_ref: str
    completion_action_ref: str
    shared_intervening_actions: tuple[str, ...]
    observed_prepared_outcome: int
    observed_control_outcome: int
    observed_outcome_difference: int
    observed_net_difference: int | None
    interpretation: str = "MATCHED_OBSERVATION_NOT_CAUSAL_IDENTIFICATION"
    motor_authority: str = "NONE"
    scheduler_uc_authenticated: bool = False
    m11_authenticated: bool = False


def compare_matched_outcomes(*, prepared: MatchedLivedEpisode,
                             control: MatchedLivedEpisode,
                             preparatory_action_ref: str,
                             completion_action_ref: str,
                             source: MatchedLivedSource) -> MatchedOutcomeContrast:
    """Contrast two claimed complete episodes with ONE differing prior action.

    The context signatures must match and be corroborated by a first-person
    port. This controls only *declared* context and the observed action sequence:
    unobserved confounders, selection, carryover and counterfactual outcomes
    remain unknowable. The contrast is not a TD update, Q value or action.
    """
    if type(prepared) is not MatchedLivedEpisode or type(control) is not MatchedLivedEpisode:
        raise ValueError("exact lived episode types required")
    prepared.validate()
    control.validate()
    _ref(preparatory_action_ref, "preparatory semantic action")
    _ref(completion_action_ref, "completion semantic action")
    if preparatory_action_ref == completion_action_ref:
        raise ValueError("preparation must be distinct from completion")
    if (isinstance(source, type) or
            not callable(getattr(source, "verify_lived", None)) or
            not callable(getattr(source, "verify_complete_episode", None))):
        raise ValueError("complete first-person episode authority required")

    first, second = prepared.events, control.events
    if (prepared.episode_ref == control.episode_ref or
            prepared.context_signature != control.context_signature or
            first[0].life_ref != second[0].life_ref or
            first[0].goal_ref != second[0].goal_ref):
        raise ValueError("episodes are not independently matched")
    if len(first) != len(second):
        raise ValueError("unequal observed opportunity windows")
    if not (first[-1].physical_step < second[0].physical_step or
            second[-1].physical_step < first[0].physical_step):
        raise ValueError("overlapping life experience cannot be paired")
    if (first[-1].action_semantic_ref != completion_action_ref or
            second[-1].action_semantic_ref != completion_action_ref or
            first[-1].lived_delta is None or
            second[-1].lived_delta is None):
        raise ValueError("same completion with both outcomes observed required")

    prior_prepared = tuple(e.action_semantic_ref for e in first[:-1])
    prior_control = tuple(e.action_semantic_ref for e in second[:-1])
    changed = [i for i, (a, b) in enumerate(zip(prior_prepared, prior_control))
               if a != b]
    if (len(changed) != 1 or
            prior_prepared[changed[0]] != preparatory_action_ref or
            prior_prepared.count(preparatory_action_ref) != 1 or
            preparatory_action_ref in prior_control):
        raise ValueError("exactly one preparatory action must differ")
    if (tuple(e.physical_step - first[0].physical_step for e in first) !=
            tuple(e.physical_step - second[0].physical_step for e in second)):
        raise ValueError("nonmatching observed temporal spacing")

    # The old study supplies the existing strict per-event replay/provenance
    # checks. Its temporal credits are deliberately NOT used as contrast data.
    for episode in (prepared, control):
        if source.verify_complete_episode(episode=episode) is not True:
            raise ValueError("complete subjective episode not attested")
        study_delayed_credit(events=episode.events, source=source)

    for field in ("capture_ref", "admission_ref", "outcome_ref"):
        refs = [getattr(e, field) for e in first + second
                if getattr(e, field) is not None]
        if len(refs) != len(set(refs)):
            raise ValueError("paired episodes replay a claimed event")

    net = (sum(e.lived_delta for e in first) -
           sum(e.lived_delta for e in second)
           if all(e.lived_delta is not None for e in first + second) else None)
    position = changed[0]
    return MatchedOutcomeContrast(
        life_ref=first[0].life_ref,
        goal_ref=first[0].goal_ref,
        context_signature=prepared.context_signature,
        prepared_episode_ref=prepared.episode_ref,
        control_episode_ref=control.episode_ref,
        preparatory_action_ref=preparatory_action_ref,
        alternative_action_ref=prior_control[position],
        completion_action_ref=completion_action_ref,
        shared_intervening_actions=tuple(
            name for i, name in enumerate(prior_prepared) if i != position
        ),
        observed_prepared_outcome=first[-1].lived_delta,
        observed_control_outcome=second[-1].lived_delta,
        observed_outcome_difference=first[-1].lived_delta - second[-1].lived_delta,
        observed_net_difference=net,
    )
