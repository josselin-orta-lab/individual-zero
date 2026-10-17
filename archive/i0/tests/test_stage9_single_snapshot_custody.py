"""Synthetic Stage-9 custody regression tests, never scientific evidence."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from lab.determinism import canonical_causal_bytes
from lab import stage9_heldout_artifact_custody as custody
from lab.stage9_memory_custody import audit_archived_closed_memory_sources
from tests.test_stage9_heldout_artifact_custody import _prepared


class Stage9SingleSnapshotCustodyTests(unittest.TestCase):
    def test_each_causal_owner_file_is_parsed_from_one_verified_byte_image(self):
        # Before this change one owner-state file was independently parsed
        # twice, then read a third time through the standalone Memory audit.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            expected_paths = {
                root / row["causal_state_path"] for row in index["runs"]
            }
            original_reader = custody._read_raw_bytes
            reads: dict[Path, int] = {}

            def counted_reader(path: Path) -> bytes:
                if path in expected_paths:
                    reads[path] = reads.get(path, 0) + 1
                return original_reader(path)

            with patch.object(
                custody, "_read_raw_bytes", side_effect=counted_reader,
            ):
                result = custody.audit_heldout_raw_artifacts(
                    registration=registration,
                    evidence=report,
                    index=index,
                    artifact_root=root,
                )
            self.assertEqual(result["runs_checked"], len(index["runs"]))
            self.assertEqual(reads, {path: 1 for path in expected_paths})
            self.assertFalse(result["physical_truth_attested"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_swapped_parser_image_fails_digest_even_if_disk_never_changes(self):
        # Model a transient substitute returned by the parser read after the
        # first SHA check. The physical files stay exactly as registered.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            target = root / index["runs"][0]["causal_state_path"]
            original_bytes = target.read_bytes()
            fake = json.loads(original_bytes)
            fake["synthetic_transient_extra_field"] = True
            injected_bytes = canonical_causal_bytes(fake)
            self.assertNotEqual(injected_bytes, original_bytes)
            original_reader = custody._read_raw_bytes
            injected = False

            def substitute_once(path: Path) -> bytes:
                nonlocal injected
                if path == target and not injected:
                    injected = True
                    return injected_bytes
                return original_reader(path)

            with patch.object(
                custody, "_read_raw_bytes", side_effect=substitute_once,
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "owner-state bytes changed between custody hash and parsing",
                ):
                    custody.audit_heldout_raw_artifacts(
                        registration=registration, evidence=report,
                        index=index, artifact_root=root,
                    )
            self.assertTrue(injected)
            self.assertEqual(target.read_bytes(), original_bytes)


    def test_journal_custody_passes_verified_image_without_reopening_parser(self):
        # A fresh path open inside the journal parser used to observe bytes
        # different from the digest-checked image. Retain the standalone
        # guarded entrypoint, but never use it for a parent custody audit.
        from lab import stage9_canonical_journal_audit as journal
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            originals = {root / row["journal_path"] for row in index["runs"]}
            journal_reads: dict[Path, int] = {}
            original_reader = custody._read_raw_bytes

            def count_journal_reads(path: Path) -> bytes:
                if path in originals:
                    journal_reads[path] = journal_reads.get(path, 0) + 1
                return original_reader(path)

            with patch.object(custody, "_read_raw_bytes", side_effect=count_journal_reads):
                with patch.object(
                    journal, "open_regular_no_follow",
                    side_effect=AssertionError(
                        "custody may not reopen journal inside source parser"
                    ),
                ):
                    result = custody.audit_heldout_raw_artifacts(
                        registration=registration, evidence=report,
                        index=index, artifact_root=root,
                    )
            self.assertEqual(result["runs_checked"], len(index["runs"]))
            self.assertEqual(journal_reads, {path: 1 for path in originals})
            self.assertFalse(result["physical_truth_attested"])

    def test_swapped_journal_image_cannot_pass_initial_and_final_file_hashes(self):
        # Model a transient equal-size image substitution after the initial
        # disk SHA check. The last disk read would still see original bytes.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            target = root / index["runs"][0]["journal_path"]
            original = target.read_bytes()
            substituted = b"X" + original[1:]
            self.assertEqual(len(substituted), len(original))
            real_reader = custody._read_raw_bytes
            applied = False

            def inject_once(path: Path) -> bytes:
                nonlocal applied
                if path == target and not applied:
                    applied = True
                    return substituted
                return real_reader(path)

            with patch.object(custody, "_read_raw_bytes", side_effect=inject_once):
                with self.assertRaisesRegex(
                    ValueError,
                    "journal bytes changed between custody hash and parsing",
                ):
                    custody.audit_heldout_raw_artifacts(
                        registration=registration, evidence=report,
                        index=index, artifact_root=root,
                    )
            self.assertTrue(applied)
            self.assertEqual(target.read_bytes(), original)

    def test_standalone_memory_file_reader_refuses_symlink(self):
        # The standalone path reader must not bypass the no-follow guard.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            _registration, _report, index = _prepared(root)
            original = root / index["runs"][0]["causal_state_path"]
            alias = root / "alias.json"
            try:
                alias.symlink_to(original)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(ValueError, "symlink"):
                audit_archived_closed_memory_sources(
                    alias,
                    claimed_episodes={},
                    physical_source_provenance={},
                )


if __name__ == "__main__":
    unittest.main()
