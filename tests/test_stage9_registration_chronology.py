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
from lab.stage9_scientific_preregistration import SPEC_PATH
from tests.test_stage9_scientific_preregistration import example_draft
from tests.test_stage9_scientific_assessment import make_report


def _git(repo: Path, *command: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), *command),
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _create_fixture(
    repo: Path, *, source_tree: bool = True,
    modify_before_registration: bool = False,
    project_installer: bool = True,
    normative_specification: bool = True,
    alter_frozen_normative: bool = False,
    modify_normative_before_registration: bool = False,
) -> tuple[str, str, str]:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Stage 9 Test")
    _git(repo, "config", "user.email", "stage9@example.invalid")
    (repo / "frozen-implementation.txt").write_text("frozen software\n", encoding="utf-8")
    _git(repo, "add", "frozen-implementation.txt")
    if project_installer:
        (repo / "pyproject.toml").write_text(
            "[project]\nname = 'individual-zero'\n", encoding="utf-8",
        )
        _git(repo, "add", "pyproject.toml")
    if source_tree:
        (repo / "src").mkdir()
        (repo / "src" / "engine.py").write_text(
            "print('frozen source')\n", encoding="utf-8",
        )
        _git(repo, "add", "src/engine.py")
    if normative_specification:
        normative = repo / SPEC_PATH
        normative.parent.mkdir(parents=True, exist_ok=True)
        original_spec = (
            Path(__file__).resolve().parents[1] / SPEC_PATH
        ).read_bytes()
        normative.write_bytes(
            original_spec + b"\n# synthetic divergent normative byte\n"
            if alter_frozen_normative else original_spec
        )
        _git(repo, "add", SPEC_PATH)
    _git(repo, "commit", "-qm", "freeze implementation")
    implementation = _git(repo, "rev-parse", "HEAD")
    if modify_normative_before_registration:
        normative = repo / SPEC_PATH
        normative.write_bytes(normative.read_bytes() + b"\n# unsealed change\n")
        _git(repo, "add", SPEC_PATH)
        _git(repo, "commit", "-qm", "mutate normative rules after freeze")
    if modify_before_registration:
        (repo / "src" / "engine.py").write_text(
            "print('changed before registration')\n", encoding="utf-8",
        )
        _git(repo, "add", "src/engine.py")
        _git(repo, "commit", "-qm", "unsealed source change")

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
            self.assertEqual(
                result["frozen_source_tree_sha"],
                _git(repo, "rev-parse", f"{freeze}:src"),
            )
            self.assertEqual(
                result["frozen_pyproject_blob_sha"],
                _git(repo, "rev-parse", f"{freeze}:pyproject.toml"),
            )
            self.assertEqual(
                result["frozen_normative_specification_blob_sha"],
                _git(repo, "rev-parse", f"{freeze}:{SPEC_PATH}"),
            )
            self.assertEqual(
                result["normative_specification_unchanged_descendant_commits_checked"],
                2,
            )
            self.assertEqual(
                result["source_tree_unchanged_descendant_commits_checked"], 2,
            )
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

    def test_changes_to_source_before_registration_are_rejected(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(
                repo, modify_before_registration=True,
            )
            with self.assertRaisesRegex(ValueError, "frozen source tree changed"):
                _audit(repo, registered, evidence)

    def test_frozen_normative_specification_cannot_be_missing_or_forged(self):
        for mode in ("missing", "wrong_digest", "changed_before_registration"):
            with self.subTest(mode=mode):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo,
                        normative_specification=mode != "missing",
                        alter_frozen_normative=mode == "wrong_digest",
                        modify_normative_before_registration=(
                            mode == "changed_before_registration"
                        ),
                    )
                    reason = {
                        "missing": "frozen normative specification missing",
                        "wrong_digest": "normative specification digest disagrees",
                        "changed_before_registration": "normative specification changed",
                    }[mode]
                    with self.assertRaisesRegex(ValueError, reason):
                        _audit(repo, registered, evidence)

    def test_transient_normative_specification_edit_or_deletion_is_rejected(self):
        for mode in ("rewrite", "delete"):
            with self.subTest(mode=mode):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, _ = _create_fixture(repo)
                    normative = repo / SPEC_PATH
                    original = normative.read_bytes()
                    if mode == "delete":
                        _git(repo, "rm", SPEC_PATH)
                    else:
                        normative.write_bytes(original + b"\n# temporary rules\n")
                        _git(repo, "add", SPEC_PATH)
                    _git(repo, "commit", "-qm", "temporarily modify normative rules")
                    normative.parent.mkdir(parents=True, exist_ok=True)
                    normative.write_bytes(original)
                    _git(repo, "add", SPEC_PATH)
                    _git(repo, "commit", "-qm", "restore original normative rules")
                    with self.assertRaisesRegex(
                        ValueError,
                        "normative specification changed|normative specification missing",
                    ):
                        _audit(repo, registered, _git(repo, "rev-parse", "HEAD"))

    def test_frozen_commit_without_source_tree_fails_closed(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(repo, source_tree=False)
            with self.assertRaisesRegex(ValueError, "frozen source tree absent"):
                _audit(repo, registered, evidence)

    def test_temporary_source_edit_cannot_be_reverted_away(self):
        for mode in ("rewrite", "delete", "add"):
            with self.subTest(mode=mode):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, _ = _create_fixture(repo)
                    source = repo / "src" / "engine.py"
                    original = source.read_bytes()
                    if mode == "delete":
                        _git(repo, "rm", "src/engine.py")
                    elif mode == "add":
                        (repo / "src" / "extra.py").write_text(
                            "print('extra')\n", encoding="utf-8",
                        )
                        _git(repo, "add", "src/extra.py")
                    else:
                        source.write_bytes(original + b"\n")
                        _git(repo, "add", "src/engine.py")
                    _git(repo, "commit", "-qm", "temporarily alter frozen source")
                    if mode == "add":
                        _git(repo, "rm", "src/extra.py")
                    else:
                        source.parent.mkdir(parents=True, exist_ok=True)
                        source.write_bytes(original)
                        _git(repo, "add", "src/engine.py")
                    _git(repo, "commit", "-qm", "restore frozen source")
                    evidence = _git(repo, "rev-parse", "HEAD")
                    with self.assertRaisesRegex(
                        ValueError, "frozen source tree changed|frozen source tree absent",
                    ):
                        _audit(repo, registered, evidence)

    def test_frozen_commit_without_installer_manifest_fails_closed(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(
                repo, project_installer=False,
            )
            with self.assertRaisesRegex(
                ValueError, "project installation manifest absent",
            ):
                _audit(repo, registered, evidence)

    def test_committed_installer_manifest_edit_is_detected(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, _ = _create_fixture(repo)
            config = repo / "pyproject.toml"
            config.write_bytes(config.read_bytes() + b"\n# changed install metadata\n")
            _git(repo, "add", "pyproject.toml")
            _git(repo, "commit", "-qm", "change package metadata")
            with self.assertRaisesRegex(
                ValueError, "project installation manifest changed",
            ):
                _audit(repo, registered, _git(repo, "rev-parse", "HEAD"))

    def test_temporary_installer_edit_or_deletion_cannot_be_reverted(self):
        for modification in ("edit", "delete"):
            with self.subTest(modification=modification):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, _ = _create_fixture(repo)
                    path = repo / "pyproject.toml"
                    original = path.read_bytes()
                    if modification == "edit":
                        path.write_bytes(original + b"\n# transient package change\n")
                        _git(repo, "add", "pyproject.toml")
                    else:
                        _git(repo, "rm", "pyproject.toml")
                    _git(repo, "commit", "-qm", "transient packaging edit")
                    path.write_bytes(original)
                    _git(repo, "add", "pyproject.toml")
                    _git(repo, "commit", "-qm", "restore package manifest")
                    with self.assertRaisesRegex(
                        ValueError,
                        "project installation manifest changed|project installation manifest absent",
                    ):
                        _audit(repo, registered, _git(repo, "rev-parse", "HEAD"))

    def test_local_git_replace_cannot_hide_a_committed_source_change(self):
        # A replacement object may make an altered commit *appear* to have
        # the original tree. The chronology audit must see the real objects.
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            freeze, registered, _ = _create_fixture(repo)
            source = repo / "src" / "engine.py"
            original = source.read_bytes()
            source.write_bytes(original + b"\n# altered")
            _git(repo, "add", "src/engine.py")
            _git(repo, "commit", "-qm", "temporarily change frozen source")
            altered = _git(repo, "rev-parse", "HEAD")
            source.write_bytes(original)
            _git(repo, "add", "src/engine.py")
            _git(repo, "commit", "-qm", "restore frozen source")
            evidence = _git(repo, "rev-parse", "HEAD")
            prior = _git(repo, "rev-parse", f"{altered}^")
            original_tree = _git(repo, "rev-parse", f"{prior}^{{tree}}")
            replacement = _git(
                repo, "commit-tree", original_tree, "-p", prior,
                "-m", "local replacement claims unmodified code",
            )
            _git(repo, "replace", altered, replacement)
            # Standard Git readers are susceptible to the local replacement.
            self.assertEqual(
                _git(repo, "rev-parse", f"{altered}:src"),
                _git(repo, "rev-parse", f"{freeze}:src"),
            )
            with self.assertRaisesRegex(ValueError, "frozen source tree changed"):
                _audit(repo, registered, evidence)

    def test_shallow_checkout_cannot_certify_git_chronology(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "full"
            source.mkdir()
            _, registered, evidence = _create_fixture(source)
            shallow = root / "shallow"
            subprocess.run(
                ("git", "clone", "-q", "--depth", "1",
                 source.as_uri(), str(shallow)),
                check=True, capture_output=True,
            )
            with self.assertRaisesRegex(ValueError, "unshallowed Git history"):
                _audit(shallow, registered, evidence)

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
