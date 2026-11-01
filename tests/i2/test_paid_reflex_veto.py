"""Paid action-control survival reflex integration, internal I2 only."""
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, COLLECT, EAT, PrototypeRefusal


class PaidReflexVetoTests(unittest.TestCase):
    def make(self, energy):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "life.sqlite"
        return IsolatedI2.create(
            path, learning=False, impulses=SCENARIOS["stable"],
            initial_energy=energy), path

    def test_low_reserve_eat_is_vetoed_after_full_paid_review(self):
        life, _ = self.make(8)
        first = life.step()
        self.assertEqual(first.chosen, COLLECT)
        life.advance_physics()
        life.advance_physics()
        second = life.step()
        self.assertIsNone(second.chosen)
        self.assertIsNone(second.admission_ref)
        self.assertEqual(second.control_status, "VETOED")
        self.assertEqual(second.actual_uc_spent, 5)
        self.assertEqual(second.inventory, 1)
        self.assertEqual(second.energy, 3)
        self.assertFalse(life.audit()["terminal"])
        self.assertEqual(life.decision_evidence()[1]["survival_reflex"]["state"], "CONSTRAIN")

    def test_safe_energy_keeps_existing_eat_action(self):
        life, _ = self.make(40)
        self.assertEqual(life.step().chosen, COLLECT)
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertEqual(second.actual_uc_spent, 5)
        self.assertEqual(life.audit()["revision"], 2)

    def test_reflex_veto_is_replayed_from_committed_energy(self):
        life, path = self.make(8)
        life.step()
        life.advance_physics()
        life.advance_physics()
        life.step()
        self.assertEqual(life.audit()["revision"], 2)
        self.assertEqual(life.decision_evidence()[1]["survival_reflex"]["state"], "CONSTRAIN")
        with sqlite3.connect(path) as db:
            db.execute("UPDATE proto_steps SET admission_ref='forged' WHERE seq=2")
        with self.assertRaises(PrototypeRefusal):
            life.audit()


if __name__ == "__main__":
    unittest.main()
