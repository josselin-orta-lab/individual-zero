"""Git-ancestry tests use disposable commits and synthetic metrics only.

These fixtures are not scientific data, an approved protocol or a Golden.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.stage9_registration_chronology import audit_registration_chronology
from lab.stage9_scientific_preregistration import SPEC_PATH
from tests.test_stage9_scientific_preregistration import example_draft
from tests.test_stage9_scientific_assessment import make_report, sealed


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
    earlier_evidence: str | None = None,
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
    if earlier_evidence is not None:
        if earlier_evidence not in {
            "identical", "placeholder", "transient_identical",
            "transient_placeholder",
            "alternate_path_identical",
            "transient_alternate_path_identical",
            "alternate_path_equivalent",
            "transient_alternate_path_equivalent",
            "alternate_path_ambiguous_duplicate",
            "alternate_path_ambiguous_nonfinite",
            "alternate_path_ambiguous_exponent",
            "alternate_path_reordered",
            "transient_alternate_path_reordered",
            "alternate_path_utf8_bom",
            "alternate_path_utf16_le",
            "alternate_path_utf16_be",
            "alternate_path_utf16_no_bom",
            "alternate_path_utf32_le",
            "transient_alternate_path_utf16_le",
            "alternate_path_utf16_whitespace",
        }:
            raise ValueError("unrecognized synthetic prior evidence scenario")
        alternate_name = earlier_evidence in {
            "alternate_path_identical", "transient_alternate_path_identical",
            "alternate_path_equivalent", "transient_alternate_path_equivalent",
            "alternate_path_ambiguous_duplicate",
            "alternate_path_ambiguous_nonfinite",
            "alternate_path_ambiguous_exponent",
            "alternate_path_reordered",
            "transient_alternate_path_reordered",
            "alternate_path_utf8_bom",
            "alternate_path_utf16_le",
            "alternate_path_utf16_be",
            "alternate_path_utf16_no_bom",
            "alternate_path_utf32_le",
            "transient_alternate_path_utf16_le",
            "alternate_path_utf16_whitespace",
        }
        early_relative = (
            "preseal/private-outcomes.json"
            if alternate_name else "results/heldout.json"
        )
        (repo / Path(early_relative).parent).mkdir(exist_ok=True)
        early_file = repo / early_relative
        if earlier_evidence.startswith("alternate_path_ambiguous_"):
            # Non-standard JSON from a preseal Git blob must never be
            # silently treated as fully scanned prospective evidence.
            encoded = json.dumps(
                make_report(draft, candidates=20),
                sort_keys=True, indent=2,
            )
            marker = '"protocol_version": "stage9-heldout-evidence-v2",'
            if marker not in encoded:
                raise AssertionError("synthetic protocol marker absent")
            if earlier_evidence.endswith("duplicate"):
                # Lenient JSON parsing yields the exact archived report, but
                # duplicate keys are forbidden by the scientific reader.
                insertion = marker + '\n  ' + marker
            elif earlier_evidence.endswith("exponent"):
                # Python's ordinary float parser otherwise turns a valid
                # JSON exponent into Infinity without calling parse_constant.
                insertion = marker + '\n  "synthetic_malformed": 1e999,'
            else:
                insertion = marker + '\n  "synthetic_malformed": NaN,'
            early_file.write_text(
                encoded.replace(marker, insertion, 1) + "\n",
                encoding="utf-8",
            )
        elif earlier_evidence.endswith((
            "utf8_bom", "utf16_le", "utf16_be", "utf16_no_bom", "utf32_le", "utf16_whitespace",
        )):
            # Python's JSON parser accepts multiple real Unicode encodings.
            # A previous bytewise ASCII-brace shortcut mistakenly skipped
            # these semantically identical earlier heldout reports.
            text = json.dumps(
                make_report(draft, candidates=20),
                sort_keys=True, indent=2,
            )
            codec = {
                "utf8_bom": "utf-8-sig",
                "utf16_le": "utf-16",
                "utf16_be": "utf-16-be",
                "utf16_no_bom": "utf-16-le",
                "utf32_le": "utf-32",
                "utf16_whitespace": "utf-16-le",
            }
            variant = next(
                name for name in codec if earlier_evidence.endswith(name)
            )
            if variant == "utf16_whitespace":
                text = " \n\t" + text
            early_file.write_bytes(text.encode(codec[variant]))
        elif earlier_evidence.endswith("reordered"):
            # Same physical rows and same source hashes, but different
            # presentation ordering and a correctly recomputed full digest.
            # None of these changes represents a prospective new sample.
            reordered = make_report(draft, candidates=20)
            reordered["runs"].reverse()
            for run in reordered["runs"]:
                run["known_cause_cases"].reverse()
                run["naturally_acquired_false_candidates"].reverse()
            reordered = sealed(reordered)
            original = make_report(draft, candidates=20)
            if reordered["evidence_sha256"] == original["evidence_sha256"]:
                raise AssertionError("synthetic reordering must change report digest")
            early_file.write_text(
                json.dumps(reordered, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
        elif earlier_evidence.endswith(("identical", "equivalent")):
            # The equivalent variant has the *same JSON meaning* as the
            # final report, but different Git blob bytes, field order and
            # whitespace. This must not bypass prospective custody.
            early_file.write_text(
                json.dumps(
                    make_report(draft, candidates=20),
                    sort_keys=earlier_evidence.endswith("identical"),
                    indent=(2 if earlier_evidence.endswith("identical") else None),
                    separators=(
                        None if earlier_evidence.endswith("identical")
                        else (",", ":")
                    ),
                ) + ("\n" if earlier_evidence.endswith("identical") else ""),
                encoding="utf-8",
            )
        else:
            early_file.write_text(
                "SYNTHETIC PREEXISTING PLACEHOLDER, NOT RESULTS\n",
                encoding="utf-8",
            )
        _git(repo, "add", early_relative)
        _git(repo, "commit", "-qm", "synthetic outcome-path before registration")
        if earlier_evidence.startswith("transient_"):
            _git(repo, "rm", early_relative)
            _git(repo, "commit", "-qm", "remove synthetic earlier outcome path")
    (repo / "research").mkdir()
    (repo / "research" / "registration.json").write_text(
        json.dumps(draft, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    _git(repo, "add", "research/registration.json")
    _git(repo, "commit", "-qm", "preregister protocol")
    registration_commit = _git(repo, "rev-parse", "HEAD")

    (repo / "results").mkdir(exist_ok=True)
    (repo / "results" / "heldout.json").write_text(
        json.dumps(make_report(draft, candidates=20), sort_keys=True, indent=2)
        + "\n", encoding="utf-8",
    )
    _git(repo, "add", "results/heldout.json")
    if earlier_evidence == "identical":
        # The eventual evidence file is already byte-identical to the
        # premature Git blob. A separate archival receipt ensures an actual
        # distinct post-registration commit exists for the chronology audit.
        (repo / "results" / "archival-note.txt").write_text(
            "SYNTHETIC late archive note, not a new result\n",
            encoding="utf-8",
        )
        _git(repo, "add", "results/archival-note.txt")
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
            self.assertFalse(
                result["evidence_path_seen_in_pre_registration_git_history"]
            )
            self.assertEqual(
                result["pre_registration_evidence_path_commits_checked"], 0,
            )
            self.assertGreater(result["pre_registration_git_objects_checked"], 0)
            self.assertGreater(result["pre_registration_json_blobs_checked"], 0)
            self.assertEqual(
                result["pre_registration_ambiguous_stage9_json_blobs"], 0,
            )
            self.assertGreaterEqual(
                result["pre_registration_oversized_blobs_not_checked"], 0,
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertTrue(result["outstanding"])
            self.assertNotEqual(result["provisional_metric_assessment"], "accepted")

    def test_pre_registration_identical_report_rejected_even_after_git_deletion(self):
        for scenario in ("identical", "transient_identical"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    with self.assertRaisesRegex(
                        ValueError,
                        "already committed before prospective registration",
                    ):
                        _audit(repo, registered, evidence)

    def test_early_evidence_under_a_different_git_path_is_not_prospective(self):
        for scenario in (
            "alternate_path_identical", "transient_alternate_path_identical",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    self.assertNotEqual(
                        _git(repo, "rev-parse", f"{evidence}:results/heldout.json"),
                        _git(repo, "rev-parse", f"{evidence}:research/registration.json"),
                    )
                    with self.assertRaisesRegex(
                        ValueError,
                        "heldout evidence bytes existed in Git before prospective registration",
                    ):
                        _audit(repo, registered, evidence)

    def test_json_equivalent_report_at_another_path_is_not_prospective(self):
        for scenario in (
            "alternate_path_equivalent",
            "transient_alternate_path_equivalent",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    early_path = repo / "preseal/private-outcomes.json"
                    archived = repo / "results/heldout.json"
                    if early_path.exists():
                        self.assertNotEqual(
                            early_path.read_bytes(), archived.read_bytes()
                        )
                        self.assertEqual(
                            json.loads(early_path.read_text()),
                            json.loads(archived.read_text()),
                        )
                    with self.assertRaisesRegex(
                        ValueError,
                        "semantically identical heldout evidence existed in Git",
                    ):
                        _audit(repo, registered, evidence)

    def test_unicode_encoded_prior_reports_cannot_disguise_same_results(self):
        for scenario in (
            "alternate_path_utf8_bom",
            "alternate_path_utf16_le",
            "alternate_path_utf16_be",
            "alternate_path_utf16_no_bom",
            "alternate_path_utf32_le",
            "transient_alternate_path_utf16_le",
            "alternate_path_utf16_whitespace",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    old_path = repo / "preseal/private-outcomes.json"
                    archived = repo / "results/heldout.json"
                    if old_path.exists():
                        self.assertNotEqual(
                            old_path.read_bytes(), archived.read_bytes(),
                        )
                        self.assertEqual(
                            json.loads(old_path.read_bytes()),
                            json.loads(archived.read_bytes()),
                        )
                    with self.assertRaisesRegex(
                        ValueError,
                        "semantically identical heldout evidence existed in Git",
                    ):
                        _audit(repo, registered, evidence)

    def test_reordered_prior_worlds_and_candidates_are_not_new_scientific_samples(self):
        for scenario in (
            "alternate_path_reordered",
            "transient_alternate_path_reordered",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    if (repo / "preseal/private-outcomes.json").exists():
                        earlier = json.loads(
                            (repo / "preseal/private-outcomes.json").read_text()
                        )
                        published = json.loads(
                            (repo / "results/heldout.json").read_text()
                        )
                        self.assertNotEqual(
                            earlier["evidence_sha256"],
                            published["evidence_sha256"],
                        )
                        self.assertNotEqual(earlier["runs"], published["runs"])
                    with self.assertRaisesRegex(
                        ValueError,
                        "reordered heldout observations existed in Git",
                    ):
                        _audit(repo, registered, evidence)

    def test_earlier_duplicate_key_stage9_report_cannot_hide_exact_outcomes(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(
                repo, earlier_evidence="alternate_path_ambiguous_duplicate",
            )
            with self.assertRaisesRegex(
                ValueError,
                "ambiguous pre-registration heldout JSON can decode",
            ):
                _audit(repo, registered, evidence)

    def test_earlier_nonfinite_stage9_report_makes_scan_incomplete(self):
        for scenario in (
            "alternate_path_ambiguous_nonfinite",
            "alternate_path_ambiguous_exponent",
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    result = _audit(repo, registered, evidence)
                    self.assertFalse(result["pre_registration_semantic_scan_complete"])
                    self.assertEqual(
                        result["pre_registration_ambiguous_stage9_json_blobs"], 1,
                    )
                    self.assertFalse(
                        result["evidence_path_seen_in_pre_registration_git_history"]
                    )
                    self.assertIsNone(result["scientific_verdict"])
                    self.assertFalse(result["golden_stage9_frozen"])

    def test_prior_placeholder_never_appears_as_clean_git_chronology(self):
        for scenario, at_registration in (
            ("placeholder", True),
            ("transient_placeholder", False),
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _, registered, evidence = _create_fixture(
                        repo, earlier_evidence=scenario,
                    )
                    result = _audit(repo, registered, evidence)
                    self.assertEqual(
                        result["chronology_status"],
                        "prior_evidence_path_requires_independent_review",
                    )
                    self.assertEqual(
                        result["evidence_path_present_at_registration"],
                        at_registration,
                    )
                    self.assertTrue(
                        result["evidence_path_seen_in_pre_registration_git_history"]
                    )
                    self.assertGreater(
                        result["pre_registration_evidence_path_commits_checked"], 0,
                    )
                    self.assertIsNone(result["scientific_verdict"])
                    self.assertFalse(result["golden_stage9_frozen"])

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


    def test_repository_and_git_configuration_environment_overrides_fail_closed(self):
        # A foreign GIT_DIR + GIT_WORK_TREE can redirect Git to a different
        # object store while preserving the caller's physical worktree path.
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(repo)
            for name, value in (
                ("GIT_DIR", str(repo / ".git")),
                ("GIT_WORK_TREE", str(repo)),
                ("GIT_OBJECT_DIRECTORY", str(repo / ".git" / "objects")),
                ("GIT_ALTERNATE_OBJECT_DIRECTORIES", str(repo / ".git" / "objects")),
                ("GIT_SHALLOW_FILE", str(repo / ".git" / "shallow")),
                ("GIT_CONFIG_COUNT", "1"),
                ("GIT_CONFIG_KEY_0", "core.worktree"),
                ("GIT_CONFIG_PARAMETERS", "'core.worktree=elsewhere'"),
                ("GIT_NAMESPACE", "other"),
                ("GIT_REPLACE_REF_BASE", "refs/malicious"),
            ):
                with self.subTest(name=name):
                    with patch.dict(os.environ, {name: value}):
                        with self.assertRaisesRegex(
                            ValueError, "Git audit refuses repository environment overrides",
                        ):
                            _audit(repo, registered, evidence)
            # Prompt and display controls do not change repository identity.
            with patch.dict(os.environ, {"GIT_TERMINAL_PROMPT": "0"}):
                self.assertIsNone(
                    _audit(repo, registered, evidence)["scientific_verdict"]
                )

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


    def test_chronology_rejects_sealed_file_symlink_aliases(self):
        # Canonicalizing Path.resolve() first used to silently turn an alias
        # into the committed file, concealing the path actually supplied.
        for role, parent_alias in (
            ("registration", False), ("registration", True),
            ("evidence", False), ("evidence", True),
        ):
            with self.subTest(role=role, parent_alias=parent_alias):
                with TemporaryDirectory() as folder:
                    repo = Path(folder)
                    _frozen, registered, evidence = _create_fixture(repo)
                    component, basename = (
                        ("research", "registration.json") if role == "registration"
                        else ("results", "heldout.json")
                    )
                    original = repo / component / basename
                    if parent_alias:
                        alias = repo / ("linked-" + component)
                        alias.symlink_to(repo / component, target_is_directory=True)
                        supplied = Path(alias.name) / basename
                    else:
                        alias = original.parent / ("alias-" + basename)
                        alias.symlink_to(original)
                        supplied = Path(component) / alias.name
                    options = {
                        "repository": repo,
                        "registration_path": Path("research/registration.json"),
                        "registration_commit": registered,
                        "evidence_path": Path("results/heldout.json"),
                        "evidence_commit": evidence,
                    }
                    options[
                        "registration_path" if role == "registration" else "evidence_path"
                    ] = supplied
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        audit_registration_chronology(**options)

    def test_noncanonical_chronology_path_cannot_hide_traversal(self):
        with TemporaryDirectory() as folder:
            repo = Path(folder)
            _, registered, evidence = _create_fixture(repo)
            with self.assertRaisesRegex(ValueError, "inside the repository"):
                audit_registration_chronology(
                    repository=repo,
                    registration_path=Path("research/../research/registration.json"),
                    registration_commit=registered,
                    evidence_path=Path("results/heldout.json"),
                    evidence_commit=evidence,
                )

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
