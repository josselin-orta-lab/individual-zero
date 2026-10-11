"""Lab-only post-cutpoint journal custody for Stage-10 private owner rebases.

This boundary verifies the *real* append-only HashChainedJournal, not a
caller-supplied reconstructed event list. It does NOT use WorldBody/oracle,
publish owner states or treat a diagnostic as a learning event. Published
events may still lack the full feature/verification data needed for exact
semantic rebase: each owner MUST validate its own replay sufficiency.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping

from i0.modules.consolidation_transaction import ConsolidationCut
from .determinism import canonical_causal_bytes, sha256_hex
from .journal import HashChainedJournal

# Concrete existing runtime event types, not speculative semantic evidence.
_OWNER_EVENTS = {
    "value_needs": frozenset({"td_update_published"}),
    "metacognition_health": frozenset({"kappa_update_published"}),
    "perception": frozenset({"perceptual_precision_update_published"}),
    "causal_model": frozenset({
        "causal_inference_status_published",
        "causal_safety_status_published",
        "causal_prediction_corrections_published",
    }),
}
# The existing Stage-8/9 runtime publishes kappa and causal updates via
# Stage4Runtime._write, whose *technical* emitter is "stage4-runtime".
# The causal owner is not the journal emitter. Never silently drop them.
_RUNTIME_OWNER_EVENTS = {
    ("stage4-runtime", "kappa_update_published"): "metacognition_health",
    ("stage4-runtime", "causal_inference_status_published"): "causal_model",
    ("stage4-runtime", "causal_safety_status_published"): "causal_model",
    ("stage4-runtime", "causal_prediction_corrections_published"): "causal_model",
}
# Stage8 publishes precision directly with these fields at the event root,
# unlike every other online update, which carries a nested "data" object.
_PRECISION_ROOT_FIELDS = (
    "source", "verification_ref", "before", "after", "precision_version",
)


@dataclass(frozen=True)
class VerifiedOnlineUpdate:
    owner_id: str
    journal_index: int
    event_id: str
    event_hash: str
    t_monde: int
    kind: str
    payload: object

    def detached_payload(self) -> object:
        return deepcopy(self.payload)


@dataclass(frozen=True)
class VerifiedPostCutSlice:
    """An exact journal prefix cursor for a scheduler-owned sync boundary."""

    cut: ConsolidationCut
    end_index: int
    end_hash: str
    updates: tuple[VerifiedOnlineUpdate, ...]
    digest: str

    def for_owner(self, owner_id: str) -> tuple[VerifiedOnlineUpdate, ...]:
        if owner_id not in _OWNER_EVENTS:
            raise ValueError("unknown Stage-10 rebase owner")
        return tuple(
            item for item in self.updates if item.owner_id == owner_id
        )


class Stage10PostCutJournal:
    """Technical integrity wrapper; never a cognitive owner or direct source."""

    def __init__(self, *, journal: HashChainedJournal) -> None:
        if not isinstance(journal, HashChainedJournal):
            raise TypeError("actual HashChainedJournal is required")
        self._journal = journal

    def _verified(self) -> tuple:
        if not self._journal.verify():
            raise ValueError("hash-chained journal integrity failure")
        return self._journal.entries

    def _check_cut(self, cut: ConsolidationCut, entries: tuple) -> None:
        cut.validate()
        if cut.journal_index >= len(entries):
            raise ValueError("cut journal occurrence is absent")
        original = entries[cut.journal_index]
        if (original.event_id != cut.journal_event_id
                or original.event_hash != cut.journal_hash):
            raise ValueError("cut identity or head hash mismatches journal")
        cut_step = original.causal_event.get("t_monde")
        if (type(cut_step) is not int
                or cut_step > cut.world_step
                or cut_step < 1):
            raise ValueError("causal cut cannot refer to a future/invalid event")

    def freeze(self, *, cut: ConsolidationCut) -> VerifiedPostCutSlice:
        entries = self._verified()
        self._check_cut(cut, entries)
        end_index = len(entries) - 1
        end_hash = entries[-1].event_hash
        items: list[VerifiedOnlineUpdate] = []
        for event in entries[cut.journal_index + 1:]:
            record = event.causal_event
            emitter, kind = record.get("emitter"), record.get("kind")
            owner = _RUNTIME_OWNER_EVENTS.get((emitter, kind))
            if owner is None:
                owner = (emitter if emitter in _OWNER_EVENTS
                         and kind in _OWNER_EVENTS[emitter] else None)
            if owner is None:
                continue
            t = record.get("t_monde")
            if type(t) is not int or t < cut.world_step:
                raise ValueError("postcut published owner event predates cut")
            if kind == "perceptual_precision_update_published" and (
                emitter == "perception" and "data" not in record
            ):
                if not all(key in record for key in _PRECISION_ROOT_FIELDS):
                    raise ValueError("precision publication missing mandatory root fields")
                payload = {key: record[key] for key in _PRECISION_ROOT_FIELDS}
            else:
                payload = record.get("data")
            if not isinstance(payload, Mapping):
                raise ValueError("published online owner event needs typed data")
            items.append(VerifiedOnlineUpdate(
                owner_id=owner, journal_index=event.index,
                event_id=event.event_id, event_hash=event.event_hash,
                t_monde=t, kind=kind, payload=deepcopy(dict(payload)),
            ))
        digest = sha256_hex(canonical_causal_bytes({
            "cut": cut.as_dict(), "end_index": end_index,
            "end_hash": end_hash,
            "updates": [{
                "owner": row.owner_id, "index": row.journal_index,
                "event_id": row.event_id, "hash": row.event_hash,
                "t_monde": row.t_monde, "kind": row.kind,
                "data": row.payload,
            } for row in items],
        }))
        return VerifiedPostCutSlice(
            cut=cut, end_index=end_index, end_hash=end_hash,
            updates=tuple(items), digest=digest,
        )

    def validate_no_intervening_updates(
        self, *, frozen: VerifiedPostCutSlice,
    ) -> None:
        """Reject stale plans rather than silently discarding recent learning.

        A final scheduler-synchronization point must refreeze and rebuild
        private rebases whenever the head moved, even for technical events:
        conservative fail-closed logic avoids provenance ambiguity.
        """
        entries = self._verified()
        self._check_cut(frozen.cut, entries)
        if (len(entries) - 1 != frozen.end_index
                or self._journal.head_hash != frozen.end_hash):
            raise ValueError("journal advanced after private rebase preparation")
        current = self.freeze(cut=frozen.cut)
        if current.digest != frozen.digest:
            raise ValueError("postcut slice was modified")
