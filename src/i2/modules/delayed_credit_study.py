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


@dataclass(frozen=True, slots=True)
class ForecastOpportunity:
    """Current *claimed* subjective context, with no future outcome fields."""

    life_ref: str
    goal_ref: str
    capture_ref: str
    physical_step: int
    context_signature: tuple[str, ...]
    preparatory_action_ref: str
    alternative_action_ref: str
    completion_action_ref: str

    def validate(self) -> None:
        for field in ("life_ref", "goal_ref", "capture_ref",
                      "preparatory_action_ref", "alternative_action_ref",
                      "completion_action_ref"):
            _ref(getattr(self, field), field)
        if type(self.physical_step) is not int or self.physical_step < 0:
            raise ValueError("invalid forecast capture step")
        if (type(self.context_signature) is not tuple or
                not 1 <= len(self.context_signature) <= 16):
            raise ValueError("bounded subjective forecast context required")
        for ref in self.context_signature:
            _ref(ref, "forecast context feature")
        if self.context_signature != tuple(sorted(set(self.context_signature))):
            raise ValueError("noncanonical forecast context")
        if len({self.preparatory_action_ref, self.alternative_action_ref,
                self.completion_action_ref}) != 3:
            raise ValueError("forecast action roles must differ")


class ProspectiveSource(MatchedLivedSource, Protocol):
    """Test port only: a future real owner must journal issuance before outcome."""

    def verify_forecast_capture(self, *, opportunity: ForecastOpportunity) -> bool: ...

    def verify_issued_forecast(self, *, forecast: ProspectiveCreditForecast) -> bool: ...


@dataclass(frozen=True, slots=True)
class ProspectiveCreditForecast:
    """Non-motor readout of old episodes, *before* any held-out outcome."""

    opportunity: ForecastOpportunity
    training_episode_refs: tuple[str, str]
    last_training_step: int
    predicted_outcome_difference: int
    interpretation: str = "OUT_OF_SAMPLE_OBSERVATIONAL_HYPOTHESIS"
    motor_authority: str = "NONE"
    scheduler_uc_authenticated: bool = False
    m11_authenticated: bool = False


@dataclass(frozen=True, slots=True)
class HeldoutForecastScore:
    """Retrospective score; never feeds back into prospective forecast."""

    life_ref: str
    issue_capture_ref: str
    training_episode_refs: tuple[str, str]
    observed_episode_refs: tuple[str, str]
    predicted_outcome_difference: int
    observed_outcome_difference: int
    absolute_error: int
    direction_agreement: bool
    interpretation: str = "HELDOUT_SYNTHETIC_SCORE_NOT_CAUSAL_PROOF"
    motor_authority: str = "NONE"
    scheduler_uc_authenticated: bool = False
    m11_authenticated: bool = False


def project_matched_outcome(*, prepared: MatchedLivedEpisode,
                            control: MatchedLivedEpisode,
                            opportunity: ForecastOpportunity,
                            source: ProspectiveSource) -> ProspectiveCreditForecast:
    """Issue a read-only prediction using ONLY past *claimed lived* episodes.

    It does not choose a candidate, change Q or learn a causal mechanism.
    The issuance port is simulated; no M11 audit/true historical signature.
    """
    if type(opportunity) is not ForecastOpportunity:
        raise ValueError("exact prospective capture required")
    opportunity.validate()
    contrast = compare_matched_outcomes(
        prepared=prepared, control=control,
        preparatory_action_ref=opportunity.preparatory_action_ref,
        completion_action_ref=opportunity.completion_action_ref,
        source=source,
    )
    last = max(prepared.events[-1].physical_step,
               control.events[-1].physical_step)
    if (opportunity.life_ref != contrast.life_ref or
            opportunity.goal_ref != contrast.goal_ref or
            opportunity.context_signature != contrast.context_signature or
            opportunity.alternative_action_ref != contrast.alternative_action_ref):
        raise ValueError("future opportunity not matched to lived training")
    if (opportunity.physical_step <= last or any(
            event.capture_ref == opportunity.capture_ref
            for event in prepared.events + control.events)):
        raise ValueError("forecast cannot observe its own future or replay capture")
    if (not callable(getattr(source, "verify_forecast_capture", None)) or
            source.verify_forecast_capture(opportunity=opportunity) is not True):
        raise ValueError("prospective subjective opportunity not attested")
    return ProspectiveCreditForecast(
        opportunity=opportunity,
        training_episode_refs=(prepared.episode_ref, control.episode_ref),
        last_training_step=last,
        predicted_outcome_difference=contrast.observed_outcome_difference,
    )


