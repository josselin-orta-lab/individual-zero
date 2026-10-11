"""Terminal mortality and independent safety-block protocol for I0 vNext.

WorldBody owns the actual physical consequences, including lethal transitions.
This protocol records a terminal outcome; it never restores an earlier world,
body, cognitive state, or random stream, and never retries a lethal action.
Technical death detection stays outside the individual's learning interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .bench import EvaluationBench
from .determinism import deterministic_id
from .journal import HashChainedJournal
from .scheduler import Scheduler
from .world import Command, TransitionResult, command_digest


@dataclass(frozen=True, slots=True)
class SafetyProtocolConfig:
    version: str
    lethal_max: int  # Legacy fixture input; ignored in the mortal runtime.
    mode: str  # campaign | diagnostic; for nonlethal safety blocks only

    def validate(self) -> None:
        if not self.version:
            raise ValueError("safety protocol version must not be empty")
        if not isinstance(self.lethal_max, int):
            raise ValueError("legacy lethal_max must be an integer")
        if self.mode not in {"campaign", "diagnostic"}:
            raise ValueError("safety protocol mode must be campaign or diagnostic")


class MortalityProtocol:
    """External terminal-state owner; no rewind, rescue mask or retry."""

    owner_id = "scheduler.mortality_protocol"

    def __init__(
        self,
        *,
        config: SafetyProtocolConfig,
        scheduler: Scheduler,
        journal: HashChainedJournal,
        bench: EvaluationBench,
    ) -> None:
        config.validate()
        self._config = config
        self._scheduler = scheduler
        self._journal = journal
        self._bench = bench
        self._dead = False
        self._blocked = False
        self._suspended = False
        self._event_sequence = 0

    @property
    def dead(self) -> bool:
        return self._dead

    @property
    def blocked(self) -> bool:
        return self._blocked

    @property
    def suspended(self) -> bool:
        return self._suspended

    def _write(self, *, kind: str, data: Mapping[str, object]) -> None:
        attempt = self._scheduler.active_attempt
        attempt_ref = attempt.attempt_ref if attempt is not None else None
        event_id = deterministic_id(
            "journal-event-v1",
            "mortality-protocol",
            self._scheduler.t_monde,
            attempt_ref,
            self._event_sequence,
            kind,
        )
        self._event_sequence += 1
        self._journal.append(
            event_id=event_id,
            causal_event={
                "emitter": self.owner_id,
                "kind": kind,
                "t_monde": self._scheduler.t_monde,
                "attempt_ref": attempt_ref,
                "data": dict(data),
            },
        )

    def confirm_death(
        self, *, command: Command, transition: TransitionResult,
    ) -> None:
        """Seal an already-applied lethal world transition, exactly once."""
        if self._dead:
            raise RuntimeError("individual is already dead")
        if not transition.lethal:
            raise ValueError("death requires a lethal world transition")
        attempt = self._scheduler.active_attempt
        if attempt is None or attempt.t_monde != transition.t_monde:
            raise RuntimeError("death requires the active physical world step")
        data = {
            "command_hash": command_digest(command),
            "reasons": list(transition.lethal_reasons),
        }
        self._write(kind="death_confirmed", data=data)
        self._bench.count_lethal_transition(
            data={"t_monde": transition.t_monde, **data}
        )
        self._dead = True

    def enter_safety_block(self, *, reason: str) -> None:
        """Freeze an unexecuted step if no command is admissible."""
        if self._dead:
            raise RuntimeError("dead individuals cannot enter a safety block")
        if not reason:
            raise ValueError("safety block reason must not be empty")
        self._blocked = True
        self._suspended = self._config.mode == "diagnostic"
        self._write(
            kind="safety_block",
            data={"mode": self._config.mode, "reason": reason},
        )
        self._bench.count_safety_block(
            data={
                "t_monde": self._scheduler.t_monde,
                "mode": self._config.mode,
                "reason": reason,
            }
        )
        self._bench.alert_operator(
            data={"t_monde": self._scheduler.t_monde, "reason": reason}
        )

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "dead": self._dead,
            "blocked": self._blocked,
            "suspended": self._suspended,
        }

    def restore_causal_state(self, state: object) -> None:
        """Snapshot import for offline copies/tests, never an active-life retry."""
        if not isinstance(state, Mapping):
            raise ValueError("mortality protocol state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("safety protocol configuration version mismatch")
        for key in ("dead", "blocked", "suspended"):
            if not isinstance(state.get(key), bool):
                raise ValueError("invalid mortality protocol state")
        if state["dead"] and (state["blocked"] or state["suspended"]):
            raise ValueError("a terminal death is not a safety block")
        self._dead = state["dead"]
        self._blocked = state["blocked"]
        self._suspended = state["suspended"]
