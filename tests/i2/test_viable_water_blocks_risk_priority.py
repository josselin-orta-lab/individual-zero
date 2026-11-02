"""Known restorative water blocks risky emergency priority at exact paid capture."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2,SCENARIOS,EAT,DRINK,COLLECT


class SafeWaterVersusRiskTests(unittest.TestCase):
    def life(self,root,name,*,water,reflex,deadline):
        return IsolatedI2.create(
            Path(root)/(name+".sqlite"), learning=True,
            impulses=SCENARIOS["adverse"],initial_energy=8,
            initial_uc=60,resources=8,restorative_water_study=water,
            last_resort_exploration=reflex,deadline_aware=deadline)

    def test_accessible_viable_water_blocks_emergency_food_override(self):
        with tempfile.TemporaryDirectory() as root:
            arms={}
            for name,water,reflex,deadline in (
                ("historic_reflex",False,True,False),
                ("safe_reflex",True,True,False),
                ("safe_combined",True,True,True)):
                life=self.life(root,name,water=water,reflex=reflex,deadline=deadline)
                first=life.step()
                self.assertEqual(first.chosen,COLLECT)
                # One paid COLLECT leaves a berry in inventory, and two
                # metabolic ticks lower the body to a critical reserve.
                life.advance_physics();life.advance_physics()
                second=life.step()
                row=life.decision_evidence()[1]
                arms[name]=(first,second,row,life.audit())
            historic=arms["historic_reflex"]
            safe=arms["safe_reflex"]
            combined=arms["safe_combined"]
            for first,second,row,audit in arms.values():
                self.assertEqual(row["before_energy"],4)
                self.assertIn(EAT,row["visible"])
                self.assertIn(DRINK,row["visible"])
                self.assertEqual(row["survival_reflex"]["state"],"CONSTRAIN")
                self.assertEqual(first.actual_uc_spent,4)
                self.assertEqual(second.actual_uc_spent,5)
                self.assertEqual(audit["actual_uc_spent"],9)
                self.assertFalse(audit["m11_authenticated"])
            self.assertEqual(historic[1].chosen,EAT)
            self.assertTrue(historic[2]["last_resort_priority_applied"])
            self.assertEqual(historic[3]["energy"],0)
            self.assertTrue(historic[3]["terminal"])
            for arm in (safe,combined):
                # Plan-viability removes an emergency *override*, not
                # the risk of an ordinary learner still selecting EAT.
                self.assertFalse(arm[2]["last_resort_priority_applied"])
                self.assertTrue(arm[2]["internal_admission"])
                self.assertEqual(arm[2]["chosen"],arm[1].chosen)
            self.assertEqual(safe[1].chosen,combined[1].chosen)

if __name__=="__main__":
    unittest.main()
