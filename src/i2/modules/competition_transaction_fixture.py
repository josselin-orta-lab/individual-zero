"""One-life SQLite *research fixture* for atomic synthetic Competition advice.

Only a synthetic UC account, candidate advice and an unsigned replayable chain
share this transaction. External frame/evidence ports in tests are mock sources;
this is NOT the real Scheduler, a verified M11 chain, or an Action Control owner.
No command, admission or born individual is produced or resumed by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from typing import Protocol

from .competition_preview import (
    OPERATION, UC_PER_CANDIDATE, CompetitionAdvice, CompetitionPreview,
    CompetitionReceipt, SubjectiveValuation, _frame,
)
from .intention_continuity import _ref
from .option_reconstruction import CandidateFrame, SemanticCandidate

SCHEMA = "i2-competition-atomic-fixture-v1"
ZERO_HASH = "0" * 64
_FAULTS = frozenset({"after_debit", "after_evidence", "before_commit", "after_commit"})
_FRAME_KEYS = frozenset({"frame_ref", "life_ref", "capture_ref", "physical_step",
                         "claim_digest", "work_correlation_ref", "candidates"})
_CANDIDATE_KEYS = frozenset({"candidate_ref", "semantic_ref", "intention_ref"})
_VALUE_KEYS = frozenset({"candidate_ref", "receipt_ref", "evidence_ref", "value"})
_EVENT_KEYS = frozenset({"seq", "frame", "status", "suggested_candidate_ref",
                         "evaluated_candidate_refs", "receipt_refs", "values", "units_spent"})


def _canonical(data: object) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=True,
                      ensure_ascii=True, allow_nan=False)


def _chain(previous: str, record: str) -> str:
    return sha256((SCHEMA + "\n" + previous + "\n" + record).encode("ascii")).hexdigest()


def _receipt_ref(life: str, frame_ref: str, candidate_ref: str, seq: int, index: int) -> str:
    return "fixture:batch:" + sha256(_canonical(
        [SCHEMA, life, frame_ref, candidate_ref, seq, index]
    ).encode("ascii")).hexdigest()


def _frame_map(frame: CandidateFrame) -> dict[str, object]:
    _frame(frame)
    return {"frame_ref": frame.frame_ref, "life_ref": frame.life_ref,
            "capture_ref": frame.capture_ref, "physical_step": frame.physical_step,
            "claim_digest": frame.claim_digest,
            "work_correlation_ref": frame.work_correlation_ref,
            "candidates": [{"candidate_ref": x.candidate_ref,
                            "semantic_ref": x.semantic_ref,
                            "intention_ref": x.intention_ref}
                           for x in frame.candidates]}


def _parse_frame(data: object) -> CandidateFrame:
    if type(data) is not dict or set(data) != _FRAME_KEYS or type(data["candidates"]) is not list:
        raise ValueError("invalid frame schema")
    parsed = []
    for item in data["candidates"]:
        if type(item) is not dict or set(item) != _CANDIDATE_KEYS:
            raise ValueError("invalid candidate schema")
        parsed.append(SemanticCandidate(**item))
    frame = CandidateFrame(**{k: v for k, v in data.items() if k != "candidates"},
                           candidates=tuple(parsed))
    return _frame(frame)


def _advice_map(advice: CompetitionAdvice) -> dict[str, object]:
    return {"status": advice.status,
            "suggested_candidate_ref": advice.suggested_candidate_ref,
            "evaluated_candidate_refs": list(advice.evaluated_candidate_refs),
            "receipt_refs": list(advice.receipt_refs),
            "values": [{"candidate_ref": v.candidate_ref, "receipt_ref": v.receipt_ref,
                        "evidence_ref": v.evidence_ref, "value": v.value}
                       for v in advice.valuation_records]}


class SourcePort(Protocol):
    """Must verify an already published, first-person frame; only a mock here."""
    def verify(self, *, life_ref: str, frame: CandidateFrame) -> bool: ...


class EvidencePort(Protocol):
    """Read-only subjective evidence required; not implemented by this fixture."""
    def evaluate_batch(self, *, frame: CandidateFrame,
                       receipts: tuple[CompetitionReceipt, ...]) -> tuple[SubjectiveValuation, ...]: ...


class FaultInjected(RuntimeError):
    """Injected failure before SQLite commit."""


class CommitAcknowledgmentLost(RuntimeError):
    """The commit succeeded, but its acknowledgment did not reach the caller."""


@dataclass(frozen=True, slots=True)
class FixtureAdviceReceipt:
    """Never a real UC/M11 receipt or motor admission."""
    seq: int
    frame_ref: str
    capture_ref: str
    status: str
    suggested_candidate_ref: str | None
    units_spent: int
    chain_head: str
    motor_authority: str = "NONE"


class _Ledger:
    """Mock port debiting inside the caller's existing SQLite transaction."""
    def __init__(self, *, conn: sqlite3.Connection | None, life: str, seq: int,
                 balance: int, fault: str | None = None) -> None:
        self.conn = conn
        self.life = life
        self.seq = seq
        self.remaining = balance
        self.spent = 0
        self.fault = fault

    def debit_batch(self, *, life_ref: str, frame_ref: str, claim_digest: str,
                    candidate_refs: tuple[str, ...], operation: str,
                    units_each: int) -> tuple[CompetitionReceipt, ...] | None:
        if life_ref != self.life or operation != OPERATION or units_each != UC_PER_CANDIDATE:
            raise ValueError("unexpected batch debit")
        cost = len(candidate_refs) * units_each
        if cost > self.remaining:
            return None
        self.remaining -= cost
        self.spent += cost
        if self.conn is not None:
            self.conn.execute("UPDATE account SET remaining_uc=remaining_uc-? WHERE id=1", (cost,))
        if self.fault == "after_debit":
            raise FaultInjected("injected before evaluation")
        return tuple(CompetitionReceipt(
            ref=_receipt_ref(self.life, frame_ref, candidate, self.seq, i),
            life_ref=life_ref, frame_ref=frame_ref, claim_digest=claim_digest,
            candidate_ref=candidate, operation=operation, units=units_each,
        ) for i, candidate in enumerate(candidate_refs))


