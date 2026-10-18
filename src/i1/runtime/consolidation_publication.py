"""Stage-10 private slow-history and scheduler-bound atomic publication boundary.

Real semantic owners must provide their own *paid* prepare_rebase implementation.
This module NEVER infers causal rules, fabricates skill success, or promotes a
Lab oracle result to individual knowledge. It protects the publication phase:
all candidates are validated before owner installation. Any failed
installation halts the mortal step without restoring earlier live states.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from i1.modules.consolidation_transaction import (
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
        self._i1_committed_refs = frozenset(
            self._current_state["consolidated_episode_refs"]
        )

    @property
    def current_version(self) -> str:
        return self._current_version

    def committed_episode_refs(self) -> frozenset[str]:
        """Read exact committed identifiers without copying private forms."""
        return self._i1_committed_refs

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
        refs = current.get("consolidated_episode_refs")
        if (type(refs) is not list
                or any(type(ref) is not str or not ref for ref in refs)
                or len(refs) != len(set(refs))):
            raise ValueError("unverified consolidated episode references")
        committed = frozenset(refs)
        # Assign only after validating the entire replacement.
        self._i1_committed_refs = committed
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
    source_history_canonical: bytes
    baseline_owner_canonical: Mapping[str, bytes]
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
        # The transaction already validates and detaches its private candidate.
        candidate = transaction.validated_candidate(
            validator=technical_validator)
        if type(candidate) is not dict:
            raise ValueError("consolidated slow history must be typed causal mapping")
        slice_ = self.postcut.freeze(cut=transaction.cut)
        # The snapshots are needed only during rebase. Retain canonical
        # bytes for precise pre-publication equality, not rollback copies.
        baseline = {}
        baseline_canonical = {}
        for name, owner in sorted(self.owners.items()):
            exported = owner.export_causal_state()
            baseline_canonical[name] = canonical_causal_bytes(exported)
            baseline[name] = deepcopy(exported)
        prepared = {}
        for name, owner in sorted(self.owners.items()):
            # Future owner adapters MUST reject journal records that cannot
            # reproduce exactly an online update from lived evidence.
            state = owner_rebasers[name](
                deepcopy(candidate), deepcopy(baseline[name]),
                tuple(slice_.for_owner(name)),
            )
            prepared[name] = _copy_causal(state)
            if (canonical_causal_bytes(owner.export_causal_state())
                    != baseline_canonical[name]):
                raise ValueError("owner preparer illegally mutated active state")
        if self.history.current_version != transaction.cut.history_version:
            raise ValueError("slow history changed during preparation")
        source_history_canonical = canonical_causal_bytes(
            self.history.export_causal_state()
        )
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
            source_history_canonical=source_history_canonical,
            baseline_owner_canonical=baseline_canonical,
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
        if canonical_causal_bytes(before_history) != prepared.source_history_canonical:
            raise ValueError("h changed before coordinated publication")
        for name, owner in self.owners.items():
            if (canonical_causal_bytes(owner.export_causal_state())
                    != prepared.baseline_owner_canonical[name]):
                raise ValueError("online owner state changed; rebuild its private rebase")

        event_id = deterministic_id(
            "stage10-history-activation-v1", prepared.consolidation_id,
            prepared.destination_version, world_step,
            self.journal.entry_count,
        )
        event_index = self.journal.entry_count
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

        # The committed history export already owns its nested state.
        # Copy only the lineage list we append to; baseline checks retain the
        # independent before_history and SlowHistory.restore still detaches.
        staged_history = dict(before_history)
        staged_history["lineage"] = list(before_history["lineage"])
        staged_history["current_version"] = prepared.destination_version
        # SlowHistory.restore_causal_state independently validates and detaches
        # this candidate before installing it as the current owned state.
        staged_history["current_state"] = prepared.candidate_history
        staged_history["lineage"].append({
            "source_version": prepared.source_version,
            "new_version": prepared.destination_version,
            "consolidation_id": transaction.id,
            "cut_index": transaction.cut.journal_index,
            "batch_digest": prepared.batch_digest,
            "candidate_digest": prepared.candidate_digest,
            "commit_index": event_index,
        })
        # Seed this throwaway validator with the genuine committed state.
        # SlowHistory requires existing consolidated_episode_refs at birth;
        # an invented empty mapping would crash before validation can start.
        # The candidate is still checked before touching any living owner.
        temp = SlowHistory(
            birth_version=prepared.source_version,
            birth_state=before_history["current_state"],
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
            # Installation of a newly published version may have mutated a
            # live owner even if the journal event was not appended. I1 may
            # never rewind such an owner. Stage10.run_step irreversibly halts
            # the mortal identity on the propagated error, while M11 also
            # refuses continuation of an uncertain private generation.
            journal_committed = (
                self.journal.entry_count != event_index
                or self.journal.head_hash != prepared.postcut_slice.end_hash
            )
            if journal_committed or not self.journal.verify():
                raise RuntimeError(
                    "irreversible consolidation journal fault after publication; "
                    "halt the individual, never restore committed active state"
                ) from error
            raise RuntimeError(
                "incomplete consolidation owner publication; "
                "halt the individual, never restore previous cognitive state"
            ) from error
        return receipt
