"""Real Stage12 SQLite M11 os._exit matrix; no standalone Stage12 WAL.

Each subprocess creates a distinct mortal identity/SQLite file. No child
execution is replayed. Readonly SQLite audit governs cold recovery.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from test_stage12_mortal_runtime import stage12_runtime


POINTS = (
    "after_intent", "before_private_execution",
    "after_private_execution", "before_sql_commit",
    "after_sql_commit", "after_publication",
)
_ID = "m11:stage12:hard-crash:current"

_SCRIPT = r"""
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / "tests"))
from lab.m11_transactional_mortal import M11TransactionalMortal
from test_stage12_mortal_runtime import stage12_runtime
db, point = sys.argv[1:]
runtime = stage12_runtime(None, m11_sqlite_custody=True)
with M11TransactionalMortal.birth(
    db_path=db, runtime=runtime,
    individual_id="m11:stage12:hard-crash:current",
) as life:
    def killed(at):
        if at == point:
            os._exit(76)
    life.run_step(test_fault=killed)
    raise AssertionError("expected actual os._exit boundary")
"""


class M11Stage12HardCrashTests(unittest.TestCase):
    def test_six_actual_process_exits_resolve_only_current_atomic_generation(self):
        for point in POINTS:
            with self.subTest(point=point), TemporaryDirectory() as folder:
                database = str(Path(folder) / "one-stage12.db")
                child = subprocess.run(
                    [sys.executable, "-c", _SCRIPT, database, point],
                    capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(child.returncode, 76, child.stderr)
                audit = SQLiteLifeLedger.audit_read_only(
                    path=database, expected_individual_id=_ID)
                self.assertTrue(Path(database).exists())
                if point in ("after_sql_commit", "after_publication"):
                    self.assertEqual(audit.generation, 1)
                    self.assertFalse(audit.pending_intent)
                    self.assertTrue(audit.may_recover)
                    with M11TransactionalMortal.cold_recover(
                        db_path=database, individual_id=_ID,
                        runtime_factory=lambda: stage12_runtime(
                            None, m11_sqlite_custody=True),
                    ) as current:
                        self.assertEqual(current.inspect()["world_step"], 1)
                        receipt = current.run_step()
                        self.assertEqual(receipt.generation, 2)
                        self.assertEqual(receipt.world_step, 2)
                else:
                    self.assertEqual(audit.generation, 0)
                    self.assertTrue(audit.pending_intent)
                    self.assertFalse(audit.may_recover)
                    with self.assertRaises(RecoveryBlocked):
                        M11TransactionalMortal.cold_recover(
                            db_path=database, individual_id=_ID,
                            runtime_factory=lambda: stage12_runtime(
                                None, m11_sqlite_custody=True),
                        )


if __name__ == "__main__":
    unittest.main()
