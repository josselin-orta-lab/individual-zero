"""#990 pure study-contract tests. Absolutely no real born-life cohort in CI."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.i2_p4_origin_failure_study_990 import (
    ARMS, MAX_STEPS, WORLD_HARMS, frozen_cells,
    frozen_birth_kwargs, first_matched_factor_divergence,
    run_study,
)


def frame(action, *, before=None, after=None, site="camp", offers=None,
          factor_tagged=False):
    body = before or {"energy": 78.0, "food": 46.0,
                      "water": 44.0, "integrity": 94.0}
    return {
        "action": action, "before": body, "after": after or body,
        "site_before": site, "site_after": site,
        "offered": offers or ["attendre", "se_deplacer_vers_passage"],
        "factor_tagged": factor_tagged,
    }


def diagnose(*failed_ticks):
    return {"ticks": [{"failed_channels": ["food"] if tick in failed_ticks
                       else []} for tick in range(5)]}


class P4OriginFailure990Contract(unittest.TestCase):
    def test_exact_six_prospectively_frozen_birth_cells(self):
        cells = frozen_cells()
        self.assertEqual(len(cells), 6)
        self.assertEqual(len(set(cells)), 6)
        self.assertEqual(len(ARMS), 3)
        self.assertEqual(len(WORLD_HARMS), 2)
        for cell in cells:
            world, harm, arm, learning, factor = cell
            law = frozen_birth_kwargs(cell)
            self.assertEqual(law["max_steps"], MAX_STEPS)
            self.assertEqual(MAX_STEPS, 128)
            self.assertEqual(law["uc"], 1000)
            self.assertEqual(law["ordinary_food_site"], "camp")
            self.assertEqual(law["second_food_site"], "passage")
            self.assertEqual(law["food_stock"], 1)
            self.assertEqual(law["second_food_stock"], 1)
            self.assertEqual(law["berry_food_gain"], 0.0)
            self.assertEqual(law["second_berry_food_gain"], 20.0)
            self.assertEqual(law["food_restock_every"], 8)
            self.assertEqual(law["second_food_restock_every"], 8)
            self.assertEqual(law["water_restock_every"], 10)
            self.assertEqual(law["ordinary_water_site"], "camp")
            self.assertFalse(law["origin_novelty_tie"])
            self.assertEqual(law["learning"], learning)
            self.assertEqual(law["need_failure_exploration"], factor)
            self.assertEqual(law["second_berry_integrity_delta"], harm)
            self.assertEqual(law["body"].as_dict(),
                             {"energy": 78, "food": 46,
                              "water": 44, "integrity": 94})
            self.assertEqual(law["temperament"].as_dict(), {
                "reward_sensitivity": 0, "threat_sensitivity": .5,
                "exploration": .3, "goal_protection": 0,
                "affiliation": 0,
            })
        self.assertEqual(
            {frozen_birth_kwargs(c)["second_berry_integrity_delta"]
             for c in cells}, {0.0, -12.0})

    def test_undeclared_cell_rejected(self):
        with self.assertRaises(ValueError):
            frozen_birth_kwargs(("favorable", 0, "factor", True, True))

    @patch("tools.i2_p4_origin_failure_study_990.NativePaidI2.create")
    def test_dry_run_refuses_before_birth_or_output(self, birth):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "cohort"
            with self.assertRaisesRegex(ValueError, "explicit"):
                run_study(destination, execute=False, expected_head="0" * 40)
            self.assertFalse(destination.exists())
        birth.assert_not_called()

    @patch("tools.i2_p4_origin_failure_study_990.NativePaidI2.create")
    def test_bad_head_refused_before_birth(self, birth):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "clean source-locked"):
                with patch("tools.i2_p4_origin_failure_study_990._require_exact_clean_checkout",
                           side_effect=ValueError("exact clean source-locked")):
                    run_study(Path(folder) / "study", execute=True,
                              expected_head="1" * 40)
        birth.assert_not_called()

    def test_off_factor_motors_do_not_create_divergence(self):
        arms = [frame("attendre"), frame("attendre")]
        outcome = first_matched_factor_divergence(
            arms, arms, diagnose(1), diagnose(1))
        self.assertEqual(outcome["classification"], "NO_MOTOR_DIVERGENCE")

    def test_genuine_matched_first_divergence_after_failed_food(self):
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage",
                             factor_tagged=True)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_AFTER_MATCHED_FAILURE_WITH_FACTOR_CREDIT")
        self.assertTrue(result["factor_tagged_at_divergence"])
        self.assertEqual(result["first_motor_divergence_tick"], 3)
        self.assertTrue(result["same_prehistory"])

    def test_matched_postfailure_divergence_without_tag_not_credited(self):
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage")]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_AFTER_MATCHED_FAILURE_NO_FACTOR_CREDIT")
        self.assertFalse(result["factor_tagged_at_divergence"])

    def test_pre_failure_divergence_not_credited_to_lived_failure(self):
        common = [frame("attendre")]
        result = first_matched_factor_divergence(
            common + [frame("attendre")],
            common + [frame("se_deplacer_vers_passage")],
            diagnose(), diagnose())
        self.assertEqual(result["classification"],
                         "DIVERGENCE_BEFORE_PERSONAL_DOUBLE_FAILURE")

    def test_different_current_body_prevents_clean_attribution(self):
        off = [frame("manger")] + [
            frame("attendre", before={"energy": 70., "food": 44.,
                                     "water": 42., "integrity": 94.})]
        on = [frame("manger")] + [
            frame("se_deplacer_vers_passage",
                  before={"energy": 69., "food": 43.,
                          "water": 42., "integrity": 94.})]
        result = first_matched_factor_divergence(
            off, on, diagnose(1), diagnose(1))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_WITH_UNMATCHED_HISTORY")
        self.assertFalse(result["same_prehistory"])

    def test_different_lengths_are_not_a_matching_effect(self):
        result = first_matched_factor_divergence(
            [frame("manger")], [frame("manger"), frame("attendre")],
            diagnose(), diagnose())
        self.assertEqual(result["classification"],
                         "DIFFERENT_OBSERVED_LIFE_LENGTHS")


if __name__ == "__main__":
    unittest.main()
