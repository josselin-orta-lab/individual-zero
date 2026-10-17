"""Deterministic logical compute budget for MVP v1.2.1.

No numerical budget is chosen here. All costs, envelopes, B_cycle and protected
capacity are explicit P-43 campaign configuration.

Spec: 5.3, 16.2-16.3, 20.3 Stage 1, P-43, INV-21, INV-22.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ComputeBudgetConfig:
    version: str
    cycle_ceiling: int
    module_envelopes: Mapping[str, int]
    protected_modules: frozenset[str]
    protected_capacity: int
    operation_costs: Mapping[str, int]
    # Public, default-off versioned software custody mode. Legacy v1 states
    # retain exactly the same keys, hashes, and cycle-renewal semantics.
    cycle_occurrence_guard: bool = False

    def validate(self) -> None:
        """Fail closed on noncanonical logical UC configuration inputs.

        A frozen dataclass does not validate annotations at runtime. Validate
        the complete P-43 vocabulary and every cost before a Scheduler owner
        can be constructed. Do not round or coerce units of logical work.
        """
        if type(self.version) is not str or not self.version:
            raise ValueError("budget config version must not be empty")
        if type(self.cycle_occurrence_guard) is not bool:
            raise ValueError("cycle occurrence guard must be boolean")
        if type(self.cycle_ceiling) is not int or self.cycle_ceiling < 0:
            raise ValueError("B_cycle must be a non-negative integer")
        if type(self.protected_capacity) is not int or self.protected_capacity < 0:
            raise ValueError("protected capacity must be a non-negative integer")
        if self.protected_capacity > self.cycle_ceiling:
            raise ValueError("protected capacity cannot exceed B_cycle")
        if not isinstance(self.module_envelopes, Mapping) or not self.module_envelopes:
            raise ValueError("module envelopes must be explicit")
        for module, envelope in self.module_envelopes.items():
            if (
                type(module) is not str or not module
                or type(envelope) is not int or envelope < 0
            ):
                raise ValueError(
                    "module envelopes require non-empty string ids "
                    "and non-negative integer values"
                )
        if type(self.protected_modules) is not frozenset:
            raise ValueError("protected modules must be a frozenset")
        if any(type(module) is not str or not module
               for module in self.protected_modules):
            raise ValueError("protected module ids must be non-empty strings")
        missing_protected = self.protected_modules - set(self.module_envelopes)
        if missing_protected:
            raise ValueError(
                "protected modules missing envelopes: "
                + ", ".join(sorted(missing_protected))
            )
        if not isinstance(self.operation_costs, Mapping) or not self.operation_costs:
            raise ValueError("operation costs must be explicit")
        for operation, cost in self.operation_costs.items():
            if (
                type(operation) is not str or not operation
                or type(cost) is not int or cost < 0
            ):
                raise ValueError(
                    "operation costs require non-empty string ids "
                    "and non-negative integer values"
                )


@dataclass(frozen=True, slots=True)
class BudgetCharge:
    accepted: bool
    module: str
    operation: str
    requested_uc: int
    consumed_cycle_uc: int
    consumed_module_uc: int
    reason: str | None


@dataclass(frozen=True, slots=True)
class BudgetCapacityQuote:
    """Passive Scheduler admission quote, not a charged cognitive service."""

    required_uc: int
    available_uc: int
    affordable: bool


class CycleComputeBudget:
    """Scheduler-owned per-cycle UC accounting with no carryover."""

    def __init__(self, *, config: ComputeBudgetConfig) -> None:
        config.validate()
        # A frozen configuration dataclass does not freeze caller-owned dicts.
        # Copy both registered UC vocabularies before any owner state can be
        # published, so later producer writes cannot change work prices.
        # Keep normal private dicts for deepcopy/asdict compatibility.
        self._config = replace(
            config,
            module_envelopes=dict(config.module_envelopes),
            operation_costs=dict(config.operation_costs),
        )
        self._cycle: int | None = None
        self._consumed_cycle = 0
        self._consumed_by_module: dict[str, int] = {}
        self._active_occurrence: tuple[int, str, int] | None = None

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

    def quote_operations(
        self, *, module: str, operations: tuple[str, ...],
    ) -> BudgetCapacityQuote:
        """Ask the Scheduler if an entire named sequence can fit right now.

        This is a pure admission check of already-owned UC counters: it
        never runs any operation, reserves UC, publishes a safety fact,
        advances a cycle, or mutates causal state. Every actual operation
        still requires its separate ordinary charge() call.
        """
        if self._cycle is None:
            raise RuntimeError("compute budget requires an open cycle")
        if type(module) is not str or module not in self._config.module_envelopes:
            raise ValueError("unknown module envelope")
        if (
            type(operations) is not tuple or not operations
            or any(type(op) is not str or op not in self._config.operation_costs
                   for op in operations)
        ):
            raise ValueError("quote requires nonempty known operations")
        required = sum(self._config.operation_costs[op] for op in operations)
        available = min(
            self._config.module_envelopes[module]
            - self.consumed_module_uc(module),
            self._config.cycle_ceiling - self._consumed_cycle,
        )
        if module not in self._config.protected_modules:
            ordinary_consumed = sum(
                value for owner, value in self._consumed_by_module.items()
                if owner not in self._config.protected_modules
            )
            available = min(
                available,
                self._config.cycle_ceiling
                - self._config.protected_capacity
                - ordinary_consumed,
            )
        available = max(0, available)
        return BudgetCapacityQuote(
            required_uc=required, available_uc=available,
            affordable=required <= available,
        )

    def open_cycle(
        self, cycle: int, *,
        occurrence: tuple[int, str, int] | None = None,
    ) -> None:
        # A bool or fractional value must never become a causal cycle index.
        # Reject before the new cycle can reset any live UC counters.
        if type(cycle) is not int or cycle < 1:
            raise ValueError("cycle must be >= 1")
        active_occurrence = None
        if self._config.cycle_occurrence_guard:
            # Identify an actual Scheduler occurrence by world step, attempt
            # and cognitive cycle. A new step may legitimately start at 1.
            # Context is supplied by the Scheduler, not inferred from
            # speculative world truth or from the previous integer alone.
            if (
                type(occurrence) is not tuple or len(occurrence) != 3
                or type(occurrence[0]) is not int or occurrence[0] < 1
                or type(occurrence[1]) is not str or not occurrence[1]
                or type(occurrence[2]) is not int or occurrence[2] != cycle
            ):
                raise ValueError("invalid Scheduler cycle occurrence identity")
            if occurrence == self._active_occurrence:
                raise RuntimeError("Scheduler cycle occurrence already opened")
            active_occurrence = occurrence
        self._cycle = cycle
        self._consumed_cycle = 0
        self._consumed_by_module = {}
        self._active_occurrence = active_occurrence

    def charge(
        self,
        *,
        module: str,
        operation: str,
        count: int = 1,
    ) -> BudgetCharge:
        if self._cycle is None:
            raise RuntimeError("compute budget requires an open cycle")
        if type(module) is not str or module not in self._config.module_envelopes:
            raise ValueError(f"unknown module envelope: {module}")
        if type(operation) is not str or operation not in self._config.operation_costs:
            raise ValueError(f"unknown operation cost: {operation}")
        # P-43 logical work is integral. Python bool is an int subclass;
        # checking only count < 0 also accepts fractional/NaN requests.
        # Validate before arithmetic, charge, or any state publication.
        if type(count) is not int or count < 0:
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

    def export_causal_state(self) -> object:
        state = {
            "config_version": self._config.version,
            "cycle": self._cycle,
            "consumed_cycle_uc": self._consumed_cycle,
            "consumed_by_module": dict(sorted(self._consumed_by_module.items())),
        }
        if self._config.cycle_occurrence_guard:
            occurrence = self._active_occurrence
            state["active_occurrence"] = (
                None if occurrence is None else {
                    "t_monde": occurrence[0],
                    "attempt_ref": occurrence[1],
                    "cycle": occurrence[2],
                }
            )
        return state

    def restore_causal_state(self, state: object) -> None:
        """Restore a complete and attainable Scheduler UC ledger atomically.

        Parsing into a detached map is not enough: a syntactically plausible
        state must also obey every envelope and the reserved safety capacity
        that ordinary charge() enforces. Validate everything before writing.
        """
        required_keys = {
            "config_version", "cycle", "consumed_cycle_uc",
            "consumed_by_module",
        }
        if self._config.cycle_occurrence_guard:
            required_keys.add("active_occurrence")
        if not isinstance(state, Mapping) or set(state) != required_keys:
            raise ValueError("invalid compute budget snapshot schema")
        if state["config_version"] != self._config.version:
            raise ValueError("compute budget configuration version mismatch")

        cycle = state["cycle"]
        consumed_cycle = state["consumed_cycle_uc"]
        consumed_by_module = state["consumed_by_module"]
        if cycle is not None and (type(cycle) is not int or cycle < 1):
            raise ValueError("invalid budget cycle")
        if type(consumed_cycle) is not int or consumed_cycle < 0:
            raise ValueError("invalid consumed cycle UC")
        if not isinstance(consumed_by_module, Mapping):
            raise ValueError("invalid per-module UC state")

        restored: dict[str, int] = {}
        ordinary_consumed = 0
        for module, value in consumed_by_module.items():
            if type(module) is not str or module not in self._config.module_envelopes:
                raise ValueError(f"unknown or invalid module in budget state: {module!r}")
            if type(value) is not int or value < 0:
                raise ValueError("invalid module UC value")
            if value > self._config.module_envelopes[module]:
                raise ValueError("restored module UC exceeds envelope")
            restored[module] = value
            if module not in self._config.protected_modules:
                ordinary_consumed += value

        if cycle is None and (consumed_cycle != 0 or restored):
            raise ValueError("unopened cycle cannot have charged work")
        if sum(restored.values()) != consumed_cycle:
            raise ValueError("cycle UC must equal sum of module UC")
        if consumed_cycle > self._config.cycle_ceiling:
            raise ValueError("restored cycle UC exceeds B_cycle")
        if ordinary_consumed > (
            self._config.cycle_ceiling - self._config.protected_capacity
        ):
            raise ValueError("restored ordinary UC exceeds protected reserve")

        occurrence = None
        if self._config.cycle_occurrence_guard:
            raw_occurrence = state["active_occurrence"]
            if cycle is None:
                if raw_occurrence is not None:
                    raise ValueError("unopened budget has an active occurrence")
            else:
                if (
                    not isinstance(raw_occurrence, Mapping)
                    or set(raw_occurrence) != {
                        "t_monde", "attempt_ref", "cycle",
                    }
                ):
                    raise ValueError("invalid restored Scheduler occurrence")
                world_step = raw_occurrence["t_monde"]
                attempt_ref = raw_occurrence["attempt_ref"]
                occurrence_cycle = raw_occurrence["cycle"]
                if (
                    type(world_step) is not int or world_step < 1
                    or type(attempt_ref) is not str or not attempt_ref
                    or type(occurrence_cycle) is not int
                    or occurrence_cycle != cycle
                ):
                    raise ValueError("invalid restored Scheduler occurrence")
                occurrence = (world_step, attempt_ref, occurrence_cycle)

        # All checks have passed; no state validation or coercion follows.
        self._cycle = cycle
        self._consumed_cycle = consumed_cycle
        self._consumed_by_module = restored
        self._active_occurrence = occurrence
