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
from math import isfinite
import json
from itertools import zip_longest
from pathlib import Path
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from i0.modules.causal_lifecycle import (
    agency_evidence_from_autobiography, decode_agency_evidence,
    decode_intervention, decode_observation, decode_review,
)
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


def _decode_archived_p47_float(value: object) -> object:
    """Decode exactly the normative canonical $f64 measurement envelope.

    Canonical JSON stores finite floats as hexadecimal strings, whereas the
    AgencyEvidence validator expects numerical P-47 measurements. Reject
    noncanonical, nonfinite and negative-zero encodings rather than trusting
    a forged tagged object just because the JSON SHA-256 matches.
    """
    if not isinstance(value, dict) or set(value) != {"$f64"}:
        return value
    encoded = value["$f64"]
    if not isinstance(encoded, str):
        raise ValueError("invalid archived P-47 floating measurement")
    try:
        decoded = float.fromhex(encoded)
    except (ValueError, OverflowError) as exc:
        raise ValueError("invalid archived P-47 floating measurement") from exc
    normalized = 0.0 if decoded == 0.0 else decoded
    if not isfinite(decoded) or normalized.hex().lower() != encoded:
        raise ValueError("noncanonical archived P-47 floating measurement")
    return decoded


def _decode_archived_agency_evidence(entry: dict[str, object]):
    # Decode only P-47 numerical slots, never arbitrary owner-state objects.
    fields = dict(entry)
    effects = fields.get("effects")
    if isinstance(effects, list):
        fields["effects"] = [
            [
                _decode_archived_p47_float(value) if index in (2, 3, 4)
                else value
                for index, value in enumerate(effect)
            ] if isinstance(effect, list) else effect
            for effect in effects
        ]
    return decode_agency_evidence(fields)


