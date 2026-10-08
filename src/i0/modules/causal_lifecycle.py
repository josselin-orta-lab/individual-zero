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
