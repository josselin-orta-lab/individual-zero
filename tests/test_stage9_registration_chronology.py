"""Git-ancestry tests use disposable commits and synthetic metrics only.

These fixtures are not scientific data, an approved protocol or a Golden.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from lab.stage9_registration_chronology import audit_registration_chronology
from tests.test_stage9_scientific_preregistration import example_draft
from tests.test_stage9_scientific_assessment import make_report


def _git(repo: Path, *command: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), *command),
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _create_fixture(repo: Path) -> tuple[str, str, str]:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Stage 9 Test")
    _git(repo, "config", "user.email", "stage9@example.invalid")
    (repo / "frozen-implementation.txt").write_text("frozen software\n", encoding="utf-8")
    _git(repo, "add", "frozen-implementation.txt")
    _git(repo, "commit", "-qm", "freeze implementation")
    implementation = _git(repo, "rev-parse", "HEAD")

    draft = example_draft()
    draft["frozen_implementation_commit"] = implementation
    (repo / "research").mkdir()
    (repo / "research" / "registration.json").write_text(
        json.dumps(draft, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    _git(repo, "add", "research/registration.json")
    _git(repo, "commit", "-qm", "preregister protocol")
    registration_commit = _git(repo, "rev-parse", "HEAD")

    (repo / "results").mkdir()
    (repo / "results" / "heldout.json").write_text(
        json.dumps(make_report(draft, candidates=20), sort_keys=True, indent=2)
        + "\n", encoding="utf-8",
    )
    _git(repo, "add", "results/heldout.json")
    _git(repo, "commit", "-qm", "archive claimed heldout data")
    evidence_commit = _git(repo, "rev-parse", "HEAD")
    return implementation, registration_commit, evidence_commit


def _audit(repo: Path, registration: str, evidence: str) -> dict[str, object]:
    return audit_registration_chronology(
        repository=repo,
        registration_path=Path("research/registration.json"),
        registration_commit=registration,
        evidence_path=Path("results/heldout.json"),
        evidence_commit=evidence,
    )


class Stage9RegistrationChronologyTests(unittest.TestCase):
    def test_exact_ancestor_chain_still_cannot_self_certify_golden(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            freeze, registered, evidence = _create_fixture(repo)
            result = _audit(repo, registered, evidence)
            self.assertEqual(result["frozen_implementation_commit"], freeze)
            self.assertEqual(result["registration_commit"], registered)
            self.assertEqual(result["evidence_commit"], evidence)
            self.assertEqual(
                result["chronology_status"],
                "git_lineage_consistent_requires_independent_review",
            )
            self.assertFalse(result["evidence_path_present_at_registration"])
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertTrue(result["outstanding"])
            self.assertNotEqual(result["provisional_metric_assessment"], "accepted")

    def test_uncommitted_changes_cannot_change_sealed_protocol_or_evidence(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(repo)
            protocol = repo / "research" / "registration.json"
            evidence_file = repo / "results" / "heldout.json"
            original_protocol = protocol.read_bytes()
            original_evidence = evidence_file.read_bytes()
            protocol.write_bytes(original_protocol + b" ")
            with self.assertRaisesRegex(ValueError, "registration bytes"):
                _audit(repo, registered, evidence)
            protocol.write_bytes(original_protocol)
            evidence_file.write_bytes(original_evidence + b" ")
            with self.assertRaisesRegex(ValueError, "heldout evidence bytes"):
                _audit(repo, registered, evidence)

    def test_wrong_order_and_unknown_git_commits_fail(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            freeze, registered, evidence = _create_fixture(repo)
            for early, late in (
                (registered, registered), (evidence, registered),
                (freeze, evidence),
            ):
                with self.subTest(early=early, late=late):
                    with self.assertRaises(ValueError):
                        _audit(repo, early, late)
            with self.assertRaises(ValueError):
                _audit(repo, "f" * 40, evidence)
            with self.assertRaises(ValueError):
                _audit(repo, "not-a-full-commit", evidence)

    def test_registration_change_committed_with_evidence_is_rejected(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, _ = _create_fixture(repo)
            path = repo / "research" / "registration.json"
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            _git(repo, "add", "research/registration.json")
            _git(repo, "commit", "-qm", "tamper registered protocol")
            altered = _git(repo, "rev-parse", "HEAD")
            with self.assertRaisesRegex(ValueError, "registration bytes"):
                _audit(repo, registered, altered)

    def test_transient_committed_registration_edit_cannot_be_reverted_away(self):
        # Endpoints have identical protocol bytes. Inspecting only the
        # registration and evidence commits would silently accept this
        # retrospective modification of supposedly frozen rules.
        for modification in ("rewrite", "delete"):
            with self.subTest(modification=modification):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, sealed, _ = _create_fixture(repo)
                    path = repo / "research" / "registration.json"
                    original = path.read_bytes()
                    if modification == "delete":
                        _git(repo, "rm", "research/registration.json")
                    else:
                        path.write_bytes(original + b" ")
                        _git(repo, "add", "research/registration.json")
                    _git(repo, "commit", "-qm", "tamper with registered protocol")
                    # git rm removes the now-empty research directory. Restore
                    # the parent directory before recreating its frozen file.
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(original)
                    _git(repo, "add", "research/registration.json")
                    _git(repo, "commit", "-qm", "restore original registered bytes")
                    evidence = _git(repo, "rev-parse", "HEAD")
                    self.assertEqual(path.read_bytes(), original)
                    with self.assertRaisesRegex(
                        ValueError, "registration changed|registration removed",
                    ):
                        _audit(repo, sealed, evidence)

    def test_unrelated_intermediate_commit_preserves_valid_lineage(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, sealed, _ = _create_fixture(repo)
            (repo / "unrelated.txt").write_text(
                "An unrelated documentation change.\n", encoding="utf-8",
            )
            _git(repo, "add", "unrelated.txt")
            _git(repo, "commit", "-qm", "unrelated intervening work")
            evidence = _git(repo, "rev-parse", "HEAD")
            result = _audit(repo, sealed, evidence)
            self.assertEqual(
                result["chronology_status"],
                "git_lineage_consistent_requires_independent_review",
            )
            self.assertEqual(
                result["registration_unchanged_descendant_commits_checked"], 2,
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_paths_outside_worktree_are_rejected(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder) / "repo"
            repo.mkdir()
            _, registered, evidence = _create_fixture(repo)
            with self.assertRaisesRegex(ValueError, "inside the repository"):
                audit_registration_chronology(
                    repository=repo,
                    registration_path=Path("../outside-registration.json"),
                    registration_commit=registered,
                    evidence_path=Path("results/heldout.json"),
                    evidence_commit=evidence,
                )


if __name__ == "__main__":
    unittest.main()
