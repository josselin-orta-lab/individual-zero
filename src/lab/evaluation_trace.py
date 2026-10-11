"""Independent scientific trace; NEVER part of I0's cognition or causal journal.

This module can be instantiated by a Bench without Oracle and holds only
purpose-specific external measurement records. No I0 or world imports.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class EvaluationRecord:
    sequence: int
    kind: str
    data: Mapping[str, object]


class EvaluationTrace:
    """Separate bench/operator trace, never part of individual causal state."""

    def __init__(self) -> None:
        self._records: list[EvaluationRecord] = []

    @property
    def records(self) -> tuple[EvaluationRecord, ...]:
        return tuple(self._records)

    def append(self, *, kind: str, data: Mapping[str, object]) -> EvaluationRecord:
        if not kind:
            raise ValueError("evaluation record kind must not be empty")
        record = EvaluationRecord(
            sequence=len(self._records),
            kind=kind,
            data=dict(data),
        )
        self._records.append(record)
        return record
