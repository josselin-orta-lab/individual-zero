"""Public, retrospective Stage-11 Scheduler cycle-occurrence diagnostics.

These tests document the *existing* low-level reset seam, rather than claiming
that an Individual Zero world step actually double-opens a cognitive cycle.
Scientific Stage 9 remains NO-GO; no held-out claim or new physical learning.
"""
from unittest import TestCase

from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget
from lab.determinism import canonical_causal_bytes
from lab.stage1_runtime import ScriptedStage1Runtime
from lab.snapshots import SnapshotType


def _configuration() -> ComputeBudgetConfig:
    return ComputeBudgetConfig(
        version="stage11-cycle-occurrence-public-diagnostic-v1",
        cycle_ceiling=8,
        module_envelopes={"worker": 8, "control": 2},
        protected_modules=frozenset({"control"}),
        protected_capacity=2,
        operation_costs={"small": 2, "one": 1},
    )


class Stage11CycleOccurrenceCustodyDiagnostics(TestCase):
    def test_unprotected_low_level_duplicate_open_resets_spending_negative(self):
        # Explicitly a KNOWN NEGATIVE LEGACY API diagnostic, not a safety
        # claim. No real runtime duplication is inferred from this call.
        budget = CycleComputeBudget(config=_configuration())
        budget.open_cycle(1)
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)
        before = budget.export_causal_state()
        self.assertEqual(before["consumed_cycle_uc"], 2)
        budget.open_cycle(1)
        after = budget.export_causal_state()
        self.assertEqual(after["cycle"], 1)
        self.assertEqual(after["consumed_cycle_uc"], 0)
        self.assertEqual(after["consumed_by_module"], {})
        self.assertNotEqual(
            canonical_causal_bytes(before), canonical_causal_bytes(after),
        )
        print("stage11_legacy_duplicate_open_negative=erased_2_uc")

    def test_two_real_world_steps_reuse_cycle_one_without_contamination(self):
        def independent():
            runner = ScriptedStage1Runtime(
                campaign_seed=211, budget_config=_configuration(),
            )
            for _ in range(2):
                runner.run_step(cycle=1)
            technical_cycles = [
                (
                    e.causal_event["t_monde"],
                    e.causal_event["attempt_ref"],
                    e.causal_event["cycle"],
                )
                for e in runner.journal.entries
                if e.causal_event["kind"] == "cycle_opened"
            ]
            self.assertEqual(
                [(world, cycle) for world, _, cycle in technical_cycles],
                [(1, 1), (2, 1)],
            )
            self.assertNotEqual(technical_cycles[0][1], technical_cycles[1][1])
            self.assertEqual(runner.compute_budget.cycle, 1)
            self.assertEqual(runner.compute_budget.consumed_cycle_uc, 0)
            self.assertEqual(runner.world.value, 2)
            self.assertTrue(runner.journal.verify())
            return (
                tuple(technical_cycles),
                runner.journal.canonical_bytes(),
                runner.journal.head_hash,
                runner.causal_fingerprint(),
            )
        self.assertEqual(independent(), independent())

    def test_snapshotted_next_world_step_same_cycle_is_legitimate(self):
        def independent():
            runner = ScriptedStage1Runtime(
                campaign_seed=212, budget_config=_configuration(),
            )
            runner.run_step(cycle=1)
            record = runner.take_snapshot(
                snapshot_type=SnapshotType.PERIODIC,
            )
            self.assertTrue(runner.snapshots.verify(record.id))
            saved = runner.causal_fingerprint()
            runner.run_step(cycle=1)
            expected = runner.causal_fingerprint()
            runner.restore(record.id)
            self.assertEqual(runner.causal_fingerprint(), saved)
            runner.run_step(cycle=1)
            self.assertEqual(runner.causal_fingerprint(), expected)
            self.assertTrue(runner.journal.verify())
            return (
                record.id, record.sha256,
                runner.journal.canonical_bytes(),
                runner.journal.head_hash,
            )
        self.assertEqual(independent(), independent())
