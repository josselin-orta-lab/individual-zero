"""Stage-10 bounded *execution boundary* for private consolidation passes.

MVP 15.4-15.6 / P-42 / INV-21, INV-23, INV-24, INV-47.

The owner of each pass supplies a versioned work plan and a pure per-unit
handler. This module NEVER invents hypotheses, Q values, rules, skills, or
knowledge. It charges physical-sleep *logical* UC before invoking any handler,
keeps unfinished work private across sleeping world steps, restarts the current
pass after waking, and uses ConsolidationTransaction for validated checkpoints.

The schedule/owner still must gate this component on actually admitted sleep,
write charged-work events into the journal, and coordinate any atomic commit.
Constructing a plan in a producer must itself be accounted for by the producer;
the work plan is not proof that a missing semantic algorithm exists.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping
from unicodedata import normalize

from lab.determinism import canonical_causal_bytes, sha256_hex
from .consolidation_budget import ConsolidationWorkBudget
from .consolidation_transaction import ConsolidationCut, ConsolidationTransaction, PASSES

_PASS_OPERATION = {
    "episode_selection": "episode_scan",
    "interleaved_replay": "episode_replay",
    "hypothesis_extraction": "rule_extraction",
    "procedural_compilation": "skill_compilation",
    "kappa_recalibration": "kappa_recalibration",
    "index_maintenance": "index_maintenance",
}


def _id(text: object) -> bool:
    return type(text) is str and bool(text.strip()) and text == normalize("NFC", text)


def _json(value: object) -> object:
    """Return owned canonical-data-compatible JSON values (no sets or NaN)."""
    if value is None or type(value) in (str, bool, int, float):
        canonical_causal_bytes(value)
        if type(value) is str and normalize("NFC", value) != value:
            raise ValueError("non-normalized causal string")
        return value
    if type(value) is list:
        return [_json(item) for item in value]
    if type(value) is dict:
        if any(not _id(key) for key in value):
            raise ValueError("causal keys must be NFC strings")
        return {key: _json(item) for key, item in value.items()}
    raise ValueError("work items and candidates must be causal JSON trees")


def _hash(value: object) -> str:
    return sha256_hex(canonical_causal_bytes(value))


@dataclass(frozen=True, slots=True)
class ConsolidationUnit:
    """One explicitly priced unit in the *owner's* versioned pass algorithm.

    Episode refs are provenance, and must be in the frozen transaction batch.
    Other owner-produced references can live in data, but do not acquire
    cognitive authority just by being present in this envelope.
    """
    unit_ref: str
    operation: str
    episode_refs: tuple[str, ...]
    data: object

    def export(self) -> dict[str, object]:
        return {
            "unit_ref": self.unit_ref, "operation": self.operation,
            "episode_refs": list(self.episode_refs), "data": _json(self.data),
        }


@dataclass(frozen=True, slots=True)
class ConsolidationPassPlan:
    consolidation_id: str
    pass_name: str
    algorithm_version: str
    batch_digest: str
    source_candidate_digest: str
    units: tuple[ConsolidationUnit, ...]

    def export(self) -> dict[str, object]:
        return {
            "consolidation_id": self.consolidation_id,
            "pass_name": self.pass_name,
            "algorithm_version": self.algorithm_version,
            "batch_digest": self.batch_digest,
            "source_candidate_digest": self.source_candidate_digest,
            "units": [unit.export() for unit in self.units],
        }

    def validate(self, tx: ConsolidationTransaction,
                 budget: ConsolidationWorkBudget) -> None:
        if (self.consolidation_id != tx.id or tx.status != "active"
                or tx.cursor >= len(PASSES) or self.pass_name != PASSES[tx.cursor]
                or not _id(self.algorithm_version)
                or self.batch_digest != tx.batch_digest
                or self.source_candidate_digest != tx.candidate_digest):
            raise ValueError("plan mismatches the private transaction or pass cursor")
        if type(self.units) is not tuple or not self.units:
            # No automatic success with an empty plan. A genuine no-op pass
            # needs an explicit, priced owner-provided verification unit.
            raise ValueError("each pass requires at least one charged unit")
        seen: set[str] = set()
        for unit in self.units:
            if not isinstance(unit, ConsolidationUnit):
                raise ValueError("invalid owner pass unit")
            if (not _id(unit.unit_ref) or unit.unit_ref in seen
                    or not _id(unit.operation)
                    or unit.operation not in budget.config.operation_costs
                    or unit.operation != _PASS_OPERATION[self.pass_name]
                    or type(unit.episode_refs) is not tuple
                    or any(not _id(ref) for ref in unit.episode_refs)
                    or len(unit.episode_refs) > 1
                    or len(set(unit.episode_refs)) != len(unit.episode_refs)
                    or not set(unit.episode_refs).issubset(tx.batch)):
                raise ValueError("invalid or unsupported pass unit provenance")
            seen.add(unit.unit_ref)
            _json(unit.data)
        if not {"pass_prepare", "pass_validate"}.issubset(budget.config.operation_costs):
            raise ValueError("P-42 pass preparation and validation must be priced")
        _hash(self.export())

    @classmethod
    def from_state(cls, state: object) -> "ConsolidationPassPlan":
        if (type(state) is not dict or set(state) != {
            "consolidation_id", "pass_name", "algorithm_version", "batch_digest",
            "source_candidate_digest", "units",
        } or type(state["units"]) is not list):
            raise ValueError("malformed pass plan snapshot")
        units = []
        for value in state["units"]:
            if type(value) is not dict or set(value) != {
                "unit_ref", "operation", "episode_refs", "data",
            } or type(value["episode_refs"]) is not list:
                raise ValueError("malformed pass work unit snapshot")
            units.append(ConsolidationUnit(
                unit_ref=value["unit_ref"], operation=value["operation"],
                episode_refs=tuple(value["episode_refs"]), data=_json(value["data"]),
            ))
        return cls(
            consolidation_id=state["consolidation_id"],
            pass_name=state["pass_name"],
            algorithm_version=state["algorithm_version"],
            batch_digest=state["batch_digest"],
            source_candidate_digest=state["source_candidate_digest"],
            units=tuple(units),
        )


@dataclass(frozen=True, slots=True)
class WorkAdvance:
    outcome: str  # processed | budget_blocked | pass_ready
    pass_name: str
    unit_cursor: int
    total_units: int
    charged_uc: int
    blocked_reason: str | None


class ConsolidationPassRunner:
    """Transactional Stage-10 pass slots: partial progress is never published.

    This component owns only the *in-progress* working candidate and plan.
    The transaction owns validated checkpoints, the budget owns UC counters.
    Snapshot owners must restore all three under scheduler coordination.
    """

    owner_id = "consolidation_pass_runner"
    schema = "stage10-pass-runner-v1"

    def __init__(self, *, transaction: ConsolidationTransaction,
                 budget: ConsolidationWorkBudget):
        self.transaction = transaction
        self.budget = budget
        self._plan: ConsolidationPassPlan | None = None
        self._period_ref: str | None = None
        self._cursor = 0
        self._working: object | None = None

    @property
    def unit_cursor(self) -> int:
        return self._cursor

    @property
    def active_pass(self) -> str | None:
        return None if self._plan is None else self._plan.pass_name

    def start_pass(self, plan: ConsolidationPassPlan) -> bool:
        """Charge explicit preparation UC before accepting a sealed plan.

        False means insufficient sleep work budget: no state was changed.
        Owner-side plan-generation work is a separate charged responsibility.
        """
        if self._plan is not None:
            raise ValueError("a private pass is already active")
        if self.budget.open_world_step is None:
            raise ValueError("pass preparation requires a sleeping work step")
        plan.validate(self.transaction, self.budget)
        debit = self.budget.charge(operation="pass_prepare")
        if not debit.accepted:
            return False
        # Never retain references to mutable caller-owned plan data.
        frozen = ConsolidationPassPlan.from_state(plan.export())
        frozen.validate(self.transaction, self.budget)
        self._plan = frozen
        self._period_ref = self.budget.active_period_ref
        self._working = self.transaction.candidate_copy()
        self._cursor = 0
        return True

    def _check_live(self) -> ConsolidationPassPlan:
        plan = self._plan
        if (plan is None or self.transaction.status != "active"
                or self.budget.open_world_step is None
                or self.budget.active_period_ref != self._period_ref):
            raise ValueError("private pass has no admitted sleeping work slot")
        if (plan.consolidation_id != self.transaction.id
                or plan.pass_name != PASSES[self.transaction.cursor]
                or plan.batch_digest != self.transaction.batch_digest
                or plan.source_candidate_digest != self.transaction.candidate_digest):
            raise ValueError("private plan outlived its transaction baseline")
        return plan

    def advance_unit(self, handler: Callable[[object, ConsolidationUnit,
                         Mapping[str, object], ConsolidationCut], object]) -> WorkAdvance:
        plan = self._check_live()
        if self._cursor == len(plan.units):
            return WorkAdvance("pass_ready", plan.pass_name, self._cursor,
                               len(plan.units), 0, None)
        unit = plan.units[self._cursor]
        charge = self.budget.charge(operation=unit.operation)
        if not charge.accepted:
            return WorkAdvance("budget_blocked", plan.pass_name, self._cursor,
                               len(plan.units), 0, charge.reason)
        scoped = self.transaction.frozen_episode_subset_copy(unit.episode_refs)
        # The handler sees only detached, frozen autobiographical inputs and
        # the current private candidate. No journal/oracle/world accessor.
        result = handler(
            deepcopy(self._working),
            deepcopy(unit),
            scoped, self.transaction.cut,
        )
        working = _json(result)
        self._working = working
        self._cursor += 1
        return WorkAdvance(
            "pass_ready" if self._cursor == len(plan.units) else "processed",
            plan.pass_name, self._cursor, len(plan.units), charge.requested_uc, None,
        )

    def finalize_pass(self, validator: Callable[[object], bool]) -> bool:
        plan = self._check_live()
        if self._cursor != len(plan.units):
            raise ValueError("unprocessed units cannot produce validated checkpoints")
        debit = self.budget.charge(operation="pass_validate")
        if not debit.accepted:
            return False
        result = self._working
        self.transaction.run_pass(
            name=plan.pass_name,
            executor=lambda _base, _batch, _cut: result,
            validator=validator,
        )
        self._plan = None
        self._period_ref = None
        self._working = None
        self._cursor = 0
        return True

    def interrupt_for_waking(self) -> None:
        self.transaction.interrupt()
        # The entire current pass, even across many work slots, is cancelled;
        # only transaction-owned *validated* checkpoints remain.
        self._plan = None
        self._period_ref = None
        self._cursor = 0
        self._working = None

    def resume_after_sleep_entry(self) -> None:
        if self._plan is not None:
            raise ValueError("cannot resume while a private pass is still running")
        self.transaction.resume()

    def _budget_anchor(self) -> dict[str, object]:
        # Capture the complete causal ledger, not only the current counters.
        # The prior closed-period history is part of reproducible continuity.
        # Restoring a runner against a different budget lineage is rejected.
        return self.budget.export_causal_state()

    def export_causal_state(self) -> dict[str, object]:
        raw = {
            "schema": self.schema,
            "consolidation_id": self.transaction.id,
            "transaction_cursor": self.transaction.cursor,
            "transaction_candidate_digest": self.transaction.candidate_digest,
            "batch_digest": self.transaction.batch_digest,
            "period_ref": self._period_ref,
            "budget_anchor": self._budget_anchor(),
            "plan": None if self._plan is None else self._plan.export(),
            "unit_cursor": self._cursor,
            "working": None if self._plan is None else deepcopy(self._working),
        }
        raw["state_digest"] = _hash(raw)
        return raw

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict or set(state) != {
            "schema", "consolidation_id", "transaction_cursor",
            "transaction_candidate_digest", "batch_digest", "period_ref",
            "budget_anchor", "plan",
            "unit_cursor", "working", "state_digest",
        } or state.get("schema") != self.schema):
            raise ValueError("incompatible pass-runner snapshot schema")
        without_digest = {k: v for k, v in state.items() if k != "state_digest"}
        if state["state_digest"] != _hash(without_digest):
            raise ValueError("pass-runner snapshot digest mismatch")
        if (state["consolidation_id"] != self.transaction.id
                or type(state["transaction_cursor"]) is not int
                or state["transaction_cursor"] != self.transaction.cursor
                or state["transaction_candidate_digest"] != self.transaction.candidate_digest
                or state["batch_digest"] != self.transaction.batch_digest):
            raise ValueError("pass-runner snapshot mismatches consolidation state")
        if state["budget_anchor"] != self._budget_anchor():
            raise ValueError("pass-runner restore requires the matching sleep budget snapshot")
        plan_raw = state["plan"]
        cursor = state["unit_cursor"]
        if plan_raw is None:
            if cursor != 0 or state["working"] is not None or state["period_ref"] is not None:
                raise ValueError("idle pass-runner snapshot contains pending work")
            restored_plan, restored_working = None, None
        else:
            restored_plan = ConsolidationPassPlan.from_state(plan_raw)
            restored_plan.validate(self.transaction, self.budget)
            if (type(cursor) is not int or cursor < 0 or cursor > len(restored_plan.units)
                    or self.budget.open_world_step is None
                    or self.budget.active_period_ref != state["period_ref"]):
                raise ValueError("invalid active private work cursor")
            restored_working = _json(state["working"])
        # All validation precedes any mutation of this causal-state owner.
        self._plan = restored_plan
        self._period_ref = state["period_ref"]
        self._cursor = cursor
        self._working = restored_working
