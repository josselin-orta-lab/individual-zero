"""Observed paid re-exposure, not an injected hidden-world prediction."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.restoration_reexposure_composition import run_restoration_reexposure

class RestorationCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_restoration_reexposure()

    def test_three_policies_are_audited_in_both_hidden_worlds(self):
        self.assertFalse(self.result["m11_authenticated"])
        self.assertFalse(self.result["independent_scientific_replication"])
        self.assertEqual(self.result["natural_learning"], "NOT_ESTABLISHED")
        for case in self.result["worlds"].values():
            self.assertEqual(set(case["arms"]),
                             {"observational","last_resort","combined"})
            for arm in case["arms"].values():
                self.assertGreater(arm["paid_uc"],0)
                self.assertEqual(arm["endpoint"]["actual_uc_spent"],arm["paid_uc"])
                for contact in arm["contacts"]:
                    self.assertGreaterEqual(contact["tick"],7)
                    self.assertTrue(contact["prior_personal_eat_nets"])
            for contrast in case["first_divergence_from_observational"].values():
                self.assertTrue(contrast["not_a_natural_learning_or_survival_verdict"])

    def test_contact_after_restoration_is_observed_not_predicted(self):
        restored = self.result["worlds"]["hidden_restoration"]["arms"]
        adverse = self.result["worlds"]["persistent_adversity"]["arms"]
        self.assertEqual(restored["observational"]["contacts"],[])
        self.assertTrue(restored["last_resort"]["contacts"])
        self.assertTrue(restored["combined"]["contacts"])
        for name in ("last_resort","combined"):
            rc=restored[name]["contacts"][0]
            ac=adverse[name]["contacts"][0]
            self.assertTrue(any(n<0 for n in rc["prior_personal_eat_nets"]))
            self.assertEqual(rc["tick"],ac["tick"])
            self.assertGreater(rc["net"],0)
            self.assertLess(ac["net"],0)

    def test_emergency_contact_is_last_paid_window_not_learned_recovery(self):
        restored=self.result["worlds"]["hidden_restoration"]
        adverse=self.result["worlds"]["persistent_adversity"]
        for name in ("last_resort","combined"):
            positive=restored["arms"][name]
            negative=adverse["arms"][name]
            self.assertEqual(positive["endpoint"]["paid_decisions"],8)
            self.assertEqual(negative["endpoint"]["paid_decisions"],8)
            self.assertEqual(positive["contacts"][0]["tick"],16)
            self.assertEqual(negative["contacts"][0]["tick"],16)
            self.assertFalse(positive["contacts"][0]["later_personally_observed"])
            self.assertFalse(negative["contacts"][0]["later_personally_observed"])
            self.assertEqual(positive["contacts"][0]["prior_personal_eat_nets"],[-10])
            self.assertEqual(negative["contacts"][0]["prior_personal_eat_nets"],[-10])
            self.assertEqual(positive["paid_uc"],negative["paid_uc"])
            # No distinguishable response to the new food outcome was
            # observable before the fixed eight-decision horizon ended.
            self.assertEqual(
                restored["first_divergence_from_observational"][name]
                    ["first_divergence_seq"],8)
            self.assertTrue(
                restored["first_divergence_from_observational"][name]
                    ["matched_prechoice"])
        self.assertEqual(
            restored["arms"]["combined"]["endpoint"],
            restored["arms"]["last_resort"]["endpoint"])
        self.assertEqual(
            restored["arms"]["combined"]["contacts"],
            restored["arms"]["last_resort"]["contacts"])

    def test_report_source_for_scientific_review(self):
        print("I2_RESTORATION_REEXPOSURE_COMPOSITION_V1="+json.dumps(
            self.result,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
