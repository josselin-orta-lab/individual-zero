"""Internal I2 causal prototype: engineering controls, not living/M11 science."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, PrototypeRefusal, COLLECT, EAT, SCENARIOS, demo,
    paired_decision_contrast,
)
from i2.modules.cognitive_cycle_fixture import (
    FaultInjected, CommitAcknowledgmentLost,
)


class IsolatedPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "prototype.sqlite"

    def create(self, **kwargs):
        return IsolatedI2.create(
            self.path, learning=kwargs.pop("learning", True),
            impulses=kwargs.pop("impulses", SCENARIOS["stable"]), **kwargs)

    def test_one_owner_paid_admitted_and_delayed_experience(self):
        i2 = self.create()
        a = i2.step()
        b = i2.step()
        self.assertEqual((a.chosen, b.chosen), (COLLECT, EAT))
        self.assertIsNotNone(a.admission_ref)
        self.assertNotEqual(a.admission_ref, b.admission_ref)
        self.assertEqual((a.actual_uc_spent, b.actual_uc_spent), (4, 5))
        self.assertEqual(b.energy, 42)
        self.assertEqual(i2.audit()["revision"], 2)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM events").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM proto_steps").fetchone()[0], 2)
            first, second = [r[0] for r in db.execute(
                "SELECT event_json FROM events ORDER BY seq")]
        self.assertNotIn("evidence:i2:outcome:2", second)
        self.assertNotIn("evidence:i2:outcome:1", first)
        self.assertIn("evidence:i2:outcome:1", second)
        self.assertFalse(i2.audit()["m11_authenticated"])

    def test_veto_prevents_internal_admission_but_costs_uc(self):
        i2 = self.create()
        veto = i2.step(veto=True)
        self.assertIsNone(veto.chosen)
        self.assertIsNone(veto.admission_ref)
        self.assertEqual(veto.control_status, "VETOED")
        self.assertEqual(veto.resources, 8)
        self.assertEqual(veto.energy, 39)
        self.assertEqual(veto.actual_uc_spent, 4)

    def test_before_commit_rolls_back_world_and_uc(self):
        i2 = self.create()
        before = i2.audit()
        with self.assertRaises(FaultInjected):
            i2.step(fault="before_commit")
        self.assertEqual(i2.audit(), before)
        self.assertEqual(i2.step().chosen, COLLECT)

    def test_after_commit_halts_no_retry_or_cold_reentry(self):
        i2 = self.create()
        with self.assertRaises(CommitAcknowledgmentLost):
            i2.step(fault="after_commit")
        self.assertEqual(i2.audit()["revision"], 1)
        with self.assertRaises(PrototypeRefusal):
            i2.step()
        cold = IsolatedI2.inspect(self.path)
        self.assertEqual(cold.audit()["revision"], 1)
        with self.assertRaises(PrototypeRefusal):
            cold.step()

    def test_terminal_absorbs_and_ancient_identity_rejected(self):
        i2 = self.create(initial_energy=2)
        self.assertTrue(i2.step().terminal)
        with self.assertRaises(PrototypeRefusal):
            i2.step()
        self.assertTrue(IsolatedI2.inspect(self.path).audit()["terminal"])
        with self.assertRaises(PrototypeRefusal):
            IsolatedI2.create(self.path, learning=False, impulses=(6,))
        other = IsolatedI2(self.path, "i2:prototype:life:foreign",
                           i2.genesis_ref, inspection_only=True)
        with self.assertRaises(PrototypeRefusal):
            other.audit()

    def test_history_tamper_rejected(self):
        i2 = self.create()
        i2.step()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE proto_steps SET energy=99 WHERE seq=1")
        with self.assertRaises(PrototypeRefusal):
            i2.audit()
        with self.assertRaises(PrototypeRefusal):
            i2.step()

    def test_no_hidden_first_capture_or_learning_overclaim(self):
        result = demo("adverse", steps=5)
        self.assertEqual(result["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertEqual(set(result["arms"]), {"observed_chosen", "fixed"})
        first = [arm["trace"][0]["chosen"] for arm in result["arms"].values()]
        self.assertEqual(first, [COLLECT, COLLECT])
        self.assertTrue(all(not arm["audit"]["engine_registered"]
                            for arm in result["arms"].values()))

    def test_adverse_first_divergence_is_a_matched_engineered_score_contrast(self):
        report = demo("adverse", steps=6)
        difference = report["behavioral_contrast"]
        self.assertEqual(
            difference["classification"],
            "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST",
        )
        self.assertEqual(difference["first_divergence_seq"], 4)
        self.assertTrue(difference["matched_prechoice"])
        self.assertEqual(difference["observational_action"], COLLECT)
        self.assertEqual(difference["fixed_action"], EAT)
        self.assertEqual(difference["candidate_score_differences"][EAT],
                         {"observational": -5, "fixed": 4})
        left = report["arms"]["observed_chosen"]["decisions"]
        right = report["arms"]["fixed"]["decisions"]
        for idx in range(3):
            self.assertEqual(left[idx]["chosen"], right[idx]["chosen"])
            self.assertEqual(left[idx]["energy_after"], right[idx]["energy_after"])
            self.assertEqual(left[idx]["uc_spent"], right[idx]["uc_spent"])
        self.assertEqual(left[3]["uc_before"], right[3]["uc_before"])
        self.assertEqual(left[3]["subjective_outcomes_available"],
                         right[3]["subjective_outcomes_available"])
        self.assertEqual(left[3]["outcomes_used_by_valuation"],
                         left[3]["subjective_outcomes_available"])
        self.assertEqual(right[3]["outcomes_used_by_valuation"], ())
        self.assertTrue(difference["not_a_natural_learning_or_survival_verdict"])

    def test_stable_null_and_neutral_tie_are_preserved_not_tuned(self):
        stable = demo("stable", steps=6)
        self.assertEqual(
            stable["behavioral_contrast"]["classification"],
            "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON",
        )
        self.assertIsNone(stable["behavioral_contrast"]["first_divergence_seq"])
        neutral = demo("neutral", steps=6)
        contrast = neutral["behavioral_contrast"]
        self.assertEqual(contrast["first_divergence_seq"], 4)
        self.assertTrue(contrast["matched_prechoice"])
        self.assertIsNone(contrast["observational_action"])
        self.assertEqual(contrast["fixed_action"], EAT)

    def test_decision_inspection_cannot_feed_subject_or_fabricate_match(self):
        subject = self.create()
        self.assertEqual(subject.decision_evidence(), ())
        subject.step()
        self.assertEqual(subject.decision_evidence()[0]["subjective_outcomes_available"], ())
        subject.step()
        readings = subject.decision_evidence()
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[1]["subjective_outcomes_available"][0]["seq"], 1)
        self.assertNotIn("impulses", readings[1])
        forged = [dict(v) for v in readings]
        forged[0]["energy_after"] += 1
        # Context that only diverges AFTER a selected action cannot be
        # treated as the same prehistory for a later divergence.
        forged[1]["chosen"] = None
        compared = paired_decision_contrast(tuple(forged), readings)
        self.assertEqual(compared["classification"],
                         "UNMATCHED_PRECHOICE_NO_CAUSAL_ATTRIBUTION")


if __name__ == "__main__":
    unittest.main()