def score_heldout_forecast(*, forecast: ProspectiveCreditForecast,
                           prepared: MatchedLivedEpisode,
                           control: MatchedLivedEpisode,
                           source: ProspectiveSource) -> HeldoutForecastScore:
    """Score distinct later observations without reissuing or revising forecast.

    Only an independent, immutable issuance record could substantiate the
    temporal commitment. The injected test port is NOT such a service.
    """
    if type(forecast) is not ProspectiveCreditForecast:
        raise ValueError("exact previously issued forecast required")
    opportunity = forecast.opportunity
    if type(opportunity) is not ForecastOpportunity:
        raise ValueError("missing exact forecast capture")
    opportunity.validate()
    if (forecast.interpretation != "OUT_OF_SAMPLE_OBSERVATIONAL_HYPOTHESIS" or
            forecast.motor_authority != "NONE" or
            forecast.scheduler_uc_authenticated is not False or
            forecast.m11_authenticated is not False or
            type(forecast.predicted_outcome_difference) is not int or
            not -200 <= forecast.predicted_outcome_difference <= 200 or
            type(forecast.last_training_step) is not int or
            forecast.last_training_step >= opportunity.physical_step or
            type(forecast.training_episode_refs) is not tuple or
            len(forecast.training_episode_refs) != 2 or
            len(set(forecast.training_episode_refs)) != 2):
        raise ValueError("invalid nonmotor forecast receipt")
    for ref in forecast.training_episode_refs:
        _ref(ref, "training episode reference")
    if (not callable(getattr(source, "verify_issued_forecast", None)) or
            source.verify_issued_forecast(forecast=forecast) is not True):
        raise ValueError("original prospective issue not authenticated")

    contrast = compare_matched_outcomes(
        prepared=prepared, control=control,
        preparatory_action_ref=opportunity.preparatory_action_ref,
        completion_action_ref=opportunity.completion_action_ref,
        source=source,
    )
    if (contrast.life_ref != opportunity.life_ref or
            contrast.goal_ref != opportunity.goal_ref or
            contrast.context_signature != opportunity.context_signature or
            contrast.alternative_action_ref != opportunity.alternative_action_ref or
            prepared.episode_ref in forecast.training_episode_refs or
            control.episode_ref in forecast.training_episode_refs or
            min(prepared.events[0].physical_step,
                control.events[0].physical_step) <= opportunity.physical_step or
            any(event.capture_ref == opportunity.capture_ref
                for event in prepared.events + control.events)):
        raise ValueError("held-out episode is stale, reused or incompatible")

    predicted = forecast.predicted_outcome_difference
    observed = contrast.observed_outcome_difference
    sign = lambda n: (n > 0) - (n < 0)
    return HeldoutForecastScore(
        life_ref=opportunity.life_ref,
        issue_capture_ref=opportunity.capture_ref,
        training_episode_refs=forecast.training_episode_refs,
        observed_episode_refs=(prepared.episode_ref, control.episode_ref),
        predicted_outcome_difference=predicted,
        observed_outcome_difference=observed,
        absolute_error=abs(predicted - observed),
        direction_agreement=sign(predicted) == sign(observed),
    )


# A *pure study* of personal feedback, not another persistence owner or Q table.
# All functions below refuse motor authority and never read a future outcome
# when issuing a prediction. The ports used by tests remain UNTRUSTED doubles.
MEMORY_MAX_SCORES = 16


