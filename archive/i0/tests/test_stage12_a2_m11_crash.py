"""Hard-kill A2 M11 custody: after-intent and after-SQL-commit boundaries."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_first_planning_state import build_life
from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from lab.stage12_a2_causal_audit import audit_stage12_a2_causal_link

IDENTITY = "i0:issue110:a2:m11-crash-fixture"
CHILD = r"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "scripts"))
from run_stage12_issue110_first_planning_state import build_life
from lab.m11_transactional_mortal import M11TransactionalMortal
db, identity, fault = sys.argv[1:]
life = build_life("near_food_free", 70.0, "horizon_three",
    wal_path=None, m11_sqlite_custody=True, birth_life_id=identity,
    a2_external_obstacle=True)[0]
with M11TransactionalMortal.birth(db_path=db, runtime=life, individual_id=identity) as owner:
    assert owner.run_step().generation == 1
    def killer(point):
        if point == fault: os._exit(73)
    owner.run_step(test_fault=killer)
    raise RuntimeError("expected os._exit")
"""

def fresh():
    return build_life("near_food_free", 70.0, "horizon_three",
        wal_path=None, m11_sqlite_custody=True, birth_life_id=IDENTITY,
        a2_external_obstacle=True)[0]


class A2CrashAtomicity(unittest.TestCase):
    def test_precommit_is_unrecoverable_and_committed_a2_exact_once(self):
        for fault, generation, recoverable in (
            ("after_private_execution", 1, False),
            ("after_sql_commit", 2, True),
        ):
            with self.subTest(fault=fault), TemporaryDirectory() as temp:
                db = str(Path(temp) / "life.sqlite")
                process = subprocess.run(
                    [sys.executable, "-c", CHILD, db, IDENTITY, fault],
                    capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(process.returncode, 73, process.stderr)
                state = SQLiteLifeLedger.audit_read_only(
                    path=db, expected_individual_id=IDENTITY)
                self.assertEqual(state.generation, generation)
                self.assertEqual(state.may_recover, recoverable)
                with SQLiteLifeLedger.open_existing(
                    path=db, expected_individual_id=IDENTITY) as ledger:
                    raw = ledger.export_canonical_journal()
                kinds = [__import__("json").loads(line)["causal_event"].get("kind")
                         for line in raw.splitlines()]
                self.assertEqual(kinds.count("external_input_applied"),
                                 int(recoverable))
                if recoverable:
                    report = audit_stage12_a2_causal_link(
                        raw, expected_interventions=((2,3,1),))
                    self.assertEqual(report.correctly_ordered_interventions, 1)
                    with M11TransactionalMortal.cold_recover(
                        db_path=db, individual_id=IDENTITY,
                        runtime_factory=fresh) as owner:
                        self.assertEqual(owner.inspect()["generation"], 2)
                        self.assertEqual(owner.run_step().generation, 3)
                else:
                    with self.assertRaises(RecoveryBlocked):
                        M11TransactionalMortal.cold_recover(
                            db_path=db, individual_id=IDENTITY,
                            runtime_factory=fresh)

if __name__ == "__main__":
    unittest.main()
