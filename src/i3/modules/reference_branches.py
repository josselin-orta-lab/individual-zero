"""Paid bounded empirical branches for the future P1.3-repertoire Stage 1.

This module is deliberately not a decision policy. It adds no World input,
action score, prior, map, plan or runtime dispatch. The ring is empty at birth
and stores only personally lived action/body effects through PersonalOutcomes.
"""
from __future__ import annotations

from .body import ACTIONS, CognitiveBudget, CognitiveWork, VITAL
from .information_value import WORK_KEYS
from .personal_outcomes import PersonalOutcomes, STORE_WORK, WINDOW

BRANCHES_PER_ACTION = WINDOW
CAPACITY = BRANCHES_PER_ACTION * len(ACTIONS)


class ReferenceBranchMemory(PersonalOutcomes):
    """Global bounded ring for 2-3 recent empirical effect branches.

    Capacity is an architecture constant, not inherited learned state:
    WINDOW records per primitive action class in the worst balanced case.
    The ring itself is global, so many token identities cannot grow memory.
    Exact-key support still precedes same-action fallback.
    """

    def __init__(self):
        super().__init__(CAPACITY)

    def branches(self, key, budget, *, support_index=None, work_receipt=None):
        """Return only paid personal bodily deltas; never invent support."""
        return self.read_support(
            key, budget, support_index=support_index,
            work_receipt=work_receipt)

    def recent_generic_effects(self, budget: CognitiveBudget, *,
                               work_receipt=None):
        """Paid action-agnostic read of the last <=WINDOW bodily deltas.

        The scan reads the existing ring but returns no action/token key.
        This is support for an unsupported-action uncertainty prior, never a
        point prediction and never a replacement for exact/same-action support.
        """
        if not isinstance(budget, CognitiveBudget):
            raise ValueError("CognitiveBudget required")
        if any(budget.remaining[k] <= 0.0 for k in VITAL):
            raise ValueError("no generic effect read after physical death")
        if work_receipt is not None and type(work_receipt) is not dict:
            raise ValueError("work_receipt must be a plain dict")
        before = budget.work
        budget.spend(CognitiveWork(
            cycles=1, memory_items=7 * len(self._samples) + 2))
        out = tuple(sample.delta for sample in list(self._samples)[-WINDOW:])
        if work_receipt is not None:
            work_receipt.clear()
            work_receipt.update({
                "schema": "i3-reference-generic-effect-read/v1",
                "status": "COMPLETE" if out else "EMPTY",
                "work": {
                    key: getattr(budget.work, key) - getattr(before, key)
                    for key in WORK_KEYS},
                "records": len(out),
                "action_identity_returned": False,
                "token_identity_returned": False,
            })
        return out


__all__ = [
    "BRANCHES_PER_ACTION", "CAPACITY", "ReferenceBranchMemory", "STORE_WORK",
]
