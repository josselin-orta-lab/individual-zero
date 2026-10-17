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



_INDEX_H_SCRIPT = r"""
import os
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0, str(Path.cwd() / "tests"))
from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.consolidation_publication import Stage10PublicationCoordinator
from test_stage12_mortal_runtime import stage12_runtime
db, point = sys.argv[1:]
original = Stage10PublicationCoordinator.publish
seen = {"h": False}
def publish(self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    seen["h"] = True
    if point == "after_private_h":
        os._exit(76)
    return result
runtime = stage12_runtime(None, m11_sqlite_custody=True, paid_index=True)
with patch.object(Stage10PublicationCoordinator, "publish", publish), \
     M11TransactionalMortal.birth(
         db_path=db, runtime=runtime,
         individual_id="m11:stage12:indexed-h-crash",
     ) as life:
    for _ in range(65):
        def fault(location):
            if (point == "after_sql_h" and location == "after_sql_commit"
                    and seen["h"]):
                os._exit(76)
        life.run_step(test_fault=fault)
    raise AssertionError("no real h activation reached within 65 physical steps")
"""

class M11Stage12HardCrashTests(unittest.TestCase):
    def test_indexed_h_is_sqlite_atomic_across_actual_process_crashes(self):
        identity = "m11:stage12:indexed-h-crash"
        for point in ("after_private_h", "after_sql_h"):
            with self.subTest(point=point), TemporaryDirectory() as folder:
                database = str(Path(folder) / "indexed-current.db")
                child = subprocess.run(
                    [sys.executable, "-c", _INDEX_H_SCRIPT, database, point],
                    capture_output=True, text=True, timeout=180,
                )
                self.assertEqual(child.returncode, 76, child.stderr)
                with SQLiteLifeLedger.open_existing(
                    path=database, expected_individual_id=identity,
                ) as ledger:
                    audit = ledger.audit()
                    stored = ledger.export_canonical_journal()
                import json
                kinds = [json.loads(line)["causal_event"]["kind"]
                         for line in stored.splitlines()]
                activations = kinds.count("stage10_consolidation_version_activated")
                receipts = kinds.count("stage10_consolidation_index_retired")
                self.assertEqual(receipts, activations)
                if point == "after_private_h":
                    self.assertTrue(audit.pending_intent)
                    self.assertFalse(audit.may_recover)
                    self.assertEqual(activations, 0)
                    with self.assertRaises(RecoveryBlocked):
                        M11TransactionalMortal.cold_recover(
                            db_path=database, individual_id=identity,
                            runtime_factory=lambda: stage12_runtime(
                                None, m11_sqlite_custody=True, paid_index=True),
                        )
                else:
                    self.assertFalse(audit.pending_intent)
                    self.assertTrue(audit.may_recover)
                    self.assertEqual(activations, 1)
                    with M11TransactionalMortal.cold_recover(
                        db_path=database, individual_id=identity,
                        runtime_factory=lambda: stage12_runtime(
                            None, m11_sqlite_custody=True, paid_index=True),
                    ) as current:
                        self.assertEqual(current.inspect()["world_step"], audit.generation)
                        receipt = current.run_step()
                        self.assertEqual(receipt.generation, audit.generation + 1)

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
