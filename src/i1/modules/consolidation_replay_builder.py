"""Resumable and strictly charged Stage-10 pass-2 *agenda construction*.

English normative MVP v1.2.1 15.6 / P-42 / INV-21,23,24,47.

This makes a work *schedule* from already frozen autobiographical episodes.
It is not semantic replay, learning, hypothesis induction or publication of h.
Every episode read, event check, ordering comparison, ordering insertion, and
output emission requires a successful logical-UC charge BEFORE the operation.
Each ``advance`` performs at most one charged operation, so a sleeping world
step never borrows work from a future step. The owner of the sleep state must
call ``cancel_for_waking`` when waking; construction then restarts from zero
in the next sleep period, as the current unvalidated pass was cancelled.

The complete canonical budget and transaction owners are external. Neither the
journal, physical WorldBody nor Lab oracle is accessible to this component.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping
from unicodedata import normalize

from lab.determinism import canonical_causal_bytes, sha256_hex
from .consolidation_budget import ConsolidationWorkBudget
from .consolidation_pass_runner import ConsolidationPassPlan, ConsolidationUnit
from .consolidation_replay_agenda import ReplayAgendaPolicy, ReplayAgendaEntry
from .consolidation_transaction import ConsolidationTransaction, PASSES


_OPERATIONS = {
    "scan": "replay_agenda_scan",
    "event": "replay_agenda_event",
    "compare": "replay_agenda_compare",
    "insert": "replay_agenda_insert",
    "emit": "replay_agenda_emit",
}


def _hash(value: object) -> str:
    return sha256_hex(canonical_causal_bytes(value))


def _ref(value: object) -> bool:
    return type(value) is str and bool(value) and value == normalize("NFC", value)


@dataclass(frozen=True, slots=True)
class ReplayBuildAdvance:
    outcome: str  # progressed | budget_blocked | ready
    operation: str | None
    charged_uc: int
    accepted_operations: int
    blocked_reason: str | None


class IncrementalReplayAgendaBuilder:
    """Snapshot-verifiable, per-work-unit replay agenda construction.

    Each stored operation is replayed only while *verifying a technical
    snapshot* (not during cognition) to independently reconstruct all mutable
    progress. No previously charged unit is charged again on restoration.
    """

    schema = "stage10-replay-agenda-builder-v1"
    owner_id = "consolidation_replay_builder"

    def __init__(self, *, transaction: ConsolidationTransaction,
                 policy: ReplayAgendaPolicy, budget: ConsolidationWorkBudget):
        policy.validate()
        if (transaction.status != "active"
                or transaction.cursor != PASSES.index("interleaved_replay")
                or not transaction.batch):
            raise ValueError("agenda construction requires an active, nonempty pass-2 batch")
        missing = set(_OPERATIONS.values()) - set(budget.config.operation_costs)
        if missing:
            raise ValueError("missing explicit P-42 agenda prices: " + ",".join(sorted(missing)))
        for operation in _OPERATIONS.values():
            if budget.config.operation_costs[operation] > budget.config.step_slot_uc:
                raise ValueError("agenda unit can never fit a sleeping work slot")
        if budget.active_period_ref is None or budget.open_world_step is None:
            raise ValueError("agenda construction requires an admitted sleep work step")
        self.transaction = transaction
        self.policy = policy
        self.budget = budget
        self._tx_id = transaction.id
        self._batch_digest = transaction.batch_digest
        self._candidate_digest = transaction.candidate_digest
        self._period_ref = budget.active_period_ref
        self._history: list[dict[str, object]] = []
        self._reset_engine()

    def _reset_engine(self) -> None:
        self._phase = "scan"
        self._episode_cursor = 0
        self._event_cursor = 0
        self._current: dict[str, object] | None = None
        self._seen_events: set[str] = set()
        self._recent: list[dict[str, object]] = []
        self._old: list[dict[str, object]] = []
        self._insert_pos = 0
        self._insert_here = False
        self._emit_recent = 0
        self._emit_old = 0
        self._emit_partition = "recent" if self.policy.start_with_recent else "old"
        self._emitting: dict[str, object] | None = None
        self._entries: list[ReplayAgendaEntry] = []

    @property
    def status(self) -> str:
        return self._phase

    @property
    def charged_operations(self) -> int:
        return len(self._history)

    @property
    def entries(self) -> tuple[ReplayAgendaEntry, ...]:
        if self._phase != "ready":
            raise ValueError("partially built replay agenda is private")
        return tuple(self._entries)

    def _require_active(self) -> None:
        if (self._phase in ("cancelled", "invalid") or self.transaction.status != "active"
                or self.transaction.cursor != PASSES.index("interleaved_replay")
                or self.transaction.id != self._tx_id
                or self.transaction.batch_digest != self._batch_digest
                or self.transaction.candidate_digest != self._candidate_digest
                or self.budget.active_period_ref != self._period_ref
                or self.budget.open_world_step is None):
            raise ValueError("agenda builder cannot run without matching sleep and causal owners")

    def _next_operation(self) -> str | None:
        if self._phase in ("ready", "cancelled"):
            return None
        if self._phase == "scan":
            return _OPERATIONS["scan"]
        if self._phase == "events":
            return _OPERATIONS["event"]
        if self._phase == "order":
            assert self._current is not None
            group = self._recent if self._current["partition"] == "recent" else self._old
            return _OPERATIONS["insert"] if self._insert_here or self._insert_pos >= len(group) else _OPERATIONS["compare"]
        if self._phase == "emit":
            return _OPERATIONS["emit"]
        raise ValueError("invalid agenda builder phase")

    def _apply_paid_operation(self, operation: str) -> None:
        """Apply exactly one previously charged operation; used uncharged
        ONLY by technical snapshot consistency verification. Never call from
        an individual's cognitive work path without ``budget.charge``.
        """
        if operation != self._next_operation():
            raise ValueError("incorrect charged replay agenda phase")
        if self._phase == "scan":
            ref = self.transaction.batch[self._episode_cursor]
            payload = self.transaction.frozen_episode_subset_copy((ref,))[ref]
            end, events = payload.get("end_t_monde"), payload.get("event_refs")
            if (payload.get("id") != ref or type(end) is not int
                    or end >= self.transaction.cut.world_step
                    or type(events) is not list or not events):
                raise ValueError("invalid pre-cut closed autobiographical episode")
            age = self.transaction.cut.world_step - end
            self._current = {
                "ref": ref, "end": end, "events": events,
                "partition": "recent" if age <= self.policy.recent_window_steps else "old",
            }
            self._event_cursor = 0
            self._phase = "events"
        elif self._phase == "events":
            assert self._current is not None
            ev = self._current["events"][self._event_cursor]
            if not _ref(ev) or ev in self._seen_events:
                raise ValueError("duplicate or invalid lived event reference")
            self._seen_events.add(ev)
            self._event_cursor += 1
            if self._event_cursor == len(self._current["events"]):
                self._insert_pos = 0
                self._insert_here = False
                self._phase = "order"
        elif self._phase == "order":
            assert self._current is not None
            recent = self._current["partition"] == "recent"
            group = self._recent if recent else self._old
            if operation == _OPERATIONS["compare"]:
                incumbent = group[self._insert_pos]
                def key(v: dict[str, object]):
                    return ((-v["end"], v["ref"]) if recent else (v["end"], v["ref"]))
                if key(self._current) < key(incumbent):
                    self._insert_here = True
                else:
                    self._insert_pos += 1
            else:
                group.insert(self._insert_pos, self._current)
                self._episode_cursor += 1
                self._current = None
                self._event_cursor = 0
                self._phase = "emit" if self._episode_cursor == len(self.transaction.batch) else "scan"
        elif self._phase == "emit":
            if self._emitting is None:
                current_group = self._recent if self._emit_partition == "recent" else self._old
                current_offset = self._emit_recent if self._emit_partition == "recent" else self._emit_old
                if current_offset >= len(current_group):
                    self._emit_partition = "old" if self._emit_partition == "recent" else "recent"
                    current_group = self._recent if self._emit_partition == "recent" else self._old
                    current_offset = self._emit_recent if self._emit_partition == "recent" else self._emit_old
                if current_offset >= len(current_group):
                    raise ValueError("invalid replay emission cursor")
                current = current_group[current_offset]
                if self._emit_partition == "recent":
                    self._emit_recent += 1
                else:
                    self._emit_old += 1
                self._emitting = {"record": current, "partition": self._emit_partition, "offset": 0}
            emission = self._emitting
            record = emission["record"]
            offset = emission["offset"]
            self._entries.append(ReplayAgendaEntry(
                unit_ref=f"replay:{len(self._entries):08d}",
                episode_ref=record["ref"],
                event_ref=record["events"][offset],
                temporal_partition=emission["partition"],
                event_offset=offset,
            ))
            emission["offset"] += 1
            if emission["offset"] == len(record["events"]):
                self._emitting = None
                self._emit_partition = "old" if self._emit_partition == "recent" else "recent"
            if (self._emitting is None
                    and self._emit_recent == len(self._recent)
                    and self._emit_old == len(self._old)):
                self._phase = "ready"
        else:
            raise ValueError("unrecognized replay builder phase")

    def advance(self) -> ReplayBuildAdvance:
        """Run at most one *charged* unit, with no implicit budget extension."""
        self._require_active()
        operation = self._next_operation()
        if operation is None:
            return ReplayBuildAdvance("ready", None, 0, len(self._history), None)
        debit = self.budget.charge(operation=operation)
        if not debit.accepted:
            return ReplayBuildAdvance("budget_blocked", operation, 0, len(self._history), debit.reason)
        # Physical evidence incompatibility is fatal for this private builder:
        # the failed logical work is charged once, never retried for free or
        # charged repeatedly. The scheduler may cancel the invalid batch.
        receipt = {
            "operation": operation,
            "world_step": self.budget.open_world_step,
            "period_ref": self._period_ref,
            "charged_uc": debit.requested_uc,
            "failed": False,
        }
        try:
            self._apply_paid_operation(operation)
        except Exception:
            receipt["failed"] = True
            self._history.append(receipt)
            self._phase = "invalid"
            raise
        self._history.append(receipt)
        return ReplayBuildAdvance(
            "ready" if self._phase == "ready" else "progressed",
            operation, debit.requested_uc, len(self._history), None,
        )

    def _engine_state(self) -> dict[str, object]:
        """Technical snapshot only. This is not cognitive work or a pass."""
        return deepcopy({
            "phase": self._phase, "episode_cursor": self._episode_cursor,
            "event_cursor": self._event_cursor, "current": self._current,
            "seen_events": sorted(self._seen_events),
            "recent": self._recent, "old": self._old,
            "insert_pos": self._insert_pos, "insert_here": self._insert_here,
            "emit_recent": self._emit_recent, "emit_old": self._emit_old,
            "emit_partition": self._emit_partition,
            "emitting": self._emitting,
            "entries": [entry.as_dict() for entry in self._entries],
        })

    def export_causal_state(self) -> dict[str, object]:
        state = {
            "schema": self.schema,
            "transaction_id": self._tx_id,
            "batch_digest": self._batch_digest,
            "candidate_digest": self._candidate_digest,
            "policy": {
                "version": self.policy.version,
                "recent_window_steps": self.policy.recent_window_steps,
                "start_with_recent": self.policy.start_with_recent,
            },
            "period_ref": self._period_ref,
            "budget_anchor": deepcopy(self.budget.export_causal_state()),
            "history": list(self._history),
            "engine": self._engine_state(),
        }
        state["digest"] = _hash(state)
        return state

    def restore_causal_state(self, state: object) -> None:
        """Validate by replaying previously charged progress *technically*.

        The budget owner must first be restored to the saved causal state.
        This does not execute owner handlers or advance physical/cognitive time.
        On any mismatch the live builder remains entirely unchanged.
        """
        if (type(state) is not dict or set(state) != {
            "schema", "transaction_id", "batch_digest", "candidate_digest",
            "policy", "period_ref", "budget_anchor", "history", "engine", "digest",
        } or state["schema"] != self.schema
                or type(state["digest"]) is not str):
            raise ValueError("incompatible replay builder snapshot schema")
        without_digest = {k: deepcopy(v) for k, v in state.items() if k != "digest"}
        if state["digest"] != _hash(without_digest):
            raise ValueError("replay builder state digest mismatch")
        if (state["transaction_id"] != self._tx_id
                or state["batch_digest"] != self._batch_digest
                or state["candidate_digest"] != self._candidate_digest
                or state["policy"] != {
                    "version": self.policy.version,
                    "recent_window_steps": self.policy.recent_window_steps,
                    "start_with_recent": self.policy.start_with_recent,
                }
                or state["period_ref"] != self._period_ref
                or state["budget_anchor"] != self.budget.export_causal_state()):
            raise ValueError("replay builder snapshot does not match causal owners")
        history = state["history"]
        if type(state["engine"]) is not dict:
            raise ValueError("invalid replay builder private progress state")
        if type(history) is not list:
            raise ValueError("invalid replay builder operation provenance")
        spent_by_step: dict[int, int] = {}
        prior_step = self.budget.export_causal_state()["entry_step"]
        open_step = self.budget.open_world_step
        total = 0
        for occurrence in history:
            if type(occurrence) is not dict or set(occurrence) != {
                "operation", "world_step", "period_ref", "charged_uc", "failed",
            }:
                raise ValueError("invalid replay builder charged-work receipt")
            op, step = occurrence["operation"], occurrence["world_step"]
            if (type(op) is not str or op not in _OPERATIONS.values()
                    or type(step) is not int or prior_step is None
                    or open_step is None or step < prior_step or step > open_step
                    or occurrence["period_ref"] != self._period_ref
                    or type(occurrence["charged_uc"]) is not int
                    or occurrence["charged_uc"] != self.budget.config.operation_costs[op]
                    or type(occurrence["failed"]) is not bool):
                raise ValueError("replay work was not charged in this sleeping period")
            prior_step = step
            total += occurrence["charged_uc"]
            spent_by_step[step] = spent_by_step.get(step, 0) + occurrence["charged_uc"]
            if spent_by_step[step] > self.budget.config.step_slot_uc:
                raise ValueError("replay work snapshot overran one sleep step")
        if (total > self.budget.consumed_period_uc
                or spent_by_step.get(open_step, 0) > self.budget.consumed_step_uc):
            raise ValueError("unfunded replay work in causal snapshot")
        # All previous work has already been charged. Replay here checks only
        # snapshot consistency; it must never call the sleep budget's charge().
        # The wake-cancelled state contains no cognitive progress and can be
        # restored even if its transaction is now suspended and sleep has ended.
        if state["engine"].get("phase") == "cancelled":
            if history:
                raise ValueError("cancelled agenda retained unvalidated work")
            shadow = object.__new__(IncrementalReplayAgendaBuilder)
            shadow.transaction, shadow.policy, shadow.budget = self.transaction, self.policy, self.budget
            shadow._tx_id = self._tx_id
            shadow._batch_digest = self._batch_digest
            shadow._candidate_digest = self._candidate_digest
            shadow._period_ref = self._period_ref
            shadow._history = []
            shadow._reset_engine()
            shadow._phase = "cancelled"
        else:
            shadow = IncrementalReplayAgendaBuilder(
                transaction=self.transaction, policy=self.policy, budget=self.budget,
            )
            for index, occurrence in enumerate(history):
                operation = occurrence["operation"]
                if operation != shadow._next_operation():
                    raise ValueError("invalid previously charged agenda operation")
                if occurrence["failed"]:
                    if index != len(history) - 1:
                        raise ValueError("failed operation cannot have later work")
                    try:
                        shadow._apply_paid_operation(operation)
                    except Exception:
                        shadow._phase = "invalid"
                    else:
                        raise ValueError("forged replay work failure")
                else:
                    shadow._apply_paid_operation(operation)
                shadow._history.append(deepcopy(occurrence))
        if state["engine"] != shadow._engine_state():
            raise ValueError("agenda snapshot inconsistent with frozen autobiography")
        # Mutation starts only after fully validating all fields and replay.
        self._phase = shadow._phase
        self._episode_cursor = shadow._episode_cursor
        self._event_cursor = shadow._event_cursor
        self._current = deepcopy(shadow._current)
        self._seen_events = set(shadow._seen_events)
        self._recent = deepcopy(shadow._recent)
        self._old = deepcopy(shadow._old)
        self._insert_pos = shadow._insert_pos
        self._insert_here = shadow._insert_here
        self._emit_recent = shadow._emit_recent
        self._emit_old = shadow._emit_old
        self._emit_partition = shadow._emit_partition
        self._emitting = deepcopy(shadow._emitting)
        self._entries = deepcopy(shadow._entries)
        self._history = list(shadow._history)

    def as_pass_plan(self) -> ConsolidationPassPlan:
        """Return priced replay *references*, never a learned h candidate."""
        self._require_active()
        if self._phase != "ready":
            raise ValueError("private agenda not yet constructed")
        digest = _hash({
            "id": self.transaction.id,
            "batch": self.transaction.batch_digest,
            "candidate": self.transaction.candidate_digest,
            "policy": {"version": self.policy.version,
                       "window": self.policy.recent_window_steps,
                       "recent_first": self.policy.start_with_recent},
            "entries": [entry.as_dict() for entry in self._entries],
        })
        return ConsolidationPassPlan(
            consolidation_id=self.transaction.id,
            pass_name="interleaved_replay",
            algorithm_version=self.policy.version,
            batch_digest=self.transaction.batch_digest,
            source_candidate_digest=self.transaction.candidate_digest,
            units=tuple(ConsolidationUnit(
                unit_ref=entry.unit_ref,
                operation="episode_replay",
                episode_refs=(entry.episode_ref,),
                data={"event_ref": entry.event_ref,
                      "event_offset": entry.event_offset,
                      "temporal_partition": entry.temporal_partition,
                      "agenda_digest": digest},
            ) for entry in self._entries),
        )

    def cancel_for_waking(self) -> None:
        """Discard the unvalidated pass schedule; do not refund UC or alter h.

        Scheduler/runner owns the actual wake and tx.interrupt() transition.
        """
        if self._phase == "cancelled":
            raise ValueError("agenda already cancelled")
        self._reset_engine()
        self._phase = "cancelled"
        self._history.clear()
