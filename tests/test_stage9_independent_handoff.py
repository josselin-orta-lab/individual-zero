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


def _synthetic_bundle(
    root: Path, *, insufficient: bool = False,
    review_eligible: bool = False, prior_evidence_path: bool = False,
    transient_prior_evidence: bool = False,
    large_unexamined_prior_blob: bool = False,
    ambiguous_prior_stage9_json: bool = False,
    reused_archives: bool = False,
    omit_one_negative_run: bool = False,
    share_candidate_episode: bool = False,
) -> dict:
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
    if insufficient and review_eligible:
        raise ValueError("synthetic bundle cannot be both eligible and insufficient")
    if insufficient:
        registration["minimum_naturally_acquired_candidates"] = 1000
    if review_eligible:
        # Numeric eligibility in a disposable fixture is still NOT
        # independently witnessed world truth, prospectivity or INV-25.
        registration["minimum_known_cause_accuracy"] = 0.20
        registration["maximum_superstitious_rule_rate"] = 0.80
        registration["minimum_naturally_acquired_candidates"] = 2
    digest = validate_registration(registration)
    manifest_index["registration_digest"] = digest
    if prior_evidence_path and transient_prior_evidence:
        raise ValueError("select one synthetic prior evidence condition")
    if transient_prior_evidence:
        (repo / "results").mkdir()
        (repo / "results" / "heldout.json").write_text(
            "SYNTHETIC PRE-REGISTRATION PLACEHOLDER, NOT RESULTS\n",
            encoding="utf-8",
        )
        _git(repo, "add", "results/heldout.json")
        _git(repo, "commit", "-qm", "synthetic early outcome-path")
        _git(repo, "rm", "results/heldout.json")
        _git(repo, "commit", "-qm", "hide early outcome-path before registration")
    if large_unexamined_prior_blob:
        # This is unrelated binary content, not fabricated heldout evidence.
        # The machine scanner cannot establish what every oversized blob
        # means; it must report that boundary to the independent reviewer.
        path = repo / "bench/raw-large.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"0" * (2 * 1024 * 1024))
        _git(repo, "add", "bench/raw-large.bin")
        _git(repo, "commit", "-qm", "archive unrelated large bench blob")
    if ambiguous_prior_stage9_json:
        # A pre-registration Stage-9-like report with forbidden nonfinite
        # content cannot be counted as a successfully inspected old blob.
        path = repo / "preseal/ambiguous.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '{"protocol_version":"stage9-heldout-evidence-v2",'
            '"registration_digest":"synthetic","runs":[],'
            '"untrusted_extra":NaN}',
            encoding="utf-8",
        )
        _git(repo, "add", "preseal/ambiguous.json")
        _git(repo, "commit", "-qm", "synthetic ambiguous preseal JSON")
    (repo / "research").mkdir()
    registration_path = Path("research/registration.json")
    (repo / registration_path).write_text(
        json.dumps(registration, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _git(repo, "add", registration_path.as_posix())
    if prior_evidence_path:
        # This is an *existing placeholder*, not identical heldout evidence.
        # The chronology reader reports ambiguity without treating it as
        # equivalent to an immutable prospective outcome witness.
        (repo / "results").mkdir()
        (repo / "results" / "heldout.json").write_text(
            "SYNTHETIC PREEXISTING PLACEHOLDER, NOT SCIENTIFIC DATA\n",
            encoding="utf-8",
        )
        _git(repo, "add", "results/heldout.json")
    _git(repo, "commit", "-qm", "synthetic prospective registration")
    registration_commit = _git(repo, "rev-parse", "HEAD")

    _unused_registration, evidence, raw_index = _prepared(
        raw_root,
        omit_negative_seed=(
            registration["holdout_seeds"][0]
            if omit_one_negative_run else None
        ),
        share_candidate_episode=share_candidate_episode,
    )
    evidence["frozen_implementation_commit"] = frozen
    evidence["registration_digest"] = digest
    for row in evidence["runs"]:
        row["world_sha256"] = registration["holdout_world_sha256"][
            row["world_id"]
        ]
    if reused_archives:
        # Keep physically distinct PATHS and inodes while copying the actual
        # first positive cell's journal and causal snapshot into another
        # seed's cell. The per-run hash, replay, journal, Memory and published
        # causal checks can all pass for this intentionally forged provenance.
        # Only the cross-run byte-identity disclosure makes it conspicuous.
        positive_rows = [
            (i, row)
            for i, row in enumerate(evidence["runs"])
            if row["world_id"] in registration["positive_world_ids"]
        ]
        if len(positive_rows) < 2:
            raise ValueError("synthetic collision needs two positive cells")
        (source_idx, source_row), (dest_idx, dest_row) = positive_rows[:2]
        src_index = raw_index["runs"][source_idx]
        dst_index = raw_index["runs"][dest_idx]
        for path_field, digest_field in (
            ("journal_path", "journal_sha256"),
            ("replay_journal_path", "replay_journal_sha256"),
            ("causal_state_path", "causal_state_sha256"),
            ("replay_causal_state_path", "replay_causal_state_sha256"),
        ):
            (raw_root / dst_index[path_field]).write_bytes(
                (raw_root / src_index[path_field]).read_bytes()
            )
            dest_row[digest_field] = source_row[digest_field]
        dest_row["known_cause_cases"] = deepcopy(source_row["known_cause_cases"])
        dest_row["naturally_acquired_false_candidates"] = deepcopy(
            source_row["naturally_acquired_false_candidates"]
        )
    evidence = sealed(evidence)
    raw_index["registration_digest"] = digest
    raw_index["evidence_sha256"] = evidence["evidence_sha256"]
    (repo / "results").mkdir(exist_ok=True)
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
            self.assertIn(
                "preregistered_metrics_not_eligible_for_independent_acceptance",
                result["review_blockers"],
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertFalse(result["evidence_path_present_at_registration"])
            self.assertFalse(
                result["evidence_path_seen_in_pre_registration_git_history"]
            )
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

    def test_review_eligible_machine_metrics_are_still_not_scientific_pass(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder), review_eligible=True)
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["provisional_metric_assessment"],
                "metrics_eligible_for_independent_review",
            )
            self.assertEqual(result["review_blockers"], [])
            self.assertTrue(result["pre_registration_semantic_scan_complete"])
            self.assertEqual(
                result["pre_registration_oversized_blobs_not_checked"], 0,
            )
            self.assertEqual(
                result["pre_registration_ambiguous_stage9_json_blobs"], 0,
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_consistent_requires_independent_scientific_review",
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_copied_original_and_replay_archives_across_seeds_block_clean_handoff(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True, reused_archives=True,
            )
            # Every file remains a different physical path/inode. The
            # independent index, hash chain and Memory checks should pass.
            result = audit_independent_heldout_handoff(**options)
            self.assertTrue(
                result["raw_artifact_custody"]["journal_chain_integrity_verified"]
            )
            self.assertTrue(
                result["raw_artifact_custody"]["closed_episode_membership_structurally_verified"]
            )
            self.assertEqual(
                result["provisional_metric_assessment"],
                "metrics_eligible_for_independent_review",
            )
            self.assertEqual(
                result["review_blockers"],
                [
                    "identical_journal_bytes_across_distinct_heldout_runs_requires_review",
                    "identical_causal_owner_bytes_across_distinct_heldout_runs_requires_review",
                ],
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertEqual(
                len(result["cross_run_identical_archives"]["journal_sha256"]), 1,
            )
            self.assertEqual(
                len(result["cross_run_identical_archives"]["causal_state_sha256"]), 1,
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_heldout_handoff_flags_one_missing_null_run_despite_pooled_pass(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True, omit_one_negative_run=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["provisional_metric_assessment"],
                "metrics_eligible_for_independent_review",
            )
            self.assertEqual(
                result["negative_runs_without_natural_candidates"],
                [{"world_id": "holdout:null", "seed": 1001}],
            )
            self.assertEqual(
                result["negative_runs_without_natural_candidates"],
                result["raw_artifact_custody"][
                    "negative_runs_without_natural_candidates"
                ],
            )
            self.assertIn(
                "natural_candidate_sampling_absent_in_some_null_runs_requires_review",
                result["review_blockers"],
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_heldout_handoff_flags_multi_rule_episode_without_fabricating_samples(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True, share_candidate_episode=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["provisional_metric_assessment"],
                "metrics_eligible_for_independent_review",
            )
            clusters = result["reused_closed_memory_candidate_episodes"]
            self.assertEqual(len(clusters), 2)
            self.assertEqual(
                [cluster["candidate_count"] for cluster in clusters], [2, 2],
            )
            self.assertEqual(
                clusters,
                result["raw_artifact_custody"][
                    "reused_closed_memory_candidate_episodes"
                ],
            )
            self.assertIn(
                "multiple_false_rules_from_one_closed_memory_episode_require_independence_review",
                result["review_blockers"],
            )
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertIsNone(result["scientific_verdict"])

    def test_diagnostic_mismatch_between_scorer_and_raw_reader_fails_closed(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True,
            )
            from lab.stage9_scientific_assessment import (
                assess_heldout_campaign, load_heldout_evidence,
            )
            from lab.stage9_scientific_preregistration import load_registration
            draft = load_registration(
                options["repository"] / options["registration_path"]
            )
            report = load_heldout_evidence(
                options["repository"] / options["evidence_path"]
            )
            real = assess_heldout_campaign(draft, report)
            forged = dict(real)
            forged["negative_runs_without_natural_candidates"] = [
                {"world_id": "holdout:null", "seed": 1001},
            ]
            with patch(
                "lab.stage9_independent_handoff.assess_heldout_campaign",
                return_value=forged,
            ):
                with self.assertRaisesRegex(
                    ValueError, "raw artifact and metric scorer disagree",
                ):
                    audit_independent_heldout_handoff(**options)

    def test_existing_placeholder_evidence_path_is_explicit_review_blocker(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True, prior_evidence_path=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertTrue(result["evidence_path_present_at_registration"])
            self.assertEqual(
                result["git_chronology"]["chronology_status"],
                "prior_evidence_path_requires_independent_review",
            )
            self.assertEqual(
                result["review_blockers"],
                ["evidence_path_preexisted_registration_requires_prospectivity_review"],
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertFalse(result["golden_stage9_frozen"])

    def test_transient_pre_registration_evidence_path_requires_review(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True,
                transient_prior_evidence=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertFalse(result["evidence_path_present_at_registration"])
            self.assertTrue(
                result["evidence_path_seen_in_pre_registration_git_history"]
            )
            self.assertEqual(
                result["review_blockers"],
                [
                    "evidence_path_existed_earlier_in_git_history_requires_prospectivity_review"
                ],
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_large_unexamined_prior_blobs_require_independent_review(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True,
                large_unexamined_prior_blob=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["review_blockers"],
                ["pre_registration_large_git_blobs_not_semantically_inspected"],
            )
            self.assertFalse(result["pre_registration_semantic_scan_complete"])
            self.assertGreater(
                result["pre_registration_oversized_blobs_not_checked"], 0,
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_ambiguous_prior_stage9_json_is_a_review_blocker(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(
                Path(folder), review_eligible=True,
                ambiguous_prior_stage9_json=True,
            )
            result = audit_independent_heldout_handoff(**options)
            self.assertEqual(
                result["provisional_metric_assessment"],
                "metrics_eligible_for_independent_review",
            )
            self.assertFalse(result["pre_registration_semantic_scan_complete"])
            self.assertEqual(
                result["pre_registration_ambiguous_stage9_json_blobs"], 1,
            )
            self.assertEqual(
                result["review_blockers"],
                ["pre_registration_ambiguous_stage9_json_requires_prospectivity_review"],
            )
            self.assertEqual(
                result["handoff_status"],
                "machine_checks_complete_with_explicit_review_blockers",
            )
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])

    def test_inconsistent_prospectivity_claim_from_component_fails_closed(self):
        with TemporaryDirectory() as folder:
            options = _synthetic_bundle(Path(folder), review_eligible=True)
            from lab.stage9_independent_handoff import audit_registration_chronology
            actual = audit_registration_chronology(
                repository=options["repository"],
                registration_path=options["registration_path"],
                registration_commit=options["registration_commit"],
                evidence_path=options["evidence_path"],
                evidence_commit=options["evidence_commit"],
            )
            altered = {**actual, "evidence_path_present_at_registration": True}
            with patch(
                "lab.stage9_independent_handoff.audit_registration_chronology",
                return_value=altered,
            ):
                with self.assertRaisesRegex(
                    ValueError, "evidence-path status is inconsistent",
                ):
                    audit_independent_heldout_handoff(**options)

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
