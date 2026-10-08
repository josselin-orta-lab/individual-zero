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

    The only supported context is explicitly `global`. Exact command-target
    matches outrank primitive-wide rules. At equal specificity, inconsistent
    observed values yield explicit uncertainty, never an arbitrary winner.
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
        active.append(c)

    replacements: dict[str, NumericPredictionCorrection] = {}
    for variable in sorted({c.variable for c in active}):
        options = [c for c in active if c.variable == variable]
        specificity = max(int(c.command_target is not None) for c in options)
        best = sorted(
            (c for c in options if int(c.command_target is not None) == specificity),
            key=lambda c: (c.contingency_ref, c.intervention_ref),
        )
        values = {float(c.observed_after) for c in best}
        if len(values) != 1:
            raise CausalCorrectionConflict(
                f"unresolved established correction conflict for {variable}"
            )
        replacements[variable] = best[0]
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
