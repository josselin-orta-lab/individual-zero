"""Memory and urgency after an actually paid finite-water last resort.

Do not claim that remembered recovery alone causes the tenth action:
the test separates observed valuation shift from survival priority.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2,SCENARIOS,EAT,DRINK

class PostDepletionMemoryReappraisal(unittest.TestCase):
    def test_recovered_food_updates_ninth_to_tenth_valuation_without_reflex_boost(self):
        with tempfile.TemporaryDirectory() as root:
            life=IsolatedI2.create(
                Path(root)/"restored.sqlite",learning=True,
                impulses=SCENARIOS["restoration"]+(6,6),
                extended_postcontact_study=True,
                restorative_water_study=True,finite_water_capacity=1,
                last_resort_exploration=True,deadline_aware=True,
                initial_energy=40,initial_uc=60,resources=8)
            life.run_world(ticks=20)
            rows=life.decision_evidence()
            audit=life.audit()
            self.assertEqual(len(rows),10)
            self.assertEqual(rows[7]["chosen"],DRINK)
            self.assertEqual(rows[8]["chosen"],EAT)
            self.assertEqual(rows[9]["chosen"],EAT)
            self.assertTrue(rows[8]["last_resort_priority_applied"])
            self.assertFalse(rows[9]["last_resort_priority_applied"])
            self.assertEqual(rows[8]["survival_reflex"]["state"],"CONSTRAIN")
            self.assertEqual(rows[9]["survival_reflex"]["state"],"NO_PREEMPTION")
            self.assertNotIn(DRINK,rows[8]["visible"])
            self.assertNotIn(DRINK,rows[9]["visible"])
            self.assertEqual(
                [x["observed_net"] for x in rows[8]["outcomes_used_by_valuation"]
                 if x["action"]==EAT],[-10])
            self.assertEqual(
                [x["observed_net"] for x in rows[9]["outcomes_used_by_valuation"]
                 if x["action"]==EAT],[-10,4])
            self.assertEqual(rows[9]["candidate_scores"][EAT],9)
            self.assertTrue(rows[9]["internal_admission"])
            self.assertGreater(rows[9]["uc_spent"],0)
            self.assertEqual(audit["water_remaining"],0)
            self.assertEqual(audit["energy"],10)
            self.assertFalse(audit["terminal"])
            self.assertFalse(audit["m11_authenticated"])
            self.assertEqual(audit["science"],"NOT_ESTABLISHED")

if __name__=="__main__":
    unittest.main()
