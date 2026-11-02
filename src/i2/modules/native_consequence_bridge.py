"""I2-only, pure physical consequence and endogenous need transition boundary.

This is a value object bridge for integration in the existing SQLite owner,
not a second WorldBody, life journal, independent witness or motor executor.
No I1 runtime imports or experimenter-issued autonomous choices.
"""
from __future__ import annotations
from dataclasses import dataclass

from i2.modules.native_body_contract import Body, PhysicalOutcome, transition
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_physiological_needs import NeedAssessment, assess_needs


@dataclass(frozen=True, slots=True)
class NativeConsequence:
    """One already admitted and actually applied physical action's consequence."""
    action: str
    before: Body
    after: Body
    needs_before: NeedAssessment
    needs_after: NeedAssessment
    terminal: bool
    lethal_reasons: tuple[str, ...]
    # This value object never authorizes a motor act or writes a journal.
    motor_authority: str = "NONE"
    m11_authenticated: bool = False


def admitted_consequence(*, before: Body, temperament: BirthTemperament,
                         action: str, admitted: bool,
                         applied: bool, berry_food_gain: float = 0.0,
                         berry_integrity_delta: float = 0.0,
                         drink_water_gain: float = 0.0) -> NativeConsequence:
    """Evaluate only an admitted, actually applied action and its observed effect.

    A caller MUST validate admission, bodily state, world resources, and
    actual hidden physical effect within its own transaction. Denying an
    unadmitted event prevents this bridge being treated as an actuator.
    """
    if type(admitted) is not bool or type(applied) is not bool:
        raise ValueError("exact admission and effect flags required")
    if not admitted or not applied:
        raise ValueError("cannot publish unadmitted or unexecuted consequence")
    if type(before) is not Body or type(temperament) is not BirthTemperament:
        raise ValueError("exact native physical body and temperament required")
    if before.food <= 0 or before.water <= 0 or before.integrity <= 0:
        raise ValueError("terminal input body cannot act")
    outcome: PhysicalOutcome = transition(
        before, action, berry_food_gain=berry_food_gain,
        berry_integrity_delta=berry_integrity_delta,
        drink_water_gain=drink_water_gain,
    )
    return NativeConsequence(
        action, before, outcome.body,
        assess_needs(before, temperament),
        assess_needs(outcome.body, temperament),
        outcome.terminal, outcome.reasons,
    )
