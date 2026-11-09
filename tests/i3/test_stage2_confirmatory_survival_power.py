"""Software-only prospective noninferiority power analysis, no World."""
from math import isnan
import inspect
import unittest

from i3.lab import stage2_confirmatory_survival_power as S


class SurvivalConfirmatoryPowerStudyTests(unittest.TestCase):
    def test_robust_5pp_noninferiority_with_zero_true_effect_is_expensive(self):
        result = S.bounded_power_requirement(
            margin=0.05, assumed_true_delta=0.0)
        self.assertEqual(result["minimum_independent_clusters_for_hoeffding_power_bound"],
                         7198)
        self.assertEqual(result["two_policy_life_ceiling"], 14396)
        self.assertEqual(result["two_policy_horizon_steps_ceiling"], 5758400)
        self.assertFalse(result["independence_proven"])
        self.assertFalse(result["margin_approved"])
        self.assertFalse(result["worlds_authorized"])

    def test_discrete_margin_power_sensitivity(self):
        expected = {
            (0.02, 0.00): 44984,
            (0.02, 0.02): 11246,
            (0.02, 0.05): 3673,
            (0.05, 0.00): 7198,
            (0.05, 0.02): 3673,
            (0.05, 0.05): 1800,
            (0.10, 0.00): 1800,
            (0.10, 0.02): 1250,
            (0.10, 0.05): 800,
        }
        for (margin, true_delta), n in expected.items():
            with self.subTest(margin=margin, true_delta=true_delta):
                z = S.bounded_power_requirement(
                    margin=margin, assumed_true_delta=true_delta)
                self.assertEqual(z["minimum_independent_clusters_for_hoeffding_power_bound"],
                                 n)
        # With eight populations the radius swamps a 5 pp loss margin.
        self.assertAlmostEqual(S.one_sided_bounded_radius(8), 0.8654091913011427)
        self.assertGreater(S.one_sided_bounded_radius(240), 0.05)

    def test_parametric_pair_scenarios_are_explicitly_nonconfirmatory(self):
        for plus, minus, n in (
            (.10, .10, 495), (.15, .15, 742),
            (.30, .30, 1484), (.11, .09, 252),
        ):
            with self.subTest(plus=plus, minus=minus):
                result = S.paired_normal_sensitivity(
                    gate_only_survival=plus, fixed_only_survival=minus,
                    margin=.05)
                self.assertEqual(result["approximate_independent_pairs"], n)
                self.assertEqual(result["status"],
                                 "ILLUSTRATIVE_NORMAL_APPROXIMATION_ONLY")
                self.assertFalse(result["exact_type_i_control_established"])
                self.assertFalse(result["admission_authorized"])
        null = S.paired_normal_sensitivity(
            gate_only_survival=.05, fixed_only_survival=.10, margin=.05)
        self.assertIsNone(null["approximate_independent_pairs"])
        self.assertEqual(null["status"], "UNDER_OR_AT_NULL_UNSUITABLE_FOR_TARGET_POWER")

    def test_no_model_can_silently_inflate_f0_to_independent_populations(self):
        study = S.sensitivity_campaign()
        self.assertEqual(study["f0_candidate_worlds"], 48)
        self.assertEqual(study["f0_candidate_matched_blocks"], 240)
        self.assertEqual(len(study["conservative_fixed_sample_sensitivity"]), 9)
        self.assertEqual(len(study["paired_model_assumption_sensitivity"]), 5)
        self.assertEqual(study["f0_blocks_independent_for_inference"],
                         "NOT_ESTABLISHED")
        self.assertFalse(study["primary_margin_approved"])
        self.assertFalse(study["meaningful_random_sampling_established"])
        self.assertFalse(study["existing_f0_indices_sufficient_for_robust_study"])
        self.assertEqual(study["future_world_exposure"], 0)
        self.assertEqual(study["future_scientific_lives_executed"], 0)
        self.assertEqual(study["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(study["historical_80_81_reused"])
        self.assertEqual(study, S.sensitivity_campaign())
        # This module imports only the F0 metadata generator, not runtime.
        self.assertNotIn("from ..runtime", inspect.getsource(S))
        self.assertNotIn("from i3.runtime", inspect.getsource(S))

    def test_fail_closed_invalid_science_inputs(self):
        errors = [
            lambda: S.bounded_power_requirement(margin=0, assumed_true_delta=0),
            lambda: S.bounded_power_requirement(margin=.05, assumed_true_delta=-.05),
            lambda: S.bounded_power_requirement(margin=.05, assumed_true_delta=-.06),
            lambda: S.bounded_power_requirement(margin=True, assumed_true_delta=0),
            lambda: S.bounded_power_requirement(margin=.05, assumed_true_delta=float("nan")),
            lambda: S.bounded_power_requirement(margin=.05, assumed_true_delta=0, power=1),
            lambda: S.one_sided_bounded_radius(True),
            lambda: S.one_sided_bounded_radius(0),
            lambda: S.one_sided_bounded_radius(8, alpha=float("inf")),
            lambda: S.paired_normal_sensitivity(
                gate_only_survival=.8, fixed_only_survival=.3, margin=.05),
            lambda: S.paired_normal_sensitivity(
                gate_only_survival=-.1, fixed_only_survival=.1, margin=.05),
            lambda: S.paired_normal_sensitivity(
                gate_only_survival=.1, fixed_only_survival=True, margin=.05),
        ]
        for i, failure in enumerate(errors):
            with self.subTest(i=i), self.assertRaises(ValueError):
                failure()


if __name__ == "__main__":
    unittest.main()
