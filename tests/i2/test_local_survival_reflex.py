"""I2 local survival reflex: exact capture binding and nonmotor readout."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.modules.unstable_world_reappraisal_contract import (
    review_reappraisal,
)
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT


class TestLocalReflex(unittest.TestCase):
    def make_subject(self, energy=40):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return IsolatedI2.create(
            Path(temp.name) / "individual.sqlite", learning=True,
            impulses=SCENARIOS["adverse"], initial_energy=energy,
        )

    def adapter(self, subject):
        subject.audit()
        _, state, rows = subject._read()
        claim = subject._claim(
            state["revision"], state["energy"], state["inventory"],
            state["resources"], rows, physical_ticks=state["tick_count"],
        )
        return LocalEnergySurvivalReflex(claim, state["energy"])

    def test_danger_levels_are_local_not_hidden_payoff_dependent(self):
        for energy, expected in (
            (1, "PREEMPT"), (2, "PREEMPT"),
            (3, "CONSTRAIN"), (4, "CONSTRAIN"),
            (5, "NO_PREEMPTION"), (40, "NO_PREEMPTION"),
        ):
            with self.subTest(energy=energy):
                subject = self.make_subject(energy)
                reflex = self.adapter(subject)
                self.assertEqual(reflex.state, expected)
                self.assertTrue(reflex.verify_survival_reflex(
                    claim=reflex.claim, snapshot=reflex.snapshot()))
                self.assertNotIn("food_phase", reflex.snapshot().evidence_ref)

    def test_spoofed_energy_and_cross_capture_are_refused(self):
        subject = self.make_subject()
        good = self.adapter(subject)
        with self.assertRaises(ValueError):
            LocalEnergySurvivalReflex(good.claim, 4)
        subject.step()
        newer = self.adapter(subject)
        self.assertFalse(newer.verify_survival_reflex(
            claim=good.claim, snapshot=good.snapshot()))
        self.assertFalse(good.verify_survival_reflex(
            claim=newer.claim, snapshot=newer.snapshot()))

    def test_contract_reflex_priority_and_no_motor_authority(self):
        subject = self.make_subject(3)
        adapter = self.adapter(subject)
        # Target is currently absent; a survival CONSTRAIN must take priority.
        # The production observation port binds the current claim only during
        # paid step(); use a narrow exact-claim authority for this pure contract.
        result = review_reappraisal(
            claim=adapter.claim, target_semantic_ref=EAT,
            chosen_results=(), observation_source=ExactObservation(adapter.claim),
            chosen_source=EmptyResults(), reflex=adapter.snapshot(),
            reflex_source=adapter,
        )
        self.assertEqual(result.review_status, "REFLEX_CONSTRAINED")
        self.assertEqual(result.motor_authority, "NONE")
        self.assertTrue(result.requires_paid_competition)

    def test_decision_diagnostics_preserve_paid_action_and_outcomes(self):
        subject = self.make_subject()
        subject.step()
        subject.step()
        readout = subject.decision_evidence()
        self.assertEqual([row["survival_reflex"]["state"] for row in readout],
                         ["NO_PREEMPTION", "NO_PREEMPTION"])
        self.assertEqual([row["chosen"] for row in readout],
                         ["affordance:collect:berry_a", EAT])
        self.assertEqual([row["uc_spent"] for row in readout], [4, 5])
        self.assertTrue(all(row["survival_reflex"]["authority"] ==
                            "LOCAL_NON_MOTOR_ONLY" for row in readout))

    def test_physically_low_energy_is_visible_before_paid_action(self):
        subject = self.make_subject(4)
        subject.advance_physics()
        subject.step()
        row = subject.decision_evidence()[0]
        self.assertEqual(row["before_energy"], 3)
        self.assertEqual(row["survival_reflex"]["state"], "CONSTRAIN")


class ExactObservation:
    def __init__(self, claim):
        self.claim = claim

    def verify(self, *, life_ref, claim, digest):
        return claim == self.claim and life_ref == claim.life_ref and digest == claim.digest()


class EmptyResults:
    def verify_chosen_result(self, *, result):
        return False


if __name__ == "__main__":
    unittest.main()
