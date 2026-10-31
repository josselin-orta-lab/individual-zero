"""Inert SQLite custody test for a paid Action Control *review*, NEVER admission.

An isolated synthetic UC account, safety finding and ControlReview share one
SQLite transaction. Real perception provenance, living state, Scheduler UC,
M11 signing, world physics and physical command admission are NOT implemented.
This is intentionally independent from the cognitive-cycle fixture: its UC
account is NOT atomic with the upstream one and cannot be used in a living I2.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3

from .action_control_boundary import (
    ActionControlBoundary, ControlReceipt, ControlReview, SafetyFinding,
    CONTROL_OPERATION, CONTROL_UC, _consistent_advice,
)
from .competition_preview import CompetitionAdvice, SubjectiveValuation
from .competition_transaction_fixture import _frame_map, _parse_frame, _advice_map
from .intention_continuity import _ref
from .option_reconstruction import CandidateFrame

SCHEMA = "i2-action-control-custody-synthetic-v1"
ZERO_HASH = "0" * 64
_FAULTS = frozenset({"after_control_debit", "after_safety", "before_commit", "after_commit"})
_EVENT_KEYS = frozenset({"seq", "frame", "advice", "control_receipt", "safety_finding",
                          "review", "units_spent"})
_ADVICE_KEYS = frozenset({"status", "suggested_candidate_ref", "evaluated_candidate_refs",
                          "receipt_refs", "values"})
_VALUE_KEYS = frozenset({"candidate_ref", "receipt_ref", "evidence_ref", "value"})
_REVIEW_KEYS = frozenset({"frame_ref", "capture_ref", "physical_step", "status",
                          "suggested_candidate_ref", "control_receipt_ref",
                          "safety_evidence_ref", "motor_authority"})
_RECEIPT_KEYS = frozenset(ControlReceipt.__dataclass_fields__)
_SAFETY_KEYS = frozenset(SafetyFinding.__dataclass_fields__)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _sha(value: object) -> str:
    return sha256(_canonical(value).encode("ascii")).hexdigest()


def _chain(prior: str, body: str) -> str:
    return sha256((SCHEMA + "\n" + prior + "\n" + body).encode("ascii")).hexdigest()


def _control_ref(life: str, frame: CandidateFrame, candidate: str, seq: int) -> str:
    return "synthetic:control:" + _sha([SCHEMA, life, frame.frame_ref,
                                        frame.claim_digest, candidate, seq])


def _parse_advice(frame: CandidateFrame, raw: object) -> CompetitionAdvice:
    if type(raw) is not dict or set(raw) != _ADVICE_KEYS or type(raw["values"]) is not list:
        raise ValueError("noncanonical stored advice")
    values = []
    for item in raw["values"]:
        if type(item) is not dict or set(item) != _VALUE_KEYS:
            raise ValueError("invalid stored valuation")
        values.append(SubjectiveValuation(**item))
    if type(raw["evaluated_candidate_refs"]) is not list or type(raw["receipt_refs"]) is not list:
        raise ValueError("invalid advice receipt collections")
    result = CompetitionAdvice(frame.frame_ref, frame.capture_ref, frame.physical_step,
                               raw["status"], raw["suggested_candidate_ref"],
                               tuple(raw["evaluated_candidate_refs"]),
                               tuple(raw["receipt_refs"]), tuple(values))
    _consistent_advice(frame, result)
    return result


class FaultInjected(RuntimeError):
    """Test-only interruption before the local COMMIT."""


class CommitAcknowledgmentLost(RuntimeError):
    """Local COMMIT succeeded; query lookup instead of recharging."""


@dataclass(frozen=True, slots=True)
class CustodyReviewReceipt:
    """Historical review status ONLY; no motor command, permit or admission."""
    seq: int
    frame_ref: str
    capture_ref: str
    status: str
    suggested_candidate_ref: str | None
    units_spent: int
    chain_head: str
    motor_authority: str = "NONE"


class _AcceptedCurrent:
    """For local replay only. NOT M11 authentication."""
    def verify_current(self, *, life_ref: str, frame: CandidateFrame,
                       advice: CompetitionAdvice) -> bool:
        return True


class _LocalLedger:
    """Debit local synthetic UC within the caller's existing transaction."""
    def __init__(self, *, conn: sqlite3.Connection | None, life_ref: str,
                 seq: int, balance: int, fault: str | None = None) -> None:
        self.conn = conn
        self.life_ref = life_ref
        self.seq = seq
        self.remaining = balance
        self.spent = 0
        self.receipt: ControlReceipt | None = None
        self.fault = fault

    def debit(self, *, life_ref: str, frame_ref: str, capture_ref: str,
              claim_digest: str, candidate_ref: str, operation: str,
              units: int) -> ControlReceipt | None:
        if (life_ref != self.life_ref or operation != CONTROL_OPERATION or
                type(units) is not int or units != CONTROL_UC):
            raise ValueError("unexpected synthetic control debit")
        if self.remaining < CONTROL_UC:
            return None
        self.remaining -= CONTROL_UC
        self.spent += CONTROL_UC
        if self.conn is not None:
            self.conn.execute("UPDATE account SET remaining_uc=remaining_uc-? WHERE id=1",
                              (CONTROL_UC,))
        if self.fault == "after_control_debit":
            raise FaultInjected("after synthetic Action Control debit")
        # The resulting deterministic receipt is generated by the *local fixture*,
        # not an external Scheduler. Its identity is tied to the full frame.
        candidate = _ref(candidate_ref, "synthetic candidate")
        frame = self._frame
        if (frame_ref != frame.frame_ref or capture_ref != frame.capture_ref or
                claim_digest != frame.claim_digest):
            raise ValueError("control debit context mismatch")
        self.receipt = ControlReceipt(
            _control_ref(self.life_ref, frame, candidate, self.seq), life_ref,
            frame_ref, capture_ref, claim_digest, candidate, operation, units)
        return self.receipt

    def bind_frame(self, frame: CandidateFrame) -> _LocalLedger:
        self._frame = frame
        return self


