"""Bounded same-SQLite owner contract: actual native body consequence and rollback.

The test supplies a synthetic already-reviewed fixture record, not an
independent living action-control attestation.
"""
import hashlib
import json
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_physiology_journal import (
    initialize_native_body, native_snapshot, commit_admitted_physics,
    audit_native_body,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


class NativeJournalTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.execute("CREATE TABLE events(seq INTEGER PRIMARY KEY, "
                        "event_json TEXT NOT NULL, event_hash TEXT NOT NULL)")
        self.db.execute("BEGIN IMMEDIATE")
        initialize_native_body(
            self.db, body=Body(50, 40, 40, 90),
            traits=BirthTemperament(0, 0.5, 0.2, 0, 0))
        self.db.commit()

    def record(self, seq=1, action="boire", veto=False):
        digest = hashlib.sha256(f"synthetic:{seq}".encode()).hexdigest()
        candidate = f"candidate-{seq}"
        control = f"receipt-{seq}"
        event = {
            "frame": {"candidates": [{
                "candidate_ref": candidate,
                "semantic_ref": action}]},
            "control_review": {
                "status": "REVIEWED_NOT_ADMITTED",
                "suggested_candidate_ref": candidate,
                "control_receipt_ref": control},
            "safety_finding": {"veto": veto},
            "control_receipt": {"ref": control}}
        self.db.execute("INSERT INTO events VALUES (?,?,?)",
                        (seq, canonical(event), digest))
        ref = "internal:i2:native-admission:" + hashlib.sha256(
            canonical([seq, digest, action]).encode()).hexdigest()
        return digest, ref

    def test_actual_admitted_drink_changes_hydration_not_energy_gain(self):
        self.db.execute("BEGIN IMMEDIATE")
        head, admission = self.record()
        result = commit_admitted_physics(
            self.db, action="boire", admission_ref=admission,
            cognition_hash=head, drink_water_gain=25)
        self.db.commit()
        self.assertEqual(result["body"]["water"], 64.6)
        self.assertEqual(result["body"]["energy"], 49.5)
        self.assertEqual(audit_native_body(self.db)["revision"], 1)
        self.assertFalse(result["m11_authenticated"])
        self.assertEqual(native_snapshot(self.db)["body"].water, 64.6)

    def test_rejected_action_rolls_back_without_extra_owner(self):
        self.db.execute("BEGIN IMMEDIATE")
        head, admission = self.record(veto=True)
        with self.assertRaises(ValueError):
            commit_admitted_physics(
                self.db, action="boire", admission_ref=admission,
                cognition_hash=head, drink_water_gain=25)
        self.db.rollback()
        self.assertEqual(native_snapshot(self.db)["revision"], 0)
        self.assertEqual(audit_native_body(self.db)["revision"], 0)

    def test_atomic_before_commit_and_foreign_receipt(self):
        self.db.execute("BEGIN IMMEDIATE")
        head, admission = self.record()
        with self.assertRaises(ValueError):
            commit_admitted_physics(
                self.db, action="boire", admission_ref="forged",
                cognition_hash=head, drink_water_gain=25)
        self.db.rollback()
        self.db.execute("BEGIN IMMEDIATE")
        head, admission = self.record()
        commit_admitted_physics(
            self.db, action="boire", admission_ref=admission,
            cognition_hash=head, drink_water_gain=25)
        self.db.rollback()
        self.assertEqual(native_snapshot(self.db)["body"].water, 40.0)
        self.assertEqual(audit_native_body(self.db)["revision"], 0)

    def test_journal_mutation_refused(self):
        self.db.execute("BEGIN IMMEDIATE")
        head, admission = self.record()
        commit_admitted_physics(
            self.db, action="boire", admission_ref=admission,
            cognition_hash=head, drink_water_gain=25)
        self.db.commit()
        self.db.execute(
            "UPDATE native_physical_events SET after_json=? WHERE seq=1",
            (canonical(Body(50, 40, 99, 90).as_dict()),))
        with self.assertRaises(ValueError):
            audit_native_body(self.db)


if __name__ == "__main__":
    unittest.main()
