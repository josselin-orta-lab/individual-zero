"""Blind restoration is an information-limit test, not exploration tuning."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.runtime.blind_restoration_probe import (
    CHANGE_START_TICK, INITIAL_ENERGY, INITIAL_RESOURCES, INITIAL_UC,
    LOCKED_ENVIRONMENTS, PROTOCOL_ID, TICK_HORIZON,
    run_blind_restoration_probe,
)
from i2.runtime.isolated_prototype import (
    EAT, SCENARIOS, PrototypeRefusal, demo,
)


class BlindRestorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One tiny cached run across all tests, not separate replications.
        cls.report = run_blind_restoration_probe()

    def test_lock_and_unmodified_existing_controls(self):
        self.assertEqual(self.report["protocol_id"], PROTOCOL_ID)
        self.assertEqual(
            self.report["locked_worlds"],
            [list(x) for x in LOCKED_ENVIRONMENTS])
        self.assertEqual(
            (TICK_HORIZON, INITIAL_UC, INITIAL_ENERGY, INITIAL_RESOURCES),
            (16, 60, 40, 8))
        self.assertEqual(CHANGE_START_TICK, 7)
        self.assertEqual(SCENARIOS["restoration"][:3],
                         SCENARIOS["adverse"][:3])
        self.assertEqual(SCENARIOS["restoration"][3:], (6,) * 5)
        self.assertEqual(self.report["natural_learning"], "NOT_ESTABLISHED")
        self.assertTrue(self.report["no_exploration_bonus_or_oracle"])
        self.assertFalse(self.report["authenticated_m11"])

    def test_hidden_restoration_is_not_detected_without_food_reexposure(self):
        restored = self.report["runs"]["hidden_restoration"]["observational"]
        persistent = self.report["runs"]["persistent_adversity"]["observational"]
        self.assertTrue(
            self.report["same_observational_subject_history_across_hidden_worlds"])
        self.assertEqual(
            self.report["interpretation"],
            "HIDDEN_CHANGE_UNIDENTIFIABLE_WITHOUT_REEXPOSURE")
        self.assertEqual(restored["choices"], persistent["choices"])
        self.assertEqual(restored["post_change_food_contacts"], [])
        self.assertIsNone(restored["first_positive_food_contact_tick"])
        self.assertFalse(restored["positive_contact_available_in_later_capture"])
        self.assertEqual(restored["death_tick"], persistent["death_tick"])
        # The last recorded negative EAT is the only experienced food value.
        later = [d for d in restored["choices"] if d["tick"] >= CHANGE_START_TICK]
        self.assertTrue(later)
        self.assertTrue(all(d["action"] != EAT for d in later))
        self.assertTrue(all(d["eat_score"] == -5 for d in later))

    def test_fixed_arm_recontacts_and_experiences_hidden_recovery(self):
        restored = self.report["runs"]["hidden_restoration"]["no_learning"]
        self.assertEqual(restored["first_post_change_food_contact_tick"], 8)
        self.assertEqual(restored["first_positive_food_contact_tick"], 8)
        self.assertTrue(restored["positive_contact_available_in_later_capture"])
        self.assertTrue(
            all(d["eat_score"] == 4 for d in restored["choices"]
                if d["eat_score"] is not None))
        self.assertTrue(any(
            4 in d["previously_experienced_eat_results"]
            for d in restored["choices"] if d["tick"] > 8))
        self.assertIsNone(restored["death_tick"])

    def test_negative_viability_and_full_uc_reporting(self):
        restored = self.report["runs"]["hidden_restoration"]
        learned, fixed = restored["observational"], restored["no_learning"]
        self.assertEqual(learned["death_tick"], 16)
        self.assertTrue(fixed["censored"])
        self.assertGreater(fixed["ending_energy"], learned["ending_energy"])
        self.assertGreater(learned["actual_uc_spent"], 0)
        self.assertGreater(fixed["actual_uc_spent"], 0)
        self.assertEqual(learned["paid_decisions"], 8)
        self.assertEqual(fixed["paid_decisions"], 8)
        self.assertEqual(
            self.report["scientific_verdict"],
            "MODEL_SPECIFIC_NEGATIVE_OR_INCONCLUSIVE")

    def test_direct_no_clock_demo_cannot_claim_hidden_reversal(self):
        with self.assertRaisesRegex(PrototypeRefusal, "requires physical world ticks"):
            demo("restoration", steps=6)

    def test_single_source_pinned_machine_readout(self):
        # Reuse the same cached execution above. Never select a favorable
        # run or accidentally count two Python versions as replicates.
        print("I2_BLIND_RESTORATION_V1_RESULTS=" + json.dumps(
            self.report, separators=(",", ":"), sort_keys=True),
            flush=True)
        self.assertEqual(len(self.report["runs"]), 2)


if __name__ == "__main__":
    unittest.main()
