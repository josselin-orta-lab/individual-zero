"""Frozen *autobiographical* evidence for Stage-10 private cognitive replay.

Only the official JournalViews projection reaches the semantic replay algorithm.
The technical hash-chain/index is consulted here solely to attest that source
events and their authorized autobiographical commits predate the causal cut.
No oracle, hidden WorldBody fields, or post-cut events cross this boundary.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from i0.modules.consolidation_transaction import ConsolidationTransaction
from .journal import HashChainedJournal
from .journal_views import JournalViews, AutobiographicalPolicy
from .determinism import canonical_causal_bytes, sha256_hex


class FrozenLivedReplayEvidence:
    def __init__(
        self, *, journal: HashChainedJournal, views: JournalViews,
        transaction: ConsolidationTransaction,
        policies: Mapping[str, AutobiographicalPolicy],
    ) -> None:
        if not isinstance(journal, HashChainedJournal) or not isinstance(views, JournalViews):
            raise TypeError("real Lab custody and projection required")
        if not journal.verify():
            raise ValueError("technical journal failed hash chain validation")
        cut = transaction.cut
        cut.validate()
        entries = journal.entries
        if cut.journal_index >= len(entries):
            raise ValueError("missing causal cut")
        anchor = entries[cut.journal_index]
        if (cut.journal_hash != anchor.event_hash
                or cut.journal_event_id != anchor.event_id):
            raise ValueError("frozen cut does not match the journal")
        projection = views.autobiographical(policies=policies)
        committed_before_cut: set[str] = set()
        for record in entries[:cut.journal_index + 1]:
            if record.causal_event.get("kind") != "auto_segment_commit":
                continue
            raw = record.causal_event
            policy = policies.get(raw.get("filter_version"))
            if policy is None:
                raise ValueError("unknown autobiographical projection policy")
            policy.validate()
            for event_ref in raw.get("event_refs", ()):
                original = journal.get(event_ref)
                if (original is None or original.index > cut.journal_index
                        or not policy.allows(original)):
                    raise ValueError("unverified pre-cut autobiographical event")
                committed_before_cut.add(event_ref)
        projected: dict[str, object] = {}
        for record in projection:
            ref = record.get("event_id")
            if (type(ref) is not str or ref not in committed_before_cut):
                # Views may contain events from later sleeping steps; never
                # expose even their identifiers to the consolidation batch.
                continue
            if ref in projected:
                # Repeated public projections do not multiply causal evidence.
                if projected[ref] != record:
                    raise ValueError("same source event projected inconsistently")
                continue
            projected[ref] = deepcopy(record)
        frozen: dict[str, list[dict[str, object]]] = {}
        episodes = transaction.frozen_episodes_copy()
        seen: set[str] = set()
        for episode_ref in transaction.batch:
            event_refs = episodes[episode_ref].get("event_refs")
            if (type(event_refs) is not list or not event_refs
                    or len(set(event_refs)) != len(event_refs)):
                raise ValueError("unusable frozen autobiographical episode references")
            events = []
            for event_ref in event_refs:
                if event_ref not in committed_before_cut or event_ref not in projected:
                    raise ValueError("episode event lacks authorized lived projection")
                event = journal.get(event_ref)
                if event is None or event.index > cut.journal_index:
                    raise ValueError("episode event is after the cut")
                if event.causal_event.get("t_monde", -1) >= cut.world_step:
                    raise ValueError("episode event is not from earlier lived time")
                if event_ref in seen:
                    raise ValueError("same physical event occurs in multiple episodes")
                seen.add(event_ref)
                events.append(deepcopy(projected[event_ref]))
            frozen[episode_ref] = events
        self._episodes = frozen
        self.cut = cut
        self.batch_digest = transaction.batch_digest
        self.digest = sha256_hex(canonical_causal_bytes({
            "cut":cut.as_dict(), "batch_digest":self.batch_digest,
            "lived":self._episodes,
        }))

    def episode_projections(self) -> dict[str, list[dict[str, object]]]:
        return deepcopy(self._episodes)
