"""Stage-10 private pass runtime: focused contract checks, not semantic consolidation."""
import unittest

from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_pass_runner import (
    ConsolidationPassPlan, ConsolidationPassRunner, ConsolidationUnit,
)
from i0.modules.consolidation_transaction import ConsolidationCut, ConsolidationTransaction


COSTS = {
    "pass_prepare": 1, "pass_validate": 1,
    "episode_scan": 2, "episode_replay": 1,
    "rule_extraction": 2, "skill_compilation": 2,
    "kappa_recalibration": 2, "index_maintenance": 1,
}


def fixture():
    tx = ConsolidationTransaction(
        consolidation_id="c:1",
        cut=ConsolidationCut(4, 12, "journal:12", "aa" * 32, "h:0"),
        episode_refs=("ep:1",),
        episode_payloads={"ep:1": {
            "id": "ep:1", "end_t_monde": 2, "event_refs": ["event:1"],
        }},
        history_candidate={"seen": []},
    )
    budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
        version="P42:runner-test-v1", period_capacity_uc=15,
        step_slot_uc=5, operation_costs=COSTS,
    ))
    budget.begin_period(period_ref="sleep:1", entry_step=4)
    budget.begin_step(world_step=4)
    runner = ConsolidationPassRunner(transaction=tx, budget=budget)
    plan = ConsolidationPassPlan(
        consolidation_id=tx.id, pass_name="episode_selection",
        algorithm_version="test-owner-v1", batch_digest=tx.batch_digest,
        source_candidate_digest=tx.candidate_digest,
        units=(ConsolidationUnit(
            unit_ref="unit:1", operation="episode_scan",
            episode_refs=("ep:1",), data={"test": True},
        ),),
    )
    return tx, budget, runner, plan


class PrivatePassRunnerContractTests(unittest.TestCase):
    def test_charged_pass_remains_private_until_validation(self):
        tx, budget, runner, plan = fixture()
        self.assertTrue(runner.start_pass(plan))
        outcome = runner.advance_unit(
            lambda state, unit, episodes, cut: {"seen": [episodes["ep:1"]["id"]]}
        )
        self.assertEqual(outcome.outcome, "pass_ready")
        self.assertEqual(tx.cursor, 0)
        self.assertEqual(tx.candidate_copy(), {"seen": []})
        self.assertTrue(runner.finalize_pass(validator=lambda state: state["seen"] == ["ep:1"]))
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(tx.candidate_copy(), {"seen": ["ep:1"]})

    def test_waking_cancels_unvalidated_work_without_refund(self):
        tx, budget, runner, plan = fixture()
        runner.start_pass(plan)
        runner.advance_unit(lambda state, unit, episodes, cut: {"seen": ["ep:1"]})
        spent = budget.consumed_period_uc
        runner.interrupt_for_waking()
        self.assertEqual(tx.status, "suspended")
        self.assertEqual(tx.cursor, 0)
        self.assertEqual(tx.candidate_copy(), {"seen": []})
        self.assertEqual(budget.consumed_period_uc, spent)

    def test_rejects_restore_with_different_budget_lineage(self):
        tx, budget, runner, plan = fixture()
        runner.start_pass(plan)
        runner.advance_unit(lambda state, unit, episodes, cut: {"seen": ["ep:1"]})
        snapshot = runner.export_causal_state()
        state = budget.export_causal_state()
        state["used_period_refs"].append("sleep:phantom")
        state["used_period_refs"].sort()
        budget.restore_causal_state(state)
        with self.assertRaises(ValueError):
            runner.restore_causal_state(snapshot)
        self.assertEqual(runner.unit_cursor, 1)


if __name__ == "__main__":
    unittest.main()
