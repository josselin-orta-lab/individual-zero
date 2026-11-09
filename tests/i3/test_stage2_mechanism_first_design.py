"""No World or scientific exposure: synthetic paired G0 design/contrast checks."""
from copy import deepcopy
import unittest

from i3.lab import stage0_design as F0
from i3.lab import stage2_mechanism_first_design as M


def synthetic_rows():
    result = []
    for (p, index, seed, arm), world in M.expected_cells().items():
        result.append({
            "population": p, "world_index": index, "genome_seed": seed,
            "arm": arm, "family": world["family"],
            "world_seed": world["world_seed"], "life_seed": world["life_seed"],
            "terminal": "censored", "steps_lived": 400,
            "energy_paid": 100.0 if arm == "FIXED_G0" else 50.0,
            "vigilance_paid": 40.0 if arm == "FIXED_G0" else 30.0,
            "inactive_steps": 50,
        })
    return result


class MechanismFirstDesignTests(unittest.TestCase):
    def test_exact_unopened_budget_and_fixed_genetic_sampling(self):
        d = M.proposal()
        self.assertEqual(d["proposed_lives"], 720)
        self.assertEqual(d["proposed_horizon_steps_ceiling"], 288000)
        self.assertEqual(d["selection_worlds_used"], 0)
        self.assertEqual(d["worlds_opened"], 0)
        self.assertFalse(d["execution_authorized"])
        self.assertFalse(d["scientific_gate_authorized"])
        self.assertFalse(d["survival_noninferiority_certified"])
        self.assertEqual(len(d["worlds"]), 48)
        self.assertEqual(M.proposal(), d)
        for p in range(8):
            self.assertEqual(M.fixed_founders(p),
                             tuple(F0.founder_seed(p, i) for i in range(5)))
        self.assertEqual(len(M.expected_cells()), 720)
        with self.assertRaisesRegex(ValueError, "occupied"):
            M.proposal([30120])

    def test_complete_matched_panel_describes_mechanism_without_approval(self):
        report = M.descriptive_readout(synthetic_rows())
        self.assertEqual(report["record_count"], 720)
        self.assertEqual(report["paired_blocks"], 240)
        self.assertFalse(report["selection_effect_tested"])
        self.assertFalse(report["survival_noninferiority_certified"])
        self.assertEqual(report["actual_original_custody"], "NOT_AUTHENTICATED")
        self.assertEqual(report["equal_population_mean_contrasts"]
                         ["GATE_minus_FIXED"]["energy_paid_per_assigned_life"], -50)
        self.assertEqual(report["equal_population_mean_contrasts"]
                         ["GATE_minus_FIXED"]["lived_steps"], 0)
        self.assertEqual(report["equal_population_mean_contrasts"]
                         ["GATE_minus_RANDOM"]["energy_paid_per_assigned_life"], 0)
        self.assertEqual(len(report["by_family"]), 3)
        profile = report["paired_outcome_profile"]
        self.assertEqual(profile["paired_blocks_per_contrast"], 240)
        self.assertFalse(profile["survival_noninferiority_certified"])
        self.assertEqual(profile["overall"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["both_survived"], 240)
        self.assertEqual(profile["overall"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["comparator_only_survived"], 0)
        self.assertEqual(profile["overall"]["GATE_minus_RANDOM"]
                         ["lived_steps_direction"]["equal"], 240)
        self.assertEqual(profile["overall"]["GATE_minus_FIXED"]
                         ["lower_paid_energy_but_shorter_life"], 0)
        for family in F0.FAMILIES:
            self.assertEqual(profile["by_family"][family]["GATE_minus_FIXED"]
                             ["paired_blocks"], 80)
        for p in range(F0.POPULATIONS):
            self.assertEqual(profile["by_population"][p]["GATE_minus_FIXED"]
                             ["paired_blocks"], 30)
        for p in range(8):
            self.assertEqual(report["by_population"][p]["GATE_minus_FIXED"]
                             ["survival_at_400"], 0)

    def test_adverse_deaths_remain_visible_despite_lower_paid_cognition(self):
        rows = synthetic_rows()
        for row in rows:
            if row["family"] == "stable" and row["arm"] == "GATE_G0":
                row["terminal"] = "dead"
                row["steps_lived"] = 100
                row["energy_paid"] = 10
                row["inactive_steps"] = 0
        report = M.descriptive_readout(rows)
        self.assertEqual(report["by_family"]["stable"]
                         ["GATE_minus_FIXED"]["lived_steps"], -300)
        self.assertEqual(report["by_family"]["stable"]
                         ["GATE_minus_FIXED"]["survival_at_400"], -1)
        self.assertEqual(report["by_family"]["depletion"]
                         ["GATE_minus_FIXED"]["survival_at_400"], 0)
        self.assertAlmostEqual(report["equal_population_mean_contrasts"]
                               ["GATE_minus_FIXED"]["lived_steps"], -100)
        self.assertLess(report["equal_population_mean_contrasts"]
                        ["GATE_minus_FIXED"]["energy_paid_per_assigned_life"], 0)
        adverse = report["paired_outcome_profile"]
        stable = adverse["by_family"]["stable"]["GATE_minus_FIXED"]
        self.assertEqual(stable["survival_discordance"]["comparator_only_survived"], 80)
        self.assertEqual(stable["lived_steps_direction"]["gate_shorter"], 80)
        self.assertEqual(stable["lower_paid_energy_but_shorter_life"], 80)
        self.assertEqual(stable["lower_paid_energy_but_worse_horizon_survival"], 80)
        self.assertEqual(stable["worst_gate_minus_comparator_lived_steps"], -300)
        self.assertEqual(adverse["overall"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["comparator_only_survived"], 80)
        self.assertEqual(adverse["by_family"]["depletion"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["comparator_only_survived"], 0)

    def test_death_at_horizon_is_not_censoring(self):
        rows = synthetic_rows()
        row = next(x for x in rows if x["arm"] == "GATE_G0")
        row["terminal"] = "dead"
        report = M.descriptive_readout(rows)
        self.assertLess(report["by_population"][row["population"]]
                        ["GATE_minus_FIXED"]["survival_at_400"], 0)
        self.assertLess(report["by_family"][row["family"]]
                        ["GATE_minus_FIXED"]["survival_at_400"], 0)
        profile = report["paired_outcome_profile"]["overall"]["GATE_minus_FIXED"]
        self.assertEqual(profile["death_on_step_400"]["gate"], 1)
        self.assertEqual(profile["survival_discordance"]["comparator_only_survived"], 1)
        self.assertEqual(profile["lived_steps_direction"]["equal"], 240)

    def test_mean_neutral_can_hide_opposite_survival_failures(self):
        # Two independent synthetic matched blocks in different families.
        # Overall averages cancel exactly; neither adverse life may disappear.
        rows = synthetic_rows()
        gate_loss = next(r for r in rows if r["arm"] == "GATE_G0"
                         and r["family"] == "stable")
        fixed_loss = next(r for r in rows if r["arm"] == "FIXED_G0"
                          and r["family"] == "depletion")
        for row in (gate_loss, fixed_loss):
            row["terminal"] = "dead"
            row["steps_lived"] = 100
            row["energy_paid"] = 10.0
            row["inactive_steps"] = 0
        report = M.descriptive_readout(rows)
        self.assertEqual(report["equal_population_mean_contrasts"]
                         ["GATE_minus_FIXED"]["lived_steps"], 0)
        self.assertEqual(report["equal_population_mean_contrasts"]
                         ["GATE_minus_FIXED"]["survival_at_400"], 0)
        profile = report["paired_outcome_profile"]
        overall = profile["overall"]["GATE_minus_FIXED"]
        self.assertEqual(overall["survival_discordance"]["gate_only_survived"], 1)
        self.assertEqual(overall["survival_discordance"]["comparator_only_survived"], 1)
        self.assertEqual(overall["worst_gate_minus_comparator_lived_steps"], -300)
        self.assertEqual(overall["best_gate_minus_comparator_lived_steps"], 300)
        self.assertEqual(overall["lower_paid_energy_but_worse_horizon_survival"], 1)
        self.assertEqual(profile["by_family"]["stable"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["comparator_only_survived"], 1)
        self.assertEqual(profile["by_family"]["depletion"]["GATE_minus_FIXED"]
                         ["survival_discordance"]["gate_only_survived"], 1)
        self.assertEqual(profile["causal_replay_selection_advantage"],
                         "NOT_ESTABLISHED")

    def test_missing_duplicate_foreign_and_invalid_receipts_fail_closed(self):
        base = synthetic_rows()
        scenarios = [
            lambda x: x.pop(),
            lambda x: x.__setitem__(1, deepcopy(x[0])),
            lambda x: x[0].__setitem__("genome_seed", F0.founder_seed(7, 29)),
            lambda x: x[0].__setitem__("world_seed", 0),
            lambda x: x[0].__setitem__("life_seed", 0),
            lambda x: x[0].__setitem__("family", "foreign"),
            lambda x: x[0].__setitem__("arm", "GATE_on_GATE_selected"),
            lambda x: x[0].__setitem__("terminal", "crashed"),
            lambda x: x[0].__setitem__("terminal", "censored"),
            lambda x: x[0].__setitem__("steps_lived", 0),
            lambda x: x[0].__setitem__("energy_paid", float("nan")),
            lambda x: x[0].__setitem__("vigilance_paid", -1),
            lambda x: x[0].__setitem__("inactive_steps", True),
            lambda x: x[0].__setitem__("world_index", True),
            lambda x: x[0].__setitem__("population", 8),
            lambda x: x[0].__setitem__("additional_fabricated_field", 2),
        ]
        for i, mutation in enumerate(scenarios):
            rows = list(base)
            rows[0] = dict(base[0])
            if i == 8:
                rows[0]["steps_lived"] = 100
            mutation(rows)
            with self.subTest(i=i), self.assertRaises(ValueError):
                M.descriptive_readout(rows)

    def test_not_an_inference_or_pre_exposure_registration(self):
        self.assertNotIn("approve", M.proposal())
        result = M.descriptive_readout(synthetic_rows())
        self.assertEqual(result["inference"],
                         "FINITE_UNOPENED_F0_DESIGN_ONLY_NO_NEW_FAMILY_GENERALIZATION")
        self.assertFalse(result["worlds_opened_by_helper"])


if __name__ == "__main__":
    unittest.main()
