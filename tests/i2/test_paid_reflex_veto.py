"""Last-resort survival exploration through paid I2 cognition, never a safety bypass."""
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, EAT, PrototypeRefusal,
)


class LastResortSurvivalTests(unittest.TestCase):
    def make(self, energy, *, learning=False, impulses=None, enabled=True):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "life.sqlite"
        return IsolatedI2.create(
            path, learning=learning, impulses=impulses or SCENARIOS["stable"],
            initial_energy=energy,
            last_resort_exploration=enabled), path

    def test_low_energy_favorable_food_is_chosen_through_paid_control(self):
        life, _ = self.make(8)
        self.assertEqual(life.step().chosen, COLLECT)
        life.advance_physics()
        life.advance_physics()
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertIsNotNone(second.admission_ref)
        self.assertEqual(second.control_status, "REVIEWED_NOT_ADMITTED")
        self.assertEqual(second.actual_uc_spent, 5)
        self.assertEqual(second.energy, 8)
        row = life.decision_evidence()[1]
        self.assertEqual(row["survival_reflex"]["state"], "CONSTRAIN")
        self.assertGreater(row["candidate_scores"][EAT], row["candidate_scores"][COLLECT])

    def test_low_energy_adverse_food_may_kill_and_is_not_oracle(self):
        life, _ = self.make(8, impulses=SCENARIOS["adverse"])
        self.assertEqual(life.step().chosen, COLLECT)
        life.advance_physics()
        life.advance_physics()
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertTrue(second.terminal)
        self.assertEqual(second.energy, 0)
        self.assertEqual(second.actual_uc_spent, 5)
        self.assertFalse(life.audit()["m11_authenticated"])

    def test_personally_harmful_food_is_retried_when_starving(self):
        life, _ = self.make(16, learning=True, impulses=SCENARIOS["adverse"])
        self.assertEqual(life.step().chosen, COLLECT)
        self.assertEqual(life.step().chosen, EAT)
        self.assertEqual(life.audit()["energy"], 4)
        self.assertEqual(life.step().chosen, COLLECT)
        self.assertEqual(life.audit()["energy"], 2)
        last = life.step()
        self.assertEqual(last.chosen, EAT)
        self.assertTrue(last.terminal)
        self.assertEqual(last.actual_uc_spent, 5)
        # An earlier personal adverse result remains the only observed
        # food consequence, not advance knowledge of the next outcome.
        decision = life.decision_evidence()[3]
        self.assertEqual(decision["survival_reflex"]["state"], "PREEMPT")
        self.assertEqual(
            [x["observed_net"] for x in decision["outcomes_used_by_valuation"]
             if x["action"] == EAT], [-10])
        self.assertTrue(decision["last_resort_priority_applied"])
        self.assertGreater(decision["candidate_scores"][EAT],
                           decision["candidate_scores"][COLLECT])

    def test_opt_out_preserves_history_in_previously_harmful_food(self):
        life, _ = self.make(16, learning=True, impulses=SCENARIOS["adverse"],
                            enabled=False)
        self.assertEqual(life.step().chosen, COLLECT)
        self.assertEqual(life.step().chosen, EAT)
        self.assertEqual(life.step().chosen, COLLECT)
        fourth = life.step()
        self.assertNotEqual(fourth.chosen, EAT)
        self.assertFalse(life.decision_evidence()[3]["last_resort_priority_applied"])

    def test_explicit_safety_veto_still_blocks_last_resort(self):
        life, _ = self.make(8)
        life.step()
        life.advance_physics()
        life.advance_physics()
        second = life.step(veto=True)
        self.assertIsNone(second.chosen)
        self.assertIsNone(second.admission_ref)
        self.assertEqual(second.control_status, "VETOED")
        self.assertEqual(second.actual_uc_spent, 5)

    def test_high_energy_keeps_normal_food_choice(self):
        life, _ = self.make(40)
        self.assertEqual(life.step().chosen, COLLECT)
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertEqual(second.actual_uc_spent, 5)

    def test_replay_rejects_forged_action(self):
        life, path = self.make(8)
        life.step()
        life.advance_physics()
        life.advance_physics()
        life.step()
        self.assertEqual(life.audit()["revision"], 2)
        with sqlite3.connect(path) as db:
            db.execute("UPDATE proto_steps SET admission_ref='forged' WHERE seq=2")
        with self.assertRaises(PrototypeRefusal):
            life.audit()


if __name__ == "__main__":
    unittest.main()
