"""Contract tests for budgeted private passes; NOT semantic learning tests."""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from i0.modules.consolidation_budget import (
    ConsolidationBudgetConfig, ConsolidationWorkBudget,
)
from i0.modules.consolidation_pass_runner import (
    ConsolidationPassRunner, ConsolidationPassPlan, ConsolidationUnit,
)
from i0.modules.consolidation_transaction import (
    ConsolidationTransaction, ConsolidationCut, PASSES,
)
from lab.determinism import canonical_causal_bytes

PRICES = {
    "pass_prepare": 1, "pass_validate": 1, "episode_scan": 2,
    "episode_replay": 1, "rule_extraction": 3,
    "skill_compilation": 3, "kappa_recalibration": 2,
    "index_maintenance": 1,
}
PASS_OPERATIONS = (
    "episode_scan", "episode_replay", "rule_extraction",
    "skill_compilation", "kappa_recalibration", "index_maintenance",
)


def new(*, step_capacity=10, period_capacity=100):
    cut = ConsolidationCut(5, 23, "journal:23", "a5" * 32, "h:v1")
    tx = ConsolidationTransaction(
        consolidation_id="consolidation:case:1", cut=cut,
        episode_refs=("e:1", "e:2"), episode_payloads={
            "e:1": {"id": "e:1", "end_t_monde": 2, "event_refs": ["ev:1"]},
            "e:2": {"id": "e:2", "end_t_monde": 4, "event_refs": ["ev:2"]},
        }, history_candidate={"applied": []},
    )
    budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
        version="P42:pass-contract-v1", period_capacity_uc=period_capacity,
        step_slot_uc=step_capacity, operation_costs=PRICES,
    ))
    return tx, budget, ConsolidationPassRunner(transaction=tx, budget=budget)


def begin(budget, step=5, ref="period:1"):
    budget.begin_period(period_ref=ref, entry_step=step)
    budget.begin_step(world_step=step)


def plan(tx, units=1, pass_name=None, prefix="w", episode_ref="e:1"):
    name = PASSES[tx.cursor] if pass_name is None else pass_name
    return ConsolidationPassPlan(
        consolidation_id=tx.id, pass_name=name,
        algorithm_version="owner-algorithm-test-v1",
        batch_digest=tx.batch_digest,
        source_candidate_digest=tx.candidate_digest,
        units=tuple(
            ConsolidationUnit(
                unit_ref=f"{prefix}:{name}:{i}",
                operation=PASS_OPERATIONS[PASSES.index(name)],
                episode_refs=(episode_ref,), data={"index": i},
            ) for i in range(units)
        ),
    )


def handler(candidate, unit, episodes, cut):
    assert set(episodes) == set(unit.episode_refs)
    assert cut.world_step == 5
    candidate["applied"].append([unit.operation, unit.unit_ref])
    return candidate


def finish_one(tx, run):
    assert run.start_pass(plan(tx))
    result = run.advance_unit(handler)
    assert result.outcome == "pass_ready"
    assert run.finalize_pass(validator=lambda state: isinstance(state["applied"], list))


