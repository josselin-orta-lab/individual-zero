"""Software-only proposed selected Stage-2.1 gate; no new lives."""
from copy import deepcopy
import unittest
from i3.lab import stage0_design as F0
from i3.lab import stage2_gate_design as G


class SelectedGateDesignTests(unittest.TestCase):
    def test_f0_structure_and_cost_ceiling(self):
        d = G.design()
        self.assertFalse(d["execution_authorized"])
        self.assertFalse(d["scientific_gate_authorized"])
        self.assertEqual(d["population_count"], 8)
        self.assertEqual(d["founder_seeds"], F0.manifest()["founder_seeds"])
        self.assertEqual(len(d["selection_worlds"]), 48)
        self.assertEqual(len(d["validation_worlds"]), 48)
        self.assertEqual({r["world_seed"] for r in d["selection_worlds"]},
                         set(range(10072, 10120)))
        self.assertEqual({r["world_seed"] for r in d["validation_worlds"]},
                         set(range(30120, 30168)))
        self.assertEqual(len(d["validation_conditions"]), 5)
        self.assertEqual((d["selection_lives_ceiling"], d["validation_lives_ceiling"],
                          d["total_lives_ceiling"], d["lived_steps_ceiling"]),
                         (3840, 1200, 5040, 2016000))
        self.assertEqual(d["random_mean_exact"], [5532, 867])
        self.assertEqual(d, G.design())

    def test_collision_detection(self):
        for seed in (10072, 30167):
            with self.subTest(seed=seed), self.assertRaisesRegex(ValueError, "occupied"):
                G.design([seed])

    def test_exact_sign_boundaries_and_ties(self):
        success = {p: 0.2 if p < 7 else -0.2 for p in range(8)}
        r = G._population_sign_test(success)
        self.assertEqual((r["wins"], r["losses"], r["ties"]), (7, 1, 0))
        self.assertEqual(r["p_one_sided"], 9 / 256)
        self.assertTrue(r["directional_pass"])
        tied = G._population_sign_test({p: (0.0 if p == 0 else success[p]) for p in range(8)})
        self.assertEqual(tied["effective_n"], 7)
        self.assertFalse(tied["directional_pass"])
        self.assertEqual(G._population_sign_test({p: 0 for p in range(8)})["p_one_sided"], 1)

    def test_joint_gate_is_not_scientific_adoption(self):
        data = {
            "cognitive_energy_per_lived_step": {p: -0.1 for p in range(8)},
            "cognitive_vigilance_per_lived_step": {p: -0.1 for p in range(8)},
            "survival_at_400": {p: 0.0 for p in range(8)},
            "inactive_step_fraction": {p: 0.0 for p in range(8)},
        }
        r = G.directional_gate(data)
        self.assertTrue(r["all_directional_tests_pass"])
        self.assertEqual(r["status"], "ARITHMETIC_ONLY_NOT_A_SCIENTIFIC_VERDICT")
        adverse = deepcopy(data)
        adverse["survival_at_400"] = {p: -0.06 for p in range(8)}
        self.assertFalse(G.directional_gate(adverse)["all_directional_tests_pass"])
        adverse["survival_at_400"] = {p: -0.05 for p in range(8)}
        self.assertFalse(G.directional_gate(adverse)["all_directional_tests_pass"])

    def test_missing_or_pseudoreplicated_data_rejected(self):
        for invalid in ({0: -1}, {p: True for p in range(8)},
                        {p: float("nan") for p in range(8)},
                        {p: [1, 2] for p in range(8)}):
            with self.subTest(invalid=str(invalid)), self.assertRaises(ValueError):
                G._population_sign_test(invalid)


if __name__ == "__main__":
    unittest.main()
