"""Second hidden food reversal after finite-water last resort.

The tenth payoff is not visible at the tenth predecision capture.
All behavior is paid through the original I2 SQLite owner.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT, DRINK


class FiniteWaterRetoxificationAfterRecovery(unittest.TestCase):
    def test_unobservable_tenth_reversal_does_not_change_tenth_choice(self):
        regimes = {
            "restored": SCENARIOS["restoration"] + (6, 6),
            "retoxified": SCENARIOS["restoration"] + (6, -8),
        }
        with tempfile.TemporaryDirectory() as root:
            outcomes = {}
            for name, impulses in regimes.items():
                life = IsolatedI2.create(
                    Path(root) / (name + ".sqlite"), learning=True,
                    impulses=impulses, extended_postcontact_study=True,
                    initial_energy=40, initial_uc=60, resources=8,
                    restorative_water_study=True, finite_water_capacity=1,
                    last_resort_exploration=True, deadline_aware=True)
                life.run_world(ticks=20)
                outcomes[name] = life.decision_evidence(), life.audit()
            stable, stable_audit = outcomes["restored"]
            changed, changed_audit = outcomes["retoxified"]
            self.assertEqual(len(stable), 10)
            self.assertEqual(len(changed), 10)
            fields = (
                "chosen", "visible", "before_energy", "before_inventory",
                "before_resources", "physical_ticks_before", "uc_before",
                "uc_spent", "candidate_scores",
                "subjective_outcomes_available",
                "last_resort_priority_applied",
                "deadline_infeasible_collect_suppressed",
            )
            for i in range(10):
                for field in fields:
                    with self.subTest(decision=i + 1, field=field):
                        self.assertEqual(stable[i][field], changed[i][field])
                if i < 9:
                    for field in ("energy_after", "inventory_after",
                                  "resources_after"):
                        self.assertEqual(stable[i][field], changed[i][field])
            for rows, audit in outcomes.values():
                self.assertEqual(rows[7]["chosen"], DRINK)
                self.assertEqual(rows[8]["chosen"], EAT)
                self.assertTrue(rows[8]["last_resort_priority_applied"])
                self.assertEqual(rows[9]["chosen"], EAT)
                self.assertFalse(rows[9]["last_resort_priority_applied"])
                self.assertEqual(rows[9]["survival_reflex"]["state"],
                                 "NO_PREEMPTION")
                self.assertTrue(rows[9]["internal_admission"])
                self.assertGreater(rows[9]["uc_spent"], 0)
                self.assertNotIn(DRINK, rows[9]["visible"])
                self.assertEqual([o["observed_net"] for o in
                    rows[9]["outcomes_used_by_valuation"] if o["action"] == EAT],
                    [-10, 4])
                self.assertEqual(rows[9]["candidate_scores"][EAT], 9)
                self.assertEqual(audit["water_remaining"], 0)
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"], "NOT_ESTABLISHED")
            self.assertEqual(stable_audit["physical_ticks"], 20)
            self.assertFalse(stable_audit["terminal"])
            self.assertEqual(stable_audit["energy"], 10)
            self.assertEqual(changed_audit["physical_ticks"], 20)
            self.assertTrue(changed_audit["terminal"])
            self.assertEqual(changed_audit["energy"], 0)
            self.assertEqual(stable_audit["actual_uc_spent"],
                             changed_audit["actual_uc_spent"])


if __name__ == "__main__":
    unittest.main()
