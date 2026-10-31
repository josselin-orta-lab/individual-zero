"""Read-only external-head comparison for I2 synthetic lifecycle *audits*.

This is not M11 attestation, a signature validator, a birth registry, or a
permission to resume an individual. A future independent witness MUST
atomically return its latest monotonic record and verify its provenance.
The synthetic test witness is NOT such an authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

WITNESS_SCHEMA = "i2-lifecycle-external-witness-proposal-v2"
from .cognitive_cycle_fixture import SCHEMA as LIFECYCLE_SCHEMA
ZERO_HASH = "0" * 64
_HEX = frozenset("0123456789abcdef")


def _ref(value: object, field: str) -> str:
    if (type(value) is not str or not 1 <= len(value) <= 256
            or any(c.isspace() or not c.isprintable() for c in value)):
        raise ValueError(f"invalid {field}")
    return value


def _head(value: object) -> str:
    if type(value) is not str or len(value) != 64 or not set(value) <= _HEX:
        raise ValueError("invalid chain head")
    return value


@dataclass(frozen=True, slots=True)
class LatestWitness:
    """Latest witness claim. Trust requires an independent verifying port."""

    witness_schema: str
    life_ref: str
    genesis_ref: str
    journal_schema: str
    committed: int
    last_step: int
    chain_head: str
    terminal_ref: str | None
    terminal_step: int | None
    proof_ref: str

    def validate(self) -> None:
        if self.witness_schema != WITNESS_SCHEMA:
            raise ValueError("unknown external witness protocol")
        _ref(self.life_ref, "witness life")
        _ref(self.genesis_ref, "witness genesis")
        _ref(self.proof_ref, "external witness proof")
        if self.journal_schema != LIFECYCLE_SCHEMA:
            raise ValueError("witness is not for unified synthetic lifecycle")
        if (type(self.committed) is not int or self.committed < 0 or
                type(self.last_step) is not int or self.last_step < -1):
            raise ValueError("invalid witness sequence")
        _head(self.chain_head)
        if self.committed == 0:
            if self.last_step != -1 or self.chain_head != ZERO_HASH:
                raise ValueError("invalid genesis-only checkpoint")
        elif self.last_step < 0 or self.chain_head == ZERO_HASH:
            raise ValueError("invalid committed witness head")
        if (self.terminal_ref is None) != (self.terminal_step is None):
            raise ValueError("incomplete terminal witness")
        if self.terminal_ref is not None:
            if not self.terminal_ref.startswith("terminal:"):
                raise ValueError("terminal reference has wrong domain")
            _ref(self.terminal_ref, "terminal ref")
            if (type(self.terminal_step) is not int or self.terminal_step < 0 or
                    self.terminal_step != self.last_step or self.committed == 0):
                raise ValueError("invalid terminal witness chronology")


class IndependentWitness(Protocol):
    """A SINGLE linearizable latest-head read and verification operation.

    The independently operated provider MUST select its freshest monotone
    revision and validate issuer, signature, revocation, freshness and
    anti-equivocation against that SAME revision before returning. A static
    signed receipt or a separate read_latest/verify_latest pair is unsafe:
    a head can change between the two calls. On any doubt it MUST raise.
    This interface has no provider implementation or trusted signer in I2.
    """

    def read_verified_latest(self, *, life_ref: str,
                             genesis_ref: str) -> LatestWitness: ...


@dataclass(frozen=True, slots=True)
class WitnessAudit:
    """Corroborated static inspection ONLY; never an M11 recovery token."""

    status: str
    life_ref: str
    genesis_ref: str
    committed: int
    chain_head: str
    terminal_ref: str | None
    proof_ref: str
    motor_authority: str = "NONE"
    resumption_authorized: bool = False
    m11_authenticated: bool = False



class WitnessRefusal(ValueError):
    """A *read-only* witness comparison failed closed.

    reason is a stable diagnostic category, not a recovery hint or an
    authorization. An unavailable/invalid proof is UNKNOWN; conflicting
    sequence/head/terminal claims do not select a winning life.
    """

    def __init__(self, reason: str, message: str) -> None:
        if reason not in {"UNKNOWN", "STALE", "FORK", "UNANCHORED"}:
            raise ValueError("unsupported witness refusal category")
        self.reason = reason
        super().__init__(message)


def compare_audit(*, report: dict[str, object], witness: IndependentWitness) -> WitnessAudit:
    """Compare an already verified v3 report to the independent latest anchor.

    This pure function is useful for protocol tests; callers MUST use
    verify_fixture() to ensure the report came from a cold local audit.
    Returns no run/dispatch/admit capability even on an exact match.
    """
    if type(report) is not dict:
        raise ValueError("a v3 audit dict is required")
    if report.get("schema") != LIFECYCLE_SCHEMA:
        raise ValueError("only v3 synthetic lifecycles can be witnessed")
    life = _ref(report.get("life_ref"), "audit life")
    genesis = _ref(report.get("genesis_ref"), "audit genesis")
    if (report.get("motor_authority") != "NONE" or
            report.get("m11_authenticated") is not False or
            report.get("scheduler_uc_authenticated") is not False or
            report.get("physiological_death_attested") is not False):
        raise ValueError("synthetic audit claims unauthorized real authority")
    seq, step = report.get("committed"), report.get("last_step")
    head = _head(report.get("chain_head"))
    if type(seq) is not int or seq < 0 or type(step) is not int or step < -1:
        raise ValueError("invalid local sequence")
    if (seq == 0 and (step != -1 or head != ZERO_HASH)) or (
            seq > 0 and (step < 0 or head == ZERO_HASH)):
        raise ValueError("invalid local genesis/head state")
    terminal = report.get("synthetic_terminal")
    if type(terminal) is not bool:
        raise ValueError("missing exact local terminal bit")
    terminal_ref = report.get("terminal_ref")
    terminal_step = report.get("terminal_step")
    if terminal:
        if (type(terminal_ref) is not str or not terminal_ref.startswith("terminal:")
                or type(terminal_step) is not int or terminal_step != step):
            raise ValueError("inconsistent local terminal seal")
        _ref(terminal_ref, "local terminal ref")
    elif terminal_ref is not None or terminal_step is not None:
        raise ValueError("unsealed local state has terminal fields")
    if isinstance(witness, type) or not callable(
            getattr(witness, "read_verified_latest", None)):
        raise ValueError("independent atomic verified-latest witness is mandatory")

    # One provider call must SELECT and VERIFY the same latest revision.
    # Only a real independent provider can enforce this contract; our
    # in-memory test doubles have no evidentiary standing.
    try:
        record = witness.read_verified_latest(life_ref=life, genesis_ref=genesis)
    except Exception as exc:
        raise WitnessRefusal(
            "UNKNOWN", "independent latest-head attestation unavailable or invalid"
        ) from exc
    if type(record) is not LatestWitness:
        raise WitnessRefusal("UNKNOWN", "no exact external witness record")
    try:
        record.validate()
    except ValueError as exc:
        raise WitnessRefusal("UNKNOWN", str(exc)) from exc
    if record.life_ref != life or record.genesis_ref != genesis:
        raise WitnessRefusal("UNKNOWN", "external witness belongs to another identity")
    if seq < record.committed:
        raise WitnessRefusal("STALE", "stale local copy: external witness has a later head")
    if seq > record.committed:
        raise WitnessRefusal("UNANCHORED", "unanchored local extension: external witness is behind")
    if step != record.last_step or head != record.chain_head:
        raise WitnessRefusal("FORK", "same-sequence local fork or altered head")
    if terminal_ref != record.terminal_ref or terminal_step != record.terminal_step:
        raise WitnessRefusal("FORK", "terminal closure does not match external witness")
    return WitnessAudit(
        status="MATCHED_TERMINAL_INSPECTION" if terminal else "MATCHED_OPEN_INSPECTION",
        life_ref=life, genesis_ref=genesis, committed=seq, chain_head=head,
        terminal_ref=terminal_ref, proof_ref=record.proof_ref,
    )


def verify_fixture(*, fixture: object, witness: IndependentWitness) -> WitnessAudit:
    """Cold audit a real I2 G2 fixture then compare to latest witness.

    This does NOT guard subsequent writes or attest real death. It is not a
    lock on WorldBody, a committed M11 owner or a recovery authorization.
    """
    from .cognitive_cycle_fixture import CognitiveCycleFixture, SCHEMA as CURRENT
    if (CURRENT != LIFECYCLE_SCHEMA or type(fixture) is not CognitiveCycleFixture
            or fixture.schema != LIFECYCLE_SCHEMA):
        raise ValueError("exact I2 synthetic v3 fixture required")
    return compare_audit(report=fixture.audit(), witness=witness)
