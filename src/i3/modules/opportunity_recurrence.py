"""Paid bounded recurrence memory for generic perceived opportunity modalities.

Software substrate only. It stores no position, source identity, token identity,
stock, schedule or World fact. The caller supplies post-perception booleans for
the generic sensor modalities water/token.

An occurrence is a modality onset: present now and absent on the previous
observed decision. Consecutive visibility therefore does not manufacture
recurrence. Only the latest three completed onset-to-onset gaps are retained.
"""
from __future__ import annotations

from collections import deque

from .body import CognitiveBudget, CognitiveWork, VITAL

SCHEMA = "i3-opportunity-recurrence-memory/v1"
MODALITIES = ("water", "token")
WINDOW = 3
OBSERVE_WORK = CognitiveWork(cycles=1, memory_items=8)


class OpportunityRecurrenceMemory:
    """Empty-at-birth chronology of generic perceived-modality onsets."""

    __slots__ = ("_step", "_previous", "_last_onset", "_gaps")

    def __init__(self):
        self._step = 0
        self._previous = {name: False for name in MODALITIES}
        self._last_onset = {name: None for name in MODALITIES}
        self._gaps = {name: deque(maxlen=WINDOW) for name in MODALITIES}

    @staticmethod
    def _alive_budget(budget):
        if not isinstance(budget, CognitiveBudget):
            raise ValueError("CognitiveBudget required")
        if any(budget.remaining[k] <= 0.0 for k in VITAL):
            raise ValueError("no recurrence cognition after physical death")

    @staticmethod
    def _presence(value):
        if (type(value) is not tuple or len(value) != 2 or
                any(type(x) is not bool for x in value)):
            raise ValueError("immutable (water_present, token_present) booleans required")
        return dict(zip(MODALITIES, value))

    def observe(self, presence, budget: CognitiveBudget, *,
                work_receipt: dict | None = None) -> dict:
        """Record one post-perception decision snapshot."""
        current = self._presence(presence)
        self._alive_budget(budget)
        if work_receipt is not None and type(work_receipt) is not dict:
            raise ValueError("work_receipt must be a plain dict")

        before = budget.work
        budget.spend(OBSERVE_WORK)
        self._step += 1

        onsets = []
        completed = []
        for modality in MODALITIES:
            if current[modality] and not self._previous[modality]:
                onsets.append(modality)
                old = self._last_onset[modality]
                if old is not None:
                    gap = self._step - old
                    if gap <= 0:
                        raise RuntimeError("nonpositive personal recurrence gap")
                    self._gaps[modality].append(gap)
                    completed.append((modality, gap))
                self._last_onset[modality] = self._step
            self._previous[modality] = current[modality]

        work = {
            key: getattr(budget.work, key) - getattr(before, key)
            for key in ("cycles", "simulated_steps", "memory_items", "replays")
        }
        result = {
            "schema": SCHEMA,
            "status": "OBSERVED",
            "personal_step": self._step,
            "onsets": tuple(onsets),
            "completed_gaps": tuple(completed),
            "work": work,
            "world_time_input": False,
            "position_input": False,
            "token_identity_input": False,
            "cost_is_physical_settlement_receipt": False,
        }
        if work_receipt is not None:
            work_receipt.clear()
            work_receipt.update({
                "schema": "i3-opportunity-recurrence-observe-work/v1",
                "status": "OBSERVED",
                "work": dict(work),
            })
        return result

    def estimate(self, modality: str, horizon: int,
                 budget: CognitiveBudget, *,
                 work_receipt: dict | None = None) -> dict:
        """Estimate one future matching opportunity from personal recurrence."""
        if modality not in MODALITIES:
            raise ValueError("known generic modality required")
        if type(horizon) is not int or horizon < 1:
            raise ValueError("positive integer planning horizon required")
        self._alive_budget(budget)
        if work_receipt is not None and type(work_receipt) is not dict:
            raise ValueError("work_receipt must be a plain dict")

        gaps = tuple(self._gaps[modality])
        before = budget.work
        read_work = CognitiveWork(cycles=1, memory_items=2 + len(gaps))
        budget.spend(read_work)
        work = {
            key: getattr(budget.work, key) - getattr(before, key)
            for key in ("cycles", "simulated_steps", "memory_items", "replays")
        }

        if not gaps:
            status = "NO_PERSONAL_RECURRENCE_SUPPORT"
            probability = None
            successes = 0
        else:
            status = "COMPLETE_EMPIRICAL_RECURRENCE_ESTIMATE"
            successes = sum(gap <= horizon for gap in gaps)
            probability = successes / len(gaps)

        result = {
            "schema": SCHEMA,
            "status": status,
            "modality": modality,
            "horizon": horizon,
            "retained_gaps": gaps,
            "support_count": len(gaps),
            "success_count": successes,
            "future_matching_opportunity_probability": probability,
            "estimator": "UNSMOOTHED_RECENT_ONSET_GAP_FRACTION",
            "current_source_persistence_assumed": False,
            "world_law_claim": False,
            "work": work,
            "cost_is_physical_settlement_receipt": False,
        }
        if work_receipt is not None:
            work_receipt.clear()
            work_receipt.update({
                "schema": "i3-opportunity-recurrence-estimate-work/v1",
                "status": status,
                "work": dict(work),
            })
        return result

    def snapshot(self) -> dict:
        """Observer/debug snapshot only; not a paid decision read."""
        return {
            "schema": SCHEMA,
            "personal_step": self._step,
            "previous_presence": tuple(
                self._previous[name] for name in MODALITIES),
            "last_onset": tuple(
                self._last_onset[name] for name in MODALITIES),
            "gaps": {
                name: tuple(self._gaps[name]) for name in MODALITIES},
        }


__all__ = [
    "MODALITIES", "OBSERVE_WORK", "OpportunityRecurrenceMemory",
    "SCHEMA", "WINDOW",
]
