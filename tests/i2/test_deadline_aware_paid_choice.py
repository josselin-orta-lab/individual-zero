"""Opt-in deadline choice: real paid difference, not a survival benefit claim."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, DRINK,
)


class DeadlineAwarePaidPolicy(unittest.TestCase):
    def create(self, energy, enabled):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return IsolatedI2.create(
            Path(tmp.name) / "life.sqlite", learning=False,
            impulses=SCENARIOS["stable"], initial_energy=energy,
            deadline_aware=enabled)

    def test_matched_paid_decision_abstains_from_futile_collect(self):
        baseline = self.create(4, False)
        changed = self.create(4, True)
        old = baseline.step()
        new = changed.step()
        self.assertEqual(old.chosen, COLLECT)
        self.assertEqual(new.chosen, DRINK)
        self.assertEqual(old.actual_uc_spent, new.actual_uc_spent)
        self.assertEqual(old.energy, new.energy)
        readout = changed.decision_evidence()[0]
        self.assertEqual(readout["candidate_scores"][COLLECT], 0)
        self.assertTrue(readout["deadline_infeasible_collect_suppressed"])
        self.assertFalse(baseline.decision_evidence()[0][
            "deadline_infeasible_collect_suppressed"])
        self.assertEqual(readout["survival_reflex"]["state"], "CONSTRAIN")
        self.assertFalse(changed.audit()["m11_authenticated"])

    def test_sufficient_energy_does_not_change_paid_choice(self):
        baseline = self.create(10, False)
        changed = self.create(10, True)
        self.assertEqual(baseline.step().chosen, COLLECT)
        self.assertEqual(changed.step().chosen, COLLECT)
        self.assertFalse(changed.decision_evidence()[0][
            "deadline_infeasible_collect_suppressed"])

    def test_composed_policy_requires_explicit_fresh_genesis(self):
        with tempfile.TemporaryDirectory() as root:
            life = IsolatedI2.create(
                Path(root) / "life.sqlite", learning=True,
                impulses=SCENARIOS["stable"], deadline_aware=True,
                last_resort_exploration=True)
            meta, _body, _rows = life._read()
            self.assertEqual(meta["deadline_aware"], 1)
            self.assertEqual(meta["last_resort_exploration"], 1)
            first = life.step()
            self.assertEqual(first.chosen, COLLECT)
            self.assertEqual(first.actual_uc_spent, 4)
            self.assertEqual(life.audit()["revision"], 1)
            self.assertFalse(life.audit()["m11_authenticated"])
            self.assertFalse(life.decision_evidence()[0][
                "deadline_infeasible_collect_suppressed"])


if __name__ == "__main__":
    unittest.main()
