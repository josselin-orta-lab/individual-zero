"""Executable exact paired *computational* survival study: no Worlds."""
from math import comb, factorial, fsum
import inspect
import unittest

from i3.lab import stage2_exact_paired_survival as P


class ExactPairedSurvivalTests(unittest.TestCase):
    def test_binomial_tails_match_direct_small_enumeration(self):
        for n in range(1, 10):
            for p in (.01, .10, .50, .90, .99):
                for k in range(n + 1):
                    low = fsum(comb(n, j) * p**j * (1-p)**(n-j)
                               for j in range(k + 1))
                    high = fsum(comb(n, j) * p**j * (1-p)**(n-j)
                                for j in range(k, n + 1))
                    with self.subTest(n=n, p=p, k=k):
                        self.assertAlmostEqual(P._binomial_tail(n, k, p, False), low,
                                               places=11)
                        self.assertAlmostEqual(P._binomial_tail(n, k, p, True), high,
                                               places=11)

    def test_clopper_pearson_closed_form_boundary_examples(self):
        result = P.exact_paired_lower_bound(
            pairs=1, gate_only=1, fixed_only=0)
        self.assertAlmostEqual(result["gate_only_probability_lower_cp"], .025)
        self.assertAlmostEqual(result["fixed_only_probability_upper_cp"], .975)
        self.assertAlmostEqual(result["simultaneous_one_sided_lower_bound"], -.95)
        self.assertFalse(result["independent_target_world_sampling_verified"])
        self.assertFalse(result["owner_authorization_inferred"])
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")

    def test_iid_pair_coverage_on_complete_small_multinomial_grids(self):
        # An independent exact enumeration of *all* n=20 outcome counts.
        # Pair-outcome dependence is intrinsic; no independence of GATE
        # and FIXED within a block is assumed in the procedure.
        n = 20
        alpha = .20
        for plus, minus in ((0., .1), (.05, .05), (.15, .25),
                            (.25, .35), (.4, .4), (.0, .6)):
            p_zero = 1 - plus - minus
            false_exclusions = 0.0
            true_diff = plus - minus
            for g in range(n + 1):
                for f in range(n - g + 1):
                    z = n - g - f
                    weight = (factorial(n) / (factorial(g) * factorial(f) *
                                              factorial(z)) *
                              plus**g * minus**f * p_zero**z)
                    low = P.exact_paired_lower_bound(
                        pairs=n, gate_only=g, fixed_only=f,
                        alpha=alpha)["simultaneous_one_sided_lower_bound"]
                    if low > true_diff + 1e-13:
                        false_exclusions += weight
            with self.subTest(plus=plus, minus=minus):
                self.assertLessEqual(false_exclusions, alpha + 1e-10)

    def test_unselected_paired_counts_not_fabricated(self):
        for g, f in ((0, 0), (0, 100), (100, 0), (100, 100), (400, 500)):
            z = P.exact_paired_lower_bound(pairs=1000, gate_only=g,
                                            fixed_only=f)
            self.assertEqual(z["both_or_neither_survive"], 1000 - g - f)
            self.assertEqual(z["observed_paired_risk_difference"], (g-f)/1000)
            self.assertLessEqual(z["simultaneous_one_sided_lower_bound"],
                                 z["observed_paired_risk_difference"] + 1e-12)
            self.assertFalse(z["owner_authorization_inferred"])

    def test_calibration_is_conditionally_reproducible_no_scientific_observation(self):
        args = dict(pairs=128, gate_only_probability=.1,
                    fixed_only_probability=.1, trials=32, seed=12345)
        a = P.simulate_conditional_rejection(**args)
        self.assertEqual(a, P.simulate_conditional_rejection(**args))
        self.assertTrue(0 <= a["conditional_rejection_fraction"] <= 1)
        self.assertEqual(a["power_or_size_interpretation"], "POWER_SENSITIVITY")
        self.assertFalse(a["exact_coverage_experimentally_proven"])
        self.assertEqual(a["scientific_lives"], 0)
        self.assertEqual(a["worlds_opened"], 0)
        b = P.simulate_conditional_rejection(
            pairs=128, gate_only_probability=.05,
            fixed_only_probability=.10, trials=32, seed=12345)
        self.assertEqual(b["power_or_size_interpretation"], "NULL_SIZE_DIAGNOSTIC")
        self.assertEqual(b["hypothetical_true_mean_difference"], -.05)

    def test_strict_input_validation_and_no_runtime_import(self):
        invalid = [
            lambda: P.exact_paired_lower_bound(pairs=True, gate_only=0, fixed_only=0),
            lambda: P.exact_paired_lower_bound(pairs=0, gate_only=0, fixed_only=0),
            lambda: P.exact_paired_lower_bound(pairs=3, gate_only=2, fixed_only=2),
            lambda: P.exact_paired_lower_bound(pairs=3, gate_only=-1, fixed_only=0),
            lambda: P.exact_paired_lower_bound(pairs=3, gate_only=1, fixed_only=True),
            lambda: P.exact_paired_lower_bound(pairs=3, gate_only=1, fixed_only=0,
                                                alpha=float("nan")),
            lambda: P.simulate_conditional_rejection(pairs=100,
                    gate_only_probability=.9, fixed_only_probability=.2),
            lambda: P.simulate_conditional_rejection(pairs=100,
                    gate_only_probability=.1, fixed_only_probability=.1,
                    trials=0),
            lambda: P.simulate_conditional_rejection(pairs=100,
                    gate_only_probability=.1, fixed_only_probability=.1,
                    trials=10001),
            lambda: P.simulate_conditional_rejection(pairs=100,
                    gate_only_probability=.1, fixed_only_probability=.1,
                    seed=True),
            lambda: P.simulate_conditional_rejection(pairs=100,
                    gate_only_probability=.1, fixed_only_probability=.1,
                    margin=0),
        ]
        for idx, bad in enumerate(invalid):
            with self.subTest(i=idx), self.assertRaises(ValueError):
                bad()
        source = inspect.getsource(P)
        self.assertNotIn("from i3.runtime", source)
        self.assertNotIn("from ..runtime", source)
        self.assertNotIn("run_life(", source)


if __name__ == "__main__":
    unittest.main()