class _CaptureSafety:
    def __init__(self, source: object, fault: str | None = None) -> None:
        self.source = source
        self.fault = fault
        self.finding: SafetyFinding | None = None

    def check(self, *, life_ref: str, frame: CandidateFrame,
              candidate_ref: str, control_receipt_ref: str) -> SafetyFinding:
        value = self.source.check(life_ref=life_ref, frame=frame,
                                  candidate_ref=candidate_ref,
                                  control_receipt_ref=control_receipt_ref)
        self.finding = value
        if self.fault == "after_safety":
            raise FaultInjected("after synthetic safety review")
        return value


class _RecordedSafety:
    """Replays recorded data, not the current outside-world safety authority."""
    def __init__(self, finding: SafetyFinding | None) -> None:
        self.finding = finding

    def check(self, *, life_ref: str, frame: CandidateFrame,
              candidate_ref: str, control_receipt_ref: str) -> SafetyFinding:
        if self.finding is None:
            raise ValueError("missing historically stored safety finding")
        return self.finding


def _receipt(seq: int, frame: CandidateFrame, review: ControlReview,
             spent: int, head: str) -> CustodyReviewReceipt:
    return CustodyReviewReceipt(seq, frame.frame_ref, frame.capture_ref,
                                review.status, review.suggested_candidate_ref,
                                spent, head)


