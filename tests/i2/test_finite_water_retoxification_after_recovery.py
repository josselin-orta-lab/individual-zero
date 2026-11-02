"""Silent tenth-food reversal after finite-water rescue: no future oracle."""
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, EAT

class SilentRetoxificationAfterRecovery(unittest.TestCase):
    def test_tenth_prechoice_is_identical_before_hidden_retoxification(self):
        regimes={"durable":SCENARIOS["restoration"]+(6,6),
                 "retoxified":SCENARIOS["restoration"]+(6,-8)}
        with tempfile.TemporaryDirectory() as root:
            observations={}
            for label,impulses in regimes.items():
                life=IsolatedI2.create(
                    Path(root)/(label+".sqlite"),learning=True,
                    impulses=impulses,extended_postcontact_study=True,
                    initial_energy=40,initial_uc=60,resources=8,
                    restorative_water_study=True,finite_water_capacity=1,
                    last_resort_exploration=True,deadline_aware=True)
                life.run_world(ticks=20)
                observations[label]=(life.decision_evidence(),life.audit())
            stable,sa=observations["durable"]
            changed,ca=observations["retoxified"]
            self.assertEqual(len(stable),10)
            self.assertEqual(len(changed),10)
            for i in range(10):
                for field in ("chosen","visible","before_energy","before_inventory",
                              "before_resources","physical_ticks_before","uc_before",
                              "uc_spent","candidate_scores",
                              "subjective_outcomes_available",
                              "last_resort_priority_applied",
                              "deadline_infeasible_collect_suppressed"):
                    with self.subTest(seq=i+1,field=field):
                        self.assertEqual(stable[i][field],changed[i][field])
                if i<9:
                    for field in ("energy_after","inventory_after","resources_after"):
                        self.assertEqual(stable[i][field],changed[i][field])
            for rows,audit in observations.values():
                self.assertEqual(rows[7]["chosen"],DRINK)
                self.assertEqual(rows[8]["chosen"],EAT)
                self.assertTrue(rows[8]["last_resort_priority_applied"])
                self.assertEqual(rows[9]["chosen"],EAT)
                self.assertTrue(rows[9]["internal_admission"])
                self.assertGreater(rows[9]["uc_spent"],0)
                self.assertFalse(rows[9]["last_resort_priority_applied"])
                self.assertEqual(rows[9]["survival_reflex"]["state"],"NO_PREEMPTION")
                self.assertNotIn(DRINK,rows[9]["visible"])
                self.assertEqual([v["observed_net"] for v in
                    rows[9]["outcomes_used_by_valuation"] if v["action"]==EAT],[-10,4])
                self.assertEqual(rows[9]["candidate_scores"][EAT],9)
                self.assertEqual(audit["water_remaining"],0)
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"],"NOT_ESTABLISHED")
            self.assertFalse(sa["terminal"])
            self.assertEqual(sa["physical_ticks"],20)
            self.assertEqual(sa["energy"],10)
            self.assertTrue(ca["terminal"])
            self.assertEqual(ca["physical_ticks"],20)
            self.assertEqual(ca["energy"],0)
            self.assertEqual(sa["actual_uc_spent"],ca["actual_uc_spent"])

if __name__=="__main__":
    unittest.main()
