"""Inert I2 Competition *advice* from an entirely evaluated candidate frame.

No living engine, no built-in value function, no physical action authority.
A caller-provided, independently trusted source must prove both the batch UC
charge and each subjective valuation. Tests use synthetic ports only.

A scarce budget never awards earlier candidates a free advantage: the ledger
must atomically debit the full frame or decline. Any spent/uncertain attempt
consumes the frame within this ephemeral session, forbidding local replays.
The session is NOT durable, authenticated, crash safe or a substitute for M11.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Protocol

from .intention_continuity import _ref
from .option_reconstruction import CandidateFrame, SemanticCandidate, _bound_id

OPERATION = "i2_competition_batch_evaluation"
UC_PER_CANDIDATE = 1  # interface proposal; NOT real Scheduler pricing
MAX_CANDIDATES = 64
MAX_VALUE_MAGNITUDE = 1024  # bounds a synthetic score, NOT a scientific threshold
_HEX = frozenset("0123456789abcdef")


def _digest(value: object) -> str:
    if (type(value) is not str or len(value) != 64
            or not set(value) <= _HEX):
        raise ValueError("invalid claim digest")
    return value


def _frame(frame: object) -> CandidateFrame:
    """Defend against malformed synthetic frames, not against forgery of M11."""
    if type(frame) is not CandidateFrame:
        raise ValueError("exact CandidateFrame required")
    for field in ("frame_ref", "life_ref", "capture_ref", "work_correlation_ref"):
        _ref(getattr(frame, field), field)
    _digest(frame.claim_digest)
    if type(frame.physical_step) is not int or frame.physical_step < 0:
        raise ValueError("physical step must be a nonnegative int")
    if (type(frame.candidates) is not tuple or len(frame.candidates) > MAX_CANDIDATES):
        raise ValueError("bounded canonical candidate tuple required")
    semantics: list[str] = []
    refs: set[str] = set()
    for candidate in frame.candidates:
        if type(candidate) is not SemanticCandidate:
            raise ValueError("exact SemanticCandidate required")
        _ref(candidate.semantic_ref, "semantic candidate")
        _ref(candidate.candidate_ref, "candidate ref")
        if candidate.intention_ref is not None:
            _ref(candidate.intention_ref, "untrusted intention tag")
            if not candidate.intention_ref.startswith("intent:i2:"):
                raise ValueError("foreign intention tag")
        expected = _bound_id("candidate", frame.life_ref, frame.claim_digest,
                             candidate.semantic_ref)
        if candidate.candidate_ref != expected or candidate.candidate_ref in refs:
            raise ValueError("candidate is unbound, forged or duplicated")
        refs.add(candidate.candidate_ref)
        semantics.append(candidate.semantic_ref)
    if semantics != sorted(set(semantics)):
        raise ValueError("noncanonical or duplicated candidate semantics")
    if not frame.frame_ref.startswith("frame:i2:"):
        raise ValueError("foreign frame")
    return frame


@dataclass(frozen=True, slots=True)
class CompetitionReceipt:
    """Reported UC receipt; authentic only through its issuing ledger."""

    ref: str
    life_ref: str
    frame_ref: str
    claim_digest: str
    candidate_ref: str
    operation: str
    units: int

    def validate(self) -> None:
        for field in ("ref", "life_ref", "frame_ref", "candidate_ref"):
            _ref(getattr(self, field), field)
        _digest(self.claim_digest)
        if self.operation != OPERATION or type(self.units) is not int or self.units != UC_PER_CANDIDATE:
            raise ValueError("invalid evaluation receipt charge")


@dataclass(frozen=True, slots=True)
class SubjectiveValuation:
    """Untrusted value signal. Real subjective provenance must be verified by the provider."""

    candidate_ref: str
    receipt_ref: str
    evidence_ref: str
    value: int

    def validate(self) -> None:
        for field in ("candidate_ref", "receipt_ref", "evidence_ref"):
            _ref(getattr(self, field), field)
        if type(self.value) is not int or abs(self.value) > MAX_VALUE_MAGNITUDE:
            raise ValueError("invalid bounded signed valuation")


@dataclass(frozen=True, slots=True)
class CompetitionAdvice:
    """Auditable ranking only. Never an authorization or executable option."""

    frame_ref: str
    capture_ref: str
    physical_step: int
    status: str
    suggested_candidate_ref: str | None
    evaluated_candidate_refs: tuple[str, ...]
    receipt_refs: tuple[str, ...]
    valuation_records: tuple[SubjectiveValuation, ...]
    # Complete evidence is audit data, not motor state; no persistent accumulator.


@dataclass(frozen=True, slots=True)
class VetoPreview:
    """A synthetic veto masks advice; it can never grant action authority."""

    frame_ref: str
    status: str
    suggested_candidate_ref: str | None
    motor_authority: str = "NONE"


class CandidateFrameAuthority(Protocol):
    """MUST authenticate current owner/frame provenance; not implemented here."""

    def verify(self, *, life_ref: str, frame: CandidateFrame) -> bool: ...


class BatchUCLedger(Protocol):
    """MUST debit all candidates atomically or none; NOT implemented here."""

    def debit_batch(self, *, life_ref: str, frame_ref: str, claim_digest: str,
                    candidate_refs: tuple[str, ...], operation: str,
                    units_each: int) -> tuple[CompetitionReceipt, ...] | None: ...


class SubjectiveEvidenceAuthority(Protocol):
    """MUST source each value from lived evidence, not Lab truth; not implemented."""

    def evaluate_batch(self, *, frame: CandidateFrame,
                       receipts: tuple[CompetitionReceipt, ...]) -> tuple[SubjectiveValuation, ...]: ...


class CompetitionPreview:
    """Single-life, in-memory, one full paid batch per capture; not Competition runtime.

    Source, receipts and valuations come from *independent injected* ports;
    none is implemented or authenticated here. The in-memory anti-replay set
    cannot survive a crash/restart.
    """

    def __init__(self, *, life_ref: str, frame_authority: CandidateFrameAuthority,
                 ledger: BatchUCLedger, evidence: SubjectiveEvidenceAuthority) -> None:
        self.life_ref = _ref(life_ref, "competition life")
        if not callable(getattr(frame_authority, "verify", None)):
            raise ValueError("independent current-frame source required")
        if not callable(getattr(ledger, "debit_batch", None)):
            raise ValueError("batch UC ledger required")
        if not callable(getattr(evidence, "evaluate_batch", None)):
            raise ValueError("subjective evaluator required")
        self._source = frame_authority
        self._ledger = ledger
        self._evidence = evidence
        self._last_step = -1
        self._reservation_lock = Lock()
        self._used_captures: set[str] = set()
        self._used_frames: set[str] = set()
        self._used_receipts: set[str] = set()

    def review(self, frame: CandidateFrame) -> CompetitionAdvice:
        frame = _frame(frame)
        if frame.life_ref != self.life_ref:
            raise ValueError("foreign frame life")
        # Only the independent upstream owner can attest the true identity
        # and provenance of this frame. A syntactically valid hash is NOT proof.
        if self._source.verify(life_ref=self.life_ref, frame=frame) is not True:
            raise ValueError("frame not authenticated by source port")
        # Atomic *in-memory* reservation prevents concurrent replay within
        # this instance, but does not provide durability after process death.
        with self._reservation_lock:
            if (frame.physical_step <= self._last_step
                    or frame.capture_ref in self._used_captures
                    or frame.frame_ref in self._used_frames):
                raise ValueError("stale, repeated or previously attempted frame")
            # A timeout or invalid receipt may mean the external ledger has
            # already charged. Never re-evaluate this same capture locally.
            self._last_step = frame.physical_step
            self._used_captures.add(frame.capture_ref)
            self._used_frames.add(frame.frame_ref)
        names = tuple(c.candidate_ref for c in frame.candidates)
        if not names:
            return CompetitionAdvice(frame.frame_ref, frame.capture_ref, frame.physical_step,
                                     "NO_CANDIDATES", None, (), (), ())
        receipts = self._ledger.debit_batch(
            life_ref=self.life_ref, frame_ref=frame.frame_ref,
            claim_digest=frame.claim_digest, candidate_refs=names,
            operation=OPERATION, units_each=UC_PER_CANDIDATE)
        if receipts is None:
            # The port contract says None means no work was charged.
            return CompetitionAdvice(frame.frame_ref, frame.capture_ref, frame.physical_step,
                                     "UNFUNDED", None, (), (), ())
        if type(receipts) is not tuple or len(receipts) != len(names):
            raise ValueError("partial or malformed batch receipt")
        for candidate_ref, receipt in zip(names, receipts):
            if type(receipt) is not CompetitionReceipt:
                raise ValueError("invalid batch receipt type")
            receipt.validate()
            if (receipt.life_ref != self.life_ref or receipt.frame_ref != frame.frame_ref
                    or receipt.claim_digest != frame.claim_digest
                    or receipt.candidate_ref != candidate_ref
                    or receipt.ref in self._used_receipts):
                raise ValueError("foreign, mismatched or previously used receipt")
            self._used_receipts.add(receipt.ref)
        if len({receipt.ref for receipt in receipts}) != len(names):
            raise ValueError("duplicated receipts in batch")
        values = self._evidence.evaluate_batch(frame=frame, receipts=receipts)
        if type(values) is not tuple or len(values) != len(names):
            raise ValueError("missing/partial subjective valuations after paid batch")
        for name, receipt, value in zip(names, receipts, values):
            if type(value) is not SubjectiveValuation:
                raise ValueError("invalid subjective valuation type")
            value.validate()
            if value.candidate_ref != name or value.receipt_ref != receipt.ref:
                raise ValueError("valuation cannot be attributed to paid candidate")
        best = max(v.value for v in values)
        eligible = [v.candidate_ref for v in values if v.value == best]
        if best <= 0:
            status, chosen = "NO_POSITIVE_EVIDENCE", None
        elif len(eligible) != 1:
            status, chosen = "AMBIGUOUS", None
        else:
            status, chosen = "ADVISORY_ONLY", eligible[0]
        return CompetitionAdvice(frame.frame_ref, frame.capture_ref, frame.physical_step,
                                 status, chosen, names, tuple(r.ref for r in receipts), values)


def veto_preview(advice: CompetitionAdvice, *, vetoed: bool) -> VetoPreview:
    """Never turns an advisory into approval, even if the toy veto is clear.

    The actual future Gatekeeper/ActionControl MUST re-evaluate and admit any
    option separately. This function has no executable action or permission.
    """
    if type(advice) is not CompetitionAdvice or type(vetoed) is not bool:
        raise ValueError("advice and explicit veto result required")
    _ref(advice.frame_ref, "advice frame")
    if vetoed:
        return VetoPreview(advice.frame_ref, "VETOED", None)
    if advice.status == "ADVISORY_ONLY" and advice.suggested_candidate_ref is not None:
        return VetoPreview(advice.frame_ref, "NOT_ADMITTED", advice.suggested_candidate_ref)
    return VetoPreview(advice.frame_ref, "NOT_ADMITTED", None)