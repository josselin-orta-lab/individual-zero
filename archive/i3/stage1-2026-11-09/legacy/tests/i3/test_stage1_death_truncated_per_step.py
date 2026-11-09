"""Exact death-truncated per-step projection tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_projection_dependence as D
from i3.lab import stage1_death_truncated_per_step as T
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.forecast_work import projection_simulated_steps_ceiling


class DeathTruncatedPerStepTests(unittest.TestCase):
    def test_forecast_quote_stays_full_255(self):
        mind = T.make_mind()
        self.assertEqual(mind.proj_chunks, (1,) * 255)
        self.assertEqual(projection_simulated_steps_ceiling(mind), 255)

    def test_direct_projection_matches_per_step_and_pays_only_reached_endpoints(self):
        body = (80., 80., 30., 80., 80.)
        candidate = T.make_mind()
        truth = D.make_mind("per_step")
        budget = CognitiveBudget(body, BodyLaws())

        cv, cb = candidate.project(body, candidate._drift, budget)
        tv, tb = truth.project(body, truth._drift)

        for a, b in zip(cv, tv):
            self.assertAlmostEqual(a, b, places=11)
        self.assertEqual(cb, tb)

        stats = candidate.projection_stats()
        self.assertEqual(stats["project_calls"], 1)
        self.assertEqual(stats["early_death_calls"], 1)
        self.assertEqual(
            budget.work.simulated_steps,
            stats["paid_projection_steps"])
        self.assertLess(budget.work.simulated_steps, 255)

    def test_frozen_characterization_runs_without_prejudging_result(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = T.run(fh.name)
        self.assertEqual(report["schema"], T.SCHEMA)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertEqual(report["projection_grid"]["cases"], 486)
        self.assertEqual(report["nonlinear_option_set"]["bodies"], 10)
        self.assertEqual(report["candidate_g"]["evaluated"], 80)
        self.assertIn(
            report["verdict"],
            ("DEATH_TRUNCATED_PER_STEP_EXACT_PASS",
             "DEATH_TRUNCATED_PER_STEP_EXACT_FAIL"))
        print("DEATH_TRUNCATED_PER_STEP_REPORT " + json.dumps({
            "verdict": report["verdict"],
            "candidate_f_cost_parity":
                report["candidate_f_cost_parity"],
            "runtime_candidate_authorized":
                report["runtime_candidate_authorized"],
            "projection_grid": report["projection_grid"],
            "nonlinear_option_set": report["nonlinear_option_set"],
            "candidate_g": report["candidate_g"],
        }, sort_keys=True))

    def test_import_does_not_load_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_death_truncated_per_step; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
