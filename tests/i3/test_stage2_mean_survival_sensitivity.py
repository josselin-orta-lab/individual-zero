"""Pure Stage-2.1 mean-survival sensitivity tests; NEVER open a World."""
import math
import unittest

from i3.lab import stage2_mean_survival_sensitivity as S


class MeanSurvivalSensitivity(unittest.TestCase):
    def test_independent_population_bound_has_correct_range(self):
        r = S.mean_survival_lower_bound({i: 0.5 for i in range(8)})
        expected = math.sqrt(2 * math.log(20) / 8)
        self.assertAlmostEqual(r["observed_population_mean"], 0.5)
        self.assertAlmostEqual(r["radius"], expected)
        self.assertAlmostEqual(r["lower_bound"], 0.5 - expected)
        self.assertFalse(r["mean_noninferiority_authorized"])
        self.assertFalse(r["scientific_worlds_authorized"])
        self.assertEqual(r["status"], "ARITHMETIC_ONLY_NO_SCIENTIFIC_VERDICT")

    def test_adverse_mean_not_masked_by_seven_favorable_signs(self):
        contrasts = {i: (-1 / 30 if i < 7 else -1) for i in range(8)}
        r = S.mean_survival_lower_bound(contrasts)
        self.assertAlmostEqual(r["observed_population_mean"], -37 / 240)
        self.assertEqual(r["lower_bound"], -1.0)
        self.assertFalse(r["mean_noninferiority_authorized"])

    def test_all_favorable_is_still_not_an_approval(self):
        r = S.mean_survival_lower_bound({i: 1.0 for i in range(8)})
        self.assertGreater(r["lower_bound"], -0.05)
        self.assertFalse(r["mean_noninferiority_authorized"])

    def test_conservative_precision_cost_is_not_power(self):
        self.assertEqual(S.hypothetical_minimum_populations(0.05), 2397)
        self.assertEqual(S.hypothetical_minimum_populations(0.1), 600)
        self.assertGreater(S.hypothetical_minimum_populations(0.025),
                           S.hypothetical_minimum_populations(0.05))

    def test_incomplete_nan_out_of_range_and_pseudoreplication_fail_closed(self):
        good = {i: 0.0 for i in range(8)}
        for bad in (
            {0: 0.0}, {**good, 8: 0.0}, {**good, 0: float("nan")},
            {**good, 0: float("inf")}, {**good, 0: -1.01},
            {**good, 0: True}, {**good, 0: [0.0]}, {**good, 0: "0.0"},
            {**good, 0: None},
        ):
            with self.subTest(bad=str(bad)), self.assertRaises(ValueError):
                S.mean_survival_lower_bound(bad)

    def test_alpha_and_precision_validated(self):
        data = {i: 0.0 for i in range(8)}
        for bad in (0, 1, -0.05, 1.05, True, None, float("nan"), float("inf"), "0.05"):
            with self.subTest(alpha=bad), self.assertRaises(ValueError):
                S.mean_survival_lower_bound(data, alpha=bad)
            with self.subTest(precision=bad), self.assertRaises(ValueError):
                S.hypothetical_minimum_populations(bad)


if __name__ == "__main__":
    unittest.main()
