"""Real os._exit death windows for isolated SQLite custody (not M-11 PASS).

No WorldBody is mutated here; these prove only that the storage transaction
does not advertise an uncommitted fatal generation as a recoverable life.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.journal import GENESIS_HASH
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


IDENTITY = "i0:sqlite:terminal-crash"


class SQLiteTerminalCrashTests(unittest.TestCase):
    def test_fatal_generation_crash_windows_never_resurrect(self):
        child = r"""
import os, sys
from lab.journal import HashChainedJournal, GENESIS_HASH
from lab.sqlite_life_store import SQLiteLifeLedger

path, point = sys.argv[1:]
identity = "i0:sqlite:terminal-crash"
def state(step):
    return {
        "individual_id": identity,
        "world": {"physical_step": step, "integrity": 0 if step else 100},
        "scheduler": {"t_monde": step},
        "owners": {"metacognition_health": {"cycle": 0}},
    }
def exit_at(where):
    if where == point:
        os._exit(73)
ledger = SQLiteLifeLedger.birth(
    path=path, individual_id=identity, initial_state=state(0),
    fault=exit_at,
)
ledger.begin_intent(expected_generation=0, intent_ref="fatal:step:1")
j = HashChainedJournal()
death = j.append(
    event_id="death:1", causal_event={
        "kind": "individual_death_confirmed",
        "t_monde": 1, "attempt_ref": "attempt:1",
    },
).as_dict()
close = j.append(
    event_id="close:1", causal_event={
        "kind": "step_closed", "t_monde": 1,
        "attempt_ref": "attempt:1", "data": {
            "outcome": "dead", "applied_command_count": 1,
            "world_advance_count": 1,
        },
    },
).as_dict()
ledger.commit_generation(
    expected_generation=0, expected_head=GENESIS_HASH,
    intent_ref="fatal:step:1", current_state=state(1),
    events=[death, close], status="dead",
)
os._exit(74)
"""
        cases = {
            "intent_after_commit": False,
            "after_event_insert": False,
            "after_current_update": False,
            "before_commit": False,
            "after_commit": True,
        }
        for point, final_commit in cases.items():
            with self.subTest(window=point), TemporaryDirectory() as directory:
                path = str(Path(directory) / "life.db")
                proc = subprocess.run(
                    [sys.executable, "-c", child, path, point],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(proc.returncode, 73, proc.stderr)
                with SQLiteLifeLedger.open_existing(
                    path=path, expected_individual_id=IDENTITY,
                ) as ledger:
                    receipt = ledger.audit()
                    self.assertFalse(receipt.may_recover)
                    with self.assertRaises(RecoveryBlocked):
                        ledger.recover_current_bytes(
                            expected_individual_id=IDENTITY,
                        )
                    if not final_commit:
                        self.assertEqual(receipt.generation, 0)
                        self.assertEqual(receipt.journal_head, GENESIS_HASH)
                        self.assertEqual(receipt.journal_count, 0)
                        self.assertEqual(receipt.status, "active")
                        self.assertTrue(receipt.pending_intent)
                        halted = ledger.seal_uncertain()
                        self.assertEqual(halted.status, "technical_halt")
                        self.assertTrue(halted.pending_intent)
                    else:
                        self.assertEqual(receipt.generation, 1)
                        self.assertEqual(receipt.status, "dead")
                        self.assertFalse(receipt.pending_intent)
                        self.assertEqual(receipt.journal_count, 2)
                        rows = [
                            json.loads(row)
                            for row in ledger.export_canonical_journal().split(b"\n")
                        ]
                        self.assertEqual(
                            [r["causal_event"]["kind"] for r in rows],
                            ["individual_death_confirmed", "step_closed"],
                        )
                        self.assertEqual(
                            rows[-1]["event_hash"], receipt.journal_head,
                        )
                    with self.assertRaises(RecoveryBlocked):
                        ledger.begin_intent(
                            expected_generation=receipt.generation,
                            intent_ref="forbidden-retry",
                        )


if __name__ == "__main__":
    unittest.main()
