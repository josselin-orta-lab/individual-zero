"""Deterministic logical compute budget for MVP v1.2.1.

No numerical budget is chosen here. All costs, envelopes, B_cycle and protected
capacity are explicit P-43 campaign configuration.

Spec: 5.3, 16.2-16.3, 20.3 Stage 1, P-43, INV-21, INV-22.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ComputeBudgetConfig:
    version: str
    cycle_ceiling: int
    module_envelopes: Mapping[str, int]
    protected_modules: frozenset[str]
    protected_capacity: int
    operation_costs: Mapping[str, int]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("budget config version must not be empty")
        if self.cycle_ceiling < 0:
            raise ValueError("B_cycle must be non-negative")
        if self.protected_capacity < 0:
            raise ValueError("protected capacity must be non-negative")
        if self.protected_capacity > self.cycle_ceiling:
            raise ValueError("protected capacity cannot exceed B_cycle")
        if not self.module_envelopes:
            raise ValueError("module envelopes must be explicit")
        for module, envelope in self.module_envelopes.items():
            if not module or envelope < 0:
                raise ValueError("module envelopes require non-empty ids and non-negative values")
        missing_protected = self.protected_modules - set(self.module_envelopes)
        if missing_protected:
            raise ValueError(
                "protected modules missing envelopes: "
                + ", ".join(sorted(missing_protected))
            )
        if not self.operation_costs:
            raise ValueError("operation costs must be explicit")
        for operation, cost in self.operation_costs.items():
            if not operation or cost < 0:
                raise ValueError("operation costs require non-empty ids and non-negative values")


@dataclass(frozen=True, slots=True)
class BudgetCharge:
    accepted: bool
    module: str
    operation: str
    requested_uc: int
    consumed_cycle_uc: int
    consumed_module_uc: int
    reason: str | None


class CycleComputeBudget:
    """Scheduler-owned per-cycle UC accounting with no carryover."""

    def __init__(self, *, config: ComputeBudgetConfig) -> None:
        config.validate()
        self._config = config
        self._cycle: int | None = None
        self._consumed_cycle = 0
        self._consumed_by_module: dict[str, int] = {}

    @property
    def owner_id(self) -> str:
        return "scheduler.compute_budget"

    @property
    def cycle(self) -> int | None:
        return self._cycle

    @property
    def consumed_cycle_uc(self) -> int:
        return self._consumed_cycle

    def consumed_module_uc(self, module: str) -> int:
        return self._consumed_by_module.get(module, 0)

    def open_cycle(self, cycle: int) -> None:
        if cycle < 1:
            raise ValueError("cycle must be >= 1")
        self._cycle = cycle
        self._consumed_cycle = 0
        self._consumed_by_module = {}

    def charge(
        self,
        *,
        module: str,
        operation: str,
        count: int = 1,
    ) -> BudgetCharge:
        if self._cycle is None:
            raise RuntimeError("compute budget requires an open cycle")
        if module not in self._config.module_envelopes:
            raise ValueError(f"unknown module envelope: {module}")
        if operation not in self._config.operation_costs:
            raise ValueError(f"unknown operation cost: {operation}")
        if count < 0:
            raise ValueError("operation count must be non-negative")

        requested = self._config.operation_costs[operation] * count
        module_before = self.consumed_module_uc(module)
        module_after = module_before + requested
        cycle_after = self._consumed_cycle + requested
        envelope = self._config.module_envelopes[module]

        reason: str | None = None
        if module_after > envelope:
            reason = "module_envelope"
        elif cycle_after > self._config.cycle_ceiling:
            reason = "cycle_ceiling"
        elif module not in self._config.protected_modules:
            ordinary_ceiling = (
                self._config.cycle_ceiling - self._config.protected_capacity
            )
            ordinary_consumed = sum(
                value
                for owner, value in self._consumed_by_module.items()
                if owner not in self._config.protected_modules
            )
            if ordinary_consumed + requested > ordinary_ceiling:
                reason = "protected_capacity"

        if reason is not None:
            return BudgetCharge(
                accepted=False,
                module=module,
                operation=operation,
                requested_uc=requested,
                consumed_cycle_uc=self._consumed_cycle,
                consumed_module_uc=module_before,
                reason=reason,
            )

        self._consumed_cycle = cycle_after
        self._consumed_by_module[module] = module_after
        return BudgetCharge(
            accepted=True,
            module=module,
            operation=operation,
            requested_uc=requested,
            consumed_cycle_uc=self._consumed_cycle,
            consumed_module_uc=module_after,
            reason=None,
        )

    def synthetic_state(self) -> str:
        """Return only the coarse state permitted for later S_t publication."""

        if self._cycle is None or self._consumed_cycle == 0:
            return "normal"
        fraction = self._consumed_cycle / self._config.cycle_ceiling if self._config.cycle_ceiling else 1.0
        if fraction >= 1.0:
            return "degraded"
        if fraction >= 0.75:
            return "constrained"
        return "normal"

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "cycle": self._cycle,
            "consumed_cycle_uc": self._consumed_cycle,
            "consumed_by_module": dict(sorted(self._consumed_by_module.items())),
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("compute budget state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("compute budget configuration version mismatch")
        cycle = state.get("cycle")
        consumed_cycle = state.get("consumed_cycle_uc")
        consumed_by_module = state.get("consumed_by_module")
        if cycle is not None and (not isinstance(cycle, int) or cycle < 1):
            raise ValueError("invalid budget cycle")
        if not isinstance(consumed_cycle, int) or consumed_cycle < 0:
            raise ValueError("invalid consumed cycle UC")
        if not isinstance(consumed_by_module, Mapping):
            raise ValueError("invalid per-module UC state")

        restored: dict[str, int] = {}
        for module, value in consumed_by_module.items():
            if module not in self._config.module_envelopes:
                raise ValueError(f"unknown module in budget state: {module}")
            if not isinstance(value, int) or value < 0:
                raise ValueError("invalid module UC value")
            restored[str(module)] = value

        if sum(restored.values()) != consumed_cycle:
            raise ValueError("cycle UC must equal sum of module UC")
        if consumed_cycle > self._config.cycle_ceiling:
            raise ValueError("restored cycle UC exceeds B_cycle")

        self._cycle = cycle
        self._consumed_cycle = consumed_cycle
        self._consumed_by_module = restored
