"""P1.3 scoring with an opt-in paid empirical branch-memory control.

This class is intentionally NOT the Stage-1 information policy. Decisions are
delegated unchanged to Mind. The only added mechanism is a bounded, paid record
of personally lived action/body effects for later cost-matched experiments.
"""
from __future__ import annotations

from .body import CognitiveBudget, CognitiveWork, validate_body
from .mind import Mind
from .personal_outcomes import STORE_WORK
from .reference_branches import ReferenceBranchMemory


class ReferenceBranchMemoryMind(Mind):
    """Unchanged P1.3 decision path plus separately paid recent effect storage."""

    def __init__(self, genome, life_seed, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        self.branch_memory = ReferenceBranchMemory()
        self.branch_records = 0
        self._pending_branch = None
        self._branch_decision_start_body = None
        self._branch_decision_work = CognitiveWork()

    def _set_branch_decision_settlement(self, start_body, work):
        """Bind branch-memory work to the exact body that funded that work."""
        if not isinstance(work, CognitiveWork):
            raise ValueError("branch decision work must be CognitiveWork")
        self._branch_decision_start_body = validate_body(start_body)
        self._branch_decision_work = work

    def _clear_branch_decision_settlement(self):
        """Discard any unconsumed per-decision settlement receipt."""
        self._branch_decision_start_body = None
        self._branch_decision_work = CognitiveWork()

    def decide(self, cap, budget):
        self._pending_branch = None
        self._clear_branch_decision_settlement()
        start_body = tuple(budget.body)
        result = super().decide(cap, budget)
        self._set_branch_decision_settlement(start_body, result[2])
        return result

    def prepare_learning(self, result, budget):
        """Preserve reference replay allocation, then buy storage if affordable.

        The reference learning plan is computed on an identical detached
        allowance because Mind.prepare_learning has no state mutation. The real
        allowance then pays exactly that work/replay count. STORE_WORK is an
        additional block and never displaces a reference replay.
        """
        self._pending_branch = None
        settlement_body = self._branch_decision_start_body
        settlement_work = self._branch_decision_work
        self._clear_branch_decision_settlement()
        if not isinstance(budget, CognitiveBudget) or budget.work != CognitiveWork():
            raise ValueError("fresh learning CognitiveBudget required")
        if tuple(result["body"]) != budget.body:
            raise ValueError("learning allowance must match the current body")

        reference_budget = CognitiveBudget(budget.body, budget.laws)
        replay_limit = super().prepare_learning(result, reference_budget)
        if replay_limit is None:
            return None

        # Same exact work the P1.3 arm would have bought from this body.
        budget.spend(reference_budget.work)
        if budget.try_spend(STORE_WORK):
            before, key, action, _ = self.last
            if settlement_body is None:
                raise RuntimeError(
                    "missing branch decision settlement start body")
            branch_key = (
                action,
                key[1] if action in ("manger", "collecter") else None,
            )
            self._pending_branch = (
                branch_key,
                tuple(settlement_body),
                settlement_work,
                tuple(result["body"]),
                budget.laws,
            )
        return replay_limit

    def learn_from_outcome(self, result, *, replay_limit=0, replay_retention=True):
        pending, self._pending_branch = self._pending_branch, None
        replays = super().learn_from_outcome(
            result, replay_limit=replay_limit,
            replay_retention=replay_retention)
        if result["dead"] or pending is None:
            return replays

        key, before, decision_work, physical_body, laws = pending
        # This suballowance verifies the already prepaid STORE_WORK block. It is
        # never passed to World and therefore cannot debit the body twice.
        sub = CognitiveBudget(physical_body, laws)
        self.branch_memory.observe(key, before, decision_work, sub)
        if sub.work != STORE_WORK:
            raise RuntimeError("branch storage exceeded its prepaid block")
        self.branch_records += 1
        return replays
