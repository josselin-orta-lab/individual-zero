"""Generic complete-causal-state snapshot infrastructure.

The snapshot manager never mutates another component's internals directly.
Each state owner exports and restores only its own causal state.

Spec: 5.3, 17.6-17.8, DC-08, INV-01, INV-33, INV-44.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol, Sequence, runtime_checkable

from .determinism import canonical_causal_bytes, deterministic_id, sha256_hex
from .journal import HashChainedJournal


class SnapshotType(str, Enum):
    BIRTH = "birth"
    PERIODIC = "periodic"
    LETHAL_CHECKPOINT = "lethal_checkpoint"
    COPY = "copy"


@runtime_checkable
class CausalStateOwner(Protocol):
    @property
    def owner_id(self) -> str:
        """Stable owner identifier."""

    def export_causal_state(self) -> object:
        """Return a complete serializable copy of state owned by this component."""

    def restore_causal_state(self, state: object) -> None:
        """Restore only state owned by this component."""


@dataclass(frozen=True, slots=True)
class SnapshotRecord:
    id: str
    type: SnapshotType
    individual_id: str
    t_monde: int
    cycle: int
    attempt_ref: str | None
    owner_ids: tuple[str, ...]
    scenario_included: bool
    sha256: str


@dataclass(slots=True)
class _StoredSnapshot:
    record: SnapshotRecord
    payload: dict[str, object]


class SnapshotManager:
    """Owns life snapshots while leaving causal state ownership unchanged."""

    def __init__(self, *, journal: HashChainedJournal) -> None:
        self._journal = journal
        self._snapshots: dict[str, _StoredSnapshot] = {}
        self._journal_sequence = 0

    def _write_journal(
        self,
        *,
        kind: str,
        record: SnapshotRecord,
    ) -> None:
        event_id = deterministic_id(
            "journal-event-v1",
            "snapshots",
            record.t_monde,
            record.cycle,
            record.attempt_ref,
            self._journal_sequence,
            kind,
            record.id,
        )
        self._journal_sequence += 1
        self._journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "snapshots",
                "kind": kind,
                "t_monde": record.t_monde,
                "cycle": record.cycle,
                "attempt_ref": record.attempt_ref,
                "snapshot_id": record.id,
                "snapshot_type": record.type.value,
                "snapshot_sha256": record.sha256,
            },
        )

    def take(
        self,
        *,
        snapshot_type: SnapshotType,
        individual_id: str,
        t_monde: int,
        cycle: int,
        attempt_ref: str | None,
        owners: Sequence[CausalStateOwner],
        versions: Mapping[str, object],
        scenario_state: object | None = None,
        context: Mapping[str, object] | None = None,
    ) -> SnapshotRecord:
        if not individual_id:
            raise ValueError("individual_id must not be empty")
        if t_monde < 0 or cycle < 0:
            raise ValueError("snapshot clocks must be non-negative")
        if snapshot_type is SnapshotType.LETHAL_CHECKPOINT and not attempt_ref:
            raise ValueError("lethal checkpoint requires attempt_ref")

        owner_states: dict[str, object] = {}
        for owner in owners:
            if not owner.owner_id:
                raise ValueError("state owner id must not be empty")
            if owner.owner_id in owner_states:
                raise ValueError(f"duplicate state owner: {owner.owner_id}")
            state = deepcopy(owner.export_causal_state())
            canonical_causal_bytes(state)
            owner_states[owner.owner_id] = state

        payload: dict[str, object] = {
            "type": snapshot_type.value,
            "individual_id": individual_id,
            "t_monde": t_monde,
            "cycle": cycle,
            "attempt_ref": attempt_ref,
            "owner_states": owner_states,
            "versions": dict(versions),
            "scenario_state": deepcopy(scenario_state),
            "context": dict(context or {}),
        }
        fingerprint = sha256_hex(canonical_causal_bytes(payload))
        snapshot_id = deterministic_id(
            "snapshot-v1",
            snapshot_type.value,
            individual_id,
            t_monde,
            cycle,
            attempt_ref,
            fingerprint,
        )
        record = SnapshotRecord(
            id=snapshot_id,
            type=snapshot_type,
            individual_id=individual_id,
            t_monde=t_monde,
            cycle=cycle,
            attempt_ref=attempt_ref,
            owner_ids=tuple(sorted(owner_states)),
            scenario_included=scenario_state is not None,
            sha256=fingerprint,
        )
        self._snapshots[snapshot_id] = _StoredSnapshot(
            record=record,
            payload=deepcopy(payload),
        )
        self._write_journal(kind="snapshot_taken", record=record)
        return record

    def record(self, snapshot_id: str) -> SnapshotRecord:
        try:
            return self._snapshots[snapshot_id].record
        except KeyError as exc:
            raise KeyError(f"unknown snapshot: {snapshot_id}") from exc

    def verify(self, snapshot_id: str) -> bool:
        stored = self._snapshots.get(snapshot_id)
        if stored is None:
            return False
        actual = sha256_hex(canonical_causal_bytes(stored.payload))
        return actual == stored.record.sha256

    def export_payload(self, snapshot_id: str) -> dict[str, object]:
        """Return a verified deep copy of a stored causal snapshot payload.

        This is used to initialize a new copy instance. It never mutates the
        source snapshot or any owner.
        """
        stored = self._snapshots.get(snapshot_id)
        if stored is None:
            raise KeyError(f"unknown snapshot: {snapshot_id}")
        if not self.verify(snapshot_id):
            raise ValueError("snapshot hash verification failed")
        return deepcopy(stored.payload)

    def restore(
        self,
        snapshot_id: str,
        *,
        owners: Sequence[CausalStateOwner],
    ) -> SnapshotRecord:
        stored = self._snapshots.get(snapshot_id)
        if stored is None:
            raise KeyError(f"unknown snapshot: {snapshot_id}")
        if not self.verify(snapshot_id):
            raise ValueError("snapshot hash verification failed")

        owner_map: dict[str, CausalStateOwner] = {}
        for owner in owners:
            if owner.owner_id in owner_map:
                raise ValueError(f"duplicate state owner: {owner.owner_id}")
            owner_map[owner.owner_id] = owner

        stored_states = stored.payload["owner_states"]
        if not isinstance(stored_states, dict):
            raise ValueError("stored snapshot owner state is malformed")

        if set(owner_map) != set(stored_states):
            missing = sorted(set(stored_states) - set(owner_map))
            extra = sorted(set(owner_map) - set(stored_states))
            raise ValueError(
                f"snapshot owner mismatch; missing={missing}, extra={extra}"
            )

        # A verified snapshot may still be incompatible with a *current*
        # owner's schema. All causal owners must be recovered together if a
        # later restore fails, including a failing owner that mutated before
        # raising. The technical journal is never rolled back (DC-08).
        owner_ids = tuple(sorted(stored_states))
        recovery: dict[str, object] = {}
        for owner_id in owner_ids:
            prior = deepcopy(owner_map[owner_id].export_causal_state())
            canonical_causal_bytes(prior)
            recovery[owner_id] = prior

        try:
            for owner_id in owner_ids:
                owner_map[owner_id].restore_causal_state(
                    deepcopy(stored_states[owner_id])
                )
        except Exception as original_error:
            failed_rollback = []
            for owner_id in reversed(owner_ids):
                try:
                    owner_map[owner_id].restore_causal_state(
                        deepcopy(recovery[owner_id])
                    )
                except Exception:
                    failed_rollback.append(owner_id)
            if failed_rollback:
                raise RuntimeError(
                    "snapshot restore failed and causal-owner rollback "
                    f"is incomplete: {sorted(failed_rollback)}"
                ) from original_error
            raise

        self._write_journal(kind="snapshot_restored", record=stored.record)
        return stored.record
