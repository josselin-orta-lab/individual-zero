"""Stage-10 private slow-history and scheduler-bound atomic publication boundary.

Real semantic owners must provide their own *paid* prepare_rebase implementation.
This module NEVER infers causal rules, fabricates skill success, or promotes a
Lab oracle result to individual knowledge. It protects the publication phase:
no owner changes until every candidate is valid, and a failed installation
restores the complete prior states before the Scheduler continues.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from i0.modules.consolidation_transaction import (
    ConsolidationCommitReceipt, ConsolidationSlot, ConsolidationTransaction,
)
from .consolidation_postcut_journal import (
    Stage10PostCutJournal, VerifiedPostCutSlice, VerifiedOnlineUpdate,
)
from .determinism import canonical_causal_bytes, deterministic_id, sha256_hex
from .journal import HashChainedJournal


def _copy_causal(data: object) -> object:
    canonical_causal_bytes(data)
    return deepcopy(data)


class CausalOwner(Protocol):
    owner_id: str
    def export_causal_state(self) -> object: ...
    def restore_causal_state(self, state: object) -> None: ...


class SlowHistory:
    """The single h owner: immutable committed lineage; never a temperament owner."""

    owner_id = "individual.slow_history"
    schema = "stage10-history-v1"

    def __init__(self, *, birth_version: str, birth_state: object) -> None:
        if type(birth_version) is not str or not birth_version:
            raise ValueError("birth slow-history version required")
        self._current_version = birth_version
        self._current_state = _copy_causal(birth_state)
        self._lineage: list[dict[str, object]] = []

    @property
    def current_version(self) -> str:
        return self._current_version

    def read_committed(self) -> object:
        return deepcopy(self._current_state)

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "current_version": self._current_version,
            "current_state": deepcopy(self._current_state),
            "lineage": deepcopy(self._lineage),
        }

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict
                or set(state) != {
                    "schema", "current_version", "current_state", "lineage",
                } or state["schema"] != self.schema
                or type(state["current_version"]) is not str
                or not state["current_version"]
                or type(state["lineage"]) is not list):
            raise ValueError("invalid committed history snapshot")
        current = _copy_causal(state["current_state"])
        seen = set()
        for row in state["lineage"]:
            if (type(row) is not dict or set(row) != {
                "source_version", "new_version", "consolidation_id",
                "cut_index", "batch_digest", "candidate_digest", "commit_index",
            } or any(type(row[k]) is not str or not row[k] for k in (
                "source_version", "new_version", "consolidation_id",
                "batch_digest", "candidate_digest",
            )) or type(row["cut_index"]) is not int
                    or type(row["commit_index"]) is not int
                    or row["commit_index"] <= row["cut_index"]
                    or row["new_version"] in seen):
                raise ValueError("invalid slow-history version lineage")
            seen.add(row["new_version"])
        if state["lineage"] and state["lineage"][-1]["new_version"] != state["current_version"]:
            raise ValueError("last published history version mismatch")
        # Assign only after validating the entire replacement.
        self._current_version = state["current_version"]
        self._current_state = current
        self._lineage = deepcopy(state["lineage"])


@dataclass(frozen=True)
class PreparedConsolidationPublication:
    consolidation_id: str
    source_version: str
    destination_version: str
    candidate_digest: str
    candidate_history: object
    batch_digest: str
    postcut_slice: VerifiedPostCutSlice
    source_history_state: object
    baseline_owner_states: Mapping[str, object]
    prepared_owner_states: Mapping[str, object]


class Stage10PublicationCoordinator:
    """Scheduler-only commit point for h and every required owner active form."""

    REQUIRED = frozenset({
        "value_needs", "metacognition_health", "perception", "causal_model",
    })

    def __init__(
        self, *, journal: HashChainedJournal,
        history: SlowHistory, slot: ConsolidationSlot,
        owners: Mapping[str, CausalOwner],
    ) -> None:
        if not isinstance(journal, HashChainedJournal):
            raise TypeError("technical journal must be real HashChainedJournal")
        if type(history) is not SlowHistory or not isinstance(slot, ConsolidationSlot):
            raise ValueError("canonical slow history and slot required")
        if set(owners) != self.REQUIRED:
            raise ValueError("every active-form causal owner must be supplied")
        if (len({id(o) for o in owners.values()}) != len(owners)
                or any(o.owner_id != key for key, o in owners.items())
                or id(history) in {id(o) for o in owners.values()}):
            raise ValueError("each causal state must have exactly one owner")
        self.journal = journal
        self.history = history
        self.slot = slot
        self.owners = dict(owners)
        self.postcut = Stage10PostCutJournal(journal=journal)

    def prepare(
        self, *,
        transaction: ConsolidationTransaction,
        technical_validator: Callable[[object], bool],
        owner_rebasers: Mapping[
            str, Callable[[object, object, tuple[VerifiedOnlineUpdate, ...]], object]
        ],
    ) -> PreparedConsolidationPublication:
        if (self.slot.current is not transaction
                or transaction.status != "active"
                or self.history.current_version != transaction.cut.history_version
                or set(owner_rebasers) != self.REQUIRED):
            raise ValueError("transaction, history source or owner rebasers mismatch")
        candidate = _copy_causal(transaction.validated_candidate(
            validator=technical_validator))
        if type(candidate) is not dict:
            raise ValueError("consolidated slow history must be typed causal mapping")
        slice_ = self.postcut.freeze(cut=transaction.cut)
        baseline = {
            name: _copy_causal(owner.export_causal_state())
            for name, owner in sorted(self.owners.items())
        }
        prepared = {}
        for name, owner in sorted(self.owners.items()):
            # Future owner adapters MUST reject journal records that cannot
            # reproduce exactly an online update from lived evidence.
            state = owner_rebasers[name](
                deepcopy(candidate), deepcopy(baseline[name]),
                tuple(slice_.for_owner(name)),
            )
            prepared[name] = _copy_causal(state)
            if canonical_causal_bytes(owner.export_causal_state()) != canonical_causal_bytes(baseline[name]):
                raise ValueError("owner preparer illegally mutated active state")
        if self.history.current_version != transaction.cut.history_version:
            raise ValueError("slow history changed during preparation")
        previous_history = self.history.export_causal_state()
        version = "h:" + sha256_hex(canonical_causal_bytes({
            "source": transaction.cut.history_version,
            "id": transaction.id, "candidate": transaction.candidate_digest,
            "postcut": slice_.digest,
        }))[:32]
        if version == self.history.current_version:
            raise ValueError("candidate version collides with source")
        return PreparedConsolidationPublication(
            consolidation_id=transaction.id,
            source_version=transaction.cut.history_version,
            destination_version=version,
            candidate_digest=transaction.candidate_digest,
            candidate_history=candidate,
            batch_digest=transaction.batch_digest,
            postcut_slice=slice_,
            source_history_state=previous_history,
            baseline_owner_states=baseline,
            prepared_owner_states=prepared,
        )

    def publish(
        self, *,
        prepared: PreparedConsolidationPublication,
        transaction: ConsolidationTransaction,
        world_step: int,
        scheduler_sync_authorized: bool,
    ) -> ConsolidationCommitReceipt:
        """One non-interleavable scheduler synchronization point.

        Caller must ensure no cognitive reader/command interleaves this call;
        merely setting sync_authorized=True is not a scheduler capability.
        """
        if (scheduler_sync_authorized is not True
                or type(world_step) is not int
                or world_step < transaction.cut.world_step
                or self.slot.current is not transaction
                or transaction.status != "active"
                or transaction.cursor != 6
                or prepared.consolidation_id != transaction.id
                or prepared.source_version != self.history.current_version
                or prepared.destination_version == self.history.current_version
                or prepared.candidate_digest != transaction.candidate_digest
                or prepared.batch_digest != transaction.batch_digest):
            raise ValueError("not an authorized completed matching consolidation")
        self.postcut.validate_no_intervening_updates(frozen=prepared.postcut_slice)
        before_history = self.history.export_causal_state()
        if canonical_causal_bytes(before_history) != canonical_causal_bytes(prepared.source_history_state):
            raise ValueError("h changed before coordinated publication")
        for name, owner in self.owners.items():
            if (canonical_causal_bytes(owner.export_causal_state())
                    != canonical_causal_bytes(prepared.baseline_owner_states[name])):
                raise ValueError("online owner state changed; rebuild its private rebase")

        event_id = deterministic_id(
            "stage10-history-activation-v1", prepared.consolidation_id,
            prepared.destination_version, world_step,
            len(self.journal.entries),
        )
        event_index = len(self.journal.entries)
        receipt = ConsolidationCommitReceipt(
            consolidation_id=transaction.id,
            source_history_version=prepared.source_version,
            new_history_version=prepared.destination_version,
            candidate_digest=prepared.candidate_digest,
            journal_commit_index=event_index,
            journal_commit_event_id=event_id,
        )
        receipt.validate()
        if receipt.journal_commit_index <= transaction.cut.journal_index:
            raise ValueError("version activation must follow causal cut")

        staged_history = deepcopy(before_history)
        staged_history["current_version"] = prepared.destination_version
        staged_history["current_state"] = _copy_causal(prepared.candidate_history)
        staged_history["lineage"].append({
            "source_version": prepared.source_version,
            "new_version": prepared.destination_version,
            "consolidation_id": transaction.id,
            "cut_index": transaction.cut.journal_index,
            "batch_digest": prepared.batch_digest,
            "candidate_digest": prepared.candidate_digest,
            "commit_index": event_index,
        })
        # Validate h before applying ANY owner states.
        temp = SlowHistory(
            birth_version=prepared.source_version,
            birth_state=prepared.candidate_history,
        )
        temp.restore_causal_state(staged_history)

        # Phase-2 of technical two-phase commit. No callbacks to cognition.
        # All individual owner states are prepared above.
        try:
            for name in sorted(self.owners):
                self.owners[name].restore_causal_state(
                    deepcopy(prepared.prepared_owner_states[name]))
            self.history.restore_causal_state(staged_history)
            self.journal.append(
                event_id=event_id,
                causal_event={
                    "emitter": "scheduler",
                    "kind": "stage10_consolidation_version_activated",
                    "t_monde": world_step,
                    "data": {
                        "source_history_version": prepared.source_version,
                        "new_history_version": prepared.destination_version,
                        "consolidation_id": prepared.consolidation_id,
                        "cut": transaction.cut.as_dict(),
                        "batch": list(transaction.batch),
                        "batch_digest": prepared.batch_digest,
                        "candidate_digest": prepared.candidate_digest,
                        "postcut_journal_end_index": prepared.postcut_slice.end_index,
                        "postcut_journal_end_hash": prepared.postcut_slice.end_hash,
                        "commit_index": event_index,
                    },
                },
            )
            self.slot.acknowledge_coordinated_commit(receipt)
        except Exception as error:
            # A successful journal append is an irreversible publication
            # boundary. If acknowledgement fails AFTER the append, rolling
            # the active owners or h back would contradict the durable causal
            # journal and permit a second publication of the same life.
            #
            # A failed fsync may have left a torn WAL: a poisoned journal
            # likewise cannot authorize restoring active published forms.
            journal_committed = (
                len(self.journal.entries) != event_index
                or self.journal.head_hash != prepared.postcut_slice.end_hash
            )
            if journal_committed or not self.journal.verify():
                raise RuntimeError(
                    "irreversible consolidation journal fault after publication; "
                    "halt the individual, never restore committed active state"
                ) from error
            # Before the journal event exists, all states were private and
            # the scheduler has not exposed an activation; safe to discard.
            self.history.restore_causal_state(before_history)
            for name in sorted(self.owners):
                self.owners[name].restore_causal_state(
                    deepcopy(prepared.baseline_owner_states[name]))
            raise
        return receipt
