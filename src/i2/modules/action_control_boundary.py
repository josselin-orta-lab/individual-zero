"""Inert I2 Action Control boundary: independent safety review, never admission.

No motor command, world effect, birth or M11 owner can be obtained from this
module. Current-capture authenticity, living status, UC and veto evidence are
external authority *requirements*, not implementations. Test doubles supply
them in isolated tests; no real life may consume this preview as permission.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Protocol

from .competition_preview import (
    CompetitionAdvice, SubjectiveValuation, _frame, _digest,
)
from .intention_continuity import _ref
from .option_reconstruction import CandidateFrame

CONTROL_OPERATION = "i2_action_control_review"
CONTROL_UC = 1  # interface proposal, NOT Scheduler pricing
_PROPOSED_STATUSES = frozenset({"ADVISORY_ONLY", "AMBIGUOUS", "NO_POSITIVE_EVIDENCE",
                                "UNFUNDED", "NO_CANDIDATES"})


@dataclass(frozen=True, slots=True)
class ControlReceipt:
    """External-debit claim, accepted only when returned by a trusted ledger."""

    ref: str
    life_ref: str
    frame_ref: str
    capture_ref: str
    claim_digest: str
    candidate_ref: str
    operation: str
    units: int

    def validate(self) -> None:
        for name in ("ref", "life_ref", "frame_ref", "capture_ref", "candidate_ref"):
            _ref(getattr(self, name), name)
        _digest(self.claim_digest)
        if self.operation != CONTROL_OPERATION or type(self.units) is not int or self.units != CONTROL_UC:
            raise ValueError("invalid control review receipt operation or cost")


@dataclass(frozen=True, slots=True)
class SafetyFinding:
    """A source-reported veto. It is NOT a motor capability or grant."""

    life_ref: str
    frame_ref: str
    capture_ref: str
    candidate_ref: str
    control_receipt_ref: str
    veto: bool
    evidence_ref: str

    def validate(self) -> None:
        for name in ("life_ref", "frame_ref", "capture_ref", "candidate_ref",
                     "control_receipt_ref", "evidence_ref"):
            _ref(getattr(self, name), name)
        if type(self.veto) is not bool:
            raise ValueError("safety veto must be a real boolean")


@dataclass(frozen=True, slots=True)
class ControlReview:
    """Read-only outcome. Even a cleared veto NEVER authorizes action."""

    frame_ref: str
    capture_ref: str
    physical_step: int
    status: str
    suggested_candidate_ref: str | None
    control_receipt_ref: str | None
    safety_evidence_ref: str | None
    motor_authority: str = "NONE"


class CurrentCaptureAuthority(Protocol):
    """Must attest active life, CURRENT capture and committed source/UC chain."""

    def verify_current(self, *, life_ref: str, frame: CandidateFrame,
                       advice: CompetitionAdvice) -> bool: ...


class ControlUCLedger(Protocol):
    """Must charge an actual UC before safety review, transactionally."""

    def debit(self, *, life_ref: str, frame_ref: str, capture_ref: str,
              claim_digest: str, candidate_ref: str, operation: str,
              units: int) -> ControlReceipt | None: ...


class IndependentSafetyAuthority(Protocol):
    """Must recheck current affordance, physical constraints and veto."""

    def check(self, *, life_ref: str, frame: CandidateFrame,
              candidate_ref: str, control_receipt_ref: str) -> SafetyFinding: ...


def _consistent_advice(frame: CandidateFrame, advice: object) -> CompetitionAdvice:
    """Reject forged/incomplete *shapes*; this is NOT M11 authentication."""
    _frame(frame)
    if type(advice) is not CompetitionAdvice:
        raise ValueError("exact CompetitionAdvice required")
    if (advice.frame_ref != frame.frame_ref or advice.capture_ref != frame.capture_ref
            or type(advice.physical_step) is not int
            or advice.physical_step != frame.physical_step
            or type(advice.status) is not str
            or advice.status not in _PROPOSED_STATUSES):
        raise ValueError("advice belongs to another or invalid frame")
    names = tuple(item.candidate_ref for item in frame.candidates)
    if (type(advice.evaluated_candidate_refs) is not tuple
            or type(advice.receipt_refs) is not tuple
            or type(advice.valuation_records) is not tuple):
        raise ValueError("noncanonical advice collections")
    if advice.status in ("NO_CANDIDATES", "UNFUNDED"):
        if (advice.status == "NO_CANDIDATES") != (len(names) == 0):
            raise ValueError("unfunded/empty mismatch")
        if (advice.suggested_candidate_ref is not None or advice.evaluated_candidate_refs
                or advice.receipt_refs or advice.valuation_records):
            raise ValueError("unpaid advice has a suggested or evaluated candidate")
        return advice
    if (not names or advice.evaluated_candidate_refs != names
            or len(advice.receipt_refs) != len(names)
            or len(advice.valuation_records) != len(names)):
        raise ValueError("partial Competition evaluation cannot be admitted")
    paid_refs: set[str] = set()
    for name, receipt, valuation in zip(names, advice.receipt_refs, advice.valuation_records):
        _ref(receipt, "competition receipt reference")
        if receipt in paid_refs:
            raise ValueError("duplicate Competition receipt")
        paid_refs.add(receipt)
        if type(valuation) is not SubjectiveValuation:
            raise ValueError("invalid subjective valuation")
        valuation.validate()
        if valuation.candidate_ref != name or valuation.receipt_ref != receipt:
            raise ValueError("valuation is not bound to paid candidate")
    best = max(item.value for item in advice.valuation_records)
    leaders = [item.candidate_ref for item in advice.valuation_records if item.value == best]
    expected_status = ("NO_POSITIVE_EVIDENCE" if best <= 0 else
                       "AMBIGUOUS" if len(leaders) > 1 else "ADVISORY_ONLY")
    expected_candidate = leaders[0] if expected_status == "ADVISORY_ONLY" else None
    if advice.status != expected_status or advice.suggested_candidate_ref != expected_candidate:
        raise ValueError("Competition winner/status not justified by complete paid valuations")
    return advice


class ActionControlBoundary:
    """A one-life NON-MOTOR safety-review boundary, with ephemeral replay guards.

    Ports MUST be connected to authenticated authorities before any living
    engine. This module cannot perform a physical action or create admission.
    Anti-replay sets are in-memory only: they do NOT survive an M11 restart.
    """

    def __init__(self, *, life_ref: str, current_authority: CurrentCaptureAuthority,
                 ledger: ControlUCLedger, safety_authority: IndependentSafetyAuthority) -> None:
        self.life_ref = _ref(life_ref, "control life")
        if not callable(getattr(current_authority, "verify_current", None)):
            raise ValueError("independent current-capture authority is mandatory")
        if not callable(getattr(ledger, "debit", None)):
            raise ValueError("independent UC ledger is mandatory")
        if not callable(getattr(safety_authority, "check", None)):
            raise ValueError("independent safety/veto authority is mandatory")
        self._current = current_authority
        self._ledger = ledger
        self._safety = safety_authority
        self._lock = Lock()
        self._last_step = -1
        self._captures: set[str] = set()
        self._frames: set[str] = set()
        self._receipts: set[str] = set()

    def review(self, *, frame: CandidateFrame, advice: CompetitionAdvice) -> ControlReview:
        _consistent_advice(frame, advice)
        if frame.life_ref != self.life_ref:
            raise ValueError("foreign life")
        # Only the *independent* authority may assert current committed M11,
        # actual paid Competition and living-state freshness. None exists here.
        if self._current.verify_current(life_ref=self.life_ref, frame=frame, advice=advice) is not True:
            raise ValueError("current physical state or provenance not attested")
        with self._lock:
            if (frame.physical_step <= self._last_step or frame.capture_ref in self._captures
                    or frame.frame_ref in self._frames):
                raise ValueError("stale or replayed current-state review")
            self._last_step = frame.physical_step
            self._captures.add(frame.capture_ref)
            self._frames.add(frame.frame_ref)
        ref = advice.suggested_candidate_ref
        if ref is None:
            return ControlReview(frame.frame_ref, frame.capture_ref, frame.physical_step,
                                 "NO_ADVICE", None, None, None)
        # Only candidates fully evaluated by Competition may reach this point.
        receipt = self._ledger.debit(
            life_ref=self.life_ref, frame_ref=frame.frame_ref,
            capture_ref=frame.capture_ref, claim_digest=frame.claim_digest,
            candidate_ref=ref, operation=CONTROL_OPERATION, units=CONTROL_UC)
        if receipt is None:
            return ControlReview(frame.frame_ref, frame.capture_ref, frame.physical_step,
                                 "UNFUNDED", None, None, None)
        if type(receipt) is not ControlReceipt:
            raise ValueError("invalid control receipt type")
        receipt.validate()
        if (receipt.life_ref != self.life_ref or receipt.frame_ref != frame.frame_ref
                or receipt.capture_ref != frame.capture_ref or receipt.claim_digest != frame.claim_digest
                or receipt.candidate_ref != ref):
            raise ValueError("control receipt is not bound to current candidate")
        with self._lock:
            if receipt.ref in self._receipts:
                raise ValueError("control receipt reused")
            self._receipts.add(receipt.ref)
        finding = self._safety.check(life_ref=self.life_ref, frame=frame,
                                     candidate_ref=ref, control_receipt_ref=receipt.ref)
        if type(finding) is not SafetyFinding:
            raise ValueError("independent veto finding missing")
        finding.validate()
        if (finding.life_ref != self.life_ref or finding.frame_ref != frame.frame_ref
                or finding.capture_ref != frame.capture_ref or finding.candidate_ref != ref
                or finding.control_receipt_ref != receipt.ref):
            raise ValueError("veto finding belongs to another physical context")
        return ControlReview(
            frame.frame_ref, frame.capture_ref, frame.physical_step,
            "VETOED" if finding.veto else "REVIEWED_NOT_ADMITTED",
            None if finding.veto else ref, receipt.ref, finding.evidence_ref)
