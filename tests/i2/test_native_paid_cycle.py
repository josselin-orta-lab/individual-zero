"""Native I2 full paid cycle: lived state, later evidence and SQLite custody."""
import sys
import tempfile
import sqlite3
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import NativePaidI2, NativeRefusal


class NativePaidCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "native.sqlite"
        self.traits = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def birth(self, **kw):
        body = kw.pop("body", Body(60, 40, 40, 90))
        traits = kw.pop("temperament", self.traits)
        return NativePaidI2.create(
            self.path, body=body, temperament=traits, **kw)

    def test_owned_native_paid_action_and_later_first_person_capture(self):
        actor = self.birth()
        before = actor.audit()
        first = actor.step()
        self.assertEqual(first["revision"], 1)
        self.assertLess(first["remaining_uc"], before["remaining_uc"])
        self.assertEqual(first["m11_authenticated"], False)
        self.assertNotEqual(first["body"], before["body"])
        later = actor.step()
        self.assertEqual(later["revision"], 2)
        self.assertEqual(actor.audit(), later)
        with sqlite3.connect(self.path) as conn:
            events = [row[0] for row in conn.execute(
                "SELECT event_json FROM events ORDER BY seq")]
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM native_physical_events").fetchone()[0], 2)
        self.assertNotIn("evidence:i2:native:outcome:1", events[0])
        self.assertIn("evidence:i2:native:outcome:1", events[1])

    def test_before_commit_rollback_and_uncertain_commit_halts(self):
        from i2.modules.cognitive_cycle_fixture import (
            FaultInjected, CommitAcknowledgmentLost)
        actor = self.birth()
        before = actor.audit()
        with self.assertRaises(FaultInjected):
            actor.step(fault="before_commit")
        self.assertEqual(actor.audit(), before)
        with self.assertRaises(CommitAcknowledgmentLost):
            actor.step(fault="after_commit")
        self.assertEqual(actor.audit()["revision"], 1)
        with self.assertRaises(NativeRefusal):
            actor.step()

    def test_paid_abstention_advances_real_physics_without_fake_motor(self):
        actor = self.birth(learning=False)
        actor.step()
        second = actor.step()
        self.assertEqual(second["revision"], 2)
        with sqlite3.connect(self.path) as conn:
            action = conn.execute(
                "SELECT admitted_action FROM native_physical_events "
                "WHERE seq=2").fetchone()[0]
            self.assertEqual(action, "NO_ACTION")
            self.assertLessEqual(second["body"]["water"], 39.2)
            saved = conn.execute(
                "SELECT event_json FROM events WHERE seq=2").fetchone()[0]
            self.assertNotIn("evidence:i2:native:outcome:2", saved)
        self.assertEqual(actor.audit()["revision"], 2)

    def test_explicit_veto_is_not_an_action_and_passive_time_elapses(self):
        actor = self.birth()
        before = actor.audit()
        after = actor.step(veto=True)
        self.assertEqual(after["revision"], 1)
        self.assertEqual(after["body"]["energy"], before["body"]["energy"])
        self.assertAlmostEqual(after["body"]["food"], 39.8)
        self.assertAlmostEqual(after["body"]["water"], 39.6)
        with sqlite3.connect(self.path) as db:
            action, marker = db.execute(
                "SELECT admitted_action,admission_ref "
                "FROM native_physical_events WHERE seq=1").fetchone()
        self.assertEqual(action, "NO_ACTION")
        self.assertTrue(marker.startswith("no-motor:"))
        self.assertLess(after["remaining_uc"], before["remaining_uc"])

    def test_terminal_after_veto_stops_body_and_cold_reentry(self):
        actor = self.birth(body=Body(60, 0.1, 40, 90))
        stopped = actor.step(veto=True)
        self.assertTrue(stopped["terminal"])
        self.assertEqual(stopped["body"]["food"], 0.0)
        with self.assertRaises(NativeRefusal):
            actor.step()
        cold = NativePaidI2.inspect(self.path)
        self.assertEqual(cold.audit(), actor.audit())
        with self.assertRaises(NativeRefusal):
            cold.step()

    def test_rehashed_but_physically_false_transition_is_rejected(self):
        import hashlib
        import json
        from i2.runtime.native_physiology_journal import (
            SCHEMA, audit_native_body)
        actor = self.birth()
        actor.step()
        with sqlite3.connect(self.path) as db:
            seq, action, ref, cog, before, after, relief, terminal, prev = db.execute(
                "SELECT seq,admitted_action,admission_ref,cognition_hash,"
                "before_json,after_json,net_physiological_relief,terminal,"
                "previous_hash FROM native_physical_events WHERE seq=1").fetchone()
            forged = json.dumps(
                {"energy": 99.0, "food": 99.0, "water": 99.0,
                 "integrity": 99.0},
                sort_keys=True, separators=(",", ":"))
            payload = json.dumps(
                [SCHEMA, seq, action, ref, cog, before, forged,
                 relief, bool(terminal), prev],
                sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(payload.encode("ascii")).hexdigest()
            db.execute(
                "UPDATE native_physical_events SET after_json=?,event_hash=? "
                "WHERE seq=1", (forged, digest))
            db.execute("UPDATE native_physiology SET body_json=?,head=? "
                       "WHERE id=1", (forged, digest))
            # Structural hashes and heads are internally consistent.
            self.assertEqual(audit_native_body(db)["revision"], 1)
        with self.assertRaisesRegex(NativeRefusal, "physiology"):
            actor.audit()

    def test_native_body_journal_tamper_rejected(self):
        actor = self.birth()
        actor.step()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE native_physical_events SET after_json='{}'")
        with self.assertRaises(ValueError):
            actor.audit()

    def test_innate_traits_and_zero_learning_flag_do_not_fake_experiences(self):
        actor = self.birth(learning=False)
        self.assertEqual(actor.audit()["temperament"], self.traits.as_dict())
        actor.step()
        actor.step()
        with sqlite3.connect(self.path) as conn:
            events = [row[0] for row in conn.execute(
                "SELECT event_json FROM events ORDER BY seq")]
        self.assertIn("evidence:i2:native:outcome:1", events[1])
        self.assertFalse(actor.audit()["engine_registered"])


if __name__ == "__main__":
    unittest.main()
