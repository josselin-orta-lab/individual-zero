"""Independent structural audit of archived Stage-9 canonical causal journals.

A matching SHA-256 alone cannot establish that an archived file is an actual
append-only journal or that a row points to a committed physical transition.
This strictly checks syntax, exact normative canonical bytes, hash links,
event identity, and each claimed physical source's applied command/transition
in the same autobiographically committed execution attempt.

It does NOT prove the recorded events actually happened, confirm independent
worlds or validate real Memory episode closure. External custody and review
remain necessary. EN MVP v1.2.1 §§17.4-17.5, 19.5, 20.3; INV-33/44/49.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from .journal import GENESIS_HASH
from .stage9_scientific_assessment import (
    _reject_duplicate_keys, _reject_nonfinite_constant,
)

ENTRY_FIELDS = frozenset({
    "index", "event_id", "previous_hash", "event_hash", "causal_event",
})


def audit_raw_causal_journal(
    path: Path, *, physical_observation_refs: set[str],
) -> dict[str, object]:
    """Read a canonical journal without modifying it or trusting its claims.

    Only a *separate* committed command and world transition from a matching
    attempt can ground a physically identified observational row. This check
    does not infer whether the claimed episode ID was really closed by Memory.
    """
    if not isinstance(physical_observation_refs, set) or any(
        not isinstance(value, str) or not value.strip()
        for value in physical_observation_refs
    ):
        raise ValueError("physical observation references must be nonempty IDs")
    events: dict[str, tuple[int, Mapping[str, object]]] = {}
    commits: list[tuple[int, Mapping[str, object]]] = []
    previous_hash = GENESIS_HASH
    index = 0

    def check(raw: bytes) -> None:
        nonlocal previous_hash, index
        try:
            row = json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_nonfinite_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid canonical journal JSON record") from exc
        if not isinstance(row, dict) or set(row) != ENTRY_FIELDS:
            raise ValueError("invalid canonical journal entry schema")
        if canonical_causal_bytes(row) != raw:
            raise ValueError("journal record is not byte-canonical")
        event_id = row["event_id"]
        event = row["causal_event"]
        if (
            type(row["index"]) is not int
            or row["index"] != index
            or not isinstance(event_id, str) or not event_id
            or event_id in events
            or not isinstance(event, dict)
            or not isinstance(row["previous_hash"], str)
            or not isinstance(row["event_hash"], str)
        ):
            raise ValueError("invalid or repeated canonical journal event identity")
        if row["previous_hash"] != previous_hash:
            raise ValueError("broken causal journal previous-hash chain")
        try:
            digest = sha256_hex(
                bytes.fromhex(previous_hash)
                + canonical_causal_bytes({
                    "event_id": event_id, "causal_event": event,
                })
            )
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid causal journal hash encoding") from exc
        if row["event_hash"] != digest:
            raise ValueError("broken causal journal event hash")
        previous_hash = digest
        events[event_id] = (index, event)
        if event.get("kind") == "auto_segment_commit":
            commits.append((index, event))
        index += 1

    # Hashing is handled by the artifact-custody caller. This second pass
    # examines exact canonical records, never a transformed JSON rendering.
    # The canonical journal format has LF *between* records but no terminal LF.
    with path.open("rb") as stream:
        buffered: bytes | None = None
        for line in stream:
            if buffered is not None:
                if not buffered.endswith(b"\n"):
                    raise ValueError("invalid canonical journal record separator")
                check(buffered[:-1])
            buffered = line
        if buffered is None:
            raise ValueError("empty canonical journal")
        if buffered.endswith(b"\n"):
            raise ValueError("canonical journal has extra final line terminator")
        check(buffered)

    matched = 0
    for ref in sorted(physical_observation_refs):
        transition_entry = events.get(ref)
        if transition_entry is None:
            raise ValueError("reported physical transition absent from raw journal")
        transition_index, transition = transition_entry
        attempt = transition.get("attempt_ref")
        t_monde = transition.get("t_monde")
        if (
            transition.get("kind") != "world_transition_experienced"
            or not isinstance(attempt, str) or not attempt
            or type(t_monde) is not int
        ):
            raise ValueError("reported observation is not a physical transition")
        matched_commits = 0
        for commit_index, commit in commits:
            if commit_index <= transition_index:
                continue
            refs = commit.get("event_refs")
            if (
                commit.get("attempt_ref") != attempt
                or commit.get("t_monde") != t_monde
                or not isinstance(refs, list)
                or ref not in refs
            ):
                continue
            has_command = any(
                isinstance(command_ref, str)
                and command_ref in events
                and events[command_ref][0] < transition_index
                and events[command_ref][1].get("kind") == "command_experienced"
                and events[command_ref][1].get("attempt_ref") == attempt
                and events[command_ref][1].get("t_monde") == t_monde
                for command_ref in refs
            )
            if has_command:
                matched_commits += 1
        if matched_commits != 1:
            raise ValueError(
                "physical observation lacks unique committed same-attempt command"
            )
        matched += 1

    return {
        "journal_events_checked": index,
        "journal_head_hash": previous_hash,
        "claimed_physical_transitions_checked": matched,
        "structural_status": "canonical_chain_and_committed_sources_verified",
        "physical_truth_attested": False,
        "memory_episode_closure_attested": False,
    }
