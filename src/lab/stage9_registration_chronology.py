"""Read-only Git ancestry audit for Stage-9 preregistration and heldout evidence.

This checks committed bytes and DAG ancestry, not when an experimenter saw
outcomes or whether claimed World/Body journals and oracle truth are genuine.
It never declares scientific acceptance or freezes a Golden. EN MVP v1.2.1
INV-25/32/33, sections 13.2, 19.5 and 20.3.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from .stage9_scientific_assessment import (
    assess_heldout_campaign, load_heldout_evidence,
)
from .stage9_scientific_preregistration import load_registration


COMMIT_ID = re.compile(r"[0-9a-f]{40}\Z")


def _git(repository: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", "-C", str(repository), *arguments),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise ValueError("Git unavailable for chronology audit") from exc
    if result.returncode:
        raise ValueError(
            "Git chronology check failed: " + arguments[0]
        )
    return result.stdout


def _file_in_repo(repository: Path, supplied: Path) -> tuple[Path, str]:
    file = (repository / supplied).resolve()
    try:
        relative = file.relative_to(repository)
    except ValueError as exc:
        raise ValueError("chronology input must be inside the repository") from exc
    if not file.is_file() or not relative.parts or ".git" in relative.parts:
        raise ValueError("chronology input must be a regular project file")
    return file, relative.as_posix()


def _check_commit(repository: Path, sha: str) -> None:
    if not isinstance(sha, str) or not COMMIT_ID.fullmatch(sha):
        raise ValueError("chronology requires an immutable full commit SHA")
    if _git(repository, "cat-file", "-t", sha).strip() != b"commit":
        raise ValueError("chronology SHA does not identify a Git commit")


def _require_ancestor(repository: Path, earlier: str, later: str) -> None:
    if earlier == later:
        raise ValueError("registration and evidence require distinct Git commits")
    try:
        result = subprocess.run(
            ("git", "-C", str(repository), "merge-base", "--is-ancestor",
             earlier, later),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    except OSError as exc:
        raise ValueError("Git unavailable for ancestry verification") from exc
    if result.returncode != 0:
        raise ValueError("frozen implementation, registration and evidence "
                         "are not in the required Git ancestor order")


def _verify_registration_unchanged_through_history(
    repository: Path, registration_commit: str, evidence_commit: str,
    registration_name: str,
) -> int:
    """Reject changes at *any* descendant commit between seal and evidence.

    Comparing only the two endpoint blobs misses a committed protocol change
    subsequently reverted just before evidence deposition. Walk all commits
    on DAG ancestry paths (including merged descendants), not just first
    parent, and require the same Git blob at each step.
    """
    sealed_blob = _git(
        repository, "rev-parse", f"{registration_commit}:{registration_name}",
    ).strip()
    descendants = _git(
        repository, "rev-list", "--ancestry-path", "--topo-order",
        f"{registration_commit}..{evidence_commit}",
    ).splitlines()
    if not descendants:
        raise ValueError("missing Git commits between registration and evidence")
    for commit in descendants:
        try:
            blob = _git(
                repository, "rev-parse",
                f"{commit.decode('ascii')}:{registration_name}",
            ).strip()
        except ValueError as exc:
            raise ValueError(
                "registration removed or renamed after prospective Git seal"
            ) from exc
        if blob != sealed_blob:
            raise ValueError(
                "registration changed within Git ancestry after prospective seal"
            )
    return len(descendants)


def audit_registration_chronology(
    *, repository: Path, registration_path: Path, registration_commit: str,
    evidence_path: Path, evidence_commit: str,
) -> dict[str, object]:
    """Check exact committed registration/evidence bytes and ancestry.

    This is a *necessary* machine-checkable precondition. It cannot prove
    preregistration preceded humans observing results, physically independent
    world generation, raw evidence provenance or independent review.
    """
    root = repository.resolve()
    if Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != root:
        raise ValueError("chronology repository must be its Git worktree root")
    registered_file, registration_name = _file_in_repo(root, registration_path)
    evidence_file, evidence_name = _file_in_repo(root, evidence_path)
    if registration_name == evidence_name:
        raise ValueError("registration and evidence must be separate files")

    registration = load_registration(registered_file)
    evidence = load_heldout_evidence(evidence_file)
    frozen = registration["frozen_implementation_commit"]
    for commit in (frozen, registration_commit, evidence_commit):
        _check_commit(root, commit)
    _require_ancestor(root, frozen, registration_commit)
    _require_ancestor(root, registration_commit, evidence_commit)

    frozen_registration = _git(root, "show", f"{registration_commit}:{registration_name}")
    if frozen_registration != registered_file.read_bytes():
        raise ValueError("registration bytes differ from prospective Git seal")
    carried_registration = _git(root, "show", f"{evidence_commit}:{registration_name}")
    if carried_registration != frozen_registration:
        raise ValueError("registration changed after prospective Git seal")
    audited_descendant_commits = _verify_registration_unchanged_through_history(
        root, registration_commit, evidence_commit, registration_name,
    )
    committed_evidence = _git(root, "show", f"{evidence_commit}:{evidence_name}")
    if committed_evidence != evidence_file.read_bytes():
        raise ValueError("heldout evidence bytes differ from committed Git artifact")

    prior_evidence = subprocess.run(
        ("git", "-C", str(root), "cat-file", "-e",
         f"{registration_commit}:{evidence_name}"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    ).returncode == 0
    if prior_evidence and (
        _git(root, "show", f"{registration_commit}:{evidence_name}")
        == committed_evidence
    ):
        raise ValueError("heldout evidence was already committed at registration")
    provisional = assess_heldout_campaign(registration, evidence)
    return {
        "chronology_status": (
            "git_lineage_consistent_requires_independent_review"
            if not prior_evidence else
            "prior_evidence_path_requires_independent_review"
        ),
        "registration_commit": registration_commit,
        "frozen_implementation_commit": frozen,
        "evidence_commit": evidence_commit,
        "registration_digest": provisional["registration_digest"],
        "evidence_sha256": provisional["evidence_sha256"],
        "provisional_metric_assessment": provisional["assessment"],
        "evidence_path_present_at_registration": prior_evidence,
        "registration_unchanged_descendant_commits_checked": (
            audited_descendant_commits
        ),
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "independently confirm the protocol was frozen before results were inspected",
            "verify physical world manifests, seeds and external oracle custody",
            "audit raw closed-Memory witnesses and reproduce frozen-code runs",
            "independent Stage-9 acceptance and INV-25 scientific review",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read-only Stage-9 Git chronology audit, never Golden",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--registration-commit", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    args = parser.parse_args()
    result = audit_registration_chronology(
        repository=args.repo, registration_path=args.registration,
        registration_commit=args.registration_commit,
        evidence_path=args.evidence, evidence_commit=args.evidence_commit,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
