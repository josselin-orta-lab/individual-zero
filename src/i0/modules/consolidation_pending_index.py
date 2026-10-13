"""Opt-in, causal P-42-priced index of still-unconsolidated Memory episodes.

This index NEVER replaces Memory or the exhaustive journal. Every newly
discovered autobiographical projection and every later priority inspection
is priced by episode_scan before access; removing published IDs is priced
by index_maintenance before the atomic h publication. Only monotonic count
metadata is consulted before a debit. The index is a checkpointed causal
owner, not an external oracle or an unpriced technical cache.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from itertools import islice
from typing import Callable, Mapping, Sequence

from .consolidation_batch import ConsolidationBatchSelector
from .consolidation_transaction import ConsolidationCut
from lab.determinism import canonical_causal_bytes


@dataclass(frozen=True, slots=True)
class _IndexedEpisode:
    payload: dict

    def as_dict(self):
        return deepcopy(self.payload)


class ChargedPendingEpisodeIndex:
    owner_id = "consolidation_selection_scan"
    schema = "stage10-priced-pending-episode-index-v1"

    def __init__(self, *, policy_version: str):
        if type(policy_version) is not str or not policy_version:
            raise ValueError("explicit versioned selection policy required")
        self.policy_version = policy_version
        self._history_version: str | None = None
        self._seen_count = 0
        self._pending: dict[str, dict] = {}
        self._cut: ConsolidationCut | None = None
        self._target = 0
        self._seen_on_begin = 0
        self._pending_on_begin = 0
        self._rank_cursor = 0
        self._ranked: list[dict] = []

    @property
    def active(self) -> bool:
        return self._cut is not None

    @property
    def complete(self) -> bool:
        return (self.active and self._seen_count == self._target
                and self._rank_cursor == len(self._pending))

    @property
    def cut(self):
        return self._cut

    @property
    def seen_count(self) -> int:
        return self._seen_count

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def cursor(self) -> int:
        return self._seen_count - self._seen_on_begin + self._rank_cursor if self.active else 0

    @property
    def total(self) -> int:
        # Every new episode is paid once to discover and once to re-rank.
        return (self._pending_on_begin + 2 * (self._target - self._seen_on_begin)
                if self.active else 0)

    def begin(self, *, cut: ConsolidationCut, total: int,
              already_consolidated: tuple[str, ...] = ()) -> None:
        cut.validate()
        if (self.active or type(total) is not int or total < self._seen_count
                or already_consolidated != ()):
            raise ValueError("invalid index selection start or unpriced consolidated ledger")
        if self._history_version is not None and cut.history_version != self._history_version:
            raise ValueError("index and committed h versions diverged")
        if self._history_version is None:
            self._history_version = cut.history_version
        self._cut, self._target = cut, total
        self._seen_on_begin = self._seen_count
        self._pending_on_begin = len(self._pending)
        self._rank_cursor, self._ranked = 0, []

    @staticmethod
    def _available(budget, operation):
        cost = budget.config.operation_costs.get(operation)
        if type(cost) is not int or cost < 1:
            raise ValueError("P-42 operation price absent")
        if budget.open_world_step is None:
            raise ValueError("paid selection requires physical sleep slot")
        free = min(
            budget.config.step_slot_uc - budget.consumed_step_uc,
            budget.config.period_capacity_uc - budget.consumed_period_uc,
        )
        return max(0, free // cost)

    def advance(self, *, budget, episode_count: int,
                read_paid_slice: Callable[[int, int], Sequence],
                selector: ConsolidationBatchSelector) -> int:
        if not self.active or self.complete:
            raise ValueError("no incomplete pending-index selection")
        if (selector.policy.version != self.policy_version
                or budget.config.operation_costs.get("episode_scan")
                != selector.policy.scan_uc_per_episode):
            raise ValueError("versioned selector or scan charge mismatch")
        if (type(episode_count) is not int or episode_count < self._target
                or not callable(read_paid_slice)):
            raise ValueError("Memory lost episodes or has no bounded paid reader")

        if self._seen_count < self._target:
            count = min(self._target - self._seen_count,
                        self._available(budget, "episode_scan"))
            if not count:
                return 0
            debit = budget.charge(operation="episode_scan", count=count)
            if not debit.accepted:
                raise RuntimeError("quoted discovery charge was refused")
            paid = read_paid_slice(self._seen_count, self._seen_count + count)
            if len(paid) != count:
                raise ValueError("paid index read must return an exact slice")
            staged = [selector._projection(ep) for ep in paid]
            refs = [p["id"] for p in staged]
            if (len(set(refs)) != len(refs)
                    or any(x in self._pending for x in refs)
                    or any(type(p["end_t_monde"]) is not int
                           or p["end_t_monde"] >= self._cut.world_step
                           for p in staged)):
                raise ValueError("late or duplicate episode at frozen causal cut")
            for payload in staged:
                self._pending[payload["id"]] = payload
            self._seen_count += count
            return count

        count = min(len(self._pending) - self._rank_cursor,
                    self._available(budget, "episode_scan"))
        if not count:
            return 0
        debit = budget.charge(operation="episode_scan", count=count)
        if not debit.accepted:
            raise RuntimeError("quoted candidate rank charge was refused")
        # Inspection of these owned projections starts only AFTER P-42 debit.
        inspected = list(islice(
            self._pending.values(), self._rank_cursor, self._rank_cursor + count))
        if len(inspected) != count:
            raise RuntimeError("index changed during frozen paid selection")
        self._ranked.extend(deepcopy(inspected))
        self._rank_cursor += count
        return count

    def finalize(self, *, selector: ConsolidationBatchSelector):
        if not self.complete or selector.policy.version != self.policy_version:
            raise ValueError("cannot select an incompletely paid frozen index")
        projections = tuple(_IndexedEpisode(p) for p in self._ranked)
        ids = tuple(p["id"] for p in self._ranked)
        selected = selector.select(
            cut=self._cut, episodes=projections,
            pending_episode_refs=ids,
            reserved_scan_uc=selector.quote_scan_uc(
                examined_episode_count=len(projections)),
        )
        self._cut = None
        self._target = self._seen_on_begin = self._pending_on_begin = 0
        self._rank_cursor, self._ranked = 0, []
        return selected

    def charge_committed_removal(self, *, budget, refs: tuple[str, ...]):
        if self.active or not refs or len(set(refs)) != len(refs):
            raise ValueError("only completed unique batches can be retired")
        # No index read or mutation is performed until an accepted debit.
        debit = budget.charge(operation="index_maintenance", count=len(refs))
        if not debit.accepted:
            return None
        # Check ledger membership only AFTER payment, but still BEFORE the
        # irreversible h commit. A corrupt index must never be acknowledged
        # after an activation whose source refs cannot be retired.
        if any(type(ref) is not str or ref not in self._pending for ref in refs):
            raise ValueError("paid index maintenance references unknown episodes")
        return debit

    def acknowledge_published(self, *, refs: tuple[str, ...],
                              charged, source_version: str,
                              new_version: str) -> None:
        if (self.active or self._history_version != source_version
                or type(new_version) is not str or not new_version
                or new_version == source_version
                or charged is None or not charged.accepted
                or charged.operation != "index_maintenance"
                or charged.count != len(refs)):
            raise ValueError("unpriced or incompatible h/index publication")
        if len(set(refs)) != len(refs) or any(ref not in self._pending for ref in refs):
            raise ValueError("h published unknown or already retired episode")
        for ref in refs:
            del self._pending[ref]
        self._history_version = new_version

    def export_causal_state(self) -> dict[str, object]:
        return deepcopy({
            "schema": self.schema, "policy_version": self.policy_version,
            "history_version": self._history_version,
            "seen_count": self._seen_count,
            "pending": list(self._pending.values()),
            "cut": None if self._cut is None else self._cut.as_dict(),
            "target": self._target,
            "seen_on_begin": self._seen_on_begin,
            "pending_on_begin": self._pending_on_begin,
            "rank_cursor": self._rank_cursor,
            "ranked": self._ranked,
        })

    def restore_causal_state(self, raw: object) -> None:
        if (not isinstance(raw, Mapping) or set(raw) != {
                "schema", "policy_version", "history_version", "seen_count",
                "pending", "cut", "target", "seen_on_begin", "pending_on_begin",
                "rank_cursor", "ranked"
            } or raw["schema"] != self.schema
                or raw["policy_version"] != self.policy_version):
            raise ValueError("incompatible pending-index causal snapshot")
        seen, target = raw["seen_count"], raw["target"]
        before, old_pending = raw["seen_on_begin"], raw["pending_on_begin"]
        rank = raw["rank_cursor"]
        history = raw["history_version"]
        pending, ranked = raw["pending"], raw["ranked"]
        if (any(type(x) is not int or x < 0 for x in
                (seen, target, before, old_pending, rank))
                or type(history) not in (str, type(None))
                or history == "" or type(pending) is not list
                or type(ranked) is not list or len(pending) > seen):
            raise ValueError("invalid pending-index snapshot counters")
        check = {}
        for p in pending:
            checked = ConsolidationBatchSelector._projection(_IndexedEpisode(p))
            if checked["id"] in check:
                raise ValueError("duplicate pending index id")
            check[checked["id"]] = checked
        inspected = []
        for p in ranked:
            checked = ConsolidationBatchSelector._projection(_IndexedEpisode(p))
            inspected.append(checked)
        if raw["cut"] is None:
            if target or before or old_pending or rank or inspected:
                raise ValueError("closed pending index contains open selection")
            cut = None
        else:
            obj = raw["cut"]
            if type(obj) is not dict or set(obj) != {
                    "world_step", "journal_index", "journal_event_id",
                    "journal_hash", "history_version"}:
                raise ValueError("invalid indexed causal cut")
            cut = ConsolidationCut(**obj)
            cut.validate()
            if (history != cut.history_version or not before <= seen <= target
                    or old_pending > before
                    or len(pending) != old_pending + seen - before
                    or rank > len(pending) or len(inspected) != rank
                    or inspected != list(islice(check.values(), 0, rank))
                    or any(p["end_t_monde"] >= cut.world_step for p in inspected)):
                raise ValueError("incomplete or changed paid pending-index snapshot")
        if history is None and (seen or pending or cut is not None):
            raise ValueError("unversioned pending index cannot hold episodes")
        # No owner field changes before all structural checks pass.
        self._history_version, self._seen_count = history, seen
        self._pending = check
        self._cut, self._target = cut, target
        self._seen_on_begin, self._pending_on_begin = before, old_pending
        self._rank_cursor, self._ranked = rank, inspected
