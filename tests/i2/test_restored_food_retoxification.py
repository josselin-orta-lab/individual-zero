"""Hidden re-toxification after personally observed recovery; no oracle.

The source-declared negative control must preserve a terminal ninth step,
rather than requiring the dead subject to reach a tenth cognitive window.
"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, EAT, PrototypeRefusal,
)


class RetoxificationAfterRecovery(unittest.TestCase):
    def test_same_ninth_prechoice_ends_with_unpredictable_terminal_contact(self):
        original = SCENARIOS["restoration"] + (6, 6)
        # The hidden payoff switches after the personally beneficial tick-16
        # contact. Neither individual gets a new sensory cue before tick 18.
        returning = SCENARIOS["restoration"] + (-8, -8)
        with tempfile.TemporaryDirectory() as root:
            outcomes = {}
            for label, impulses in (("restored", original),
                                    ("retoxified", returning)):
                life = IsolatedI2.create(
                    Path(root) / (label + ".sqlite"),
                    learning=True, impulses=impulses,
                    initial_energy=40, initial_uc=60, resources=8,
                    last_resort_exploration=True,
                    extended_postcontact_study=True,
                )
                execution = life.run_world(ticks=20)
                outcomes[label] = (life, life.decision_evidence(), life.audit(),
                                   execution)
            safe_life, stable, sa, safe_execution = outcomes["restored"]
            bad_life, changed, ca, bad_execution = outcomes["retoxified"]
            self.assertEqual(len(stable), 10)
            # Real negative observation in both Python CI versions: the
            # re-toxified individual dies at decision 9 / physical tick 18.
            self.assertEqual(len(changed), 9)
            self.assertEqual(ca["revision"], 9)
            self.assertTrue(ca["terminal"])
            self.assertEqual(ca["energy"], 0)
            self.assertEqual(ca["physical_ticks"], 18)
            self.assertFalse(sa["terminal"])
            self.assertEqual(sa["physical_ticks"], 20)
            self.assertEqual(sa["revision"], 10)
            # The world transition was not observable to cognition. Compare
            # the complete prechoice history of all nine paid decisions.
            for i in range(9):
                with self.subTest(decision=i+1):
                    a, b = stable[i], changed[i]
                    for field in ("chosen", "visible", "before_energy",
                                  "before_inventory", "before_resources",
                                  "physical_ticks_before", "uc_before",
                                  "uc_spent", "candidate_scores",
                                  "subjective_outcomes_available",
                                  "last_resort_priority_applied",
                                  "deadline_infeasible_collect_suppressed"):
                        self.assertEqual(a[field], b[field], field)
                    if i < 8:
                        for field in ("energy_after", "inventory_after",
                                      "resources_after"):
                            self.assertEqual(a[field], b[field], field)
            ninth = changed[8]
            self.assertEqual(ninth["physical_ticks_before"], 18)
            self.assertEqual(ninth["chosen"], EAT)
            self.assertTrue(ninth["internal_admission"])
            self.assertEqual(ninth["candidate_scores"][EAT], 9)
            self.assertFalse(ninth["last_resort_priority_applied"])
            self.assertEqual([
                x["observed_net"] for x in ninth["outcomes_used_by_valuation"]
                if x["action"] == EAT], [-10, 4])
            self.assertGreater(stable[8]["energy_after"],
                               changed[8]["energy_after"])
            self.assertEqual(changed[8]["energy_after"], 0)
            self.assertTrue(changed[8]["terminal"])
            self.assertGreater(sa["energy"], ca["energy"])
            # No postmortem cognitive decision or silently forced recovery.
            with self.assertRaises(PrototypeRefusal):
                bad_life.step()
            self.assertEqual(bad_life.audit()["revision"], 9)
            self.assertEqual(safe_life.audit()["revision"], 10)
            for audit in (sa, ca):
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
