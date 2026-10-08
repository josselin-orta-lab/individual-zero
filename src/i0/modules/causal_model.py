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
from math import isfinite
from typing import Mapping, Sequence

from .action_control import StaticSafetyFacts
from .causal_lifecycle import (CausalObservation, CausalHypothesisReview, CausalIntervention, CausalInferenceChange, AgencyEvidence, agency_evidence_from_autobiography, decode_agency_evidence, decode_observation, decode_review, decode_intervention, serialize_value)


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
    observed_step: int | None = None
    integrity_observed: float | None = None

    def validate(self) -> None:
        if (self.t_monde < 1 or self.resource_kind not in ("berry_a", "berry_b")
            or not self.option_ref or not self.motive_ref
            or not isfinite(self.integrity_before)
            or not 0 <= self.integrity_before <= 100):
            raise ValueError("invalid motivated food exposure")
        if self.observed_step is None:
            if self.integrity_observed is not None:
                raise ValueError("unpaired observation")
        elif (self.observed_step != self.t_monde + 1
              or self.integrity_observed is None
              or not isfinite(self.integrity_observed)
              or not 0 <= self.integrity_observed <= 100):
            raise ValueError("a lived exposure needs next-step physical telemetry")


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
        self._credited_episodes: set[tuple[str, str]] = set()
        self._credited_observations: set[tuple[str, str]] = set()
        self._version = 0
        self._lived_food_exposures: dict[int, LivedFoodExposure] = {}
        self._causal_observations: dict[str, CausalObservation] = {}
        self._pending_causal_observations: list[CausalObservation] = []
        self._pending_causal_reviews: list[CausalHypothesisReview] = []
        self._pending_causal_interventions: list[CausalIntervention] = []
        self._causal_interventions: dict[str, CausalIntervention] = {}
        self._causal_reviews: set[str] = set()
        self._causal_credits: set[tuple[str, str, str]] = set()
        # Failure boundaries are causal state: stale successful trials must
        # not re-establish a refuted contingency without fresh contexts.
        self._causal_revision_boundaries: dict[str, tuple[int, str]] = {}
        self._agency_evidence: dict[str, AgencyEvidence] = {}
        self._pending_agency_evidence: list[AgencyEvidence] = []

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

    def record_applied_food_exposure(
        self, *, t_monde: int, resource_kind: str,
        option_ref: str, motive_ref: str, integrity_before: float,
    ) -> None:
        """Only already-executed, independently goal-motivated actions enter.

        No generated dangerous test option and no reward/bench/oracle inputs.
        These are pending action references, not promoted evidence.
        """
        item = LivedFoodExposure(
            t_monde=t_monde, resource_kind=resource_kind,
            option_ref=option_ref, motive_ref=motive_ref,
            integrity_before=integrity_before,
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
        if item is None or item.observed_step is not None:
            return
        updated = replace(
            item, observed_step=t_monde, integrity_observed=float(integrity),
        )
        updated.validate()
        self._lived_food_exposures[item.t_monde] = updated

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
        if not episode_ref:
            raise ValueError("missing Memory episode reference")
        events = {
            e["event_id"]: e for e in autobiographical_events
            if isinstance(e.get("event_id"), str)
            and e.get("kind") in {
                "command_experienced", "world_transition_experienced",
            }
        }
        commands: dict[int, Mapping[str, object]] = {}
        transitions: dict[int, Mapping[str, object]] = {}
        for event_ref in event_refs:
            event = events.get(event_ref)
            if event is None:
                continue
            t = event.get("t_monde")
            if not isinstance(t, int) or t < 1:
                continue
            if event["kind"] == "command_experienced":
                if t in commands:
                    # Conflicting exposures must never be manufactured as
                    # independent by duplicate projections.
                    commands.pop(t, None)
                    continue
                commands[t] = event
            elif event["kind"] == "world_transition_experienced":
                if t in transitions:
                    transitions.pop(t, None)
                    continue
                transitions[t] = event

        candidate: list[SafetyEvidence] = []
        causal_observations: list[CausalObservation] = []
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
            # The allowed autobiographical effects may reveal other physical
            # harm (creature/danger zone). When present, independent attribution
            # to food is impossible and the candidate is withheld.
            if any(
                isinstance(effects.get(key), (int, float))
                and effects[key] > 0
                for key in ("creature_damage", "danger_zone_damage")
            ):
                continue
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
            ))
            # Observation of exposure is not causal proof or an intervention.
            # Absence-of-exposure baselines require other *lived* comparable
            # episodes and are never generated from this successful meal.
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
            if item.identifier in self._seen_ids or any(
                old.identifier == item.identifier for old in self._pending
            ):
                raise ValueError("duplicate closed Memory safety evidence")
        for item in causal_observations:
            item.validate()
            if item.identifier in self._causal_observations or any(
                old.identifier == item.identifier
                for old in self._pending_causal_observations
            ):
                raise ValueError("duplicate closed Memory causal observation")
        for item in candidate:
            self.integrate(item)
        for item in causal_observations:
            self.integrate_causal_observation(item)
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
        admitted: list[AgencyEvidence] = []
        for event in autobiographical_events:
            if event.get("event_id") not in refs:
                continue
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

    def publish_causal_inference(self) -> tuple[CausalInferenceChange, ...]:
        """Publish independent §13.2 evidence atomically, with frozen input stages."""
        from collections import defaultdict
        original = dict(self._published)
        published = dict(original)
        observations = dict(self._causal_observations)
        interventions = dict(self._causal_interventions)
        reviews = set(self._causal_reviews)
        credits = set(self._causal_credits)
        revisions = dict(self._causal_revision_boundaries)
        changes: list[CausalInferenceChange] = []

        # Batch arrival never bypasses the prior published lifecycle level.
        for o in sorted(self._pending_causal_observations, key=lambda x: x.identifier):
            if o.predicate not in SAFETY_PREDICATES and o.predicate not in self.config.causal_predicates:
                raise ValueError("unregistered causal predicate")
            key = (o.contingency_ref, o.episode_ref, "observation")
            if key in credits or any(
                v.contingency_ref == o.contingency_ref
                and v.observation_ref == o.observation_ref
                for v in observations.values()
            ):
                continue
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
            published[o.contingency_ref] = old

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
            # Above-base-rate comparisons require matching observable context
            # and controlled variables. No mismatched context can create a rate.
            matched = [(x, y) for x in exposed for y in control
                       if x.observation_context == y.observation_context
                       and x.controlled_variables == y.controlled_variables]
            if not matched:
                continue
            # P-35 n1 counts observed cause+effect co-occurrences,
            # not merely cause-present episodes without the effect.
            confirmed = {
                x.identifier for x, _ in matched if x.effect_present
            }
            if len(confirmed) < self.config.n1:
                continue
            e = {x.identifier: x for x, _ in matched}
            b = {y.identifier: y for _, y in matched}
            if sum(x.effect_present for x in e.values()) * len(b) <= (
                sum(y.effect_present for y in b.values()) * len(e)
            ):
                continue
            new = replace(current, causal_status="correlation_observee", version=current.version + 1)
            published[ref] = new
            changes.append(CausalInferenceChange(ref, current.causal_status, new.causal_status, new.version, sorted(e)[-1], "controlled_base_rate"))

        for review in sorted(self._pending_causal_reviews, key=lambda x: x.identifier):
            old = original.get(review.contingency_ref)
            if old is None or old.causal_status != "correlation_observee":
                raise ValueError("review requires previously published correlation")
            for a_ref, b_ref in review.contrasting_pairs:
                a, b = observations.get(a_ref), observations.get(b_ref)
                if (a is None or b is None or a.contingency_ref != old.ref
                    or b.contingency_ref != old.ref or not a.cause_present
                    or b.cause_present or a.controlled_variables != b.controlled_variables
                    or a.observation_context != b.observation_context
                    or a.episode_ref == b.episode_ref):
                    raise ValueError("review lacks independent matched controls")
            reviews.add(review.identifier)
            current = published[old.ref]
            new = replace(current, causal_status="hypothese_causale", version=current.version + 1)
            published[old.ref] = new
            changes.append(CausalInferenceChange(old.ref, current.causal_status, new.causal_status, new.version, review.identifier, "matched_alternatives"))

        for trial in sorted(self._pending_causal_interventions, key=lambda x: (x.observed_step, x.identifier)):
            old = original.get(trial.contingency_ref)
            if old is None or old.causal_status not in {
                "hypothese_causale", "testee_par_intervention", "etablie"
            }:
                raise ValueError("intervention needs previously published hypothesis")
            key = (trial.contingency_ref, trial.episode_ref, "intervention")
            if key in credits or any(v.observation_ref == trial.observation_ref for v in interventions.values()):
                continue
            credits.add(key)
            interventions[trial.identifier] = trial
            current = published[old.ref]
            if not trial.observed_effect and old.causal_status == "etablie":
                revisions[old.ref] = (trial.observed_step, trial.identifier)
                next_status = "hypothese_causale"
            else:
                boundary = revisions.get(old.ref, (-1, ""))[0]
                contexts = {
                    x.context_signature for x in interventions.values()
                    if x.contingency_ref == old.ref and x.observed_effect
                    and x.attribution == "self_compatible" and x.observed_step > boundary
                }
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

        # Comparator descriptions do not influence causal or safety statuses.
        # Publish them only after all staged inference validations succeed.
        agency = dict(self._agency_evidence)
        for report in sorted(
            self._pending_agency_evidence,
            key=lambda value: (value.observed_t_monde, value.event_ref),
        ):
            if report.event_ref in {v.event_ref for v in agency.values()}:
                raise ValueError("duplicate published physical agency observation")
            agency[report.identifier] = report
        self._published = published
        self._agency_evidence = agency
        self._causal_observations = observations
        self._causal_interventions = interventions
        self._causal_reviews = reviews
        self._causal_credits = credits
        self._causal_revision_boundaries = revisions
        self._pending_causal_observations.clear()
        self._pending_causal_reviews.clear()
        self._pending_causal_interventions.clear()
        self._pending_agency_evidence.clear()
        self._version += 1
        return tuple(changes)

    def integrate(self, evidence: SafetyEvidence) -> None:
        evidence.validate()  # INV-03/27: reject before any causal write.
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
        self._pending.clear()
        self._version += 1
        return tuple(changes)

    def export_causal_state(self) -> object:
        return {
            "config_version": self.config.version,
            "version": self._version,
            "published": [
                {name: getattr(c, name) for name in c.__dataclass_fields__}
                for _, c in sorted(self._published.items())
            ],
            "pending": [
                {name: getattr(e, name) for name in e.__dataclass_fields__}
                for e in self._pending
            ],
            "seen": sorted(self._seen_ids),
            "episodes": [list(x) for x in sorted(self._credited_episodes)],
            "observations": [list(x) for x in sorted(self._credited_observations)],
            "causal_observations": [serialize_value(x) for _,x in sorted(self._causal_observations.items())],
            "causal_interventions": [serialize_value(x) for _,x in sorted(self._causal_interventions.items())],
            "causal_reviews": sorted(self._causal_reviews),
            "causal_credits": [list(x) for x in sorted(self._causal_credits)],
            "agency_evidence": [serialize_value(v) for _, v in sorted(self._agency_evidence.items())],
            "pending_agency_evidence": [serialize_value(v) for v in self._pending_agency_evidence],
            "causal_revision_boundaries": [
                [key, step, ref] for key, (step, ref) in sorted(self._causal_revision_boundaries.items())
            ],
            "pending_causal_observations": [serialize_value(x) for x in self._pending_causal_observations],
            "pending_causal_reviews": [serialize_value(x) for x in self._pending_causal_reviews],
            "pending_causal_interventions": [serialize_value(x) for x in self._pending_causal_interventions],
            "lived_food_exposures": [
                {name: getattr(v, name) for name in v.__dataclass_fields__}
                for _, v in sorted(self._lived_food_exposures.items())
            ],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping) or state.get("config_version") != self.config.version:
            raise ValueError("causal model snapshot config mismatch")
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
        episodes = {tuple(x) for x in state["episodes"]}
        observations = {tuple(x) for x in state["observations"]}
        if any(len(key) != 2 for key in episodes | observations):
            raise ValueError("invalid causal evidence credit key")
        version = state["version"]
        if not isinstance(version, int) or version < 0:
            raise ValueError("invalid causal model version")
        self._published = records
        self._pending = pending
        self._credited_episodes = episodes
        self._credited_observations = observations
        self._seen_ids = set(state["seen"])
        exposure_rows = state.get("lived_food_exposures", [])
        exposures = {}
        for raw in exposure_rows:
            exposure = LivedFoodExposure(**raw)
            exposure.validate()
            if exposure.t_monde in exposures:
                raise ValueError("duplicate pending lived exposure")
            exposures[exposure.t_monde] = exposure
        self._lived_food_exposures = exposures
        obs={x.identifier:x for x in (decode_observation(v) for v in state.get("causal_observations",[]))}
        trials={x.identifier:x for x in (decode_intervention(v) for v in state.get("causal_interventions",[]))}
        pending_obs=[decode_observation(v) for v in state.get("pending_causal_observations",[])]
        pending_review=[decode_review(v) for v in state.get("pending_causal_reviews",[])]
        pending_trial=[decode_intervention(v) for v in state.get("pending_causal_interventions",[])]
        self._causal_observations=obs
        self._causal_interventions=trials
        self._causal_reviews=set(state.get("causal_reviews",[]))
        self._causal_credits={tuple(v) for v in state.get("causal_credits",[])}
        self._causal_revision_boundaries={
            key:(step,ref) for key,step,ref in state.get("causal_revision_boundaries",[])
        }
        self._pending_causal_observations=pending_obs
        self._pending_causal_reviews=pending_review
        self._pending_causal_interventions=pending_trial
        agency_rows = [decode_agency_evidence(v) for v in state.get("agency_evidence", [])]
        pending_agency = [decode_agency_evidence(v) for v in state.get("pending_agency_evidence", [])]
        refs = [v.event_ref for v in (*agency_rows, *pending_agency)]
        if len(refs) != len(set(refs)):
            raise ValueError("duplicate agency comparison in causal snapshot")
        self._agency_evidence = {v.identifier: v for v in agency_rows}
        self._pending_agency_evidence = pending_agency
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
