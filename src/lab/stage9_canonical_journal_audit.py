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
from io import BytesIO
import json
from pathlib import Path
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from .journal import GENESIS_HASH
from .stage9_secure_file_read import open_regular_no_follow
from .stage9_scientific_assessment import (
    _reject_duplicate_keys, _reject_nonfinite_constant,
)

ENTRY_FIELDS = frozenset({
    "index", "event_id", "previous_hash", "event_hash", "causal_event",
})


def audit_raw_causal_journal(
    path: Path, *, physical_observation_refs: set[str],
    published_agency_event_refs: set[str] | None = None,
    verified_journal_bytes: bytes | None = None,
) -> dict[str, object]:
    """Audit exact canonical records without trusting journal claims.

    The optional byte image is supplied by the custody audit *after* that
    caller verifies its SHA-256 against the registered held-out report.
    Standalone use still opens the path through a guarded no-follow descriptor.
    Supplying bytes alone does not independently attest their physical origin.

    Only a separate committed command and transition from the same attempt
    can ground an observational row; this is not a Memory closure witness.
    """
    if not isinstance(physical_observation_refs, set) or any(
        not isinstance(value, str) or not value.strip()
        for value in physical_observation_refs
    ):
        raise ValueError("physical observation references must be nonempty IDs")
    agency_refs = (
        set() if published_agency_event_refs is None
        else published_agency_event_refs
    )
    if not isinstance(agency_refs, set) or any(
        not isinstance(ref, str) or not ref.strip()
        for ref in agency_refs
    ):
        raise ValueError("published agency references must be nonempty IDs")
    events: dict[str, tuple[int, Mapping[str, object]]] = {}
    # Separate technical occurrences (including cancelled retries) by the
    # execution attempt and world step. An accepted physical step cannot
    # silently conceal a second command, advancement, or Memory commit.
    physical_by_attempt: dict[
        tuple[str, int], dict[str, list[tuple[int, str]]]
    ] = {}
    commits_by_attempt: dict[
        tuple[str, int], list[tuple[int, Mapping[str, object]]]
    ] = {}
    attempt_steps: dict[str, int] = {}
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
        kind = event.get("kind")
        if kind in {
            "command_experienced", "world_transition_experienced",
            "auto_segment_commit",
        }:
            attempt = event.get("attempt_ref")
            step = event.get("t_monde")
            if (
                not isinstance(attempt, str) or not attempt
                or type(step) is not int or step < 0
            ):
                raise ValueError(
                    "invalid physical journal event attempt and world step"
                )
            prior_step = attempt_steps.setdefault(attempt, step)
            if prior_step != step:
                raise ValueError("physical attempt reused across world steps")
            key = (attempt, step)
            if kind == "auto_segment_commit":
                commits_by_attempt.setdefault(key, []).append((index, event))
            else:
                physical_by_attempt.setdefault(key, {}).setdefault(
                    kind, []
                ).append((index, event_id))
        index += 1

    # Use the *same* registered-digest-bound bytes from the custody caller.
    # Direct use still reads a guarded descriptor. BytesIO reproduces the
    # identical line iteration, including exact final-LF validation.
    if verified_journal_bytes is not None and not isinstance(
        verified_journal_bytes, bytes
    ):
        raise ValueError("verified canonical journal image must be bytes")
    source = (
        open_regular_no_follow(path) if verified_journal_bytes is None
        else BytesIO(verified_journal_bytes)
    )
    with source as stream:
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

    # INV-53 is per *world step*, not per attempt_ref. After rollback the
    # technical journal may retain cancelled commands and transitions on
    # different attempts for one world time, but those uncommitted attempts
    # cannot become second accepted advancements. Two distinct attempts that
    # each contain a command, transition and autobiographical commit at the
    # same t_monde claim two completed world advancements: reject regardless
    # of whether the operator selected both as held-out observations.
    accepted_steps: dict[int, str] = {}
    for (attempt, step), commits in sorted(commits_by_attempt.items()):
        # Every autobiographical commit is part of the committed journal,
        # even if its transition is not selected for the scientific score.
        # The per-source checks below alone cannot reject a duplicated or
        # malformed *unreported* completed physical step.
        if len(commits) != 1:
            raise ValueError("physical attempt has multiple Memory commits")
        commit_index, commit = commits[0]
        refs = commit.get("event_refs")
        if (
            not isinstance(refs, list)
            or any(not isinstance(value, str) or not value for value in refs)
            or len(set(refs)) != len(refs)
            or any(
                value not in events or events[value][0] >= commit_index
                for value in refs
            )
        ):
            raise ValueError("invalid committed physical event references")
        pair = physical_by_attempt.get((attempt, step), {})
        commands = pair.get("command_experienced", ())
        transitions = pair.get("world_transition_experienced", ())
        if not commands and not transitions:
            # An admissibility block before sending can close a step with
            # zero applied commands and zero world advancement (INV-53).
            continue
        if len(commands) != 1 or len(transitions) != 1:
            raise ValueError(
                "committed physical attempt has nonunique command or world advancement"
            )
        command_index, command_ref = commands[0]
        transition_index, transition_ref = transitions[0]
        if (
            not command_index < transition_index < commit_index
            or command_ref not in refs
            or transition_ref not in refs
        ):
            raise ValueError("committed physical attempt lacks ordered applied events")
        if any(
            events[value][1].get("kind") in {
                "command_experienced", "world_transition_experienced",
            }
            and (
                events[value][1].get("attempt_ref"),
                events[value][1].get("t_monde"),
            ) != (attempt, step)
            for value in refs
        ):
            raise ValueError("committed physical attempt references foreign physical source")
        previous_attempt = accepted_steps.get(step)
        if previous_attempt is not None and previous_attempt != attempt:
            raise ValueError(
                "multiple committed physical advancements at one world step"
            )
        accepted_steps[step] = attempt

    matched = 0
    physical_source_provenance: dict[str, dict[str, object]] = {}
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
        # INV-53 concerns the *actual attempt*, not only the event_refs
        # chosen by a purported commit. An unreferenced extra command or
        # transition would otherwise disappear from the claimed denominator.
        paired = physical_by_attempt.get((attempt, t_monde), {})
        commands = paired.get("command_experienced", ())
        transitions = paired.get("world_transition_experienced", ())
        if (
            len(commands) != 1
            or len(transitions) != 1
            or transitions[0] != (transition_index, ref)
        ):
            raise ValueError(
                "physical observation has nonunique command or world advancement"
            )
        command_index, command_ref = commands[0]
        if command_index >= transition_index:
            raise ValueError("physical observation precedes its applied command")

        # INV-44: exactly one autobiographical commit can close the accepted
        # attempt. Check the *whole* event_refs list, not just two convenient
        # members, so a rehashed foreign or future source cannot be laundered.
        closed = commits_by_attempt.get((attempt, t_monde), ())
        if len(closed) != 1:
            raise ValueError(
                "physical observation lacks unique same-attempt Memory commit"
            )
        commit_index, commit = closed[0]
        refs = commit.get("event_refs")
        if (
            commit_index <= transition_index
            or not isinstance(refs, list)
            or any(not isinstance(value, str) or not value for value in refs)
            or len(set(refs)) != len(refs)
            or ref not in refs
            or command_ref not in refs
        ):
            raise ValueError(
                "physical observation lacks unique committed same-attempt command"
            )
        if any(
            event_ref not in events
            or events[event_ref][0] >= commit_index
            or events[event_ref][1].get("attempt_ref") != attempt
            or events[event_ref][1].get("t_monde") != t_monde
            for event_ref in refs
        ):
            raise ValueError("Memory commit refers to foreign or future event")
        physical_source_provenance[ref] = {
            "command_ref": command_ref,
            "attempt_ref": attempt,
            "t_monde": t_monde,
        }
        matched += 1

    # P-47 evidence that is already published must originate from its
    # *actual* DC-09-committed comparator occurrence, not merely an event ID
    # appended to a resealed Memory snapshot. An independent physical source
    # still requires external witness; this is a structural byte-level join.
    agency_source_events: dict[str, Mapping[str, object]] = {}
    agency_physical_sources: dict[str, dict[str, object]] = {}
    for ref in sorted(agency_refs):
        source = events.get(ref)
        if source is None or source[1].get("kind") != "agency_comparison":
            raise ValueError("published agency comparison absent from raw journal")
        source_index, event = source
        attempt = event.get("attempt_ref")
        step = event.get("t_monde")
        if (
            not isinstance(attempt, str) or not attempt
            or type(step) is not int or step < 0
            or not isinstance(event.get("data"), dict)
        ):
            raise ValueError("invalid raw agency comparison provenance")
        commits = commits_by_attempt.get((attempt, step), ())
        if len(commits) != 1:
            raise ValueError("published agency source lacks same-attempt commit")
        commit_index, commit = commits[0]
        refs = commit.get("event_refs")
        # A P-47 source must come from an accepted physically executed step:
        # it is compared to the new capture before that step's next command,
        # never invented after the outcome or in an orphan attempt.
        paired = physical_by_attempt.get((attempt, step), {})
        commands = paired.get("command_experienced", ())
        transitions = paired.get("world_transition_experienced", ())
        if len(commands) != 1 or len(transitions) != 1:
            raise ValueError(
                "published agency source lacks same-attempt physical execution"
            )
        command_index, command_ref = commands[0]
        transition_index, transition_ref = transitions[0]
        if not (
            source_index < command_index < transition_index < commit_index
        ):
            raise ValueError(
                "published agency source violates physical comparator event order"
            )
        if (
            not isinstance(refs, list)
            or ref not in refs
            or command_ref not in refs
            or transition_ref not in refs
            or len(refs) != len(set(refs))
            or any(
                v not in events
                or events[v][0] >= commit_index
                or events[v][1].get("attempt_ref") != attempt
                or events[v][1].get("t_monde") != step
                for v in refs
            )
        ):
            raise ValueError(
                "published agency comparison absent from its autobiographical commit"
            )
        agency_source_events[ref] = event
        agency_physical_sources[ref] = {
            "command_ref": command_ref,
            "transition_ref": transition_ref,
            "attempt_ref": attempt,
            "t_monde": step,
        }

    return {
        "journal_events_checked": index,
        "journal_head_hash": previous_hash,
        "claimed_physical_transitions_checked": matched,
        "physical_source_provenance": physical_source_provenance,
        "published_agency_source_events": agency_source_events,
        "published_agency_physical_sources": agency_physical_sources,
        "published_agency_sources_checked": len(agency_source_events),
        "structural_status": "canonical_chain_and_committed_sources_verified",
        "physical_truth_attested": False,
        "memory_episode_closure_attested": False,
    }
