"""Read-only raw Stage-9 held-out artifact custody audit (never scientific acceptance).

A claimed SHA-256 in an evidence JSON is not a witnessed journal. This tool
checks it against actual immutable-candidate files, with distinct original/
replay artifacts per registered world/seed. It does NOT establish that those
bytes were produced by the declared world, individual, oracle or source code.
EN MVP v1.2.1 sections 13.2, 19.5, 20.3; INV-25/32/33.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from itertools import zip_longest
from pathlib import Path
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from i0.modules.causal_lifecycle import decode_intervention, decode_observation
from .stage9_canonical_journal_audit import audit_raw_causal_journal
from .stage9_memory_custody import audit_archived_closed_memory_sources
from .stage9_scientific_assessment import (
    _reject_duplicate_keys, _reject_nonfinite_constant,
    assess_heldout_campaign, load_heldout_evidence,
)
from .stage9_scientific_preregistration import load_registration


INDEX_VERSION = "stage9-heldout-raw-artifact-index-v4"
INDEX_FIELDS = frozenset({
    "protocol_version", "registration_digest", "evidence_sha256", "runs",
})
RUN_INDEX_FIELDS = frozenset({
    "world_id", "seed", "journal_path", "replay_journal_path",
    "causal_state_path", "replay_causal_state_path",
})
RAW_HASH_FIELDS = {
    "journal_path": "journal_sha256",
    "replay_journal_path": "replay_journal_sha256",
    "causal_state_path": "causal_state_sha256",
    "replay_causal_state_path": "replay_causal_state_sha256",
}


def load_raw_artifact_index(path: Path) -> dict[str, object]:
    """Reject ambiguous JSON; shape validation occurs before any disk reads."""
    index = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite_constant,
    )
    if not isinstance(index, dict):
        raise ValueError("raw artifact index must be a JSON object")
    return index


def _physical_file(root: Path, supplied: object) -> Path:
    if not isinstance(supplied, str) or not supplied.strip():
        raise ValueError("artifact paths must be nonempty strings")
    relative = Path(supplied)
    if (
        relative.is_absolute() or not relative.parts
        or any(part in (".", "..") for part in relative.parts)
    ):
        raise ValueError("artifact path must be relative and without traversal")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("artifact path may not traverse symlinks")
    physical = current.resolve()
    try:
        physical.relative_to(root)
    except ValueError as exc:
        raise ValueError("artifact path escapes its declared root") from exc
    if not physical.is_file():
        raise ValueError("missing raw artifact file")
    return physical


def _file_hash_and_size(path: Path) -> tuple[str, int]:
    digest = sha256()
    total = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            digest.update(chunk)
    if total == 0:
        raise ValueError("empty raw artifact cannot witness an executed run")
    return digest.hexdigest(), total


def _equal_bytes(first: Path, second: Path) -> bool:
    with first.open("rb") as a, second.open("rb") as b:
        for left, right in zip_longest(
            iter(lambda: a.read(1024 * 1024), b""),
            iter(lambda: b.read(1024 * 1024), b""),
        ):
            if left != right:
                return False
    return True


def audit_heldout_raw_artifacts(
    *, registration: Mapping[str, object],
    evidence: Mapping[str, object],
    index: Mapping[str, object],
    artifact_root: Path,
) -> dict[str, object]:
    """Compare physically present files to already-validated evidence claims.

    Two differently named paths (or hardlinks) to the same file are rejected.
    In v4, the canonical closed-Memory owner state is also read from disk and
    reported episode membership is cross-checked against the unique committed
    physical command/transition source (DC-09, INV-33/44/53).
    The index is retrospective file custody metadata, NOT a preregistration or
    a proof that independent world steps really occurred.
    """
    scored = assess_heldout_campaign(registration, evidence)
    if not isinstance(index, dict) or set(index) != INDEX_FIELDS:
        raise ValueError("raw artifact index has missing or extra fields")
    if index["protocol_version"] != INDEX_VERSION:
        raise ValueError("raw artifact index schema mismatch")
    if (
        index["registration_digest"] != scored["registration_digest"]
        or index["evidence_sha256"] != scored["evidence_sha256"]
    ):
        raise ValueError("raw artifact index is not bound to evidence registration")
    rows = index["runs"]
    if not isinstance(rows, list):
        raise ValueError("raw artifact index runs must be a list")

    original_runs = {
        (r["world_id"], r["seed"]): r for r in evidence["runs"]
    }
    if len(rows) != len(original_runs):
        raise ValueError("raw artifact index missing or adding registered runs")
    # The selected custody root itself must not be an alias. Otherwise a
    # symlink swap can redirect every relative evidence path even when
    # individual paths below the resolved root contain no symlink.
    # An alias in *any ancestor* redirects the custody root just as surely
    # as an alias at its last path component.
    root_path = artifact_root.absolute()
    if any(part.is_symlink() for part in (root_path, *root_path.parents)):
        raise ValueError("raw artifact root or ancestor may not be a symlink")
    root = artifact_root.resolve()
    if not root.is_dir():
        raise ValueError("raw artifact root must be a directory")

    seen_runs: set[tuple[str, int]] = set()
    seen_paths: set[Path] = set()
    seen_inodes: set[tuple[int, int]] = set()
    pinned_inodes: dict[Path, tuple[int, int]] = {}
    pinned_artifacts: list[tuple[object, str, Path, tuple[int, int]]] = []
    total_size = 0
    verified_files = 0
    journal_events_checked = 0
    physical_sources_checked = 0
    memory_episodes_scanned = 0
    closed_memory_sources_checked = 0
    for item in rows:
        if not isinstance(item, dict) or set(item) != RUN_INDEX_FIELDS:
            raise ValueError("invalid raw artifact run index")
        world = item["world_id"]
        seed = item["seed"]
        if (
            not isinstance(world, str) or type(seed) is not int
            or (world, seed) not in original_runs
            or (world, seed) in seen_runs
        ):
            raise ValueError("unknown or duplicate indexed world/seed run")
        seen_runs.add((world, seed))
        reported = original_runs[(world, seed)]
        paths: dict[str, Path] = {}
        for index_key, expected_sha_key in RAW_HASH_FIELDS.items():
            physical = _physical_file(root, item[index_key])
            inode = (physical.stat().st_dev, physical.stat().st_ino)
            if physical in seen_paths or inode in seen_inodes:
                raise ValueError("raw artifact reused across runs or replay roles")
            seen_paths.add(physical)
            seen_inodes.add(inode)
            pinned_inodes[physical] = inode
            pinned_artifacts.append((item[index_key], reported[expected_sha_key], physical, inode))
            actual_sha, size = _file_hash_and_size(physical)
            if actual_sha != reported[expected_sha_key]:
                raise ValueError(
                    "raw artifact digest disagrees with registered heldout report: "
                    + index_key
                )
            total_size += size
            verified_files += 1
            paths[index_key] = physical
        if (
            not _equal_bytes(paths["journal_path"], paths["replay_journal_path"])
            or not _equal_bytes(
                paths["causal_state_path"], paths["replay_causal_state_path"],
            )
        ):
            raise ValueError("original and replay raw artifact bytes differ")
        # Digests alone do not prove that the named file is an append-only
        # journal, or that a physical observation ever appeared in it.
        # This structural check is independent of the report's own hashes.
        references = {
            entry["observation_ref"]
            for name in ("known_cause_cases", "naturally_acquired_false_candidates")
            for entry in reported[name]
        }
        # Audit every admitted causal physical source, including interventions
        # omitted from the held-out report's selected scoring rows.
        try:
            archived = json.loads(
                paths["causal_state_path"].read_bytes().decode("utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_nonfinite_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid archived causal owner-state JSON") from exc
        causal_owner = archived.get("causal_model") if isinstance(archived, dict) else None
        if isinstance(causal_owner, dict):
            for ledger in ("causal_observations", "causal_interventions"):
                entries = causal_owner.get(ledger)
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, dict) and isinstance(entry.get("observation_ref"), str):
                            references.add(entry["observation_ref"])
        journal_audit = audit_raw_causal_journal(
            paths["journal_path"], physical_observation_refs=references,
        )
        journal_events_checked += journal_audit["journal_events_checked"]
        physical_sources_checked += journal_audit["claimed_physical_transitions_checked"]
        claimed_episodes = {
            entry["observation_ref"]: entry["episode_ref"]
            for name in ("known_cause_cases", "naturally_acquired_false_candidates")
            for entry in reported[name]
        }
        for ledger in ("causal_observations", "causal_interventions"):
            for entry in causal_owner.get(ledger, []):
                observation = entry["observation_ref"]
                episode = entry.get("episode_ref")
                if (
                    not isinstance(episode, str) or not episode
                    or (observation in claimed_episodes and claimed_episodes[observation] != episode)
                ):
                    raise ValueError("archived causal evidence episode disagrees with heldout source")
                claimed_episodes[observation] = episode
        # A reported natural candidate must correspond to the actual
        # canonical contingency and its archived causal status. Matching only
        # physical episodes would let a forged report invent an established
        # rule without any such rule in the frozen causal owner.
        try:
            state = json.loads(
                paths["causal_state_path"].read_bytes().decode("utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_nonfinite_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid archived causal owner-state JSON") from exc
        if not isinstance(state, dict):
            raise ValueError("archived causal owners must be an object")
        owner = state.get("causal_model")
        published = owner.get("published") if isinstance(owner, dict) else None
        if not isinstance(published, list):
            raise ValueError("archived causal model published state is missing")
        by_ref = {}
        for row in published:
            if (
                not isinstance(row, dict)
                or not isinstance(row.get("ref"), str)
                or not row["ref"]
                or row["ref"] in by_ref
            ):
                raise ValueError("invalid or duplicate archived causal contingency")
            by_ref[row["ref"]] = row
        # Credits are only an index of admitted lived observations and
        # interventions, never independent evidence. Detect invented credits
        # even when a forged snapshot is canonically encoded and rehashed.
        observations = owner.get("causal_observations")
        interventions = owner.get("causal_interventions")
        credits = owner.get("causal_credits")
        if not all(isinstance(rows, list) for rows in (
            observations, interventions, credits,
        )):
            raise ValueError("archived causal provenance ledgers are missing")
        expected_credits = set()
        for rows, kind in ((observations, "observation"),
                           (interventions, "intervention")):
            for entry in rows:
                if not isinstance(entry, dict):
                    raise ValueError("invalid archived causal evidence entry")
                ref = entry.get("contingency_ref")
                observation = entry.get("observation_ref")
                if not all(isinstance(v, str) and v for v in (ref, observation)):
                    raise ValueError("invalid archived causal evidence credit identity")
                if ref not in by_ref:
                    raise ValueError("archived causal evidence refers to unpublished contingency")
                # All admitted causal observations and interventions must
                # agree with the journal's physical world step, including
                # evidence that was not selected for the held-out score.
                physical = journal_audit["physical_source_provenance"][observation]
                if entry.get("observed_step") != physical["t_monde"]:
                    raise ValueError("archived causal evidence world step disagrees with physical source")
                if kind == "intervention" and (
                    entry.get("command_ref") != physical["command_ref"]
                    or entry.get("episode_ref") != claimed_episodes[observation]
                ):
                    raise ValueError("archived intervention disagrees with physical source")
                key = (ref, observation, kind)
                if key in expected_credits:
                    raise ValueError("duplicate archived causal evidence credit")
                expected_credits.add(key)
        # An observation_ref is a physical identity: it cannot be credited
        # to two independent causal rows, even if their contingency differs.
        credited_physical_refs = [
            key[1] for key in expected_credits
        ]
        if len(set(credited_physical_refs)) != len(credited_physical_refs):
            raise ValueError("physical observation reused across causal evidence credits")
        actual_credits = []
        for entry in credits:
            if (
                not isinstance(entry, list) or len(entry) != 3
                or any(not isinstance(value, str) or not value for value in entry)
            ):
                raise ValueError("invalid archived causal credit")
            actual_credits.append(tuple(entry))
        if (
            len(set(actual_credits)) != len(actual_credits)
            or set(actual_credits) != expected_credits
        ):
            raise ValueError("archived causal credits disagree with admitted evidence")
        for candidate in reported["naturally_acquired_false_candidates"]:
            actual = by_ref.get(candidate["contingency_ref"])
            if (
                actual is None
                or actual.get("causal_status") != candidate["causal_status"]
            ):
                raise ValueError("reported natural candidate disagrees with archived causal status")
        # Cross-check syntactic and normative admissibility after independent
        # physical/journal/credit checks. A rehashed owner snapshot must not
        # launder oracle-derived, rolled-back, counterfactual, or unapplied
        # evidence into the causal history.
        validated_interventions = []
        for records, decoder in (
            (observations, decode_observation),
            (interventions, decode_intervention),
        ):
            seen_evidence_ids = set()
            for entry in records:
                try:
                    admitted = decoder(entry)
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(
                        "archived causal evidence is not admissible"
                    ) from exc
                if admitted.identifier in seen_evidence_ids:
                    raise ValueError("duplicate archived causal evidence identifier")
                seen_evidence_ids.add(admitted.identifier)
                if decoder is decode_intervention:
                    validated_interventions.append(admitted)
        # A frozen causal status is not independent evidence. Reconstruct
        # §13.2's negative-result revision boundary and its subsequent
        # successful independent intervention contexts from admitted lived
        # trials rather than trusting the snapshot's claimed status.
        revision_rows = owner.get("causal_revision_boundaries", [])
        if not isinstance(revision_rows, list):
            raise ValueError("invalid archived causal revision boundaries")
        archived_revisions = {}
        for entry in revision_rows:
            if (
                not isinstance(entry, list) or len(entry) != 3
                or not isinstance(entry[0], str) or entry[0] not in by_ref
                or type(entry[1]) is not int or entry[1] < 1
                or not isinstance(entry[2], str) or not entry[2]
                or entry[0] in archived_revisions
            ):
                raise ValueError("invalid archived causal revision boundary")
            archived_revisions[entry[0]] = (entry[1], entry[2])
        witnessed_revisions = {}
        for trial in sorted(
            validated_interventions,
            key=lambda entry: (entry.observed_step, entry.identifier),
        ):
            if trial.observed_effect:
                continue
            previous = witnessed_revisions.get(
                trial.contingency_ref, (-1, ""),
            )[0]
            if trial.observed_step > previous:
                witnessed_revisions[trial.contingency_ref] = (
                    trial.observed_step, trial.identifier,
                )
        if archived_revisions != witnessed_revisions:
            raise ValueError(
                "archived causal revision boundary disagrees with lived counterexamples"
            )
        for row in published:
            if row["causal_status"] not in {
                "testee_par_intervention", "etablie",
            }:
                continue
            ref = row["ref"]
            successes = [
                trial for trial in validated_interventions
                if trial.contingency_ref == ref
                and trial.observed_effect
                and trial.attribution == "self_compatible"
            ]
            if not successes:
                raise ValueError(
                    "archived tested causal status lacks lived intervention"
                )
            if row["causal_status"] != "etablie":
                continue
            contract = owner.get("config_contract")
            n2 = contract.get("n2") if isinstance(contract, dict) else None
            if type(n2) is not int or n2 < 1:
                raise ValueError(
                    "archived established causal status lacks frozen n2 threshold"
                )
            last_failure = witnessed_revisions.get(ref, (-1, ""))[0]
            contexts = {
                trial.context_signature for trial in successes
                if trial.observed_step > last_failure
            }
            if len(contexts) < n2:
                raise ValueError(
                    "archived established causal status lacks independent post-revision contexts"
                )
        memory_audit = audit_archived_closed_memory_sources(
            paths["causal_state_path"],
            claimed_episodes=claimed_episodes,
            physical_source_provenance=journal_audit["physical_source_provenance"],
        )
        memory_episodes_scanned += memory_audit["closed_memory_episodes_scanned"]
        closed_memory_sources_checked += memory_audit[
            "claimed_closed_memory_sources_checked"
        ]
        # Detect durable replacement or mutation after the first hash and
        # structural parsing passes. This is not an atomic filesystem snapshot:
        # an external witness still needs to ensure files cannot change during
        # the audit, including transient edits reverted before this check.
        for index_key, expected_sha_key in RAW_HASH_FIELDS.items():
            physical = paths[index_key]
            if (
                _physical_file(root, item[index_key]) != physical
                or (physical.stat().st_dev, physical.stat().st_ino)
                != pinned_inodes[physical]
                or _file_hash_and_size(physical)[0] != reported[expected_sha_key]
            ):
                raise ValueError("raw artifact changed during custody audit")
    # Each run is checked again before returning, not just immediately after
    # its own parsing. A later run must not mask changes to earlier artifacts.
    for relative, expected_digest, original_path, original_inode in pinned_artifacts:
        current_path = _physical_file(root, relative)
        if (
            current_path != original_path
            or (current_path.stat().st_dev, current_path.stat().st_ino)
            != original_inode
            or _file_hash_and_size(current_path)[0] != expected_digest
        ):
            raise ValueError("raw artifact changed before custody audit completion")
    if seen_runs != set(original_runs):
        raise ValueError("raw artifact index did not cover every heldout run")

    return {
        "artifact_custody_status": (
            "raw_bytes_match_report_requires_independent_provenance_review"
        ),
        "index_sha256": sha256_hex(canonical_causal_bytes(index)),
        "registration_digest": scored["registration_digest"],
        "evidence_sha256": scored["evidence_sha256"],
        "provisional_metric_assessment": scored["assessment"],
        "runs_checked": len(seen_runs),
        "raw_files_checked": verified_files,
        "total_bytes_checked": total_size,
        "original_replay_bytes_identical": True,
        "journal_chain_integrity_verified": True,
        "journal_events_checked": journal_events_checked,
        "committed_physical_sources_checked": physical_sources_checked,
        "archived_causal_owner_state_canonical": True,
        "closed_memory_episodes_scanned": memory_episodes_scanned,
        "claimed_closed_memory_sources_checked": closed_memory_sources_checked,
        "closed_episode_membership_structurally_verified": True,
        "memory_runtime_attested": False,
        "physical_truth_attested": False,
        "memory_episode_closure_attested": False,
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "attest that archived files were produced by the declared frozen code",
            "independently witness physical world provenance and oracle custody",
            "independently attest that archived Memory state was produced by the real run",
            "verify prospective registration, sampling independence and INV-25",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-9 read-only heldout artifact hash check; not Golden",
    )
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    result = audit_heldout_raw_artifacts(
        registration=load_registration(args.registration),
        evidence=load_heldout_evidence(args.evidence),
        index=load_raw_artifact_index(args.index),
        artifact_root=args.artifact_root,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
