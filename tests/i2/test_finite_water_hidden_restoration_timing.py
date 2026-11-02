"""Timing-only falsifier for paid recontact after known water exhaustion.

The three future food schedules are declared before each genesis.
All subjects share prior harmful food, finite safe water and the same
first-person ninth predecision capture; no oracle or action is injected.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT, DRINK

class FiniteWaterHiddenRestorationTiming(unittest.TestCase):
    def test_hidden_reversal_timing_does_not_leak_into_last_resort(self):
        schedules={
            "never": SCENARIOS["adverse"]+(-8,-8),
            "restored_by_ninth": SCENARIOS["restoration"]+(6,6),
            "restored_after_ninth": SCENARIOS["adverse"]+(-8,6),
        }
        with tempfile.TemporaryDirectory() as root:
            arms={}
            for name, impulses in schedules.items():
                life=IsolatedI2.create(
                    Path(root)/(name+".sqlite"), learning=True,
                    impulses=impulses, extended_postcontact_study=True,
                    initial_energy=40,initial_uc=60,resources=8,
                    restorative_water_study=True,finite_water_capacity=1,
                    last_resort_exploration=True,deadline_aware=True)
                life.run_world(ticks=20)
                arms[name]=(life.decision_evidence(),life.audit())
            toxic,ta=arms["never"]
            restored,ra=arms["restored_by_ninth"]
            delayed,da=arms["restored_after_ninth"]
            self.assertGreaterEqual(len(toxic),9)
            self.assertGreaterEqual(len(restored),9)
            self.assertGreaterEqual(len(delayed),9)
            for i in range(9):
                for field in ("chosen","visible","before_energy","before_inventory",
                              "before_resources","physical_ticks_before","uc_before",
                              "uc_spent","candidate_scores",
                              "subjective_outcomes_available",
                              "last_resort_priority_applied"):
                    self.assertEqual(toxic[i][field],restored[i][field],(i,field))
                    self.assertEqual(toxic[i][field],delayed[i][field],(i,field))
            for rows,audit in arms.values():
                self.assertEqual(rows[7]["chosen"],DRINK)
                self.assertEqual(rows[8]["chosen"],EAT)
                self.assertNotIn(DRINK,rows[8]["visible"])
                self.assertTrue(rows[8]["last_resort_priority_applied"])
                self.assertTrue(rows[8]["internal_admission"])
                self.assertGreater(rows[8]["uc_spent"],0)
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"],"NOT_ESTABLISHED")
            self.assertTrue(ta["terminal"])
            self.assertTrue(da["terminal"])
            self.assertEqual(ta["physical_ticks"],18)
            self.assertEqual(da["physical_ticks"],18)
            self.assertFalse(ra["terminal"])
            self.assertEqual(ra["physical_ticks"],20)
            self.assertEqual(ra["energy"],10)

if __name__=="__main__":
    unittest.main()
