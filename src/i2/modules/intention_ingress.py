"""Research-only boundary for an I2 semantic-intention prototype.

This module verifies *consistency* of caller-supplied capture and UC receipts.
It cannot establish the truth of a first-person capture or payment on its own:
the injected technical ports MUST be backed by an independently authenticated
observation owner and real UC ledger before any living-engine integration.

The only state transition it can invoke is IntentionContinuity.open/observe.
No command, Option, winner, safety label or motor-control API exists here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
import json
from typing import Protocol

from .intention_continuity import (
    FirstPersonCapture, IntentionContinuity, IntentionTransition, _ref,
)

INTAKE_SCHEMA = "i2-intention-intake-claim-v1"
INTAKE_OPERATION = "i2_intention_consider"
INTAKE_UC = 1  # proposed software contract, not scientific calibration


def _refs(value: object, name: str) -> tuple[str, ...]:
    if (type(value) is not tuple or not 1 <= len(value) <= 64
            or value != tuple(sorted(set(value)))):
        raise ValueError(f"invalid canonical {name}")
    for item in value:
        _ref(item, name)
    return value


@dataclass(frozen=True, slots=True)
class ObservationClaim:
    """Technical claim to be checked by an independent, trusted source port."""

    life_ref: str
    capture: FirstPersonCapture
    source_event_ref: str
    subjective_evidence_refs: tuple[str, ...]

    def validate(self) -> None:
        _ref(self.life_ref, "life ref")
        if type(self.capture) is not FirstPersonCapture:
            raise ValueError("expected first-person capture projection")
        self.capture.validate()
        _ref(self.source_event_ref, "observation source ref")
        _refs(self.subjective_evidence_refs, "subjective evidence refs")

    def digest(self) -> str:
        """Canonical content binding, NOT a signature or authenticity proof."""
        self.validate()
        c = self.capture
        payload = {
            "schema": INTAKE_SCHEMA, "life_ref": self.life_ref,
            "source_event_ref": self.source_event_ref,
            "subjective_evidence_refs": list(self.subjective_evidence_refs),
            "capture": {
                "step": c.step, "ref": c.ref, "goal_ref": c.goal_ref,
                "accessible_semantics": list(c.accessible_semantics),
                "contradicted_semantics": list(c.contradicted_semantics),
            },
        }
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
        return sha256(data).hexdigest()


@dataclass(frozen=True, slots=True)
class UCReceipt:
    """Technical receipt. It is authentic only when returned by a trusted port."""

    ref: str
    life_ref: str
    capture_ref: str
    claim_digest: str
    operation: str
    units: int

    def validate(self) -> None:
        _ref(self.ref, "UC receipt ref")
        _ref(self.life_ref, "UC life ref")
        _ref(self.capture_ref, "UC capture ref")
        if (type(self.claim_digest) is not str or len(self.claim_digest) != 64
                or any(ch not in "0123456789abcdef" for ch in self.claim_digest)):
            raise ValueError("invalid UC claim digest")
        if self.operation != INTAKE_OPERATION or type(self.units) is not int or self.units != INTAKE_UC:
            raise ValueError("UC receipt operation/cost mismatch")


class ObservationAuthority(Protocol):
    def verify(self, *, life_ref: str, claim: ObservationClaim,
               digest: str) -> bool: ...


class UCLedgerAuthority(Protocol):
    def debit(self, *, life_ref: str, capture_ref: str, claim_digest: str,
              operation: str, units: int) -> UCReceipt | None: ...


class IntentionIngress:
    """One-life, source-only integration seam with strict fail-closed ports.

    The source authority must bind a *real* committed first-person projection
    to the individual before any cognitive debit. The UC ledger must perform
    an actual debit and return its own receipt before owner state is accessed.
    These authorities are injected, NOT implemented by I2 at this stage.

    In particular a digest, a mock port or a claimed receipt is never M11
    authentication. There is no crash-recovery or mortal-life runtime here.
    """

    def __init__(self, *, life_ref: str, observation_authority: ObservationAuthority,
                 uc_authority: UCLedgerAuthority) -> None:
        self.life_ref = _ref(life_ref, "session life ref")
        if observation_authority is None or uc_authority is None:
            raise ValueError("independent observation and UC authorities required")
        if not callable(getattr(observation_authority, "verify", None)):
            raise ValueError("observation authority port absent")
        if not callable(getattr(uc_authority, "debit", None)):
            raise ValueError("UC debit authority port absent")
        self._source = observation_authority
        self._budget = uc_authority
        self._owner = IntentionContinuity()
        self._seen_captures: set[str] = set()
        self._used_receipts: set[str] = set()
        self._last_step = -1
        # Serialize ingress through owner mutation: concurrent calls cannot
        # both spend UC for the same capture.
        self._lock = Lock()

    @property
    def current(self):
        """Read-only semantic state. Not a motor candidate or command."""
        with self._lock:
            return self._owner.current

    def _admit(self, claim: ObservationClaim, *, evidence_ref: str | None) -> UCReceipt:
        if type(claim) is not ObservationClaim:
            raise ValueError("observation claim required")
        claim.validate()
        if claim.life_ref != self.life_ref:
            raise ValueError("foreign life observation")
        if claim.capture.step <= self._last_step or claim.capture.ref in self._seen_captures:
            raise ValueError("stale or reused capture")
        if evidence_ref is not None:
            _ref(evidence_ref, "origin evidence")
            if evidence_ref not in claim.subjective_evidence_refs:
                raise ValueError("intention evidence absent from subjective capture")
        digest = claim.digest()
        verified = self._source.verify(life_ref=self.life_ref, claim=claim,
                                       digest=digest)
        if verified is not True:
            raise ValueError("capture provenance not authenticated by source port")
        # Reserve before calling a potentially non-idempotent external debit.
        # Timeouts, malformed receipts and lost acknowledgements cannot
        # trigger a second charge for this capture in the current session.
        # This is only an ephemeral guard, NOT durable M11 idempotency.
        self._last_step = claim.capture.step
        self._seen_captures.add(claim.capture.ref)
        # The real UC debit must occur before consulting IntentionContinuity.
        ticket = self._budget.debit(life_ref=self.life_ref,
            capture_ref=claim.capture.ref, claim_digest=digest,
            operation=INTAKE_OPERATION, units=INTAKE_UC)
        if type(ticket) is not UCReceipt:
            raise ValueError("UC not paid or receipt missing")
        ticket.validate()
        if (ticket.life_ref != self.life_ref or ticket.capture_ref != claim.capture.ref
                or ticket.claim_digest != digest or ticket.ref in self._used_receipts):
            raise ValueError("UC receipt is foreign, stale, duplicated or unbound")
        # An external debit may have occurred even if the policy rejects the
        # cognitive attempt. Record the claimed receipt to forbid its reuse.
        self._used_receipts.add(ticket.ref)
        return ticket

    def open(self, *, claim: ObservationClaim, semantic_ref: str,
             evidence_ref: str, ttl_steps: int) -> IntentionTransition:
        # Syntactic preflight without reading cognitive state or spending UC.
        _ref(semantic_ref, "intended semantic ref")
        _ref(evidence_ref, "origin evidence ref")
        if type(ttl_steps) is not int or not 1 <= ttl_steps <= 64:
            raise ValueError("bounded intention TTL required")
        with self._lock:
            ticket = self._admit(claim, evidence_ref=evidence_ref)
            return self._owner.open(
                capture=claim.capture, semantic_ref=semantic_ref,
                evidence_ref=evidence_ref, ttl_steps=ttl_steps,
                work_ref=ticket.ref,
            )

    def observe(self, *, claim: ObservationClaim) -> IntentionTransition:
        with self._lock:
            ticket = self._admit(claim, evidence_ref=None)
            return self._owner.observe(capture=claim.capture, work_ref=ticket.ref)

    def inspect_proposal_state(self) -> dict[str, object]:
        """Unsigned local owner view, NEVER a durable M11 recovery checkpoint."""
        with self._lock:
            return self._owner.export_state()