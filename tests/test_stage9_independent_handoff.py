"""Synthetic end-to-end Stage-9 handoff tests, never an experiment."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage9_independent_handoff import (
    HANDOFF_VERSION, audit_independent_heldout_handoff,
)
from lab.stage9_scientific_preregistration import (
    SPEC_PATH, validate_registration,
)
from tests.test_stage9_heldout_artifact_custody import _prepared
from tests.test_stage9_registered_manifest_custody import _fixture
from tests.test_stage9_registration_chronology import _git
from tests.test_stage9_scientific_assessment import sealed


def _synthetic_bundle(root: Path, *, insufficient: bool = False) -> dict:
    """Disposable Git+world+raw bundle, NO real causal experiment."""
    repo, manifest_root, raw_root = (
        root / "repo", root / "manifests", root / "raw",
    )
    for folder in (repo, manifest_root, raw_root):
        folder.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Stage 9 Synthetic")
    _git(repo, "config", "user.email", "stage9-synthetic@example.invalid")
    (repo / "src").mkdir()
    (repo / "src" / "engine.py").write_text(
        "print('synthetic engine, not real Individual Zero')\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text(
        "[project]\nname = 'individual-zero-synthetic'\n", encoding="utf-8",
    )
    normative = repo / SPEC_PATH
    normative.parent.mkdir(parents=True, exist_ok=True)
    normative.write_bytes(
        (Path(__file__).resolve().parents[1] / SPEC_PATH).read_bytes()
    )
    _git(repo, "add", "src", "pyproject.toml", SPEC_PATH)
    _git(repo, "commit", "-qm", "synthetic implementation freeze")
    frozen = _git(repo, "rev-parse", "HEAD")

    registration, manifest_index = _fixture(manifest_root)
    registration["frozen_implementation_commit"] = frozen
    if insufficient:
        registration["minimum_naturally_acquired_candidates"] = 1000
    digest = validate_registration(registration)
    manifest_index["registration_digest"] = digest
    (repo / "research").mkdir()
    registration_path = Path("research/registration.json")
    (repo / registration_path).write_text(
        json.dumps(registration, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", registration_path.as_posix())
    _git(repo, "commit", "-qm", "synthetic prospective registration")
    registration_commit = _git(repo, "rev-parse", "HEAD")

    _unused_registration, evidence, raw_index = _prepared(raw_root)
    evidence["frozen_implementation_commit"] = frozen
    evidence["registration_digest"] = digest
    for row in evidence["runs"]:
        row["world_sha256"] = registration["holdout_world_sha256"][
            row["world_id"]
        ]
    evidence = sealed(evidence)
    raw_index["registration_digest"] = digest
    raw_index["evidence_sha256"] = evidence["evidence_sha256"]
    (repo / "results").mkdir()
    evidence_path = Path("results/heldout.json")
    (repo / evidence_path).write_text(
        json.dumps(evidence, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", evidence_path.as_posix())
    _git(repo, "commit", "-qm", "synthetic claimed evidence archive")
    evidence_commit = _git(repo, "rev-parse", "HEAD")

    manifest_index_path = root / "manifest-index.json"
    raw_index_path = root / "raw-index.json"
    manifest_index_path.write_text(
        json.dumps(manifest_index, sort_keys=True), encoding="utf-8",
    )
    raw_index_path.write_text(
        json.dumps(raw_index, sort_keys=True), encoding="utf-8",
    )
    return {
        "repository": repo,
        "registration_path": registration_path,
        "registration_commit": registration_commit,
        "evidence_path": evidence_path,
        "evidence_commit": evidence_commit,
        "manifest_index_path": manifest_index_path,
        "manifest_root": manifest_root,
        "raw_index_path": raw_index_path,
        "raw_artifact_root": raw_root,
    }


class Stage9IndependentHandoffTests(unittest.TestCase):
    def test_one_command_cross_checks_complete_synthetic_bundle(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder))
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(result["protocol_version"], HANDOFF_VERSION)
            self.assertEqual(
                result["current_checkout_preflight"]["normative_specification_blob_sha"],
                result["git_chronology"]["frozen_normative_specification_blob_sha"],
            )
            self.assertEqual(
                result["physical_manifest_custody"]["total_manifest_files_checked"],
                7,
            )
            self.assertEqual(result["raw_artifact_custody"]["runs_checked"], 4)
            self.assertEqual(
                result["evidence_sha256"],
                result["raw_artifact_custody"]["evidence_sha256"],
            )
            self.assertEqual(
                result["registration_digest"],
                result["git_chronology"]["registration_digest"],
            )
            self.assertEqual(
                result["machine_handoff_sha256"],
                sha256_hex(canonical_causal_bytes({
                    key: val for key, val in result.items()
                    if key != "machine_handoff_sha256"
                })),
            )
            self.assertTrue(result["outstanding"])
            self.assertFalse(result["independent_world_custody_attested"])
            self.assertFalse(result["prospective_approval_attested"])
            self.assertFalse(result["frozen_runtime_execution_attested"])
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_unfavorable_metrics_are_preserved_not_promoted(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder), insufficient=True)
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["provisional_metric_assessment"],
                "insufficient_natural_candidates",
            )
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertIsNone(result["scientific_verdict"])

    def test_missing_or_changed_inputs_fail_before_any_handoff_receipt(self):
        for scenario, expectation in (
            ("changed_manifest", "physical manifest digest mismatch"),
            ("missing_raw", "missing|not a regular file|raw"),
            ("forged_manifest_index", "physical manifest index differs"),
            ("forged_raw_index", "raw artifact index is not bound"),
            ("changed_evidence", "committed|Git|evidence"),
            ("changed_normative", "local Git changes"),
        ):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    options = _synthetic_bundle(root)
                    if scenario == "changed_manifest":
                        path = root / "manifests/frozen_manifests/equipment.manifest"
                        path.write_bytes(path.read_bytes() + b"forged")
                    elif scenario == "missing_raw":
                        path = root / "raw/run0/original.jsonl"
                        path.unlink()
                    elif scenario == "forged_manifest_index":
                        index = json.loads(options["manifest_index_path"].read_text())
                        index["registration_digest"] = "f" * 64
                        options["manifest_index_path"].write_text(json.dumps(index))
                    elif scenario == "forged_raw_index":
                        index = json.loads(options["raw_index_path"].read_text())
                        index["evidence_sha256"] = "e" * 64
                        options["raw_index_path"].write_text(json.dumps(index))
                    elif scenario == "changed_evidence":
                        p = root / "repo/results/heldout.json"
                        p.write_bytes(p.read_bytes() + b"\n")
                    elif scenario == "changed_normative":
                        p = root / "repo" / SPEC_PATH
                        p.write_bytes(p.read_bytes() + b"\n# changed outside Git\n")
                    with self.assertRaisesRegex(ValueError, expectation):
                        audit_independent_heldout_handoff(**options)

    def test_component_cannot_return_a_self_certified_scientific_verdict(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder))
            # The aggregator rejects a component trying to promote a
            # consistent byte-level report to a scientific result.
            with patch(
                "lab.stage9_independent_handoff.audit_registered_manifest_files"
            ) as mocked:
                mocked.return_value = {
                    "scientific_verdict": "PASS",
                    "golden_stage9_frozen": True,
                }
                with self.assertRaisesRegex(ValueError, "self-certify"):
                    audit_independent_heldout_handoff(**options)

    def test_receipt_is_deterministic_without_rewriting_any_inputs(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder))
            files = [
                options["manifest_index_path"],
                options["raw_index_path"],
                options["repository"] / options["registration_path"],
                options["repository"] / options["evidence_path"],
            ]
            before = {str(path): path.read_bytes() for path in files}
            first = audit_independent_heldout_handoff(**options)
            second = audit_independent_heldout_handoff(**options)
            self.assertEqual(first, second)
            self.assertEqual(
                before,
                {str(path): path.read_bytes() for path in files},
            )


if __name__ == "__main__":
    unittest.main()
