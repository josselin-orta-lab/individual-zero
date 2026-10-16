"""A2.30-S negative controls: only living Stage3 observations inform knowledge."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_b_a230s_observable_probes import (
    single_world, study, mutually_available_first_difference,
)


class ObservableHazardProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="a230s-unit-")
        cls.output = Path(cls.temp.name) / "study"
        cls.summary = study(cls.output)
        cls.worlds = json.loads((cls.output / "a230s-worlds.json").read_text())
        cls.pairs = json.loads((cls.output / "a230s-pairs.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_physical_world_counts_and_mortality(self):
        self.assertEqual(len(self.worlds), 36)
        self.assertEqual(len({x["id"] for x in self.worlds}), 36)
        self.assertEqual(self.summary["physical_lab_steps"], 104)
        self.assertEqual(self.summary["external_terminals"], 8)
        self.assertEqual(self.summary["steps_per_family"],
                         {"FOOD": 36, "MOVE": 32, "DECAY": 36})
        self.assertFalse(self.summary["uc_cost_evaluated"])
        self.assertEqual(self.summary["new_i0_births"], 0)
        self.assertEqual(self.summary["new_i0_autonomous_steps"], 0)

    def test_food_collection_and_waiting_cannot_reveal_hidden_toxin(self):
        food = [p for p in self.pairs if p["family"] == "FOOD"]
        self.assertEqual(len(food), 12)
        self.assertEqual(
            sum(p["first_mutually_lived_difference"] == 3 for p in food), 4
        )
        self.assertEqual(
            sum(p["first_mutually_lived_difference"] is None for p in food), 8
        )
        self.assertTrue(all(not p["discrimination_before_exposure"]
                            for p in food))
        lethal = [
            x for x in self.worlds
            if x["family"] == "FOOD"
            and x["variant_external_only"] == "toxin_100"
        ]
        self.assertEqual(len(lethal), 4)
        self.assertTrue(all(x["terminal_step_external_only"] == 3 for x in lethal))
        self.assertTrue(all(len(x["possible_lived_captures"]) == 3
                            for x in lethal))  # initial, after wait, after collect

    def test_movement_exposure_precedes_damage_information_or_death(self):
        moves = [p for p in self.pairs if p["family"] == "MOVE"]
        self.assertEqual(
            sum(p["first_mutually_lived_difference"] == 2 for p in moves), 4
        )
        self.assertEqual(
            sum(p["first_mutually_lived_difference"] is None for p in moves), 8
        )
        self.assertTrue(all(not p["discrimination_before_exposure"]
                            for p in moves))
        lethal = [x for x in self.worlds
                  if x["family"] == "MOVE" and
                  x["variant_external_only"] == "lethal_east"]
        self.assertEqual(len(lethal), 4)
        self.assertTrue(all(x["terminal_step_external_only"] == 2 for x in lethal))
        self.assertTrue(all(len(x["possible_lived_captures"]) == 2
                            for x in lethal))

    def test_bodily_decay_accessible_on_first_safe_wait(self):
        decay = [p for p in self.pairs if p["family"] == "DECAY"]
        self.assertEqual(len(decay), 12)
        self.assertTrue(all(p["first_mutually_lived_difference"] == 1
                            for p in decay))
        self.assertTrue(all(x["terminal_step_external_only"] is None
                            for x in self.worlds if x["family"] == "DECAY"))

    def test_no_postmortem_observation_is_counted_as_lived(self):
        for row in self.worlds:
            self.assertEqual(row["postterminal_lived_capture_count"], 0)
            self.assertEqual(
                len(row["external_physical_evidence"]),
                row["steps_applied"]
            )
            if row["terminal_step_external_only"] is not None:
                self.assertEqual(
                    len(row["possible_lived_captures"]),
                    row["terminal_step_external_only"]
                )
                self.assertTrue(
                    row["external_physical_evidence"][-1]
                    ["terminal_for_external_audit_only"]
                )
            else:
                self.assertEqual(len(row["possible_lived_captures"]), 4)

    def test_first_person_compare_ignores_external_terminal_effect(self):
        benign = single_world("FOOD", "benign", 35.0, (5,5))
        fatal = single_world("FOOD", "toxin_100", 35.0, (5,5))
        self.assertIsNone(mutually_available_first_difference(benign, fatal))
        self.assertNotEqual(
            benign["external_physical_evidence"][-1]
            ["after_for_external_audit_only"]["body"]["integrity"],
            fatal["external_physical_evidence"][-1]
            ["after_for_external_audit_only"]["body"]["integrity"],
        )

    def test_no_oracle_or_omniscient_capture_in_probe_observation(self):
        path = (Path(__file__).resolve().parents[1] / "scripts"
                / "run_stage12_issue110_b_a230s_observable_probes.py")
        source = path.read_text()
        self.assertNotIn(".ground_truth(", source)
        self.assertNotIn("Stage4Runtime(", source)
        self.assertNotIn("stage12_outcome_responsibility_judgement", source)
        self.assertNotIn("from lab.oracle", source.lower())


if __name__ == "__main__":
    unittest.main()
