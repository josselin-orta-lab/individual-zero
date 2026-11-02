"""Pure I2 endogenous body-needs readout with immutable birth temperament.

No imports from I1. This is a first-person, current-body assessment for
future integration into the existing I2 SQLite owner; no motor or UC authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from i2.modules.native_body_contract import Body, CHANNELS
from i2.modules.native_birth_temperament import BirthTemperament

SETPOINTS = {"energy": 80.0, "food": 70.0, "water": 70.0, "integrity": 100.0}
WEIGHTS = {"energy": 1.0, "food": 1.0, "water": 1.0, "integrity": 1.0}
VERSION = "i2-native-current-body-needs-v1"


@dataclass(frozen=True, slots=True)
class NeedAssessment:
    version: str
    deficits: dict[str, float]
    pressures: dict[str, float]
    leading_need: str | None
    immediate_danger: tuple[str, ...]
    motor_authority: str = "NONE"


def assess_needs(body: Body, temperament: BirthTemperament,
                 *, setpoints: dict[str, float] | None = None) -> NeedAssessment:
    """Only current body and immutable innate threat sensitivity affect urgency.

    Does not read food effects, future outcomes, hidden world or experiences.
    Learned preferences remain independently owned by cognition.
    """
    if type(body) is not Body or type(temperament) is not BirthTemperament:
        raise ValueError("native I2 body and birth temperament required")
    goals = dict(SETPOINTS if setpoints is None else setpoints)
    if (set(goals) != set(CHANNELS)
            or any(type(v) not in (float, int) or not isfinite(v)
                   or not 0 < v <= 100 for v in goals.values())):
        raise ValueError("four finite positive body setpoints required")
    deficits = {name: max(0.0, min(1.0,
                    (goals[name] - getattr(body, name)) / goals[name]))
                for name in CHANNELS}
    # Threat sensitivity modulates protective attention, not body physics.
    threat_gain = 1.0 + 0.5 * temperament.threat_sensitivity
    weight = dict(WEIGHTS)
    weight["integrity"] *= threat_gain
    pressures = {name: min(1.0, deficits[name] * weight[name])
                 for name in CHANNELS}
    priority = max(CHANNELS, key=lambda name: pressures[name])
    leading = priority if pressures[priority] > 0 else None
    danger = tuple(name for name in ("food", "water", "integrity")
                   if getattr(body, name) <= 10.0)
    return NeedAssessment(
        VERSION, deficits, pressures, leading, danger)
