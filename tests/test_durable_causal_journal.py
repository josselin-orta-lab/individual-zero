"""Exclusive crash-durable append-only causal journal (software contract)."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lab.journal import HashChainedJournal


class DurableJournalTests(unittest.TestCase):
    def test_abrupt_process_exit_preserves_acknowledged_journal_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "i0-life.jsonl")
            child = (
                "import os, sys\n"
                "from lab.journal import HashChainedJournal\n"
                "journal = HashChainedJournal()\n"
                "journal.enable_durable_wal(path=sys.argv[1])\n"
                "for i in range(20):\n"
                "    journal.append(event_id='event:' + str(i), causal_event={"
                "'kind':'lived', 't_monde':i, 'data':{'n':i}})\n"
                "os._exit(0)\n"
            )
            subprocess.run(
                [sys.executable, "-c", child, path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            result = HashChainedJournal.audit_durable_wal(path)
            self.assertEqual(result["verified_entries"], 20)
            self.assertEqual(len(result["head_hash"]), 64)
            with self.assertRaises(FileExistsError):
                HashChainedJournal().enable_durable_wal(path=path)
            if os.name == "posix":
                self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)

    def test_tampering_and_torn_last_record_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.jsonl")
            journal = HashChainedJournal()
            journal.enable_durable_wal(path=path)
            journal.append(event_id="first", causal_event={"kind": "world_step", "t_monde": 1})
            original = Path(path).read_bytes()
            self.assertTrue(original.endswith(b"\n"))
            self.assertEqual(HashChainedJournal.audit_durable_wal(path)["verified_entries"], 1)
            Path(path).write_bytes(original[:-1])
            with self.assertRaises(ValueError):
                HashChainedJournal.audit_durable_wal(path)
            Path(path).write_bytes(original.replace(b"world_step", b"fake_step"))
            with self.assertRaises(ValueError):
                HashChainedJournal.audit_durable_wal(path)
            Path(path).write_bytes(original + original)
            with self.assertRaises(ValueError):
                HashChainedJournal.audit_durable_wal(path)

    def test_activation_is_birth_only_and_io_failure_poison_is_permanent(self):
        with tempfile.TemporaryDirectory() as directory:
            old = HashChainedJournal()
            old.append(event_id="old", causal_event={"kind": "old"})
            with self.assertRaises(ValueError):
                old.enable_durable_wal(path=str(Path(directory) / "old.jsonl"))
            path = str(Path(directory) / "new.jsonl")
            journal = HashChainedJournal()
            journal.enable_durable_wal(path=path)
            self.assertTrue(journal.durable_wal_enabled)
            with patch("lab.journal.os.fsync", side_effect=OSError("injected I/O failure")):
                with self.assertRaises(OSError):
                    journal.append(event_id="uncommitted", causal_event={"kind": "test"})
            self.assertFalse(journal.verify())
            self.assertEqual(journal.entries, ())
            with self.assertRaises(RuntimeError):
                journal.append(event_id="later", causal_event={"kind": "test"})
            self.assertEqual(journal.entries, ())


if __name__ == "__main__":
    unittest.main()
