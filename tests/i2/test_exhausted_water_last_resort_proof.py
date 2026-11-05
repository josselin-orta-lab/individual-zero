"""The paid last-resort food recontact after finite safe water depletion.

The same policy has the same first-person experience in two hidden worlds;
the ninth food consequence, not privileged future knowledge, differs.
"""
import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2,SCENARIOS,DRINK,EAT

class ExhaustedWaterLastResortProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lives={}
        cls.snapshots={}
        cls.readouts={}
        cls.temp=tempfile.TemporaryDirectory()
        for world in ("adverse","restoration"):
            for policy,reflex in (("combined",True),("deadline",False)):
                life=IsolatedI2.create(
                    Path(cls.temp.name)/f"{world}-{policy}.sqlite",
                    learning=True,impulses=SCENARIOS[world]+(SCENARIOS[world][-1],)*2,
                    extended_postcontact_study=True,
                    restorative_water_study=True,finite_water_capacity=1,
                    last_resort_exploration=reflex,deadline_aware=True,
                    initial_energy=40,initial_uc=60,resources=8)
                life.run_world(ticks=20)
                cls.snapshots[world,policy]=life.audit()
                cls.readouts[world,policy]=life.decision_evidence()
                cls.lives[world,policy]=life

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_first_nine_captures_identical_across_hidden_worlds(self):
        for policy in ("combined","deadline"):
            toxic=self.readouts["adverse",policy]
            restored=self.readouts["restoration",policy]
            for index in range(9):
                a,b=toxic[index],restored[index]
                for field in ("chosen","before_energy","before_inventory",
                              "before_resources","visible","candidate_scores",
                              "subjective_outcomes_available","uc_before",
                              "uc_spent","last_resort_priority_applied"):
                    self.assertEqual(a[field],b[field],(policy,index,field))

    def test_combined_recontact_is_paid_after_exhaustion_not_an_oracle(self):
        for world in ("adverse","restoration"):
            rows=self.readouts[world,"combined"]
            self.assertEqual(rows[7]["chosen"],DRINK)
            self.assertEqual(rows[8]["chosen"],EAT)
            self.assertNotIn(DRINK,rows[8]["visible"])
            self.assertEqual(rows[8]["before_energy"],4)
            self.assertTrue(rows[8]["last_resort_priority_applied"])
            self.assertTrue(rows[8]["internal_admission"])
            self.assertGreater(rows[8]["uc_spent"],0)
            self.assertEqual([o["observed_net"] for o in
                rows[8]["outcomes_used_by_valuation"] if o["action"]==EAT],[-10])
            self.assertEqual(self.snapshots[world,"combined"]["water_remaining"],0)
            self.assertFalse(self.snapshots[world,"combined"]["m11_authenticated"])

    def test_bounded_positive_and_fatal_outcomes_preserved(self):
        self.assertTrue(self.snapshots["adverse","combined"]["terminal"])
        self.assertEqual(self.snapshots["adverse","combined"]["physical_ticks"],18)
        self.assertEqual(self.snapshots["adverse","combined"]["energy"],0)
        self.assertFalse(self.snapshots["restoration","combined"]["terminal"])
        self.assertEqual(self.snapshots["restoration","combined"]["physical_ticks"],20)
        self.assertEqual(self.snapshots["restoration","combined"]["energy"],10)
        for world in ("adverse","restoration"):
            self.assertTrue(self.snapshots[world,"deadline"]["terminal"])
            self.assertEqual(self.snapshots[world,"deadline"]["physical_ticks"],20)
            self.assertEqual(self.readouts[world,"deadline"][8]["chosen"],None)
            self.assertFalse(self.readouts[world,"deadline"][8]["internal_admission"])
            for policy in ("combined","deadline"):
                self.assertEqual(self.snapshots[world,policy]["science"],"NOT_ESTABLISHED")

if __name__=="__main__":
    unittest.main()
