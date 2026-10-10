"""Read-only Git ancestry audit for Stage-9 preregistration and heldout evidence.

This checks committed bytes and DAG ancestry, not when an experimenter saw
outcomes or whether claimed World/Body journals and oracle truth are genuine.
It never declares scientific acceptance or freezes a Golden. EN MVP v1.2.1
INV-25/32/33, sections 13.2, 19.5 and 20.3.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
import re
import subprocess

from .stage9_scientific_assessment import (
    assess_heldout_campaign, load_heldout_evidence,
)
from .stage9_scientific_preregistration import SPEC_PATH, load_registration


COMMIT_ID = re.compile(r"[0-9a-f]{40}\Z")


def _git(repository: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ("git", "-C", str(repository), "--no-replace-objects", *arguments),
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
            ("git", "-C", str(repository), "--no-replace-objects",
             "merge-base", "--is-ancestor",
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


SOURCE_TREE_PATH = "src"
PROJECT_INSTALL_PATH = "pyproject.toml"


def _verify_frozen_source_tree(
    repository: Path, frozen_commit: str, evidence_commit: str,
) -> tuple[str, str, int]:
    """Pin source code AND project installer across the experiment lineage.

    Git object IDs identify content (including file modes and paths). Checking
    each descendant, rather than the final endpoint alone, also detects an
    intermediate source edit subsequently reverted before evidence archival.
    Project metadata matters too: it selects the Python package entry points,
    build backend, Python compatibility and dependency requirements. Neither
    object ID proves which checkout, environment or binary actually ran.
    """
    def tree_at(commit: str) -> bytes:
        try:
            oid = _git(repository, "rev-parse", f"{commit}:{SOURCE_TREE_PATH}").strip()
        except ValueError as exc:
            raise ValueError("frozen source tree absent in Git ancestry") from exc
        if _git(repository, "cat-file", "-t", oid.decode("ascii")).strip() != b"tree":
            raise ValueError("frozen source path is not a Git tree")
        return oid

    def installer_blob_at(commit: str) -> bytes:
        try:
            oid = _git(
                repository, "rev-parse", f"{commit}:{PROJECT_INSTALL_PATH}",
            ).strip()
        except ValueError as exc:
            raise ValueError("frozen project installation manifest absent") from exc
        if _git(repository, "cat-file", "-t", oid.decode("ascii")).strip() != b"blob":
            raise ValueError("frozen project installation manifest is not a file")
        return oid

    frozen_tree = tree_at(frozen_commit)
    frozen_installer = installer_blob_at(frozen_commit)
    descendants = _git(
        repository, "rev-list", "--ancestry-path", "--topo-order",
        f"{frozen_commit}..{evidence_commit}",
    ).splitlines()
    if not descendants:
        raise ValueError("missing source-tree descendants before evidence")
    for commit in descendants:
        current = tree_at(commit.decode("ascii"))
        if current != frozen_tree:
            raise ValueError("frozen source tree changed within Git ancestry")
        if installer_blob_at(commit.decode("ascii")) != frozen_installer:
            raise ValueError("frozen project installation manifest changed within Git ancestry")
    return (
        frozen_tree.decode("ascii"), frozen_installer.decode("ascii"),
        len(descendants),
    )


def _verify_frozen_normative_specification(
    repository: Path, frozen_commit: str, evidence_commit: str,
    expected_sha256: str,
) -> tuple[str, int]:
    """Keep the English normative rules byte-identical across the Git DAG.

    Source and installer code may remain frozen even while the specification
    used to interpret outcomes is changed and then reverted. Verify the
    normative blob at *every* descendant from software freeze to evidence,
    including the prospective registration commit and merged descendants.
    """
    def blob_at(commit: str) -> bytes:
        try:
            oid = _git(repository, "rev-parse", f"{commit}:{SPEC_PATH}").strip()
        except ValueError as exc:
            raise ValueError(
                "frozen normative specification missing in Git ancestry"
            ) from exc
        if _git(repository, "cat-file", "-t", oid.decode("ascii")).strip() != b"blob":
            raise ValueError("normative specification must be a Git blob")
        return oid

    original_blob = blob_at(frozen_commit)
    original_bytes = _git(repository, "cat-file", "blob", original_blob.decode("ascii"))
    if sha256(original_bytes).hexdigest() != expected_sha256:
        raise ValueError(
            "frozen normative specification digest disagrees with preregistration"
        )
    descendants = _git(
        repository, "rev-list", "--ancestry-path", "--topo-order",
        f"{frozen_commit}..{evidence_commit}",
    ).splitlines()
    if not descendants:
        raise ValueError("missing normative specification ancestry to evidence")
    for commit in descendants:
        if blob_at(commit.decode("ascii")) != original_blob:
            raise ValueError("normative specification changed within Git ancestry")
    return original_blob.decode("ascii"), len(descendants)


def _audit_pre_registration_evidence_history(
    repository: Path, registration_commit: str, evidence_name: str,
    archived_bytes: bytes,
) -> tuple[bool, int]:
    """Detect an early result at its final path, including create/delete.

    Looking only at the registration commit misses a pre-registration Git
    outcome deliberately deleted immediately before sealing the protocol.
    Search the registration commit's *own ancestors*, not unrelated branches.
    A byte-identical result in earlier history is incompatible with a
    prospective heldout claim. Different earlier contents (e.g. a placeholder)
    remain ambiguous and must be independently reviewed.
    """
    commits = _git(
        repository, "log", "--full-history", "--format=%H",
        registration_commit, "--", evidence_name,
    ).splitlines()
    for commit in commits:
        commit_hex = commit.decode("ascii")
        exists = subprocess.run(
            ("git", "-C", str(repository), "--no-replace-objects",
             "cat-file", "-e", f"{commit_hex}:{evidence_name}"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if exists.returncode == 0 and (
            _git(repository, "show", f"{commit_hex}:{evidence_name}")
            == archived_bytes
        ):
            raise ValueError(
                "heldout evidence was already committed before prospective registration"
            )
    return bool(commits), len(commits)


def _reject_pre_registration_evidence_blob(
    repository: Path, registration_commit: str, evidence_commit: str,
    evidence_name: str,
) -> int:
    """Reject early byte-identical results, even at a *different* Git path.

    A path-specific Git log is insufficient: a preexisting result can be
    committed under another name and later copied into the reported path.
    Git blob IDs commit to the exact file bytes, not its name. Enumerate
    all objects reachable from the sealed registration commit, including
    deleted ancestors and merged history. This cannot detect re-encoding,
    external results, or data inspected but never committed.
    """
    evidence_blob = _git(
        repository, "rev-parse", f"{evidence_commit}:{evidence_name}",
    ).strip()
    if _git(repository, "cat-file", "-t", evidence_blob.decode("ascii")).strip() != b"blob":
        raise ValueError("heldout evidence must be a committed Git blob")
    objects = _git(
        repository, "rev-list", "--objects", "--no-object-names",
        registration_commit,
    ).splitlines()
    if evidence_blob in objects:
        raise ValueError(
            "heldout evidence bytes existed in Git before prospective registration"
        )
    return len(objects)


def _reject_duplicate_candidate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key in earlier candidate JSON")
        result[key] = value
    return result


def _reject_nonfinite_candidate_constant(value: str) -> None:
    raise ValueError("nonfinite earlier candidate JSON constant")


def _unordered_stage9_report_payload(value: object) -> dict[str, object] | None:
    """Canonicalize only *presentation* order for Stage-9 prior-result checks.

    The report-level SHA-256 changes when the same records are presented in
    another order. World/seed cells, known-cause cases and false-rule rows
    are identified independently of list position, so reordering these
    arrays or recalculating evidence_sha256 is not a new heldout experiment.
    This is a screening comparison, never a way to validate scientific data.
    """
    if (
        not isinstance(value, dict)
        or value.get("protocol_version") != "stage9-heldout-evidence-v2"
        or not isinstance(value.get("runs"), list)
    ):
        return None

    def sorted_json_rows(rows: list[object]) -> list[object]:
        return sorted(
            rows,
            key=lambda item: json.dumps(
                item, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"), allow_nan=False,
            ),
        )

    payload = {key: item for key, item in value.items()
               if key != "evidence_sha256"}
    normalized_runs = []
    for row in value["runs"]:
        if not isinstance(row, dict):
            return None
        normalized = dict(row)
        for field in (
            "known_cause_cases", "naturally_acquired_false_candidates",
        ):
            if not isinstance(row.get(field), list):
                return None
            normalized[field] = sorted_json_rows(row[field])
        normalized_runs.append(normalized)
    payload["runs"] = sorted_json_rows(normalized_runs)
    return payload


def _reject_semantic_pre_registration_evidence(
    repository: Path, registration_commit: str, evidence: dict[str, object],
    archived_size: int,
) -> tuple[int, int, int]:
    """Detect earlier JSON reports with identical content but different bytes.

    Exact Git-blob equality is checked separately, without a size limit.
    This bounded supplementary scan catches reordered and reformatted JSON
    anywhere in the registration's reachable Git history. Oversized objects
    are counted as unexamined; external custody still decides prospectivity.
    """
    ids = _git(
        repository, "rev-list", "--objects", "--no-object-names",
        registration_commit,
    ).splitlines()
    if not ids:
        raise ValueError("missing pre-registration Git objects")
    try:
        metadata = subprocess.run(
            ("git", "-C", str(repository), "--no-replace-objects",
             "cat-file", "--batch-check"),
            input=b"".join(oid + b"\n" for oid in ids),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    except OSError as exc:
        raise ValueError("Git unavailable for semantic evidence scan") from exc
    if metadata.returncode:
        raise ValueError("pre-registration Git metadata scan failed")
    rows = metadata.stdout.splitlines()
    if len(rows) != len(ids):
        raise ValueError("incomplete pre-registration Git metadata scan")
    # Large unrelated blobs (e.g. the normative specification) must not
    # exhaust the audit. The soft cap allows substantial JSON reformatting
    # while disclosing the unexamined object count.
    size_limit = min(max(archived_size * 8 + 4096, 1024 * 1024), 64 * 1024 * 1024)
    compared = skipped = ambiguous_stage9 = 0
    archived_unordered = _unordered_stage9_report_payload(evidence)
    if archived_unordered is None:
        raise ValueError("archived heldout evidence has no comparable Stage-9 rows")
    for oid, row in zip(ids, rows):
        fields = row.split()
        if (
            len(fields) != 3 or fields[0] != oid or
            fields[1] not in (b"blob", b"tree", b"commit", b"tag")
        ):
            raise ValueError("invalid pre-registration Git object metadata")
        if fields[1] != b"blob":
            continue
        try:
            size = int(fields[2])
        except ValueError as exc:
            raise ValueError("invalid pre-registration Git blob size") from exc
        if size > size_limit:
            skipped += 1
            continue
        raw = _git(repository, "cat-file", "blob", oid.decode("ascii"))
        # Do not require a known filename extension. A JSON report can be
        # hidden behind a .txt, .bin or extensionless tracked path.
        if not raw.lstrip().startswith(b"{"):
            continue
        compared += 1
        try:
            candidate = json.loads(
                raw,
                object_pairs_hook=_reject_duplicate_candidate_keys,
                parse_constant=_reject_nonfinite_candidate_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
            # A malformed prior Stage-9 envelope is not proof of an
            # independent prospectively acquired report. In particular,
            # silently skipping duplicate-key or NaN-bearing variants would
            # turn a known provenance ambiguity into a clean receipt.
            # Read it a *second time* permissively only to identify an
            # obvious prior Stage-9 envelope. Never use this parse for
            # accepted evidence or metric computation.
            try:
                loose = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
                loose = None
            is_stage9 = (
                isinstance(loose, dict)
                and loose.get("protocol_version") == "stage9-heldout-evidence-v2"
                and "registration_digest" in loose and "runs" in loose
            ) or (
                b"stage9-heldout-evidence-v2" in raw
                and b"registration_digest" in raw and b"runs" in raw
            )
            if is_stage9:
                if loose == evidence:
                    raise ValueError(
                        "ambiguous pre-registration heldout JSON can decode "
                        "to archived scientific evidence"
                    )
                ambiguous_stage9 += 1
            continue
        if candidate == evidence:
            raise ValueError(
                "semantically identical heldout evidence existed in Git before preregistration"
            )
        try:
            unordered = _unordered_stage9_report_payload(candidate)
        except (TypeError, ValueError, RecursionError):
            unordered = None
        if unordered is not None and unordered == archived_unordered:
            raise ValueError(
                "reordered heldout observations existed in Git before preregistration"
            )
    return compared, skipped, ambiguous_stage9


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
    if _git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise ValueError("chronology requires complete unshallowed Git history")
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
    source_tree_sha, installer_blob_sha, source_commits_checked = _verify_frozen_source_tree(
        root, frozen, evidence_commit,
    )
    normative_blob_sha, normative_commits_checked = _verify_frozen_normative_specification(
        root, frozen, evidence_commit,
        registration["normative_specification_sha256"],
    )

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
        ("git", "-C", str(root), "--no-replace-objects", "cat-file", "-e",
         f"{registration_commit}:{evidence_name}"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    ).returncode == 0
    earlier_evidence, prior_evidence_commits_checked = (
        _audit_pre_registration_evidence_history(
            root, registration_commit, evidence_name, committed_evidence,
        )
    )
    # Git log normally records any create/delete of the path, but a commit
    # can carry a preexisting file unchanged. Preserve the endpoint check.
    earlier_evidence = earlier_evidence or prior_evidence
    prior_objects_checked = _reject_pre_registration_evidence_blob(
        root, registration_commit, evidence_commit, evidence_name,
    )
    semantic_blobs_checked, oversized_blobs_not_checked, ambiguous_stage9_blobs = (
        _reject_semantic_pre_registration_evidence(
            root, registration_commit, evidence, len(committed_evidence),
        )
    )
    provisional = assess_heldout_campaign(registration, evidence)
    return {
        "chronology_status": (
            "git_lineage_consistent_requires_independent_review"
            if not earlier_evidence else
            "prior_evidence_path_requires_independent_review"
        ),
        "registration_commit": registration_commit,
        "frozen_implementation_commit": frozen,
        "frozen_source_tree_sha": source_tree_sha,
        "frozen_pyproject_blob_sha": installer_blob_sha,
        "frozen_normative_specification_blob_sha": normative_blob_sha,
        "normative_specification_unchanged_descendant_commits_checked": (
            normative_commits_checked
        ),
        "source_tree_unchanged_descendant_commits_checked": source_commits_checked,
        "evidence_commit": evidence_commit,
        "registration_digest": provisional["registration_digest"],
        "evidence_sha256": provisional["evidence_sha256"],
        "provisional_metric_assessment": provisional["assessment"],
        "evidence_path_present_at_registration": prior_evidence,
        "evidence_path_seen_in_pre_registration_git_history": earlier_evidence,
        "pre_registration_evidence_path_commits_checked": (
            prior_evidence_commits_checked
        ),
        "pre_registration_git_objects_checked": prior_objects_checked,
        "pre_registration_json_blobs_checked": semantic_blobs_checked,
        "pre_registration_oversized_blobs_not_checked": oversized_blobs_not_checked,
        "pre_registration_ambiguous_stage9_json_blobs": ambiguous_stage9_blobs,
        "pre_registration_semantic_scan_complete": (
            oversized_blobs_not_checked == 0 and ambiguous_stage9_blobs == 0
        ),
        "registration_unchanged_descendant_commits_checked": (
            audited_descendant_commits
        ),
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "independently confirm the protocol was frozen before results were inspected",
            "verify physical world manifests, seeds and external oracle custody",
            "audit raw closed-Memory witnesses and reproduce frozen-code runs",
            "verify the actual executed checkout and binary match the frozen Git source",
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
