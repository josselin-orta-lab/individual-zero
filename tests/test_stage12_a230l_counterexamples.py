"""A2.30-L adversarial evidence: same perceptions need not imply same outcome."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_b_a230l_counterexamples import (
    run_physical_counterexamples,
)


class ControlledPhysicalAliasingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_physical_counterexamples()

    def test_hidden_lethal_transition_same_visible_input(self):
        row = self.result["hidden_lethal_movement"]
        self.assertTrue(row["identical_accessible_input"])
        self.assertTrue(row["distinct_physical_consequences"])
        self.assertFalse(row["left_terminal"])
        self.assertTrue(row["right_terminal"])
        self.assertTrue(row["trainer_rejected_conflicting_outcomes"])

    def test_same_berry_a_visible_before_ingestion_but_toxic_effect_differs(self):
        row = self.result["hidden_toxic_ingestion"]
        self.assertTrue(row["identical_accessible_input"])
        self.assertEqual(row["same_visible_berry_species"], "berry_a")
        self.assertEqual(row["food_after_pair"][0], row["food_after_pair"][1])
        self.assertGreater(
            row["integrity_after_pair"][0],
            row["integrity_after_pair"][1],
        )
        self.assertTrue(row["trainer_rejected_conflicting_outcomes"])

    def test_visible_food_is_not_safe_to_drop_for_absolute_predictions(self):
        row = self.result["observable_food_difference"]
        self.assertEqual(row["difference_in_accessible_input"], "body.food")
        self.assertTrue(row["all_other_accessible_input_fields_equal"])
        self.assertNotEqual(*row["food_after"])

    def test_fixture_never_construction_of_stage4_i0_runtime(self):
        script = (Path(__file__).resolve().parents[1]
                  / "scripts" / "run_stage12_issue110_b_a230l_counterexamples.py")
        content = script.read_text()
        self.assertNotIn("build_stage4_reference_runtime", content)
        self.assertNotIn("Stage4Runtime(", content)

    def test_no_training_uses_i0_life_or_oracle_and_steps_not_double_counted(self):
        row = self.result
        self.assertEqual(row["physical_lab_worlds"], 6)
        self.assertEqual(row["physically_applied_lab_steps"], 8)
        self.assertEqual(row["new_individual_zero_births"], 0)
        self.assertEqual(row["new_i0_autonomous_steps"], 0)
        self.assertFalse(row["oracle_to_i0_feedback"])
        self.assertFalse(row["generalization_of_safety_proven"])


if __name__ == "__main__":
    unittest.main()
