"""Read-only custody of reported closed-Memory episode references.

Checks the saved, canonical all-owner causal snapshot from an already hashed
Stage-9 run. A declared physical observation must be in an *existing closed*
Memory episode along with the recorded applied command from its unique
AutoSegmentCommit. This is a structural cross-check, never a witness that
Memory or the real world actually performed the recorded events.

EN MVP v1.2.1 §§10.3-10.4, 17.4-17.5; DC-09; INV-27/33/44.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .determinism import canonical_causal_bytes
from .stage9_scientific_assessment import (
    _reject_duplicate_keys, _reject_nonfinite_constant,
)


def audit_archived_closed_memory_sources(
    state_path: Path, *,
    claimed_episodes: Mapping[str, str],
    physical_source_provenance: Mapping[str, Mapping[str, object]],
    claimed_agency_comparisons: Mapping[str, tuple[str, int]] | None = None,
) -> dict[str, object]:
    """Validate exact serialized Memory closure without mutating any file."""
    if set(claimed_episodes) != set(physical_source_provenance):
        raise ValueError("archived Memory claims disagree with physical sources")
    try:
        raw = state_path.read_bytes()
        causal_owners = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid archived causal owner-state JSON") from exc
    if not isinstance(causal_owners, dict):
        raise ValueError("archived causal owners must be an object")
    try:
        exact = canonical_causal_bytes(causal_owners)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid archived canonical causal state") from exc
    if raw != exact:
        raise ValueError("archived causal owner state is not byte-canonical")

    # "memory" is the real EpisodicMemory.owner_id, not a new owner.
    memory = causal_owners.get("memory")
    if not isinstance(memory, dict):
        raise ValueError("archived causal state lacks Memory owner")
    episodes = memory.get("episodes")
    seen = memory.get("seen_event_refs")
    if not isinstance(episodes, list) or not isinstance(seen, list):
        raise ValueError("archived Memory episode and seen-ref lists are required")
    if any(not isinstance(ref, str) or not ref for ref in seen):
        raise ValueError("invalid seen autobiographical event identity")
    if len(seen) != len(set(seen)):
        raise ValueError("duplicate Memory seen event identity")
    seen_refs = set(seen)

    closed: dict[str, tuple[set[str], int, int]] = {}
    owned_refs: set[str] = set()
    for item in episodes:
        if not isinstance(item, dict):
            raise ValueError("invalid archived closed Memory episode")
        episode_ref = item.get("id")
        refs = item.get("event_refs")
        start = item.get("start_t_monde")
        end = item.get("end_t_monde")
        if (
            not isinstance(episode_ref, str) or not episode_ref
            or episode_ref in closed
            or not isinstance(refs, list) or not refs
            or any(not isinstance(ref, str) or not ref for ref in refs)
            or len(set(refs)) != len(refs)
            or type(start) is not int or type(end) is not int
            or start < 0 or end < start
        ):
            raise ValueError("invalid or repeated archived closed Memory episode")
        if any(ref in owned_refs or ref not in seen_refs for ref in refs):
            raise ValueError("reused or unseen event in archived Memory episode")
        owned_refs.update(refs)
        closed[episode_ref] = (set(refs), start, end)

    for observation_ref, episode_ref in sorted(claimed_episodes.items()):
        if not isinstance(observation_ref, str) or not observation_ref:
            raise ValueError("invalid physical Memory source reference")
        if not isinstance(episode_ref, str) or not episode_ref:
            raise ValueError("invalid claimed closed Memory episode reference")
        if episode_ref not in closed:
            raise ValueError("reported Memory episode is not archived as closed")
        info = physical_source_provenance[observation_ref]
        command_ref = info.get("command_ref")
        world_step = info.get("t_monde")
        event_refs, start, end = closed[episode_ref]
        if (
            not isinstance(command_ref, str) or not command_ref
            or type(world_step) is not int
            or observation_ref not in event_refs
            or command_ref not in event_refs
            or not (start <= world_step <= end)
        ):
            raise ValueError(
                "physical command and observation are not in one closed Memory episode"
            )

    # The observed P-47 comparison is a separate DC-09 autobiographical
    # event, not the world-transition ID. Its published source must be
    # present in the exact closed episode that admitted the report.
    agency_claims = (
        {} if claimed_agency_comparisons is None
        else claimed_agency_comparisons
    )
    for event_ref, claimed in sorted(agency_claims.items()):
        if (
            not isinstance(event_ref, str) or not event_ref
            or not isinstance(claimed, (tuple, list)) or len(claimed) != 2
            or not isinstance(claimed[0], str) or not claimed[0]
            or type(claimed[1]) is not int or claimed[1] < 0
        ):
            raise ValueError("invalid published agency Memory provenance")
        episode_ref, observed_step = claimed
        item = closed.get(episode_ref)
        if (
            item is None
            or event_ref not in item[0]
            or event_ref not in seen_refs
            or not (item[1] <= observed_step <= item[2])
        ):
            raise ValueError(
                "published agency comparison absent from its closed Memory episode"
            )

    return {
        "archived_causal_owner_state_canonical": True,
        "closed_memory_episodes_scanned": len(closed),
        "claimed_closed_memory_sources_checked": len(claimed_episodes),
        "published_agency_comparisons_checked": len(agency_claims),
        "closed_episode_membership_structurally_verified": True,
        "memory_runtime_attested": False,
        "physical_truth_attested": False,
    }
