"""Logged external scenario engine for normative Stage 2.

Scenario state is external but causal when it changes deterministic continuation.
Every injection is journaled before application.

Spec: 4.6, 17.6, 19.2, 20.3 Stage 2, INV-33.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import canonical_causal_bytes, deterministic_id
from .journal import HashChainedJournal
from .world import WorldBody


@dataclass(frozen=True, slots=True)
class ScenarioEvent:
    t_monde: int
    sequence: int
    operation: str
    payload: Mapping[str, object]
    phase: str = "before_step"

    def as_dict(self) -> dict[str, object]:
        data = {
            "t_monde": self.t_monde,
            "sequence": self.sequence,
            "operation": self.operation,
            "payload": deepcopy(dict(self.payload)),
        }
        # Do not rewrite canonical historical schedules or journal payloads.
        if self.phase != "before_step":
            data["phase"] = self.phase
        return data


class ScenarioInputRejected(ValueError):
    """An external input was rejected; its world-step batch is cancelled."""


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
        # Inputs which cannot be canonically journaled before application
        # must be rejected at scenario registration, not at world-step open
        # after Scheduler has already advanced (normative 4.6 / INV-33).
        checked: list[ScenarioEvent] = []
        for event in events:
            if (
                not isinstance(event, ScenarioEvent)
                or type(event.t_monde) is not int
                or event.t_monde < 1
                or type(event.sequence) is not int
                or event.sequence < 0
                or not isinstance(event.operation, str)
                or not event.operation.strip()
                or event.phase not in ("before_step", "after_admission")
                or not isinstance(event.payload, Mapping)
            ):
                raise ValueError("malformed external scenario event schema")
            try:
                canonical_causal_bytes(event.as_dict())
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "external scenario event is not canonically encodable"
                ) from exc
            checked.append(event)
        # The source ScenarioEvent dataclass is frozen, but its nested
        # payload Mapping may not be. Own a complete detached program:
        # neither the caller nor exported/returned views can rewrite it.
        self._events = tuple(
            ScenarioEvent(
                t_monde=event.t_monde,
                sequence=event.sequence,
                operation=event.operation,
                payload=deepcopy(dict(event.payload)),
                phase=event.phase,
            )
            for event in sorted(
                checked,
                key=lambda row: (
                    row.t_monde,
                    0 if row.phase == "before_step" else 1,
                    row.sequence,
                ),
            )
        )
        if len({(e.t_monde, e.sequence) for e in self._events}) != len(self._events):
            raise ValueError("scenario event coordinates must be unique")
        self._journal = journal
        self._next_index = 0
        # Only failure paths carry this causal halt marker. Successful
        # historical scenario snapshots retain exactly their previous bytes.
        self._rejected_event: tuple[int, int] | None = None

    @property
    def halted(self) -> bool:
        return self._rejected_event is not None

    def apply_for_step(self, *, t_monde: int, world: WorldBody) -> tuple[ScenarioEvent, ...]:
        if self.halted:
            raise RuntimeError("rejected external scenario branch cannot continue")

        # External events for one world-step opening are a single operation
        # for causal recovery. Snapshot the real WorldBody, never its oracle,
        # only when an input is actually due at this simulated instant.
        batch_start = self._next_index
        before_world = (
            deepcopy(world.export_causal_state())
            if batch_start < len(self._events)
            and self._events[batch_start].t_monde == t_monde
            else None
        )
        applied: list[ScenarioEvent] = []
        while self._next_index < len(self._events):
            event = self._events[self._next_index]
            if event.t_monde == t_monde and event.phase == "after_admission":
                raise RuntimeError("after-admission scenario requires mortal dispatch")
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
            receipt_stage = "received"
            try:
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
                        "payload": deepcopy(dict(event.payload)),
                    },
                )
                receipt_stage = "application"
                world.apply_scenario_event(event.operation, event.payload)
                receipt_stage = "applied"
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
            except Exception as error:
                # Any failure at this world-input boundary is fail-closed.
                # Earlier successful inputs in this *same* step and even a
                # partially applied failing input must leave no world change.
                self._next_index = batch_start
                self._rejected_event = (event.t_monde, event.sequence)
                recovery_error = None
                try:
                    if before_world is None:
                        raise RuntimeError("missing external input batch recovery point")
                    world.restore_causal_state(deepcopy(before_world))
                except Exception as exc:
                    recovery_error = exc

                self._journal.append(
                    event_id=deterministic_id(
                        "journal-event-v1",
                        "scenario", self._scenario_id, self._version,
                        event.t_monde, event.sequence, "rejected",
                    ),
                    causal_event={
                        "emitter": "scenario",
                        "kind": "external_input_rejected",
                        "scenario_id": self._scenario_id,
                        "scenario_version": self._version,
                        "t_monde": event.t_monde,
                        "sequence": event.sequence,
                        "operation": event.operation,
                        "reason": (
                            "technical_journal_failure"
                            if receipt_stage != "application"
                            else (
                                "invalid_operation_or_payload"
                                if isinstance(
                                    error, (ValueError, TypeError, KeyError, OverflowError),
                                ) else "application_error"
                            )
                        ),
                        "error_type": type(error).__name__,
                        "world_recovered": recovery_error is None,
                        "previous_inputs_reverted": len(applied),
                    },
                )
                if applied:
                    self._journal.append(
                        event_id=deterministic_id(
                            "journal-event-v1",
                            "scenario", self._scenario_id, self._version,
                            event.t_monde, event.sequence, "batch-rollback",
                        ),
                        causal_event={
                            "emitter": "scenario",
                            "kind": "external_input_batch_rolled_back",
                            "scenario_id": self._scenario_id,
                            "scenario_version": self._version,
                            "t_monde": event.t_monde,
                            "sequence": event.sequence,
                            "previous_inputs_reverted": len(applied),
                            "world_recovered": recovery_error is None,
                        },
                    )
                if recovery_error is not None:
                    raise RuntimeError(
                        "external input rejected and WorldBody rollback failed"
                    ) from recovery_error
                raise ScenarioInputRejected(
                    "external scenario input rejected; branch fail-stopped"
                ) from error
            self._next_index += 1
            applied.append(event)

        return tuple(deepcopy(event) for event in applied)

    def apply_for_step_irreversible(
        self, *, t_monde: int, world: WorldBody,
        phase: str = "before_step",
    ) -> tuple[ScenarioEvent, ...]:
        """Prepare a whole external batch privately, then commit without rewind.

        v1.3 opt-in only. The physical world is unchanged while the detached
        candidate is being validated. Once publication starts, *no* failure
        attempts to restore a prior living state. A failed receipt stops the
        entire runtime through the caller's technical-halt boundary.

        All scenario evidence stays in the Lab. No individual is given the
        future schedule, the private candidate or an oracle read.
        """
        if self.halted:
            raise RuntimeError("halted external scenario cannot continue")
        if type(t_monde) is not int or t_monde < 1:
            raise ValueError("invalid scenario world step")
        if phase not in ("before_step", "after_admission"):
            raise ValueError("unknown external-input application phase")
        start = self._next_index
        due: list[ScenarioEvent] = []
        for event in self._events[start:]:
            if event.t_monde > t_monde:
                break
            if event.t_monde < t_monde:
                raise RuntimeError("scenario event was skipped before application")
            if event.phase != phase:
                if phase == "before_step" and event.phase == "after_admission":
                    break
                raise RuntimeError("earlier external input phase was skipped")
            due.append(event)
        if not due:
            return ()

        # Private candidate construction is not a rollback of the living
        # world. It is an uncommitted proposal under the world owner's rules.
        publication_attempted = False
        published = False
        try:
            candidate = deepcopy(world)
            for event in due:
                candidate.apply_scenario_event(
                    event.operation, deepcopy(dict(event.payload)),
                )
            proposed_state = candidate.export_causal_state()
            canonical_causal_bytes(proposed_state)

            for event in due:
                self._journal.append(
                    event_id=deterministic_id(
                        "journal-event-v1", "scenario", self._scenario_id,
                        self._version, event.t_monde, event.sequence,
                    ),
                    causal_event={
                        "emitter": "scenario",
                        "kind": "external_input_received",
                        "scenario_id": self._scenario_id,
                        "scenario_version": self._version,
                        "t_monde": event.t_monde,
                        "sequence": event.sequence,
                        "operation": event.operation,
                        "payload": deepcopy(dict(event.payload)),
                        **({"phase": event.phase}
                           if event.phase != "before_step" else {}),
                    },
                )

            # Forward commit accepts only the already checked operation batch.
            # No arbitrary historical state can be imported into mortal I0.
            publication_attempted = True
            world.apply_scenario_batch_atomically(tuple(
                (event.operation, event.payload) for event in due
            ))
            published = True
            self._next_index = start + len(due)
            for event in due:
                self._journal.append(
                    event_id=deterministic_id(
                        "journal-event-v1", "scenario", self._scenario_id,
                        self._version, event.t_monde, event.sequence, "applied",
                    ),
                    causal_event={
                        "emitter": "scenario",
                        "kind": "external_input_applied",
                        "scenario_id": self._scenario_id,
                        "scenario_version": self._version,
                        "t_monde": event.t_monde,
                        "sequence": event.sequence,
                        **({"phase": event.phase}
                           if event.phase != "before_step" else {}),
                    },
                )
            return tuple(deepcopy(event) for event in due)
        except Exception as original:
            # A publication failure is potentially a partial external
            # transition. Even after an invalid private proposal, fail closed.
            # NEVER call world.restore_causal_state(previous_state).
            self._rejected_event = (due[0].t_monde, due[0].sequence)
            self._next_index = start
            try:
                self._journal.append(
                    event_id=deterministic_id(
                        "journal-event-v1", "scenario", self._scenario_id,
                        self._version, due[0].t_monde, due[0].sequence,
                        "irreversible-halt",
                    ),
                    causal_event={
                        "emitter": "scenario",
                        "kind": "external_input_batch_halted",
                        "scenario_id": self._scenario_id,
                        "scenario_version": self._version,
                        "t_monde": due[0].t_monde,
                        "sequence": due[0].sequence,
                        "input_count": len(due),
                        "world_publication_attempted": publication_attempted,
                        "world_publication_confirmed": published,
                        "error_type": type(original).__name__,
                    },
                )
            except Exception:
                # If the journal itself is unavailable, a missing receipt
                # is not permission to resume or to re-apply the batch.
                pass
            raise ScenarioInputRejected(
                "irreversible external scenario halted; no world rewind"
            ) from original


    def export_causal_state(self) -> object:
        state = {
            "scenario_id": self._scenario_id,
            "version": self._version,
            "next_index": self._next_index,
            "events": [event.as_dict() for event in self._events],
        }
        if self._rejected_event is not None:
            state["rejected_event"] = {
                "t_monde": self._rejected_event[0],
                "sequence": self._rejected_event[1],
            }
        return state

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("scenario state must be a mapping")
        if state.get("scenario_id") != self._scenario_id:
            raise ValueError("scenario id mismatch")
        if state.get("version") != self._version:
            raise ValueError("scenario version mismatch")
        # The schedule is causal external state. Matching only the ID,
        # version and cursor would accept a different future while falsely
        # claiming an exact interval replay (INV-33).
        if state.get("events") != [event.as_dict() for event in self._events]:
            raise ValueError("scenario event schedule mismatch")
        next_index = state.get("next_index")
        if type(next_index) is not int or not 0 <= next_index <= len(self._events):
            raise ValueError("invalid scenario next_index")
        rejected = state.get("rejected_event")
        rejected_at = None
        if rejected is not None:
            if (
                not isinstance(rejected, Mapping)
                or set(rejected) != {"t_monde", "sequence"}
                or type(rejected["t_monde"]) is not int
                or type(rejected["sequence"]) is not int
            ):
                raise ValueError("invalid rejected scenario input marker")
            rejected_at = (rejected["t_monde"], rejected["sequence"])
            failed_event_positions = [
                index for index, event in enumerate(self._events)
                if (event.t_monde, event.sequence) == rejected_at
            ]
            first_at_step = next(
                (
                    index for index, event in enumerate(self._events)
                    if event.t_monde == rejected_at[0]
                ),
                None,
            )
            # apply_for_step always compensates the WHOLE input batch
            # and rewinds the cursor to its first event, even if an
            # error happened after earlier inputs for this step.
            if (
                not failed_event_positions
                or first_at_step is None
                or next_index != first_at_step
            ):
                raise ValueError(
                    "invalid rejected scenario input marker or cursor"
                )
        self._next_index = next_index
        self._rejected_event = rejected_at