@dataclass(frozen=True, slots=True)
class OutcomeFeedbackMemory:
    """Bounded subjective outcome history; no action, Q, or live state owner."""

    life_ref: str
    goal_ref: str
    context_signature: tuple[str, ...]
    preparatory_action_ref: str
    alternative_action_ref: str
    completion_action_ref: str
    last_observed_step: int = -1
    observed_differences: tuple[int, ...] = ()
    used_issue_captures: tuple[str, ...] = ()
    used_episode_refs: tuple[str, ...] = ()
    motor_authority: str = "NONE"
    m11_authenticated: bool = False

    def validate(self) -> None:
        for name in ("life_ref", "goal_ref", "preparatory_action_ref",
                     "alternative_action_ref", "completion_action_ref"):
            _ref(getattr(self, name), name)
        if (len({self.preparatory_action_ref, self.alternative_action_ref,
                 self.completion_action_ref}) != 3 or
                type(self.context_signature) is not tuple or
                not 1 <= len(self.context_signature) <= 16):
            raise ValueError("invalid bounded feedback identity")
        for item in self.context_signature:
            _ref(item, "feedback context")
        if self.context_signature != tuple(sorted(set(self.context_signature))):
            raise ValueError("noncanonical feedback context")
        n = len(self.observed_differences)
        if (type(self.observed_differences) is not tuple or
                type(self.used_issue_captures) is not tuple or
                type(self.used_episode_refs) is not tuple or
                n > MEMORY_MAX_SCORES or
                len(self.used_issue_captures) != n or
                len(self.used_episode_refs) != 2 * n or
                type(self.last_observed_step) is not int or
                self.last_observed_step < -1 or
                (n == 0 and self.last_observed_step != -1) or
                (n > 0 and self.last_observed_step < 0) or
                self.motor_authority != "NONE" or
                self.m11_authenticated is not False):
            raise ValueError("invalid nonmotor feedback snapshot")
        if any(type(value) is not int or not -200 <= value <= 200
               for value in self.observed_differences):
            raise ValueError("invalid observed feedback")
        for ref in self.used_issue_captures + self.used_episode_refs:
            _ref(ref, "consumed feedback evidence")
        if (len(set(self.used_issue_captures)) != n or
                len(set(self.used_episode_refs)) != 2 * n):
            raise ValueError("duplicate feedback evidence")


