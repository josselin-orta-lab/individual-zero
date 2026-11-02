"""Paid ninth decision after hidden-world recovery; no future oracle.

Separate ten-decision fresh genesis, never a modification of the locked
eight-decision restoration study. Outcomes are first-person only after
the preceding real action and paid subsequent capture.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, EAT, PrototypeRefusal,
)


class PostContactDecisionTests(unittest.TestCase):
    def make(self, restored):
        folder=tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        impulses=SCENARIOS["restoration" if restored else "adverse"]
        return IsolatedI2.create(
            Path(folder.name)/"subject.sqlite", learning=True,
            impulses=impulses+(impulses[-1],)*2,
            initial_energy=40, initial_uc=60, resources=8,
            last_resort_exploration=True,
            extended_postcontact_study=True)

    def test_restore_result_is_first_person_at_next_paid_decision(self):
        life=self.make(True)
        result=life.run_world(ticks=18)
        decisions=life.decision_evidence()
        self.assertEqual(len(decisions),9)
        recontact=decisions[7]
        subsequent=decisions[8]
        self.assertEqual(recontact["chosen"],EAT)
        self.assertEqual(recontact["physical_ticks_before"],16)
        self.assertFalse(any(
            x["seq"]==recontact["seq"] for x in
            recontact["subjective_outcomes_available"]))
        seen=[x["observed_net"] for x in subsequent["subjective_outcomes_available"]
              if x["action"]==EAT]
        self.assertEqual(seen,[-10,4])
        self.assertIn(4,[x["observed_net"] for x in
                         subsequent["outcomes_used_by_valuation"] if x["action"]==EAT])
        self.assertEqual(life.audit()["revision"],9)
        self.assertFalse(life.audit()["m11_authenticated"])
        self.assertGreater(life.audit()["actual_uc_spent"],38)

    def test_continued_toxicity_is_not_reclassified_as_recovery(self):
        life=self.make(False)
        life.run_world(ticks=18)
        decisions=life.decision_evidence()
        self.assertEqual(len(decisions),8)
        self.assertEqual(decisions[7]["chosen"],EAT)
        self.assertTrue(life.audit()["terminal"])
        self.assertEqual(life.audit()["physical_ticks"],16)

    def test_old_eight_action_genesis_refuses_silent_extension(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(PrototypeRefusal):
                IsolatedI2.create(
                    Path(root)/"invalid.sqlite",learning=True,
                    impulses=SCENARIOS["restoration"]+(6,6),
                    last_resort_exploration=True)


if __name__=="__main__":
    unittest.main()
