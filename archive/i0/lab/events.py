"""Structured events emitted by the neutral Lab runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class LabEvent:
    """A serializable event emitted during a run."""

    run_id: str
    kind: str
    cycle: int | None = None
    data: Mapping[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "kind": self.kind,
            "cycle": self.cycle,
            "data": dict(self.data),
        }
