"""Focused Stage-2 paid-work characterization, never a born-life experiment."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage2_fixed_scores_horizon_software as M
from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork, cognitive_cost
)
from i3.modules.world import World


class FixedScoresHorizonSoftwareTests(unittest.TestCase):
    def test_frozen_complete_grid_without_world(self):
        with patch.object(World, "__init__", side_effect=AssertionError(
                "scientific or engineering World forbidden in this software gate")):
            result = M.audit()
        self.assertEqual(result["schema"], M.SCHEMA)
        self.assertEqual(result["source_kind"], "SYNTHETIC_UNPAID_FIXTURE_NOT_BORN")
        self.assertEqual(result["body_count"], 3)
        self.assertEqual(len(result["forecast_rows"]), 3 * 2 * 3)
        self.assertEqual(len(result["competition_rows"]), 3 * 3)
        self.assertEqual(result["worlds_opened"], 0)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        self.assertFalse(result["stage2_3_go"])
        self.assertTrue(result["fixed_competition_scores"])
        self.assertEqual(len(result["deterministic_software_sha256"]), 64)
        print("I3_STAGE2_DEPTH_SOFTWARE_RESULT=" + json.dumps({
            "sha256": result["deterministic_software_sha256"],
            "forecast_rows": len(result["forecast_rows"]),
            "competition_rows": len(result["competition_rows"]),
            "depth_changed_bodies": result["bodies_with_changed_depth_forecasts"],
            "raw_rank_changed_bodies": result["bodies_with_changed_raw_top"],
            "science": result["scientific_verdict"],
            "worlds": result["worlds_opened"],
        }, sort_keys=True))

    def test_each_native_model_forecast_actually_purchases_projection_work(self):
        result = M.audit()
        laws = BodyLaws()
        for row in result["forecast_rows"]:
            with self.subTest(body=row["body_index"], plan=row["plan"],
                              horizon=row["horizon"]):
                self.assertGreaterEqual(row["modeled_plan_steps"], 0)
                self.assertLessEqual(row["modeled_plan_steps"], row["horizon"])
                self.assertGreaterEqual(row["work"]["simulated_steps"],
                                        row["modeled_plan_steps"])
                self.assertGreater(row["work"]["simulated_steps"], 0)
                self.assertEqual(row["work"]["cycles"], 0)
                self.assertEqual(row["work"]["replays"], 0)
                self.assertGreater(row["paid_energy"], 0)
                self.assertGreater(row["paid_vigilance"], 0)
                self.assertEqual(len(row["post_model_budget_body"]), 5)
                bill = CognitiveWork(**row["work"])
                expected = cognitive_cost(laws, bill)
                self.assertAlmostEqual(row["paid_energy"], expected[0], places=12)
                self.assertAlmostEqual(row["paid_vigilance"], expected[1], places=12)

    def test_competition_repeats_frozen_scores_and_pays_every_cycle(self):
        result = M.audit()
        for row in result["competition_rows"]:
            with self.subTest(body=row["body_index"],
                              ceiling=row["cycles_ceiling"]):
                self.assertIn(row["chosen"], ("wait", "sleep"))
                self.assertGreaterEqual(row["cycles_paid"], 0)
                self.assertLessEqual(row["cycles_paid"], row["cycles_ceiling"])
                self.assertLessEqual(row["score_gap_from_raw_best"], 1e-12)
                self.assertEqual(row["work"]["cycles"], row["cycles_paid"])
                self.assertEqual(row["work"]["simulated_steps"], 0)
                self.assertEqual(row["work"]["memory_items"], 0)
                self.assertEqual(row["work"]["replays"], 0)
                self.assertAlmostEqual(
                    row["paid_energy"], row["cycles_paid"] * 0.02, places=12)
                self.assertAlmostEqual(
                    row["paid_vigilance"], row["cycles_paid"] * 0.05, places=12)
                if row["cycles_ceiling"] == 0:
                    self.assertEqual(row["cycles_paid"], 0)
                    self.assertEqual(row["paid_energy"], 0)
                    self.assertEqual(row["paid_vigilance"], 0)

    def test_failed_native_allowance_executes_no_unpaid_mental_work(self):
        body = (0.001, 60., 60., 80., 80.)
        budget = CognitiveBudget(body, BodyLaws())
        mind = M._source()
        with self.assertRaises(CognitiveFundingError):
            mind.simulate(body, M.PLANS[0][1], 8, budget)
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual(budget.remaining, body)
        competing = M._source()
        zero = CognitiveBudget(body, BodyLaws())
        winner, used = competing._compete(
            [("wait", -1.), ("sleep", -2.)], 4, zero)
        self.assertEqual(winner, "wait")
        self.assertEqual(used, 0)
        self.assertEqual(zero.work, CognitiveWork())

    def test_deterministic_and_no_policy_mutation(self):
        a = M.audit()
        b = M.audit()
        self.assertEqual(a, b)
        self.assertEqual(a["deterministic_software_sha256"],
                         b["deterministic_software_sha256"])
        self.assertTrue(0 <= a["bodies_with_changed_depth_forecasts"] <= 3)
        self.assertTrue(0 <= a["bodies_with_changed_raw_top"] <= 3)


if __name__ == "__main__":
    unittest.main()
