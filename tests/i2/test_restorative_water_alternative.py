"""Source-declared restorative water, matched paid first survival choice."""
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, DRINK, COLLECT, SCENARIOS

class RestorativeWaterTests(unittest.TestCase):
    def test_water_is_real_known_viable_alternative_and_deadline_matters(self):
        with tempfile.TemporaryDirectory() as root:
            arms={}
            for name, water, reflex, deadline in (
                ("old_world",False,True,False),
                ("reflex_only",True,True,False),
                ("deadline_only",True,False,True),
                ("combined",True,True,True),
            ):
                life=IsolatedI2.create(
                    Path(root)/(name+".sqlite"),learning=True,
                    impulses=SCENARIOS["adverse"],initial_energy=6,
                    resources=8,initial_uc=60,
                    restorative_water_study=water,
                    last_resort_exploration=reflex,deadline_aware=deadline)
                life.run_world(ticks=2)
                arms[name]=(life.decision_evidence()[0],life.audit())
            old=arms["old_world"][0]
            self.assertEqual(old["chosen"],COLLECT)
            self.assertEqual(arms["reflex_only"][0]["chosen"],COLLECT)
            self.assertEqual(arms["deadline_only"][0]["chosen"],DRINK)
            self.assertEqual(arms["combined"][0]["chosen"],DRINK)
            self.assertEqual(arms["combined"][1]["energy"],8)
            self.assertEqual(arms["reflex_only"][1]["energy"],2)
            self.assertEqual(arms["old_world"][1]["energy"],2)
            self.assertEqual(arms["deadline_only"][1]["energy"],8)
            self.assertEqual({x[0]["uc_spent"] for x in arms.values()},{4})
            for name in ("deadline_only","combined"):
                self.assertTrue(arms[name][0]["deadline_infeasible_collect_suppressed"])
            for row,audit in arms.values():
                self.assertFalse(audit["m11_authenticated"])
                self.assertTrue(row["internal_admission"])

    def test_existing_world_water_remains_nonrestorative(self):
        with tempfile.TemporaryDirectory() as root:
            a=IsolatedI2.create(Path(root)/"a.sqlite",learning=True,
                 impulses=SCENARIOS["stable"],initial_energy=4,
                 deadline_aware=True)
            b=IsolatedI2.create(Path(root)/"b.sqlite",learning=True,
                 impulses=SCENARIOS["stable"],initial_energy=4,
                 deadline_aware=True,restorative_water_study=True)
            a.run_world(ticks=2);b.run_world(ticks=2)
            self.assertEqual(a.decision_evidence()[0]["chosen"],DRINK)
            self.assertEqual(b.decision_evidence()[0]["chosen"],DRINK)
            self.assertEqual(a.audit()["energy"],0)
            self.assertEqual(b.audit()["energy"],6)

if __name__=="__main__":
    unittest.main()
