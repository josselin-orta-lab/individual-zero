"""Offline Stage-6 equipment-corpus recording and coverage checks.

This module belongs to Lab. It may observe a controlled training world while
constructing examples, but the resulting EquipmentCorpus contains only the
accessible SimulationState presented to equipment.

Spec: 12.5, P-46, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass

from i0.equipment import EquipmentCorpus, EquipmentCorpusExample
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture

from .world import WorldBody


REQUIRED_EQUIPMENT_FAMILIES = frozenset(
    {
        "movement_free",
        "movement_blocked",
        "collection_without_tool",
        "collection_with_tool",
        "resource_consumption",
        "drinking",
        "tool_crafting",
        "stone_placement",
        "shelter_state",
        "creature_day",
        "creature_night",
        "sleep",
        "wait",
    }
)


@dataclass(frozen=True, slots=True)
class CorpusCoverage:
    required: tuple[str, ...]
    present: tuple[str, ...]
    missing: tuple[str, ...]
    extra: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing


def evaluate_corpus_coverage(corpus: EquipmentCorpus) -> CorpusCoverage:
    corpus.validate()
    present = set(corpus.families())
    return CorpusCoverage(
        required=tuple(sorted(REQUIRED_EQUIPMENT_FAMILIES)),
        present=tuple(sorted(present)),
        missing=tuple(sorted(REQUIRED_EQUIPMENT_FAMILIES - present)),
        extra=tuple(sorted(present - REQUIRED_EQUIPMENT_FAMILIES)),
    )


def require_corpus_coverage(corpus: EquipmentCorpus) -> None:
    coverage = evaluate_corpus_coverage(corpus)
    if not coverage.complete:
        raise ValueError(
            "equipment corpus missing required families: "
            + ", ".join(coverage.missing)
        )


class EquipmentCorpusRecorder:
    """Record controlled training transitions as accessible-state examples."""

    def __init__(self, *, corpus_version: str) -> None:
        if not corpus_version:
            raise ValueError("corpus version must not be empty")
        self._version = corpus_version
        self._examples: list[EquipmentCorpusExample] = []

    def record_transition(
        self,
        *,
        world: WorldBody,
        t_monde: int,
        family: str,
        command: PrimitiveCommand,
    ) -> EquipmentCorpusExample:
        if not family:
            raise ValueError("corpus family must not be empty")
        if t_monde < 1:
            raise ValueError("t_monde must be >= 1")

        perception = SymbolicPerception()
        before_capture = perception.capture(
            local_state=world.capture_local(t_monde=t_monde).as_dict(),
            telemetry=world.telemetry(),
        )
        before = state_from_capture(
            capture=before_capture,
            is_night=world.is_night(t_monde),
        )

        transition = world.apply(command, t_monde=t_monde)

        after_capture = perception.capture(
            local_state=world.capture_local(t_monde=t_monde + 1).as_dict(),
            telemetry=world.telemetry(),
        )
        after = state_from_capture(
            capture=after_capture,
            is_night=world.is_night(t_monde + 1),
        )

        example = EquipmentCorpusExample(
            family=family,
            state=before,
            command=command,
            observed_next_state=after,
            terminal=transition.lethal,
        )
        example.validate()
        self._examples.append(example)
        return example

    def build(self) -> EquipmentCorpus:
        corpus = EquipmentCorpus(
            version=self._version,
            examples=tuple(self._examples),
        )
        corpus.validate()
        return corpus
