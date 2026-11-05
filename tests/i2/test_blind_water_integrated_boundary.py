"""Lock the observed blind-water integrated boundary, including deaths.

The water payoff is learned only through paid DRINK. No food phase is
present in current subjective evidence before the risky recontact.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, EAT

class BlindWaterIntegratedBoundary(unittest.TestCase):
    def test_one_use_hidden_worlds_and_policy_ablations(self):
        with tempfile.TemporaryDirectory() as root:
            lives={}
            for world in ("adverse","restoration"):
                for name,reflex in (("deadline",False),("combined",True)):
                    life=IsolatedI2.create(
                        Path(root)/f"{world}-{name}.sqlite",
                        learning=True,impulses=SCENARIOS[world]+
                        (SCENARIOS[world][-1],)*2,
                        extended_postcontact_study=True,
                        initial_energy=40,initial_uc=60,resources=8,
                        restorative_water_study=True,water_effect_blind=True,
                        finite_water_capacity=1,last_resort_exploration=reflex,
                        deadline_aware=True)
                    life.run_world(ticks=20)
                    lives[world,name]=(life.decision_evidence(),life.audit())
            for world in ("adverse","restoration"):
                deadline,da=lives[world,"deadline"]
                composed,ca=lives[world,"combined"]
                for i in range(8):
                    for field in ("chosen","energy_after","before_energy","uc_spent"):
                        self.assertEqual(deadline[i][field],composed[i][field],(world,i,field))
                self.assertEqual(deadline[7]["chosen"],DRINK)
                self.assertEqual(composed[7]["chosen"],DRINK)
                self.assertNotIn(DRINK,composed[8]["visible"])
                self.assertEqual(ca["water_remaining"],0)
                self.assertEqual(da["water_remaining"],0)
                self.assertEqual(composed[8]["chosen"],EAT)
                self.assertTrue(composed[8]["last_resort_priority_applied"])
                self.assertTrue(composed[8]["internal_admission"])
                self.assertGreater(composed[8]["uc_spent"],0)
                self.assertIsNone(deadline[8]["chosen"])
                self.assertFalse(deadline[8]["last_resort_priority_applied"])
                self.assertTrue(da["terminal"])
                self.assertEqual(da["physical_ticks"],20)
                self.assertFalse(ca["m11_authenticated"])
                self.assertEqual(ca["science"],"NOT_ESTABLISHED")
            adverse,aa=lives["adverse","combined"]
            restored,ra=lives["restoration","combined"]
            for i in range(9):
                for field in ("chosen","visible","before_energy",
                              "subjective_outcomes_available","candidate_scores",
                              "uc_before","uc_spent","last_resort_priority_applied"):
                    self.assertEqual(adverse[i][field],restored[i][field],(i,field))
            self.assertTrue(aa["terminal"])
            self.assertEqual(aa["physical_ticks"],18)
            self.assertEqual(aa["energy"],0)
            self.assertFalse(ra["terminal"])
            self.assertEqual(ra["physical_ticks"],20)
            self.assertEqual(ra["energy"],10)

if __name__=="__main__":
    unittest.main()
