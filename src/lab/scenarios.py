"""Small deterministic scenarios used to validate the Lab runtime."""

from __future__ import annotations

from dataclasses import dataclass

from i0.interfaces import Observation


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
