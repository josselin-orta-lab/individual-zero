"""MVP v1.3.1: a real cognitive I0 runs without Oracle or EvaluationBench.

Historical evaluated Stage fixtures remain backward compatible; the new
standalone constructor is explicitly selected at birth.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from unittest.mock import patch

from lab.bench import EvaluationBench
from lab.journal_views import EvaluationTrace
from lab.mortal_execution import MortalStatus
from lab.oracle import create_oracle
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Command


def journal_kinds(instance):
    return [e.causal_event["kind"] for e in instance.journal.entries]


class StandaloneExhaustiveJournalTests(unittest.TestCase):
    def test_fresh_process_refuses_oracle_and_bench_module_imports(self):
        program = r'''
import importlib.abc
import sys
class NoLaboratoryModules(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {"lab.oracle", "lab.bench"}:
            raise ImportError("forbidden laboratory dependency " + fullname)
        return None
sys.meta_path.insert(0, NoLaboratoryModules())
from lab.stage4_reference_fixture import build_stage4_reference_runtime
individual = build_stage4_reference_runtime(autonomous_mortal=True)
assert individual.bench is None
assert individual.stage3.substrate.evaluation_trace is None
assert individual.stage3.substrate.mortal_status.value == "active"
for _ in range(3):
    result = individual.run_step()
    assert result.execution_status == "applied"
assert individual.journal.verify()
assert "lab.oracle" not in sys.modules
assert "lab.bench" not in sys.modules
print("standalone_without_oracle_bench:OK")
'''
        run = subprocess.run(
            [sys.executable, "-c", program],
            capture_output=True, text=True,
            timeout=90, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("standalone_without_oracle_bench:OK", run.stdout)

    def test_standalone_and_externally_evaluated_mortal_lives_match(self):
        standalone = build_stage4_reference_runtime(autonomous_mortal=True)
        evaluated = build_stage4_reference_runtime()
        evaluated.stage3.substrate.enable_mortal_world()
        self.assertIsNone(standalone.bench)
        self.assertIsNotNone(evaluated.bench)
        for _ in range(3):
            a = standalone.run_step()
            b = evaluated.run_step()
            self.assertEqual(a.execution_status, b.execution_status)
            self.assertEqual(a.command_primitive, b.command_primitive)
            self.assertEqual(
                standalone.world.export_causal_state(),
                evaluated.world.export_causal_state(),
            )
            self.assertEqual(
                standalone.journal.canonical_bytes(),
                evaluated.journal.canonical_bytes(),
            )
        self.assertTrue(standalone.journal.verify())

    def test_external_oracle_and_bench_reads_never_change_i0(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        individual.run_step()
        before_world = individual.world.export_causal_state()
        before_cognition = individual.s_t.export_causal_state()
        before_journal = individual.journal.canonical_bytes()
        oracle, capability = create_oracle(individual.world)
        trace = EvaluationTrace()
        external_bench = EvaluationBench(
            oracle=oracle, capability=capability, trace=trace,
        )
        truth = external_bench.oracle_truth()
        self.assertIn("position", truth)
        external_bench.count_safety_block(
            data={"probe": "scientific_external_only"},
        )
        self.assertEqual(individual.world.export_causal_state(), before_world)
        self.assertEqual(individual.s_t.export_causal_state(), before_cognition)
        self.assertEqual(individual.journal.canonical_bytes(), before_journal)
        self.assertEqual(len(trace.records), 2)
        self.assertTrue(individual.journal.verify())

    def test_terminal_death_is_recorded_in_full_internal_journal(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        sub = individual.stage3.substrate
        individual.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": individual.world.position.as_dict(), "active": True},
        )
        sub.open_step()
        result = sub.execute(Command("attendre"))
        self.assertEqual(result.status, "dead")
        self.assertEqual(sub.mortal_status, MortalStatus.DEAD)
        self.assertTrue(individual.journal.verify())
        kinds = journal_kinds(individual)
        self.assertIn("command_experienced", kinds)
        self.assertIn("world_transition_experienced", kinds)
        self.assertIn("individual_death_confirmed", kinds)
        self.assertIn("step_closed", kinds)
        self.assertEqual(kinds.count("individual_death_confirmed"), 1)
        self.assertLess(
            kinds.index("world_transition_experienced"),
            kinds.index("individual_death_confirmed"),
        )
        self.assertLess(
            kinds.index("individual_death_confirmed"),
            kinds.index("step_closed"),
        )
        self.assertNotIn("oracle_read", kinds)
        self.assertNotIn("lethal_rollback_completed", kinds)
        journal_bytes = individual.journal.canonical_bytes()
        with self.assertRaises(RuntimeError):
            individual.run_step()
        self.assertEqual(individual.journal.canonical_bytes(), journal_bytes)

    def test_bench_failure_cannot_erase_death_or_internal_event(self):
        runtime = build_stage4_reference_runtime()
        sub = runtime.stage3.substrate
        sub.enable_mortal_world()
        runtime.world.apply_scenario_event(
            "set_lethal_zone",
            {"position": runtime.world.position.as_dict(), "active": True},
        )
        sub.open_step()
        with patch.object(
            sub.bench, "count_lethal_transition",
            side_effect=RuntimeError("external evaluator crashed"),
        ):
            result = sub.execute(Command("attendre"))
        self.assertEqual(result.status, "dead")
        self.assertEqual(sub.mortal_status, MortalStatus.DEAD)
        self.assertTrue(runtime.journal.verify())
        self.assertEqual(journal_kinds(runtime).count("individual_death_confirmed"), 1)

    def test_stage10_keeps_consolidated_history_and_complete_journal(self):
        runtime = build_stage10_reference_runtime(
            start_fatigued=True, autonomous_mortal=True,
        )
        self.assertIsNone(runtime.bench)
        self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
        before_version = runtime.slow_history.current_version
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.command_primitive, "dormir")
        self.assertEqual(runtime.slow_history.current_version, before_version)
        self.assertTrue(runtime.journal.verify())
        self.assertTrue(len(runtime.journal.entries) > 0)
        self.assertIn("world_transition_experienced", journal_kinds(runtime))

    def test_stage11_keeps_full_journal_without_evaluation_service(self):
        runtime = build_stage11_reference_runtime(autonomous_mortal=True)
        self.assertIsNone(runtime.bench)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        self.assertTrue(runtime.journal.verify())
        self.assertIn("world_transition_experienced", journal_kinds(runtime))


if __name__ == "__main__":
    unittest.main()
