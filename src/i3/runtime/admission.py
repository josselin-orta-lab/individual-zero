"""Admission tickets for replay-gate lives (ADR-0017 / ADR-0019).

A ticket binds one admitted life to one exact World name, one cohort and one
transport fingerprint. Only `i3.lab.stage2_admission.admit` may mint tickets;
`run_life` refuses a replay-gate policy without a ticket bound to the World it
is about to run. This is defense in depth for the fail-closed scientific
admission required before an owner lift; it carries no cognition.
"""
from __future__ import annotations

from dataclasses import dataclass

_MINT = object()
SCIENTIFIC_COHORTS = ("development", "selection", "validation", "reserve")
COHORTS = ("engineering",) + SCIENTIFIC_COHORTS


@dataclass(frozen=True)
class AdmissionTicket:
    cohort: str
    family: str
    index: int
    world_seed: int
    world_name: str
    transport_fingerprint: str
    _mint: object

    def receipt(self) -> dict:
        return {"cohort": self.cohort, "family": self.family, "index": self.index,
                "world_seed": self.world_seed, "world_name": self.world_name,
                "transport_fingerprint": self.transport_fingerprint}


def mint(*, cohort, family, index, world_seed, world_name, transport_fingerprint):
    """Called only by the lab admission guard after its checks."""
    if cohort not in COHORTS:
        raise ValueError("unknown cohort")
    return AdmissionTicket(cohort, family, index, world_seed, world_name,
                           transport_fingerprint, _MINT)


def verify(ticket, spec_name: str) -> dict:
    """Raise unless `ticket` was minted by the guard for exactly this World."""
    if not isinstance(ticket, AdmissionTicket) or ticket._mint is not _MINT:
        raise PermissionError("replay-gate life requires a guard-minted admission ticket")
    if ticket.world_name != spec_name:
        raise PermissionError("admission ticket is bound to a different World")
    return ticket.receipt()
