"""Replay-gate admission receipts: full WorldSpec binding (ADR-0017/0019).

These are structural custody checks rather than a Python security sandbox.
The laboratory guard is the supported source of tickets.
"""
from __future__ import annotations

from dataclasses import dataclass
from i3.modules.world import WorldSpec
from i3.runtime.provenance import digest, world_snapshot

_MINT = object()
SCIENTIFIC_COHORTS = ("development", "selection", "validation", "reserve")
COHORTS = ("engineering",) + SCIENTIFIC_COHORTS


def world_sha256(spec: WorldSpec) -> str:
    return digest(world_snapshot(spec))


@dataclass(frozen=True)
class AdmissionTicket:
    cohort: str
    family: str
    index: int
    world_seed: int
    world_name: str
    world_sha256: str
    transport_fingerprint: str
    _mint: object

    def receipt(self) -> dict:
        return {"cohort": self.cohort, "family": self.family,
                "index": self.index, "world_seed": self.world_seed,
                "world_name": self.world_name, "world_sha256": self.world_sha256,
                "transport_fingerprint": self.transport_fingerprint}


def mint(*, cohort, family, index, world_seed, spec: WorldSpec,
         transport_fingerprint):
    """Called only by the laboratory guard after cohort admission."""
    if cohort not in COHORTS:
        raise ValueError("unknown cohort")
    if not isinstance(spec, WorldSpec):
        raise TypeError("admission requires WorldSpec")
    return AdmissionTicket(cohort, family, index, world_seed, spec.name,
                           world_sha256(spec), transport_fingerprint, _MINT)


def verify(ticket, spec: WorldSpec) -> dict:
    """Reject a different WorldSpec even when the name is unchanged."""
    if not isinstance(ticket, AdmissionTicket) or ticket._mint is not _MINT:
        raise PermissionError("replay-gate life requires a guard-minted admission ticket")
    if not isinstance(spec, WorldSpec):
        raise TypeError("admission verification requires WorldSpec")
    if ticket.world_name != spec.name or ticket.world_sha256 != world_sha256(spec):
        raise PermissionError("admission ticket is bound to a different WorldSpec")
    return ticket.receipt()
