"""G1-LAB tests: integrated one-commit cognitive advice and INTERNAL body effect.

Software feasibility and falsifiers, NOT evidence of a born or M11 life.
One immutable experiment schedule is hidden until the paid advice is issued.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.lab.integrated_loop import (  # noqa: E402
    COLLECT, EAT, DRINK, IntegratedLab, LabRefusal,
    REGIMES, run_pair,
)
from i2.modules.cognitive_cycle_fixture import FaultInjected  # noqa: E402


class G1LabClosedLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "one-owner.sqlite"

    def make(self, *, learning=True, deltas=REGIMES["stable"],
             initial_energy=40, initial_uc=60, resources=12):
        return IntegratedLab.create(
            self.path, life_ref="lab:subject:first", genesis_ref="lab:genesis:first",
            learning=learning, deltas=deltas, initial_energy=initial_energy,
            initial_uc=initial_uc, resources=resources)

    def test_past_only_unforced_actions_and_single_sqlite_owner(self):
        lab = self.make()
        first = lab.step()
        self.assertEqual(first.chosen, COLLECT)
        self.assertEqual(first.inventory, 1)
        self.assertEqual(first.result_net, -2)
        self.assertEqual(first.uc_spent, 4)
        self.assertEqual(first.motor_authority, "NONE")
        second = lab.step()
        self.assertEqual(second.chosen, EAT)
        self.assertEqual(second.inventory, 0)
        self.assertEqual(second.result_net, 6)
        self.assertEqual(second.uc_spent, 5)
        self.assertEqual(second.energy, 44)
        self.assertNotIn(EAT, first.visible)
        self.assertIn(EAT, second.visible)
        self.assertEqual(lab.audit()["revision"], 2)
        self.assertEqual(lab.audit()["cognition"]["committed"], 2)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM g1_lab_steps").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM account").fetchone()[0], 1)
        lab = IntegratedLab.reopen(
            self.path, life_ref="lab:subject:first", genesis_ref="lab:genesis:first")
        self.assertEqual(lab.audit()["energy"], 44)
        self.assertEqual(lab.step().chosen, COLLECT)

    def test_adverse_learning_and_fixed_ablation_are_comparable_not_equal_spend(self):
        result = run_pair(REGIMES["adverse"], initial_energy=40)
        self.assertEqual(result["status"], "G1_LAB_ONLY_NOT_BORN")
        self.assertFalse(result["m11_authenticated"])
        self.assertEqual(result["motor_authority"], "NONE")
        controls = result["arms"]["fixed"]
        learning = result["arms"]["observational"]
        self.assertEqual(controls["actions"][:2], [COLLECT, EAT])
        self.assertEqual(learning["actions"][:2], [COLLECT, EAT])
        self.assertNotEqual(controls["actions"], learning["actions"])
        self.assertTrue(all(x["motor_authority"] == "NONE"
                            for x in learning["steps"] if "chosen" in x))
        self.assertTrue(all(x["uc_spent"] >= 1 for x in learning["steps"]
                            if "chosen" in x))

    def test_stable_collect_eat_is_NOT_evidence_of_learning(self):
        report = run_pair(REGIMES["stable"], initial_energy=40)
        fixed = report["arms"]["fixed"]["actions"]
        learned = report["arms"]["observational"]["actions"]
        self.assertEqual(fixed[:4], [COLLECT, EAT, COLLECT, EAT])
        self.assertEqual(learned[:4], fixed[:4])
        self.assertEqual(report["arms"]["fixed"]["net_energy_change"],
                         report["arms"]["observational"]["net_energy_change"])

    def test_protocol_reversal_and_recovery_keep_negative_results(self):
        for regime in ("reversal", "recovery", "neutral"):
            with self.subTest(regime=regime):
                report = run_pair(REGIMES[regime], initial_energy=40)
                self.assertEqual(set(report["arms"]), {"fixed", "observational"})
                for arm in report["arms"].values():
                    self.assertLessEqual(len(arm["actions"]), len(REGIMES[regime]))
                    self.assertGreater(arm["spent_synthetic_uc"], 0)
                    self.assertTrue(all(row["motor_authority"] == "NONE"
                                        for row in arm["steps"] if "chosen" in row))

    def test_one_transaction_rolls_back_both_uc_and_body(self):
        lab = self.make()
        prior = lab.audit()
        with self.assertRaises(FaultInjected):
            lab.step(fault="before_commit")
        after = lab.audit()
        self.assertEqual(prior["revision"], after["revision"])
        self.assertEqual(prior["cognition"]["remaining_synthetic_uc"],
                         after["cognition"]["remaining_synthetic_uc"])
        self.assertEqual(prior["energy"], after["energy"])
        self.assertEqual(prior["inventory"], after["inventory"])
        self.assertEqual(lab.step().chosen, COLLECT)
        self.assertEqual(lab.audit()["revision"], 1)

    def test_veto_never_executes_eating_or_collecting(self):
        lab = self.make()
        denied = lab.step(veto=True)
        self.assertEqual(denied.control_status, "VETOED")
        self.assertIsNone(denied.chosen)
        self.assertEqual(denied.inventory, 0)
        self.assertEqual(denied.resources, 12)
        self.assertEqual(denied.energy, 39)  # one metabolism tick, no action
        self.assertEqual(denied.uc_spent, 4)  # even veto review is paid
        self.assertEqual(lab.step().chosen, COLLECT)

    def test_local_terminal_prevents_further_lab_capture(self):
        lab = self.make(initial_energy=2)
        r = lab.step()
        self.assertTrue(r.terminal)
        self.assertEqual(r.energy, 0)
        with self.assertRaisesRegex(LabRefusal, "terminal"):
            lab.step()
        self.assertTrue(lab.audit()["terminal"])
        self.assertFalse(lab.audit()["cognition"]["physiological_death_attested"])

    def test_exhausted_uc_blocks_cognition_and_physical_action(self):
        lab = self.make(initial_uc=4)
        r = lab.step()
        self.assertEqual(r.uc_remaining, 0)
        before = lab.audit()
        with self.assertRaisesRegex(ValueError, "UC exhausted"):
            lab.step()
        after = lab.audit()
        self.assertEqual(after["revision"], before["revision"])
        self.assertEqual(after["inventory"], before["inventory"])
        self.assertEqual(after["energy"], before["energy"])

    def test_no_same_cycle_or_hidden_regime_foresight(self):
        # The first action cannot know whether later eating will be good.
        firsts = []
        for label, regime in (("helpful", REGIMES["stable"]),
                              ("harmful", REGIMES["adverse"])):
            path = Path(self.tmp.name) / (label + ".sqlite")
            lab = IntegratedLab.create(
                path, life_ref="lab:subject:"+label,
                genesis_ref="lab:genesis:"+label,
                learning=True, deltas=regime, initial_energy=40)
            first = lab.step()
            firsts.append((first.chosen, first.visible, first.result_net))
            with sqlite3.connect(path) as db:
                observed = db.execute("SELECT event_json FROM events WHERE seq=1").fetchone()[0]
                self.assertNotIn('"observed_result"', observed)
        self.assertEqual(firsts[0], firsts[1])

    def test_historical_body_tampering_fails_closed_before_next_capture(self):
        lab = self.make(initial_energy=40)
        lab.step()
        lab.step()
        before = lab.audit()
        self.assertEqual(before["revision"], 2)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE g1_lab_steps SET net=net+1 WHERE seq=1")
        with self.assertRaisesRegex(LabRefusal, "cannot replay"):
            lab.audit()
        with self.assertRaisesRegex(LabRefusal, "cannot replay"):
            lab.step()

    def test_historical_action_mutation_fails_closed_even_if_final_body_same(self):
        lab = self.make(initial_energy=40)
        lab.step()
        lab.step()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE g1_lab_steps SET action_ref=? WHERE seq=1", (DRINK,))
        with self.assertRaisesRegex(LabRefusal, "differs from paid"):
            lab.audit()

    def test_past_body_energy_forgery_fails_even_with_matching_head(self):
        lab = self.make(initial_energy=40)
        lab.step()
        lab.step()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE g1_lab_steps SET before_energy=25 WHERE seq=1")
        with self.assertRaisesRegex(LabRefusal, "capture or subjective"):
            lab.audit()

    def test_foreign_identity_reopening_refused(self):
        lab = self.make()
        lab.step()
        with self.assertRaisesRegex(LabRefusal, "foreign"):
            IntegratedLab.reopen(self.path, life_ref="lab:other", genesis_ref="lab:genesis:first")


if __name__ == "__main__":
    unittest.main()