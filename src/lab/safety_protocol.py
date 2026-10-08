"""Technical lethal-rollback protocol for normative Stage 2.

The protocol mask and consecutive-lethal counter are technical Scheduler state.
They are not knowledge and are never exposed through the autobiographical view.

Spec: 18.3-18.6, DC-08, DC-14, INV-27-29, INV-44, INV-49.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .bench import EvaluationBench
from .determinism import deterministic_id
from .journal import HashChainedJournal
from .scheduler import Scheduler
from .snapshots import CausalStateOwner, SnapshotManager
from .world import Command, TransitionResult, command_digest


@dataclass(frozen=True, slots=True)
class SafetyProtocolConfig:
    version: str
    lethal_max: int
    mode: str  # campaign | diagnostic

    def validate(self) -> None:
        if not self.version:
            raise ValueError("safety protocol version must not be empty")
        if self.lethal_max < 1:
            raise ValueError("R_letal_max must be >= 1")
        if self.mode not in {"campaign", "diagnostic"}:
            raise ValueError("safety protocol mode must be campaign or diagnostic")


@dataclass(frozen=True, slots=True)
class LethalHandlingResult:
    blocked: bool
    resumed: bool
    attempt_ref: str | None
    consecutive_lethal: int


class LethalSafetyProtocol:
    """Owns rollback mask/counter without turning death into cognition."""

    owner_id = "scheduler.safety_protocol"

    def __init__(
        self,
        *,
        config: SafetyProtocolConfig,
        scheduler: Scheduler,
        snapshots: SnapshotManager,
        journal: HashChainedJournal,
        bench: EvaluationBench,
    ) -> None:
        config.validate()
        self._config = config
        self._scheduler = scheduler
        self._snapshots = snapshots
        self._journal = journal
        self._bench = bench
        self._masked_command_hashes: set[str] = set()
        self._consecutive_lethal = 0
        self._blocked = False
        self._suspended = False
        self._event_sequence = 0

    @property
    def consecutive_lethal(self) -> int:
        return self._consecutive_lethal

    @property
    def blocked(self) -> bool:
        return self._blocked

    @property
    def suspended(self) -> bool:
        return self._suspended

    def is_masked(self, command: Command) -> bool:
        return command_digest(command) in self._masked_command_hashes

    def _write(self, *, kind: str, data: Mapping[str, object]) -> None:
        attempt = self._scheduler.active_attempt
        attempt_ref = attempt.attempt_ref if attempt is not None else None
        event_id = deterministic_id(
            "journal-event-v1",
            "safety-protocol",
            self._scheduler.t_monde,
            attempt_ref,
            self._event_sequence,
            kind,
        )
        self._event_sequence += 1
        self._journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "scheduler.safety_protocol",
                "kind": kind,
                "t_monde": self._scheduler.t_monde,
                "attempt_ref": attempt_ref,
                "data": dict(data),
            },
        )

    def handle_lethal(
        self,
        *,
        checkpoint_id: str,
        command: Command,
        transition: TransitionResult,
        restore_owners: Sequence[CausalStateOwner],
    ) -> LethalHandlingResult:
        if not transition.lethal:
            raise ValueError("handle_lethal requires a lethal transition")

        command_hash = command_digest(command)
        self._write(
            kind="lethal_transition_detected",
            data={
                "command_hash": command_hash,
                "reasons": list(transition.lethal_reasons),
            },
        )
        self._bench.count_lethal_transition(
            data={
                "t_monde": transition.t_monde,
                "command_hash": command_hash,
                "reasons": list(transition.lethal_reasons),
            }
        )

        self._snapshots.restore(
            checkpoint_id,
            owners=restore_owners,
        )
        self._bench.count_lethal_rollback(
            data={
                "t_monde": transition.t_monde,
                "checkpoint_id": checkpoint_id,
            }
        )

        self._consecutive_lethal += 1
        self._masked_command_hashes.add(command_hash)
        self._write(
            kind="lethal_rollback_completed",
            data={
                "checkpoint_id": checkpoint_id,
                "command_hash": command_hash,
                "R_letal_consecutif": self._consecutive_lethal,
            },
        )

        if self._consecutive_lethal > self._config.lethal_max:
            self._blocked = True
            self._suspended = self._config.mode == "diagnostic"
            self._write(
                kind="safety_block",
                data={
                    "mode": self._config.mode,
                    "R_letal_consecutif": self._consecutive_lethal,
                },
            )
            self._bench.count_safety_block(
                data={
                    "t_monde": transition.t_monde,
                    "mode": self._config.mode,
                    "R_letal_consecutif": self._consecutive_lethal,
                }
            )
            self._bench.alert_operator(
                data={
                    "t_monde": transition.t_monde,
                    "reason": "R_letal_max_exceeded",
                }
            )
            return LethalHandlingResult(
                blocked=True,
                resumed=False,
                attempt_ref=None,
                consecutive_lethal=self._consecutive_lethal,
            )

        attempt = self._scheduler.new_attempt_after_rollback()
        return LethalHandlingResult(
            blocked=False,
            resumed=True,
            attempt_ref=attempt.attempt_ref,
            consecutive_lethal=self._consecutive_lethal,
        )

    def complete_nonlethal_step(self) -> None:
        self._masked_command_hashes.clear()
        self._consecutive_lethal = 0
        self._blocked = False
        self._suspended = False

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "masked_command_hashes": sorted(self._masked_command_hashes),
            "consecutive_lethal": self._consecutive_lethal,
            "blocked": self._blocked,
            "suspended": self._suspended,
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("safety protocol state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("safety protocol configuration version mismatch")
        hashes = state.get("masked_command_hashes")
        count = state.get("consecutive_lethal")
        blocked = state.get("blocked")
        suspended = state.get("suspended")
        if not isinstance(hashes, list) or not all(isinstance(x, str) for x in hashes):
            raise ValueError("invalid protocol mask state")
        if not isinstance(count, int) or count < 0:
            raise ValueError("invalid consecutive lethal counter")
        if not isinstance(blocked, bool) or not isinstance(suspended, bool):
            raise ValueError("invalid safety block state")
        self._masked_command_hashes = set(hashes)
        self._consecutive_lethal = count
        self._blocked = blocked
        self._suspended = suspended
