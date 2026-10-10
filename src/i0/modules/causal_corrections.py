"""Read-only Stage-9 personal numerical correction layer (§12.3, INV-25).

Corrections belong to the single canonical Causal Model object. The frozen
Equipment is not modified. This first deliberately narrow implementation
supports direct post-command *body* values in the global application context,
and no categorical/probabilistic inference. Never guess absent corrections.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Protocol, Sequence

from i0.equipment import EquipmentPrediction, PredictedEffect, SimulationState
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex

BODY_VARIABLES = frozenset({"energy", "food", "water", "integrity"})


@dataclass(frozen=True, slots=True)
class NumericPredictionCorrection:
    contingency_ref: str
    intervention_ref: str
    agency_evidence_ref: str
    command_primitive: str
    command_target: str | None
    variable: str
    observed_after: float
    application_context: str = "global"
    # Real-source rules are exact-context observations, not universally valid
    # absolute body assignments. None retains the older isolated test contract.
    observed_before_body: tuple[tuple[str, float], ...] | None = None
    observed_before_position: tuple[int, int] | None = None
    observed_before_state_digest: str | None = None

    def validate(self) -> None:
        if not all((
            self.contingency_ref, self.intervention_ref,
            self.agency_evidence_ref, self.command_primitive,
        )):
            raise ValueError("correction requires anchored causal provenance")
        if self.variable not in BODY_VARIABLES:
            raise ValueError("Stage-9 numeric layer only supports physical body effects")
        if self.application_context != "global":
            raise ValueError("context-specific corrections require an explicit matcher")
        if self.command_target is not None and (
            not isinstance(self.command_target, str) or not self.command_target
        ):
            raise ValueError("invalid optional command target")
        if (
            isinstance(self.observed_after, bool)
            or not isinstance(self.observed_after, (int, float))
            or not isfinite(self.observed_after)
            or not 0 <= self.observed_after <= 100
        ):
            raise ValueError("correction must contain bounded observed body telemetry")
        if self.observed_before_body is not None:
            before = dict(self.observed_before_body)
            if set(before) != BODY_VARIABLES or len(self.observed_before_body) != 4:
                raise ValueError("physical correction requires exact body context")
            if any(
                isinstance(v, bool) or not isinstance(v, (int, float))
                or not isfinite(v) or not 0 <= v <= 100
                for v in before.values()
            ):
                raise ValueError("invalid observed pre-action body context")
            if (self.observed_before_position is None
                or len(self.observed_before_position) != 2
                or any(type(v) is not int for v in self.observed_before_position)):
                raise ValueError("physical correction requires exact observed position")
        elif self.observed_before_position is not None:
            raise ValueError("position without physical body context")
        if self.observed_before_state_digest is not None and (
            self.observed_before_body is None
            or len(self.observed_before_state_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.observed_before_state_digest)
        ):
            raise ValueError("invalid full accessible pre-action state digest")


@dataclass(frozen=True, slots=True)
class LivedNumericOutcome:
    """DC-09 witnessed physical outcome, not yet an authorized correction.

    Command+transition are from the same closed Memory episode. The pre-action
    context is captured by Perception at a successfully dispatched command,
    and the next Perception capture must corroborate the transition's value.
    Agency and intervention evidence are linked later by immutable references.
    """
    identifier: str
    contingency_ref: str
    episode_ref: str
    command_event_ref: str
    transition_event_ref: str
    option_ref: str
    sent_t_monde: int
    observed_t_monde: int
    command_primitive: str
    command_target: str
    variable: str
    observed_before_body: tuple[tuple[str, float], ...]
    observed_before_position: tuple[int, int]
    observed_before_state_digest: str
    observed_after: float

    def validate(self) -> None:
        if not all(isinstance(v, str) and v for v in (
            self.identifier, self.contingency_ref, self.episode_ref,
            self.command_event_ref, self.transition_event_ref, self.option_ref,
            self.command_primitive, self.command_target,
        )):
            raise ValueError("physical outcome lacks closed autobiographical provenance")
        if (type(self.sent_t_monde) is not int
            or type(self.observed_t_monde) is not int
            or self.sent_t_monde < 1
            or self.observed_t_monde != self.sent_t_monde + 1):
            raise ValueError("physical outcome is not a next-step lived observation")
        if self.variable != "integrity" or self.command_primitive != "manger":
            raise ValueError("Stage-9 lived numeric bridge supports food integrity only")
        if self.contingency_ref != f"toxic:{self.command_target}":
            raise ValueError("numeric witness does not match canonical food identity")
        correction = NumericPredictionCorrection(
            contingency_ref=self.contingency_ref,
            intervention_ref=self.command_event_ref,
            agency_evidence_ref=self.transition_event_ref,
            command_primitive=self.command_primitive,
            command_target=self.command_target,
            variable=self.variable,
            observed_after=self.observed_after,
            observed_before_body=self.observed_before_body,
            observed_before_position=self.observed_before_position,
            observed_before_state_digest=self.observed_before_state_digest,
        )
        correction.validate()
        before = dict(self.observed_before_body)
        if not self.observed_after < before["integrity"]:
            raise ValueError("toxicity witness requires an actual integrity loss")


def decode_lived_numeric_outcome(data: dict[str, object]) -> LivedNumericOutcome:
    raw = dict(data)
    raw["observed_before_body"] = tuple(
        tuple(v) for v in raw["observed_before_body"]
    )
    raw["observed_before_position"] = tuple(raw["observed_before_position"])
    result = LivedNumericOutcome(**raw)
    result.validate()
    return result


class EstablishedCorrectionSource(Protocol):
    def established_prediction_corrections(self) -> tuple[NumericPredictionCorrection, ...]:
        ...


class CausalCorrectionConflict(LookupError):
    """Equal-specificity established rules disagree; prediction unavailable."""


def correct_equipment_prediction(
    *,
    source: EstablishedCorrectionSource,
    command: PrimitiveCommand,
    state: SimulationState,
    prediction: EquipmentPrediction,
) -> tuple[EquipmentPrediction, tuple[str, ...]]:
    """Apply at most one established correction to each concerned component.

    The only supported application context is explicitly `global`.
    Constraints on command target, observed body/position and full accessible
    state determine specificity. A rule can override another only when it is
    at least as constrained on every dimension and stricter on one. Conflicting
    applicable rules with incomparable constraints remain unavailable.
    """
    active = []
    for c in source.established_prediction_corrections():
        c.validate()
        if c.command_primitive != command.primitive:
            continue
        if c.command_target is not None and (
            command.parameters.get("target") != c.command_target
        ):
            continue
        if c.observed_before_body is not None and (
            (state.x, state.y) != c.observed_before_position
            or any(
                float(state.body[name]) != float(value)
                for name, value in c.observed_before_body
            )
        ):
            continue
        if c.observed_before_state_digest is not None and (
            sha256_hex(canonical_causal_bytes(state.as_dict()))
            != c.observed_before_state_digest
        ):
            continue
        active.append(c)

    def constraints(correction: NumericPredictionCorrection) -> tuple[int, int, int]:
        # A full-state digest is stricter than body/position matching, which
        # in turn is stricter than having no measured pre-action context.
        # A command target is an independent constraint, not a substitute
        # for a physical state condition.
        return (
            int(correction.command_target is not None),
            int(correction.observed_before_body is not None),
            int(correction.observed_before_state_digest is not None),
        )

    def dominates(left: NumericPredictionCorrection,
                  right: NumericPredictionCorrection) -> bool:
        a, b = constraints(left), constraints(right)
        return all(x >= y for x, y in zip(a, b)) and a != b

    replacements: dict[str, NumericPredictionCorrection] = {}
    for variable in sorted({c.variable for c in active}):
        options = [c for c in active if c.variable == variable]
        # Reject incomparable *conflicting* rules. Selecting a targeted rule
        # over an exact-context untargeted rule by arbitrary priority would
        # invent evidence that neither is universally more specific.
        maximal = [
            c for c in options
            if not any(dominates(other, c) for other in options)
        ]
        values = {float(c.observed_after) for c in maximal}
        if len(values) != 1:
            raise CausalCorrectionConflict(
                f"unresolved established correction conflict for {variable}"
            )
        replacements[variable] = min(
            maximal,
            key=lambda c: (
                c.contingency_ref, c.intervention_ref, c.agency_evidence_ref,
            ),
        )
    if not replacements:
        return prediction, ()

    body = dict(prediction.next_state.body)
    for name, correction in replacements.items():
        body[name] = float(correction.observed_after)
    new_state = replace(prediction.next_state, body=body)
    new_state.validate()

    effect_by_name = {e.variable: e for e in prediction.effects}
    for name, correction in replacements.items():
        previous = effect_by_name.get(name)
        effect_by_name[name] = PredictedEffect(
            variable=name,
            before=(
                state.body[name] if previous is None else previous.before
            ),
            after=correction.observed_after,
            # Do not invent calibrated certainty when a numeric correction is
            # applied; preserve the frozen Equipment's confidence.
            confidence=(
                prediction.confidence if previous is None else previous.confidence
            ),
        )
    new_prediction = replace(
        prediction,
        next_state=new_state,
        effects=tuple(effect_by_name[name] for name in sorted(effect_by_name)),
    )
    new_prediction.validate()
    return new_prediction, tuple(sorted({
        c.contingency_ref for c in replacements.values()
    }))
