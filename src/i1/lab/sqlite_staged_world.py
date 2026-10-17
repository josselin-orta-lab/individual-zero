"""Non-publishing WorldBody candidate for the SQLite M-11 transaction seam.

Preparing is not official physical execution. No public physics, mortal
boundary, journal or cognitive owner is modified here. The later integrated
coordinator must commit all versions and receipts before a once-only physical
publication; this module intentionally has NO publish()/restore() shortcut.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .determinism import canonical_causal_bytes, sha256_hex
from .world import Command, TransitionResult, WorldBody, validate_command


@dataclass(frozen=True, slots=True)
class PreparedMortalWorldEffect:
    """Detached private physics receipt. Not permission to dispatch or resume."""

    source_state_hash: str
    proposed_state: object
    proposed_state_hash: str
    transition: TransitionResult

    @property
    def lethal(self) -> bool:
        return self.transition.lethal


def prepare_mortal_world_effect(
    world: WorldBody, command: Command, *, world_step: int,
) -> PreparedMortalWorldEffect:
    """Run the unchanged physics once on a private, detached world candidate.

    The official WorldBody retains both its exact state and its mortal
    dispatch capability. A caller MUST NOT publish this candidate directly:
    the future coordinator must bind it to a verified current-state DB
    transaction and update the public mortal boundary once, after COMMIT.
    """
    if not isinstance(world, WorldBody):
        raise TypeError("real WorldBody required")
    if world._mortal_dispatch_key is None:
        raise ValueError("candidate requires installed mortal dispatch custody")
    if world._mortal_dispatch_active:
        raise RuntimeError("cannot stage during a live physical dispatch")
    world._require_mutable_world()
    validate_command(command)
    if type(world_step) is not int or world_step < 1:
        raise ValueError("positive physical world_step required")
    before = canonical_causal_bytes(world.export_causal_state())
    candidate = deepcopy(world)
    # The copied authority lives solely inside the private candidate.
    # It does not authorize any command on the public WorldBody instance.
    with candidate._admit_mortal_dispatch(candidate._mortal_dispatch_key):
        transition = candidate.apply(command, t_monde=world_step)
    after = candidate.export_causal_state()
    if (
        transition.t_monde != world_step or transition.command != command
        or canonical_causal_bytes(world.export_causal_state()) != before
    ):
        raise RuntimeError("private physical preparation mutated the live world")
    return PreparedMortalWorldEffect(
        source_state_hash=sha256_hex(before),
        proposed_state=deepcopy(after),
        proposed_state_hash=sha256_hex(canonical_causal_bytes(after)),
        transition=transition,
    )
