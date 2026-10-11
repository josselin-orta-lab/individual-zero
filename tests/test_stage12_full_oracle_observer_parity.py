"""Strict full-runtime oracle-observer parity, including real Stage10 sleep.

The independent Bench may observe hidden truth, but has no reference back
into the individual. No truth is injected into I0's perception, memory,
causal journal or motor control. Two deterministic physical executions are
compared, not the same individual restarted from a past state.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.bench import EvaluationBench
from lab.evaluation_trace import EvaluationTrace
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.oracle import OracleAccessDenied, create_oracle
from lab.stage12_operator_console import Stage12OperatorConsole
from test_v131_stage12_sixpass_operator_integration import integrated_all_module_runtime


class Stage12ReadOnlyObserverParityTests(unittest.TestCase):
    @staticmethod
    def assert_same_clean_and_observed(test, clean, observed):
        test.assertEqual(clean.journal.canonical_bytes(),
                         observed.journal.canonical_bytes())
        test.assertEqual(clean.world.export_causal_state(),
                         observed.world.export_causal_state())
        clean_states = {
            owner.owner_id: owner.export_causal_state()
            for owner in clean.causal_owners
        }
        observed_states = {
            owner.owner_id: owner.export_causal_state()
            for owner in observed.causal_owners
        }
        test.assertEqual(clean_states, observed_states)
        test.assertIsNone(clean.stage3.substrate.bench)
        test.assertIsNone(observed.stage3.substrate.bench)
        test.assertIsNone(clean.stage3.substrate.evaluation_trace)
        test.assertIsNone(observed.stage3.substrate.evaluation_trace)

    def test_external_truth_reads_never_change_selections_learning_sleep_or_h(self):
        with TemporaryDirectory() as directory:
            first = str(Path(directory) / "i0-unobserved.jsonl")
            second = str(Path(directory) / "i0-external-observer.jsonl")
            clean = integrated_all_module_runtime(first)
            observed = integrated_all_module_runtime(second)
            # The observer stays outside the I0 graph. The world-truth
            # capability never crosses a cognitive or journal interface.
            oracle, capability = create_oracle(observed.world)
            bench = EvaluationBench(
                trace=EvaluationTrace(), oracle=oracle, capability=capability,
            )
            self.assert_same_clean_and_observed(self, clean, observed)

            def matched_world_step():
                bench.oracle_truth()
                lhs = clean.run_step()
                rhs = observed.run_step()
                self.assertEqual(lhs, rhs)
                bench.oracle_truth()
                self.assert_same_clean_and_observed(self, clean, observed)
                return lhs

            for _ in range(16):
                if clean.memory.episodes:
                    break
                self.assertEqual(matched_world_step().execution_status, "applied")
            self.assertTrue(clean.memory.episodes)
            original_h = clean.slow_history.current_version
            for runtime in (clean, observed):
                fatigue = runtime.sleep_health.export_causal_state()
                fatigue["fatigue"] = 1.0
                runtime.sleep_health.restore_causal_state(fatigue)

            for _ in range(10):
                result = matched_world_step()
                self.assertEqual(result.execution_status, "applied")
                if result.command_primitive == "dormir":
                    break
            else:
                self.fail("two physically matched autonomous lives never selected dormir")

            for _ in range(18):
                self.assertEqual(matched_world_step().execution_status, "applied")
                if clean.slow_history.current_version != original_h:
                    break
            self.assertNotEqual(clean.slow_history.current_version, original_h)
            self.assertIsNone(clean.consolidation.current)
            self.assertIsNone(observed.consolidation.current)

            for individual in (clean, observed):
                Stage12OperatorConsole(
                    substrate=individual.stage3.substrate,
                    mode="diagnostic", policy_version="stage12-parity-stop-dev-v1",
                ).arreter(reason="completed_observer_parity")
            self.assert_same_clean_and_observed(self, clean, observed)
            for runtime, path in ((clean, first), (observed, second)):
                journal = runtime.journal
                self.assertTrue(journal.verify())
                audit = audit_export_bytes(
                    journal.canonical_bytes(),
                    expected_head=journal.head_hash,
                    expected_count=len(journal.entries),
                )
                self.assertEqual(audit.consolidation_publications, 1)
                self.assertEqual(
                    HashChainedJournal.audit_durable_wal(path)["head_hash"],
                    journal.head_hash,
                )
            oracle.close()
            with self.assertRaises(OracleAccessDenied):
                bench.oracle_truth()


if __name__ == "__main__":
    unittest.main()
