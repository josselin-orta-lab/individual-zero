"""Minimal contracts required to execute and observe an Individual.

These types deliberately avoid encoding assumptions about memory, motivation,
affect, planning, or other cognitive mechanisms. They exist so the Lab can run
an Individual before those mechanisms are scientifically selected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Observation:
    """Input presented to an Individual for one execution cycle."""

    cycle: int
    kind: str
    data: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Action:
    """Externally visible action requested by an Individual."""

    kind: str
    data: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PrimitiveCommand:
    """Primitive command contract shared by I0 and the world boundary."""

    primitive: str
    parameters: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "primitive": self.primitive,
            "parameters": dict(self.parameters),
        }


@dataclass(frozen=True, slots=True)
class StepResult:
    """Observable result of one Individual step."""

    action: Action
    state: Mapping[str, object] = field(default_factory=dict)


@runtime_checkable
class Individual(Protocol):
    """Smallest contract required by the neutral Lab runtime."""

    def reset(self, *, seed: int) -> None:
        """Reset the Individual to a reproducible initial state."""

    def step(self, observation: Observation) -> StepResult:
        """Process one observation and return an observable step result."""
