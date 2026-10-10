"""Logged external scenario engine for normative Stage 2.

Scenario state is external but causal when it changes deterministic continuation.
Every injection is journaled before application.

Spec: 4.6, 17.6, 19.2, 20.3 Stage 2, INV-33.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import deterministic_id
from .journal import HashChainedJournal
from .world import WorldBody


@dataclass(frozen=True, slots=True)
class ScenarioEvent:
    t_monde: int
    sequence: int
    operation: str
    payload: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "t_monde": self.t_monde,
            "sequence": self.sequence,
            "operation": self.operation,
            "payload": dict(self.payload),
        }


class InjectedScenario:
    """Deterministic external-input schedule applied only through the world."""

    owner_id = "scenario"

    def __init__(
        self,
        *,
        scenario_id: str,
        version: str,
        events: Sequence[ScenarioEvent],
        journal: HashChainedJournal,
    ) -> None:
        if not scenario_id or not version:
            raise ValueError("scenario id and version must not be empty")
        self._scenario_id = scenario_id
        self._version = version
        self._events = tuple(
            sorted(events, key=lambda event: (event.t_monde, event.sequence))
        )
        if len({(e.t_monde, e.sequence) for e in self._events}) != len(self._events):
            raise ValueError("scenario event coordinates must be unique")
        self._journal = journal
        self._next_index = 0

    def apply_for_step(self, *, t_monde: int, world: WorldBody) -> tuple[ScenarioEvent, ...]:
        applied: list[ScenarioEvent] = []
        while self._next_index < len(self._events):
            event = self._events[self._next_index]
            if event.t_monde != t_monde:
                if event.t_monde > t_monde:
                    break
                raise RuntimeError("scenario event was skipped before application")

            event_id = deterministic_id(
                "journal-event-v1",
                "scenario",
                self._scenario_id,
                self._version,
                event.t_monde,
                event.sequence,
            )
            self._journal.append(
                event_id=event_id,
                causal_event={
                    "emitter": "scenario",
                    "kind": "external_input_received",
                    "scenario_id": self._scenario_id,
                    "scenario_version": self._version,
                    "t_monde": event.t_monde,
                    "sequence": event.sequence,
                    "operation": event.operation,
                    "payload": dict(event.payload),
                },
            )
            world.apply_scenario_event(event.operation, event.payload)
            self._journal.append(
                event_id=deterministic_id(
                    "journal-event-v1",
                    "scenario",
                    self._scenario_id,
                    self._version,
                    event.t_monde,
                    event.sequence,
                    "applied",
                ),
                causal_event={
                    "emitter": "scenario",
                    "kind": "external_input_applied",
                    "scenario_id": self._scenario_id,
                    "scenario_version": self._version,
                    "t_monde": event.t_monde,
                    "sequence": event.sequence,
                },
            )
            self._next_index += 1
            applied.append(event)

        return tuple(applied)

    def export_causal_state(self) -> object:
        return {
            "scenario_id": self._scenario_id,
            "version": self._version,
            "next_index": self._next_index,
            "events": [event.as_dict() for event in self._events],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("scenario state must be a mapping")
        if state.get("scenario_id") != self._scenario_id:
            raise ValueError("scenario id mismatch")
        if state.get("version") != self._version:
            raise ValueError("scenario version mismatch")
        next_index = state.get("next_index")
        if not isinstance(next_index, int) or not 0 <= next_index <= len(self._events):
            raise ValueError("invalid scenario next_index")
        self._next_index = next_index
