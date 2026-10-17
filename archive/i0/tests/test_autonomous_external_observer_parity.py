"""MVP v1.3.1: independent external truth reads never alter I0 lives.

These are developer-level exact parity checks, not a scientific verdict.
An observed individual is still constructed in autonomous_mortal mode; the
laboratory observer is created *after* I0 and never injected into its graph.
Historical legacy rollback fixtures are deliberately not used as controls.
"""
from __future__ import annotations

import unittest

from lab.bench import EvaluationBench
from lab.evaluation_trace import EvaluationTrace
from lab.independent_journal_audit import audit_export_bytes
from lab.mortal_execution import MortalStatus
from lab.oracle import OracleAccessDenied, create_oracle
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class IndependentExternalObserverParityTests(unittest.TestCase):
    @staticmethod
    def attach_scientific_observer(individual):
        assert individual.bench is None
        oracle, capability = create_oracle(individual.world)
        external = EvaluationBench(
            trace=EvaluationTrace(), oracle=oracle, capability=capability,
        )
        return external, oracle

    def assert_same_individual_state(self, clean, externally_observed):
        self.assertEqual(clean.journal.canonical_bytes(),
                         externally_observed.journal.canonical_bytes())
        self.assertEqual(clean.journal.head_hash, externally_observed.journal.head_hash)
        self.assertEqual(clean.world.export_causal_state(),
                         externally_observed.world.export_causal_state())
        self.assertEqual(clean.scheduler.export_causal_state(),
                         externally_observed.scheduler.export_causal_state())
        self.assertIsNone(clean.bench)
        self.assertIsNone(externally_observed.bench)
        for name in ("s_t", "q_active", "kappa_active", "memory",
                     "slow_history", "causal_model", "sleep_session"):
            first = getattr(clean, name, None)
            second = getattr(externally_observed, name, None)
            if first is not None and hasattr(first, "export_causal_state"):
                self.assertEqual(first.export_causal_state(),
                                 second.export_causal_state(), name)

    def test_matched_cognitive_and_sleep_trajectories_ignore_external_oracle(self):
        cases = (
            (lambda: build_stage4_reference_runtime(autonomous_mortal=True), 3),
            (lambda: build_stage10_reference_runtime(
                start_fatigued=True, autonomous_mortal=True), 2),
            (lambda: build_stage11_reference_runtime(
                enable_geography=True, autonomous_mortal=True), 3),
        )
        for make, count in cases:
            with self.subTest(factory=make.__code__.co_firstlineno):
                clean = make()
                evaluated = make()
                bench, oracle = self.attach_scientific_observer(evaluated)
                self.assert_same_individual_state(clean, evaluated)
                for _ in range(count):
                    # External observer may read hidden physical facts, but I0
                    # has no reference to it or to the result of this read.
                    bench.oracle_truth()
                    before = evaluated.journal.canonical_bytes()
                    self.assertEqual(evaluated.journal.canonical_bytes(), before)
                    a = clean.run_step()
                    b = evaluated.run_step()
                    self.assertEqual(a, b)
                    bench.oracle_truth()
                    self.assert_same_individual_state(clean, evaluated)
                checked = audit_export_bytes(
                    evaluated.journal.canonical_bytes(),
                    expected_head=evaluated.journal.head_hash,
                    expected_count=len(evaluated.journal.entries),
                )
                self.assertEqual(checked.world_steps_closed, count)
                oracle.close()
                with self.assertRaises(OracleAccessDenied):
                    bench.oracle_truth()
                self.assert_same_individual_state(clean, evaluated)

    def test_unknown_lethal_transition_unaffected_by_secret_external_reads(self):
        clean = build_stage4_reference_runtime(autonomous_mortal=True)
        evaluated = build_stage4_reference_runtime(autonomous_mortal=True)
        # All possible current/adjacent destinations become lethal through
        # the external test fixture, not through either I0's cognition.
        for instance in (clean, evaluated):
            position = instance.world.position
            for x, y in (
                (position.x, position.y), (position.x - 1, position.y),
                (position.x + 1, position.y),
                (position.x, position.y - 1), (position.x, position.y + 1),
            ):
                instance.world.apply_scenario_event("set_lethal_zone", {
                    "position": {"x": x, "y": y}, "active": True,
                })
        bench, oracle = self.attach_scientific_observer(evaluated)
        bench.oracle_truth()
        a = clean.run_step()
        b = evaluated.run_step()
        self.assertEqual(a, b)
        self.assertEqual(a.execution_status, "dead")
        self.assertEqual(clean.stage3.substrate.mortal_status, MortalStatus.DEAD)
        self.assertEqual(evaluated.stage3.substrate.mortal_status, MortalStatus.DEAD)
        bench.oracle_truth()
        self.assert_same_individual_state(clean, evaluated)
        verified = audit_export_bytes(evaluated.journal.canonical_bytes())
        self.assertEqual(verified.terminal_deaths, 1)
        self.assertEqual(verified.autobiographical_commits, 0)
        with self.assertRaises(RuntimeError):
            clean.run_step()
        with self.assertRaises(RuntimeError):
            evaluated.run_step()
        oracle.close()


if __name__ == "__main__":
    unittest.main()
