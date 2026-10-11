"""Logical Stage-10 sleep consolidation budget, not a waking cognition budget.

Implements the P-42 per-sleep-period and per-sleep-world-step work envelopes.
Only charged work may run. No wall-clock timing, free work, implicit budget
transfers, or simulated-time advancement. Scheduler integration must journal
charges and use this ledger only after a real sleep transition.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class ConsolidationBudgetConfig:
    version: str
    period_capacity_uc: int
    step_slot_uc: int
    operation_costs: Mapping[str, int]

    def validate(self) -> None:
        if type(self.version) is not str or not self.version.strip():
            raise ValueError("P-42 budget configuration requires a version")
        if any(type(x) is not int or x < 0 for x in (
            self.period_capacity_uc, self.step_slot_uc,
        )):
            raise ValueError("work capacity cannot be negative or non-integral")
        if (not isinstance(self.operation_costs, Mapping)
                or not self.operation_costs):
            raise ValueError("explicit work operation price schedule required")
        for operation, cost in self.operation_costs.items():
            if (type(operation) is not str or not operation.strip()
                    or type(cost) is not int or cost < 1):
                raise ValueError("all consolidation work must have positive logical cost")


@dataclass(frozen=True, slots=True)
class ConsolidationWorkCharge:
    accepted: bool
    operation: str
    count: int
    requested_uc: int
    consumed_period_uc: int
    consumed_step_uc: int
    reason: str | None


class ConsolidationWorkBudget:
    """Single period of sleep work; interruption preserves the transaction.

    Every open_step is one simulated sleep step, not a cognitive cycle. A new
    period may start after wake even if the old consolidation is suspended.
    This owner has no ability to publish consolidated knowledge or commands.
    """

    owner_id = "consolidation_work_budget"
    schema = "stage10-consolidation-work-budget-v1"

    def __init__(self, config: ConsolidationBudgetConfig) -> None:
        config.validate()
        self.config = ConsolidationBudgetConfig(
            version=config.version, period_capacity_uc=config.period_capacity_uc,
            step_slot_uc=config.step_slot_uc,
            operation_costs=MappingProxyType(dict(config.operation_costs)),
        )
        self._period_ref: str | None = None
        self._used_period_refs: set[str] = set()
        self._entry_step: int | None = None
        self._step: int | None = None
        self._consumed_period_uc = 0
        self._consumed_step_uc = 0
        self._last_closed_step: int | None = None

    @property
    def active_period_ref(self) -> str | None:
        return self._period_ref

    @property
    def consumed_period_uc(self) -> int:
        return self._consumed_period_uc

    @property
    def consumed_step_uc(self) -> int:
        return self._consumed_step_uc

    @property
    def open_world_step(self) -> int | None:
        return self._step

    def begin_period(self, *, period_ref: str, entry_step: int) -> None:
        if self._period_ref is not None:
            raise ValueError("cannot overlap two sleep periods")
        if (type(period_ref) is not str or not period_ref.strip()
                or period_ref in self._used_period_refs
                or type(entry_step) is not int or entry_step < 1):
            raise ValueError("invalid or repeated sleep period identifier or entry")
        if self._last_closed_step is not None and entry_step <= self._last_closed_step:
            raise ValueError("sleep periods must advance in world time")
        self._period_ref = period_ref
        self._used_period_refs.add(period_ref)
        self._entry_step = entry_step
        self._step = None
        self._consumed_period_uc = 0
        self._consumed_step_uc = 0

    def begin_step(self, *, world_step: int) -> None:
        if self._period_ref is None or self._entry_step is None:
            raise ValueError("cannot open work slot outside a sleep period")
        if type(world_step) is not int or world_step < self._entry_step:
            raise ValueError("invalid sleep step")
        if self._step is not None and world_step != self._step + 1:
            raise ValueError("sleep steps must progress consecutively")
        if self._step is None and world_step != self._entry_step:
            raise ValueError("first work step must match sleep entry")
        self._step = world_step
        self._consumed_step_uc = 0

    def charge(self, *, operation: str, count: int = 1) -> ConsolidationWorkCharge:
        if self._period_ref is None or self._step is None:
            raise ValueError("work can only occur in an open sleep step")
        if operation not in self.config.operation_costs:
            raise ValueError("unknown versioned consolidation operation")
        if type(count) is not int or count < 1:
            raise ValueError("work operation count must be a positive integer")
        requested = self.config.operation_costs[operation] * count
        reason = None
        if self._consumed_step_uc + requested > self.config.step_slot_uc:
            reason = "step_slot"
        elif self._consumed_period_uc + requested > self.config.period_capacity_uc:
            reason = "period_capacity"
        if reason is None:
            self._consumed_step_uc += requested
            self._consumed_period_uc += requested
        return ConsolidationWorkCharge(
            accepted=reason is None, operation=operation, count=count,
            requested_uc=requested, consumed_period_uc=self._consumed_period_uc,
            consumed_step_uc=self._consumed_step_uc, reason=reason,
        )

    def end_period(self) -> dict[str, object]:
        if self._period_ref is None:
            raise ValueError("no sleep period to end")
        receipt = {
            "period_ref": self._period_ref,
            "entry_step": self._entry_step,
            "last_work_step": self._step,
            "consumed_period_uc": self._consumed_period_uc,
        }
        self._last_closed_step = self._step if self._step is not None else self._entry_step
        self._period_ref = None
        self._entry_step = None
        self._step = None
        self._consumed_step_uc = 0
        self._consumed_period_uc = 0
        return receipt

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema, "config_version": self.config.version,
            "period_ref": self._period_ref,
            "used_period_refs": sorted(self._used_period_refs),
            "entry_step": self._entry_step,
            "step": self._step,
            "consumed_period_uc": self._consumed_period_uc,
            "consumed_step_uc": self._consumed_step_uc,
            "last_closed_step": self._last_closed_step,
        }

    def restore_causal_state(self, raw: object) -> None:
        if (not isinstance(raw, Mapping) or set(raw) != {
            "schema", "config_version", "period_ref", "used_period_refs",
            "entry_step", "step", "consumed_period_uc", "consumed_step_uc",
            "last_closed_step",
        } or raw.get("schema") != self.schema
                or raw.get("config_version") != self.config.version):
            raise ValueError("incompatible P-42 budget snapshot")
        period = raw["period_ref"]
        used = raw["used_period_refs"]
        entry, step, last = raw["entry_step"], raw["step"], raw["last_closed_step"]
        total, current = raw["consumed_period_uc"], raw["consumed_step_uc"]
        if (type(used) is not list or any(type(x) is not str or not x for x in used)
                or len(set(used)) != len(used) or used != sorted(used)):
            raise ValueError("invalid sleep period provenance")
        if (period is not None and (type(period) is not str or not period or period not in used)):
            raise ValueError("active period missing from provenance")
        if any(type(x) is not int or x < 0 for x in (total, current)):
            raise ValueError("negative or non-integral work counter")
        if total > self.config.period_capacity_uc or current > self.config.step_slot_uc or current > total:
            raise ValueError("work budget overrun in snapshot")
        if last is not None and (type(last) is not int or last < 1):
            raise ValueError("invalid last closed sleep step")
        if period is None:
            if entry is not None or step is not None or total or current or (used and last is None):
                raise ValueError("closed budget snapshot has live counters")
        else:
            if type(entry) is not int or entry < 1 or (last is not None and entry <= last):
                raise ValueError("invalid active period entry")
            if step is None:
                if total or current:
                    raise ValueError("no step open but work consumed")
            elif type(step) is not int or step < entry:
                raise ValueError("invalid opened sleep work step")
        # All checks precede owner mutation; malformed restoration is atomic.
        self._period_ref = period
        self._used_period_refs = set(used)
        self._entry_step = entry
        self._step = step
        self._consumed_period_uc = total
        self._consumed_step_uc = current
        self._last_closed_step = last


def select_batch_with_charged_work(*, budget: ConsolidationWorkBudget,
                                   selector, cut, episodes: Sequence,
                                   pending_episode_refs: tuple[str, ...]):
    """Charge the actual ledger before any selection access (P-42, INV-21).

    A single scan that exceeds the step slot is refused rather than silently
    spreading work over steps. Scalable resumable scanning is a separate open
    integration gate. A failed semantic validator does not refund work spent.
    """
    from .consolidation_batch import BatchSelectionBudgetError

    if budget.active_period_ref is None or budget.open_world_step is None:
        raise ValueError("batch selection requires an open sleeping world step")
    cfg = selector.policy
    actual = budget.config.operation_costs.get("episode_scan")
    if actual != cfg.scan_uc_per_episode:
        raise ValueError("P-42 selector and budget schedule disagree")
    quoted = selector.quote_scan_uc(examined_episode_count=len(episodes))
    if not episodes:
        # Zero scanned records => no charge, but no false candidate either.
        return selector.select(
            cut=cut, episodes=episodes, pending_episode_refs=pending_episode_refs,
            reserved_scan_uc=0,
        )
    receipt = budget.charge(operation="episode_scan", count=len(episodes))
    if not receipt.accepted:
        raise BatchSelectionBudgetError(
            "episode scan suspended by " + str(receipt.reason)
        )
    if receipt.requested_uc != quoted:
        raise ValueError("actual logical work differs from the selected quote")
    return selector.select(
        cut=cut, episodes=episodes, pending_episode_refs=pending_episode_refs,
        reserved_scan_uc=receipt.requested_uc,
    )
