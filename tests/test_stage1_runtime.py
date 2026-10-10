from __future__ import annotations

import time
import unittest

from lab.compute_budget import ComputeBudgetConfig
from lab.stage1_runtime import ScriptedStage1Runtime
from lab.snapshots import SnapshotType


def fixture_budget_config() -> ComputeBudgetConfig:
    return ComputeBudgetConfig(
        version="stage1-test-v1",
        cycle_ceiling=100,
        module_envelopes={"stage1_fixture": 100},
        protected_modules=frozenset({"stage1_fixture"}),
        protected_capacity=10,
        operation_costs={"fixture_op": 1},
    )


class ScriptedStage1RuntimeTests(unittest.TestCase):
    def run_reference(self, *, steps: int) -> ScriptedStage1Runtime:
        runtime = ScriptedStage1Runtime(campaign_seed=17, budget_config=fixture_budget_config())
        for _ in range(steps):
            runtime.run_step(cycle=1)
        return runtime

    def test_two_fresh_runs_produce_byte_identical_journals(self) -> None:
        first = self.run_reference(steps=3)
        second = self.run_reference(steps=3)

        self.assertEqual(
            first.journal.canonical_bytes(),
            second.journal.canonical_bytes(),
        )
        self.assertEqual(
            first.causal_fingerprint(),
            second.causal_fingerprint(),
        )
        self.assertTrue(first.journal.verify())
        self.assertTrue(second.journal.verify())

    def test_snapshot_restore_reproduces_exact_causal_continuation(self) -> None:
        runtime = self.run_reference(steps=2)
        snapshot = runtime.take_snapshot(
            snapshot_type=SnapshotType.PERIODIC,
        )

        runtime.run_step(cycle=1)
        runtime.run_step(cycle=1)
        expected = runtime.causal_fingerprint()

        journal_length_before_restore = len(runtime.journal.entries)

        runtime.restore(snapshot.id)
        runtime.run_step(cycle=1)
        runtime.run_step(cycle=1)
        actual = runtime.causal_fingerprint()

        self.assertEqual(actual, expected)
        self.assertGreater(len(runtime.journal.entries), journal_length_before_restore)
        self.assertTrue(runtime.journal.verify())

    def test_snapshot_restores_producer_local_sequences(self) -> None:
        runtime = self.run_reference(steps=1)
        snapshot = runtime.take_snapshot()
        before = {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
            if owner.owner_id.startswith("bus.producer_buffer.")
        }

        runtime.run_step(cycle=1)
        runtime.restore(snapshot.id)

        after = {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
            if owner.owner_id.startswith("bus.producer_buffer.")
        }

        self.assertEqual(after, before)

    def test_world_advances_once_per_normal_step(self) -> None:
        runtime = ScriptedStage1Runtime(campaign_seed=17, budget_config=fixture_budget_config())

        runtime.run_step(cycle=1)
        runtime.run_step(cycle=1)
        runtime.run_step(cycle=1)

        self.assertEqual(runtime.world.value, 3)
        self.assertEqual(runtime.scheduler.t_monde, 3)

    def test_bus_is_empty_at_normal_step_boundary(self) -> None:
        runtime = ScriptedStage1Runtime(campaign_seed=17, budget_config=fixture_budget_config())

        runtime.run_step(cycle=1)

        self.assertEqual(runtime.bus.available, ())

    def test_snapshot_hash_verifies_in_integrated_runtime(self) -> None:
        runtime = self.run_reference(steps=2)

        snapshot = runtime.take_snapshot()

        self.assertTrue(runtime.snapshots.verify(snapshot.id))

    def test_machine_delay_has_no_causal_effect(self) -> None:
        baseline = ScriptedStage1Runtime(campaign_seed=23, budget_config=fixture_budget_config())
        delayed = ScriptedStage1Runtime(campaign_seed=23, budget_config=fixture_budget_config())

        for _ in range(3):
            baseline.run_step(cycle=1)

        for _ in range(3):
            time.sleep(0.002)
            delayed.run_step(cycle=1)

        self.assertEqual(
            baseline.journal.canonical_bytes(),
            delayed.journal.canonical_bytes(),
        )
        self.assertEqual(
            baseline.causal_fingerprint(),
            delayed.causal_fingerprint(),
        )


if __name__ == "__main__":
    unittest.main()
