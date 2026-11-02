"""Lock adverse outcomes and effective environmental sample in seeded panel.

Single cached panel run. These are descriptive toy-world observations,
not an estimate of independent-population survival probability.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.seeded_varying_world_panel import SEEDS, POLICIES, run_panel


class SeededPanelNegativeOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = run_panel()

    def test_actual_endpoint_matrix_preserves_fatal_counterexamples(self):
        expected_alive = {
            "observational": set(),
            "deadline": set(),
            "last_resort": {211, 307},
            "combined": {211, 307},
        }
        for name, *_ in POLICIES:
            observed_alive = {
                seed for seed in SEEDS
                if not self.panel["results"][str(seed)]["arms"][name][
                    "endpoint"]["modeled_terminal_observed"]
            }
            self.assertEqual(observed_alive, expected_alive[name])
        for seed in SEEDS:
            arms = self.panel["results"][str(seed)]["arms"]
            for label, arm in arms.items():
                with self.subTest(seed=seed, label=label):
                    self.assertEqual(arm["endpoint"]["actual_uc_spent"], 38)
                    self.assertEqual(arm["endpoint"]["ending_physical_tick"], 16)
                    if seed in (211, 307) and label in ("last_resort", "combined"):
                        self.assertEqual(arm["endpoint"]["ending_energy"], 6)
                        self.assertTrue(arm["endpoint"]["right_censored"])
                    else:
                        self.assertEqual(arm["endpoint"]["ending_energy"], 0)
                        self.assertEqual(arm["endpoint"]["modeled_death_tick"], 16)

    def test_deduplicated_environments_do_not_imply_combination_benefit(self):
        panel = self.panel
        self.assertEqual(panel["distinct_world_count"], 4)
        self.assertEqual(panel["distinct_exposed_world_count"], 4)
        self.assertEqual(
            {tuple(g["seeds"]) for g in panel["seeded_world_groups_researcher_only"]},
            {(101,), (211, 307), (401,), (503,)},
        )
        for seed in SEEDS:
            arms = panel["results"][str(seed)]["arms"]
            for field in ("actions", "decision_ticks", "audit_uc"):
                self.assertEqual(arms["last_resort"][field], arms["combined"][field])
            self.assertEqual(
                arms["last_resort"]["endpoint"],
                arms["combined"]["endpoint"],
            )
            self.assertEqual(arms["last_resort"]["last_resort_raises"], 1)
            self.assertEqual(arms["combined"]["last_resort_raises"], 1)
            self.assertEqual(arms["combined"]["deadline_suppressions"], 1)
            self.assertEqual(arms["observational"]["last_resort_raises"], 0)
            self.assertEqual(arms["deadline"]["last_resort_raises"], 0)
        self.assertEqual(panel["generalized_survival_benefit"], "NOT_ESTABLISHED")
        self.assertEqual(panel["natural_learning"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
