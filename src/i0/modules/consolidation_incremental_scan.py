"""Durable, strictly P-42-priced incremental selection over a fixed causal cut.

The scan consumes one bounded slice of immutable autobiographical episodes
per sleeping step; neither scores nor source payloads are read before charge.
No partially scanned batch can be published or used as a semantic transaction.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from lab.determinism import canonical_causal_bytes, sha256_hex
from .consolidation_batch import ConsolidationBatchSelector
from .consolidation_transaction import ConsolidationCut


@dataclass(frozen=True, slots=True)
class _FrozenEpisode:
    data: dict

    def as_dict(self):
        return deepcopy(self.data)


class IncrementalChargedSelection:
    """Independent causal owner, resumable across actual sleep periods.

    A scan fixes the number of pre-cut episodes. Newly closed episodes cannot
    enter its candidate list, even when scanning takes multiple waking cycles.
    """

    owner_id = "consolidation_selection_scan"
    schema = "stage10-consolidation-incremental-selection-v1"

    def __init__(self, *, policy_version: str):
        if not isinstance(policy_version, str) or not policy_version:
            raise ValueError("explicit scan policy version required")
        self.policy_version = policy_version
        self._cut = None
        self._total = 0
        self._offset = 0
        self._committed = ()
        self._payloads = []

    @property
    def active(self) -> bool:
        return self._cut is not None

    @property
    def complete(self) -> bool:
        return self.active and self._offset == self._total

    @property
    def cursor(self) -> int:
        return self._offset

    @property
    def total(self) -> int:
        return self._total

    @property
    def cut(self):
        return self._cut

    def begin(self, *, cut: ConsolidationCut, total: int,
              already_consolidated: tuple[str, ...]) -> None:
        cut.validate()
        if self.active or type(total) is not int or total < 1:
            raise ValueError("invalid overlapping or empty scan")
        if (type(already_consolidated) is not tuple
                or any(type(x) is not str or not x for x in already_consolidated)
                or len(set(already_consolidated)) != len(already_consolidated)):
            raise ValueError("invalid consolidated ledger")
        self._cut = cut
        self._total = total
        self._offset = 0
        self._committed = tuple(sorted(already_consolidated))
        self._payloads = []

    def advance(self, *, budget, episode_count: int,
                read_paid_slice: Callable[[int, int], Sequence],
                selector: ConsolidationBatchSelector):
        """Charge a bounded *entire* slice before inspecting its contents."""
        if not self.active or self.complete:
            raise ValueError("no incomplete scan")
        if selector.policy.version != self.policy_version:
            raise ValueError("changed selection policy")
        if (type(episode_count) is not int or episode_count < self._total
                or not callable(read_paid_slice)):
            raise ValueError("Memory lost episodes or invalid paid scan reader")
        cost = selector.policy.scan_uc_per_episode
        if budget.config.operation_costs.get("episode_scan") != cost:
            raise ValueError("selection scan price mismatch")
        free_step = budget.config.step_slot_uc - budget.consumed_step_uc
        free_period = budget.config.period_capacity_uc - budget.consumed_period_uc
        count = min(self._total - self._offset, free_step // cost, free_period // cost)
        if count <= 0:
            return 0
        receipt = budget.charge(operation="episode_scan", count=count)
        if not receipt.accepted or receipt.requested_uc != count * cost:
            raise RuntimeError("quoted incremental scan was not paid")
        # Read payloads only after a successful debit.
        paid = read_paid_slice(self._offset, self._offset + count)
        if len(paid) != count:
            raise ValueError("paid episode reader returned an incomplete slice")
        staged = [selector._projection(episode) for episode in paid]
        known = {p["id"] for p in self._payloads}
        if len({p["id"] for p in staged}) != len(staged) or any(
                p["id"] in known or p["end_t_monde"] >= self._cut.world_step
                for p in staged):
            raise ValueError("nonunique or post-cut scan material")
        self._payloads.extend(staged)
        self._offset += count
        return count

    def finalize(self, *, selector: ConsolidationBatchSelector):
        if not self.complete or selector.policy.version != self.policy_version:
            raise ValueError("cannot publish an incomplete or mismatched scan")
        committed = set(self._committed)
        pending = tuple(
            p["id"] for p in self._payloads if p["id"] not in committed
        )
        result = selector.select(
            cut=self._cut, episodes=tuple(_FrozenEpisode(deepcopy(p))
                                         for p in self._payloads),
            pending_episode_refs=pending,
            reserved_scan_uc=selector.quote_scan_uc(
                examined_episode_count=self._total),
        )
        self.clear()
        return result

    def clear(self) -> None:
        self._cut = None
        self._total = self._offset = 0
        self._committed = ()
        self._payloads = []

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema, "policy_version": self.policy_version,
            "cut": None if self._cut is None else self._cut.as_dict(),
            "total": self._total, "cursor": self._offset,
            "already_consolidated": list(self._committed),
            "paid_payloads": deepcopy(self._payloads),
        }

    def restore_causal_state(self, raw: object) -> None:
        if (not isinstance(raw, Mapping)
                or set(raw) != {"schema", "policy_version", "cut", "total",
                               "cursor", "already_consolidated", "paid_payloads"}
                or raw["schema"] != self.schema
                or raw["policy_version"] != self.policy_version):
            raise ValueError("incompatible selection owner")
        total, cursor = raw["total"], raw["cursor"]
        refs, payloads = raw["already_consolidated"], raw["paid_payloads"]
        if (type(total) is not int or type(cursor) is not int
                or total < 0 or not 0 <= cursor <= total
                or type(refs) is not list or refs != sorted(set(refs))
                or any(type(ref) is not str or not ref for ref in refs)
                or type(payloads) is not list or len(payloads) != cursor):
            raise ValueError("corrupt selection snapshot")
        if raw["cut"] is None:
            if total or cursor or refs or payloads:
                raise ValueError("closed scan retains candidates")
            cut = None
        else:
            if total < 1:
                raise ValueError("invalid active scan length")
            cutraw = raw["cut"]
            if type(cutraw) is not dict or set(cutraw) != {
                    "world_step", "journal_index", "journal_event_id",
                    "journal_hash", "history_version"}:
                raise ValueError("invalid cut data")
            cut = ConsolidationCut(**cutraw)
            cut.validate()
        checked = []
        seen = set()
        for p in payloads:
            if type(p) is not dict:
                raise ValueError("invalid paid projection")
            checked_p = ConsolidationBatchSelector._projection(_FrozenEpisode(p))
            if checked_p["id"] in seen or (
                    cut is not None and checked_p["end_t_monde"] >= cut.world_step):
                raise ValueError("duplicated or late paid projection")
            seen.add(checked_p["id"])
            checked.append(checked_p)
        self._cut = cut
        self._total, self._offset = total, cursor
        self._committed = tuple(refs)
        self._payloads = checked
