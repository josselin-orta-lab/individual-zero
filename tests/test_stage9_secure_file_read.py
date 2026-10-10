"""Synthetic descriptor-race tests; never physical heldout evidence."""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.journal import HashChainedJournal
from lab.stage9_canonical_journal_audit import audit_raw_causal_journal
from lab.stage9_heldout_artifact_custody import (
    _equal_bytes, _file_hash_and_size, _read_raw_bytes,
)
from lab.stage9_secure_file_read import open_regular_no_follow
from lab import stage9_secure_file_read as guarded


class Stage9SecureFileReadTests(unittest.TestCase):
    def test_regular_raw_evidence_can_still_be_hashed_compared_and_parsed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            primary = root / "original.bin"
            replay = root / "replay.bin"
            primary.write_bytes(b"synthetic-original-file")
            replay.write_bytes(primary.read_bytes())
            self.assertEqual(
                _file_hash_and_size(primary),
                (sha256(primary.read_bytes()).hexdigest(), len(primary.read_bytes())),
            )
            self.assertEqual(_read_raw_bytes(primary), primary.read_bytes())
            self.assertTrue(_equal_bytes(primary, replay))
            replay.write_bytes(b"changed")
            self.assertFalse(_equal_bytes(primary, replay))
            journal = HashChainedJournal()
            journal.append(
                event_id="synthetic-event-1",
                causal_event={"kind": "diagnostic_only"},
            )
            path = root / "synthetic-journal.jsonl"
            path.write_bytes(journal.canonical_bytes())
            result = audit_raw_causal_journal(
                path, physical_observation_refs=set(),
            )
            self.assertEqual(result["journal_events_checked"], 1)
            self.assertFalse(result["physical_truth_attested"])

    def test_leaf_and_parent_symlink_swap_during_open_are_rejected(self):
        # A preflight Path.is_symlink() would see an ordinary file. Inject
        # the substitution at the exact descriptor open to expose a TOCTOU.
        for scenario in ("leaf", "parent"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    subdir = root / "raw"
                    subdir.mkdir()
                    source = subdir / "original.bin"
                    source.write_bytes(b"synthetic-frozen-evidence")
                    relocated = (
                        root / "relocated-original.bin"
                        if scenario == "leaf" else root / "relocated-raw"
                    )
                    part = source.name if scenario == "leaf" else subdir.name
                    real_open = guarded.os.open
                    swapped = False

                    def replace_during_open(path, flags, *, dir_fd=None):
                        nonlocal swapped
                        if not swapped and path == part and dir_fd is not None:
                            swapped = True
                            victim = source if scenario == "leaf" else subdir
                            victim.rename(relocated)
                            victim.symlink_to(
                                relocated, target_is_directory=scenario == "parent",
                            )
                        return real_open(path, flags, dir_fd=dir_fd)

                    with patch.object(guarded.os, "open", side_effect=replace_during_open):
                        with self.assertRaisesRegex(ValueError, "symlink"):
                            _file_hash_and_size(source)
                    self.assertTrue(swapped)
                    self.assertTrue(source.is_symlink())

    def test_in_place_mutation_during_read_is_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "mutable.raw"
            path.write_bytes(b"original")
            with self.assertRaisesRegex(ValueError, "changed during descriptor read"):
                with open_regular_no_follow(path) as stream:
                    self.assertEqual(stream.read(), b"original")
                    path.write_bytes(b"original mutated")

    def test_symlinks_special_files_and_missing_files_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            real = root / "real.bin"
            real.write_bytes(b"synthetic")
            alias = root / "alias.bin"
            alias.symlink_to(real)
            with self.assertRaisesRegex(ValueError, "symlink"):
                _read_raw_bytes(alias)
            with self.assertRaises(ValueError):
                _read_raw_bytes(root / "missing.bin")
            with self.assertRaisesRegex(ValueError, "not a regular file"):
                _read_raw_bytes(root)
            if hasattr(os, "mkfifo"):
                pipe = root / "fake.raw"
                os.mkfifo(pipe)
                with self.assertRaisesRegex(ValueError, "not a regular file"):
                    _read_raw_bytes(pipe)

    def test_original_and_replay_comparison_cannot_follow_a_swapped_leaf(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source, replay, other = (
                root / "original.bin", root / "replay.bin", root / "elsewhere.bin",
            )
            for path in (source, replay, other):
                path.write_bytes(b"matching synthetic bytes")
            real_open = guarded.os.open
            replaced = False

            def hijack_replay(path, flags, *, dir_fd=None):
                nonlocal replaced
                if not replaced and path == replay.name and dir_fd is not None:
                    replaced = True
                    replay.unlink()
                    replay.symlink_to(other)
                return real_open(path, flags, dir_fd=dir_fd)

            with patch.object(guarded.os, "open", side_effect=hijack_replay):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    _equal_bytes(source, replay)
            self.assertTrue(replaced)


if __name__ == "__main__":
    unittest.main()