class _PublishedValues:
    """Replay saved values to the same pure Competition policy, not a new oracle."""
    def __init__(self, values: object) -> None:
        if type(values) is not list:
            raise ValueError("invalid saved values")
        self.values = []
        for item in values:
            if type(item) is not dict or set(item) != _VALUE_KEYS:
                raise ValueError("invalid saved valuation")
            v = SubjectiveValuation(**item)
            v.validate()
            self.values.append(v)

    def evaluate_batch(self, *, frame: CandidateFrame,
                       receipts: tuple[CompetitionReceipt, ...]) -> tuple[SubjectiveValuation, ...]:
        return tuple(self.values)


class _AcceptFrame:
    def verify(self, *, life_ref: str, frame: CandidateFrame) -> bool:
        return True  # Only for audit replay; NOT an independent attester.


class CompetitionTransactionFixture:
    """Atomic *synthetic* UC debit + advice + replay record, no motor authority.

    A frame source must validate upstream identity before any transaction. A
    separate evidence port provides *read-only* observed valuations. Neither
    source is implemented nor authenticated by this fixture. The SQLite budget
    is NOT the Scheduler, and its hash chain has no independently signed root.
    """
    def __init__(self, *, path: Path, life_ref: str, frame_source: SourcePort,
                 evidence_source: EvidencePort) -> None:
        self.path = Path(path)
        self.life_ref = _ref(life_ref, "fixture life")
        if not callable(getattr(frame_source, "verify", None)):
            raise ValueError("frame attestation port required")
        if not callable(getattr(evidence_source, "evaluate_batch", None)):
            raise ValueError("independent evidence port required")
        self.source = frame_source
        self.evidence = evidence_source

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               frame_source: SourcePort, evidence_source: EvidencePort) -> CompetitionTransactionFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("synthetic UC capacity invalid")
        obj = cls(path=path, life_ref=life_ref,
                  frame_source=frame_source, evidence_source=evidence_source)
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
                    event_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
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
    def reopen(cls, *, path: Path, life_ref: str, frame_source: SourcePort,
               evidence_source: EvidencePort) -> CompetitionTransactionFixture:
        obj = cls(path=path, life_ref=life_ref,
                  frame_source=frame_source, evidence_source=evidence_source)
        obj.audit()  # Read-only audit; never instantiate or resume a born life.
        return obj

    def _connect(self, *, readonly: bool = False) -> sqlite3.Connection:
        if self.path.is_symlink() or not self.path.is_file():
            raise ValueError("missing or linked synthetic database")
        conn = sqlite3.connect(self.path.resolve().as_uri() +
                               ("?mode=ro" if readonly else "?mode=rw"),
                               uri=True, isolation_level=None, timeout=5)
        conn.execute("PRAGMA busy_timeout=5000")
        if not readonly:
            conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _verify(self, conn: sqlite3.Connection) -> tuple[int, int, int, str]:
        meta = conn.execute("SELECT schema_id, life_ref, capacity FROM identity WHERE id=1").fetchone()
        if (meta is None or meta[:2] != (SCHEMA, self.life_ref) or
                type(meta[2]) is not int or not 0 <= meta[2] <= 1000000):
            raise ValueError("fixture identity mismatch")
        state = conn.execute("SELECT remaining_uc, last_step, committed, chain_head FROM account WHERE id=1").fetchone()
        if state is None:
            raise ValueError("fixture account absent")
        balance = meta[2]
        prev, count, last_step = ZERO_HASH, 0, -1
        captures: set[str] = set()
        for seq, step, capture_ref, frame_ref, text, previous, chain_hash in conn.execute(
            "SELECT seq,physical_step,capture_ref,frame_ref,event_json,previous_hash,event_hash FROM events ORDER BY seq"
        ):
            count += 1
            if (type(text) is not str or seq != count or previous != prev or
                    _chain(prev, text) != chain_hash):
                raise ValueError("broken local competition event chain")
            data = json.loads(text)
            if type(data) is not dict or set(data) != _EVENT_KEYS or _canonical(data) != text:
                raise ValueError("noncanonical local competition event")
            frame = _parse_frame(data["frame"])
            if (frame.life_ref != self.life_ref or frame.frame_ref != frame_ref or
                    frame.capture_ref != capture_ref or frame.physical_step != step or
                    frame.physical_step <= last_step or frame.capture_ref in captures or
                    data["seq"] != seq):
                raise ValueError("competition replay time or source mismatch")
            replay_ledger = _Ledger(conn=None, life=self.life_ref, seq=seq, balance=balance)
            # All published valuations are checked by the actual pure advice
            # contract, with synthetic local receipts recomputed independently.
            source = _PublishedValues(data["values"])
            advice = CompetitionPreview(life_ref=self.life_ref, frame_authority=_AcceptFrame(),
                                        ledger=replay_ledger, evidence=source).review(frame)
            if data["values"] != _advice_map(advice)["values"]:
                raise ValueError("valuation replay mismatch")
            expected = _advice_map(advice)
            if any(data[field] != expected[field] for field in expected):
                raise ValueError("competition policy replay mismatch")
            if type(data["units_spent"]) is not int or data["units_spent"] != replay_ledger.spent:
                raise ValueError("synthetic debit replay mismatch")
            balance = replay_ledger.remaining
            prev, last_step = chain_hash, step
            captures.add(capture_ref)
        if (state != (balance, last_step, count, prev)):
            raise ValueError("competition account/custody mismatch")
        return balance, last_step, count, prev

    def audit(self) -> dict[str, object]:
        """Reconstruct exact local synthetic account and advice, NOT M11 proof."""
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            remaining, step, count, head = self._verify(conn)
            return {"schema": SCHEMA, "life_ref": self.life_ref,
                    "remaining_synthetic_uc": remaining, "last_step": step,
                    "record_count": count, "chain_head": head,
                    "m11_authenticated": False, "scheduler_uc_authenticated": False,
                    "motor_authority": "NONE"}
        finally:
            conn.close()

    def review(self, *, frame: CandidateFrame,
               _fault_at: str | None = None) -> FixtureAdviceReceipt:
        if _fault_at is not None and _fault_at not in _FAULTS:
            raise ValueError("unknown software fault point")
        frame = _frame(frame)
        if frame.life_ref != self.life_ref:
            raise ValueError("foreign fixture life")
        if self.source.verify(life_ref=self.life_ref, frame=frame) is not True:
            raise ValueError("frame source did not attest synthetic frame")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            _, last_step, count, head = self._verify(conn)
            if frame.physical_step <= last_step or conn.execute(
                "SELECT 1 FROM events WHERE capture_ref=? OR frame_ref=?",
                (frame.capture_ref, frame.frame_ref),
            ).fetchone():
                raise ValueError("already consumed or stale frame")
            row = conn.execute("SELECT remaining_uc FROM account WHERE id=1").fetchone()
            ledger = _Ledger(conn=conn, life=self.life_ref, seq=count + 1,
                             balance=row[0], fault=_fault_at)
            advice = CompetitionPreview(life_ref=self.life_ref, frame_authority=_AcceptFrame(),
                                        ledger=ledger, evidence=self.evidence).review(frame)
            if _fault_at == "after_evidence":
                raise FaultInjected("injected after evaluation")
            event = {"seq": count + 1, "frame": _frame_map(frame),
                     **_advice_map(advice), "units_spent": ledger.spent}
            text = _canonical(event)
            new_head = _chain(head, text)
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                         (count + 1, frame.physical_step, frame.capture_ref, frame.frame_ref,
                          text, head, new_head))
            conn.execute("UPDATE account SET last_step=?,committed=?,chain_head=? WHERE id=1",
                         (frame.physical_step, count + 1, new_head))
            if _fault_at == "before_commit":
                raise FaultInjected("injected before COMMIT")
            conn.execute("COMMIT")
            if _fault_at == "after_commit":
                raise CommitAcknowledgmentLost("COMMIT succeeded; use lookup instead of retry")
            return FixtureAdviceReceipt(count + 1, frame.frame_ref, frame.capture_ref,
                                        advice.status, advice.suggested_candidate_ref,
                                        ledger.spent, new_head)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def lookup(self, *, capture_ref: str) -> FixtureAdviceReceipt | None:
        _ref(capture_ref, "capture ref")
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            self._verify(conn)
            row = conn.execute("SELECT seq,frame_ref,event_json,event_hash FROM events WHERE capture_ref=?",
                               (capture_ref,)).fetchone()
            if row is None:
                return None
            seq, frame_ref, text, event_hash = row
            event = json.loads(text)
            return FixtureAdviceReceipt(seq, frame_ref, capture_ref, event["status"],
                                        event["suggested_candidate_ref"],
                                        event["units_spent"], event_hash)
        finally:
            conn.close()
