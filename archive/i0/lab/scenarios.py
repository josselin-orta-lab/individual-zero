"""Scenario contracts and small deterministic technical scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from i0.interfaces import Observation


class Scenario(Protocol):
    """Source of observations for a Lab run."""

    label: str

    def observation(self, cycle: int) -> Observation:
        """Return the observation presented at a given cycle."""


@dataclass(frozen=True, slots=True)
class SmokeScenario:
    """Technical smoke scenario, not a scientific benchmark.

    The scenario emits one deterministic tick observation per cycle.
    """

    label: str = "bootstrap-smoke"

    def observation(self, cycle: int) -> Observation:
        if cycle < 0:
            raise ValueError("cycle must be non-negative")

        return Observation(
            cycle=cycle,
            kind="tick",
            data={
                "scenario": self.label,
                "value": cycle,
            },
        )
