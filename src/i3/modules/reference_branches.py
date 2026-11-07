"""Paid bounded empirical branches for the future P1.3-repertoire Stage 1.

This module is deliberately not a decision policy. It adds no World input,
action score, prior, map, plan or runtime dispatch. The ring is empty at birth
and stores only personally lived action/body effects through PersonalOutcomes.
"""
from __future__ import annotations

from .body import ACTIONS
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


__all__ = [
    "BRANCHES_PER_ACTION", "CAPACITY", "ReferenceBranchMemory", "STORE_WORK",
]
