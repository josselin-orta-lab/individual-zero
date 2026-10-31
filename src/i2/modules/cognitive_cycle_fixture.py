"""Inert I2 SQLite fixture: one atomic *synthetic* cognitive cycle.

The same SQLite COMMIT covers a mock 1-UC intention consultation, the resulting
semantic state, reconstruction of current candidates, a fully funded mock
Competition batch (or abstention), and an unsigned audit record.

This is NOT a living engine, a real Scheduler, an M11 WAL, first-person proof,
Action Control or a physical command. Ports are read-only claims; tests use
synthetic sources. Never attach this fixture to a real individual's UC account.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from typing import Protocol

from .intention_continuity import IntentionContinuity, IntentionTransition, _ref
from .intention_ingress import ObservationClaim, INTAKE_UC
from .intention_atomic_fixture import _claim_map, _parse_claim, _request
from .option_reconstruction import reconstruct_candidates, CandidateFrame
from .competition_preview import (
    CompetitionPreview, CompetitionReceipt, SubjectiveValuation,
    OPERATION, UC_PER_CANDIDATE, _frame,
)
from .competition_transaction_fixture import _frame_map, _advice_map, _AcceptFrame, _PublishedValues

SCHEMA = "i2-unified-cognitive-cycle-fixture-v1"
ZERO_HASH = "0" * 64
_FAULTS = frozenset({"after_intake_debit", "after_intention", "after_competition_debit",
                    "before_commit", "after_commit"})
_EVENT_FIELDS = frozenset({
    "seq", "claim", "claim_digest", "request", "intake_receipt_ref", "intention_kind",
    "owner_snapshot", "frame", "advice", "intake_uc", "competition_uc",
})


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_json(value).encode("ascii")).hexdigest()


def _chain(previous: str, body: str) -> str:
    return sha256((SCHEMA + "\n" + previous + "\n" + body).encode("ascii")).hexdigest()


def _intake_ref(life: str, digest: str, seq: int) -> str:
    return "cycle:intake:" + _digest([SCHEMA, life, digest, seq])


def _competition_ref(life: str, frame_ref: str, candidate_ref: str,
                     seq: int, index: int) -> str:
    return "cycle:competition:" + _digest([SCHEMA, life, frame_ref, candidate_ref, seq, index])


class ObservationSource(Protocol):
    def verify(self, *, life_ref: str, claim: ObservationClaim, digest: str) -> bool: ...


class ValuationSource(Protocol):
    def evaluate_batch(self, *, frame: CandidateFrame,
                       receipts: tuple[CompetitionReceipt, ...]) -> tuple[SubjectiveValuation, ...]: ...


class FaultInjected(RuntimeError):
    """Test-only fault before one local COMMIT."""


class CommitAcknowledgmentLost(RuntimeError):
    """SQLite COMMIT succeeded, but the caller lost the acknowledgment."""


@dataclass(frozen=True, slots=True)
class CycleReceipt:
    """A synthetic audit receipt, explicitly not admission or real UC evidence."""
    seq: int
    capture_ref: str
    claim_digest: str
    intention_kind: str
    competition_status: str
    suggested_candidate_ref: str | None
    intake_uc: int
    competition_uc: int
    chain_head: str
    motor_authority: str = "NONE"


class _LocalLedger:
    """A mock whole-frame budget coupled to the *existing* SQLite transaction."""

    def __init__(self, *, life: str, seq: int, balance: int,
                 conn: sqlite3.Connection | None, fault: str | None = None) -> None:
        self.life = life
        self.seq = seq
        self.remaining = balance
        self.spent = 0
        self.conn = conn
        self.fault = fault

    def debit_batch(self, *, life_ref: str, frame_ref: str, claim_digest: str,
                    candidate_refs: tuple[str, ...], operation: str,
                    units_each: int) -> tuple[CompetitionReceipt, ...] | None:
        if (life_ref != self.life or operation != OPERATION or
                type(units_each) is not int or units_each != UC_PER_CANDIDATE or
                type(candidate_refs) is not tuple):
            raise ValueError("unexpected synthetic batch debit")
        cost = len(candidate_refs) * units_each
        if cost > self.remaining:
            return None
        self.remaining -= cost
        self.spent += cost
        if self.conn is not None:
            self.conn.execute("UPDATE account SET remaining_uc=remaining_uc-? WHERE id=1", (cost,))
        if self.fault == "after_competition_debit":
            raise FaultInjected("injected after synthetic competition debit")
        return tuple(CompetitionReceipt(
            ref=_competition_ref(self.life, frame_ref, candidate, self.seq, index),
            life_ref=self.life, frame_ref=frame_ref, claim_digest=claim_digest,
            candidate_ref=candidate, operation=operation, units=units_each,
        ) for index, candidate in enumerate(candidate_refs))


def _consult(owner: IntentionContinuity, claim: ObservationClaim, request: dict,
             receipt_ref: str) -> tuple[str, IntentionTransition | None]:
    try:
        if request["method"] == "open":
            transition = owner.open(capture=claim.capture,
                                    semantic_ref=request["semantic_ref"],
                                    evidence_ref=request["evidence_ref"],
                                    ttl_steps=request["ttl_steps"], work_ref=receipt_ref)
        else:
            transition = owner.observe(capture=claim.capture, work_ref=receipt_ref)
    except ValueError:
        # This valid but disallowed operation consumes one synthetic cognition UC.
        # No current-capture transition means that competition MUST NOT run.
        return "policy_rejected", None
    return transition.kind, transition


def _make_receipt(seq: int, claim: ObservationClaim, data: dict, chain: str) -> CycleReceipt:
    advice = data["advice"]
    return CycleReceipt(
        seq=seq, capture_ref=claim.capture.ref, claim_digest=data["claim_digest"],
        intention_kind=data["intention_kind"],
        competition_status="POLICY_REJECTED" if advice is None else advice["status"],
        suggested_candidate_ref=None if advice is None else advice["suggested_candidate_ref"],
        intake_uc=data["intake_uc"], competition_uc=data["competition_uc"], chain_head=chain,
    )


class CognitiveCycleFixture:
    """Inert single-file atomic cognition demonstration, never a born life.

    No inter-ledger transaction is implied: this fixture owns one *synthetic*
    budget, a single local intention owner and the Competition proposal.
    """

    def __init__(self, *, path: Path, life_ref: str,
                 observation_source: ObservationSource,
                 valuation_source: ValuationSource) -> None:
        self.path = Path(path)
        self.life_ref = _ref(life_ref, "synthetic life")
        if not callable(getattr(observation_source, "verify", None)):
            raise ValueError("observation source required")
        if not callable(getattr(valuation_source, "evaluate_batch", None)):
            raise ValueError("subjective value source required")
        self.observation_source = observation_source
        self.valuation_source = valuation_source

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               observation_source: ObservationSource,
               valuation_source: ValuationSource) -> CognitiveCycleFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("invalid synthetic UC capacity")
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source)
        if obj.path.is_symlink() or not obj.path.parent.is_dir():
            raise ValueError("invalid synthetic fixture directory")
        fd = os.open(obj.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.close(fd)
        conn = obj._connect()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE identity (
                    id INTEGER PRIMARY KEY CHECK(id=1), schema_id TEXT NOT NULL,
                    life_ref TEXT NOT NULL, capacity INTEGER NOT NULL);
                CREATE TABLE account (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    remaining_uc INTEGER NOT NULL CHECK(remaining_uc>=0),
                    last_step INTEGER NOT NULL,
                    committed INTEGER NOT NULL, owner_json TEXT NOT NULL,
                    chain_head TEXT NOT NULL);
                CREATE TABLE events (
                    seq INTEGER PRIMARY KEY,
                    physical_step INTEGER NOT NULL UNIQUE,
                    capture_ref TEXT NOT NULL UNIQUE,
                    claim_digest TEXT NOT NULL UNIQUE,
                    event_json TEXT NOT NULL, previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE);
            """)
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO identity VALUES (1,?,?,?)", (SCHEMA, obj.life_ref, synthetic_uc))
            conn.execute("INSERT INTO account VALUES (1,?,-1,0,?,?)",
                         (synthetic_uc, _json(IntentionContinuity().export_state()), ZERO_HASH))
            conn.execute("COMMIT")
        finally:
            conn.close()
        obj.audit()
        return obj

    @classmethod
    def reopen(cls, *, path: Path, life_ref: str,
               observation_source: ObservationSource,
               valuation_source: ValuationSource) -> CognitiveCycleFixture:
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source)
        obj.audit()  # Read-only fixture inspection, NOT M11 life recovery.
        return obj

    def _connect(self, *, readonly: bool = False) -> sqlite3.Connection:
        if self.path.is_symlink() or not self.path.is_file():
            raise ValueError("absent or linked synthetic fixture")
        conn = sqlite3.connect(self.path.resolve().as_uri() +
                               ("?mode=ro" if readonly else "?mode=rw"),
                               uri=True, isolation_level=None, timeout=5)
        conn.execute("PRAGMA busy_timeout=5000")
        if not readonly:
            conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _verify(self, conn: sqlite3.Connection) -> tuple[int, int, int, str, IntentionContinuity]:
        meta = conn.execute("SELECT schema_id, life_ref, capacity FROM identity WHERE id=1").fetchone()
        if (meta is None or meta[:2] != (SCHEMA, self.life_ref) or
                type(meta[2]) is not int or not 0 <= meta[2] <= 1000000):
            raise ValueError("synthetic life identity or schema mismatch")
        account = conn.execute("SELECT remaining_uc,last_step,committed,owner_json,chain_head "
                               "FROM account WHERE id=1").fetchone()
        if account is None:
            raise ValueError("synthetic state absent")
        balance = meta[2]
        last_step = -1
        chain = ZERO_HASH
        owner = IntentionContinuity()
        count = 0
        capture_refs: set[str] = set()
        digests: set[str] = set()
        for seq, step, ref, digest, body, previous_hash, event_hash in conn.execute(
            "SELECT seq,physical_step,capture_ref,claim_digest,event_json,previous_hash,event_hash "
            "FROM events ORDER BY seq"
        ):
            count += 1
            if (seq != count or type(body) is not str or previous_hash != chain or
                    _chain(chain, body) != event_hash):
                raise ValueError("synthetic event chain mismatch")
            data = json.loads(body)
            if type(data) is not dict or set(data) != _EVENT_FIELDS or _json(data) != body:
                raise ValueError("noncanonical cognitive cycle event")
            claim = _parse_claim(data["claim"])
            request = data["request"]
            if type(request) is not dict or set(request) != {"method", "semantic_ref", "evidence_ref", "ttl_steps"}:
                raise ValueError("invalid stored request")
            request = _request(**request)
            if (claim.life_ref != self.life_ref or claim.capture.step != step or
                    step <= last_step or ref in capture_refs or digest in digests or
                    claim.capture.ref != ref or claim.digest() != digest or
                    data["claim_digest"] != digest or data["seq"] != seq or
                    type(data["intake_uc"]) is not int or data["intake_uc"] != INTAKE_UC or
                    data["intake_receipt_ref"] != _intake_ref(self.life_ref, digest, seq) or
                    request["method"] == "open" and request["evidence_ref"] not in claim.subjective_evidence_refs):
                raise ValueError("stored observation and request mismatch")
            if balance < INTAKE_UC:
                raise ValueError("record exceeds synthetic account capacity")
            balance -= INTAKE_UC
            kind, transition = _consult(owner, claim, request, data["intake_receipt_ref"])
            if data["intention_kind"] != kind or data["owner_snapshot"] != owner.export_state():
                raise ValueError("intention replay mismatch")
            if transition is None:
                if data["frame"] is not None or data["advice"] is not None or data["competition_uc"] != 0:
                    raise ValueError("rejected intention cannot publish competition")
            else:
                frame = reconstruct_candidates(claim=claim, transition=transition,
                                               current=owner.current)
                if data["frame"] != _frame_map(frame):
                    raise ValueError("candidate frame replay mismatch")
                saved_advice = data["advice"]
                if type(saved_advice) is not dict or type(saved_advice.get("values")) is not list:
                    raise ValueError("invalid saved competition advice")
                ledger = _LocalLedger(life=self.life_ref, seq=seq, balance=balance, conn=None)
                advice = CompetitionPreview(life_ref=self.life_ref, frame_authority=_AcceptFrame(),
                                            ledger=ledger, evidence=_PublishedValues(saved_advice["values"])).review(frame)
                if saved_advice != _advice_map(advice) or type(data["competition_uc"]) is not int or data["competition_uc"] != ledger.spent:
                    raise ValueError("competition replay or UC mismatch")
                balance = ledger.remaining
            chain = event_hash
            last_step = step
            capture_refs.add(ref)
            digests.add(digest)
        if account != (balance, last_step, count, _json(owner.export_state()), chain):
            raise ValueError("synthetic account, intention or head mismatch")
        return balance, last_step, count, chain, owner

    def audit(self) -> dict[str, object]:
        """Read-only full-policy replay, not a signed record or M11 attestation."""
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            remaining, step, count, head, owner = self._verify(conn)
            return {"schema": SCHEMA, "life_ref": self.life_ref,
                    "remaining_synthetic_uc": remaining, "last_step": step,
                    "committed": count, "chain_head": head,
                    "intention": owner.export_state()["current"],
                    "m11_authenticated": False, "scheduler_uc_authenticated": False,
                    "motor_authority": "NONE"}
        finally:
            conn.close()

    def _process(self, *, claim: ObservationClaim, request: dict,
                 _fault_at: str | None = None) -> CycleReceipt:
        if _fault_at is not None and _fault_at not in _FAULTS:
            raise ValueError("invalid test fault point")
        if type(claim) is not ObservationClaim:
            raise ValueError("exact subjective claim required")
        claim.validate()
        if claim.life_ref != self.life_ref:
            raise ValueError("foreign synthetic life")
        if request["method"] == "open" and request["evidence_ref"] not in claim.subjective_evidence_refs:
            raise ValueError("unobserved intention evidence")
        digest = claim.digest()
        # The injected source MUST be read-only and backed by authenticated
        # first-person events in a future life. Here it is a synthetic test port.
        if self.observation_source.verify(life_ref=self.life_ref, claim=claim, digest=digest) is not True:
            raise ValueError("unattested synthetic observation")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            balance, last_step, count, head, owner = self._verify(conn)
            if claim.capture.step <= last_step or conn.execute(
                "SELECT 1 FROM events WHERE capture_ref=? OR claim_digest=?",
                (claim.capture.ref, digest),
            ).fetchone():
                raise ValueError("stale or duplicate synthetic capture")
            if balance < INTAKE_UC:
                raise ValueError("synthetic UC exhausted before intention")
            conn.execute("UPDATE account SET remaining_uc=remaining_uc-? WHERE id=1", (INTAKE_UC,))
            balance -= INTAKE_UC
            if _fault_at == "after_intake_debit":
                raise FaultInjected("test failure after intake debit")
            seq = count + 1
            intake_ref = _intake_ref(self.life_ref, digest, seq)
            kind, transition = _consult(owner, claim, request, intake_ref)
            if _fault_at == "after_intention":
                raise FaultInjected("test failure after intention consideration")
            if transition is None:
                frame_map, advice_map, comp_uc = None, None, 0
            else:
                frame = reconstruct_candidates(claim=claim, transition=transition,
                                               current=owner.current)
                ledger = _LocalLedger(life=self.life_ref, seq=seq, balance=balance,
                                      conn=conn, fault=_fault_at)
                advice = CompetitionPreview(life_ref=self.life_ref, frame_authority=_AcceptFrame(),
                                            ledger=ledger, evidence=self.valuation_source).review(frame)
                frame_map = _frame_map(frame)
                advice_map = _advice_map(advice)
                comp_uc = ledger.spent
                balance = ledger.remaining
            event = {"seq": seq, "claim": _claim_map(claim), "claim_digest": digest,
                     "request": request, "intake_receipt_ref": intake_ref,
                     "intention_kind": kind, "owner_snapshot": owner.export_state(),
                     "frame": frame_map, "advice": advice_map,
                     "intake_uc": INTAKE_UC, "competition_uc": comp_uc}
            body = _json(event)
            next_hash = _chain(head, body)
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                         (seq, claim.capture.step, claim.capture.ref, digest,
                          body, head, next_hash))
            conn.execute("UPDATE account SET last_step=?, committed=?, owner_json=?, chain_head=? WHERE id=1",
                         (claim.capture.step, seq, _json(owner.export_state()), next_hash))
            if _fault_at == "before_commit":
                raise FaultInjected("test failure immediately before commit")
            conn.execute("COMMIT")
            if _fault_at == "after_commit":
                raise CommitAcknowledgmentLost("commit completed; resolve by lookup, do not retry")
            return _make_receipt(seq, claim, event, next_hash)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def open(self, *, claim: ObservationClaim, semantic_ref: str,
             evidence_ref: str, ttl_steps: int,
             _fault_at: str | None = None) -> CycleReceipt:
        return self._process(claim=claim,
                             request=_request("open", semantic_ref, evidence_ref, ttl_steps),
                             _fault_at=_fault_at)

    def observe(self, *, claim: ObservationClaim,
                _fault_at: str | None = None) -> CycleReceipt:
        return self._process(claim=claim, request=_request("observe"),
                             _fault_at=_fault_at)

    def lookup(self, *, capture_ref: str) -> CycleReceipt | None:
        """Read a confirmed cycle without performing another cognitive evaluation."""
        _ref(capture_ref, "capture ref")
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            self._verify(conn)
            row = conn.execute("SELECT seq,claim_digest,event_json,event_hash FROM events WHERE capture_ref=?",
                               (capture_ref,)).fetchone()
            if row is None:
                return None
            seq, digest, body, head = row
            e = json.loads(body)
            claim = _parse_claim(e["claim"])
            return _make_receipt(seq, claim, e, head)
        finally:
            conn.close()
