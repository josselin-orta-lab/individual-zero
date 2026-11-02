"""I2-native immutable birth trait coordinates, without I1 runtime imports.

The five raw coordinates are comparable inputs, NOT a copy of I1's
Stage5/Gatekeeper learning or action selection. No cognition consumes these yet.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite

CHANNELS = ("reward_sensitivity", "threat_sensitivity", "exploration",
            "goal_protection", "affiliation")
VERSION = "i2-comparable-five-coordinate-birth-v1"


@dataclass(frozen=True, slots=True)
class BirthTemperament:
    reward_sensitivity: float
    threat_sensitivity: float
    exploration: float
    goal_protection: float
    affiliation: float

    def __post_init__(self) -> None:
        if any(not isfinite(v) or not -1 <= v <= 1
               for v in (self.reward_sensitivity, self.threat_sensitivity,
                         self.exploration, self.goal_protection, self.affiliation)):
            raise ValueError("exact finite five-coordinate [-1,1] temperament")

    def as_dict(self) -> dict[str, float]:
        return {key: getattr(self, key) for key in CHANNELS}


def birth_temperament(*, individual_ref: str,
                      paired_research_source: str | None = None) -> BirthTemperament:
    """Derive independent native traits from a fixed public research key.

    A paired source may be shared across I1 and I2 as an experimental
    parameter, never as inherited life state. The I1 hash/version is not
    assumed equal: actual matching must be verified from recorded coordinates
    at genesis before comparative cohorts.
    """
    if (type(individual_ref) is not str or
            not individual_ref.startswith("i2:") or
            not 3 <= len(individual_ref) <= 128):
        raise ValueError("I2-only bounded identity required")
    key = paired_research_source if paired_research_source is not None else individual_ref
    if (type(key) is not str or not 3 <= len(key) <= 128 or
            (paired_research_source is not None and
             not key.startswith("research-pair:"))):
        raise ValueError("only declared paired research sources allowed")
    values = []
    for channel in CHANNELS:
        digest = sha256((VERSION + ":" + key + ":" + channel).encode()).digest()
        values.append(round(2.0 * int.from_bytes(digest[:8], "big")
                            / (2**64 - 1) - 1.0, 6))
    return BirthTemperament(*values)


def declared_temperament(values: dict[str, float]) -> BirthTemperament:
    """Explicit externally preregistered shared raw coordinates, not hidden outcomes."""
    if type(values) is not dict or set(values) != set(CHANNELS):
        raise ValueError("five exact birth coordinates required")
    return BirthTemperament(*(values[name] for name in CHANNELS))
