"""Observe survival reflex release after a paid emergency food recontact.

Single fresh ten-phase restored world. This is a temporal behavior smoke,
not a claim the subject learned to inhibit the reflex.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT

class ReflexRecoveryIntegrationTests(unittest.TestCase):
    def test_emergency_then_observed_reward_then_nonurgent_tenth_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            life=IsolatedI2.create(
                Path(tmp)/"subject.sqlite", learning=True,
                impulses=SCENARIOS["restoration"]+(6,6),
                initial_energy=40, initial_uc=60, resources=8,
                last_resort_exploration=True, extended_postcontact_study=True)
            life.run_world(ticks=20)
            rows=life.decision_evidence()
            self.assertEqual(len(rows),10)
            eighth,ninth,tenth=rows[7:]
            self.assertEqual(eighth["chosen"],EAT)
            self.assertTrue(eighth["last_resort_priority_applied"])
            self.assertEqual(ninth["chosen"],EAT)
            self.assertFalse(ninth["last_resort_priority_applied"])
            self.assertIn(4,[r["observed_net"]
                for r in ninth["outcomes_used_by_valuation"] if r["action"]==EAT])
            self.assertEqual(tenth["survival_reflex"]["state"],"NO_PREEMPTION")
            self.assertFalse(tenth["last_resort_priority_applied"])
            self.assertFalse(tenth["deadline_infeasible_collect_suppressed"])
            self.assertGreater(tenth["before_energy"],4)
            self.assertGreater(tenth["uc_spent"],0)
            self.assertEqual(life.audit()["revision"],10)
            self.assertFalse(life.audit()["m11_authenticated"])
            self.assertEqual(life.audit()["science"],"NOT_ESTABLISHED")

if __name__=="__main__":
    unittest.main()
