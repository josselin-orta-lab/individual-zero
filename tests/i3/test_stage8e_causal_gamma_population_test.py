"""Synthetic Stage8-E2 Gamma block DID design only. Never a native life."""
from copy import deepcopy
import unittest

from i3.lab import stage8e_causal_gamma_population_test as E


def profiles(contrast=10.):
    return [{
        "population": p,
        "mean_G2_steps": {
            "S_sham": 250. + contrast/2 + (p%3-1),
            "M_sham": 250.,
            "S_swap": 250. - contrast/2,
            "M_swap": 250.,
        },
        "original_lives_by_arm": {arm:144 for arm in E.ARMS},
    } for p in range(E.POPULATIONS)]


class Stage8EGammaBlockCausalDesignPureTests(unittest.TestCase):
    def test_complete_four_arm_64_population_template(self):
        r=E.analyze_design_only(profiles())
        self.assertEqual(r["population_units"],64)
        self.assertEqual(r["g2_native_original_lives_required"],36864)
        self.assertEqual(r["new_lives"],0)
        self.assertFalse(r["scientific_claim_authorized"])
        self.assertEqual(len(r["all_64_population_did"]),64)
        self.assertTrue(r["nominal_design_only_nonzero_compatible"])
        self.assertAlmostEqual(r["primary_gamma_block_did_mean_steps"],10.)

    def test_zero_variance_must_never_get_nominal_success(self):
        p=profiles()
        for row in p:
            row["mean_G2_steps"]["S_sham"]=255.
        r=E.analyze_design_only(p)
        self.assertEqual(r["primary_gamma_block_did_population_sd_steps"],0.)
        self.assertIsNone(r["primary_gamma_block_did_t_statistic"])
        self.assertFalse(r["nominal_design_only_nonzero_compatible"])

    def test_all_zero_contrasts_do_not_succeed(self):
        r=E.analyze_design_only(profiles(0.))
        self.assertFalse(r["nominal_design_only_nonzero_compatible"])

    def test_missing_duplicated_censored_or_nonnumeric_cells_fail_closed(self):
        p=profiles()
        with self.assertRaises(ValueError):
            E.analyze_design_only(p[:-1])
        q=deepcopy(p);q[4]["population"]=3
        with self.assertRaises(ValueError):
            E.analyze_design_only(q)
        q=deepcopy(p);q[4]["original_lives_by_arm"]["M_swap"]=143
        with self.assertRaises(ValueError):
            E.analyze_design_only(q)
        q=deepcopy(p);q[4]["mean_G2_steps"]["M_swap"]=float("nan")
        with self.assertRaises(ValueError):
            E.analyze_design_only(q)
        q=deepcopy(p);q[4]["mean_G2_steps"]["M_swap"]=401.
        with self.assertRaises(ValueError):
            E.analyze_design_only(q)
        q=deepcopy(p);del q[4]["mean_G2_steps"]["M_swap"]
        with self.assertRaises(ValueError):
            E.analyze_design_only(q)

    def test_medianish_null_is_not_misread_as_evidence(self):
        p=profiles(0.5)
        r=E.analyze_design_only(p)
        self.assertFalse(r["scientific_claim_authorized"])
        self.assertEqual(r["design_threshold_two_sided_alpha"],0.025)


if __name__ == "__main__":
    unittest.main()