def _published_p47_from_journal(
    *, event_ref: str, episode_ref: str, causal_event: Mapping[str, object],
):
    """Rebuild the typed P-47 evidence from its exact canonical journal data."""
    data = causal_event.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("effects"), list):
        raise ValueError("invalid raw P-47 comparator data")
    source_data = dict(data)
    source_data["effects"] = [
        {
            key: (
                _decode_archived_p47_float(value)
                if key in {"predicted", "observed", "precision"} else value
            )
            for key, value in effect.items()
        } if isinstance(effect, dict) else effect
        for effect in data["effects"]
    ]
    try:
        result = agency_evidence_from_autobiography(
            episode_ref=episode_ref,
            event={
                "event_id": event_ref,
                "kind": "agency_comparison",
                "t_monde": causal_event.get("t_monde"),
                "data": source_data,
            },
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid raw P-47 comparator data") from exc
    if result is None:
        raise ValueError("raw P-47 comparator has no admissible evidence")
    return result


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
    published_agency_comparisons_checked = 0
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
        published_agency_refs = set()
        if isinstance(causal_owner, dict) and isinstance(
            causal_owner.get("agency_evidence"), list,
        ):
            for entry in causal_owner["agency_evidence"]:
                if (
                    isinstance(entry, dict)
                    and isinstance(entry.get("event_ref"), str)
                ):
                    published_agency_refs.add(entry["event_ref"])
        journal_audit = audit_raw_causal_journal(
            paths["journal_path"], physical_observation_refs=references,
            published_agency_event_refs=published_agency_refs,
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
        # A passive physical observation can inform different contingencies.
        # The (contingency_ref, observation_ref, kind) ledger key above
        # prevents re-crediting it *within* one rule. Interventions require a
        # stronger globally unique physical action and are checked below,
        # matching CausalModel.restore_causal_state().
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
        validated_observations = {}
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
                else:
                    validated_observations[admitted.identifier] = admitted
        # §13.2 independent intervention contexts cannot be manufactured
        # by reusing one physical transition, comparator, emitted step or
        # observed world step. These are per-rule except the physical
        # transition, exactly as in the canonical owner's snapshot restore.
        intervention_physical = set()
        intervention_comparators = set()
        intervention_emissions = set()
        intervention_observed_steps = set()
        for trial in validated_interventions:
            comparator = (trial.contingency_ref, trial.comparator_ref)
            emission = (trial.contingency_ref, trial.emitted_step)
            observed = (trial.contingency_ref, trial.observed_step)
            if (
                trial.observation_ref in intervention_physical
                or comparator in intervention_comparators
                or emission in intervention_emissions
                or observed in intervention_observed_steps
            ):
                raise ValueError(
                    "archived intervention reuses physical or comparator provenance"
                )
            intervention_physical.add(trial.observation_ref)
            intervention_comparators.add(comparator)
            intervention_emissions.add(emission)
            intervention_observed_steps.add(observed)
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
        # Restore §13.2's historical correlation and matched-hypothesis
        # evidence rather than accepting references in a resealed snapshot
        # as if they were independent proof. These observations were already
        # linked above to committed physical transitions and closed Memory.
        correlation_rows = owner.get("causal_correlation_witnesses", [])
        if not isinstance(correlation_rows, list):
            raise ValueError("invalid archived causal correlation witness ledger")
        correlated_refs = set()
        for witness in correlation_rows:
            if (
                not isinstance(witness, list) or len(witness) != 3
                or not isinstance(witness[0], str)
                or witness[0] not in by_ref
                or witness[0] in correlated_refs
                or not all(
                    isinstance(ids, list) and ids
                    and all(isinstance(ref, str) and ref for ref in ids)
                    and ids == sorted(set(ids))
                    for ids in witness[1:]
                )
            ):
                raise ValueError("invalid archived causal correlation witness")
            ref, treated_ids, control_ids = witness
            treated = [validated_observations.get(key) for key in treated_ids]
            controls = [validated_observations.get(key) for key in control_ids]
            contract = owner.get("config_contract")
            n1 = contract.get("n1") if isinstance(contract, dict) else None
            if (
                type(n1) is not int or n1 < 1
                or any(row is None or row.contingency_ref != ref
                       or not row.cause_present for row in treated)
                or any(row is None or row.contingency_ref != ref
                       or row.cause_present for row in controls)
            ):
                raise ValueError("archived correlation lacks matched lived evidence")
            if (
                not all(any(
                    a.observation_context == b.observation_context
                    and a.controlled_variables == b.controlled_variables
                    for b in controls
                ) for a in treated)
                or not all(any(
                    a.observation_context == b.observation_context
                    and a.controlled_variables == b.controlled_variables
                    for a in treated
                ) for b in controls)
                or sum(row.effect_present for row in treated) < n1
                or (
                    sum(row.effect_present for row in treated) * len(controls)
                    <= sum(row.effect_present for row in controls) * len(treated)
                )
            ):
                raise ValueError("archived correlation lacks controlled base-rate contrast")
            correlated_refs.add(ref)
        review_ids = owner.get("causal_reviews", [])
        proof_rows = owner.get("causal_review_proofs", [])
        if not isinstance(review_ids, list) or not isinstance(proof_rows, list):
            raise ValueError("invalid archived causal review ledger")
        if (
            any(not isinstance(ref, str) or not ref for ref in review_ids)
            or len(review_ids) != len(set(review_ids))
        ):
            raise ValueError("invalid archived causal review identity")
        reviewed_refs = set()
        seen_proofs = set()
        for proof_row in proof_rows:
            if not isinstance(proof_row, dict):
                raise ValueError("invalid archived causal review proof")
            try:
                proof = decode_review(proof_row)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("invalid archived causal review proof") from exc
            if proof.identifier in seen_proofs:
                raise ValueError("duplicate archived causal review proof")
            seen_proofs.add(proof.identifier)
            rule = by_ref.get(proof.contingency_ref)
            if (
                rule is None
                or rule.get("causal_status") not in {
                    "hypothese_causale", "testee_par_intervention", "etablie",
                }
            ):
                raise ValueError("archived review lacks published causal hypothesis")
            for treated_id, control_id in proof.contrasting_pairs:
                treated = validated_observations.get(treated_id)
                control = validated_observations.get(control_id)
                if (
                    treated is None or control is None
                    or treated.contingency_ref != proof.contingency_ref
                    or control.contingency_ref != proof.contingency_ref
                    or not treated.cause_present or control.cause_present
                    or treated.controlled_variables != control.controlled_variables
                    or treated.observation_context != control.observation_context
                    or treated.observation_ref == control.observation_ref
                    or treated.observed_step == control.observed_step
                ):
                    raise ValueError(
                        "archived review lacks independent matched physical controls"
                    )
            reviewed_refs.add(proof.contingency_ref)
        if set(review_ids) != seen_proofs:
            raise ValueError("archived causal review ids disagree with proofs")
        # §13.2 applies to *all* published causal levels: observed
        # correlations must retain their matched historical controls, and
        # every hypothesis must retain an independently contrasted review.
        # Restricting this gate to tested/established claims would let a
        # rehashed snapshot invent hypotheses eligible for test proposals.
        correlated_expected = {
            row["ref"] for row in published
            if row.get("causal_status") != "aucun"
        }
        reviewed_expected = {
            row["ref"] for row in published
            if row.get("causal_status") in {
                "hypothese_causale", "testee_par_intervention", "etablie",
            }
        }
        if correlated_refs != correlated_expected:
            raise ValueError(
                "archived promoted causal status lacks historical correlation"
            )
        if reviewed_refs != reviewed_expected:
            raise ValueError(
                "archived causal hypothesis lacks matched review proof"
            )
        # A published intervention is not backed by its own comparator
        # labels. Preserve the canonical owner's publication boundary:
        # only the published DC-09/P-47 agency ledger can corroborate a
        # trial. Pending comparisons never count as causal evidence.
        agency_rows = owner.get("agency_evidence", [])
        pending_agency_rows = owner.get("pending_agency_evidence", [])
        if (
            not isinstance(agency_rows, list)
            or not isinstance(pending_agency_rows, list)
        ):
            raise ValueError("invalid archived agency comparison ledgers")
        agency_by_id = {}
        all_agency_ids = set()
        agency_event_refs = set()
        for rows in (agency_rows, pending_agency_rows):
            for entry in rows:
                if not isinstance(entry, dict):
                    raise ValueError("invalid archived agency comparison")
                try:
                    comparison = _decode_archived_agency_evidence(entry)
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(
                        "invalid archived agency comparison"
                    ) from exc
                if (
                    comparison.identifier in all_agency_ids
                    or comparison.event_ref in agency_event_refs
                ):
                    raise ValueError(
                        "duplicate published or pending agency comparison provenance"
                    )
                all_agency_ids.add(comparison.identifier)
                agency_event_refs.add(comparison.event_ref)
                if rows is agency_rows:
                    agency_by_id[comparison.identifier] = comparison
        for trial in validated_interventions:
            comparison = agency_by_id.get(trial.comparator_ref)
            if (
                comparison is None
                or comparison.source != "agency_comparator"
                or comparison.episode_ref != trial.episode_ref
                or comparison.option_ref != trial.command_ref
                or comparison.sent_t_monde != trial.emitted_step
                or comparison.observed_t_monde != trial.observed_step
                or comparison.status != trial.comparator_status
                or comparison.attribution != trial.attribution
            ):
                raise ValueError(
                    "archived causal intervention lacks matching published agency comparison"
                )
        # The archived P-47 measurements, version and comparator outcome
        # must be the exact projection of the canonical source occurrence.
        # Source event IDs, closed Memory membership and hashes alone would
        # allow two contradictory measurements to masquerade as one event.
        for comparison in agency_by_id.values():
            source = journal_audit["published_agency_source_events"][
                comparison.event_ref
            ]
            reconstructed = _published_p47_from_journal(
                event_ref=comparison.event_ref,
                episode_ref=comparison.episode_ref,
                causal_event=source,
            )
            if reconstructed != comparison:
                raise ValueError(
                    "archived agency comparison disagrees with raw P-47 source"
                )
        memory_audit = audit_archived_closed_memory_sources(
            paths["causal_state_path"],
            claimed_episodes=claimed_episodes,
            physical_source_provenance=journal_audit["physical_source_provenance"],
            claimed_agency_comparisons={
                report.event_ref: (report.episode_ref, report.observed_t_monde)
                for report in agency_by_id.values()
            },
        )
        published_agency_comparisons_checked += memory_audit[
            "published_agency_comparisons_checked"
        ]
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
        "published_agency_comparisons_checked": published_agency_comparisons_checked,
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
