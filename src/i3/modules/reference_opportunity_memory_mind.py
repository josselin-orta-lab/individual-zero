"""P1.3 storage-only control with paid generic opportunity recurrence memory.

This class extends the existing branch-memory storage control. Current decisions
remain exactly on that control's P1.3 path. A generic water/token presence pair
from already-paid personal perception is only committed after the World step,
during learning, if an additional recurrence-storage block is affordable.

The recurrence memory is never read by this class while deciding.
"""
from __future__ import annotations

from .body import CognitiveBudget, CognitiveWork
from .opportunity_recurrence import (
    OBSERVE_WORK, OpportunityRecurrenceMemory)
from .reference_memory_mind import ReferenceBranchMemoryMind


class ReferenceOpportunityMemoryMind(ReferenceBranchMemoryMind):
    """Reference branch-memory control plus separately paid recurrence storage."""

    def __init__(self, genome, life_seed, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        self.opportunity_memory = OpportunityRecurrenceMemory()
        self.opportunity_records = 0
        self._pending_opportunity_presence = None
        self._pending_opportunity_commit = None

    def decide(self, cap, budget):
        self._pending_opportunity_presence = None
        self._pending_opportunity_commit = None
        result = super().decide(cap, budget)

        info = result[3]
        if info.get("funding") != "NO_PROCESSING_BUDGET":
            cells = [
                self.map[q] for q in self.visible
                if self.map.get(q) is not None
            ]
            self._pending_opportunity_presence = (
                any(cell[0] for cell in cells),
                any(bool(cell[1]) for cell in cells),
            )
        return result

    def prepare_learning(self, result, budget):
        """Buy all existing reference/branch work before recurrence storage."""
        self._pending_opportunity_commit = None
        presence = self._pending_opportunity_presence
        self._pending_opportunity_presence = None

        replay_limit = super().prepare_learning(result, budget)
        if replay_limit is None or presence is None:
            return replay_limit

        if budget.try_spend(OBSERVE_WORK):
            self._pending_opportunity_commit = (
                presence,
                tuple(result["body"]),
                budget.laws,
            )
        return replay_limit

    def learn_from_outcome(
            self, result, *, replay_limit=0, replay_retention=True):
        pending, self._pending_opportunity_commit = (
            self._pending_opportunity_commit, None)
        replays = super().learn_from_outcome(
            result, replay_limit=replay_limit,
            replay_retention=replay_retention)

        if result["dead"] or pending is None:
            return replays

        presence, physical_body, laws = pending
        sub = CognitiveBudget(physical_body, laws)
        self.opportunity_memory.observe(presence, sub)
        if sub.work != OBSERVE_WORK:
            raise RuntimeError(
                "opportunity recurrence storage exceeded prepaid block")
        self.opportunity_records += 1
        return replays


__all__ = ["ReferenceOpportunityMemoryMind"]
