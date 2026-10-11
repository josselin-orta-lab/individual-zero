"""SQLite life-custody transaction and real os._exit crash tests (not M-11 PASS)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.journal import HashChainedJournal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


def state(identity="i0:birth:1", step=0):
    return {
        "individual_id": identity,
        "world": {"position": {"x": 1, "y": 1}, "physical_step": step},
        "scheduler": {"t_monde": step},
        "owners": {"metacognition_health": {"last_cycle": step}},
    }


def entry(journal, identity):
    return journal.append(
        event_id=identity,
        causal_event={"kind": "test_causal_receipt", "t_monde": len(journal.entries) + 1},
    ).as_dict()


class SQLiteLifeCustodyTests(unittest.TestCase):
    def test_atomic_state_events_and_latest_generation_are_coherent(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "individual.db")
            journal = HashChainedJournal()
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ) as ledger:
                self.assertEqual(ledger.audit().generation, 0)
                self.assertTrue(ledger.audit().may_recover)
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                records = [entry(journal, "event:1"), entry(journal, "event:2")]
                committed = ledger.commit_generation(
                    expected_generation=0, expected_head="00" * 32,
                    intent_ref="step:1", current_state=state(step=1),
                    events=records,
                )
                self.assertEqual(committed.generation, 1)
                self.assertEqual(committed.journal_head, journal.head_hash)
                self.assertEqual(committed.journal_count, 2)
                self.assertEqual(ledger.export_canonical_journal(), journal.canonical_bytes())
                self.assertEqual(
                    json.loads(ledger.recover_current_bytes(
                        expected_individual_id="i0:birth:1",
                    ))["scheduler"]["t_monde"],
                    1,
                )
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id="i0:birth:1",
            ) as ledger:
                self.assertEqual(ledger.audit().generation, 1)
                self.assertEqual(ledger.export_canonical_journal(), journal.canonical_bytes())
                ledger.begin_intent(expected_generation=1, intent_ref="step:2")
                journal.append(
                    event_id="event:3",
                    causal_event={"kind": "test_causal_receipt", "t_monde": 2},
                )
                committed = ledger.commit_generation(
                    expected_generation=1, expected_head=journal.entries[1].event_hash,
                    intent_ref="step:2", current_state=state(step=2),
                    events=[journal.entries[2].as_dict()],
                )
                self.assertEqual(committed.journal_count, 3)
                self.assertEqual(committed.generation, 2)

    def test_birth_only_and_wrong_identity_are_rejected(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "individual.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ):
                with self.assertRaises(FileExistsError):
                    SQLiteLifeLedger.birth(
                        path=path, individual_id="i0:birth:1", initial_state=state(),
                    )
            with self.assertRaises(RecoveryBlocked):
                SQLiteLifeLedger.open_existing(
                    path=path, expected_individual_id="i0:other",
                )
            with self.assertRaises(ValueError):
                SQLiteLifeLedger.open_existing(
                    path=str(Path(tmp) / "missing.db"),
                    expected_individual_id="i0:birth:1",
                )

    def test_stale_and_duplicate_causes_poison_instead_of_retry(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "individual.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ) as ledger:
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=99, intent_ref="wrong")
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=0, intent_ref="step:1")
            # A failed stale intent is not an applied physical effect; reopen
            # validates the original active record without promoting anything.
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id="i0:birth:1",
            ) as ledger:
                self.assertTrue(ledger.audit().may_recover)
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                with self.assertRaises(RecoveryBlocked):
                    ledger.recover_current_bytes(expected_individual_id="i0:birth:1")
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=0, intent_ref="step:2")
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id="i0:birth:1",
            ) as ledger:
                sealed = ledger.seal_uncertain()
                self.assertEqual(sealed.status, "technical_halt")
                self.assertFalse(sealed.may_recover)
                with self.assertRaises(RecoveryBlocked):
                    ledger.recover_current_bytes(expected_individual_id="i0:birth:1")

    def test_terminal_death_is_persistent_and_has_no_recovery_api(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "individual.db")
            journal = HashChainedJournal()
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ) as ledger:
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                rows = [
                    journal.append(
                        event_id="transition:1",
                        causal_event={"kind": "world_transition_experienced", "t_monde": 1},
                    ).as_dict(),
                    journal.append(
                        event_id="death:1", causal_event={
                            "kind": "individual_death_confirmed",
                            "t_monde": 1, "attempt_ref": "attempt:1",
                        },
                    ).as_dict(),
                    journal.append(
                        event_id="close:1", causal_event={
                            "kind": "step_closed", "t_monde": 1,
                            "attempt_ref": "attempt:1", "data": {
                                "outcome": "dead",
                                "applied_command_count": 1,
                                "world_advance_count": 1,
                            },
                        },
                    ).as_dict(),
                ]
                receipt = ledger.commit_generation(
                    expected_generation=0, expected_head="00" * 32,
                    intent_ref="step:1", current_state=state(step=1),
                    events=rows, status="dead",
                )
                self.assertEqual(receipt.status, "dead")
                self.assertEqual(ledger.export_canonical_journal(), journal.canonical_bytes())
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id="i0:birth:1",
            ) as ledger:
                self.assertEqual(ledger.audit().status, "dead")
                with self.assertRaises(RecoveryBlocked):
                    ledger.recover_current_bytes(expected_individual_id="i0:birth:1")
                with self.assertRaises(RecoveryBlocked):
                    ledger.begin_intent(expected_generation=1, intent_ref="step:2")

    def test_one_writer_per_identity_but_independent_readonly_audit(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "individual.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ) as ledger:
                receipt = SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id="i0:birth:1",
                )
                self.assertEqual(receipt.generation, 0)
                self.assertTrue(receipt.may_recover)
                with self.assertRaises(RecoveryBlocked):
                    SQLiteLifeLedger.open_existing(
                        path=path, expected_individual_id="i0:birth:1",
                    )
                ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                frozen = SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id="i0:birth:1",
                )
                self.assertTrue(frozen.pending_intent)
                self.assertFalse(frozen.may_recover)
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id="i0:birth:1",
            ) as ledger:
                self.assertEqual(ledger.seal_uncertain().status, "technical_halt")
            self.assertFalse(SQLiteLifeLedger.audit_read_only(
                path=path, expected_individual_id="i0:birth:1",
            ).may_recover)
            with self.assertRaises(RecoveryBlocked):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id="another-life",
                )

    def test_operator_cli_verifies_exact_anchor_without_loading_runtime(self):
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "operator-life.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id="i0:birth:1", initial_state=state(),
            ):
                command = [
                    sys.executable, "scripts/audit_i0_sqlite.py",
                    "--db", path, "--identity", "i0:birth:1",
                    "--expect-generation", "0", "--expect-head", "00" * 32,
                ]
                accepted = subprocess.run(
                    command, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(accepted.returncode, 0, accepted.stderr)
                report = json.loads(accepted.stdout)
                self.assertEqual(report["journal_count"], 0)
                self.assertTrue(report["may_recover"])
                self.assertEqual(
                    report["claim"],
                    "internal_consistency_only_not_independent_physical_truth",
                )
                rejected = subprocess.run(
                    command[:-1] + ["f" * 64],
                    capture_output=True, text=True, timeout=20,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("trusted operator anchor", rejected.stderr)

    def test_corrupted_state_and_chain_are_rejected(self):
        for corruption in ("state_hash", "event"):
            with self.subTest(corruption=corruption), TemporaryDirectory() as tmp:
                path = str(Path(tmp) / "individual.db")
                journal = HashChainedJournal()
                with SQLiteLifeLedger.birth(
                    path=path, individual_id="i0:birth:1", initial_state=state(),
                ) as ledger:
                    ledger.begin_intent(expected_generation=0, intent_ref="step:1")
                    ledger.commit_generation(
                        expected_generation=0, expected_head="00" * 32,
                        intent_ref="step:1", current_state=state(step=1),
                        events=[entry(journal, "event:1")],
                    )
                db = sqlite3.connect(path)
                if corruption == "state_hash":
                    db.execute("UPDATE life_current SET state_hash='bad'")
                else:
                    db.execute(
                        "UPDATE causal_occurrence SET event_hash=? WHERE idx=0",
                        ("f" * 64,),
                    )
                db.commit()
                db.close()
                with self.assertRaises(RecoveryBlocked):
                    SQLiteLifeLedger.open_existing(
                        path=path, expected_individual_id="i0:birth:1",
                    )

    def test_crash_windows_leave_uncertain_fence_or_complete_generation(self):
        child = r"""
