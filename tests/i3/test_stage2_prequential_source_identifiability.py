"""Precommitted no-World order source test. No Stage-2 research promotion."""
import json
import math
import unittest
from unittest.mock import patch

from i3.lab import stage2_prequential_source_identifiability as E
from i3.modules.body import CognitiveBudget
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import _ExperiencedEffect
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.world import World


class PrequentialSourceIdentifiabilityTests(unittest.TestCase):
    def test_exact_frozen_source_has_no_world_or_policy_decision(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World")), patch.object(
                              Mind, "decide",
                              side_effect=AssertionError("no native decision")), patch.object(
                                  CognitiveBudget, "try_spend",
                                  side_effect=AssertionError("no paid calculation")):
            report = E.audit()
        print("I3_PREQUENTIAL_SOURCE_IDENTIFIABILITY="+json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False))
        self.assertEqual(report["status"], "SOFTWARE_SOURCE_SEPARABILITY_WITNESS_PASS")
        self.assertEqual(report["new_worlds"], 0)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertFalse(report["actual_optional_cognition_purchased"])
        self.assertFalse(report["real_world_cognitive_debit"])
        self.assertFalse(report["incremental_prospective_predictive_value_demonstrated"])
        self.assertFalse(report["native_motor_mediation_demonstrated"])
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(len(report["deterministic_sha256"]), 64)

    def test_native_mean_and_recent_support_match_but_past_errors_differ(self):
        report = E.audit()
        a,b = report["order_a"],report["order_b"]
        self.assertEqual(a["terminal_model_stats"], b["terminal_model_stats"])
        self.assertEqual(a["terminal_prediction"], b["terminal_prediction"])
        self.assertEqual(a["terminal_exact_count"], 8)
        self.assertEqual(b["terminal_exact_count"], 8)
        self.assertEqual(a["terminal_prediction"][2], 3)
        self.assertEqual(a["terminal_uncertainty"], b["terminal_uncertainty"])
        self.assertEqual(a["last_bounded_effect_support"], b["last_bounded_effect_support"])
        self.assertEqual(a["last_bounded_effect_support"], (4,4,4))
        self.assertEqual(sorted(a["water_effects"]), sorted(b["water_effects"]))
        self.assertGreater(b["total_prequential_five_channel_mse"],
                           a["total_prequential_five_channel_mse"])
        self.assertEqual(E._trace(E.ORDER_A), a)

    def test_actual_bounded_reference_support_operator_agrees_on_synthetic_inputs(self):
        # Internal synthetic source injection, intentionally unpaid and NEVER
        # presented as original first-person World data or a real paid read.
        support=[]
        for history in (E.ORDER_A, E.ORDER_B):
            m=ReferenceBranchMemory()
            for water in history:
                m._samples.append(_ExperiencedEffect(
                    ("boire", None), (0.,0.,float(water),0.,0.)))
            support.append(m._support(("boire", None)))
        self.assertEqual(support[0], support[1])
        self.assertEqual(tuple(x[2] for x in support[0]), (4.,4.,4.))
        self.assertEqual(len(support[0]), 3)

    def test_preoutcome_freeze_and_first_unseen_are_explicit(self):
        a,b=E.audit()["order_a"],E.audit()["order_b"]
        for row in (a,b):
            for i,item in enumerate(row["events"]):
                self.assertEqual(item["step"], i+1)
                self.assertEqual(item["previous_exact_count"], i)
                self.assertAlmostEqual(item["native_preoutcome_uncertainty"],
                                       1/math.sqrt(1+i))
                expected=(sum(row["water_effects"][:i])/i if i else 0.)
                self.assertAlmostEqual(
                    item["native_preoutcome_forecast"][2], expected)
                self.assertEqual(item["lived_outcome_delta"][2],
                                 row["water_effects"][i])
                self.assertGreaterEqual(item["prequential_five_channel_mse"], 0.)
        self.assertEqual(a["events"][0]["previous_exact_count"], 0)
        self.assertNotEqual(a["events"][0]["lived_outcome_delta"],
                            b["events"][0]["lived_outcome_delta"])

    def test_frozen_design_and_invalid_inputs_fail_closed(self):
        for invalid in ((0,)*7, [0]*8, (False,)*8,
                        (float("nan"),)+(0,)*7,
                        (float("inf"),)+(0,)*7):
            with self.subTest(value=str(invalid)), self.assertRaises(ValueError):
                E._trace(invalid)
        with patch.object(E, "ORDER_B", (8,0,0,0,4,4,4,5)):
            with self.assertRaisesRegex(ValueError, "frozen preflight"):
                E.audit()
        with patch.object(E, "WINDOW", 4):
            with self.assertRaisesRegex(ValueError, "bounded branch"):
                E.audit()

    def test_deterministic_same_input_and_no_new_originals(self):
        a,b=E.audit(),E.audit()
        self.assertEqual(a,b)
        self.assertEqual(E.ORDER_A, (0,0,0,8,4,4,4,4))
        self.assertEqual(E.ORDER_B, (8,0,0,0,4,4,4,4))


if __name__ == "__main__":
    unittest.main()
