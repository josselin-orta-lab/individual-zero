"""Read-only correlation of two *synthetic* I2 inspections, not M11.

No physical effect, signer, Scheduler, birth, recovery or motor path exists.
The external port is an unimplemented trust requirement. Even agreement of
two reports cannot prove that the provider is independent or up to date.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cognitive_cycle_fixture import CognitiveCycleFixture, UncertainCommitInspection
from .intention_ingress import ObservationClaim
from .lifecycle_external_witness import (
    IndependentWitness, LIFECYCLE_SCHEMA, WitnessAudit, WitnessRefusal,
    compare_audit,
)


@dataclass(frozen=True, slots=True)
class UncertainWitnessInspection:
    """Correlated reports, strictly incapable of authorizing continuation."""

    local: UncertainCommitInspection
    witness: WitnessAudit
    motor_authority: str = "NONE"
    retry_authorized: bool = False
    resumption_authorized: bool = False
    m11_authenticated: bool = False


def _inspect(*, fixture: object, witness: IndependentWitness,
             local_probe: Callable[[], UncertainCommitInspection]
             ) -> UncertainWitnessInspection:
    if (type(fixture) is not CognitiveCycleFixture or
            fixture.schema != LIFECYCLE_SCHEMA):
        raise ValueError("exact inert v5 fixture required")

    # Three separate local read transactions. This checks detected changes
    # between reads but cannot lock out subsequent writes or global rollback.
    before = fixture.audit()
    local = local_probe()
    if (type(local) is not UncertainCommitInspection or
            local.observed_committed != before["committed"] or
            local.observed_head != before["chain_head"]):
        raise WitnessRefusal(
            "UNKNOWN", "local synthetic journal moved between audit and attempt inspection"
        )
    if local.outcome == "CONFLICT_LOCAL":
        # A wrong attempt or predecessor is not an external-head mismatch.
        # Refuse before even consulting an untrusted provider.
        raise WitnessRefusal("UNKNOWN", "attempt conflicts with audited local predecessor")
    if local.outcome not in {"RECORDED_LOCAL_ONLY", "ABSENT_LOCAL_ONLY"}:
        raise WitnessRefusal("UNKNOWN", "unknown local attempt inspection result")

    try:
        corroboration = compare_audit(report=before, witness=witness)
    finally:
        # Run this even when the remote provider fails/refuses. A concurrent
        # local COMMIT must not be mislabeled as a stable STALE/UNANCHORED.
        after = fixture.audit()
        if after != before:
            raise WitnessRefusal(
                "UNKNOWN", "local synthetic journal moved during external inspection"
            )
    return UncertainWitnessInspection(local=local, witness=corroboration)


def inspect_uncertain_cognition_with_witness(
    *, fixture: object, witness: IndependentWitness,
    previous_count: int, previous_head: str, claim: ObservationClaim,
) -> UncertainWitnessInspection:
    """Inspect a possibly committed claimed capture. Never dispatch or retry."""
    if type(fixture) is not CognitiveCycleFixture:
        raise ValueError("exact inert v5 fixture required")
    return _inspect(
        fixture=fixture, witness=witness,
        local_probe=lambda: fixture.inspect_uncertain_cognition(
            previous_count=previous_count, previous_head=previous_head, claim=claim,
        ),
    )


def inspect_uncertain_terminal_with_witness(
    *, fixture: object, witness: IndependentWitness,
    previous_count: int, previous_head: str,
    physical_step: int, terminal_ref: str, evidence_ref: str,
) -> UncertainWitnessInspection:
    """Inspect a synthetic terminal claim; never infer real death or rebirth."""
    if type(fixture) is not CognitiveCycleFixture:
        raise ValueError("exact inert v5 fixture required")
    return _inspect(
        fixture=fixture, witness=witness,
        local_probe=lambda: fixture.inspect_uncertain_terminal(
            previous_count=previous_count, previous_head=previous_head,
            physical_step=physical_step, terminal_ref=terminal_ref,
            evidence_ref=evidence_ref,
        ),
    )
