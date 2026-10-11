"""Independent tests for real P-42 work admission, no Stage-11 runtime."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import unittest

from i0.modules.consolidation_budget import (
    ConsolidationBudgetConfig, ConsolidationWorkBudget,
    select_batch_with_charged_work,
)
from i0.modules.consolidation_batch import (
    BatchSelectionPolicy, BatchSelectionBudgetError, ConsolidationBatchSelector,
)
from i0.modules.consolidation_transaction import ConsolidationCut
from test_stage10_consolidation_batch import EpisodeView, policy


def config(**kwargs):
    defaults = ConsolidationBudgetConfig(
        version="P-42:budget-dev-v1", period_capacity_uc=12,
        step_slot_uc=6,
        operation_costs={
            "episode_scan": 2, "episode_replay": 1,
            "rule_extraction": 3, "skill_compilation": 3,
            "kappa_recalibration": 2, "index_maintenance": 1,
        },
    )
    return replace(defaults, **kwargs)


def begin(budget, period="period:1", step=5):
    budget.begin_period(period_ref=period, entry_step=step)
    budget.begin_step(world_step=step)


class SleepConsolidationBudgetTests(unittest.TestCase):
    def test_step_slot_and_period_capacity_are_independent(self):
        owner = ConsolidationWorkBudget(config())
        begin(owner)
        charge = owner.charge(operation="episode_scan", count=3)
        self.assertTrue(charge.accepted)
        self.assertEqual(charge.requested_uc, 6)
        denied = owner.charge(operation="index_maintenance", count=1)
        self.assertFalse(denied.accepted)
        self.assertEqual(denied.reason, "step_slot")
        self.assertEqual(owner.consumed_period_uc, 6)
        owner.begin_step(world_step=6)
        self.assertEqual(owner.consumed_step_uc, 0)
        self.assertEqual(owner.consumed_period_uc, 6)
        self.assertTrue(owner.charge(operation="episode_scan", count=3).accepted)
        owner.begin_step(world_step=7)
        denied = owner.charge(operation="index_maintenance")
        self.assertFalse(denied.accepted)
        self.assertEqual(denied.reason, "period_capacity")
        self.assertEqual(owner.consumed_period_uc, 12)

    def test_no_charges_outside_sleep_or_with_unregistered_operations(self):
        owner = ConsolidationWorkBudget(config())
        with self.assertRaises(ValueError):
            owner.charge(operation="episode_scan")
        begin(owner)
        for operation, count in (("unknown", 1), ("episode_scan", 0), ("episode_scan", -1), ("episode_scan", True)):
            with self.subTest(operation=operation, count=count), self.assertRaises(ValueError):
                owner.charge(operation=operation, count=count)
        self.assertEqual(owner.consumed_period_uc, 0)

    def test_sleep_world_step_clock_is_strict_and_single_owner(self):
        owner = ConsolidationWorkBudget(config())
        begin(owner)
        with self.assertRaises(ValueError):
            owner.begin_period(period_ref="period:2", entry_step=6)
        for invalid in (5, 4, 7):
            with self.assertRaises(ValueError):
                owner.begin_step(world_step=invalid)
        owner.begin_step(world_step=6)
        receipt = owner.end_period()
        self.assertEqual(receipt["last_work_step"], 6)
        with self.assertRaises(ValueError):
            owner.begin_period(period_ref="period:1", entry_step=7)
        with self.assertRaises(ValueError):
            owner.begin_period(period_ref="period:3", entry_step=6)
        owner.begin_period(period_ref="period:3", entry_step=8)
        owner.begin_step(world_step=8)
        self.assertEqual(owner.consumed_period_uc, 0)

    def test_zero_work_budget_fails_closed_without_fake_sleep_scan(self):
        owner = ConsolidationWorkBudget(config(period_capacity_uc=0, step_slot_uc=0))
        begin(owner)
        result = owner.charge(operation="episode_scan", count=1)
        self.assertFalse(result.accepted)
        self.assertEqual(owner.consumed_period_uc, 0)

    def test_snapshot_json_roundtrip_and_atomic_invalid_restore(self):
        owner = ConsolidationWorkBudget(config())
        begin(owner)
        owner.charge(operation="episode_scan", count=2)
        valid = owner.export_causal_state()
        restored = ConsolidationWorkBudget(config())
        restored.restore_causal_state(json.loads(json.dumps(valid)))
        self.assertEqual(restored.export_causal_state(), valid)
        for forged in (
            {**valid, "consumed_step_uc": 100},
            {**valid, "config_version": "P-42:changed"},
            {**valid, "step": 1},
            {**valid, "period_ref": "not-in-ledger"},
            {**valid, "used_period_refs": []},
            {**valid, "consumed_period_uc": 0},
        ):
            with self.subTest(forged=forged), self.assertRaises(ValueError):
                restored.restore_causal_state(forged)
            self.assertEqual(restored.export_causal_state(), valid)

    def test_config_is_frozen_against_caller_mutation(self):
        values = {"episode_scan": 2}
        owner = ConsolidationWorkBudget(config(operation_costs=values))
        values["episode_scan"] = 500
        begin(owner)
        self.assertEqual(owner.charge(operation="episode_scan").requested_uc, 2)
        with self.assertRaises(TypeError):
            owner.config.operation_costs["episode_scan"] = 500

    def test_invalid_policy_and_cost_are_rejected(self):
        for invalid in (
            config(operation_costs={"episode_scan": 0}),
            config(operation_costs={"episode_scan": True}),
            config(period_capacity_uc=-1),
            config(step_slot_uc=-1),
            config(operation_costs={}),
        ):
            with self.assertRaises(ValueError):
                ConsolidationWorkBudget(invalid)

    def test_charged_batch_selection_debits_real_owner_before_read(self):
        owner = ConsolidationWorkBudget(config())
        begin(owner)
        selector = ConsolidationBatchSelector(policy())
        episodes = (EpisodeView("a", 2), EpisodeView("b", 3))
        batch = select_batch_with_charged_work(
            budget=owner, selector=selector, cut=ConsolidationCut(5, 2, "e:2", "af" * 32, "h:0"),
            episodes=episodes, pending_episode_refs=("a", "b"),
        )
        self.assertEqual(set(batch.episode_refs), {"a", "b"})
        self.assertEqual(batch.scan_uc, 4)
        self.assertEqual(owner.consumed_period_uc, 4)

    def test_stale_budget_config_or_exhausted_step_cannot_read(self):
        class Trap:
            def as_dict(self):
                raise AssertionError("scanned before debit")
        owner = ConsolidationWorkBudget(config(step_slot_uc=1))
        begin(owner)
        with self.assertRaises(BatchSelectionBudgetError):
            select_batch_with_charged_work(
                budget=owner, selector=ConsolidationBatchSelector(policy()),
                cut=ConsolidationCut(5, 2, "e:2", "af" * 32, "h:0"),
                episodes=(Trap(),), pending_episode_refs=("x",),
            )
        self.assertEqual(owner.consumed_period_uc, 0)
        bad_selector = ConsolidationBatchSelector(policy(scan_uc_per_episode=3))
        with self.assertRaises(ValueError):
            select_batch_with_charged_work(
                budget=owner, selector=bad_selector,
                cut=ConsolidationCut(5, 2, "e:2", "af" * 32, "h:0"),
                episodes=(Trap(),), pending_episode_refs=("x",),
            )
        self.assertEqual(owner.consumed_period_uc, 0)

    def test_zero_scan_still_requires_sleep_slot(self):
        owner = ConsolidationWorkBudget(config())
        selector = ConsolidationBatchSelector(policy())
        arguments = dict(budget=owner, selector=selector,
            cut=ConsolidationCut(5, 2, "e:2", "af" * 32, "h:0"),
            episodes=(), pending_episode_refs=())
        with self.assertRaises(ValueError):
            select_batch_with_charged_work(**arguments)
        begin(owner)
        result = select_batch_with_charged_work(**arguments)
        self.assertEqual(result.episode_refs, ())
        self.assertEqual(result.scan_uc, 0)

    def test_snapshot_after_wake_and_subsequent_period_resumption(self):
        owner = ConsolidationWorkBudget(config())
        begin(owner)
        owner.charge(operation="episode_replay", count=3)
        self.assertEqual(owner.end_period()["consumed_period_uc"], 3)
        snap = json.loads(json.dumps(owner.export_causal_state()))
        copy = ConsolidationWorkBudget(config())
        copy.restore_causal_state(snap)
        copy.begin_period(period_ref="period:2", entry_step=7)
        copy.begin_step(world_step=7)
        self.assertTrue(copy.charge(operation="episode_scan", count=3).accepted)
        self.assertEqual(copy.consumed_period_uc, 6)
        self.assertEqual(copy.consumed_step_uc, 6)


if __name__ == "__main__":
    unittest.main()
