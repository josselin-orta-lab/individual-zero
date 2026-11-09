"""Frozen exact-cache accounting sensitivity tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_separable_cache_accounting as A
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork


class SeparableCacheAccountingTests(unittest.TestCase):
    def test_frozen_memory_and_compute_contract(self):
        self.assertEqual(A.TRACE_KEY_ITEMS, 13)
        self.assertEqual(A.TRACE_STORE_ITEMS, 1035)
        self.assertEqual(A.TRACE_READ_ITEMS, 19)
        self.assertEqual(A.SIM_PER_TRACE["bundle5_lower"], 51)
        self.assertEqual(A.SIM_PER_TRACE["scalar1_upper"], 255)
        self.assertEqual(
            A._cache_no_hit_projection_ceiling("bundle5_lower"),
            CognitiveWork(cycles=1, simulated_steps=255, memory_items=5270))
        self.assertEqual(
            A._cache_no_hit_projection_ceiling("scalar1_upper"),
            CognitiveWork(cycles=1, simulated_steps=1275, memory_items=5270))

    def test_direct_projection_remains_exact_in_both_arms(self):
        for arm in A.ARMS:
            exact = A._direct_exactness(arm)
            self.assertLessEqual(exact["max_value_error"], 1e-10)
            self.assertLessEqual(exact["max_body_error"], 1e-10)

    def test_hit_pays_read_but_no_rebuild(self):
        mind = A.make_mind("bundle5_lower")
        body = (80., 30., 30., 80., 80.)
        budget = CognitiveBudget((100.,) * 5, BodyLaws())
        mind.project(body, mind._drift, budget)
        first_stats = mind.cache_stats()
        first_work = budget.work
        self.assertEqual(first_stats["trace_builds"], 5)
        self.assertEqual(first_stats["trace_hits"], 0)

        mind.project(body, mind._drift, budget)
        second_stats = mind.cache_stats()
        delta = A._delta(budget.work, first_work)
        self.assertEqual(second_stats["trace_builds"], 5)
        self.assertEqual(second_stats["trace_hits"], 5)
        self.assertEqual(
            delta,
            CognitiveWork(cycles=1, memory_items=5 * A.TRACE_READ_ITEMS))

    def test_frozen_80_state_characterization_runs_without_prejudging_result(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = A.run(fh.name)
        self.assertEqual(report["schema"], A.SCHEMA)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        for arm in A.ARMS:
            self.assertEqual(report["arms"][arm]["evaluated"], 80)
            self.assertEqual(len(report["rows"][arm]), 80)
            self.assertEqual(
                report["arms"][arm]["actual_work_ceiling_violations"], 0)
        self.assertIn(
            report["classification"],
            (
                "CACHE_ACCOUNTING_ROBUSTLY_FUNDED",
                "CACHE_ACCOUNTING_UNFUNDED_EVEN_LOWER_BOUND",
                "CACHE_ACCOUNTING_SENSITIVE",
            ))
        print("SEPARABLE_CACHE_ACCOUNTING_REPORT " + json.dumps({
            "classification": report["classification"],
            "conservative_runtime_candidate_authorized":
                report["conservative_runtime_candidate_authorized"],
            "direct_exactness": report["direct_exactness"],
            "arms": report["arms"],
        }, sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_separable_cache_accounting; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
