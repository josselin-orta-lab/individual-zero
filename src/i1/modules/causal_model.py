"""Stage-9 canonical causal knowledge, initial DC-05 safety-status slice.

Source of truth: mvp-specification-v1.2.1 (EN), §§5.3, 9.3-9.4,
13.1-13.3, DC-05, P-35/P-36, INV-01/03/25/27/33.

The Causal Model is the single owner of every learned safety status. A status
change is published only at the end of a cycle; Action Control reads through
a read-only service, never a duplicated fact table.

This first slice deliberately DOES NOT infer causal establishment or write
simulator corrections. Full intervention lifecycle, test proposals, and
attribution are separate Stage-9 work items.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from json import dumps
from math import isfinite
from typing import Iterable, Mapping, Sequence

from .action_control import StaticSafetyFacts
from .causal_corrections import (
    LivedNumericOutcome, NumericPredictionCorrection, decode_lived_numeric_outcome,
)
from .causal_lifecycle import (CausalObservation, CausalHypothesisReview, CausalIntervention, CausalInferenceChange, AgencyEvidence, agency_evidence_from_autobiography, decode_agency_evidence, decode_observation, decode_review, decode_intervention, serialize_value, CausalTestTarget)


# The existing, versioned MVP veto policy permits exactly these categories.
# Do not add any silent safety category while the specification is v1.2.1.
SAFETY_PREDICATES = frozenset({
    "toxic_item", "lethal_zone", "protected_invariant_violation",
})
CAUSAL_STATUSES = frozenset({
    "aucun", "correlation_observee", "hypothese_causale",
    "testee_par_intervention", "etablie",
})
SAFETY_STATUSES = frozenset({"aucun", "etabli_pour_securite"})


def _verify_shared_observation_provenance(
    rows: Iterable[CausalObservation],
) -> None:
    """One physical transition keeps its episode and world step across rules.

    One transition may inform several different contingencies. Its causality,
    candidate subject, and contextual controls can differ by hypothesis, but
    the originating closed Memory episode and world step cannot. Same-rule
    physical aliases are checked separately with their full factual content.
    """
    sources: dict[str, tuple[str, int, str]] = {}
    for row in rows:
        prior = sources.get(row.observation_ref)
        if prior is None:
            sources[row.observation_ref] = (
                row.episode_ref, row.observed_step, row.contingency_ref,
            )
        elif (
            prior[2] != row.contingency_ref
            and prior[:2] != (row.episode_ref, row.observed_step)
        ):
            raise ValueError(
                "conflicting cross-contingency physical observation provenance"
            )


def _ambiguous_closed_projection_steps(
    events: Sequence[Mapping[str, object]],
) -> set[int]:
    """Find physical steps with duplicate referenced autobiographical IDs.

    A repeated source ID cannot masquerade as an unrelated event kind and
    escape the physical command/transition cardinality checks. Do not
    poison independent steps or projections outside the closed episode.
    """
    seen: dict[str, object] = {}
    ambiguous: set[int] = set()
    for event in events:
        ref = event.get("event_id")
        if not isinstance(ref, str):
            continue
        step = event.get("t_monde")
        if ref in seen:
            for candidate in (seen[ref], step):
                if type(candidate) is int and candidate >= 1:
                    ambiguous.add(candidate)
        else:
            seen[ref] = step
    return ambiguous


@dataclass(frozen=True, slots=True)
class CausalModelConfig:
    version: str
    n1: int
    n2: int
    n_sec: int
    m_sec: int
    # Non-safety causal predicates must be explicitly registered and versioned.
    # Existing veto categories remain closed and unchanged (DC-05).
    causal_predicates: tuple[str, ...] = ()
    # Explicit, versioned physical comparison pairs (treatment, observed
    # different food). Empty by default: no automatic baseline is inferred.
    food_control_pairs: tuple[tuple[str, str], ...] = ()
    # Stage-9 preregistered, currently supported non-harmful test primitives.
    # No automatic action derivation from an arbitrary predicate or belief.
    # (predicate, subject_ref, primitive); P-48 motivation is not fabricated.
    safe_test_actions: tuple[tuple[str, str, str], ...] = ()

    def validate(self) -> None:
        if not self.version or any(
            not isinstance(n, int) or isinstance(n, bool) or n < 1
            for n in (self.n1, self.n2, self.n_sec, self.m_sec)
        ):
            raise ValueError("invalid versioned P-35/P-36 thresholds")
        if (any(not isinstance(p, str) or not p.strip() for p in self.causal_predicates)
            or len(set(self.causal_predicates)) != len(self.causal_predicates)):
            raise ValueError("invalid versioned causal predicate registry")
        if (
            any(
                not isinstance(pair, (tuple, list)) or len(pair) != 2
                or pair[0] not in {"berry_a", "berry_b"}
                or pair[1] not in {"berry_a", "berry_b"}
                or pair[0] == pair[1]
                for pair in self.food_control_pairs
            )
            or len({pair[0] for pair in self.food_control_pairs})
                != len(self.food_control_pairs)
        ):
            raise ValueError("invalid preregistered physically observed food controls")
        if (
            any(
                not isinstance(row, (tuple, list)) or len(row) != 3
                or row[0] not in self.causal_predicates
                or row[1] != "water"
                or row[2] != "boire"
                for row in self.safe_test_actions
            )
            or len({(row[0], row[1]) for row in self.safe_test_actions})
               != len(self.safe_test_actions)
        ):
            raise ValueError("unsupported or duplicate preregistered causal test action")


@dataclass(frozen=True, slots=True)
class SafetyEvidence:
    identifier: str
    contingency_ref: str
    predicate: str
    subject_ref: str
    context_signature: str
    episode_ref: str
    observation_ref: str
    emission_step: int
    observation_step: int
    harm_observed: bool
    source: str
    independent_episode: bool
    comparable_context: bool
    alternative_cause_sufficient: bool
    exposure_motivated_independently: bool
    # A lived food injury may be a real association while its physical cause
    # remains underdetermined. Only dc05_admissible rows may enter the safety
    # credit ledger; ambiguous rows stay first-person observations only.
    epistemic_status: str = "dc05_admissible"
    oracle_derived: bool = False
    rollback_cancelled: bool = False
    counterfactual: bool = False

    def validate(self) -> None:
        if self.predicate not in SAFETY_PREDICATES:
            raise ValueError("predicate absent from the normative veto policy")
        if not all((
            self.identifier, self.contingency_ref, self.subject_ref,
            self.context_signature, self.episode_ref, self.observation_ref,
        )):
            raise ValueError("missing DC-05 physical evidence provenance")
        if self.predicate == "lethal_zone":
            parts = self.subject_ref.split(",")
            if len(parts) != 2:
                raise ValueError("lethal-zone subject must be an x,y position")
            try:
                tuple(int(part) for part in parts)
            except ValueError as exc:
                raise ValueError("invalid lethal-zone position") from exc
        if self.epistemic_status not in {
            "dc05_admissible", "ambiguous_food_association",
        }:
            raise ValueError("unknown DC-05 epistemic admission status")
        if self.oracle_derived or self.rollback_cancelled or self.counterfactual:
            raise ValueError("forbidden-or-cancelled provenance cannot enter Causal Model")
        if not (
            self.source == "monde"
            and self.observation_step > self.emission_step >= 0
            and self.independent_episode
            and self.comparable_context
            and not self.alternative_cause_sufficient
            and self.exposure_motivated_independently
        ):
            raise ValueError("DC-05 requires independent lived harm/no-harm episodes")


@dataclass(frozen=True, slots=True)
class LivedFoodExposure:
    """Causal Model's independent-motivation reference to an applied action.

    The source is a successful, goal-motivated Action Control dispatch. It is
    NOT evidence by itself: it must be paired with a later Perception capture
    and matching events in a Memory-closed DC-09 autobiographical episode.
    """
    t_monde: int
    resource_kind: str
    option_ref: str
    motive_ref: str
    integrity_before: float
    body_before: tuple[tuple[str, float], ...] | None = None
    position_before: tuple[int, int] | None = None
    state_before_digest: str | None = None
    # Obtained from the actual PerceptualCapture at the admitted food step,
    # never inferred from WorldBody's hidden creature_damage field.
    visible_creature_at_exposure: bool = False
    observed_step: int | None = None
    integrity_observed: float | None = None

    def validate(self) -> None:
        if (self.t_monde < 1 or self.resource_kind not in ("berry_a", "berry_b")
            or not self.option_ref or not self.motive_ref
            or not isfinite(self.integrity_before)
            or not 0 <= self.integrity_before <= 100):
            raise ValueError("invalid motivated food exposure")
        if type(self.visible_creature_at_exposure) is not bool:
            raise ValueError("food competing-cause observation must be boolean")
        if (self.body_before is None) != (self.position_before is None):
            raise ValueError("partial pre-action physical context")
        if self.body_before is not None:
            from .causal_corrections import BODY_VARIABLES
            body = dict(self.body_before)
            if len(self.body_before) != 4 or set(body) != BODY_VARIABLES:
                raise ValueError("invalid complete observed pre-action body")
            if (any(
                isinstance(v, bool) or not isinstance(v, (int, float))
                or not isfinite(v) or not 0 <= v <= 100
                for v in body.values()
            ) or body["integrity"] != self.integrity_before):
                raise ValueError("inconsistent pre-action physical telemetry")
            if (len(self.position_before) != 2
                or any(type(v) is not int for v in self.position_before)):
                raise ValueError("invalid pre-action observable position")
        if self.state_before_digest is not None and (
            self.body_before is None or self.position_before is None
            or len(self.state_before_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.state_before_digest)
        ):
            raise ValueError("invalid accessible pre-action state digest")
        if self.observed_step is None:
            if self.integrity_observed is not None:
                raise ValueError("unpaired observation")
        elif (self.observed_step != self.t_monde + 1
              or self.integrity_observed is None
              or not isfinite(self.integrity_observed)
              or not 0 <= self.integrity_observed <= 100):
            raise ValueError("a lived exposure needs next-step physical telemetry")


@dataclass(frozen=True, slots=True)
class LivedAmbientIntegrityControl:
    """Observed no-food wait, not an Oracle declaration of environmental safety.

    A control is eligible only after its actual command and transition appear
    in a closed DC-09 memory episode, followed by matching Perception
    telemetry. A clean wait at the same position on the immediately
    preceding world step is *limited* evidence against a persistent ambient
    injury. It cannot prove a time-varying hazard absent.
    """

    t_monde: int
    option_ref: str
    position: tuple[int, int]
    integrity_before: float
    observed_step: int | None = None
    integrity_observed: float | None = None
    episode_ref: str | None = None
    command_ref: str | None = None
    transition_ref: str | None = None

    def validate(self) -> None:
        if (
            type(self.t_monde) is not int or self.t_monde < 1
            or not isinstance(self.option_ref, str) or not self.option_ref
            or not isinstance(self.position, (tuple, list))
            or len(self.position) != 2
            or any(type(v) is not int for v in self.position)
            or type(self.integrity_before) not in (int, float)
            or not isfinite(self.integrity_before)
            or not 0 <= self.integrity_before <= 100
        ):
            raise ValueError("invalid lived ambient control context")
        if (self.observed_step is None) != (self.integrity_observed is None):
            raise ValueError("incomplete ambient control observation")
        if self.observed_step is not None and (
            type(self.observed_step) is not int
            or self.observed_step != self.t_monde + 1
            or type(self.integrity_observed) not in (int, float)
            or not isfinite(self.integrity_observed)
            or not 0 <= self.integrity_observed <= 100
        ):
            raise ValueError("ambient control must have next-step Perception telemetry")
        refs = (self.episode_ref, self.command_ref, self.transition_ref)
        if any(ref is not None for ref in refs):
            if (
                any(not isinstance(ref, str) or not ref for ref in refs)
                or self.command_ref == self.transition_ref
                or self.observed_step is None
                or self.integrity_observed != self.integrity_before
            ):
                raise ValueError("ambient control lacks independently lived proof")


@dataclass(frozen=True, slots=True)
class LivedHydrationExposure:
    """Passive, independently selected water action; no hypothesis needed.

    The two labels 'boire' and 'attendre' are OBSERVED controls only, never
    commands generated to satisfy n1. DC-09 closure and next Perception are
    independently required before this becomes a CausalObservation.
    """
    t_monde: int
    primitive: str
    option_ref: str
    position: tuple[int, int]
    water_before: float
    observed_step: int | None = None
    water_observed: float | None = None

    def validate(self) -> None:
        if (
            type(self.t_monde) is not int or self.t_monde < 1
            or self.primitive not in {"boire", "attendre"}
            or not isinstance(self.option_ref, str) or not self.option_ref
            or not isinstance(self.position, (tuple, list))
            or len(self.position) != 2
            or any(type(v) is not int for v in self.position)
            or isinstance(self.water_before, bool)
            or not isinstance(self.water_before, (float, int))
            or not isfinite(self.water_before)
            or not 0 <= self.water_before < 100.0
        ):
            raise ValueError("invalid lived hydration observation source")
        if self.observed_step is None:
            if self.water_observed is not None:
                raise ValueError("unpaired water observation")
        elif (
            self.observed_step != self.t_monde + 1
            or self.water_observed is None
            or isinstance(self.water_observed, bool)
            or not isinstance(self.water_observed, (float, int))
            or not isfinite(self.water_observed)
            or not 0 <= self.water_observed <= 100
        ):
            raise ValueError("invalid next-step water Perception")


@dataclass(frozen=True, slots=True)
class LivedCausalAction:
    """Applied benign test or independently motivated action awaiting evidence.

    Sending a command is not an intervention credit. A later accessible
    Perception capture, a closed DC-09 physical action and a separately
    published P-47 comparison must all agree before CausalIntervention exists.
    """
    identifier: str
    contingency_ref: str
    contingency_version: int
    option_ref: str
    motive_type: str
    sent_t_monde: int
    position: tuple[int, int]
    water_before: float
    observed_t_monde: int | None = None
    water_observed: float | None = None
    command_event_ref: str | None = None
    transition_event_ref: str | None = None
    physical_episode_ref: str | None = None

    def validate(self) -> None:
        if (
            not self.identifier or not self.contingency_ref
            or not self.option_ref
            or self.motive_type not in {"active_goal", "test_causal"}
            or type(self.contingency_version) is not int
            or self.contingency_version < 1
            or type(self.sent_t_monde) is not int or self.sent_t_monde < 1
            or not isinstance(self.position, (tuple, list))
            or len(self.position) != 2
            or any(type(x) is not int for x in self.position)
            or isinstance(self.water_before, bool)
            or not isinstance(self.water_before, (int, float))
            or not isfinite(self.water_before)
            or not 0 <= self.water_before < 100
        ):
            raise ValueError("invalid pre-action causal test provenance")
        if self.observed_t_monde is None:
            if self.water_observed is not None:
                raise ValueError("unpaired causal test capture")
        elif (
            self.observed_t_monde != self.sent_t_monde + 1
            or self.water_observed is None
            or isinstance(self.water_observed, bool)
            or not isinstance(self.water_observed, (int, float))
            or not isfinite(self.water_observed)
            or not 0 <= self.water_observed <= 100
        ):
            raise ValueError("invalid causal test follow-up capture")
        refs = (
            self.command_event_ref, self.transition_event_ref,
            self.physical_episode_ref,
        )
        if any(v is not None for v in refs) and (
            self.observed_t_monde is None
            or any(not isinstance(v, str) or not v for v in refs)
        ):
            raise ValueError("partial closed Memory action provenance")


@dataclass(frozen=True, slots=True)
class CanonicalContingency:
    ref: str
    version: int
    predicate: str
    subject_ref: str
    context_signature: str
    causal_status: str
    safety_status: str
    evidence_refs: tuple[str, ...]
    harmful_episodes: tuple[str, ...]
    harmless_episodes: tuple[str, ...]
    innate: bool = False

    def validate(self) -> None:
        if (
            not self.ref or self.version < 1
            or not isinstance(self.predicate, str) or not self.predicate.strip()
            or (self.predicate not in SAFETY_PREDICATES and self.safety_status != "aucun")
            or self.causal_status not in CAUSAL_STATUSES
            or self.safety_status not in SAFETY_STATUSES
        ):
            raise ValueError("invalid canonical contingency")


@dataclass(frozen=True, slots=True)
class CausalStatusChange:
    contingency_ref: str
    before: str
    after: str
    version: int
    evidence_ref: str
    episode_ref: str


class CausalModel:
    """Sole canonical writer; pending evidence is invisible until publication."""

    owner_id = "causal_model"

    def __init__(self, config: CausalModelConfig) -> None:
        config.validate()
        self.config = config
        self._published: dict[str, CanonicalContingency] = {}
        self._pending: list[SafetyEvidence] = []
        self._seen_ids: set[str] = set()
        self._admitted_safety_evidence: list[SafetyEvidence] = []
        self._credited_episodes: set[tuple[str, str]] = set()
        self._credited_observations: set[tuple[str, str]] = set()
        self._version = 0
        self._lived_food_exposures: dict[int, LivedFoodExposure] = {}
        self._lived_ambient_integrity_controls: dict[int, LivedAmbientIntegrityControl] = {}
        self._lived_hydration_exposures: dict[int, LivedHydrationExposure] = {}
        # Exact DC-09 physical command/transition references, not oracle facts.
        self._hydration_observation_witnesses: dict[str, tuple[str, str]] = {}
        self._lived_causal_actions: dict[str, LivedCausalAction] = {}
        # Immutable closed-episode witnesses retained when a lived action is
        # converted into a pending intervention. Canonical phase-5 admission
        # checks these instead of trusting a CausalIntervention declaration.
        self._causal_action_witnesses: dict[str, LivedCausalAction] = {}
        self._causal_observations: dict[str, CausalObservation] = {}
        self._pending_causal_observations: list[CausalObservation] = []
        self._pending_causal_reviews: list[CausalHypothesisReview] = []
        self._pending_causal_interventions: list[CausalIntervention] = []
        self._causal_interventions: dict[str, CausalIntervention] = {}
        self._causal_reviews: set[str] = set()
        # Retain the precise physical samples supporting the first P-35
        # promotion; subsequent contradictory observations cannot erase the
        # original above-base-rate witness from the causal audit trail.
        self._causal_correlation_witnesses: dict[
            str, tuple[tuple[str, ...], tuple[str, ...]]
        ] = {}
        self._causal_review_proofs: dict[str, CausalHypothesisReview] = {}
        self._causal_credits: set[tuple[str, str, str]] = set()
        # Failure boundaries are causal state: stale successful trials must
        # not re-establish a refuted contingency without fresh contexts.
        self._causal_revision_boundaries: dict[str, tuple[int, str]] = {}
        self._agency_evidence: dict[str, AgencyEvidence] = {}
        self._pending_agency_evidence: list[AgencyEvidence] = []
        self._numeric_witnesses: dict[str, LivedNumericOutcome] = {}
        self._pending_numeric_witnesses: list[LivedNumericOutcome] = []

    @property
    def version(self) -> int:
        return self._version

    def contingencies(
        self, *, context_signature: str | None = None,
        status: str | None = None,
    ) -> tuple[CanonicalContingency, ...]:
        if status is not None and status not in CAUSAL_STATUSES | SAFETY_STATUSES:
            raise ValueError("unrecognized normative causal or safety status")
        return tuple(
            record for _, record in sorted(self._published.items())
            if (context_signature is None or record.context_signature == context_signature)
            and (status is None or status in (record.safety_status, record.causal_status))
        )

    def get(self, contingency_ref: str) -> CanonicalContingency | None:
        return self._published.get(contingency_ref)

    def proposer_test(self) -> tuple[CausalTestTarget, ...]:
        """Read-only §13.4 proposals from published, revisable hypotheses.

        This Stage-9 subset designates only explicitly registered drinking
        tests for a non-safety predicate. It neither creates motivation nor
        bypasses Planning/Action Control. Unsafe ingestion tests and invented
        commands are never inferred from causal correlation.
        """
        actions = {
            (predicate, subject): primitive
            for predicate, subject, primitive in self.config.safe_test_actions
        }
        targets: list[CausalTestTarget] = []
        for contingency in self.contingencies():
            if (
                contingency.causal_status not in {
                    "hypothese_causale", "testee_par_intervention"
                }
                or contingency.safety_status != "aucun"
                or contingency.predicate in SAFETY_PREDICATES
            ):
                continue
            primitive = actions.get(
                (contingency.predicate, contingency.subject_ref)
            )
            if primitive is None:
                continue
            target = CausalTestTarget(
                contingency_ref=contingency.ref,
                contingency_version=contingency.version,
                predicate=contingency.predicate,
                subject_ref=contingency.subject_ref,
                application_context=contingency.context_signature,
                primitive=primitive,
                motive_ref=f"test_causal:{contingency.ref}",
            )
            target.validate()
            targets.append(target)
        return tuple(targets)

    def record_applied_hydration_observation(
        self, *, t_monde: int, primitive: str, option_ref: str,
        current_water_source: bool, position: tuple[int, int],
        water_before: float,
    ) -> bool:
        """Register only an independently applied drink or ordinary wait.

        This is passive observation, *not* a causal test, and neither option
        proposals nor intended but blocked actions may call this adapter.
        """
        if (
            "hydration_effect" not in self.config.causal_predicates
            or primitive not in {"boire", "attendre"}
            or not current_water_source
            or isinstance(water_before, bool)
            or not isinstance(water_before, (int, float))
            or not isfinite(water_before)
            or water_before >= 100
        ):
            return False
        sample = LivedHydrationExposure(
            t_monde=t_monde, primitive=primitive, option_ref=option_ref,
            position=position, water_before=float(water_before),
        )
        sample.validate()
        if t_monde in self._lived_hydration_exposures:
            raise ValueError("multiple hydration commands in one world step")
        self._lived_hydration_exposures[t_monde] = sample
        return True

    def observe_hydration_followup(
        self, *, t_monde: int, water: float,
    ) -> None:
        """Only accessible next-step body telemetry, never a world/oracle read."""
        if (
            type(t_monde) is not int or t_monde < 1
            or isinstance(water, bool) or not isinstance(water, (int, float))
            or not isfinite(water) or not 0 <= water <= 100
        ):
            raise ValueError("invalid hydration Perception capture")
        row = self._lived_hydration_exposures.get(t_monde - 1)
        if row is None or row.observed_step is not None:
            return
        update = replace(
            row, observed_step=t_monde, water_observed=float(water),
        )
        update.validate()
        self._lived_hydration_exposures[row.t_monde] = update

    def ingest_closed_hydration_episode(
        self, *, episode_ref: str, event_refs: Sequence[str],
        autobiographical_events: Sequence[Mapping[str, object]],
    ) -> tuple[CausalObservation, ...]:
        """Admit only matching DC-09 command/physical consequence pairs.

        An externally altered next-step water reading does not corroborate
        the step's physical transition, so it cannot become an observation.
        Actual non-drinking WAITs provide controls only at the same accessible
        water-source site and do not create new experiments or motivations.
        """
        if (
            not isinstance(episode_ref, str) or not episode_ref
            or len(event_refs) != len(set(event_refs))
        ):
            raise ValueError("invalid closed hydration episode")
        allowed = set(event_refs)
        events = tuple(
            event for event in autobiographical_events
            if event.get("event_id") in allowed
        )
        ambiguous_steps = _ambiguous_closed_projection_steps(events)
        rows = []
        retire = []
        for sample in sorted(
            self._lived_hydration_exposures.values(),
            key=lambda v: v.t_monde,
        ):
            if sample.observed_step is None:
                continue
            if sample.t_monde in ambiguous_steps:
                retire.append(sample.t_monde)
                continue
            commands = [
                event for event in events
                if event.get("kind") == "command_experienced"
                and event.get("t_monde") == sample.t_monde
            ]
            transitions = [
                event for event in events
                if event.get("kind") == "world_transition_experienced"
                and event.get("t_monde") == sample.t_monde
            ]
            if not commands and not transitions:
                continue
            # This command belongs to a closed episode; mismatches can never
            # be resurrected by reopening the same world step later.
            retire.append(sample.t_monde)
            if len(commands) != 1 or len(transitions) != 1:
                continue
            # P-35 credits physical co-occurrences, not Memory episode IDs.
            # DC-05 retains its separate distinct-episode safety threshold.
            command, physical = commands[0], transitions[0]
            effects = physical.get("effects")
            body = physical.get("body_after")
            pos = physical.get("position_after")
            if (
                command.get("primitive") != sample.primitive
                or command.get("parameters") != {}
                or not isinstance(effects, Mapping)
                or not isinstance(body, Mapping)
                or not isinstance(pos, Mapping)
                or (
                    pos.get("x"), pos.get("y")
                ) != sample.position
                or body.get("water") != sample.water_observed
                or (
                    effects.get("drank") is not True
                    if sample.primitive == "boire"
                    else effects.get("rest") != "attendre"
                )
            ):
                continue
            command_id = command.get("event_id")
            transition_id = physical.get("event_id")
            if (
                not isinstance(command_id, str) or not command_id
                or not isinstance(transition_id, str) or not transition_id
                or command_id == transition_id
            ):
                continue
            site = f"{sample.position[0]},{sample.position[1]}"
            observation = CausalObservation(
                identifier=f"lived-hydration:{episode_ref}:{transition_id}",
                contingency_ref="causal:hydration",
                predicate="hydration_effect",
                subject_ref="water",
                application_context="water_source",
                observation_context="water_source",
                episode_ref=episode_ref,
                observation_ref=transition_id,
                observed_step=sample.observed_step,
                cause_present=sample.primitive == "boire",
                effect_present=sample.water_observed > sample.water_before,
                controlled_variables=(
                    ("water_source", "present"), ("site", site),
                ),
            )
            observation.validate()
            if (
                observation.identifier in self._hydration_observation_witnesses
                or observation.identifier in self._causal_observations
                or any(
                    old.identifier == observation.identifier
                    for old in (*self._pending_causal_observations, *rows)
                )
                or any(
                    transition_id == pair[1]
                    for pair in self._hydration_observation_witnesses.values()
                )
            ):
                raise ValueError("duplicate lived hydration physical transition")
            rows.append(observation)
        for obs in rows:
            self.integrate_causal_observation(obs)
            # Source references are retained after publication so a typed
            # or replayed observation cannot fabricate an autonomous review.
            command = next(
                event for event in events
                if event.get("kind") == "command_experienced"
                and event.get("t_monde") == obs.observed_step - 1
            )
            self._hydration_observation_witnesses[obs.identifier] = (
                str(command["event_id"]), obs.observation_ref,
            )
        for step in retire:
            del self._lived_hydration_exposures[step]
        return tuple(rows)

    def record_applied_causal_action(
        self, *, t_monde: int, option_ref: str,
        motive_type: str, motive_ref: str, primitive: str,
        current_water_source: bool, position: tuple[int, int],
        water_before: float,
    ) -> tuple[LivedCausalAction, ...]:
        """Receive only an actually applied Action Control decision (Stage 9).

        The caller is the dispatch adapter, after nonlethal application.
        This is a *pending* causal action, not published intervention evidence.
        Pre-existing hypotheses and explicit P-35 safe actions are required.
        Goal-motivated actions may be incidental interventions: they never
        create a new exploratory motivation or demand dangerous re-exposure.
        """
        if (
            primitive != "boire" or not current_water_source
            or motive_type not in {"active_goal", "test_causal"}
            or not option_ref or not motive_ref
            or isinstance(water_before, bool)
            or not isinstance(water_before, (float, int))
            or not isfinite(water_before) or water_before >= 100
        ):
            return ()
        # Once established, the contingency remains revisable by further
        # independently goal-motivated lived actions (§13.2). Do not propose
        # another experimental action merely to reconfirm it.
        candidates = list(self.proposer_test())
        if motive_type == "active_goal":
            for contingency in self.contingencies(status="etablie"):
                if (
                    contingency.predicate not in SAFETY_PREDICATES
                    and (
                        contingency.predicate, contingency.subject_ref, "boire"
                    ) in self.config.safe_test_actions
                    and contingency.context_signature == "water_source"
                ):
                    candidates.append(CausalTestTarget(
                        contingency_ref=contingency.ref,
                        contingency_version=contingency.version,
                        predicate=contingency.predicate,
                        subject_ref=contingency.subject_ref,
                        application_context=contingency.context_signature,
                        primitive="boire",
                        motive_ref=f"test_causal:{contingency.ref}",
                    ))
        rows = []
        for target in candidates:
            if (
                target.primitive != primitive
                or target.application_context != "water_source"
            ):
                continue
            if motive_type == "test_causal" and (
                motive_ref != target.motive_ref
                or option_ref != (
                    f"option:causal-test:{target.contingency_ref}:"
                    f"v{target.contingency_version}"
                )
            ):
                continue
            row = LivedCausalAction(
                identifier=(
                    f"lived-causal:{target.contingency_ref}:"
                    f"{option_ref}:{t_monde}"
                ),
                contingency_ref=target.contingency_ref,
                contingency_version=target.contingency_version,
                option_ref=option_ref,
                motive_type=motive_type,
                sent_t_monde=t_monde,
                position=position,
                water_before=float(water_before),
            )
            row.validate()
            if (
                row.identifier in self._lived_causal_actions
                or f"intervention:{row.identifier}"
                   in self._causal_action_witnesses
                or any(
                    v.contingency_ref == row.contingency_ref
                    and v.sent_t_monde == row.sent_t_monde
                    for v in (
                        *self._lived_causal_actions.values(),
                        *self._causal_action_witnesses.values(),
                        *rows,
                    )
                )
            ):
                # A differently named option cannot turn a second claim
                # about one physical world step into an independent P-35
                # intervention for the same canonical contingency. Keep
                # separate real steps, and separate predicates, untouched.
                raise ValueError("duplicate applied causal action")
            rows.append(row)
        for row in rows:
            self._lived_causal_actions[row.identifier] = row
        return tuple(rows)

    def observe_causal_action_followup(
        self, *, t_monde: int, water: float,
    ) -> None:
        """Only the next individual-accessible Perception body capture."""
        if (
            type(t_monde) is not int or t_monde < 1
            or isinstance(water, bool) or not isinstance(water, (float, int))
            or not isfinite(water) or not 0 <= water <= 100
        ):
            raise ValueError("invalid causal test Perception capture")
        for ref, row in tuple(self._lived_causal_actions.items()):
            if row.sent_t_monde != t_monde - 1 or row.observed_t_monde is not None:
                continue
            updated = replace(
                row, observed_t_monde=t_monde, water_observed=float(water),
            )
            updated.validate()
            self._lived_causal_actions[ref] = updated

    def ingest_closed_causal_action_episode(
        self, *, episode_ref: str, event_refs: Sequence[str],
        autobiographical_events: Sequence[Mapping[str, object]],
    ) -> tuple[LivedCausalAction, ...]:
        """Bind an applied drinking action to exact closed DC-09 event IDs.

        The comparator may close in a different episode. Its evidence is
        joined *later*, only after publication by the canonical owner.
        This method cannot credit a typed intervention.
        """
        if not episode_ref or len(set(event_refs)) != len(event_refs):
            raise ValueError("invalid closed Memory causal action references")
        allowed = set(event_refs)
        events = [
            item for item in autobiographical_events
            if item.get("event_id") in allowed
        ]
        ambiguous_steps = _ambiguous_closed_projection_steps(events)
        changes = []
        invalidated = []
        for row in sorted(self._lived_causal_actions.values(),
                          key=lambda value: value.identifier):
            if (
                row.observed_t_monde is None
                or row.command_event_ref is not None
            ):
                continue
            if row.sent_t_monde in ambiguous_steps:
                invalidated.append(row.identifier)
                continue
            # Select all physical projections at the source step before
            # inspecting the expected outcome. Filtering by successful
            # drink fields first would hide an additional, incompatible
            # command or transition and manufacture unique P-35 evidence.
            commands = [
                event for event in events
                if event.get("kind") == "command_experienced"
                and event.get("t_monde") == row.sent_t_monde
            ]
            transitions = [
                event for event in events
                if event.get("kind") == "world_transition_experienced"
                and event.get("t_monde") == row.sent_t_monde
            ]
            if len(commands) != 1 or len(transitions) != 1:
                if commands or transitions:
                    # A closed Memory projection of this physical step that
                    # lacks its matching partner cannot be reopened later
                    # under another episode identity. This mirrors the
                    # observational hydration admission path (P-35/DC-09).
                    # An entirely unrelated episode must leave it pending.
                    invalidated.append(row.identifier)
                continue
            command, transition = commands[0], transitions[0]
            if (
                command.get("primitive") != "boire"
                or command.get("parameters") != {}
                or not isinstance(transition.get("effects"), Mapping)
                or transition["effects"].get("drank") is not True
                or not isinstance(transition.get("body_after"), Mapping)
                or transition["body_after"].get("water") != row.water_observed
                or not isinstance(transition.get("position_after"), Mapping)
                or (
                    transition["position_after"].get("x"),
                    transition["position_after"].get("y"),
                ) != row.position
            ):
                invalidated.append(row.identifier)
                continue
            command_ref = command.get("event_id")
            transition_ref = transition.get("event_id")
            if (
                not isinstance(command_ref, str)
                or not isinstance(transition_ref, str)
                or command_ref == transition_ref
            ):
                continue
            updated = replace(
                row,
                command_event_ref=command_ref,
                transition_event_ref=transition_ref,
                physical_episode_ref=episode_ref,
            )
            updated.validate()
            changes.append(updated)
        for row in changes:
            self._lived_causal_actions[row.identifier] = row
        for identifier in invalidated:
            del self._lived_causal_actions[identifier]
        return tuple(changes)

    @staticmethod
    def _verified_lived_drink_intervention(
        trial: CausalIntervention,
        witness: LivedCausalAction | None,
        report: AgencyEvidence | None,
    ) -> bool:
        """Canonical physical join for the supported Stage-9 water test.

        A published comparator is descriptive evidence; the separately
        Memory-closed physical command and transition must additionally agree.
        A typed trial is not permitted to invent or redirect its provenance.
        """
        if witness is None or report is None:
            return False
        witness.validate()
        site = (
            f"water_source:{witness.position[0]},{witness.position[1]}"
        )
        expected_controls = (
            ("primitive", "boire"),
            ("water_source", "present"),
            ("site", f"{witness.position[0]},{witness.position[1]}"),
        )
        water_effects = [
            effect for effect in report.effects if effect[0] == "water"
        ]
        return (
            trial.identifier == f"intervention:{witness.identifier}"
            and witness.contingency_ref == trial.contingency_ref
            and witness.physical_episode_ref is not None
            and witness.command_event_ref is not None
            and witness.command_event_ref != witness.transition_event_ref
            and witness.transition_event_ref == trial.observation_ref
            and witness.option_ref == trial.command_ref
            and witness.sent_t_monde == trial.emitted_step
            and witness.observed_t_monde == trial.observed_step
            and trial.context_signature == site
            and trial.controlled_variables == expected_controls
            and witness.water_observed is not None
            and trial.observed_effect
                == (witness.water_observed > witness.water_before)
            and report.option_ref == witness.option_ref
            and report.sent_t_monde == witness.sent_t_monde
            and report.observed_t_monde == witness.observed_t_monde
            and len(water_effects) == 1
            and water_effects[0][3] == witness.water_observed
            and water_effects[0][1] == (
                "conforming" if trial.observed_effect else "nonconforming"
            )
        )

    def promote_lived_causal_interventions(self) -> tuple[CausalIntervention, ...]:
        """Publish no facts: stage only fully joined, *published* P-47 evidence.

        The caller invokes this after Memory ingestion, in phase 1. Comparator
        results from the same cycle cannot authorize the test until a future
        cycle; the ordinary phase-5 causal publication remains the sole writer.
        """
        trials = []
        retire = []
        for row in sorted(self._lived_causal_actions.values(),
                          key=lambda value: value.identifier):
            if (
                row.physical_episode_ref is None
                or row.transition_event_ref is None
                or row.observed_t_monde is None
                or row.water_observed is None
            ):
                continue
            contingency = self._published.get(row.contingency_ref)
            if (
                contingency is None
                or contingency.version < row.contingency_version
                or contingency.causal_status not in {
                    "hypothese_causale", "testee_par_intervention", "etablie"
                }
            ):
                retire.append(row.identifier)
                continue
            matching = [
                report for report in self._agency_evidence.values()
                if (
                    report.option_ref == row.option_ref
                    and report.sent_t_monde == row.sent_t_monde
                    and report.observed_t_monde == row.observed_t_monde
                )
            ]
            if not matching:
                continue
            if len(matching) != 1:
                # Ambiguous provenance can never be upgraded to causality.
                retire.append(row.identifier)
                continue
            report = matching[0]
            water_effects = [
                effect for effect in report.effects
                if effect[0] == "water"
            ]
            if (
                len(water_effects) != 1
                or water_effects[0][3] != row.water_observed
            ):
                retire.append(row.identifier)
                continue
            effect_status = water_effects[0][1]
            observed = row.water_observed > row.water_before
            if observed:
                admitted = (
                    report.status == "conforming"
                    and report.attribution == "self_compatible"
                    and effect_status == "conforming"
                )
            else:
                admitted = (
                    report.status == "nonconforming"
                    and report.attribution == "uncertain"
                    and effect_status == "nonconforming"
                )
            if not admitted:
                retire.append(row.identifier)
                continue
            context = f"water_source:{row.position[0]},{row.position[1]}"
            trial = CausalIntervention(
                identifier=f"intervention:{row.identifier}",
                contingency_ref=row.contingency_ref,
                episode_ref=report.episode_ref,
                observation_ref=row.transition_event_ref,
                command_ref=row.option_ref,
                comparator_ref=report.identifier,
                context_signature=context,
                emitted_step=row.sent_t_monde,
                observed_step=row.observed_t_monde,
                observed_effect=observed,
                comparator_status=report.status,
                attribution=report.attribution,
                controlled_variables=(
                    ("primitive", "boire"),
                    ("water_source", "present"),
                    ("site", f"{row.position[0]},{row.position[1]}"),
                ),
                action_applied=True,
            )
            trial.validate()
            if (
                trial.identifier not in self._causal_interventions
                and all(
                    pending.identifier != trial.identifier
                    for pending in self._pending_causal_interventions
                )
            ):
                trials.append(trial)
            retire.append(row.identifier)
        for trial in trials:
            witness_ref = trial.identifier.removeprefix("intervention:")
            witness = self._lived_causal_actions[witness_ref]
            if trial.identifier in self._causal_action_witnesses:
                raise ValueError("duplicate physical causal intervention witness")
            if not self._verified_lived_drink_intervention(
                trial, witness, self._agency_evidence.get(trial.comparator_ref),
            ):
                raise ValueError("lived intervention physical lineage mismatch")
        for trial in trials:
            witness_ref = trial.identifier.removeprefix("intervention:")
            self.integrate_causal_intervention(trial)
            self._causal_action_witnesses[trial.identifier] = (
                self._lived_causal_actions[witness_ref]
            )
        for identifier in retire:
            del self._lived_causal_actions[identifier]
        return tuple(trials)

    def record_applied_ambient_integrity_control(
        self, *, t_monde: int, option_ref: str,
        position: tuple[int, int], integrity_before: float,
    ) -> None:
        """Observe an already applied ordinary wait, never request an action."""
        control = LivedAmbientIntegrityControl(
            t_monde=t_monde, option_ref=option_ref,
            position=position, integrity_before=float(integrity_before),
        )
        control.validate()
        if t_monde in self._lived_ambient_integrity_controls:
            raise ValueError("duplicate ambient control on world step")
        self._lived_ambient_integrity_controls[t_monde] = control

    def record_applied_food_exposure(
        self, *, t_monde: int, resource_kind: str,
        option_ref: str, motive_ref: str, integrity_before: float,
        body_before: Mapping[str, float] | None = None,
        position_before: tuple[int, int] | None = None,
        state_before_digest: str | None = None,
        visible_creature_at_exposure: bool = False,
    ) -> None:
        """Only already-executed, independently goal-motivated actions enter.

        No generated dangerous test option and no reward/bench/oracle inputs.
        These are pending action references, not promoted evidence.
        """
        item = LivedFoodExposure(
            t_monde=t_monde, resource_kind=resource_kind,
            option_ref=option_ref, motive_ref=motive_ref,
            integrity_before=integrity_before,
            body_before=(
                None if body_before is None else
                tuple(sorted((name, float(v)) for name, v in body_before.items()))
            ),
            position_before=position_before,
            state_before_digest=state_before_digest,
            visible_creature_at_exposure=visible_creature_at_exposure,
        )
        item.validate()
        if t_monde in self._lived_food_exposures:
            raise ValueError("more than one food exposure in a world step")
        self._lived_food_exposures[t_monde] = item

    def observe_followup_capture(
        self, *, t_monde: int, integrity: float,
    ) -> None:
        """Only the next *accessible Perception capture* can corroborate harm."""
        if t_monde < 1 or not isfinite(integrity) or not 0 <= integrity <= 100:
            raise ValueError("invalid physical capture")
        item = self._lived_food_exposures.get(t_monde - 1)
        if item is not None and item.observed_step is None:
            updated = replace(
                item, observed_step=t_monde, integrity_observed=float(integrity),
            )
            updated.validate()
            self._lived_food_exposures[item.t_monde] = updated
        control = self._lived_ambient_integrity_controls.get(t_monde - 1)
        if control is not None and control.observed_step is None:
            updated_control = replace(
                control, observed_step=t_monde, integrity_observed=float(integrity),
            )
            updated_control.validate()
            self._lived_ambient_integrity_controls[control.t_monde] = updated_control
        # No need to retain old controls forever. Preserve any wait whose
        # immediately following meal still awaits an actual DC-09 closure;
        # everything else is ineligible to control a later food exposure.
        expired = [
            step for step in self._lived_ambient_integrity_controls
            if step + 2 < t_monde
            and step + 1 not in self._lived_food_exposures
        ]
        for step in expired:
            del self._lived_ambient_integrity_controls[step]

    def ingest_closed_autobiographical_episode(
        self, *, episode_ref: str, event_refs: Sequence[str],
        autobiographical_events: Sequence[Mapping[str, object]],
    ) -> tuple[SafetyEvidence, ...]:
        """DC-05: consume only lived, closed Memory episodes from DC-09.

        Never read technical journal or current world. We require a matching
        authorized command+transition, actual ingestion, next-step physical
        telemetry, and no observable sufficient alternative injury cause.
        A candidate receives the *real* Memory episode ID, not a manufactured
        new episode for each command. No shortcut to causal `etablie`.
        """
        if (
            not isinstance(episode_ref, str) or not episode_ref
            or len(event_refs) != len(set(event_refs))
        ):
            raise ValueError("invalid closed Memory episode reference ledger")
        # DC-09 projections are immutable journal facts. Do not let a
        # repeated event ID silently overwrite a different source payload,
        # even if the final payload appears to match the pending exposure.
        # Only identifiers credited by this closed episode may be considered.
        closed_refs = set(event_refs)
        events: dict[str, Mapping[str, object]] = {}
        for projection in autobiographical_events:
            if not isinstance(projection, Mapping):
                continue
            ref = projection.get("event_id")
            if (
                not isinstance(ref, str) or ref not in closed_refs
                or projection.get("kind") not in {
                    "command_experienced", "world_transition_experienced",
                }
            ):
                continue
            if ref in events:
                raise ValueError(
                    "duplicate closed Memory autobiographical event projection"
                )
            events[ref] = projection
        commands: dict[int, Mapping[str, object]] = {}
        transitions: dict[int, Mapping[str, object]] = {}
        ambiguous_steps: set[int] = set()
        for event_ref in event_refs:
            event = events.get(event_ref)
            if event is None:
                continue
            t = event.get("t_monde")
            if type(t) is not int or t < 1 or t in ambiguous_steps:
                continue
            if event["kind"] == "command_experienced":
                if t in commands:
                    # Once a closed world step has conflicting projections,
                    # a third differently named event must not resurrect
                    # the same physical exposure. Retire both arms.
                    commands.pop(t, None)
                    transitions.pop(t, None)
                    ambiguous_steps.add(t)
                    continue
                commands[t] = event
            elif event["kind"] == "world_transition_experienced":
                if t in transitions:
                    transitions.pop(t, None)
                    commands.pop(t, None)
                    ambiguous_steps.add(t)
                    continue
                transitions[t] = event

        # Verify independently executed non-ingestion controls using ONLY the
        # same closed first-person command/transition pairs as food exposures.
        # A forged or missing half-pair is retired, never silently credited.
        staged_controls = dict(self._lived_ambient_integrity_controls)
        for control_step, control in sorted(staged_controls.items()):
            if control.episode_ref is not None or control.observed_step is None:
                continue
            if control_step in ambiguous_steps:
                del staged_controls[control_step]
                continue
            command = commands.get(control_step)
            physical = transitions.get(control_step)
            if command is None and physical is None:
                continue
            position = physical.get("position_after") if physical is not None else None
            body = physical.get("body_after") if physical is not None else None
            effects = physical.get("effects") if physical is not None else None
            command_ref = command.get("event_id") if command is not None else None
            transition_ref = physical.get("event_id") if physical is not None else None
            if (
                command is None or physical is None
                or command.get("primitive") != "attendre"
                or command.get("parameters") != {}
                or not isinstance(position, Mapping)
                or (position.get("x"), position.get("y")) != control.position
                or not isinstance(body, Mapping)
                or body.get("integrity") != control.integrity_observed
                or not isinstance(effects, Mapping)
                or effects.get("rest") != "attendre"
                or control.integrity_observed != control.integrity_before
                or not isinstance(command_ref, str) or not command_ref
                or not isinstance(transition_ref, str) or not transition_ref
                or command_ref == transition_ref
            ):
                del staged_controls[control_step]
                continue
            verified = replace(
                control, episode_ref=episode_ref,
                command_ref=command_ref, transition_ref=transition_ref,
            )
            verified.validate()
            staged_controls[control_step] = verified

        candidate: list[SafetyEvidence] = []
        causal_observations: list[CausalObservation] = []
        numeric_witnesses: list[LivedNumericOutcome] = []
        for t in sorted(commands.keys() & transitions.keys()):
            exposure = self._lived_food_exposures.get(t)
            if exposure is None or exposure.observed_step is None:
                continue
            command = commands[t]
            transition = transitions[t]
            parameters = command.get("parameters")
            effects = transition.get("effects")
            body_after = transition.get("body_after")
            if (
                command.get("primitive") != "manger"
                or not isinstance(parameters, Mapping)
                or parameters.get("target") != exposure.resource_kind
                or not isinstance(effects, Mapping)
                or set(effects) != {"ate"}
                or effects.get("ate") != exposure.resource_kind
                or not isinstance(body_after, Mapping)
            ):
                continue
            after = body_after.get("integrity")
            if (
                not isinstance(after, (int, float))
                or not isfinite(after)
                or after != exposure.integrity_observed
            ):
                # Scenario changed telemetry, or the following capture is
                # missing; neither should masquerade as an observed consequence.
                continue
            # Hidden physical attribution is outside I0's epistemic boundary.
            # This code intentionally never inspects creature_damage or
            # danger_zone_damage, even to reject a row: cognition may only use
            # lived controls and perceptible competing causes.
            harm_observed = after < exposure.integrity_before
            baseline = staged_controls.get(t - 1)
            matched_control = bool(
                baseline is not None
                and baseline.episode_ref is not None
                and baseline.observed_step == t
                and exposure.position_before is not None
                and baseline.position == exposure.position_before
                and baseline.integrity_observed == exposure.integrity_before
            )
            # A creature perceived adjacent during the *food* decision
            # remains a plausible concurrent cause even when the previous
            # no-food wait was clean. This is lived evidence, not an oracle
            # assertion about whether that creature physically attacked.
            if harm_observed and (
                not matched_control or exposure.visible_creature_at_exposure
            ):
                continue

            # A clean preceding wait excludes only harm observed during that
            # wait. It cannot exclude a hidden hazard that appears exactly at
            # the food step. Under the current perceptual contract there is no
            # food-specific lived signal that distinguishes that world from a
            # genuinely toxic berry world. Therefore every harmful food
            # association remains epistemically ambiguous for DC-05. Repeated
            # positions or episodes cannot manufacture unobserved etiology.
            epistemic_status = (
                "ambiguous_food_association"
                if harm_observed else "dc05_admissible"
            )

            event = transition
            candidate.append(SafetyEvidence(
                identifier=f"dc05:{episode_ref}:{event['event_id']}",
                contingency_ref=f"toxic:{exposure.resource_kind}",
                predicate="toxic_item",
                subject_ref=exposure.resource_kind,
                context_signature="global",
                episode_ref=episode_ref,
                observation_ref=str(event["event_id"]),
                emission_step=exposure.t_monde,
                observation_step=exposure.observed_step,
                harm_observed=after < exposure.integrity_before,
                source="monde",
                independent_episode=True,
                comparable_context=True,
                alternative_cause_sufficient=False,
                exposure_motivated_independently=True,
                epistemic_status=epistemic_status,
            ))
            if (
                epistemic_status == "dc05_admissible"
                and exposure.body_before is not None
                and exposure.position_before is not None
                and exposure.state_before_digest is not None
                and after < exposure.integrity_before
            ):
                witness = LivedNumericOutcome(
                    identifier=f"numeric-witness:{episode_ref}:{event['event_id']}",
                    contingency_ref=f"toxic:{exposure.resource_kind}",
                    episode_ref=episode_ref,
                    command_event_ref=str(command["event_id"]),
                    transition_event_ref=str(event["event_id"]),
                    option_ref=exposure.option_ref,
                    sent_t_monde=exposure.t_monde,
                    observed_t_monde=exposure.observed_step,
                    command_primitive="manger",
                    command_target=exposure.resource_kind,
                    variable="integrity",
                    observed_before_body=exposure.body_before,
                    observed_before_position=exposure.position_before,
                    observed_before_state_digest=exposure.state_before_digest,
                    observed_after=float(after),
                )
                numeric_witnesses.append(witness)
            # An explicitly ambiguous harmful association must not silently
            # become a causal observation. Under the current v1.3.1 food
            # contract only lived no-harm observations remain eligible here.
            if epistemic_status == "dc05_admissible":
                causal_observations.append(CausalObservation(
                identifier=f"causal-observation:{episode_ref}:{event['event_id']}",
                contingency_ref=f"toxic:{exposure.resource_kind}",
                predicate="toxic_item",
                subject_ref=exposure.resource_kind,
                application_context="global",
                observation_context="food_consumption",
                episode_ref=episode_ref,
                observation_ref=str(event["event_id"]),
                observed_step=exposure.observed_step,
                cause_present=True,
                effect_present=after < exposure.integrity_before,
                    controlled_variables=(("primitive", "manger"),),
                ))
        # A *different actually eaten food* may be an independently lived
        # no-exposure comparison for a preregistered treatment. Same episode
        # and physical reference are preserved: this is NOT a new experience.
        for observed in tuple(causal_observations):
            for treatment, control in self.config.food_control_pairs:
                if observed.subject_ref != control:
                    continue
                causal_observations.append(CausalObservation(
                    identifier=f"causal-control:{treatment}:{observed.identifier}",
                    contingency_ref=f"toxic:{treatment}",
                    predicate="toxic_item",
                    subject_ref=treatment,
                    application_context=observed.application_context,
                    observation_context=observed.observation_context,
                    episode_ref=observed.episode_ref,
                    observation_ref=observed.observation_ref,
                    observed_step=observed.observed_step,
                    cause_present=False,
                    effect_present=observed.effect_present,
                    controlled_variables=observed.controlled_variables,
                ))
        # All validations are preflight: a rejected Memory episode cannot
        # partially mutate safety state without matching causal observation.
        for item in candidate:
            item.validate()
            if item.epistemic_status == "dc05_admissible" and (
                item.identifier in self._seen_ids or any(
                    old.identifier == item.identifier for old in self._pending
                )
            ):
                raise ValueError("duplicate closed Memory safety evidence")
        for item in causal_observations:
            item.validate()
            if item.identifier in self._causal_observations or any(
                old.identifier == item.identifier
                for old in self._pending_causal_observations
            ):
                raise ValueError("duplicate closed Memory causal observation")
        for witness in numeric_witnesses:
            witness.validate()
            if (
                witness.identifier in self._numeric_witnesses
                or any(
                    old.transition_event_ref == witness.transition_event_ref
                    for old in (
                        *self._numeric_witnesses.values(),
                        *self._pending_numeric_witnesses,
                    )
                )
            ):
                raise ValueError("duplicated closed physical numeric outcome")
        # Publish verified control state only AFTER the entire incoming
        # episode has passed its existing atomic evidence preflight.
        self._lived_ambient_integrity_controls = staged_controls
        for item in candidate:
            if item.epistemic_status == "dc05_admissible":
                self.integrate(item)
        for item in causal_observations:
            self.integrate_causal_observation(item)
        for witness in numeric_witnesses:
            self._pending_numeric_witnesses.append(witness)
        # A physically ambiguous closed attempt is retired, not left
        # available to support another forged episode later. Ordinary
        # observed but unpaired commands retain the previous lifecycle.
        for t in ambiguous_steps:
            self._lived_food_exposures.pop(t, None)
        # Exposure refs can be discarded only once their command is represented
        # by a *closed* episode; unobserved attempts cannot be counted later.
        for t, command in commands.items():
            if command.get("primitive") == "manger":
                self._lived_food_exposures.pop(t, None)
        return tuple(candidate)

    def pending_causal_observations(self) -> tuple[CausalObservation, ...]:
        """Read-only records for causal provenance logging."""
        return tuple(self._pending_causal_observations)

    def integrate_causal_observation(self, observation: CausalObservation) -> None:
        observation.validate()
        if observation.identifier in self._causal_observations or any(
            x.identifier == observation.identifier for x in self._pending_causal_observations
        ):
            raise ValueError("duplicate observation")
        self._pending_causal_observations.append(observation)

    def integrate_hypothesis_review(self, review: CausalHypothesisReview) -> None:
        review.validate()
        if review.identifier in self._causal_reviews or any(
            x.identifier == review.identifier for x in self._pending_causal_reviews
        ):
            raise ValueError("duplicate review")
        self._pending_causal_reviews.append(review)

    def integrate_causal_intervention(self, trial: CausalIntervention) -> None:
        trial.validate()
        if trial.identifier in self._causal_interventions or any(
            x.identifier == trial.identifier for x in self._pending_causal_interventions
        ):
            raise ValueError("duplicate intervention")
        self._pending_causal_interventions.append(trial)

    @staticmethod
    def _published_comparison_supports(
        trial: CausalIntervention, report: AgencyEvidence | None,
    ) -> bool:
        """Bind a typed intervention to previously published DC-09/P-47 evidence.

        This checks provenance, not causal truth. Pending comparisons cannot
        authorize an intervention in the same phase-5 publication batch.
        """
        return (
            report is not None
            and report.source == "agency_comparator"
            and report.identifier == trial.comparator_ref
            and report.episode_ref == trial.episode_ref
            and report.option_ref == trial.command_ref
            and report.sent_t_monde == trial.emitted_step
            and report.observed_t_monde == trial.observed_step
            and report.status == trial.comparator_status
            and report.attribution == trial.attribution
        )

    def established_prediction_corrections(self) -> tuple[NumericPredictionCorrection, ...]:
        """INV-25: derived immutable view, not a mutable simulator fact store.

        An established status alone is insufficient. Supporting independent
        interventions must join already published DC-09 AgencyEvidence with
        matching time, option and attribution. The numerical after-value is
        additionally required to match a genuine separately lived,
        Perception-corroborated Memory transition for the same option.
        """
        verified_interventions: dict[str, list[CausalIntervention]] = {}
        for trial in self._causal_interventions.values():
            report = self._agency_evidence.get(trial.comparator_ref)
            if (
                not trial.observed_effect
                or not self._published_comparison_supports(trial, report)
                or trial.comparator_status != "conforming"
                or trial.attribution != "self_compatible"
            ):
                continue
            verified_interventions.setdefault(trial.contingency_ref, []).append(trial)

        # Ephemeral published evidence view. The first two admissible
        # lookups scan it directly; only a third lookup pays for an index.
        # No persistent cache, extra causal owner or hidden information.
        published_reports: tuple[AgencyEvidence, ...] | None = None
        published_by_action: dict[
            tuple[str, int, int], list[AgencyEvidence]
        ] | None = None
        eligible_lookups = 0

        # Query-local eligibility cache: every numeric witness of the same
        # published contingency shares the same revision and interventions.
        # Never persist this index or grant another owner causal authority.
        active_by_contingency: dict[str, tuple[str, ...] | None] = {}
        rules: list[NumericPredictionCorrection] = []
        for _, witness in sorted(self._numeric_witnesses.items()):
            contingency = self._published.get(witness.contingency_ref)
            if (
                contingency is None
                or contingency.causal_status != "etablie"
                or contingency.predicate != "toxic_item"
                or contingency.subject_ref != witness.command_target
                or contingency.context_signature != "global"
            ):
                continue
            trials = verified_interventions.get(contingency.ref, ())
            revision = self._causal_revision_boundaries.get(
                contingency.ref, (-1, "")
            )[0]
            # A recovered causal status cannot revive a numerical value
            # measured before a contradictory lived intervention. The
            # simulator needs a new, Memory-closed Perception measurement
            # and its own already-published P-47 comparison after revision.
            if witness.observed_t_monde <= revision:
                continue
            # Only interventions after the latest published refutation
            # establish the current rule. Export provenance from that same
            # revision window, never from a stale pre-refutation success.
            if contingency.ref not in active_by_contingency:
                active_trials = tuple(
                    trial for trial in trials
                    if trial.observed_step > revision
                )
                matching_contexts = {
                    trial.context_signature for trial in active_trials
                }
                active_by_contingency[contingency.ref] = (
                    (min(trial.identifier for trial in active_trials),)
                    if len(matching_contexts) >= self.config.n2
                    else None
                )
            selected = active_by_contingency[contingency.ref]
            if selected is None:
                continue
            intervention_ref = selected[0]

            if published_reports is None:
                published_reports = self.published_agency_evidence()
            eligible_lookups += 1
            if eligible_lookups == 3:
                published_by_action = {}
                for report in published_reports:
                    key = (
                        report.option_ref, report.sent_t_monde,
                        report.observed_t_monde,
                    )
                    published_by_action.setdefault(key, []).append(report)

            # Preserve the original direct scan for small histories; do
            # not allocate a filtering generator for one or two witnesses.
            matching_reports = (
                published_reports if published_by_action is None
                else published_by_action.get(
                    (witness.option_ref, witness.sent_t_monde,
                     witness.observed_t_monde), ()
                )
            )
            for report in matching_reports:
                if (
                    report.option_ref != witness.option_ref
                    or report.sent_t_monde != witness.sent_t_monde
                    or report.observed_t_monde != witness.observed_t_monde
                ):
                    continue
                compatible = any(
                    variable == witness.variable
                    and status in {"conforming", "nonconforming"}
                    and observed == witness.observed_after
                    for variable, status, _predicted, observed, _tolerance, _version
                    in report.effects
                )
                if not compatible:
                    continue
                rule = NumericPredictionCorrection(
                    contingency_ref=contingency.ref,
                    intervention_ref=intervention_ref,
                    agency_evidence_ref=report.identifier,
                    command_primitive=witness.command_primitive,
                    command_target=witness.command_target,
                    variable=witness.variable,
                    observed_after=witness.observed_after,
                    observed_before_body=witness.observed_before_body,
                    observed_before_position=witness.observed_before_position,
                    observed_before_state_digest=witness.observed_before_state_digest,
                )
                rule.validate()
                rules.append(rule)
        return tuple(sorted(
            rules,
            key=lambda rule: (
                rule.contingency_ref, rule.intervention_ref,
                rule.agency_evidence_ref, rule.command_target or "",
                rule.observed_after,
            ),
        ))

    def published_agency_evidence(self) -> tuple[AgencyEvidence, ...]:
        """Only phase-5-published descriptive comparisons, never interventions."""
        return tuple(self._agency_evidence[key] for key in sorted(self._agency_evidence))

    def ingest_closed_agency_comparisons(
        self, *, episode_ref: str, event_refs: Sequence[str],
        autobiographical_events: Sequence[Mapping[str, object]],
    ) -> tuple[AgencyEvidence, ...]:
        """DC-09 Memory handoff; no technical-journal read or oracle labels.

        The comparison is an observed item of evidence; it never directly
        increments P-35 intervention/context counts or changes a status.
        """
        if not episode_ref:
            raise ValueError("closed Memory episode reference is mandatory")
        refs = set(event_refs)
        if len(refs) != len(event_refs):
            raise ValueError("repeated event reference within Memory episode")
        # Fail closed on source-ID collisions *before* decoding P-47.
        # Otherwise a repeated event ID with a different kind (or a
        # malformed comparison) can be silently ignored while its other
        # projection is accepted as independent evidence. Unrelated event
        # kinds from the same Memory episode do not enter this gate.
        closed_events = [
            event for event in autobiographical_events
            if event.get("event_id") in refs
        ]
        agency_source_refs = {
            event["event_id"] for event in closed_events
            if event.get("kind") == "agency_comparison"
        }
        agency_projection_refs = [
            event["event_id"] for event in closed_events
            if event["event_id"] in agency_source_refs
        ]
        if len(agency_projection_refs) != len(set(agency_projection_refs)):
            raise ValueError("duplicate closed Memory agency event projection")
        admitted: list[AgencyEvidence] = []
        for event in closed_events:
            report = agency_evidence_from_autobiography(
                episode_ref=episode_ref, event=event,
            )
            if report is not None:
                admitted.append(report)
        # Preflight the whole episode; no partial causal buffering if one
        # observation is duplicate or has inconsistent physical provenance.
        historical_refs = {v.event_ref for v in self._agency_evidence.values()}
        pending_refs = {v.event_ref for v in self._pending_agency_evidence}
        seen_in_batch: set[str] = set()
        for report in admitted:
            if (report.event_ref in historical_refs
                or report.event_ref in pending_refs
                or report.event_ref in seen_in_batch):
                raise ValueError("DC-09 comparator observation credited more than once")
            seen_in_batch.add(report.event_ref)
        self._pending_agency_evidence.extend(admitted)
        return tuple(admitted)

    def _lived_food_hypothesis_review(
        self,
        contingency: CanonicalContingency,
        observations: Mapping[str, CausalObservation],
    ) -> CausalHypothesisReview | None:
        """Make explicit only a preregistered alternative actually experienced.

        A different consumed food is a control only when the closed DC-09
        episode produced both its own positive exposure and the corresponding
        negative treatment observation. Typed control claims alone are not
        proof of a lived comparison. This produces NO test action or
        intervention, and never overrides the separate safety veto.
        """
        if (
            contingency.causal_status != "correlation_observee"
            or contingency.predicate != "toxic_item"
            or contingency.context_signature != "global"
        ):
            return None
        control_food = next((
            control for treatment, control in self.config.food_control_pairs
            if treatment == contingency.subject_ref
        ), None)
        if control_food is None:
            return None

        exposed: list[CausalObservation] = []
        controls: list[CausalObservation] = []
        for observation in observations.values():
            if (
                observation.contingency_ref != contingency.ref
                or observation.predicate != contingency.predicate
                or observation.subject_ref != contingency.subject_ref
                or observation.application_context != contingency.context_signature
                or observation.observation_context != "food_consumption"
                or observation.controlled_variables != (("primitive", "manger"),)
                or f"dc05:{observation.episode_ref}:{observation.observation_ref}"
                   not in self._seen_ids
            ):
                continue
            physical_id = (
                f"causal-observation:{observation.episode_ref}:"
                f"{observation.observation_ref}"
            )
            if observation.cause_present:
                if observation.identifier == physical_id and observation.effect_present:
                    exposed.append(observation)
                continue
            if observation.identifier != (
                f"causal-control:{contingency.subject_ref}:{physical_id}"
            ) or observation.effect_present:
                continue
            # The no-treatment record must have been generated from the
            # same real transition as eating the declared control food.
            actual_control = observations.get(physical_id)
            if (
                actual_control is None
                or actual_control.contingency_ref != f"toxic:{control_food}"
                or actual_control.predicate != "toxic_item"
                or actual_control.subject_ref != control_food
                or not actual_control.cause_present
                or actual_control.effect_present != observation.effect_present
                or actual_control.episode_ref != observation.episode_ref
                or actual_control.observation_ref != observation.observation_ref
                or actual_control.observed_step != observation.observed_step
                or actual_control.observation_context != observation.observation_context
                or actual_control.controlled_variables != observation.controlled_variables
            ):
                continue
            controls.append(observation)

        # The sorted controls are invariant across all exposed observations.
        # Sorting once preserves the exact first admissible pair and ranking.
        sorted_controls = sorted(controls, key=lambda row: row.identifier)
        for present in sorted(exposed, key=lambda row: row.identifier):
            for absent in sorted_controls:
                if (
                    present.observation_ref == absent.observation_ref
                    or present.observed_step == absent.observed_step
                    or present.observation_context != absent.observation_context
                    or present.controlled_variables != absent.controlled_variables
                ):
                    continue
                review = CausalHypothesisReview(
                    identifier=(
                        f"lived-food-review:{contingency.ref}:"
                        f"{present.identifier}:{absent.identifier}"
                    ),
                    contingency_ref=contingency.ref,
                    alternatives=(f"observed_control_food:{control_food}",),
                    contrasting_pairs=((present.identifier, absent.identifier),),
                )
                review.validate()
                return review
        return None

    def _lived_hydration_hypothesis_review(
        self, contingency: CanonicalContingency,
        observations: Mapping[str, CausalObservation],
    ) -> CausalHypothesisReview | None:
        """Explicit observed 'attendre' alternative, never a typed placebo.

        Both arms must have separately closed physical witnesses, distinct
        world transitions and steps, and the same water-source site.
        Autobiographical episode IDs are provenance, not causal sample IDs.
        """
        if (
            contingency.causal_status != "correlation_observee"
            or contingency.ref != "causal:hydration"
            or contingency.predicate != "hydration_effect"
            or contingency.subject_ref != "water"
            or contingency.context_signature != "water_source"
        ):
            return None
        observed = [
            value for value in observations.values()
            if value.identifier in self._hydration_observation_witnesses
            and value.contingency_ref == contingency.ref
            and value.predicate == contingency.predicate
            and value.application_context == contingency.context_signature
            and value.observation_context == "water_source"
            and value.controlled_variables
        ]
        treated = sorted(
            (value for value in observed if value.cause_present
             and value.effect_present),
            key=lambda value: value.identifier,
        )
        controls = sorted(
            (value for value in observed if not value.cause_present
             and not value.effect_present),
            key=lambda value: value.identifier,
        )
        # Recovered or directly validated observations may contain lists:
        # equality comparisons worked for them, but list-backed controls
        # cannot be used as dictionary keys. Never silently normalize proof.
        # Preserve the original ordered scan for these uncommon inputs.
        canonical_controls = all(
            type(row.controlled_variables) is tuple
            and all(type(pair) is tuple for pair in row.controlled_variables)
            for rows in (treated, controls) for row in rows
        )
        controls_by_context: dict[
            tuple[str, tuple[tuple[str, str], ...]], list[CausalObservation]
        ] = {}
        if canonical_controls:
            for baseline in controls:
                key = (baseline.observation_context, baseline.controlled_variables)
                controls_by_context.setdefault(key, []).append(baseline)
        for effect in treated:
            comparable = (
                controls_by_context.get(
                    (effect.observation_context, effect.controlled_variables), ()
                ) if canonical_controls else controls
            )
            for baseline in comparable:
                if (
                    effect.observation_ref == baseline.observation_ref
                    or effect.observed_step == baseline.observed_step
                    or effect.controlled_variables != baseline.controlled_variables
                    or effect.observation_context != baseline.observation_context
                ):
                    continue
                review = CausalHypothesisReview(
                    identifier=(
                        f"lived-hydration-review:{contingency.ref}:"
                        f"{effect.identifier}:{baseline.identifier}"
                    ),
                    contingency_ref=contingency.ref,
                    alternatives=("observed_primitive:attendre",),
                    contrasting_pairs=((
                        effect.identifier, baseline.identifier,
                    ),),
                )
                review.validate()
                return review
        return None

    def publish_causal_inference(self) -> tuple[CausalInferenceChange, ...]:
        """Publish independent §13.2 evidence atomically, with frozen input stages."""
        from collections import defaultdict
        from itertools import chain
        original = dict(self._published)
        published = dict(original)
        observations = dict(self._causal_observations)
        interventions = dict(self._causal_interventions)
        reviews = set(self._causal_reviews)
        correlation_witnesses = dict(self._causal_correlation_witnesses)
        review_proofs = dict(self._causal_review_proofs)
        credits = set(self._causal_credits)
        revisions = dict(self._causal_revision_boundaries)
        changes: list[CausalInferenceChange] = []

        # Cross-rule causal interpretations may share a physical transition,
        # but cannot manufacture a different Memory episode or world clock
        # for that single source. Check the whole batch before publication.
        # The verifier consumes its input exactly once. Do not allocate a
        # second full-history tuple solely to check shared lived provenance.
        _verify_shared_observation_provenance(chain(
            observations.values(), self._pending_causal_observations,
        ))

        # Most publication cycles have zero or one new observation. Build
        # this transient index only for batches large enough to amortize it.
        # It is not persistent evidence, memory or another causal owner.
        index_physical_sources = len(self._pending_causal_observations) >= 3
        first_physical: dict[tuple[str, str], CausalObservation] = {}
        if index_physical_sources:
            for prior in observations.values():
                first_physical.setdefault(
                    (prior.contingency_ref, prior.observation_ref), prior
                )

        # Batch arrival never bypasses the prior published lifecycle level.
        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):
            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:
                raise ValueError("unregistered causal predicate")
            key = (o.contingency_ref, o.observation_ref, "observation")
            # A colliding identifier may replace an earlier physical
            # source in the mapping. Keep exact old scan semantics for the
            # rest of this batch instead of retaining a stale indexed row.
            if index_physical_sources and o.identifier in observations:
                index_physical_sources = False
            if index_physical_sources:
                first = first_physical.get((o.contingency_ref, o.observation_ref))
                same_physical = (first,) if first is not None else ()
            else:
                same_physical = (
                    v for v in observations.values()
                    if v.contingency_ref == o.contingency_ref
                    and v.observation_ref == o.observation_ref
                )
            for existing in same_physical:
                # A second identifier for the same physical transition is
                # harmless only if every claim about its provenance and
                # observation matches. Merely comparing cause/effect labels
                # would silently discard a contradictory world step or
                # Memory episode, contaminating n1 provenance. Distinct
                # physical references remain independent even when an
                # autobiographical episode contains multiple transitions.
                if replace(existing, identifier=o.identifier) != o:
                    raise ValueError(
                        "conflicting causal labels for one physical observation"
                    )
                break
            else:
                if key in credits:
                    # Credits are always paired to accepted observations.
                    # A lone credit cannot justify silently losing a row.
                    raise ValueError("causal observation credit lacks its source")
                old = published.get(o.contingency_ref)
                if old is None:
                    old = CanonicalContingency(
                        ref=o.contingency_ref, version=1, predicate=o.predicate,
                        subject_ref=o.subject_ref, context_signature=o.application_context,
                        causal_status="aucun", safety_status="aucun",
                        evidence_refs=(), harmful_episodes=(), harmless_episodes=(),
                    )
                elif (old.predicate, old.subject_ref, old.context_signature) != (
                    o.predicate, o.subject_ref, o.application_context
                ):
                    raise ValueError("observation mismatches canonical contingency")
                credits.add(key)
                observations[o.identifier] = o
                if index_physical_sources:
                    first_physical.setdefault(
                        (o.contingency_ref, o.observation_ref), o
                    )
                published[o.contingency_ref] = old
                continue
            # An identical physical alias has no second P-35 credit.
            continue

        byref = defaultdict(list)
        for o in observations.values():
            byref[o.contingency_ref].append(o)
        for ref in sorted(byref):
            old = original.get(ref)
            current = published[ref]
            if old is not None and old.causal_status != "aucun":
                continue
            exposed = [x for x in byref[ref] if x.cause_present]
            control = [x for x in byref[ref] if not x.cause_present]
            if not control:
                continue
            # A control and a treated observation are compatible only if
            # BOTH the first-person observation context and their ordered,
            # witnessed controlled variables match exactly. Most native and
            # cold-imported records use hashable tuple-of-tuples controls.
            # Find shared keys instead of allocating the Cartesian product.
            if all(
                type(row.controlled_variables) is tuple
                and all(type(pair) is tuple for pair in row.controlled_variables)
                for row in byref[ref]
            ):
                exposed_keys = {
                    (x.observation_context, x.controlled_variables)
                    for x in exposed
                }
                control_keys = {
                    (y.observation_context, y.controlled_variables)
                    for y in control
                }
                shared_keys = exposed_keys & control_keys
                if not shared_keys:
                    continue
                e = {
                    x.identifier: x for x in exposed
                    if (x.observation_context, x.controlled_variables)
                    in shared_keys
                }
                b = {
                    y.identifier: y for y in control
                    if (y.observation_context, y.controlled_variables)
                    in shared_keys
                }
            else:
                # A directly integrated record may use list-valued controls,
                # which CausalObservation.validate() also accepts. Preserve
                # the original list/tuple equality semantics exactly for
                # these noncanonical, potentially unhashable representations.
                e = {}
                b = {}
                for x in exposed:
                    for y in control:
                        if (
                            x.observation_context == y.observation_context
                            and x.controlled_variables == y.controlled_variables
                        ):
                            e[x.identifier] = x
                            b[y.identifier] = y
                if not e:
                    continue
            # P-35 n1 counts DISTINCT cause+effect observations, never
            # duplicate treated/control PAIRS for the same physical record.
            confirmed = {
                x.identifier for x in e.values() if x.effect_present
            }
            if len(confirmed) < self.config.n1:
                continue
            # Already counted distinct positive exposed identifiers above.
            if len(confirmed) * len(b) <= (
                sum(y.effect_present for y in b.values()) * len(e)
            ):
                continue
            new = replace(current, causal_status="correlation_observee", version=current.version + 1)
            published[ref] = new
            treated_ids = tuple(sorted(e))
            control_ids = tuple(sorted(b))
            correlation_witnesses[ref] = (treated_ids, control_ids)
            changes.append(CausalInferenceChange(ref, current.causal_status, new.causal_status, new.version, treated_ids[-1], "controlled_base_rate"))

        # An already published correlation may autonomously become a
        # hypothesis when the preregistered alternative was *physically*
        # observed in distinct world transitions, even in the same closed
        # episode. Newly correlated facts
        # cannot skip a publication stage in this batch.
        pending_review_refs = {
            review.contingency_ref for review in self._pending_causal_reviews
        }
        lived_reviews = tuple(
            review
            for ref, record in sorted(original.items())
            if ref not in pending_review_refs
            # Each reviewer requires a distinct predicate. Never invoke
            # both expensive observation scans for the same contingency.
            for review in (
                (
                    self._lived_food_hypothesis_review(record, observations)
                    if record.predicate == "toxic_item" else
                    self._lived_hydration_hypothesis_review(record, observations)
                    if record.predicate == "hydration_effect" else None
                ),
            )
            if review is not None
        )
        for review in sorted(
            (*self._pending_causal_reviews, *lived_reviews),
            key=lambda x: x.identifier,
        ):
            old = original.get(review.contingency_ref)
            if old is None or old.causal_status != "correlation_observee":
                raise ValueError("review requires previously published correlation")
            for a_ref, b_ref in review.contrasting_pairs:
                a, b = observations.get(a_ref), observations.get(b_ref)
                if (a is None or b is None or a.contingency_ref != old.ref
                    or b.contingency_ref != old.ref or not a.cause_present
                    or b.cause_present or a.controlled_variables != b.controlled_variables
                    or a.observation_context != b.observation_context
                    or a.observation_ref == b.observation_ref
                    or a.observed_step == b.observed_step):
                    raise ValueError("review lacks independent matched controls")
            reviews.add(review.identifier)
            review_proofs[review.identifier] = review
            current = published[old.ref]
            # Multiple independently supported reviews may share a phase-5
            # batch. Keep their provenance, but promote the canonical
            # contingency only once: a hypothesis cannot transition to
            # the same status again or gain a fictitious new version.
            if current.causal_status != "correlation_observee":
                continue
            new = replace(current, causal_status="hypothese_causale", version=current.version + 1)
            published[old.ref] = new
            changes.append(CausalInferenceChange(old.ref, current.causal_status, new.causal_status, new.version, review.identifier, "matched_alternatives"))

        # Build a private, per-publication lookup from already accepted
        # intervention witnesses. These lists are not part of any causal
        # snapshot and do not provide evidence or a cross-step trust cache.
        # Index each newly credited trial immediately, so later rows in the
        # same sorted pending batch see precisely the same earlier witnesses.
        prior_by_physical = defaultdict(list)
        prior_by_comparator = defaultdict(list)
        prior_by_emitted = defaultdict(list)
        prior_by_observed = defaultdict(list)
        positive_by_ref = defaultdict(list)
        # One transient context set per contingency/revision, enabled only
        # for larger batches. Refutation invalidates every pre-boundary count.
        reuse_positive_contexts = len(self._pending_causal_interventions) >= 3
        positive_contexts_by_ref: dict[str, tuple[int, set[str]]] = {}

        def index_admitted_trial(item: CausalIntervention) -> None:
            prior_by_physical[item.observation_ref].append(item)
            prior_by_comparator[
                (item.contingency_ref, item.comparator_ref)
            ].append(item)
            prior_by_emitted[
                (item.contingency_ref, item.emitted_step)
            ].append(item)
            prior_by_observed[
                (item.contingency_ref, item.observed_step)
            ].append(item)
            if item.observed_effect and item.attribution == "self_compatible":
                positive_by_ref[item.contingency_ref].append(item)
                # Only already admitted physical evidence may extend an
                # existing context view, and only beyond its revision bound.
                if reuse_positive_contexts:
                    cached = positive_contexts_by_ref.get(item.contingency_ref)
                    if cached is not None and item.observed_step > cached[0]:
                        cached[1].add(item.context_signature)

        for item in interventions.values():
            index_admitted_trial(item)

        for trial in sorted(self._pending_causal_interventions, key=lambda x: (x.observed_step, x.identifier)):
            old = original.get(trial.contingency_ref)
            if old is None or old.causal_status not in {
                "hypothese_causale", "testee_par_intervention", "etablie"
            }:
                raise ValueError("intervention needs previously published hypothesis")
            # A typed declaration cannot establish causal status by itself.
            # Only already published, Memory-closed AgencyComparator evidence
            # can support the phase-5 admission of a lived intervention.
            report = self._agency_evidence.get(trial.comparator_ref)
            if not self._published_comparison_supports(trial, report):
                raise ValueError(
                    "intervention requires matching previously published DC-09 agency comparison"
                )
            # For the supported live Stage-9 drinking-test protocol, a
            # comparison alone cannot certify an action: the canonical owner
            # also requires its already closed and Perception-corroborated
            # physical witness. This check applies to manually integrated
            # typed trials as well as to the autonomous producer.
            if (
                (old.predicate, old.subject_ref, "boire")
                in self.config.safe_test_actions
                and not self._verified_lived_drink_intervention(
                    trial, self._causal_action_witnesses.get(trial.identifier),
                    report,
                )
            ):
                raise ValueError(
                    "intervention requires matching closed physical action evidence"
                )
            # A Memory episode may contain several physically distinct
            # interventions. Its identifier does not prove uniqueness: count
            # each observed transition once, and reject reused P-47 outcomes
            # or repeated emission/observation world-step claims for the same
            # contingency. Different event IDs pointing to the same observed
            # step cannot manufacture an additional independent context.
            key = (trial.contingency_ref, trial.observation_ref, "intervention")
            # All four index predicates exactly match the previous scan of
            # interventions.values(). A witness may appear in several index
            # buckets; repeated references do not change the existential
            # alias/conflict check below, or the fact that any reuse denies
            # a second intervention credit.
            prior_uses = tuple(chain(
                prior_by_physical.get(trial.observation_ref, ()),
                prior_by_comparator.get(
                    (trial.contingency_ref, trial.comparator_ref), ()
                ),
                prior_by_emitted.get(
                    (trial.contingency_ref, trial.emitted_step), ()
                ),
                prior_by_observed.get(
                    (trial.contingency_ref, trial.observed_step), ()
                ),
            ))
            # A reused physical source grants no extra n2 credit. It is only
            # a harmless alias if every physical claim matches: action,
            # Memory episode, context, controls, world steps, comparator,
            # and outcome. Checking outcomes alone misses fabricated context
            # changes that could hide a contradictory observation. Normalize
            # only the row identifier; dataclass equality covers all other
            # present and future physical provenance fields.
            # Other contingencies may describe other effects of the same
            # source but still receive no second intervention credit here.
            if any(
                other.contingency_ref == trial.contingency_ref
                and replace(other, identifier=trial.identifier) != trial
                for other in prior_uses
            ):
                raise ValueError(
                    "conflicting causal intervention claims for one physical source"
                )
            if key in credits or prior_uses:
                continue
            credits.add(key)
            interventions[trial.identifier] = trial
            index_admitted_trial(trial)
            current = published[old.ref]
            if not trial.observed_effect:
                # A failed lived intervention invalidates the assumption
                # that earlier positive contexts still demonstrate a
                # persistent effect. Only an established claim is demoted;
                # tested hypotheses retain their status but must accumulate
                # fresh, subsequent contexts before establishment.
                previous_boundary = revisions.get(old.ref, (-1, ""))[0]
                if trial.observed_step > previous_boundary:
                    revisions[old.ref] = (trial.observed_step, trial.identifier)
                    # Old positive contexts can no longer establish the claim.
                    if reuse_positive_contexts:
                        positive_contexts_by_ref.pop(old.ref, None)
                # An earlier successful trial in this *same* phase-5 batch
                # can have established the claim. A later real counterexample
                # must revoke that status, even if the batch's frozen input
                # was only "testee_par_intervention". Do not treat the stale
                # input status as the current epistemic state.
                next_status = (
                    "hypothese_causale"
                    if current.causal_status == "etablie"
                    else current.causal_status
                )
            else:
                boundary = revisions.get(old.ref, (-1, ""))[0]
                # Check only positive, self-compatible interventions of
                # this contingency, including earlier accepted batch rows.
                # The source list stays authoritative. Cached context sets
                # are local to this publication and this exact revision.
                cached = (
                    positive_contexts_by_ref.get(old.ref)
                    if reuse_positive_contexts else None
                )
                if cached is None or cached[0] != boundary:
                    contexts = {
                        x.context_signature for x in positive_by_ref.get(old.ref, ())
                        if x.observed_step > boundary
                    }
                    if reuse_positive_contexts:
                        positive_contexts_by_ref[old.ref] = (boundary, contexts)
                else:
                    contexts = cached[1]
                if trial.observed_effect and old.causal_status == "hypothese_causale":
                    next_status = "testee_par_intervention"
                elif trial.observed_effect and old.causal_status == "testee_par_intervention" and len(contexts) >= self.config.n2:
                    next_status = "etablie"
                else:
                    next_status = current.causal_status
            if next_status != current.causal_status:
                new = replace(current, causal_status=next_status, version=current.version + 1)
                published[old.ref] = new
                changes.append(CausalInferenceChange(old.ref, current.causal_status, next_status, new.version, trial.identifier, "independent_intervention"))

        # When independent physical interventions were admitted together,
        # the frozen input level prevents skipping hypothesis -> tested ->
        # established in one batch. On a later publication, already credited
        # distinct contexts can complete n2 even with no new intervention.
        # A failed observation since the last valid context prevents this.
        for ref, previous in sorted(original.items()):
            if (
                previous.causal_status != "testee_par_intervention"
                or published[ref].causal_status != "testee_par_intervention"
            ):
                continue
            boundary = revisions.get(ref, (-1, ""))[0]
            successful = [
                item for item in positive_by_ref.get(ref, ())
                if item.observed_step > boundary
            ]
            if len({item.context_signature for item in successful}) < self.config.n2:
                continue
            current = published[ref]
            # The previous sorted(...)[-1] chose the greatest observed
            # (world-step, identifier) pair. Select the same witness without
            # sorting every historical success of this contingency.
            witness = max(
                successful, key=lambda item: (item.observed_step, item.identifier)
            )
            new = replace(
                current, causal_status="etablie", version=current.version + 1,
            )
            published[ref] = new
            changes.append(CausalInferenceChange(
                ref, current.causal_status, new.causal_status, new.version,
                witness.identifier, "independent_intervention",
            ))

        # Comparator descriptions do not influence causal or safety statuses.
        # Publish them only after all staged inference validations succeed.
        agency = dict(self._agency_evidence)
        # Build an ephemeral index of physical references present in the
        # current mapping. Identifier replacements must not leave stale refs.
        agency_event_refs = {report.event_ref for report in agency.values()}
        for report in sorted(
            self._pending_agency_evidence,
            key=lambda value: (value.observed_t_monde, value.event_ref),
        ):
            if report.event_ref in agency_event_refs:
                raise ValueError("duplicate published physical agency observation")
            displaced = agency.get(report.identifier)
            if displaced is not None and not any(
                other.event_ref == displaced.event_ref
                for key, other in agency.items()
                if key != report.identifier
            ):
                # An overwritten report no longer occupies its old source.
                # This rare fallback preserves exact previous semantics.
                agency_event_refs.discard(displaced.event_ref)
            agency[report.identifier] = report
            agency_event_refs.add(report.event_ref)
        numeric = dict(self._numeric_witnesses)
        # One transient index per publication. The identifier guard rejects
        # overwrites, so every accepted physical reference stays present.
        numeric_transition_refs = {
            prior.transition_event_ref for prior in numeric.values()
        }
        for witness in sorted(
            self._pending_numeric_witnesses, key=lambda row: row.identifier,
        ):
            witness.validate()
            if (
                witness.identifier in numeric
                or witness.transition_event_ref in numeric_transition_refs
            ):
                raise ValueError("duplicate published physical numeric witness")
            numeric[witness.identifier] = witness
            numeric_transition_refs.add(witness.transition_event_ref)
        self._published = published
        self._numeric_witnesses = numeric
        self._pending_numeric_witnesses.clear()
        self._agency_evidence = agency
        self._causal_observations = observations
        # Suppressed duplicates of a physical transition cannot retain
        # their witness and support a future uncredited causal review.
        self._hydration_observation_witnesses = {
            ref: pair for ref, pair in self._hydration_observation_witnesses.items()
            if ref in observations
        }
        self._causal_interventions = interventions
        self._causal_reviews = reviews
        self._causal_correlation_witnesses = correlation_witnesses
        self._causal_review_proofs = review_proofs
        self._causal_credits = credits
        self._causal_revision_boundaries = revisions
        self._pending_causal_observations.clear()
        self._pending_causal_reviews.clear()
        self._pending_causal_interventions.clear()
        self._pending_agency_evidence.clear()
        self._version += 1
        return tuple(changes)

    def integrate(self, evidence: SafetyEvidence) -> None:
        evidence.validate()
        if evidence.epistemic_status != "dc05_admissible":
            raise ValueError("ambiguous association cannot receive DC-05 credit")  # INV-03/27: reject before any causal write.
        if (
            evidence.identifier in self._seen_ids
            or any(v.identifier == evidence.identifier for v in self._pending)
        ):
            raise ValueError("duplicate causal evidence identifier")
        self._pending.append(evidence)

    def publish(self) -> tuple[CausalStatusChange, ...]:
        """End-of-cycle atomic visibility for all pending DC-05 updates."""
        published = dict(self._published)
        episodes = set(self._credited_episodes)
        observations = set(self._credited_observations)
        seen = set(self._seen_ids)
        admitted = list(self._admitted_safety_evidence)
        changes: list[CausalStatusChange] = []
        for e in sorted(
            self._pending,
            key=lambda v: (v.observation_step, v.emission_step, v.identifier),
        ):
            seen.add(e.identifier)
            episode_key = (e.contingency_ref, e.episode_ref)
            observation_key = (e.contingency_ref, e.observation_ref)
            if episode_key in episodes or observation_key in observations:
                continue
            episodes.add(episode_key)
            observations.add(observation_key)
            admitted.append(e)
            current = published.get(e.contingency_ref)
            if current is None:
                current = CanonicalContingency(
                    ref=e.contingency_ref, version=1,
                    predicate=e.predicate, subject_ref=e.subject_ref,
                    context_signature=e.context_signature,
                    causal_status="aucun", safety_status="aucun",
                    evidence_refs=(), harmful_episodes=(), harmless_episodes=(),
                )
            elif (
                current.predicate != e.predicate
                or current.subject_ref != e.subject_ref
                or current.context_signature != e.context_signature
            ):
                raise ValueError("DC-05 incompatible evidence for canonical contingency")

            old_status = current.safety_status
            harmful = current.harmful_episodes
            harmless = current.harmless_episodes
            if e.harm_observed:
                harmful = harmful + (e.episode_ref,)
                harmless = ()
                if old_status != "etabli_pour_securite" and len(harmful) >= self.config.n_sec:
                    new_status = "etabli_pour_securite"
                else:
                    new_status = old_status
            else:
                harmless = harmless + (e.episode_ref,)
                if old_status == "aucun":
                    # Contrary lived experience invalidates a run of supporting
                    # episodes: DC-05 forbids promotion across contradictions.
                    harmful = ()
                    new_status = old_status
                elif not current.innate and len(harmless) >= self.config.m_sec:
                    new_status = "aucun"
                    harmful = ()
                else:
                    new_status = old_status

            revised = replace(
                current, version=current.version + (1 if current.evidence_refs else 0),
                safety_status=new_status,
                evidence_refs=current.evidence_refs + (e.identifier,),
                harmful_episodes=harmful,
                harmless_episodes=harmless,
            )
            revised.validate()
            published[e.contingency_ref] = revised
            if old_status != new_status:
                changes.append(CausalStatusChange(
                    contingency_ref=e.contingency_ref,
                    before=old_status, after=new_status,
                    version=revised.version,
                    evidence_ref=e.identifier,
                    episode_ref=e.episode_ref,
                ))
        # Nothing is published if any batched event is inconsistent.
        self._published = published
        self._credited_episodes = episodes
        self._credited_observations = observations
        self._seen_ids = seen
        self._admitted_safety_evidence = admitted
        self._pending.clear()
        self._version += 1
        return tuple(changes)

    def export_causal_state(self) -> object:
        state = {
            "config_version": self.config.version,
            "config_contract": {
                "n1": self.config.n1, "n2": self.config.n2,
                "n_sec": self.config.n_sec, "m_sec": self.config.m_sec,
                "causal_predicates": list(self.config.causal_predicates),
                "food_control_pairs": [list(pair) for pair in self.config.food_control_pairs],
                "safe_test_actions": [list(row) for row in self.config.safe_test_actions],
            },
            "version": self._version,
            "published": [
                {name: getattr(c, name) for name in c.__dataclass_fields__}
                for _, c in sorted(self._published.items())
            ],
            "pending": [
                self._serialize_safety_evidence(e)
                for e in self._pending
            ],
            "seen": sorted(self._seen_ids),
            "admitted_safety_evidence": [
                self._serialize_safety_evidence(e)
                for e in self._admitted_safety_evidence
            ],
            # Detect accidental or partial damage even where a changed lived
            # event happens to yield identical *final* status counters.
            # The external hash-chained journal remains authoritative.
            "admitted_safety_evidence_sha256": self._safety_ledger_sha256(
                self._admitted_safety_evidence
            ),
            "episodes": [list(x) for x in sorted(self._credited_episodes)],
            "observations": [list(x) for x in sorted(self._credited_observations)],
            "causal_observations": [serialize_value(x) for _,x in sorted(self._causal_observations.items())],
            "causal_interventions": [serialize_value(x) for _,x in sorted(self._causal_interventions.items())],
            "causal_reviews": sorted(self._causal_reviews),
            "causal_correlation_witnesses": [
                [ref, list(treated), list(controls)]
                for ref, (treated, controls)
                in sorted(self._causal_correlation_witnesses.items())
            ],
            "causal_review_proofs": [
                serialize_value(review)
                for _, review in sorted(self._causal_review_proofs.items())
            ],
            "causal_credits": [list(x) for x in sorted(self._causal_credits)],
            "agency_evidence": [serialize_value(v) for _, v in sorted(self._agency_evidence.items())],
            "pending_agency_evidence": [serialize_value(v) for v in self._pending_agency_evidence],
            "causal_revision_boundaries": [
                [key, step, ref] for key, (step, ref) in sorted(self._causal_revision_boundaries.items())
            ],
            "pending_causal_observations": [serialize_value(x) for x in self._pending_causal_observations],
            "pending_causal_reviews": [serialize_value(x) for x in self._pending_causal_reviews],
            "pending_causal_interventions": [serialize_value(x) for x in self._pending_causal_interventions],
            "numeric_witnesses": [
                {name: getattr(w, name) for name in w.__dataclass_fields__}
                for _, w in sorted(self._numeric_witnesses.items())
            ],
            "pending_numeric_witnesses": [
                {name: getattr(w, name) for name in w.__dataclass_fields__}
                for w in self._pending_numeric_witnesses
            ],
            "lived_food_exposures": [
                {
                    **{
                        name: getattr(v, name) for name in v.__dataclass_fields__
                        if name != "visible_creature_at_exposure"
                    },
                    # Do not change historic Stage 9–11 digest formats when
                    # the optional lived competitor flag is absent/false.
                    **({"visible_creature_at_exposure": True}
                       if v.visible_creature_at_exposure else {}),
                }
                for _, v in sorted(self._lived_food_exposures.items())
            ],
            "lived_hydration_exposures": [
                {
                    **{name: getattr(v, name) for name in v.__dataclass_fields__},
                    "position": list(v.position),
                }
                for _, v in sorted(self._lived_hydration_exposures.items())
            ],
            "hydration_observation_witnesses": [
                [ref, command_ref, transition_ref]
                for ref, (command_ref, transition_ref)
                in sorted(self._hydration_observation_witnesses.items())
            ],
            "lived_causal_actions": [
                {
                    **{name: getattr(v, name) for name in v.__dataclass_fields__},
                    "position": list(v.position),
                }
                for _, v in sorted(self._lived_causal_actions.items())
            ],
            "causal_action_witnesses": [
                {
                    "intervention_ref": trial_ref,
                    **{name: getattr(v, name) for name in v.__dataclass_fields__},
                    "position": list(v.position),
                }
                for trial_ref, v in sorted(self._causal_action_witnesses.items())
            ],
        }
        # Exact backward compatibility: historic no-control snapshots and
        # their hash-chained Stage-11 journal digests must not gain an empty
        # field purely because this optional safeguard now exists.
        if self._lived_ambient_integrity_controls:
            state["lived_ambient_integrity_controls"] = [
                {
                    **{name: getattr(v, name) for name in v.__dataclass_fields__},
                    "position": list(v.position),
                }
                for _, v in sorted(self._lived_ambient_integrity_controls.items())
            ]
        return state

    @staticmethod
    def _serialize_safety_evidence(row: SafetyEvidence) -> dict[str, object]:
        payload = {
            name: getattr(row, name)
            for name in row.__dataclass_fields__
            if name != "epistemic_status"
        }
        # Preserve historical snapshot bytes/digests for ordinary admissible
        # DC-05 evidence. Only non-default epistemic classifications need the
        # new field, and ambiguous rows are never admitted to the credit ledger.
        if row.epistemic_status != "dc05_admissible":
            payload["epistemic_status"] = row.epistemic_status
        return payload

    @staticmethod
    def _safety_ledger_sha256(rows: Sequence[SafetyEvidence]) -> str:
        payload = [
            CausalModel._serialize_safety_evidence(row)
            for row in rows
        ]
        return sha256(dumps(
            payload, sort_keys=True, ensure_ascii=False,
            allow_nan=False, separators=(",", ":"),
        ).encode("utf-8")).hexdigest()

    def restore_causal_state(self, state: object) -> None:
        """Validate a whole snapshot before changing this canonical owner.

        The decoder has late-stage provenance checks (physical outcomes,
        P-47 reports, and witnessed actions). It must never leave the live
        owner half-restored when a later row is invalid. Construct a fresh
        private candidate, validate it completely, then atomically replace
        the state of this *same* externally referenced owner.
        """
        replacement = type(self)(self.config)
        replacement._restore_causal_state_unchecked(state)
        # Commit only canonical-owned fields. Preserve non-state instance
        # instrumentation (e.g. a phase-5 failure hook) and references to
        # this owner, rather than replacing its whole attribute namespace.
        self.__dict__.update(replacement.__dict__)

    def _restore_causal_state_unchecked(self, state: object) -> None:
        if not isinstance(state, Mapping) or state.get("config_version") != self.config.version:
            raise ValueError("causal model snapshot config mismatch")
        expected_contract = {
            "n1": self.config.n1, "n2": self.config.n2,
            "n_sec": self.config.n_sec, "m_sec": self.config.m_sec,
            "causal_predicates": list(self.config.causal_predicates),
            "food_control_pairs": [list(pair) for pair in self.config.food_control_pairs],
            "safe_test_actions": [list(row) for row in self.config.safe_test_actions],
        }
        if state.get("config_contract") != expected_contract:
            raise ValueError("causal model snapshot protocol mismatch")
        records = {}
        for raw in state["published"]:
            c = CanonicalContingency(
                **{key: tuple(value) if key in {
                    "evidence_refs", "harmful_episodes", "harmless_episodes",
                } else value for key, value in raw.items()}
            )
            c.validate()
            if c.ref in records:
                raise ValueError("duplicate canonical contingency in snapshot")
            records[c.ref] = c
        pending = [SafetyEvidence(**row) for row in state["pending"]]
        for e in pending:
            e.validate()
        # DC-05 / INV-33: safety evidence also has a publication ledger.
        # A snapshot must not silently collapse duplicate identities, erase
        # credited episodes, or restore an unearned safety veto.
        episode_rows = state["episodes"]
        observation_rows = state["observations"]
        for rows in (episode_rows, observation_rows):
            if any(
                not isinstance(row, (tuple, list))
                or len(row) != 2
                or any(not isinstance(value, str) or not value for value in row)
                for row in rows
            ):
                raise ValueError("invalid safety physical credit key")
        episodes = {tuple(row) for row in episode_rows}
        observations = {tuple(row) for row in observation_rows}
        if (
            len(episodes) != len(episode_rows)
            or len(observations) != len(observation_rows)
        ):
            raise ValueError("duplicate safety physical credit in snapshot")
        seen_rows = list(state["seen"])
        if (
            any(not isinstance(ref, str) or not ref for ref in seen_rows)
            or len(seen_rows) != len(set(seen_rows))
        ):
            raise ValueError("invalid or duplicate seen safety evidence identity")
        pending_refs = [e.identifier for e in pending]
        if (
            len(pending_refs) != len(set(pending_refs))
            or not set(pending_refs).isdisjoint(seen_rows)
        ):
            raise ValueError("pending safety evidence collides with seen identity")
        accepted_refs = [
            ref for record in records.values() for ref in record.evidence_refs
        ]
        if (
            len(accepted_refs) != len(set(accepted_refs))
            or not set(accepted_refs).issubset(seen_rows)
        ):
            raise ValueError("unwitnessed published safety evidence reference")
        ledger = [SafetyEvidence(**row) for row in state.get("admitted_safety_evidence", [])]
        for row in ledger:
            row.validate()
        if (
            state.get("admitted_safety_evidence_sha256")
            != self._safety_ledger_sha256(ledger)
        ):
            raise ValueError("safety snapshot ledger digest mismatch")
        if (
            len({row.identifier for row in ledger}) != len(ledger)
            or {row.identifier for row in ledger} != set(accepted_refs)
            or {(row.contingency_ref, row.episode_ref) for row in ledger} != episodes
            or {(row.contingency_ref, row.observation_ref) for row in ledger} != observations
        ):
            raise ValueError("safety snapshot admitted evidence ledger mismatch")
        # Every admitted safety episode adds one episode credit, one physical
        # observation credit and one reference. The seen ledger may be longer:
        # duplicate or nonindependent evidence is recorded as already seen.
        if not (
            len(accepted_refs) == len(episodes) == len(observations)
        ):
            raise ValueError("safety snapshot credits mismatch published evidence")
        # Global totals alone are not sufficient: a corrupted snapshot could
        # reassign one physical credit to another contingency while keeping
        # both global counts unchanged.
        if any(ref not in records for ref, _ in episodes | observations):
            raise ValueError("safety snapshot credit refers to unknown contingency")
        for record in records.values():
            earned = {
                episode for contingency, episode in episodes
                if contingency == record.ref
            }
            observed_for_ref = {
                observation for contingency, observation in observations
                if contingency == record.ref
            }
            if (
                len(earned) != len(record.evidence_refs)
                or len(observed_for_ref) != len(record.evidence_refs)
            ):
                raise ValueError("safety snapshot credits mismatch contingency")
            if (
                not set(record.harmful_episodes).issubset(earned)
                or not set(record.harmless_episodes).issubset(earned)
                or len(record.harmful_episodes) != len(set(record.harmful_episodes))
                or len(record.harmless_episodes) != len(set(record.harmless_episodes))
            ):
                raise ValueError("safety snapshot episode provenance mismatch")
            if (
                record.safety_status == "etabli_pour_securite"
                and not record.innate
                and len(record.harmful_episodes) < self.config.n_sec
            ):
                raise ValueError("safety snapshot status lacks independent harm evidence")
        # Replay actual admissible physical harm/no-harm history. Unlike
        # counters alone, this checks promotion AND demotion chronology.
        derived = {}
        for e in ledger:
            prev = derived.get(e.contingency_ref)
            if prev is None:
                prev = CanonicalContingency(
                    ref=e.contingency_ref, version=1, predicate=e.predicate,
                    subject_ref=e.subject_ref, context_signature=e.context_signature,
                    causal_status="aucun", safety_status="aucun",
                    evidence_refs=(), harmful_episodes=(), harmless_episodes=(),
                )
            if (prev.predicate, prev.subject_ref, prev.context_signature) != (
                e.predicate, e.subject_ref, e.context_signature
            ):
                raise ValueError("safety snapshot evidence ledger context mismatch")
            harm, safe, status = prev.harmful_episodes, prev.harmless_episodes, prev.safety_status
            if e.harm_observed:
                harm, safe = harm + (e.episode_ref,), ()
                if status != "etabli_pour_securite" and len(harm) >= self.config.n_sec:
                    status = "etabli_pour_securite"
            else:
                safe = safe + (e.episode_ref,)
                if status == "aucun":
                    harm = ()
                elif len(safe) >= self.config.m_sec:
                    status, harm = "aucun", ()
            derived[e.contingency_ref] = replace(
                prev, safety_status=status,
                evidence_refs=prev.evidence_refs + (e.identifier,),
                harmful_episodes=harm, harmless_episodes=safe,
            )
        for ref, actual in records.items():
            if actual.innate:
                continue
            expected = derived.get(ref)
            if expected is None:
                if actual.evidence_refs:
                    raise ValueError("safety snapshot ledger missing evidence")
                continue
            if any((
                expected.safety_status != actual.safety_status,
                expected.evidence_refs != actual.evidence_refs,
                expected.harmful_episodes != actual.harmful_episodes,
                expected.harmless_episodes != actual.harmless_episodes,
            )):
                raise ValueError("safety snapshot ledger status history mismatch")
        version = state["version"]
        if not isinstance(version, int) or version < 0:
            raise ValueError("invalid causal model version")
        self._published = records
        self._pending = pending
        self._credited_episodes = episodes
        self._credited_observations = observations
        self._seen_ids = set(seen_rows)
        self._admitted_safety_evidence = ledger
        exposure_rows = state.get("lived_food_exposures", [])
        exposures = {}
        for raw in exposure_rows:
            exposure = LivedFoodExposure(**raw)
            exposure.validate()
            if exposure.t_monde in exposures:
                raise ValueError("duplicate pending lived exposure")
            exposures[exposure.t_monde] = exposure
        self._lived_food_exposures = exposures
        controls: dict[int, LivedAmbientIntegrityControl] = {}
        used_control_sources: set[str] = set()
        for raw in state.get("lived_ambient_integrity_controls", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid ambient-control snapshot row")
            item = LivedAmbientIntegrityControl(**{
                **raw, "position": tuple(raw["position"]),
            })
            item.validate()
            if (
                item.t_monde in controls
                or (item.command_ref is not None
                    and (item.command_ref in used_control_sources
                         or item.transition_ref in used_control_sources))
            ):
                raise ValueError("duplicate lived ambient-control provenance")
            controls[item.t_monde] = item
            if item.command_ref is not None:
                used_control_sources.add(item.command_ref)
                used_control_sources.add(item.transition_ref)
        self._lived_ambient_integrity_controls = controls
        hydration = {}
        for raw in state.get("lived_hydration_exposures", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid pending hydration exposure")
            row = LivedHydrationExposure(**{
                **raw, "position": tuple(raw["position"]),
            })
            row.validate()
            if row.t_monde in hydration:
                raise ValueError("duplicate pending hydration exposure")
            hydration[row.t_monde] = row
        self._lived_hydration_exposures = hydration
        water_witnesses = {}
        used_transitions = set()
        for row in state.get("hydration_observation_witnesses", []):
            if (
                not isinstance(row, (list, tuple))
                or len(row) != 3
                or any(not isinstance(value, str) or not value for value in row)
            ):
                raise ValueError("invalid hydration observation witness")
            ref, command_ref, transition_ref = row
            if (
                ref in water_witnesses or command_ref == transition_ref
                or transition_ref in used_transitions
            ):
                raise ValueError("duplicate hydration physical evidence")
            water_witnesses[ref] = (command_ref, transition_ref)
            used_transitions.add(transition_ref)
        self._hydration_observation_witnesses = water_witnesses
        actions = {}
        for raw in state.get("lived_causal_actions", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid pending lived causal action")
            row = LivedCausalAction(**{
                **raw, "position": tuple(raw["position"]),
            })
            row.validate()
            if row.identifier in actions:
                raise ValueError("duplicated pending lived causal action")
            actions[row.identifier] = row
        self._lived_causal_actions = actions
        witnesses = {}
        for raw in state.get("causal_action_witnesses", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid closed causal action witness")
            trial_ref = raw.get("intervention_ref")
            if not isinstance(trial_ref, str):
                raise ValueError("missing causal action witness intervention reference")
            witness = LivedCausalAction(**{
                **{k: v for k, v in raw.items() if k != "intervention_ref"},
                "position": tuple(raw["position"]),
            })
            witness.validate()
            if (
                witness.physical_episode_ref is None
                or witness.command_event_ref is None
                or witness.transition_event_ref is None
                or trial_ref != f"intervention:{witness.identifier}"
                or trial_ref in witnesses
            ):
                raise ValueError("invalid or duplicate closed causal action witness")
            witnesses[trial_ref] = witness
        if any(
            witness.identifier in actions
            for witness in witnesses.values()
        ):
            raise ValueError("closed causal action may not remain pending")
        self._causal_action_witnesses = witnesses
        # INV-33 / DC-08: a snapshot must round-trip exactly. A dictionary
        # comprehension would silently discard repeated causal rows, while a
        # set would erase duplicated credits. Reject identity collisions
        # before constructing the restored canonical collections.
        observation_rows = [
            decode_observation(v) for v in state.get("causal_observations", [])
        ]
        pending_obs = [
            decode_observation(v) for v in state.get("pending_causal_observations", [])
        ]
        all_observation_refs = [
            row.identifier for row in (*observation_rows, *pending_obs)
        ]
        if len(all_observation_refs) != len(set(all_observation_refs)):
            raise ValueError("duplicate causal observation identity in snapshot")
        obs = {row.identifier: row for row in observation_rows}
        # Phase-5 admits at most one physical transition per contingency.
        # Different episode/record IDs cannot convert the same experienced
        # transition into two independent n1 observations after replay.
        observation_physical_refs = [
            (row.contingency_ref, row.observation_ref)
            for row in observation_rows
        ]
        if len(observation_physical_refs) != len(set(observation_physical_refs)):
            raise ValueError(
                "causal snapshot reuses published observational physical transition"
            )
        _verify_shared_observation_provenance(observation_rows)

        intervention_rows = [
            decode_intervention(v) for v in state.get("causal_interventions", [])
        ]
        pending_trial = [
            decode_intervention(v) for v in state.get("pending_causal_interventions", [])
        ]
        all_intervention_refs = [
            row.identifier for row in (*intervention_rows, *pending_trial)
        ]
        if len(all_intervention_refs) != len(set(all_intervention_refs)):
            raise ValueError("duplicate causal intervention identity in snapshot")
        trials = {row.identifier: row for row in intervention_rows}
        # Preserve the same physical-independence gates as phase-5 admission:
        # an actual world transition may back at most one intervention and
        # one contingency may not count the same comparator or world step
        # twice. None of these rules compare passive control observations
        # with treated observations, which can share an experienced instant.
        physical_refs = set()
        comparator_refs = set()
        emitted_steps = set()
        observed_steps = set()
        for trial in intervention_rows:
            comparator_key = (trial.contingency_ref, trial.comparator_ref)
            emitted_key = (trial.contingency_ref, trial.emitted_step)
            observed_key = (trial.contingency_ref, trial.observed_step)
            if (
                trial.observation_ref in physical_refs
                or comparator_key in comparator_refs
                or emitted_key in emitted_steps
                or observed_key in observed_steps
            ):
                raise ValueError(
                    "causal snapshot reuses published intervention physical provenance"
                )
            physical_refs.add(trial.observation_ref)
            comparator_refs.add(comparator_key)
            emitted_steps.add(emitted_key)
            observed_steps.add(observed_key)
        # Snapshot provenance must be internally consistent: the immutable
        # witness of an actual closed water-source command may not be an
        # orphan or point to another observation's physical transition.
        hydration_rows = {
            row.identifier: row for row in (*obs.values(), *pending_obs)
        }
        for ref, (command_ref, transition_ref) in water_witnesses.items():
            observation = hydration_rows.get(ref)
            if (
                observation is None
                or observation.identifier != (
                    f"lived-hydration:{observation.episode_ref}:"
                    f"{transition_ref}"
                )
                or observation.observation_ref != transition_ref
                or observation.contingency_ref != "causal:hydration"
                or observation.predicate != "hydration_effect"
                or observation.subject_ref != "water"
                or observation.application_context != "water_source"
                or observation.observation_context != "water_source"
                or len(observation.controlled_variables) != 2
                or observation.controlled_variables[0] != (
                    "water_source", "present"
                )
                or observation.controlled_variables[1][0] != "site"
                or command_ref == transition_ref
            ):
                raise ValueError("hydration snapshot witness mismatches physical observation")
        pending_review = [
            decode_review(v) for v in state.get("pending_causal_reviews", [])
        ]
        published_review_refs = list(state.get("causal_reviews", []))
        all_review_refs = [
            *published_review_refs, *(row.identifier for row in pending_review)
        ]
        if len(all_review_refs) != len(set(all_review_refs)):
            raise ValueError("duplicate causal review identity in snapshot")
        credit_rows = [tuple(row) for row in state.get("causal_credits", [])]
        if len(credit_rows) != len(set(credit_rows)):
            raise ValueError("duplicate causal evidence credit in snapshot")
        # Phase-5 credits have no autonomous causal authority: they are an
        # index of already-published lived observations and interventions.
        # A snapshot with an omitted or invented credit could re-count an
        # episode or suppress later independent evidence after resumption.
        # Pending evidence is intentionally excluded until its publication.
        observation_credits = {
            (row.contingency_ref, row.observation_ref, "observation")
            for row in obs.values()
        }
        intervention_credits = {
            (row.contingency_ref, row.observation_ref, "intervention")
            for row in trials.values()
        }
        if (
            len(observation_credits) != len(obs)
            or len(intervention_credits) != len(trials)
            or set(credit_rows) != observation_credits | intervention_credits
        ):
            raise ValueError("causal snapshot credits mismatch published evidence")
        # Stage-9 snapshot provenance is a claim, never new evidence. Store
        # the *original* matched base-rate subset so subsequent physical
        # observations cannot retroactively invalidate a true earlier
        # correlation, and an edited status cannot promote itself on restore.
        correlation_witnesses = {}
        for raw in state.get("causal_correlation_witnesses", []):
            if (
                not isinstance(raw, (list, tuple)) or len(raw) != 3
                or not isinstance(raw[0], str) or not raw[0]
                or raw[0] in correlation_witnesses
            ):
                raise ValueError("invalid causal snapshot correlation witness identity")
            ref, treated_ids, control_ids = raw
            if (
                not isinstance(treated_ids, (list, tuple))
                or not isinstance(control_ids, (list, tuple))
                or not treated_ids or not control_ids
                or any(not isinstance(k, str) or not k for k in (*treated_ids, *control_ids))
                # These are validated nonempty string references. Equality
                # with sorted(set(refs)) is precisely strict lexical order;
                # check adjacent IDs instead of sorting and copying history.
                or any(
                    refs[i - 1] >= refs[i]
                    for refs in (treated_ids, control_ids)
                    for i in range(1, len(refs))
                )
            ):
                raise ValueError("invalid causal snapshot correlation witness samples")
            treated = [obs.get(k) for k in treated_ids]
            controls = [obs.get(k) for k in control_ids]
            # First reject absent, foreign or wrongly classified records,
            # before reading their context. No pending observation can satisfy
            # these lookups: obs contains published lived evidence only.
            if (
                any(x is None or x.contingency_ref != ref or not x.cause_present
                    for x in treated)
                or any(x is None or x.contingency_ref != ref or x.cause_present
                    for x in controls)
            ):
                raise ValueError("causal snapshot invalid controlled correlation witness")
            # Each restored observation has already passed decode_observation,
            # which canonicalizes the witnessed control pairs to tuples of
            # nonempty strings. Both old all(any(...)) directions hold iff the
            # complete sets of exact observable context/controls keys agree.
            # No unmatched treated OR control record may gain causal credit.
            treated_keys = {
                (x.observation_context, x.controlled_variables)
                for x in treated
            }
            control_keys = {
                (y.observation_context, y.controlled_variables)
                for y in controls
            }
            if treated_keys != control_keys:
                raise ValueError("causal snapshot invalid controlled correlation witness")
            treated_positive = sum(x.effect_present for x in treated)
            if (
                treated_positive < self.config.n1
                or (
                    treated_positive * len(controls)
                    <= sum(y.effect_present for y in controls) * len(treated)
                )
            ):
                raise ValueError("causal snapshot invalid controlled correlation witness")
            correlation_witnesses[ref] = (
                tuple(treated_ids), tuple(control_ids)
            )
        promoted_refs = {
            ref for ref, record in records.items()
            if record.causal_status != "aucun"
        }
        if set(correlation_witnesses) != promoted_refs:
            raise ValueError(
                "causal snapshot promoted status lacks historical correlation witness"
            )

        # A review ID alone is not an audited hypothesis. Persist its
        # alternatives and matched independent physical controls, and check
        # them against *published* observations, never a pending claim.
        review_proofs = [
            decode_review(row) for row in state.get("causal_review_proofs", [])
        ]
        if (
            len({p.identifier for p in review_proofs}) != len(review_proofs)
            or {p.identifier for p in review_proofs} != set(published_review_refs)
        ):
            raise ValueError("causal snapshot review proof ledger mismatch")
        reviewed_refs = set()
        for proof in review_proofs:
            record = records.get(proof.contingency_ref)
            if (
                record is None
                or record.causal_status not in {
                    "hypothese_causale", "testee_par_intervention", "etablie"
                }
            ):
                raise ValueError("causal snapshot review lacks published hypothesis")
            for a_ref, b_ref in proof.contrasting_pairs:
                a, b = obs.get(a_ref), obs.get(b_ref)
                if (
                    a is None or b is None
                    or a.contingency_ref != record.ref
                    or b.contingency_ref != record.ref
                    or not a.cause_present or b.cause_present
                    or a.controlled_variables != b.controlled_variables
                    or a.observation_context != b.observation_context
                    or a.observation_ref == b.observation_ref
                    or a.observed_step == b.observed_step
                ):
                    raise ValueError(
                        "causal snapshot review proof lacks independent matched controls"
                    )
            reviewed_refs.add(record.ref)
        hypothesis_refs = {
            ref for ref, record in records.items()
            if record.causal_status in {
                "hypothese_causale", "testee_par_intervention", "etablie"
            }
        }
        if reviewed_refs != hypothesis_refs:
            raise ValueError(
                "causal snapshot hypothesis lacks published matched review"
            )
        boundary_rows = list(state.get("causal_revision_boundaries", []))
        boundary_refs = [key for key, _step, _ref in boundary_rows]
        if len(boundary_refs) != len(set(boundary_refs)):
            raise ValueError("duplicate causal revision boundary in snapshot")
        boundary_index = {
            key: (step, ref) for key, step, ref in boundary_rows
        }
        # §13.2 / INV-33: an intervention with a physically observed missing
        # effect is the only source of a revision boundary. Check the most
        # recent *published* negative result for every contingency, using
        # the same stable ordering and tie rule as phase-5 publication.
        # Pending interventions have not yet established new boundaries.
        witnessed_boundaries = {}
        successful_by_contingency = {}
        # Restore checks every published intervention. Do not sort the full
        # history just to find the latest failed physical outcome. The old
        # stable chronological rule keeps the smallest identifier among
        # failures at the same last observed world-step.
        for trial in trials.values():
            if trial.observed_effect:
                if trial.attribution == "self_compatible":
                    successful_by_contingency.setdefault(
                        trial.contingency_ref, []
                    ).append(trial)
                continue
            prior = witnessed_boundaries.get(trial.contingency_ref)
            if (
                prior is None
                or trial.observed_step > prior[0]
                or (trial.observed_step == prior[0]
                    and trial.identifier < prior[1])
            ):
                witnessed_boundaries[trial.contingency_ref] = (
                    trial.observed_step, trial.identifier,
                )
        if boundary_index != witnessed_boundaries:
            raise ValueError(
                "causal snapshot revision boundary mismatches published counterexample"
            )

        self._causal_observations = obs
        self._causal_interventions = trials
        self._causal_reviews = set(published_review_refs)
        self._causal_correlation_witnesses = correlation_witnesses
        self._causal_review_proofs = {p.identifier: p for p in review_proofs}
        self._causal_credits = set(credit_rows)
        self._causal_revision_boundaries = boundary_index
        self._pending_causal_observations=pending_obs
        self._pending_causal_reviews=pending_review
        self._pending_causal_interventions=pending_trial
        agency_rows = [decode_agency_evidence(v) for v in state.get("agency_evidence", [])]
        pending_agency = [decode_agency_evidence(v) for v in state.get("pending_agency_evidence", [])]
        refs = [v.event_ref for v in (*agency_rows, *pending_agency)]
        if len(refs) != len(set(refs)):
            raise ValueError("duplicate agency comparison in causal snapshot")
        agency_ids = [v.identifier for v in (*agency_rows, *pending_agency)]
        if len(agency_ids) != len(set(agency_ids)):
            raise ValueError("duplicate agency evidence identity in snapshot")
        self._agency_evidence = {v.identifier: v for v in agency_rows}
        self._pending_agency_evidence = pending_agency
        # Every *published* causal intervention was admitted only after its
        # comparator was independently published. Restore must preserve that
        # join: losing or relabeling a comparison would otherwise let a
        # snapshot retain an unwitnessed n2 credit (DC-09, INV-33).
        # Pending interventions are intentionally not checked here: their
        # comparator may still be pending publication.
        for trial in trials.values():
            canonical = records.get(trial.contingency_ref)
            if canonical is None:
                raise ValueError(
                    "causal snapshot intervention lacks canonical contingency"
                )
            report = self._agency_evidence.get(trial.comparator_ref)
            if not self._published_comparison_supports(trial, report):
                raise ValueError(
                    "causal snapshot intervention lacks matching published agency comparison"
                )
            if (
                (canonical.predicate, canonical.subject_ref, "boire")
                in self.config.safe_test_actions
                and not self._verified_lived_drink_intervention(
                    trial, witnesses.get(trial.identifier), report,
                )
            ):
                raise ValueError(
                    "causal snapshot intervention lacks matching closed physical action"
                )
        # §13.2 / INV-25: a persisted status has epistemic consequences.
        # Restoring "tested" without any observed successful intervention,
        # or "established" without n2 independent post-refutation contexts,
        # would skip the real phase-5 progression and could suppress tests
        # or authorize established-only uses without earned causal evidence.
        for contingency in records.values():
            if contingency.causal_status not in {
                "testee_par_intervention", "etablie",
            }:
                continue
            # The temporary index was built from the entire independently
            # validated published trial ledger, never pending interventions.
            positive = successful_by_contingency.get(contingency.ref, ())
            if not positive:
                raise ValueError(
                    "causal snapshot tested status lacks lived intervention"
                )
            if contingency.causal_status == "etablie":
                last_failure_step = boundary_index.get(
                    contingency.ref, (-1, "")
                )[0]
                independent_contexts = {
                    row.context_signature for row in positive
                    if row.observed_step > last_failure_step
                }
                if len(independent_contexts) < self.config.n2:
                    raise ValueError(
                        "causal snapshot established status lacks independent post-revision contexts"
                    )
        witnesses = [
            decode_lived_numeric_outcome(raw)
            for raw in state.get("numeric_witnesses", ())
        ]
        if len({v.identifier for v in witnesses}) != len(witnesses):
            raise ValueError("duplicate lived numeric witnesses in causal snapshot")
        pending_witnesses = [
            decode_lived_numeric_outcome(raw)
            for raw in state.get("pending_numeric_witnesses", ())
        ]
        if len({
            w.identifier for w in (*witnesses, *pending_witnesses)
        }) != len(witnesses) + len(pending_witnesses):
            raise ValueError("duplicate numeric witness identity in snapshot")
        if len({
            w.transition_event_ref for w in (*witnesses, *pending_witnesses)
        }) != len(witnesses) + len(pending_witnesses):
            raise ValueError("same physical transition across published/pending witnesses")

        # Numeric correction witnesses cannot have autonomous snapshot
        # authority. They must remain joined to the exact food causal
        # observation that the live admission path created from the same
        # Memory-closed physical transition. This prevents restore from
        # manufacturing a correction witness that runtime cognition never
        # earned.
        published_numeric_sources = {
            row.identifier: row for row in obs.values()
        }
        pending_numeric_sources = {
            row.identifier: row for row in pending_obs
        }
        for witness, sources in (
            *((row, published_numeric_sources) for row in witnesses),
            *((row, pending_numeric_sources) for row in pending_witnesses),
        ):
            expected_ref = (
                f"causal-observation:{witness.episode_ref}:"
                f"{witness.transition_event_ref}"
            )
            observation = sources.get(expected_ref)
            if (
                observation is None
                or observation.contingency_ref != witness.contingency_ref
                or observation.predicate != "toxic_item"
                or observation.subject_ref != witness.command_target
                or observation.episode_ref != witness.episode_ref
                or observation.observation_ref != witness.transition_event_ref
                or observation.observed_step != witness.observed_t_monde
                or not observation.cause_present
                or not observation.effect_present
            ):
                raise ValueError(
                    "numeric snapshot witness lacks matching lived causal observation"
                )
        self._numeric_witnesses = {v.identifier: v for v in witnesses}
        self._pending_numeric_witnesses = pending_witnesses
        self._version = version


class CanonicalSafetyFacts:
    """Read-only Action Control adapter: innate policy plus canonical learned facts.

    Only global-context learnt prohibitions are exposed via the Stage-3
    context-free SafetyFactSource interface; context-specific applications
    require the later Stage-9 context-aware admissibility service.
    """

    def __init__(self, *, innate: StaticSafetyFacts, causal_model: CausalModel) -> None:
        self._innate = innate
        self._model = causal_model

    def item_status(self, *, resource_kind: str) -> str:
        status = self._innate.item_status(resource_kind=resource_kind)
        if status == "known_toxic":
            return status
        for fact in self._model.contingencies(
            context_signature="global", status="etabli_pour_securite"
        ):
            if fact.predicate == "toxic_item" and fact.subject_ref == resource_kind:
                return "known_toxic"
        return status

    def zone_status(self, *, x: int, y: int) -> str:
        status = self._innate.zone_status(x=x, y=y)
        if status == "known_lethal":
            return status
        subject = f"{x},{y}"
        for fact in self._model.contingencies(
            context_signature="global", status="etabli_pour_securite"
        ):
            if fact.predicate == "lethal_zone" and fact.subject_ref == subject:
                return "known_lethal"
        return status