class ConsolidationPassRunnerTests(unittest.TestCase):
    def test_incomplete_pass_remains_private_until_validation(self):
        tx, budget, runner = new()
        begin(budget)
        self.assertTrue(runner.start_pass(plan(tx, units=2)))
        self.assertEqual(budget.consumed_step_uc, 1)
        before = tx.export_causal_state()
        step = runner.advance_unit(handler)
        self.assertEqual(step.outcome, "processed")
        self.assertEqual(step.unit_cursor, 1)
        self.assertEqual(step.charged_uc, 2)
        self.assertEqual(tx.export_causal_state(), before)
        with self.assertRaises(ValueError):
            runner.finalize_pass(validator=lambda _: True)
        self.assertEqual(runner.advance_unit(handler).outcome, "pass_ready")
        self.assertEqual(budget.consumed_step_uc, 5)
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(budget.consumed_step_uc, 6)
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(len(tx.candidate_copy()["applied"]), 2)
        self.assertIsNone(runner.active_pass)

    def test_full_six_pass_contract_never_publishes_active_owner(self):
        tx, budget, runner = new()
        begin(budget)
        for i in range(len(PASSES)):
            if i:
                budget.begin_step(world_step=5 + i)
            finish_one(tx, runner)
        self.assertEqual(tx.completed_passes, PASSES)
        self.assertEqual(len(tx.validated_candidate(validator=lambda _: True)["applied"]), 6)
        self.assertEqual(tx.status, "active")
        self.assertEqual(tx.cut.history_version, "h:v1")
        # The six fixture handlers are NOT the six cognitive passes.

    def test_cross_step_progress_is_charged_once_and_persistent(self):
        tx, budget, runner = new(step_capacity=3)
        begin(budget)
        self.assertTrue(runner.start_pass(plan(tx, units=3)))
        self.assertEqual(runner.advance_unit(handler).outcome, "processed")
        self.assertEqual(runner.advance_unit(handler).outcome, "budget_blocked")
        self.assertEqual(budget.consumed_step_uc, 3)
        self.assertEqual(runner.unit_cursor, 1)
        self.assertEqual(tx.cursor, 0)
        budget.begin_step(world_step=6)
        self.assertEqual(runner.advance_unit(handler).unit_cursor, 2)
        self.assertEqual(runner.advance_unit(handler).outcome, "budget_blocked")
        budget.begin_step(world_step=7)
        self.assertEqual(runner.advance_unit(handler).outcome, "pass_ready")
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(budget.consumed_period_uc, 8)

    def test_validation_waits_for_its_own_uc_and_never_fakes_checkpoint(self):
        tx, budget, runner = new(step_capacity=3)
        begin(budget)
        self.assertTrue(runner.start_pass(plan(tx)))
        runner.advance_unit(handler)
        self.assertFalse(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(tx.cursor, 0)
        budget.begin_step(world_step=6)
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(tx.cursor, 1)

    def test_no_budget_does_not_accept_plan_or_invoke_handler(self):
        tx, budget, runner = new(step_capacity=0, period_capacity=0)
        begin(budget)
        self.assertFalse(runner.start_pass(plan(tx)))
        self.assertIsNone(runner.active_pass)
        self.assertEqual(budget.consumed_period_uc, 0)
        with self.assertRaises(ValueError):
            runner.advance_unit(lambda *_: self.fail("invoked without UC"))

    def test_no_charge_cannot_process_a_unit(self):
        tx, budget, runner = new(step_capacity=1)
        begin(budget)
        self.assertTrue(runner.start_pass(plan(tx)))
        calls = []
        result = runner.advance_unit(lambda *_: calls.append("incorrect"))
        self.assertEqual(result.outcome, "budget_blocked")
        self.assertEqual(calls, [])
        self.assertEqual(runner.unit_cursor, 0)

    def test_incomplete_work_is_cancelled_on_wake_and_restarted(self):
        tx, budget, runner = new()
        begin(budget)
        finish_one(tx, runner)
        self.assertEqual(tx.cursor, 1)
        self.assertTrue(runner.start_pass(plan(tx, units=3)))
        runner.advance_unit(handler)
        self.assertEqual(runner.unit_cursor, 1)
        before = budget.consumed_period_uc
        runner.interrupt_for_waking()
        self.assertEqual(tx.status, "suspended")
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(len(tx.candidate_copy()["applied"]), 1)
        self.assertIsNone(runner.active_pass)
        self.assertEqual(budget.consumed_period_uc, before)
        budget.end_period()
        budget.begin_period(period_ref="period:2", entry_step=8)
        budget.begin_step(world_step=8)
        runner.resume_after_sleep_entry()
        self.assertEqual(tx.id, "consolidation:case:1")
        self.assertTrue(runner.start_pass(plan(tx, units=3)))
        for _ in range(3):
            runner.advance_unit(handler)
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(tx.cursor, 2)
        self.assertEqual(len(tx.candidate_copy()["applied"]), 4)

    def test_raised_handler_costs_uc_but_cannot_publish_mutation(self):
        tx, budget, runner = new()
        begin(budget)
        runner.start_pass(plan(tx))
        previous = runner.export_causal_state()
        def boom(candidate, *_):
            candidate["applied"].append(["invalid"])
            raise RuntimeError("handler crashed")
        with self.assertRaises(RuntimeError):
            runner.advance_unit(boom)
        self.assertEqual(runner.unit_cursor, previous["unit_cursor"])
        self.assertEqual(runner.export_causal_state()["working"], previous["working"])
        self.assertEqual(budget.consumed_period_uc, 3)
        self.assertEqual(tx.cursor, 0)
        self.assertEqual(runner.advance_unit(handler).outcome, "pass_ready")
        self.assertEqual(budget.consumed_period_uc, 5)

    def test_invalid_owner_result_charged_and_not_checkpointed(self):
        tx, budget, runner = new()
        begin(budget)
        runner.start_pass(plan(tx))
        with self.assertRaises(ValueError):
            runner.advance_unit(lambda *_: {"nonfinite": float("nan")})
        self.assertEqual(runner.unit_cursor, 0)
        self.assertEqual(tx.candidate_copy(), {"applied": []})
        self.assertEqual(budget.consumed_period_uc, 3)

    def test_failed_final_validator_never_creates_checkpoint(self):
        tx, budget, runner = new()
        begin(budget)
        runner.start_pass(plan(tx))
        runner.advance_unit(handler)
        self.assertEqual(budget.consumed_period_uc, 3)
        with self.assertRaises(ValueError):
            runner.finalize_pass(validator=lambda _: False)
        self.assertEqual(tx.cursor, 0)
        self.assertEqual(runner.unit_cursor, 1)
        self.assertEqual(budget.consumed_period_uc, 4)
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(tx.cursor, 1)

    def test_owner_plan_has_pinned_batch_version_and_operation(self):
        tx, budget, runner = new()
        begin(budget)
        good = plan(tx)
        for changes in (
            {"consolidation_id": "other"}, {"batch_digest": "e" * 64},
            {"algorithm_version": ""}, {"source_candidate_digest": "0" * 64},
            {"pass_name": PASSES[1]}, {"units": ()},
            {"units": (ConsolidationUnit("m", "episode_replay", ("e:1",), {}),)},
            {"units": (ConsolidationUnit("m", "episode_scan", ("missing",), {}),)},
            {"units": (ConsolidationUnit("m", "episode_scan", ("e:1",), {}),) * 2},
        ):
            from dataclasses import replace
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                runner.start_pass(replace(good, **changes))
        self.assertEqual(budget.consumed_period_uc, 0)

    def test_plan_mutation_after_admission_is_not_observed(self):
        tx, budget, runner = new()
        begin(budget)
        raw = {"value": [1]}
        p = plan(tx)
        from dataclasses import replace
        p = replace(p, units=(ConsolidationUnit("u:1", "episode_scan", ("e:1",), raw),))
        self.assertTrue(runner.start_pass(p))
        raw["value"].append(99)
        observed = []
        def record(candidate, unit, *_):
            observed.extend(unit.data["value"])
            return candidate
        runner.advance_unit(record)
        self.assertEqual(observed, [1])

    def test_snapshot_roundtrip_at_partial_cursor_replays_identically(self):
        tx, budget, runner = new(step_capacity=5)
        begin(budget)
        runner.start_pass(plan(tx, units=3))
        runner.advance_unit(handler)
        frozen = [json.loads(json.dumps(state)) for state in (
            tx.export_causal_state(), budget.export_causal_state(),
            runner.export_causal_state(),
        )]
        tx2 = ConsolidationTransaction.restore(frozen[0])
        budget2 = ConsolidationWorkBudget(budget.config)
        budget2.restore_causal_state(frozen[1])
        runner2 = ConsolidationPassRunner(transaction=tx2, budget=budget2)
        runner2.restore_causal_state(frozen[2])
        for b, r, t in ((budget, runner, tx), (budget2, runner2, tx2)):
            r.advance_unit(handler)
            b.begin_step(world_step=6)
            r.advance_unit(handler)
            r.finalize_pass(validator=lambda _: True)
            self.assertEqual(t.cursor, 1)
        self.assertEqual(canonical_causal_bytes(tx.export_causal_state()),
                         canonical_causal_bytes(tx2.export_causal_state()))
        self.assertEqual(runner.export_causal_state(), runner2.export_causal_state())
        self.assertEqual(budget.export_causal_state(), budget2.export_causal_state())

    def test_snapshot_corruption_or_different_owner_is_atomic_failure(self):
        tx, budget, runner = new()
        begin(budget)
        runner.start_pass(plan(tx, units=2))
        runner.advance_unit(handler)
        saved = runner.export_causal_state()
        before = deepcopy(saved)
        for mutation in (
            {**saved, "unit_cursor": 99},
            {**saved, "consolidation_id": "another"},
            {**saved, "plan": None},
            {**saved, "working": {"forged": True}},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                runner.restore_causal_state(mutation)
            self.assertEqual(runner.export_causal_state(), before)
        tx3, budget3, runner3 = new()
        begin(budget3)
        with self.assertRaises(ValueError):
            runner3.restore_causal_state(saved)
        self.assertEqual(runner3.unit_cursor, 0)

    def test_snapshot_detects_changed_prior_budget_lineage(self):
        tx, budget, runner = new()
        begin(budget)
        self.assertTrue(runner.start_pass(plan(tx, units=2)))
        runner.advance_unit(handler)
        previous = runner.export_causal_state()
        changed = deepcopy(budget.export_causal_state())
        changed["used_period_refs"].append("period:phantom")
        changed["used_period_refs"].sort()
        budget.restore_causal_state(changed)
        with self.assertRaises(ValueError):
            runner.restore_causal_state(previous)
        self.assertEqual(runner.unit_cursor, 1)

    def test_living_cognition_is_not_implied_by_a_work_runner(self):
        tx, budget, runner = new()
        with self.assertRaises(ValueError):
            runner.start_pass(plan(tx))
        # The transaction may be interrupted even before its first pass,
        # but this does not imply an admitted world command or a sleep step.
        runner.interrupt_for_waking()
        self.assertEqual(tx.status, "suspended")
        self.assertEqual(tx.cursor, 0)


if __name__ == "__main__":
    unittest.main()
