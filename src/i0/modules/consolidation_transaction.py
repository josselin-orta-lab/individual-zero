"""Stage-10 private consolidation transaction state machine (MVP 15.6).

This is an integration boundary, NOT a six-pass semantic implementation.
A pass executor must be supplied by the actual causal owner. No active
knowledge or slow-history version is published by this component.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Callable

PASSES = (
    "episode_selection", "interleaved_replay", "hypothesis_extraction",
    "procedural_compilation", "kappa_recalibration", "index_maintenance",
)


@dataclass(frozen=True)
class ConsolidationCut:
    world_step: int
    journal_event_id: str
    history_version: str

    def validate(self) -> None:
        if type(self.world_step) is not int or self.world_step < 1:
            raise ValueError("invalid causal cut world step")
        if not self.journal_event_id or not self.history_version:
            raise ValueError("causal cut and source history version required")


@dataclass(frozen=True)
class PassCheckpoint:
    name: str
    candidate: object


class ConsolidationTransaction:
    """Single frozen batch, six private passes and resumable checkpoints.

    Work units are logical pass invocations, never wall-clock time. A pass
    executor receives a private copy and returns the next private candidate;
    the executor cannot publish owner states. A failed pass preserves the
    last checkpoint. Atomic installation of h and active owners is deliberately
    external and MUST be provided by the scheduler in a later integration.
    """

    schema = "stage10-consolidation-transaction-v1"

    def __init__(self, *, consolidation_id: str, cut: ConsolidationCut,
                 episode_refs: tuple[str, ...], history_candidate: object):
        cut.validate()
        if not isinstance(consolidation_id, str) or not consolidation_id:
            raise ValueError("stable consolidation identifier required")
        if not isinstance(episode_refs, tuple) or any(
            not isinstance(ref, str) or not ref for ref in episode_refs
        ) or len(set(episode_refs)) != len(episode_refs):
            raise ValueError("frozen batch needs unique episode references")
        self.id = consolidation_id
        self.cut = cut
        self._batch = episode_refs
        self._checkpoints: list[PassCheckpoint] = []
        self._candidate = deepcopy(history_candidate)
        self._initial = deepcopy(history_candidate)
        self._status = "active"

    @property
    def batch(self) -> tuple[str, ...]:
        return self._batch

    @property
    def status(self) -> str:
        return self._status

    @property
    def cursor(self) -> int:
        return len(self._checkpoints)

    @property
    def completed_passes(self) -> tuple[str, ...]:
        return tuple(point.name for point in self._checkpoints)

    def candidate_copy(self) -> object:
        return deepcopy(self._candidate)

    def interrupt(self) -> None:
        if self._status != "active":
            raise ValueError("only an active transaction can be interrupted")
        self._candidate = deepcopy(
            self._checkpoints[-1].candidate if self._checkpoints else self._initial
        )
        self._status = "suspended"

    def resume(self) -> None:
        if self._status != "suspended":
            raise ValueError("only suspended transaction may resume")
        self._status = "active"

    def run_pass(self, *, name: str, executor: Callable[[object, tuple[str, ...], ConsolidationCut], object],
                 validator: Callable[[object], bool]) -> None:
        if self._status != "active" or self.cursor == len(PASSES):
            raise ValueError("transaction not active or already complete")
        if name != PASSES[self.cursor]:
            raise ValueError("passes must be completed in normative order")
        before = deepcopy(self._candidate)
        result = executor(before, self._batch, self.cut)
        if validator(result) is not True:
            raise ValueError("private consolidation pass failed technical validation")
        candidate = deepcopy(result)
        self._checkpoints.append(PassCheckpoint(name, deepcopy(candidate)))
        self._candidate = candidate

    def validated_candidate(self, *, validator: Callable[[object], bool]) -> object:
        if self._status != "active" or self.cursor != len(PASSES):
            raise ValueError("all six passes must complete before publication")
        candidate = deepcopy(self._candidate)
        if validator(candidate) is not True:
            raise ValueError("completed private history failed validation")
        return candidate

    def export_causal_state(self) -> dict[str, object]:
        return deepcopy({
            "schema": self.schema,
            "id": self.id,
            "cut": {
                "world_step": self.cut.world_step,
                "journal_event_id": self.cut.journal_event_id,
                "history_version": self.cut.history_version,
            },
            "batch": list(self._batch),
            "initial": self._initial,
            "checkpoints": [
                {"name": point.name, "candidate": point.candidate}
                for point in self._checkpoints
            ],
            "candidate": self._candidate,
            "status": self._status,
        })

    @classmethod
    def restore(cls, state: Mapping[str, object]) -> "ConsolidationTransaction":
        if not isinstance(state, Mapping) or set(state) != {
            "schema", "id", "cut", "batch", "initial", "checkpoints",
            "candidate", "status",
        } or state.get("schema") != cls.schema:
            raise ValueError("incompatible consolidation snapshot")
        raw_cut = state["cut"]
        if not isinstance(raw_cut, Mapping) or set(raw_cut) != {
            "world_step", "journal_event_id", "history_version"
        }:
            raise ValueError("invalid consolidation cut snapshot")
        cut = ConsolidationCut(**raw_cut)
        batch = state["batch"]
        if not isinstance(batch, list):
            raise ValueError("invalid frozen batch snapshot")
        restored = cls(consolidation_id=state["id"], cut=cut,
                       episode_refs=tuple(batch), history_candidate=state["initial"])
        raw_points = state["checkpoints"]
        if not isinstance(raw_points, list) or len(raw_points) > len(PASSES):
            raise ValueError("invalid consolidation pass cursor")
        for index, point in enumerate(raw_points):
            if not isinstance(point, Mapping) or set(point) != {"name", "candidate"} or point["name"] != PASSES[index]:
                raise ValueError("invalid checkpoint chronology")
            restored._checkpoints.append(
                PassCheckpoint(point["name"], deepcopy(point["candidate"]))
            )
        if state["status"] not in {"active", "suspended"}:
            raise ValueError("invalid transaction status")
        expected = restored._checkpoints[-1].candidate if restored._checkpoints else restored._initial
        if state["candidate"] != expected:
            raise ValueError("snapshot candidate differs from last checkpoint")
        restored._candidate = deepcopy(expected)
        restored._status = state["status"]
        return restored


class ConsolidationSlot:
    """Enforces INV-47 independent of the Stage-11 runtime."""

    def __init__(self) -> None:
        self._current: ConsolidationTransaction | None = None

    @property
    def current(self) -> ConsolidationTransaction | None:
        return self._current

    def begin(self, transaction: ConsolidationTransaction) -> None:
        if self._current is not None:
            raise ValueError("suspended or active consolidation takes priority")
        if transaction.status != "active" or transaction.cursor:
            raise ValueError("only a fresh transaction may begin")
        self._current = transaction

    def resume(self) -> ConsolidationTransaction:
        if self._current is None:
            raise ValueError("no suspended consolidation")
        self._current.resume()
        return self._current

    def clear_after_coordinated_commit(self, transaction_id: str) -> None:
        if self._current is None or self._current.id != transaction_id:
            raise ValueError("transaction identity mismatch")
        if self._current.status != "active" or self._current.cursor != len(PASSES):
            raise ValueError("transaction not ready for coordinated publication")
        self._current = None
