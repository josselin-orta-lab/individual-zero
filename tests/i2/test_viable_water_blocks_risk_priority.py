"""An earlier toxic meal makes source-bound emergency priority measurable.

After seven identical paid actions and personally observed harmful EAT,
all four lives reach the same critical eighth predecision state. The
water-positive world is opt-in at fresh genesis, not a food-payoff oracle.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT, DRINK, COLLECT


class SafeWaterVersusRiskTests(unittest.TestCase):
    def test_known_viable_water_blocks_reflex_overriding_harmful_memory(self):
        with tempfile.TemporaryDirectory() as root:
            arms = {}
            policies = (
                ("historic_reflex", False, True, False),
                ("safe_reflex", True, True, False),
                ("safe_deadline", True, False, True),
                ("safe_combined", True, True, True),
            )
            for name, water, reflex, deadline in policies:
                life = IsolatedI2.create(
                    Path(root) / (name + ".sqlite"),
                    learning=True, impulses=SCENARIOS["adverse"],
                    initial_energy=40, resources=8, initial_uc=60,
                    restorative_water_study=water,
                    last_resort_exploration=reflex,
                    deadline_aware=deadline)
                life.run_world(ticks=16)
                rows = life.decision_evidence()
                self.assertEqual(len(rows), 8)
                arms[name] = (rows, life.audit())
            original_rows, old = arms["historic_reflex"]
            for name, (rows, audit) in arms.items():
                with self.subTest(policy=name):
                    self.assertEqual(audit["actual_uc_spent"], 38)
                    self.assertEqual(audit["revision"], 8)
                    self.assertFalse(audit["m11_authenticated"])
                    for i in range(7):
                        # Up to the critical eighth window, the selected
                        # actions and physical consequences are identical.
                        for field in ("chosen", "before_energy",
                                      "energy_after", "before_inventory",
                                      "inventory_after", "before_resources",
                                      "resources_after",
                                      "subjective_outcomes_available"):
                            self.assertEqual(rows[i][field],
                                             original_rows[i][field], (i, field))
                    eighth = rows[7]
                    ref = original_rows[7]
                    for field in ("before_energy", "before_inventory",
                                  "before_resources", "visible", "uc_before",
                                  "physical_ticks_before",
                                  "subjective_outcomes_available"):
                        self.assertEqual(eighth[field], ref[field], field)
                    self.assertEqual(eighth["before_energy"], 2)
                    self.assertEqual(eighth["survival_reflex"]["state"], "PREEMPT")
                    self.assertIn(EAT, eighth["visible"])
                    self.assertIn(DRINK, eighth["visible"])
                    self.assertIn(COLLECT, eighth["visible"])
                    self.assertEqual([x["observed_net"] for x in eighth[
                        "outcomes_used_by_valuation"] if x["action"] == EAT], [-10])
                    self.assertTrue(eighth["internal_admission"])
            historic = arms["historic_reflex"][0][7]
            safe = arms["safe_reflex"][0][7]
            deadline = arms["safe_deadline"][0][7]
            combined = arms["safe_combined"][0][7]
            self.assertEqual(historic["chosen"], EAT)
            self.assertTrue(historic["last_resort_priority_applied"])
            self.assertTrue(old["terminal"])
            self.assertEqual(old["energy"], 0)
            # Known safe restorative DRINK blocks the EXTRA emergency EAT
            # priority. Without deadline planning, COLLECT still wins.
            self.assertFalse(safe["last_resort_priority_applied"])
            self.assertEqual(safe["chosen"], COLLECT)
            self.assertEqual(arms["safe_reflex"][1]["energy"], 0)
            self.assertTrue(arms["safe_reflex"][1]["terminal"])
            self.assertEqual(safe["candidate_scores"][EAT], -5)
            self.assertEqual(safe["candidate_scores"][COLLECT], 3)
            self.assertEqual(safe["candidate_scores"][DRINK], 1)
            # Deadline suppression removes an infeasible COLLECT; DRINK
            # now wins the original unchanged paid Competition.
            for row, name in ((deadline, "safe_deadline"),
                              (combined, "safe_combined")):
                self.assertEqual(row["chosen"], DRINK)
                self.assertFalse(row["last_resort_priority_applied"])
                self.assertTrue(row["deadline_infeasible_collect_suppressed"])
                self.assertEqual(arms[name][1]["energy"], 6)
                self.assertEqual(row["candidate_scores"][COLLECT], 0)
                self.assertEqual(row["candidate_scores"][DRINK], 1)
                self.assertFalse(arms[name][1]["terminal"])
            self.assertEqual(deadline["uc_spent"], combined["uc_spent"])
            self.assertEqual(arms["safe_deadline"][1]["actual_uc_spent"],
                             arms["safe_combined"][1]["actual_uc_spent"])


if __name__ == "__main__":
    unittest.main()
