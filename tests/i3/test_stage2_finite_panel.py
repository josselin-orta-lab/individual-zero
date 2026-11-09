"""Synthetic receipts only: finite Stage-2.1 validation contract, no World."""
from copy import deepcopy
import unittest

from i3.lab import stage0_design as F0
from i3.lab import stage2_finite_panel as P


def founders():
    return {
        arm: {p: [F0.founder_seed(p, j) for j in range(F0.KEEP)]
              for p in range(F0.POPULATIONS)}
        for arm in ("FIXED", "GATE")
    }


def rows_for(selected=None):
    selected = selected or founders()
    rows = []
    for (condition, p, index, seed), world in P.expected_cells(selected).items():
        random_arm = condition == "RANDOM_on_GATE_selected"
        rows.append({
            "condition": condition, "population": p,
            "family": world["family"], "world_index": index,
            "world_seed": world["world_seed"], "genome_seed": seed,
            "life_seed": world["life_seed"], "terminal": "censored",
            "steps_lived": 400, "cognitive_energy_paid": 20.0,
            "cognitive_vigilance_paid": 30.0, "inactive_steps": 40,
            "sleep_steps": 8, "replays_paid": 40 if random_arm else 80,
            "random_draws": 8 if random_arm else 0,
            "random_nominal_replays": 50 if random_arm else 0,
            "random_eligible_replays": 40 if random_arm else 0,
        })
    return rows


class FinitePanelContract(unittest.TestCase):
    def test_exact_1200_cells_and_descriptive_contrasts(self):
        rows = rows_for()
        self.assertEqual(len(rows), 1200)
        output = P.reduce_finite_panel(founders(), rows)
        self.assertEqual(output["finite_panel_cells"], 1200)
        self.assertFalse(output["world_opening_authorized"])
        self.assertEqual(output["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(output["source_and_original_custody"], "NOT_AUTHENTICATED")
        self.assertEqual(output["population_independence"], "NOT_ESTABLISHED")
        self.assertEqual(output["population_denominator_per_condition"], 30)
        self.assertEqual(len(output["populations"]), 8)
        self.assertEqual(set(output["families"]), set(F0.FAMILIES))
        for family in F0.FAMILIES:
            self.assertEqual(output["families"][family]["by_condition"]
                             ["GATE_on_GATE_selected"]["assigned"], 80)
        self.assertEqual(output["populations"][0]["GATE_on_GATE_selected"]
                         ["energy_paid_per_assigned_life"], 20)
        self.assertEqual(output["populations"][0]["GATE_on_GATE_selected"]
                         ["energy_paid_per_lived_step"], 0.05)
        self.assertEqual(output["finite_panel_population_mean_survival_deltas"]
                         ["GATE_selected_minus_FIXED_selected"], 0)
        self.assertEqual(output["populations"][0]["RANDOM_on_GATE_selected"]
                         ["random_nominal_replays"], 1500)

    def test_censored_and_dead_on_400_are_different(self):
        rows = rows_for()
        gate = next(x for x in rows if x["condition"] == "GATE_on_GATE_selected")
        gate["terminal"] = "dead"
        out = P.reduce_finite_panel(founders(), rows)
        self.assertEqual(out["populations"][gate["population"]]
                         ["GATE_on_GATE_selected"]["deaths"], 1)
        self.assertEqual(out["populations"][gate["population"]]
                         ["GATE_on_GATE_selected"]["censored_at_400"], 29)

    def test_unfavorable_family_remains_visible(self):
        rows = rows_for()
        for row in rows:
            if row["family"] == "stable" and row["condition"] == "GATE_on_GATE_selected":
                row["terminal"] = "dead"
                row["steps_lived"] = 100
                row["sleep_steps"] = 2
                row["replays_paid"] = 10
                row["inactive_steps"] = 0
        out = P.reduce_finite_panel(founders(), rows)
        self.assertEqual(out["families"]["stable"]["gate_minus_fixed_survival"], -1)
        self.assertEqual(out["families"]["depletion"]["gate_minus_fixed_survival"], 0)
        self.assertEqual(out["finite_panel_population_mean_survival_deltas"]
                         ["GATE_selected_minus_FIXED_selected"], -1 / 3)

    def test_incomplete_duplicate_foreign_and_forged_families_rejected(self):
        original = rows_for()
        cases = [
            original[:-1],
            original + [deepcopy(original[0])],
            [deepcopy(original[0])] + deepcopy(original[1:]),
            deepcopy(original),
            deepcopy(original),
            deepcopy(original),
        ]
        cases[2][0]["world_index"] = 120
        cases[2][0]["genome_seed"] = F0.founder_seed(7, 30)
        cases[3][0]["family"] = "pulse" if cases[3][0]["family"] != "pulse" else "stable"
        cases[4][0]["world_seed"] += 1
        cases[5][0]["life_seed"] += 1
        for index, case in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(ValueError):
                P.reduce_finite_panel(founders(), case)
        duplicate = deepcopy(original)
        duplicate[1] = deepcopy(duplicate[0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            P.reduce_finite_panel(founders(), duplicate)

    def test_payment_and_random_custody_fail_closed(self):
        for field, value in [
            ("cognitive_energy_paid", -1),
            ("cognitive_vigilance_paid", float("nan")),
            ("cognitive_energy_paid", True),
            ("inactive_steps", 401),
            ("sleep_steps", 401),
            ("replays_paid", 200),
            ("steps_lived", 0),
            ("steps_lived", 401),
            ("terminal", "crashed"),
        ]:
            rows = rows_for()
            rows[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                P.reduce_finite_panel(founders(), rows)
        random_index = next(i for i, row in enumerate(rows_for())
                            if row["condition"] == "RANDOM_on_GATE_selected")
        for field, value in [
            ("random_draws", 9),
            ("random_draws", 0),
            ("random_nominal_replays", 48),
            ("random_nominal_replays", 57),
            ("random_eligible_replays", 51),
            ("replays_paid", 41),
        ]:
            rows = rows_for()
            rows[random_index][field] = value
            with self.subTest(random_field=field), self.assertRaises(ValueError):
                P.reduce_finite_panel(founders(), rows)
        other = rows_for()
        other[0]["random_draws"] = 1
        with self.assertRaises(ValueError):
            P.reduce_finite_panel(founders(), other)

    def test_selected_genomes_require_complete_distinct_population_pools(self):
        for mutate in ("missing", "duplicate", "wrong_population", "bool_seed"):
            chosen = founders()
            if mutate == "missing":
                del chosen["GATE"][7]
            elif mutate == "duplicate":
                chosen["GATE"][0][1] = chosen["GATE"][0][0]
            elif mutate == "wrong_population":
                chosen["FIXED"][0][0] = F0.founder_seed(1, 0)
            else:
                chosen["GATE"][0][0] = True
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                P.expected_cells(chosen)


if __name__ == "__main__":
    unittest.main()
