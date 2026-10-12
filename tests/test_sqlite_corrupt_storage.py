"""Malformed SQLite files must fail closed at the standalone audit boundary."""
from __future__ import annotations

from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.journal import GENESIS_HASH, HashChainedJournal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


ID = "i0:sqlite:bad-storage"


def state():
    return {
        "individual_id": ID, "world": {"step": 0},
        "scheduler": {"t_monde": 0},
        "owners": {"metacognition_health": {"cycle": 0}},
    }


class MalformedSQLiteCustodyTests(unittest.TestCase):
    def test_independent_audit_handles_a_missing_schema_column(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "invalid.db")
            # A readable but counterfeit/old-schema database is not an I0
            # current-state generation, even if it contains a plausible ID.
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE life_current (slot INTEGER, individual_id TEXT)")
                db.execute(
                    "INSERT INTO life_current VALUES (1, ?)", (ID,),
                )
            with self.assertRaisesRegex(RecoveryBlocked, "malformed storage"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=ID,
                )
            proc = subprocess.run(
                [sys.executable, "scripts/audit_i0_sqlite.py",
                 "--db", path, "--identity", ID],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("audit rejected", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)

    def test_integer_event_hash_cannot_crash_or_pass_audit(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "invalid-hash.db")
            journal = HashChainedJournal()
            row = journal.append(
                event_id="first:event",
                causal_event={"kind": "test_causal_receipt", "t_monde": 0},
            ).as_dict()
            with SQLiteLifeLedger.birth(
                path=path, individual_id=ID, initial_state=state(),
            ) as ledger:
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                ledger.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="step:1", current_state=state(),
                    events=[row],
                )
            with sqlite3.connect(path) as db:
                db.execute("UPDATE causal_occurrence SET event_hash=1 WHERE idx=0")
            with self.assertRaisesRegex(RecoveryBlocked, "hash|canonical"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=ID,
                )

    def test_nontext_pending_intent_is_not_a_live_recovery_lease(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "invalid-intent.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id=ID, initial_state=state(),
            ) as ledger:
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
            with sqlite3.connect(path) as db:
                db.execute("UPDATE pending_intent SET intent_ref=? WHERE slot=1",
                           (sqlite3.Binary(b"garbled"),))
            with self.assertRaisesRegex(RecoveryBlocked, "intent"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=ID,
                )


if __name__ == "__main__":
    unittest.main()