def _feedback_memory_digest(memory: OutcomeFeedbackMemory) -> str:
    """Bind the FULL immutable H2 snapshot, not merely its mean and length.

    This is a canonical local fingerprint. It is not a signature or M11
    attestation and it cannot prove that the remembered events were lived.
    """
    from dataclasses import asdict
    from hashlib import sha256
    import json

    memory.validate()
    payload = {
        "domain": "i2-h2-feedback-snapshot-v1",
        "state": asdict(memory),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("ascii")
    return "sha256:" + sha256(raw).hexdigest()


def empty_feedback_memory(opportunity: ForecastOpportunity) -> OutcomeFeedbackMemory:
    """Initial state is just the current subjective identity, not knowledge."""
    if type(opportunity) is not ForecastOpportunity:
        raise ValueError("exact forecast opportunity required")
    opportunity.validate()
    return OutcomeFeedbackMemory(
        opportunity.life_ref, opportunity.goal_ref, opportunity.context_signature,
        opportunity.preparatory_action_ref, opportunity.alternative_action_ref,
        opportunity.completion_action_ref,
    )


class FeedbackSource(ProspectiveSource, Protocol):
    def verify_feedback_issue(self, *, readout: FeedbackReadout) -> bool: ...


@dataclass(frozen=True, slots=True)
class FeedbackReadout:
    """Past-only readout bound to exact memory contents, without motor rights.

    memory_digest is a local non-secret fingerprint, not an M11 signature.
    """

    baseline: ProspectiveCreditForecast
    memory_version: int
    predicted_outcome_difference: Fraction
    memory_digest: str
    interpretation: str = "PAST_ONLY_FEEDBACK_HYPOTHESIS"
    motor_authority: str = "NONE"
    scheduler_uc_authenticated: bool = False
    m11_authenticated: bool = False


@dataclass(frozen=True, slots=True)
class FeedbackUpdate:
    """A scored *claimed* observation and its immutable revised memory."""

    new_memory: OutcomeFeedbackMemory
    heldout_score: HeldoutForecastScore
    predicted_outcome_difference: Fraction
    absolute_error: Fraction
    direction_agreement: bool
    interpretation: str = "SYNTHETIC_ADAPTATION_NOT_CAUSAL_OR_MOTOR_PROOF"
    motor_authority: str = "NONE"


def read_feedback(*, memory: OutcomeFeedbackMemory,
                  forecast: ProspectiveCreditForecast,
                  source: FeedbackSource) -> FeedbackReadout:
    """Read from PREVIOUS observations; the future heldout pair is not an input."""
    if type(memory) is not OutcomeFeedbackMemory or type(forecast) is not ProspectiveCreditForecast:
        raise ValueError("exact feedback memory and baseline required")
    memory.validate()
    op = forecast.opportunity
    if type(op) is not ForecastOpportunity:
        raise ValueError("exact prospective opportunity required")
    op.validate()
    if ((op.life_ref, op.goal_ref, op.context_signature,
         op.preparatory_action_ref, op.alternative_action_ref,
         op.completion_action_ref) !=
        (memory.life_ref, memory.goal_ref, memory.context_signature,
         memory.preparatory_action_ref, memory.alternative_action_ref,
         memory.completion_action_ref)):
        raise ValueError("feedback belongs to a different context or individual")
    if (forecast.interpretation != "OUT_OF_SAMPLE_OBSERVATIONAL_HYPOTHESIS" or
            forecast.motor_authority != "NONE" or
            forecast.scheduler_uc_authenticated is not False or
            forecast.m11_authenticated is not False or
            type(forecast.predicted_outcome_difference) is not int or
            not -200 <= forecast.predicted_outcome_difference <= 200 or
            type(forecast.last_training_step) is not int or
            forecast.last_training_step >= op.physical_step or
            type(forecast.training_episode_refs) is not tuple or
            len(forecast.training_episode_refs) != 2 or
            len(set(forecast.training_episode_refs)) != 2 or
            op.physical_step <= memory.last_observed_step or
            op.capture_ref in memory.used_issue_captures or
            len(memory.observed_differences) >= MEMORY_MAX_SCORES):
        raise ValueError("stale, full or unauthorized forecast")
    for ref in forecast.training_episode_refs:
        _ref(ref, "training episode")
    if (not callable(getattr(source, "verify_issued_forecast", None)) or
            source.verify_issued_forecast(forecast=forecast) is not True):
        raise ValueError("unverified original forecast")

    # A deliberately simple empirical mean, not causal inference or TD/Q:
    # no observation -> historic matched contrast; subsequent observations
    # -> exact arithmetic average of heldout outcomes already witnessed.
    values = memory.observed_differences
    estimate = (Fraction(sum(values), len(values)) if values else
                Fraction(forecast.predicted_outcome_difference))
    return FeedbackReadout(
        forecast, len(values), estimate, _feedback_memory_digest(memory)
    )


def learn_from_feedback(*, memory: OutcomeFeedbackMemory,
                        readout: FeedbackReadout,
                        prepared: MatchedLivedEpisode,
                        control: MatchedLivedEpisode,
                        source: FeedbackSource) -> FeedbackUpdate:
    """Validate a later heldout result before revising the immutable snapshot."""
    if type(readout) is not FeedbackReadout:
        raise ValueError("exact readout required")
    expected = read_feedback(memory=memory, forecast=readout.baseline, source=source)
    if readout != expected:
        raise ValueError("changed or reused feedback prediction")
    if (not callable(getattr(source, "verify_feedback_issue", None)) or
            source.verify_feedback_issue(readout=readout) is not True):
        raise ValueError("feedback readout was not independently issued")

    score = score_heldout_forecast(
        forecast=readout.baseline, prepared=prepared, control=control, source=source)
    if (type(prepared) is not MatchedLivedEpisode or
            type(control) is not MatchedLivedEpisode):
        raise ValueError("exact heldout episodes required")
    first_test_step = min(prepared.events[0].physical_step,
                          control.events[0].physical_step)
    if (first_test_step <= memory.last_observed_step or
            score.issue_capture_ref in memory.used_issue_captures or
            any(ref in memory.used_episode_refs for ref in score.observed_episode_refs)):
        raise ValueError("already observed or replayed outcome")
    last = max(prepared.events[-1].physical_step,
               control.events[-1].physical_step)
    revised = OutcomeFeedbackMemory(
        life_ref=memory.life_ref, goal_ref=memory.goal_ref,
        context_signature=memory.context_signature,
        preparatory_action_ref=memory.preparatory_action_ref,
        alternative_action_ref=memory.alternative_action_ref,
        completion_action_ref=memory.completion_action_ref,
        last_observed_step=last,
        observed_differences=memory.observed_differences +
                             (score.observed_outcome_difference,),
        used_issue_captures=memory.used_issue_captures + (score.issue_capture_ref,),
        used_episode_refs=memory.used_episode_refs + score.observed_episode_refs,
    )
    revised.validate()
    predicted, actual = readout.predicted_outcome_difference, score.observed_outcome_difference
    sign = lambda value: (value > 0) - (value < 0)
    return FeedbackUpdate(
        new_memory=revised, heldout_score=score,
        predicted_outcome_difference=predicted,
        absolute_error=abs(predicted - actual),
        direction_agreement=sign(predicted) == sign(actual),
    )


class PaidFeedbackValuationPort:
    """G2-only bridge from a past-only H2 forecast to *paid* Competition values.

    Competition's existing ledger MUST call this after a full batch debit.
    The computed feedback readout also requires an issuance assertion before
    affecting valuations; a historical forecast receipt alone is not enough.
    This port does not own UC, store memory, authenticate M11 or admit action.
    Its source and baseline are test-injected, not physiological authorities.
    """

    def __init__(self, *, claim: object, forecast: ProspectiveCreditForecast,
                 memory: OutcomeFeedbackMemory, source: FeedbackSource,
                 baseline: object) -> None:
        from .intention_ingress import ObservationClaim
        if type(claim) is not ObservationClaim:
            raise ValueError("exact current subjective claim required")
        claim.validate()
        if type(forecast) is not ProspectiveCreditForecast:
            raise ValueError("exact H2 forecast required")
        if type(memory) is not OutcomeFeedbackMemory:
            raise ValueError("exact H2 feedback memory required")
        if (not callable(getattr(source, "verify_issued_forecast", None)) or
                not callable(getattr(source, "verify_forecast_capture", None)) or
                not callable(getattr(source, "verify_feedback_issue", None))):
            raise ValueError("first-person forecast and feedback issuance verification required")
        if not callable(getattr(baseline, "evaluate_batch", None)):
            raise ValueError("independent full-frame baseline evaluator required")
        self.claim = claim
        self.forecast = forecast
        self.memory = memory
        self.source = source
        self.baseline = baseline

    def evaluate_batch(self, *, frame: object,
                       receipts: tuple[object, ...]) -> tuple[object, ...]:
        """Fail closed after the *existing* full-frame UC charge, never before."""
        from hashlib import sha256
        import json
        from .competition_preview import (
            CompetitionReceipt, MAX_VALUE_MAGNITUDE, SubjectiveValuation, _frame,
        )
        frame = _frame(frame)
        claim = self.claim
        op = self.forecast.opportunity
        if (type(op) is not ForecastOpportunity or
                frame.life_ref != claim.life_ref or
                frame.life_ref != op.life_ref or
                frame.capture_ref != claim.capture.ref or
                frame.capture_ref != op.capture_ref or
                frame.physical_step != claim.capture.step or
                frame.physical_step != op.physical_step or
                frame.claim_digest != claim.digest() or
                claim.capture.goal_ref != op.goal_ref):
            raise ValueError("H2 forecast not bound to paid current capture")
        if (type(receipts) is not tuple or len(receipts) != len(frame.candidates) or
                any(type(r) is not CompetitionReceipt for r in receipts)):
            raise ValueError("full paid Competition receipts required")
        names = tuple(candidate.semantic_ref for candidate in frame.candidates)
        if (op.preparatory_action_ref not in names or
                op.alternative_action_ref not in names):
            raise ValueError("H2 options must both be currently perceivable")
        if self.source.verify_forecast_capture(opportunity=op) is not True:
            raise ValueError("current first-person opportunity not attested")
        # No cognitive feedback lookup is performed until Competition has
        # debited every visible candidate, including unaffected alternatives.
        readout = read_feedback(memory=self.memory, forecast=self.forecast,
                                source=self.source)
        # The historical forecast alone does not attest the derived feedback
        # readout. Do not let an unissued or altered calibration affect advice.
        # This G2 port is a synthetic double, not a durable M11 issuance.
        if self.source.verify_feedback_issue(readout=readout) is not True:
            raise ValueError("paid H2 feedback readout not attested as issued")
        diff = readout.predicted_outcome_difference
        if diff.denominator != 1:
            # The motor preview accepts only integer values; choosing a
            # rounding or quantization rule here would silently add policy.
            raise ValueError("fractional H2 value lacks calibrated conversion")
        difference = diff.numerator
        if abs(difference) > MAX_VALUE_MAGNITUDE:
            raise ValueError("H2 predicted contrast out of bounds")
        baseline = self.baseline.evaluate_batch(frame=frame, receipts=receipts)
        if type(baseline) is not tuple or len(baseline) != len(frame.candidates):
            raise ValueError("complete baseline valuations required")
        valuations: list[SubjectiveValuation] = []
        for candidate, receipt, prior in zip(frame.candidates, receipts, baseline):
            receipt.validate()
            if (receipt.life_ref != frame.life_ref or
                    receipt.frame_ref != frame.frame_ref or
                    receipt.claim_digest != frame.claim_digest or
                    receipt.candidate_ref != candidate.candidate_ref):
                raise ValueError("foreign or incomplete paid candidate receipt")
            if type(prior) is not SubjectiveValuation:
                raise ValueError("baseline valuation must be exact")
            prior.validate()
            if (prior.candidate_ref != candidate.candidate_ref or
                    prior.receipt_ref != receipt.ref):
                raise ValueError("baseline valuation not bound to paid candidate")
            adjustment = (max(0, difference) if
                          candidate.semantic_ref == op.preparatory_action_ref else
                          max(0, -difference) if
                          candidate.semantic_ref == op.alternative_action_ref else 0)
            updated = prior.value + adjustment
            if abs(updated) > MAX_VALUE_MAGNITUDE:
                raise ValueError("feedback cannot overflow bounded valuations")
            # Correlation only, NOT an M11 signature or independent evidence.
            bound = json.dumps(
                [frame.claim_digest, candidate.candidate_ref, receipt.ref,
                 prior.evidence_ref, readout.memory_version, difference,
                 readout.memory_digest, self.forecast.training_episode_refs],
                sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            ).encode("ascii")
            evidence = "feedback:synthetic:" + sha256(bound).hexdigest()
            valuations.append(SubjectiveValuation(
                candidate.candidate_ref, receipt.ref, evidence, updated,
            ))
        return tuple(valuations)


# Physical evidence guard for later I2 design: a *read-only* correspondence
# check. No M11 provider is implemented and it NEVER admits motor execution.
# This generation label is a local compatibility fence, not an attestation.
PHYSICAL_CLAIM_GENERATION = "I2"
@dataclass(frozen=True, slots=True)
class PhysicalEffectClaim:
    life_ref: str
    generation_ref: str
    admission_ref: str
    command_ref: str
    before_step: int
    after_step: int
    before_state_ref: str
    after_state_ref: str
    committed_event_ref: str
    terminal: bool

    def validate(self) -> None:
        for name in ("life_ref", "generation_ref", "admission_ref",
                     "command_ref", "before_state_ref", "after_state_ref",
                     "committed_event_ref"):
            _ref(getattr(self, name), name)
        if (type(self.before_step) is not int or
                type(self.after_step) is not int or
                self.before_step < 0 or self.after_step != self.before_step + 1 or
                type(self.terminal) is not bool):
            raise ValueError("invalid committed physical claim chronology")


class PhysicalEffectAuthority(Protocol):
    def verify_committed_effect(self, *, effect: PhysicalEffectClaim) -> bool: ...
    def verify_subjective_after(self, *, event: ClaimedLivedStep,
                                effect: PhysicalEffectClaim) -> bool: ...


@dataclass(frozen=True, slots=True)
class LivedPhysicalCorrespondence:
    life_ref: str
    generation_ref: str
    physical_step: int
    admission_ref: str
    committed_event_ref: str
    subjective_capture_ref: str
    observed_delta: int
    interpretation: str = "PHYSICAL_CORRESPONDENCE_CLAIM_ONLY"
    motor_authority: str = "NONE"
    m11_authenticated: bool = False


def verify_lived_physical_correspondence(
        *, effect: PhysicalEffectClaim, event: ClaimedLivedStep,
        authority: PhysicalEffectAuthority) -> LivedPhysicalCorrespondence:
    """Require distinct committed-physics and post-effect subjective attestations.

    This verifies consistency of claims through an injected provider. A mock
    provider cannot establish the truth of a body, M11 or physical causality.
    Terminal effects must be inspected elsewhere, never learned from here.
    Unobserved results cannot be turned into zero-valued lived credit.
    """
    if type(effect) is not PhysicalEffectClaim or type(event) is not ClaimedLivedStep:
        raise ValueError("exact physical and first-person claims required")
    effect.validate()
    event.validate()
    if (effect.generation_ref != PHYSICAL_CLAIM_GENERATION or
            effect.life_ref != event.life_ref or
            effect.after_step != event.physical_step or
            effect.admission_ref != event.admission_ref or
            effect.command_ref != event.action_semantic_ref or
            event.capture_ref == effect.committed_event_ref or
            event.lived_delta is None or event.outcome_ref is None or
            effect.terminal):
        raise ValueError("foreign, terminal or mismatched physical effect")
    if (isinstance(authority, type) or
            not callable(getattr(authority, "verify_committed_effect", None)) or
            not callable(getattr(authority, "verify_subjective_after", None))):
        raise ValueError("independent committed physical authority required")
    if authority.verify_committed_effect(effect=effect) is not True:
        raise ValueError("committed physical effect not attested")
    if authority.verify_subjective_after(event=event, effect=effect) is not True:
        raise ValueError("post-effect subjective observation not attested")
    return LivedPhysicalCorrespondence(
        effect.life_ref, effect.generation_ref, effect.after_step,
        effect.admission_ref, effect.committed_event_ref,
        event.capture_ref, event.lived_delta,
    )


@dataclass(frozen=True, slots=True)
class PhysicallyLinkedCredit:
    """An observational research result, never a motor or M11 credential."""

    study: DelayedCreditStudy
    correspondences: tuple[LivedPhysicalCorrespondence, ...]
    interpretation: str = "SYNTHETIC_LINKED_ASSOCIATION_NOT_CAUSAL_PROOF"
    motor_authority: str = "NONE"
    m11_authenticated: bool = False


def study_physically_linked_credit(
        *, events: tuple[ClaimedLivedStep, ...],
        effects: tuple[PhysicalEffectClaim, ...],
        authority: PhysicalEffectAuthority,
        horizon: int = 8, decay_numerator: int = 1,
        decay_denominator: int = 2) -> PhysicallyLinkedCredit:
    """Refuse the ENTIRE study unless every claimed transition is linked.

    The one-to-one order follows chronological physical steps. The after
    state of an effect must be the next before state; duplicate commits,
    admissions, broken state links and missing observations fail closed.
    Equal or revisited physical states are allowed: an applied action may be
    ineffective, or may return the body to an earlier state. Only the real
    commit authority could prove these claims; this remains a G2 test port.
    """
    if (type(events) is not tuple or type(effects) is not tuple or
            not events or len(events) != len(effects) or len(events) > 128):
        raise ValueError("one physical effect required for every lived step")
    if (isinstance(authority, type) or
            not callable(getattr(authority, "verify_committed_effect", None)) or
            not callable(getattr(authority, "verify_subjective_after", None))):
        raise ValueError("physical proof source required")

    class _AlreadyLinked:
        def verify_lived(self, *, event: ClaimedLivedStep) -> bool:
            # Correspondence has already checked this exact tuple; never
            # consult a different mock authority or a world oracle.
            return True

    correspondences: list[LivedPhysicalCorrespondence] = []
    previous: PhysicalEffectClaim | None = None
    used_commit_refs: set[str] = set()
    used_admissions: set[str] = set()
    for event, effect in zip(events, effects):
        verified = verify_lived_physical_correspondence(
            effect=effect, event=event, authority=authority)
        if effect.committed_event_ref in used_commit_refs or effect.admission_ref in used_admissions:
            raise ValueError("replayed physical event or admission")
        if previous is not None and (
                effect.life_ref != previous.life_ref or
                effect.generation_ref != previous.generation_ref or
                effect.before_step != previous.after_step or
                effect.before_state_ref != previous.after_state_ref):
            raise ValueError("disconnected physical state sequence")
        used_commit_refs.add(effect.committed_event_ref)
        used_admissions.add(effect.admission_ref)
        correspondences.append(verified)
        previous = effect
    result = study_delayed_credit(
        events=events, source=_AlreadyLinked(), horizon=horizon,
        decay_numerator=decay_numerator, decay_denominator=decay_denominator)
    return PhysicallyLinkedCredit(result, tuple(correspondences))
