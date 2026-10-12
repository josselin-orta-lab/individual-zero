"""Opt-in M-11 physical/cognitive coordinator for a *single* active process.

The world, Scheduler and cognition execute on a DETACHED candidate first.
The candidate is not observable through this owner until the canonical
journal suffix and complete registered owner state share one SQLite COMMIT.
The only publication is a pointer swap to the committed candidate.

This is a development integration gate, NOT yet a cold-start Stage10/11
recovery certification. Failures permanently poison this coordinator;
pending/uncertain identities are NEVER restored as earlier lives.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
import os
from pathlib import Path
from typing import Any, Callable

from .determinism import canonical_causal_bytes, sha256_hex
from .journal import GENESIS_HASH
from .mortal_execution import MortalStatus
from .sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from .sqlite_runtime_custody import capture_registered_current_state


def _copy_private_runtime(runtime: Any) -> Any:
    """Clone registered runtime with frozen mapping proxies shared read-only.

    `mappingproxy` is not pickleable/copyable on supported Python versions;
    frozen S_t snapshots contain recursive proxies and are immutable views.
    Sharing those proxy objects is safe because they contain frozen values,
    while every mutable runtime owner is cloned by deepcopy.
    """
    proxies: dict[int, object] = {}
    visited: set[int] = set()

    def collect(value: object) -> None:
        marker = id(value)
        if marker in visited:
            return
        visited.add(marker)
        if isinstance(value, MappingProxyType):
            proxies[marker] = value
            return
        if value is None or isinstance(value, (str, bytes, int, float, bool, complex)):
            return
        if isinstance(value, dict):
            for key, item in value.items():
                collect(key)
                collect(item)
        elif isinstance(value, (list, tuple, set, frozenset)):
            for item in value:
                collect(item)
        else:
            mod = type(value).__module__
            if not (mod.startswith("i0.") or mod.startswith("lab.")):
                return
            own = getattr(value, "__dict__", None)
            if isinstance(own, dict):
                for item in own.values():
                    collect(item)
            for base in type(value).__mro__:
                slots = getattr(base, "__slots__", ())
                if isinstance(slots, str):
                    slots = (slots,)
                for slot in slots:
                    if slot not in {"__dict__", "__weakref__"}:
                        try:
                            collect(object.__getattribute__(value, slot))
                        except AttributeError:
                            continue

    collect(runtime)
    return deepcopy(runtime, proxies)


@dataclass(frozen=True, slots=True)
class TransactionalStepReceipt:
    generation: int
    world_step: int
    status: str
    journal_count: int
    journal_head: str
    outcome: str


class M11TransactionalMortal:
    """The *single* official world owner for an opted-in mortal execution.

    The original runtime provided at birth remains private and cannot be
    published to consumers as a life. This class does not expose it.
    """

    def __init__(self, *, runtime: Any, ledger: SQLiteLifeLedger,
                 individual_id: str) -> None:
        self._runtime = runtime
        self._ledger = ledger
        self.individual_id = individual_id
        self._stopped = False

    @classmethod
    def birth(cls, *, db_path: str, runtime: Any,
              individual_id: str) -> "M11TransactionalMortal":
        if not isinstance(db_path, str) or not os.path.isabs(db_path):
            raise ValueError("M-11 requires a new absolute database path")
        if (runtime.stage3.substrate._mortal_boundary is None
                or runtime.stage3.substrate.mortal_status is not MortalStatus.ACTIVE
                or runtime.scheduler.t_monde != 0
                or runtime.journal.entries
                or runtime.stage3.substrate.bench is not None
                or runtime.stage3.substrate.evaluation_trace is not None
                or runtime.stage3.substrate._operator_frame_sink is not None
                or runtime.journal.durable_wal_enabled):
            raise ValueError("M-11 requires a fresh, standalone mortal runtime without side effects")
        state = capture_registered_current_state(runtime, individual_id=individual_id)
        ledger = SQLiteLifeLedger.birth(
            path=db_path, individual_id=individual_id, initial_state=state)
        return cls(runtime=runtime, ledger=ledger, individual_id=individual_id)

    def inspect(self) -> dict[str, object]:
        """No mutable runtime owner is ever returned to a caller."""
        receipt = self._ledger.audit()
        return {
            "individual_id": receipt.individual_id,
            "generation": receipt.generation,
            "status": receipt.status,
            "journal_count": receipt.journal_count,
            "journal_head": receipt.journal_head,
            "pending_intent": receipt.pending_intent,
            "world_step": self._runtime.scheduler.t_monde,
        }

    def close(self) -> None:
        self._stopped = True
        self._ledger.close()

    def __enter__(self) -> "M11TransactionalMortal":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def run_step(self, *,
                 test_fault: Callable[[str], None] | None = None
                 ) -> TransactionalStepReceipt:
        if self._stopped:
            raise RecoveryBlocked("transactional life is no longer dispatchable")
        base = self._ledger.audit()
        if not base.may_recover:
            raise RecoveryBlocked("terminal or uncertain current generation")
        if self._runtime.stage3.substrate.mortal_status is not MortalStatus.ACTIVE:
            raise RecoveryBlocked("current runtime has already stopped")
        old_state = capture_registered_current_state(
            self._runtime, individual_id=self.individual_id,
        )
        if (base.state_hash != sha256_hex(canonical_causal_bytes(old_state))
                or base.journal_head != self._runtime.journal.head_hash
                or base.journal_count != len(self._runtime.journal.entries)):
            self._stopped = True
            raise RecoveryBlocked("unsanctioned mutation of published world or owners")
        # Fence durable BEFORE copying, executing or publishing ANY world step.
        intent = f"m11:world:{base.generation + 1}:{base.journal_head[:16]}"
        try:
            self._ledger.begin_intent(
                expected_generation=base.generation, intent_ref=intent)
            if test_fault:
                test_fault("after_intent")
            candidate = _copy_private_runtime(self._runtime)
            # Absolute prohibition on running private frames with Oracle,
            # Bench, a duplicate WAL owner, or an operator callback.
            if (candidate.stage3.substrate.bench is not None
                    or candidate.journal.durable_wal_enabled
                    or candidate.stage3.substrate._operator_frame_sink is not None):
                raise RecoveryBlocked("unsafe external side effect in private candidate")
            if test_fault:
                test_fault("before_private_execution")
            outcome = candidate.run_step()
            if test_fault:
                test_fault("after_private_execution")
            # A live owner MUST NOT have observed the candidate's private effects.
            if capture_registered_current_state(
                self._runtime, individual_id=self.individual_id) != old_state:
                raise RecoveryBlocked("candidate mutated previously published owner")
            status = candidate.stage3.substrate.mortal_status
            lifecycle = (
                "dead" if status is MortalStatus.DEAD
                else "active" if status is MortalStatus.ACTIVE
                else "technical_halt"
            )
            if lifecycle == "technical_halt":
                raise RecoveryBlocked("uncertain private execution cannot commit")
            proposed = capture_registered_current_state(
                candidate, individual_id=self.individual_id,
                expected_owner_ids=tuple(old_state["owner_ids"]),
            )
            if proposed.get("lifecycle") != lifecycle:
                raise RecoveryBlocked("candidate lifecycle and registered image diverged")
            events = [
                event.as_dict()
                for event in candidate.journal.entries[base.journal_count:]
            ]
            if not events:
                raise RecoveryBlocked("generation missing canonical journal occurrences")
            if test_fault:
                test_fault("before_sql_commit")
            committed = self._ledger.commit_generation(
                expected_generation=base.generation,
                expected_head=base.journal_head,
                intent_ref=intent,
                current_state=proposed,
                events=events,
                status=lifecycle,
            )
            if test_fault:
                test_fault("after_sql_commit")
            # ONE official publication of every state owner after durable
            # commit. No WorldBody.apply or command replay on the old runtime.
            self._runtime = candidate
            if test_fault:
                test_fault("after_publication")
            return TransactionalStepReceipt(
                generation=committed.generation,
                world_step=candidate.scheduler.t_monde,
                status=lifecycle,
                journal_count=committed.journal_count,
                journal_head=committed.journal_head,
                outcome=outcome.execution_status,
            )
        except BaseException:
            self._stopped = True
            # Deliberately never roll back a committed effect or continue from
            # an uncertain transaction. The db is auditable after reopen.
            raise