import os, sys
from lab.journal import HashChainedJournal
from lab.sqlite_life_store import SQLiteLifeLedger

path, point = sys.argv[1:]
state = lambda n: {
    "individual_id": "i0:crash-test",
    "world": {"physical_step": n},
    "scheduler": {"t_monde": n},
    "owners": {"metacognition_health": {"cycle": n}},
}
def fault(where):
    if where == point:
        os._exit(71)
ledger = SQLiteLifeLedger.birth(
    path=path, individual_id="i0:crash-test", initial_state=state(0),
    fault=fault,
)
ledger.begin_intent(expected_generation=0, intent_ref="step:1")
j = HashChainedJournal()
event = j.append(event_id="step:1", causal_event={"kind": "test_causal_receipt", "t_monde": 1})
ledger.commit_generation(
    expected_generation=0, expected_head="00" * 32,
    intent_ref="step:1", current_state=state(1),
    events=[event.as_dict()],
)
os._exit(72)
"""
        cases = {
            "intent_after_commit": (0, True),
            "after_event_insert": (0, True),
            "after_current_update": (0, True),
            "before_commit": (0, True),
            "after_commit": (1, False),
        }
        for point, (generation, pending) in cases.items():
            with self.subTest(point=point), TemporaryDirectory() as tmp:
                path = str(Path(tmp) / "life.db")
                result = subprocess.run(
                    [sys.executable, "-c", child, path, point],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 71, result.stderr)
                with SQLiteLifeLedger.open_existing(
                    path=path, expected_individual_id="i0:crash-test",
                ) as ledger:
                    receipt = ledger.audit()
                    self.assertEqual(receipt.generation, generation)
                    self.assertEqual(receipt.pending_intent, pending)
                    self.assertEqual(receipt.journal_count, generation)
                    if pending:
                        with self.assertRaises(RecoveryBlocked):
                            ledger.recover_current_bytes(
                                expected_individual_id="i0:crash-test",
                            )
                        self.assertEqual(ledger.seal_uncertain().status, "technical_halt")
                    else:
                        self.assertEqual(
                            json.loads(ledger.recover_current_bytes(
                                expected_individual_id="i0:crash-test",
                            ))["world"]["physical_step"], 1,
                        )


if __name__ == "__main__":
    unittest.main()
