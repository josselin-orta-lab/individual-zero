"""Synthetic Git fixtures for local Stage-9 source integrity preflight."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.stage9_frozen_worktree import verify_frozen_worktree
from tests.test_stage9_registration_chronology import _create_fixture, _git


class FrozenWorktreePreflightTests(unittest.TestCase):
    def test_clean_later_checkout_is_verified_without_scientific_certification(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            frozen, _, evidence = _create_fixture(repo)
            result = verify_frozen_worktree(
                repository=repo, frozen_implementation_commit=frozen,
            )
            self.assertEqual(result["git_head"], evidence)
            self.assertEqual(
                result["source_tree_sha"], _git(repo, "rev-parse", f"{frozen}:src"),
            )
            self.assertEqual(
                result["pyproject_blob_sha"],
                _git(repo, "rev-parse", f"{frozen}:pyproject.toml"),
            )
            self.assertGreaterEqual(result["verified_tracked_files"], 2)
            self.assertEqual(
                result["worktree_status"],
                "frozen_tracked_code_matches_local_checkout",
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertTrue(result["outstanding"])

    def test_uncommitted_tracked_source_or_packaging_change_fails(self):
        for name in ("src/engine.py", "pyproject.toml"):
            with self.subTest(name=name):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    frozen, _, _ = _create_fixture(repo)
                    target = repo / name
                    target.write_bytes(target.read_bytes() + b"\n# altered\n")
                    with self.assertRaisesRegex(ValueError, "local Git changes"):
                        verify_frozen_worktree(
                            repository=repo, frozen_implementation_commit=frozen,
                        )

    def test_staged_change_and_deleted_source_fail(self):
        for deleted in (False, True):
            with self.subTest(deleted=deleted):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    frozen, _, _ = _create_fixture(repo)
                    source = repo / "src" / "engine.py"
                    if deleted:
                        source.unlink()
                    else:
                        source.write_text("print('changed')\n", encoding="utf-8")
                    _git(repo, "add", "-A", "src")
                    with self.assertRaisesRegex(ValueError, "local Git changes"):
                        verify_frozen_worktree(
                            repository=repo, frozen_implementation_commit=frozen,
                        )

    def test_untracked_python_and_ignored_python_are_refused(self):
        for ignored in (False, True):
            with self.subTest(ignored=ignored):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    frozen, _, _ = _create_fixture(repo)
                    if ignored:
                        (repo / ".gitignore").write_text(
                            "src/rogue.py\n", encoding="utf-8",
                        )
                    (repo / "src" / "rogue.py").write_text(
                        "print('not frozen')\n", encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        ValueError, "untracked executable source|local Git changes",
                    ):
                        verify_frozen_worktree(
                            repository=repo, frozen_implementation_commit=frozen,
                        )

    def test_untracked_non_source_document_does_not_invalidate_worktree(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            frozen, _, _ = _create_fixture(repo)
            (repo / "unrelated-notes.txt").write_text("note\n", encoding="utf-8")
            result = verify_frozen_worktree(
                repository=repo, frozen_implementation_commit=frozen,
            )
            self.assertIsNone(result["scientific_verdict"])

    def test_head_with_committed_source_change_is_rejected(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            frozen, _, _ = _create_fixture(repo)
            source = repo / "src" / "engine.py"
            source.write_text("print('modified')\n", encoding="utf-8")
            _git(repo, "add", "src/engine.py")
            _git(repo, "commit", "-qm", "modify implementation")
            with self.assertRaisesRegex(ValueError, "current HEAD differs"):
                verify_frozen_worktree(
                    repository=repo, frozen_implementation_commit=frozen,
                )

    def test_invalid_sha_and_nested_directory_are_not_accepted(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            frozen, _, _ = _create_fixture(repo)
            for sha in ("not-a-sha", "f" * 40):
                with self.subTest(sha=sha):
                    with self.assertRaises(ValueError):
                        verify_frozen_worktree(
                            repository=repo, frozen_implementation_commit=sha,
                        )
            with self.assertRaisesRegex(ValueError, "worktree root"):
                verify_frozen_worktree(
                    repository=repo / "src",
                    frozen_implementation_commit=frozen,
                )


if __name__ == "__main__":
    unittest.main()
