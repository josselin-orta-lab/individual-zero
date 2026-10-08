"""Stage-9 normative causal-evidence contracts (§13.1-13.3, P-35, INV-25).

Observational association is NOT an intervention. Each record carries
independent, accessible provenance; no oracle/bench label is admissible.
The canonical Causal Model, never this value-object module, owns all state.

This first causal-cycle protocol accepts independently sourced, typed evidence;
the automatic Memory/Agency -> intervention producer and Simulator consumer
remain separate, explicitly unfinished Stage-9 integration work.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


def _nonblank(value: str) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _controls_valid(controls: tuple[tuple[str, str], ...]) -> bool:
    keys: list[str] = []
    for pair in controls:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            return False
        key, value = pair
        if not _nonblank(key) or not _nonblank(value):
            return False
        keys.append(key)
    return len(keys) == len(set(keys))


@dataclass(frozen=True, slots=True)
class CausalObservation:
    identifier: str
    contingency_ref: str
    predicate: str
    subject_ref: str
    application_context: str
    observation_context: str
    episode_ref: str
    observation_ref: str
    observed_step: int
    cause_present: bool
    effect_present: bool
    controlled_variables: tuple[tuple[str, str], ...]
    source: str = "monde"
    independent_episode: bool = True
    oracle_derived: bool = False
    rollback_cancelled: bool = False
    counterfactual: bool = False

    def validate(self) -> None:
        if not all(_nonblank(s) for s in (
            self.identifier, self.contingency_ref, self.predicate,
            self.subject_ref, self.application_context, self.observation_context,
            self.episode_ref, self.observation_ref,
        )):
            raise ValueError("causal observation requires stable provenance")
        if (
            type(self.observed_step) is not int or self.observed_step < 1
            or type(self.cause_present) is not bool
            or type(self.effect_present) is not bool
            or not _controls_valid(self.controlled_variables)
        ):
            raise ValueError("invalid observational variables or world time")
        if (self.source != "monde" or not self.independent_episode
            or self.oracle_derived or self.rollback_cancelled
            or self.counterfactual):
            raise ValueError("causal observation is not independent lived evidence")


@dataclass(frozen=True, slots=True)
class CausalHypothesisReview:
    identifier: str
    contingency_ref: str
    alternatives: tuple[str, ...]
    # (cause-present observation ref, cause-absent observation ref)
    contrasting_pairs: tuple[tuple[str, str], ...]

    def validate(self) -> None:
        if not _nonblank(self.identifier) or not _nonblank(self.contingency_ref):
            raise ValueError("hypothesis review requires identity")
        if (
            not self.alternatives or not self.contrasting_pairs
            or not all(_nonblank(s) for s in self.alternatives)
            or len(self.alternatives) != len(set(self.alternatives))
        ):
            raise ValueError("alternatives and matched controls must be explicit")
        for pair in self.contrasting_pairs:
            if len(pair) != 2 or not all(_nonblank(s) for s in pair):
                raise ValueError("invalid contrasting observation references")


@dataclass(frozen=True, slots=True)
class CausalIntervention:
    identifier: str
    contingency_ref: str
    episode_ref: str
    observation_ref: str
    command_ref: str
    comparator_ref: str
    context_signature: str
    emitted_step: int
    observed_step: int
    observed_effect: bool
    comparator_status: str
    attribution: str
    # Explicit values accessible in the intervention context: no verdict flags.
    controlled_variables: tuple[tuple[str, str], ...]
    action_applied: bool
    source: str = "monde"
    oracle_derived: bool = False
    rollback_cancelled: bool = False
    counterfactual: bool = False

    def validate(self) -> None:
        if not all(_nonblank(s) for s in (
            self.identifier, self.contingency_ref, self.episode_ref,
            self.observation_ref, self.command_ref, self.comparator_ref,
            self.context_signature,
        )):
            raise ValueError("intervention lacks physically grounded references")
        if (
            type(self.emitted_step) is not int or type(self.observed_step) is not int
            or self.emitted_step < 1
            or self.observed_step <= self.emitted_step
            or type(self.observed_effect) is not bool
            or not _controls_valid(self.controlled_variables)
        ):
            raise ValueError("invalid intervention time or contextual controls")
        if self.comparator_status not in {"conforming", "nonconforming"}:
            raise ValueError("unverifiable effects cannot be causal interventions")
        if self.attribution not in {"self_compatible", "uncertain"}:
            raise ValueError("external-world explanation is not evidence of intervention")
        if (
            not self.action_applied or self.source != "monde"
            or self.oracle_derived or self.rollback_cancelled
            or self.counterfactual
        ):
            raise ValueError("only nonlethal, applied, lived interventions count")
        if self.observed_effect and (
            self.comparator_status != "conforming"
            or self.attribution != "self_compatible"
        ):
            raise ValueError("successful intervention needs compatible observed effect")
        if not self.observed_effect and self.comparator_status != "nonconforming":
            raise ValueError("absent intervention effect must be observed nonconforming")


@dataclass(frozen=True, slots=True)
class AgencyEvidence:
    """DC-09-backed Action Control comparator observation, not causal proof.

    This record is descriptive only. It does not count as an intervention,
    create a hypothesis, establish a contingency, or authorize a veto.
    Effects retain the P-47 comparator version and observed numerical values.
    """
    identifier: str
    episode_ref: str
    event_ref: str
    option_ref: str
    sent_t_monde: int
    observed_t_monde: int
    status: str
    attribution: str
    # (variable, status, predicted, observed, tolerance, p47_version)
    effects: tuple[tuple[str | None, str, float | None, float | None, float | None, str], ...]
    source: str = "agency_comparator"

    def validate(self) -> None:
        from math import isfinite

        if not all(_nonblank(v) for v in (
            self.identifier, self.episode_ref, self.event_ref, self.option_ref,
        )):
            raise ValueError("agency comparison requires an autobiographical source")
        if (
            self.source != "agency_comparator"
            or type(self.sent_t_monde) is not int or self.sent_t_monde < 0
            or type(self.observed_t_monde) is not int
            or self.observed_t_monde <= self.sent_t_monde
            or self.status not in {"conforming", "nonconforming", "indeterminable"}
            or self.attribution not in {"self_compatible", "world_justified", "uncertain"}
            or not self.effects
        ):
            raise ValueError("invalid lived agency comparison")
        statuses = []
        for effect in self.effects:
            if not isinstance(effect, (tuple, list)) or len(effect) != 6:
                raise ValueError("invalid P-47 observed effect")
            variable, status, predicted, observed, tolerance, version = effect
            if status not in {
                "conforming", "nonconforming", "indeterminable", "expected_effect_missing",
            } or not _nonblank(version):
                raise ValueError("unknown comparator outcome or P-47 version")
            if variable is not None and not _nonblank(variable):
                raise ValueError("invalid observed effect variable")
            if status in {"conforming", "nonconforming"} and variable is None:
                raise ValueError("comparison result must identify its variable")
            for value in (predicted, observed, tolerance):
                if value is not None and (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(value)
                ):
                    raise ValueError("nonfinite comparator measurement")
            if tolerance is not None and tolerance < 0:
                raise ValueError("negative P-47 tolerance")
            if status in {"conforming", "nonconforming"} and (
                predicted is None or observed is None or tolerance is None
            ):
                raise ValueError("comparator evidence requires observed physical value")
            statuses.append(status)
        if self.status == "conforming" and any(v != "conforming" for v in statuses):
            raise ValueError("conforming comparison has nonconforming effects")
        if self.status == "nonconforming" and "nonconforming" not in statuses:
            raise ValueError("nonconforming comparison lacks a mismatched effect")
        if self.status == "indeterminable" and all(v == "conforming" for v in statuses):
            raise ValueError("indeterminate comparison cannot have all effects confirmed")


def agency_evidence_from_autobiography(
    *, episode_ref: str, event: Mapping[str, object],
) -> AgencyEvidence | None:
    """Only a DC-09 projected, versioned P-47 comparison is admissible.

    The caller supplies one event from an actually closed Memory episode. A
    missing option (e.g., a reflex) has no plan intervention attribution.
    Old Stage-3-8 comparator projections are not silently reinterpreted.
    """
    if event.get("kind") != "agency_comparison":
        return None
    data = event.get("data")
    if not isinstance(data, Mapping) or not isinstance(data.get("option_ref"), str):
        return None
    effects_raw = data.get("effects")
    if not isinstance(effects_raw, (tuple, list)) or not effects_raw:
        return None
    effects = []
    for item in effects_raw:
        if not isinstance(item, Mapping):
            raise ValueError("invalid autobiographical comparator effect")
        version = item.get("comparator_version")
        if not _nonblank(version):
            # Never forge P-47 provenance for an unversioned older comparator.
            return None
        effects.append((
            item.get("variable"),
            item.get("status"),
            item.get("predicted"),
            item.get("observed"),
            item.get("precision"),
            version,
        ))
    event_ref = event.get("event_id")
    if not isinstance(event_ref, str):
        raise ValueError("missing DC-09 event identity")
    report = AgencyEvidence(
        identifier=f"agency-evidence:{episode_ref}:{event_ref}",
        episode_ref=episode_ref,
        event_ref=event_ref,
        option_ref=data["option_ref"],
        sent_t_monde=data.get("sent_t_monde"),
        observed_t_monde=data.get("observed_t_monde"),
        status=data.get("status"),
        attribution=data.get("attribution"),
        effects=tuple(effects),
    )
    report.validate()
    return report


def decode_agency_evidence(raw: Mapping[str, object]) -> AgencyEvidence:
    data = dict(raw)
    data["effects"] = tuple(tuple(effect) for effect in data["effects"])
    report = AgencyEvidence(**data)
    report.validate()
    return report


@dataclass(frozen=True, slots=True)
class CausalInferenceChange:
    contingency_ref: str
    before: str
    after: str
    version: int
    evidence_ref: str
    protocol: str


def decode_observation(value: Mapping[str, object]) -> CausalObservation:
    data = dict(value)
    data["controlled_variables"] = tuple(tuple(pair) for pair in data["controlled_variables"])
    event = CausalObservation(**data)
    event.validate()
    return event


def decode_review(value: Mapping[str, object]) -> CausalHypothesisReview:
    data = dict(value)
    data["alternatives"] = tuple(data["alternatives"])
    data["contrasting_pairs"] = tuple(tuple(pair) for pair in data["contrasting_pairs"])
    review = CausalHypothesisReview(**data)
    review.validate()
    return review


def decode_intervention(value: Mapping[str, object]) -> CausalIntervention:
    data = dict(value)
    data["controlled_variables"] = tuple(tuple(pair) for pair in data["controlled_variables"])
    trial = CausalIntervention(**data)
    trial.validate()
    return trial


def serialize_value(value: object) -> dict[str, object]:
    return {name: getattr(value, name) for name in value.__dataclass_fields__}
