"""Engineering-only survival B1 plan: no scientific World in unit tests."""
from pathlib import Path
import json
import unittest

from i3.lab import engineering_cohort as ENG
from i3.lab import stage2_admission as ADM
from i3.lab import stage2_panel as PANEL


PLAN = (Path(__file__).resolve().parents[2] / "src" / "i3" / "docs" /
        "studies" / "stage2-replay-gate-selected-design" /
        "ENGINEERING_B1_PLAN.json")


class SurvivalB1EngineeringOnlyTests(unittest.TestCase):
    def test_plan_is_non_evidentiary_and_closed_for_scientific_indices(self):
        plan = PANEL.load_plan(PLAN)
        self.assertEqual(plan["scientific"]["indices"], [])
        self.assertEqual(plan["scientific"]["genome_seeds"], [])
        self.assertFalse(PANEL.cases(plan, "scientific"))
        self.assertTrue(plan["no_engineering_outcomes_publish"])
        self.assertTrue(plan["no_inference"])
        cases = PANEL.cases(plan, "engineering")
        self.assertEqual(len(cases), 24)
        self.assertEqual(set(x["cohort"] for x in cases), {"engineering"})
        self.assertEqual({x["policy"] for x in cases},
                         {"reference", "p13_replay_gate_v1"})
        blocks = {}
        for row in cases:
            self.assertIn(ENG.ENGINEERING[row["index"]], ENG.ENGINEERING)
            key = (row["family"], row["index"], row["genome_seed"])
            blocks.setdefault(key, []).append(row)
        self.assertEqual(len(blocks), 12)
        for pair in blocks.values():
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0]["life_seed"], pair[1]["life_seed"])
            self.assertEqual(pair[0]["genome_seed"], pair[1]["genome_seed"])
            self.assertEqual(pair[0]["index"], pair[1]["index"])

    def test_historical_runner_scientific_entrypoint_still_closed(self):
        # Must reject before World construction or reading live outcomes.
        with self.assertRaises(PermissionError):
            PANEL.execute(PLAN, "/tmp/should-not-exist-scientific")
        for cohort in ("development", "selection", "validation", "reserve"):
            with self.subTest(cohort=cohort), self.assertRaises(PermissionError):
                ADM.admit(cohort, "stable", 33, PLAN)

    def test_frozen_engineering_seed_is_not_science(self):
        for i in (30, 31, 32, 33):
            self.assertTrue(ENG.is_engineering_seed(ENG.ENGINEERING[i]))
            with self.assertRaises(PermissionError):
                ENG.assert_not_engineering(ENG.ENGINEERING[i])


if __name__ == "__main__":
    unittest.main()
