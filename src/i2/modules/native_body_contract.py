"""I2-owned physical body contract for future common-world parity experiments.

Pure physics only: this is not an alternate WorldBody owner, actuator or
living runtime. Action effects and terminal checks must later be atomically
integrated into the sole I2 SQLite owner; no I1 code or life state is imported.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

CHANNELS = ("energy", "food", "water", "integrity")
COSTS = {
    "se_deplacer": 2.0, "collecter": 1.0, "manger": 0.5,
    "boire": 0.5, "poser_une_pierre": 1.5,
    "fabriquer_outil": 1.5, "dormir": 0.25, "attendre": 0.35,
}
PHYSICS_VERSION = "i2-independent-i1-natural-v4-physical-reference-v1"


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


@dataclass(frozen=True, slots=True)
class Body:
    energy: float
    food: float
    water: float
    integrity: float

    def __post_init__(self) -> None:
        if any(not isfinite(value) or not 0 <= value <= 100
               for value in (self.energy, self.food, self.water, self.integrity)):
            raise ValueError("four finite [0,100] body channels required")

    def as_dict(self) -> dict[str, float]:
        return {key: getattr(self, key) for key in CHANNELS}


@dataclass(frozen=True, slots=True)
class PhysicalOutcome:
    body: Body
    terminal: bool
    reasons: tuple[str, ...]
    version: str = PHYSICS_VERSION


def transition(body: Body, action: str, *, berry_food_gain: float = 0.0,
               berry_integrity_delta: float = 0.0,
               drink_water_gain: float = 0.0,
               rest_integrity_gain: float = 0.2,
               sleep_energy_gain: float = 3.0,
               food_decay: float = 0.2,
               water_decay: float = 0.4) -> PhysicalOutcome:
    """Reference local transition, after a separately admitted physical action.

    Mirrors I1 natural-v4 *body* coupling for ordinary actions with an
    externally specified effect. It does not assert accessibility, inventory,
    position, action success, hazards, night, or first-person knowledge.
    The caller must supply only an actually applied effect, never anticipated
    future nutrition. World parity is therefore PARTIAL, not established.
    """
    if type(body) is not Body or action not in COSTS:
        raise ValueError("exact body and known physical action required")
    args = (berry_food_gain, berry_integrity_delta, drink_water_gain,
            rest_integrity_gain, sleep_energy_gain, food_decay, water_decay)
    if any(type(v) not in (int, float) or not isfinite(v) for v in args):
        raise ValueError("non-finite physical effect")
    if (berry_food_gain < 0 or drink_water_gain < 0 or
            rest_integrity_gain < 0 or sleep_energy_gain < 0 or
            food_decay < 0 or water_decay < 0):
        raise ValueError("invalid nonnegative physics")
    if action != "manger" and (berry_food_gain != 0 or berry_integrity_delta != 0):
        raise ValueError("food consequence only follows an applied eat")
    if action != "boire" and drink_water_gain != 0:
        raise ValueError("water consequence only follows an applied drink")

    energy = body.energy
    food = _clamp(body.food - food_decay)
    water = _clamp(body.water - water_decay)
    integrity = body.integrity
    hydrated = water >= 0.05
    if action == "dormir":
        possible = min(sleep_energy_gain, max(0.0, 100.0 - energy))
        gained = min(possible, food / 0.05) if hydrated else 0.0
        energy += gained
        food -= gained * 0.05
    else:
        energy -= COSTS[action]
    if action in ("attendre", "dormir") and hydrated:
        repair = min(rest_integrity_gain, max(0.0, 100.0 - integrity),
                     food / 0.10)
        integrity += repair
        food -= repair * 0.10
    energy = _clamp(energy)
    if action == "manger":
        food = _clamp(food + berry_food_gain)
        integrity = _clamp(integrity + berry_integrity_delta)
    elif action == "boire":
        water = _clamp(water + drink_water_gain)
    next_body = Body(energy, _clamp(food), water, _clamp(integrity))
    reasons = tuple(key for key, fatal in (
        ("zero_food", next_body.food <= 0),
        ("zero_water", next_body.water <= 0),
        ("zero_integrity", next_body.integrity <= 0)) if fatal)
    return PhysicalOutcome(next_body, bool(reasons), reasons)
