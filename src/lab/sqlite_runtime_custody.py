"""Non-publishing inventory of the mortal runtime's *registered* owners.

M-11 preparation only. This code does not create live state, cold-restore
owners, publish physics, run a command or replace the one Action Control
dispatcher. Runtime-local fields not registered as causal owners remain an
explicit integration blocker, not a presumed part of this state image.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Sequence

from .determinism import canonical_causal_bytes, sha256_hex
from .mortal_execution import MortalStatus
from .sqlite_current_envelope import (
    REGISTERED_CURRENT_SCHEMA, registered_current_metadata,
)


def capture_registered_current_state(
    runtime: object, *, individual_id: str,
    expected_owner_ids: Sequence[str] | None = None,
) -> dict[str, object]:
    """Read a quiescent, terminal-safe, one-generation owner graph.

    Only autonomous mortal instances without an open attempt qualify. No
    temporary owner/WorldBody state is ever restored. The separate caller
    must still prove that all mutable runtime fields have been registered
    before using this for a live M-11 transaction.
    """
    substrate = runtime.stage3.substrate  # type: ignore[attr-defined]
    boundary = substrate._mortal_boundary
    world = runtime.world  # type: ignore[attr-defined]
    scheduler = runtime.scheduler  # type: ignore[attr-defined]
    journal = runtime.journal  # type: ignore[attr-defined]
    if (
        boundary is None
        or substrate.mortal_status not in (MortalStatus.ACTIVE, MortalStatus.DEAD)
        or substrate.bench is not None
        or substrate.evaluation_trace is not None
        or getattr(substrate.safety, "blocked", False)
        or scheduler.active_attempt is not None
        or not world._historical_restore_forbidden
        or world._mortal_dispatch_key is None
        or world._mortal_dispatch_active
        or boundary._world is not world
        or boundary.last_world_step != scheduler.t_monde
    ):
        raise RuntimeError("registered custody requires a quiescent autonomous mortal generation")
    if type(individual_id) is not str or not individual_id:
        raise ValueError("current generation requires an explicit individual identity")
    if not journal.verify():
        raise RuntimeError("causal journal failed verification before owner capture")

    declared = tuple(runtime.causal_owners)  # type: ignore[attr-defined]
    identities = [owner.owner_id for owner in declared]
    if (
        len(identities) != len(set(identities))
        or len(identities) < 3
        or sum(owner is world for owner in declared) != 1
        or sum(owner is scheduler for owner in declared) != 1
    ):
        raise ValueError("registered owner roster is incomplete, duplicated or aliased")
    roster = tuple(sorted(identities))
    if expected_owner_ids is not None and roster != tuple(expected_owner_ids):
        raise ValueError("registered causal owner roster changed within one identity")

    states: dict[str, object] = {}
    for owner in declared:
        if not callable(getattr(owner, "export_causal_state", None)):
            raise ValueError("registered owner lacks causal state export")
        # Detached ownership: a later producer mutation cannot rewrite this
        # already captured state or its digest.
        state = deepcopy(owner.export_causal_state())
        canonical_causal_bytes(state)
        states[owner.owner_id] = state
    envelope = {
        "custody_schema": REGISTERED_CURRENT_SCHEMA,
        "individual_id": individual_id,
        "world": states.pop("world_and_body"),
        "scheduler": states.pop("scheduler.clock"),
        "owners": states,
        "owner_ids": list(roster),
        "owner_roster_hash": sha256_hex(canonical_causal_bytes(list(roster))),
        "rng_owner_ids": [
            name for name in roster if name.endswith(".random_streams")
        ],
        "lifecycle": boundary.status.value,
        "journal": {
            "count": len(journal.entries), "head": journal.head_hash,
        },
    }
    registered_current_metadata(envelope)
    # Export is observation only. Repeat only the small authoritative
    # physical/clock checks, not arbitrary cognitive hooks.
    if (
        canonical_causal_bytes(world.export_causal_state())
        != canonical_causal_bytes(envelope["world"])
        or canonical_causal_bytes(scheduler.export_causal_state())
        != canonical_causal_bytes(envelope["scheduler"])
    ):
        raise RuntimeError("world or scheduler changed during non-publishing capture")
    return envelope
