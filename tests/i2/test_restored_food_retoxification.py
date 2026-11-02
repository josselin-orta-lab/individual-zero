"""Hidden re-toxification after personally observed recovery; no oracle."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT

class RetoxificationAfterRecovery(unittest.TestCase):
    def test_same_prechoice_ninth_history_cannot_predict_hidden_retoxification(self):
        original=SCENARIOS["restoration"]+(6,6)
        # Hidden world changes AFTER the positive chosen contact at tick 16.
        returning=SCENARIOS["restoration"]+(-8,-8)
        with tempfile.TemporaryDirectory() as root:
            outcomes={}
            for label,impulses in (("restored",original),("retoxified",returning)):
                life=IsolatedI2.create(
                    Path(root)/(label+".sqlite"),learning=True,
                    impulses=impulses,initial_energy=40,initial_uc=60,resources=8,
                    last_resort_exploration=True,extended_postcontact_study=True)
                life.run_world(ticks=20)
                outcomes[label]=(life.decision_evidence(),life.audit())
            stable,sa=outcomes["restored"]
            changed,ca=outcomes["retoxified"]
            self.assertEqual(len(stable),10)
            self.assertEqual(len(changed),10)
            for i in range(9):
                self.assertEqual(stable[i]["chosen"],changed[i]["chosen"])
                self.assertEqual(stable[i]["before_energy"],changed[i]["before_energy"])
                self.assertEqual(stable[i]["candidate_scores"],changed[i]["candidate_scores"])
            self.assertEqual(stable[8]["chosen"],EAT)
            self.assertEqual(changed[8]["chosen"],EAT)
            self.assertIn(4,[o["observed_net"] for o in changed[8][
                "outcomes_used_by_valuation"] if o["action"]==EAT])
            self.assertGreater(sa["energy"],ca["energy"])
            self.assertFalse(sa["m11_authenticated"])
            self.assertFalse(ca["m11_authenticated"])
            self.assertEqual(sa["science"],"NOT_ESTABLISHED")
            self.assertEqual(ca["science"],"NOT_ESTABLISHED")

if __name__=="__main__":
    unittest.main()
