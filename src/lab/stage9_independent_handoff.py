"""Read-only Stage-9 scientific handoff: one fail-closed machine audit.

This composes existing, independently testable custody readers. It does not
certify experiment prospectivity, hidden-world independence, true runtime,
oracle isolation, scientific acceptance, INV-25, or a Golden.

Normative: EN MVP v1.2.1 §§9.6, 13.2, 19.5 and Stage 9 (20.3).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_frozen_worktree import verify_frozen_worktree
from .stage9_heldout_artifact_custody import (
    audit_heldout_raw_artifacts, load_raw_artifact_index,
)
from .stage9_registered_manifest_custody import (
    audit_registered_manifest_files, load_manifest_index,
)
from .stage9_registration_chronology import (
    _file_in_repo, audit_registration_chronology,
)
from .stage9_scientific_assessment import (
    assess_heldout_campaign, load_heldout_evidence,
)
from .stage9_scientific_preregistration import (
    load_registration, validate_registration,
)

HANDOFF_VERSION = "stage9-independent-heldout-machine-handoff-v1"
MANIFEST_STATUS = "registered_manifest_bytes_match_requires_independent_review"
RAW_STATUS = "raw_bytes_match_report_requires_independent_provenance_review"
CHRONOLOGY_STATUSES = frozenset({
    "git_lineage_consistent_requires_independent_review",
    "prior_evidence_path_requires_independent_review",
})


def _require_uncertified(report: object, *, name: str) -> dict[str, object]:
    if not isinstance(report, dict):
        raise ValueError(f"{name} must return a structured machine audit")
    if report.get("scientific_verdict") is not None or (
        report.get("golden_stage9_frozen") is not False
    ):
        raise ValueError(f"{name} tried to self-certify scientific Stage 9")
    return report


def audit_independent_heldout_handoff(
    *, repository: Path, registration_path: Path, registration_commit: str,
    evidence_path: Path, evidence_commit: str,
    manifest_index_path: Path, manifest_root: Path,
    raw_index_path: Path, raw_artifact_root: Path,
) -> dict[str, object]:
    """Verify *all* machine-readable inputs before external Stage-9 review.

    Fail before producing a receipt if any one audit fails, so an operator
    cannot mistake a partial list of green commands for a complete bundle.
    Paths and Git commits refer to the independently provided original
    artifacts. Even a successful receipt is not scientific acceptance.
    """
    root = repository.resolve()
    chronology = _require_uncertified(
        audit_registration_chronology(
            repository=root,
            registration_path=registration_path,
            registration_commit=registration_commit,
            evidence_path=evidence_path,
            evidence_commit=evidence_commit,
        ),
        name="Git chronology",
    )
    if chronology.get("chronology_status") not in CHRONOLOGY_STATUSES:
        raise ValueError("unrecognized or incomplete Stage-9 chronology result")
    prior_evidence = chronology.get("evidence_path_present_at_registration")
    prior_history = chronology.get(
        "evidence_path_seen_in_pre_registration_git_history"
    )
    scanned_completely = chronology.get(
        "pre_registration_semantic_scan_complete"
    )
    unchecked_blobs = chronology.get(
        "pre_registration_oversized_blobs_not_checked"
    )
    if (
        type(scanned_completely) is not bool
        or type(unchecked_blobs) is not int
        or unchecked_blobs < 0
        or scanned_completely != (unchecked_blobs == 0)
    ):
        raise ValueError("Git semantic ancestry coverage is inconsistent")
    if (
        type(prior_evidence) is not bool
        or type(prior_history) is not bool
        or (prior_evidence and not prior_history)
        or (
            chronology["chronology_status"]
            == "prior_evidence_path_requires_independent_review"
        ) != prior_history
    ):
        raise ValueError("Git chronology evidence-path status is inconsistent")
    # The present checkout must also match the frozen bytes. This is a
    # *retrospective* local check, not an attestation of the historical
    # executable or process that produced the heldout artifacts.
    checkout = _require_uncertified(
        verify_frozen_worktree(
            repository=root,
            frozen_implementation_commit=chronology[
                "frozen_implementation_commit"
            ],
        ),
        name="current frozen worktree",
    )
    if (
        checkout.get("frozen_implementation_commit")
        != chronology["frozen_implementation_commit"]
        or checkout.get("source_tree_sha")
        != chronology["frozen_source_tree_sha"]
        or checkout.get("pyproject_blob_sha")
        != chronology["frozen_pyproject_blob_sha"]
        or checkout.get("normative_specification_blob_sha")
        != chronology["frozen_normative_specification_blob_sha"]
    ):
        raise ValueError("current checkout differs from frozen Git chronology")
    # Resolve the same files as the committed-Git reader, not a caller-supplied
    # out-of-repository replacement of a sealed registration or report.
    registered_file, _ = _file_in_repo(root, registration_path)
    evidence_file, _ = _file_in_repo(root, evidence_path)
    registration = load_registration(registered_file)
    evidence = load_heldout_evidence(evidence_file)
    digest = validate_registration(registration)
    provisional = _require_uncertified(
        assess_heldout_campaign(registration, evidence),
        name="heldout metric scorer",
    )

    manifests = _require_uncertified(
        audit_registered_manifest_files(
            registration=registration,
            index=load_manifest_index(manifest_index_path),
            artifact_root=manifest_root,
        ),
        name="physical manifest custody",
    )
    if manifests.get("manifest_custody_status") != MANIFEST_STATUS:
        raise ValueError("physical manifest custody was not verified")

    raw = _require_uncertified(
        audit_heldout_raw_artifacts(
            registration=registration,
            evidence=evidence,
            index=load_raw_artifact_index(raw_index_path),
            artifact_root=raw_artifact_root,
        ),
        name="raw artifact custody",
    )
    if raw.get("artifact_custody_status") != RAW_STATUS:
        raise ValueError("raw artifact custody was not verified")
    for label, report in (
        ("chronology", chronology),
        ("provisional metrics", provisional),
        ("physical manifests", manifests),
        ("raw artifacts", raw),
    ):
        if report.get("registration_digest") != digest:
            raise ValueError(f"{label} digest differs from preregistration")
    for label, report in (("chronology", chronology), ("raw artifacts", raw)):
        if report.get("evidence_sha256") != provisional.get("evidence_sha256"):
            raise ValueError(f"{label} differs from archived heldout evidence")
    if (
        chronology.get("frozen_implementation_commit")
        != registration["frozen_implementation_commit"]
        or chronology.get("registration_commit") != registration_commit
        or chronology.get("evidence_commit") != evidence_commit
    ):
        raise ValueError("Git handoff identifies a different frozen campaign")
    if (
        chronology.get("provisional_metric_assessment")
        != provisional.get("assessment")
        or raw.get("provisional_metric_assessment")
        != provisional.get("assessment")
    ):
        raise ValueError("independent checks disagree on provisional metrics")
    if (
        manifests.get("holdout_worlds_checked")
        != len(registration["holdout_world_ids"])
        or manifests.get("calibration_worlds_checked")
        != len(registration["calibration_world_ids"])
        or raw.get("runs_checked") != (
            len(registration["holdout_world_ids"])
            * len(registration["holdout_seeds"])
        )
    ):
        raise ValueError("Stage-9 handoff has incomplete registered coverage")

    # Distinguish a complete machine-custody pass from *eligibility* for an
    # independent acceptance review. A preexisting report path can be an
    # innocent placeholder, but it must never be silently reported as clean
    # prospectivity. Likewise, unfavorable or nonevaluable metrics are not
    # equivalent to a preregistered confidence pass.
    review_blockers = []
    if prior_evidence:
        review_blockers.append(
            "evidence_path_preexisted_registration_requires_prospectivity_review"
        )
    elif prior_history:
        review_blockers.append(
            "evidence_path_existed_earlier_in_git_history_requires_prospectivity_review"
        )
    if provisional["assessment"] != "metrics_eligible_for_independent_review":
        review_blockers.append(
            "preregistered_metrics_not_eligible_for_independent_acceptance"
        )
    if unchecked_blobs:
        review_blockers.append(
            "pre_registration_large_git_blobs_not_semantically_inspected"
        )
    handoff = {
        "protocol_version": HANDOFF_VERSION,
        "handoff_status": (
            "machine_checks_complete_with_explicit_review_blockers"
            if review_blockers
            else "machine_checks_consistent_requires_independent_scientific_review"
        ),
        "review_blockers": review_blockers,
        "evidence_path_present_at_registration": prior_evidence,
        "evidence_path_seen_in_pre_registration_git_history": prior_history,
        "pre_registration_semantic_scan_complete": scanned_completely,
        "pre_registration_oversized_blobs_not_checked": unchecked_blobs,
        "registration_digest": digest,
        "evidence_sha256": provisional["evidence_sha256"],
        "frozen_implementation_commit":
            registration["frozen_implementation_commit"],
        "registration_commit": registration_commit,
        "evidence_commit": evidence_commit,
        "provisional_metric_assessment": provisional["assessment"],
        "git_chronology": chronology,
        "current_checkout_preflight": checkout,
        "physical_manifest_custody": manifests,
        "raw_artifact_custody": raw,
        "provisional_metrics": provisional,
        "independent_world_custody_attested": False,
        "independent_seed_selection_attested": False,
        "frozen_runtime_execution_attested": False,
        "prospective_approval_attested": False,
        "oracle_isolation_attested": False,
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "independently attest protocol approval before outcomes were available",
            "inspect actual physical world semantics, independent seeds and oracle isolation",
            "witness the actual frozen software runtime, Memory closure and raw events",
            "review any prior evidence path, metric failure or zero denominator",
            "complete external Stage-9 scientific acceptance review and INV-25",
        ],
    }
    handoff["machine_handoff_sha256"] = sha256_hex(
        canonical_causal_bytes(handoff)
    )
    return handoff


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit all Stage-9 machine custody gates, never certify Golden",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--registration-commit", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    parser.add_argument("--manifest-index", type=Path, required=True)
    parser.add_argument("--manifest-root", type=Path, required=True)
    parser.add_argument("--raw-index", type=Path, required=True)
    parser.add_argument("--raw-artifact-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        audit_independent_heldout_handoff(
            repository=args.repo,
            registration_path=args.registration,
            registration_commit=args.registration_commit,
            evidence_path=args.evidence,
            evidence_commit=args.evidence_commit,
            manifest_index_path=args.manifest_index,
            manifest_root=args.manifest_root,
            raw_index_path=args.raw_index,
            raw_artifact_root=args.raw_artifact_root,
        ),
        sort_keys=True, indent=2,
    ))


if __name__ == "__main__":
    main()
