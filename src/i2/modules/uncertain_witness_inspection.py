"""Read-only correlation of two *synthetic* I2 inspections, not M11.

No physical effect, signer, Scheduler, birth, recovery or motor path exists.
The external port is an unimplemented trust requirement. Even agreement of
two reports cannot prove that the provider is independent or up to date.
"""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Callable

from .cognitive_cycle_fixture import CognitiveCycleFixture, UncertainCommitInspection
from .intention_ingress import ObservationClaim
from .lifecycle_external_witness import (
    IndependentWitness, LatestWitness, LIFECYCLE_SCHEMA, WitnessAudit, WitnessRefusal,
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
             local_probe: Callable[[], UncertainCommitInspection],
             minimum_witness: LatestWitness | None = None,
             ) -> UncertainWitnessInspection:
    if (type(fixture) is not CognitiveCycleFixture or
            fixture.schema != LIFECYCLE_SCHEMA):
        raise ValueError("exact inert v5 fixture required")

    # Three separate local read transactions. This checks detected changes
    # between reads but cannot lock out subsequent writes or global rollback.
    before = fixture.audit()
    try:
        local = local_probe()
    except (OSError, RuntimeError, sqlite3.DatabaseError) as exc:
        # A failed second read has no usable single-snapshot proof.
        # Never contact the external provider or infer an absent COMMIT.
        raise WitnessRefusal(
            "UNKNOWN", "local uncertain-commit inspection unavailable"
        ) from exc
    if (type(local) is not UncertainCommitInspection or
            local.observed_committed != before["committed"] or
            local.observed_head != before["chain_head"]):
        raise WitnessRefusal(
            "UNKNOWN", "local synthetic journal moved between audit and attempt inspection"
        )
    if minimum_witness is not None:
        if type(minimum_witness) is not LatestWitness:
            raise ValueError("exact pinned witness required")
        minimum_witness.validate()
        if (minimum_witness.life_ref != before["life_ref"] or
                minimum_witness.genesis_ref != before["genesis_ref"]):
            raise ValueError("foreign pinned witness")
        prefix = local.audited_prefix
        if prefix is None or prefix.requested_seq != minimum_witness.committed:
            raise WitnessRefusal("UNKNOWN", "missing same-snapshot pinned prefix")
        if (prefix.observed_head != before["chain_head"] or
                prefix.observed_committed != before["committed"]):
            raise WitnessRefusal("UNKNOWN", "local journal moved during prefix inspection")
        if prefix.prefix_head is None:
            raise WitnessRefusal("STALE", "local history shorter than pinned witness")
        if (prefix.prefix_head != minimum_witness.chain_head or
                prefix.prefix_step != minimum_witness.last_step or
                prefix.prefix_terminal_ref != minimum_witness.terminal_ref or
                (minimum_witness.terminal_ref is not None and
                 prefix.observed_committed > minimum_witness.committed)):
            raise WitnessRefusal("FORK", "local attempt does not descend from pinned witness")
    if local.outcome == "CONFLICT_LOCAL":
        # A wrong attempt or predecessor is not an external-head mismatch.
        # Refuse before even consulting an untrusted provider.
        raise WitnessRefusal("UNKNOWN", "attempt conflicts with audited local predecessor")
    if local.outcome not in {"RECORDED_LOCAL_ONLY", "ABSENT_LOCAL_ONLY"}:
        raise WitnessRefusal("UNKNOWN", "unknown local attempt inspection result")

    try:
        corroboration = compare_audit(report=before, witness=witness,
                                      minimum_witness=minimum_witness)
    finally:
        # Run this even when the remote provider fails/refuses. A concurrent
        # local COMMIT must not be mislabeled as a stable STALE/UNANCHORED.
        try:
            after = fixture.audit()
        except Exception as exc:
            raise WitnessRefusal(
                "UNKNOWN", "local journal unavailable after uncertain witness inspection"
            ) from exc
        if after != before:
            raise WitnessRefusal(
                "UNKNOWN", "local synthetic journal moved during external inspection"
            )
    return UncertainWitnessInspection(local=local, witness=corroboration)


def inspect_uncertain_cognition_with_witness(
    *, fixture: object, witness: IndependentWitness,
    previous_count: int, previous_head: str, claim: ObservationClaim,
    minimum_witness: LatestWitness | None = None,
) -> UncertainWitnessInspection:
    """Inspect a possibly committed claimed capture. Never dispatch or retry."""
    if type(fixture) is not CognitiveCycleFixture:
        raise ValueError("exact inert v5 fixture required")
    return _inspect(
        fixture=fixture, witness=witness, minimum_witness=minimum_witness,
        local_probe=lambda: fixture.inspect_uncertain_cognition(
            previous_count=previous_count, previous_head=previous_head, claim=claim,
            minimum_sequence=(None if minimum_witness is None else minimum_witness.committed),
        ),
    )


def inspect_uncertain_terminal_with_witness(
    *, fixture: object, witness: IndependentWitness,
    previous_count: int, previous_head: str,
    physical_step: int, terminal_ref: str, evidence_ref: str,
    minimum_witness: LatestWitness | None = None,
) -> UncertainWitnessInspection:
    """Inspect a synthetic terminal claim; never infer real death or rebirth."""
    if type(fixture) is not CognitiveCycleFixture:
        raise ValueError("exact inert v5 fixture required")
    return _inspect(
        fixture=fixture, witness=witness, minimum_witness=minimum_witness,
        local_probe=lambda: fixture.inspect_uncertain_terminal(
            previous_count=previous_count, previous_head=previous_head,
            physical_step=physical_step, terminal_ref=terminal_ref,
            evidence_ref=evidence_ref,
            minimum_sequence=(None if minimum_witness is None else minimum_witness.committed),
        ),
    )
