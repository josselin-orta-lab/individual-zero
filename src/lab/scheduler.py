"""Deterministic simulated-time scheduler for normative Stage 1.

The scheduler owns the technical clock and attempt_ref. It does not own
Competition's deliberation counter c; callers provide the cycle index.

Spec: 3.1-3.4, 5.3, 17.2, 20.3 Stage 1, DC-11, INV-22, INV-33, INV-53.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Mapping, Sequence

from .determinism import deterministic_id
from .journal import HashChainedJournal


class CyclePhase(IntEnum):
    FREEZE = 0
    PRODUCTION = 1
    SELECTION = 2
    EVALUATION = 3
    ACCUMULATION_DECISION = 4
    CLOSURE = 5


@dataclass(frozen=True, slots=True)
class StepAttempt:
    t_monde: int
    attempt_index: int
    attempt_ref: str


@dataclass(frozen=True, slots=True)
class PhaseContext:
    t_monde: int
    cycle: int
    attempt_ref: str
    phase: CyclePhase


PhaseHook = Callable[[PhaseContext], None]


class Scheduler:
    """Sequential scheduler with canonical six-phase execution."""

    def __init__(
        self,
        *,
        journal: HashChainedJournal,
        phase_component_order: Mapping[int, Sequence[str]],
    ) -> None:
        expected_phases = {phase.value for phase in CyclePhase}
        if set(phase_component_order) != expected_phases:
            raise ValueError("phase_component_order must define phases 0 through 5")

        normalized: dict[CyclePhase, tuple[str, ...]] = {}
        for phase in CyclePhase:
            names = tuple(phase_component_order[phase.value])
            if len(names) != len(set(names)):
                raise ValueError(f"duplicate component in phase {phase.value}")
            normalized[phase] = names

        self._journal = journal
        self._phase_component_order = normalized
        self._t_monde = 0
        self._active_attempt: StepAttempt | None = None
        self._journal_sequence = 0

    @property
    def t_monde(self) -> int:
        return self._t_monde

    @property
    def active_attempt(self) -> StepAttempt | None:
        return self._active_attempt

    @property
    def owner_id(self) -> str:
        return "scheduler.clock"

    def export_causal_state(self) -> object:
        attempt = self._active_attempt
        return {
            "t_monde": self._t_monde,
            "active_attempt": None
            if attempt is None
            else {
                "t_monde": attempt.t_monde,
                "attempt_index": attempt.attempt_index,
                "attempt_ref": attempt.attempt_ref,
            },
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("scheduler causal state must be a mapping")
        t_monde = state.get("t_monde")
        if not isinstance(t_monde, int) or t_monde < 0:
            raise ValueError("scheduler t_monde must be a non-negative integer")
        raw_attempt = state.get("active_attempt")
        if raw_attempt is None:
            attempt = None
        elif isinstance(raw_attempt, Mapping):
            attempt_t = raw_attempt.get("t_monde")
            attempt_index = raw_attempt.get("attempt_index")
            attempt_ref = raw_attempt.get("attempt_ref")
            if (
                not isinstance(attempt_t, int)
                or attempt_t != t_monde
                or not isinstance(attempt_index, int)
                or attempt_index < 0
                or not isinstance(attempt_ref, str)
                or not attempt_ref
            ):
                raise ValueError("invalid scheduler active_attempt state")
            attempt = StepAttempt(
                t_monde=attempt_t,
                attempt_index=attempt_index,
                attempt_ref=attempt_ref,
            )
        else:
            raise ValueError("invalid scheduler active_attempt state")

        self._t_monde = t_monde
        self._active_attempt = attempt

    def _write(
        self,
        *,
        kind: str,
        cycle: int | None = None,
        phase: CyclePhase | None = None,
        data: Mapping[str, object] | None = None,
    ) -> None:
        attempt_ref = (
            self._active_attempt.attempt_ref
            if self._active_attempt is not None
            else "no-active-attempt"
        )
        event_id = deterministic_id(
            "journal-event-v1",
            "scheduler",
            self._t_monde,
            cycle,
            attempt_ref,
            self._journal_sequence,
            kind,
        )
        self._journal_sequence += 1
        payload: dict[str, object] = {
            "emitter": "scheduler",
            "kind": kind,
            "t_monde": self._t_monde,
            "attempt_ref": attempt_ref,
            "data": dict(data or {}),
        }
        if cycle is not None:
            payload["cycle"] = cycle
        if phase is not None:
            payload["phase"] = phase.value
        self._journal.append(event_id=event_id, causal_event=payload)

    def open_step(self) -> StepAttempt:
        if self._active_attempt is not None:
            raise RuntimeError("cannot open a new world step while one is active")

        self._t_monde += 1
        attempt = StepAttempt(
            t_monde=self._t_monde,
            attempt_index=0,
            attempt_ref=deterministic_id(
                "attempt-v1",
                self._t_monde,
                0,
            ),
        )
        self._active_attempt = attempt
        self._write(
            kind="step_opened",
            data={"attempt_index": attempt.attempt_index},
        )
        return attempt

    def run_cycle(
        self,
        *,
        cycle: int,
        hooks: Mapping[CyclePhase, Mapping[str, PhaseHook]],
    ) -> None:
        if self._active_attempt is None:
            raise RuntimeError("a cognitive cycle requires an active world step")
        if cycle < 1:
            raise ValueError("cycle index must be >= 1")

        self._write(kind="cycle_opened", cycle=cycle)

        for phase in CyclePhase:
            expected_components = self._phase_component_order[phase]
            provided = hooks.get(phase)
            if provided is None:
                raise ValueError(f"missing hooks for phase {phase.value}")
            if set(provided) != set(expected_components):
                missing = sorted(set(expected_components) - set(provided))
                extra = sorted(set(provided) - set(expected_components))
                raise ValueError(
                    f"phase {phase.value} hook mismatch; "
                    f"missing={missing}, extra={extra}"
                )

            context = PhaseContext(
                t_monde=self._t_monde,
                cycle=cycle,
                attempt_ref=self._active_attempt.attempt_ref,
                phase=phase,
            )
            self._write(kind="phase_opened", cycle=cycle, phase=phase)

            for component in expected_components:
                provided[component](context)
                self._write(
                    kind="phase_component_completed",
                    cycle=cycle,
                    phase=phase,
                    data={"component": component},
                )

            self._write(kind="phase_closed", cycle=cycle, phase=phase)

        self._write(kind="cycle_closed", cycle=cycle)

    def close_step(
        self,
        *,
        outcome: str,
        applied_command_count: int,
        world_advance_count: int,
    ) -> None:
        if self._active_attempt is None:
            raise RuntimeError("cannot close a world step when none is active")

        if outcome in {"normal", "dead"}:
            expected = (1, 1)
        elif outcome in {"blocked", "external_stop"}:
            expected = (0, 0)
        else:
            raise ValueError(f"unknown step outcome: {outcome}")

        actual = (applied_command_count, world_advance_count)
        if actual != expected:
            raise ValueError(
                f"step outcome {outcome!r} requires counts {expected}, got {actual}"
            )

        self._write(
            kind="step_closed",
            data={
                "outcome": outcome,
                "applied_command_count": applied_command_count,
                "world_advance_count": world_advance_count,
            },
        )
        self._active_attempt = None
