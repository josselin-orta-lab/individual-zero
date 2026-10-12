"""Pure, read-only schema checks for opt-in registered runtime state custody.

The SQLite auditor can import this module without importing WorldBody, I0,
Oracle, Bench or a cognitive runtime. The envelope is deliberately a *roster*
contract, not a claim that every transient runtime field is restorable.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from unicodedata import normalize

from .determinism import canonical_causal_bytes, sha256_hex


REGISTERED_CURRENT_SCHEMA = "i0-registered-current-state-v1"
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_STATUSES = frozenset({
    "active", "dead", "technical_halt", "safety_block", "experiment_stopped",
})
_PHYSICAL_OWNERS = frozenset({"world_and_body", "scheduler.clock"})


def registered_current_metadata(state: Mapping[str, object]) -> tuple[str, str, int, str, str] | None:
    """Return (roster SHA, status, count, head, identity) for a strict envelope.

    Legacy phase-one toy states remain distinguishable (return None). An
    envelope that declares this contract is never silently treated as legacy.
    The DB pins the roster across successive committed generations.
    """
    if "custody_schema" not in state:
        return None
    if state.get("custody_schema") != REGISTERED_CURRENT_SCHEMA:
        raise ValueError("unsupported current runtime custody schema")
    identity = state.get("individual_id")
    owner_ids = state.get("owner_ids")
    owners = state.get("owners")
    roster_hash = state.get("owner_roster_hash")
    rng_ids = state.get("rng_owner_ids")
    journal = state.get("journal")
    status = state.get("lifecycle")
    world = state.get("world")
    scheduler = state.get("scheduler")
    if (
        type(identity) is not str or not identity
        or normalize("NFC", identity) != identity
        or type(owner_ids) is not list or not owner_ids
        or not isinstance(owners, Mapping) or not owners
        or not isinstance(world, Mapping)
        or not isinstance(scheduler, Mapping)
        or type(rng_ids) is not list
        or not isinstance(journal, Mapping)
        or status not in _STATUSES
        or type(roster_hash) is not str or not _HEX.fullmatch(roster_hash)
    ):
        raise ValueError("invalid registered current-state envelope")
    if any(
        type(owner_id) is not str or not owner_id
        or normalize("NFC", owner_id) != owner_id
        for owner_id in owner_ids
    ):
        raise ValueError("invalid registered causal owner identity")
    if (
        owner_ids != sorted(set(owner_ids))
        or set(owner_ids) != set(owners) | _PHYSICAL_OWNERS
        or _PHYSICAL_OWNERS.intersection(owners)
    ):
        raise ValueError("missing, duplicated or unexpected registered causal owners")
    if rng_ids != sorted(owner_id for owner_id in owner_ids if owner_id.endswith(".random_streams")):
        raise ValueError("registered RNG owner is omitted or falsely declared")
    if sha256_hex(canonical_causal_bytes(owner_ids)) != roster_hash:
        raise ValueError("registered causal owner roster digest mismatch")
    count, head = journal.get("count"), journal.get("head")
    if (
        type(count) is not int or count < 0
        or type(head) is not str or not _HEX.fullmatch(head)
        or type(scheduler.get("t_monde")) is not int
        or scheduler["t_monde"] < 0
        or scheduler.get("active_attempt") is not None
    ):
        raise ValueError("registered current-state journal or clock is invalid")
    return roster_hash, status, count, head, identity
