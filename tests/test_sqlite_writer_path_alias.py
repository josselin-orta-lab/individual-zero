"""One physical SQLite life must have exactly one active writer lease.

SQLite path aliases must not create independent per-filename leases for the
same underlying database. Each test uses a new isolated temporary directory.
These are storage integrity checks, not live M-11 recovery certification.
"""
from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


IDENTITY = "i0:m11:unique-writer-path"


def genesis():
    return {
        "individual_id": IDENTITY,
        "world": {"physical_step": 0},
        "scheduler": {"t_monde": 0},
        "owners": {"metacognition_health": {"cycle": 0}},
    }


class SQLiteWriterPathAliasTests(unittest.TestCase):
    def test_symlink_alias_cannot_open_second_live_writer(self):
        with TemporaryDirectory() as directory:
            actual = Path(directory) / "life.db"
            alias = Path(directory) / "life-alias.db"
            with SQLiteLifeLedger.birth(
                path=str(actual), individual_id=IDENTITY, initial_state=genesis(),
            ) as first:
                alias.symlink_to(actual)
                self.assertTrue(alias.is_file())
                # An operator read via the alias must see the SAME SQLite
                # transaction/WAL snapshot, not an alternate alias-WAL.
                same = SQLiteLifeLedger.audit_read_only(
                    path=str(alias), expected_individual_id=IDENTITY,
                )
                self.assertEqual(same.generation, first.audit().generation)
                self.assertEqual(same.journal_head, first.audit().journal_head)
                with self.assertRaisesRegex(RecoveryBlocked, "active process writer"):
                    SQLiteLifeLedger.open_existing(
                        path=str(alias), expected_individual_id=IDENTITY,
                    )
                self.assertTrue(first.audit().may_recover)

    def test_hardlink_alias_cannot_open_second_live_writer(self):
        with TemporaryDirectory() as directory:
            actual = Path(directory) / "life.db"
            alias = Path(directory) / "life-hardlink.db"
            with SQLiteLifeLedger.birth(
                path=str(actual), individual_id=IDENTITY, initial_state=genesis(),
            ) as first:
                os.link(actual, alias)
                self.assertEqual(actual.stat().st_ino, alias.stat().st_ino)
                # A hardlinked filename gives SQLite a different sidecar,
                # so do not even open it as a supposedly read-only auditor.
                with self.assertRaisesRegex(RecoveryBlocked, "hardlink"):
                    SQLiteLifeLedger.audit_read_only(
                        path=str(alias), expected_individual_id=IDENTITY,
                    )
                with self.assertRaisesRegex(RecoveryBlocked, "hardlink|active process writer"):
                    SQLiteLifeLedger.open_existing(
                        path=str(alias), expected_individual_id=IDENTITY,
                    )
                self.assertTrue(first.audit().may_recover)

    def test_birth_via_symlinked_directory_uses_same_lease_identity(self):
        with TemporaryDirectory() as directory:
            actual_dir = Path(directory) / "actual"
            actual_dir.mkdir()
            alias_dir = Path(directory) / "linked"
            alias_dir.symlink_to(actual_dir, target_is_directory=True)
            alias_path = alias_dir / "life.db"
            actual_path = actual_dir / "life.db"
            with SQLiteLifeLedger.birth(
                path=str(alias_path), individual_id=IDENTITY,
                initial_state=genesis(),
            ) as first:
                self.assertEqual(first.path, str(actual_path))
                with self.assertRaisesRegex(RecoveryBlocked, "active process writer"):
                    SQLiteLifeLedger.open_existing(
                        path=str(actual_path), expected_individual_id=IDENTITY,
                    )


if __name__ == "__main__":
    unittest.main()
