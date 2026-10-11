"""Standalone mortal technical safety block, without Oracle or Bench.

The technical rollback mask does not exist for a mortal individual.
All events are written to the same complete internal causal journal.
"""
from __future__ import annotations

from typing import Mapping

from .determinism import deterministic_id
from .journal import HashChainedJournal
from .scheduler import Scheduler


class StandaloneSafetyOwner:
    owner_id = "scheduler.safety_protocol"

    def __init__(
        self, *, config_version: str,
        scheduler: Scheduler, journal: HashChainedJournal,
    ) -> None:
        if not isinstance(config_version, str) or not config_version:
            raise ValueError("standalone safety config_version is required")
        self._config = type("_StandaloneConfig", (), {"version": config_version})()
        self._scheduler = scheduler
        self._journal = journal
        self._blocked = False

    @property
    def blocked(self) -> bool:
        return self._blocked

    @property
    def suspended(self) -> bool:
        return False

    def is_masked(self, command: object) -> bool:
        """Rollback masks never restrict a mortal individual's action."""
        return False

    def enter_safety_block(self, *, reason: str) -> None:
        if self._blocked:
            raise RuntimeError("individual is already safety-blocked")
        if not isinstance(reason, str) or not reason:
            raise ValueError("safety block reason is required")
        attempt = self._scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("safety block requires an open world step")
        self._journal.append(
            event_id=deterministic_id(
                "journal-event-v1", "standalone-safety",
                attempt.attempt_ref, "blocked",
            ),
            causal_event={
                "emitter": self.owner_id,
                "kind": "safety_block",
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "reason": reason,
            },
        )
        self._blocked = True

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "mode": "standalone_mortal",
            "blocked": self._blocked,
        }

    def restore_causal_state(self, state: object) -> None:
        """Only identical state attestations; no life-state rewind."""
        if not isinstance(state, Mapping) or dict(state) != self.export_causal_state():
            raise ValueError("standalone safety cannot rewind its state")