class ActionControlCustodyFixture:
    """One-file durable *synthetic* safety-review custody, no motor capability.

    The external current-source and veto-source MUST be read-only; a duplicate
    debit only becomes impossible inside THIS fixture, not in a real Scheduler.
    Neither a review receipt nor the SQLite data is an admission token.
    """

    def __init__(self, *, path: Path, life_ref: str,
                 current_source: object, safety_source: object) -> None:
        self.path = Path(path)
        self.life_ref = _ref(life_ref, "synthetic control life")
        if not callable(getattr(current_source, "verify_current", None)):
            raise ValueError("current-life attestation port is required")
        if not callable(getattr(safety_source, "check", None)):
            raise ValueError("independent safety veto port is required")
        self.current_source = current_source
        self.safety_source = safety_source

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               current_source: object, safety_source: object) -> ActionControlCustodyFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("invalid synthetic UC capacity")
        obj = cls(path=path, life_ref=life_ref,
                  current_source=current_source, safety_source=safety_source)
        if obj.path.is_symlink() or not obj.path.parent.is_dir():
            raise ValueError("invalid fixture directory")
        fd = os.open(obj.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.close(fd)
        conn = obj._connect()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE identity (id INTEGER PRIMARY KEY CHECK(id=1),
                    schema_id TEXT NOT NULL, life_ref TEXT NOT NULL,
                    capacity INTEGER NOT NULL);
                CREATE TABLE account (id INTEGER PRIMARY KEY CHECK(id=1),
                    remaining_uc INTEGER NOT NULL CHECK(remaining_uc>=0),
                    last_step INTEGER NOT NULL, committed INTEGER NOT NULL,
                    chain_head TEXT NOT NULL);
                CREATE TABLE events (seq INTEGER PRIMARY KEY,
                    physical_step INTEGER NOT NULL UNIQUE,
                    capture_ref TEXT NOT NULL UNIQUE,
                    frame_ref TEXT NOT NULL UNIQUE,
                    event_json TEXT NOT NULL, previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE);
            """)
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO identity VALUES (1,?,?,?)",
                         (SCHEMA, obj.life_ref, synthetic_uc))
            conn.execute("INSERT INTO account VALUES (1,?,-1,0,?)",
                         (synthetic_uc, ZERO_HASH))
            conn.execute("COMMIT")
        finally:
            conn.close()
        obj.audit()
        return obj

    @classmethod
    def reopen(cls, *, path: Path, life_ref: str, current_source: object,
               safety_source: object) -> ActionControlCustodyFixture:
        obj = cls(path=path, life_ref=life_ref,
                  current_source=current_source, safety_source=safety_source)
        obj.audit()  # Read-only audit of a local fixture, NEVER life recovery.
        return obj

    def _connect(self, *, readonly: bool = False) -> sqlite3.Connection:
        if self.path.is_symlink() or not self.path.is_file():
            raise ValueError("missing or symlinked synthetic database")
        conn = sqlite3.connect(self.path.resolve().as_uri() +
                               ("?mode=ro" if readonly else "?mode=rw"),
                               uri=True, isolation_level=None, timeout=5)
        conn.execute("PRAGMA busy_timeout=5000")
        if not readonly:
            conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _verify(self, conn: sqlite3.Connection) -> tuple[int, int, int, str]:
        identity = conn.execute("SELECT schema_id,life_ref,capacity FROM identity WHERE id=1").fetchone()
        if (identity is None or identity[:2] != (SCHEMA, self.life_ref)
                or type(identity[2]) is not int or not 0 <= identity[2] <= 1000000):
            raise ValueError("invalid synthetic custody identity")
        account = conn.execute("SELECT remaining_uc,last_step,committed,chain_head FROM account WHERE id=1").fetchone()
        if account is None:
            raise ValueError("missing synthetic account")
        remaining = identity[2]
        seq_count, last_step, previous = 0, -1, ZERO_HASH
        captures: set[str] = set()
        frames: set[str] = set()
        for seq, step, cref, fref, body, prior, head in conn.execute(
                "SELECT seq,physical_step,capture_ref,frame_ref,event_json,previous_hash,event_hash "
                "FROM events ORDER BY seq"):
            seq_count += 1
            if (seq != seq_count or type(body) is not str or prior != previous or
                    _chain(previous, body) != head):
                raise ValueError("broken local control-review chain")
            record = json.loads(body)
            if (type(record) is not dict or set(record) != _EVENT_KEYS or
                    _canonical(record) != body or record["seq"] != seq):
                raise ValueError("malformed control-review event")
            frame = _parse_frame(record["frame"])
            advice = _parse_advice(frame, record["advice"])
            if (frame.life_ref != self.life_ref or frame.frame_ref != fref
                    or frame.capture_ref != cref or frame.physical_step != step
                    or step <= last_step or cref in captures or fref in frames):
                raise ValueError("control review chronology or identity mismatch")
            rr = record["control_receipt"]
            sf = record["safety_finding"]
            if rr is not None and (type(rr) is not dict or set(rr) != _RECEIPT_KEYS):
                raise ValueError("malformed stored synthetic control receipt")
            if sf is not None and (type(sf) is not dict or set(sf) != _SAFETY_KEYS):
                raise ValueError("malformed stored safety finding")
            if type(record["review"]) is not dict or set(record["review"]) != _REVIEW_KEYS:
                raise ValueError("malformed stored control review")
            recorded_finding = SafetyFinding(**sf) if sf is not None else None
            ledger = _LocalLedger(conn=None, life_ref=self.life_ref,
                                  seq=seq, balance=remaining).bind_frame(frame)
            reviewed = ActionControlBoundary(
                life_ref=self.life_ref, current_authority=_AcceptedCurrent(),
                ledger=ledger, safety_authority=_RecordedSafety(recorded_finding),
            ).review(frame=frame, advice=advice)
            if (asdict(reviewed) != record["review"] or
                    (asdict(ledger.receipt) if ledger.receipt else None) != rr or
                    type(record["units_spent"]) is not int or
                    ledger.spent != record["units_spent"]):
                raise ValueError("published control review or debit replay mismatch")
            if reviewed.motor_authority != "NONE":
                raise ValueError("motor authority is forbidden")
            remaining = ledger.remaining
            previous, last_step = head, step
            captures.add(cref)
            frames.add(fref)
        if account != (remaining, last_step, seq_count, previous):
            raise ValueError("synthetic control account and event journal disagree")
        return remaining, last_step, seq_count, previous

    def audit(self) -> dict[str, object]:
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            remaining, step, count, head = self._verify(conn)
            return {"schema": SCHEMA, "life_ref": self.life_ref,
                    "remaining_synthetic_uc": remaining, "last_step": step,
                    "committed": count, "chain_head": head,
                    "m11_authenticated": False, "scheduler_uc_authenticated": False,
                    "motor_authority": "NONE"}
        finally:
            conn.close()

    def review(self, *, frame: CandidateFrame, advice: CompetitionAdvice,
               _fault_at: str | None = None) -> CustodyReviewReceipt:
        if _fault_at is not None and _fault_at not in _FAULTS:
            raise ValueError("unknown synthetic fault point")
        _consistent_advice(frame, advice)
        if frame.life_ref != self.life_ref:
            raise ValueError("foreign synthetic control life")
        if self.current_source.verify_current(life_ref=self.life_ref,
                                              frame=frame, advice=advice) is not True:
            raise ValueError("synthetic frame is no longer current")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            balance, last_step, count, head = self._verify(conn)
            if (frame.physical_step <= last_step or conn.execute(
                    "SELECT 1 FROM events WHERE capture_ref=? OR frame_ref=?",
                    (frame.capture_ref, frame.frame_ref)).fetchone()):
                raise ValueError("stale or replayed synthetic control review")
            seq = count + 1
            ledger = _LocalLedger(conn=conn, life_ref=self.life_ref, seq=seq,
                                  balance=balance, fault=_fault_at).bind_frame(frame)
            safety = _CaptureSafety(self.safety_source, fault=_fault_at)
            review = ActionControlBoundary(
                life_ref=self.life_ref, current_authority=_AcceptedCurrent(),
                ledger=ledger, safety_authority=safety).review(frame=frame, advice=advice)
            if review.motor_authority != "NONE":
                raise ValueError("unexpected nonzero motor authority")
            # Fail closed on a context shift before COMMIT. This is still NOT a
            # physical-world lock: no post-COMMIT motor use is ever permitted.
            if self.current_source.verify_current(life_ref=self.life_ref,
                                                  frame=frame, advice=advice) is not True:
                raise ValueError("current capture changed before review publication")
            event = {"seq": seq, "frame": _frame_map(frame), "advice": _advice_map(advice),
                     "control_receipt": asdict(ledger.receipt) if ledger.receipt else None,
                     "safety_finding": asdict(safety.finding) if safety.finding else None,
                     "review": asdict(review), "units_spent": ledger.spent}
            body = _canonical(event)
            next_hash = _chain(head, body)
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                         (seq, frame.physical_step, frame.capture_ref, frame.frame_ref,
                          body, head, next_hash))
            conn.execute("UPDATE account SET last_step=?,committed=?,chain_head=? WHERE id=1",
                         (frame.physical_step, seq, next_hash))
            if _fault_at == "before_commit":
                raise FaultInjected("before local synthetic COMMIT")
            conn.execute("COMMIT")
            if _fault_at == "after_commit":
                raise CommitAcknowledgmentLost("committed; use lookup, do not recharge")
            return _receipt(seq, frame, review, ledger.spent, next_hash)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def lookup(self, *, capture_ref: str) -> CustodyReviewReceipt | None:
        """Read-only resolution of lost acknowledgment; never a second review."""
        _ref(capture_ref, "synthetic capture")
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            self._verify(conn)
            row = conn.execute("SELECT seq,event_json,event_hash FROM events WHERE capture_ref=?",
                               (capture_ref,)).fetchone()
            if row is None:
                return None
            seq, body, head = row
            record = json.loads(body)
            frame = _parse_frame(record["frame"])
            saved_review = ControlReview(**record["review"])
            return _receipt(seq, frame, saved_review, record["units_spent"], head)
        finally:
            conn.close()
