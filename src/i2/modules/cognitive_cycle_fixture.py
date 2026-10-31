"""Inert I2 SQLite fixture: one atomic *synthetic* cognitive cycle.

The optional v2 mode extends the same single SQLite COMMIT across a mock
intention consultation, reconstruction, full-frame Competition advice and an
independent synthetic Action Control review and veto, debited from ONE local
UC balance. The original v1 cognition-only fixture remains supported.

This is NOT a living engine, real Scheduler, M11 WAL, physical Action Control,
first-person proof or motor command. External ports are simulated read-only
claims; do not attach this fixture to a living individual's UC account.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
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
from .action_control_boundary import ActionControlBoundary, SafetyFinding, ControlReview
from .action_control_custody_fixture import (
    _LocalLedger as _ControlLedger, _CaptureSafety, _RecordedSafety,
    _AcceptedCurrent, _RECEIPT_KEYS, _SAFETY_KEYS, _REVIEW_KEYS,
)

SCHEMA = "i2-unified-cognitive-cycle-fixture-v1"
CONTROL_SCHEMA = "i2-unified-cognitive-control-fixture-v2"
ZERO_HASH = "0" * 64
_FAULTS = frozenset({"after_intake_debit", "after_intention", "after_competition_debit",
                    "after_control_debit", "after_safety", "before_commit", "after_commit"})
_EVENT_FIELDS = frozenset({
    "seq", "claim", "claim_digest", "request", "intake_receipt_ref", "intention_kind",
    "owner_snapshot", "frame", "advice", "intake_uc", "competition_uc",
})
_CONTROL_EVENT_FIELDS = _EVENT_FIELDS | frozenset({
    "control_review", "control_receipt", "safety_finding", "control_uc",
})


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_json(value).encode("ascii")).hexdigest()


def _chain(previous: str, body: str, *, schema: str = SCHEMA) -> str:
    return sha256((schema + "\n" + previous + "\n" + body).encode("ascii")).hexdigest()


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
    control_status: str | None = None
    control_uc: int = 0
    control_receipt_ref: str | None = None
    control_suggested_candidate_ref: str | None = None
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
        control_status=None if data.get("control_review") is None else data["control_review"]["status"],
        control_uc=data.get("control_uc", 0),
        control_receipt_ref=(None if data.get("control_receipt") is None
                             else data["control_receipt"]["ref"]),
        control_suggested_candidate_ref=(None if data.get("control_review") is None
                                         else data["control_review"]["suggested_candidate_ref"]),
    )


class CognitiveCycleFixture:
    """Inert single-file atomic cognition demonstration, never a born life.

    No inter-ledger transaction is implied: this fixture owns one *synthetic*
    budget, a single local intention owner and the Competition proposal.
    """

    def __init__(self, *, path: Path, life_ref: str,
                 observation_source: ObservationSource,
                 valuation_source: ValuationSource,
                 current_source: object | None = None,
                 safety_source: object | None = None) -> None:
        self.path = Path(path)
        self.life_ref = _ref(life_ref, "synthetic life")
        if not callable(getattr(observation_source, "verify", None)):
            raise ValueError("observation source required")
        if not callable(getattr(valuation_source, "evaluate_batch", None)):
            raise ValueError("subjective value source required")
        if (current_source is None) != (safety_source is None):
            raise ValueError("both current and safety ports required for unified control mode")
        if current_source is not None:
            if not callable(getattr(current_source, "verify_current", None)):
                raise ValueError("independent current-capture source required")
            if not callable(getattr(safety_source, "check", None)):
                raise ValueError("independent safety veto source required")
        self.observation_source = observation_source
        self.valuation_source = valuation_source
        self.current_source = current_source
        self.safety_source = safety_source
        self.control_enabled = current_source is not None
        self.schema = CONTROL_SCHEMA if self.control_enabled else SCHEMA

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               observation_source: ObservationSource,
               valuation_source: ValuationSource,
               current_source: object | None = None,
               safety_source: object | None = None) -> CognitiveCycleFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("invalid synthetic UC capacity")
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source,
                  current_source=current_source, safety_source=safety_source)
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
            conn.execute("INSERT INTO identity VALUES (1,?,?,?)", (obj.schema, obj.life_ref, synthetic_uc))
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
               valuation_source: ValuationSource,
               current_source: object | None = None,
               safety_source: object | None = None) -> CognitiveCycleFixture:
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source,
                  current_source=current_source, safety_source=safety_source)
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
        if (meta is None or meta[:2] != (self.schema, self.life_ref) or
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
                    _chain(chain, body, schema=self.schema) != event_hash):
                raise ValueError("synthetic event chain mismatch")
            data = json.loads(body)
            if type(data) is not dict or set(data) != (_CONTROL_EVENT_FIELDS if self.control_enabled else _EVENT_FIELDS) or _json(data) != body:
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
            if self.control_enabled:
                if type(data["control_uc"]) is not int or data["control_uc"] < 0:
                    raise ValueError("malformed synthetic control UC cost")
                if transition is None:
                    if (data["control_review"] is not None or data["control_receipt"] is not None
                            or data["safety_finding"] is not None or data["control_uc"] != 0):
                        raise ValueError("rejected intention cannot publish safety review")
                else:
                    stored_review = data["control_review"]
                    stored_receipt = data["control_receipt"]
                    stored_finding = data["safety_finding"]
                    if (type(stored_review) is not dict or set(stored_review) != _REVIEW_KEYS
                            or (stored_receipt is not None and
                                (type(stored_receipt) is not dict or set(stored_receipt) != _RECEIPT_KEYS))
                            or (stored_finding is not None and
                                (type(stored_finding) is not dict or set(stored_finding) != _SAFETY_KEYS))):
                        raise ValueError("invalid stored synthetic safety records")
                    recorded_finding = SafetyFinding(**stored_finding) if stored_finding is not None else None
                    control_ledger = _ControlLedger(
                        conn=None, life_ref=self.life_ref, seq=seq, balance=balance,
                    ).bind_frame(frame)
                    review = ActionControlBoundary(
                        life_ref=self.life_ref, current_authority=_AcceptedCurrent(),
                        ledger=control_ledger, safety_authority=_RecordedSafety(recorded_finding),
                    ).review(frame=frame, advice=advice)
                    if (asdict(review) != stored_review or
                            (asdict(control_ledger.receipt) if control_ledger.receipt else None) != stored_receipt or
                            type(data["control_uc"]) is not int or
                            data["control_uc"] != control_ledger.spent or
                            review.motor_authority != "NONE"):
                        raise ValueError("synthetic Action Control replay or debit mismatch")
                    balance = control_ledger.remaining
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
            return {"schema": self.schema, "life_ref": self.life_ref,
                    "control_review_included": self.control_enabled,
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
            control_review, control_receipt, safety_finding, control_uc = None, None, None, 0
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
                if self.control_enabled:
                    # This is a read-only *synthetic* external freshness assertion,
                    # not a WorldBody lock or an M11 witness.
                    if self.current_source.verify_current(
                        life_ref=self.life_ref, frame=frame, advice=advice,
                    ) is not True:
                        raise ValueError("synthetic control context not current")
                    control_ledger = _ControlLedger(
                        conn=conn, life_ref=self.life_ref, seq=seq,
                        balance=balance, fault=_fault_at,
                    ).bind_frame(frame)
                    safety = _CaptureSafety(self.safety_source, fault=_fault_at)
                    review = ActionControlBoundary(
                        life_ref=self.life_ref, current_authority=_AcceptedCurrent(),
                        ledger=control_ledger, safety_authority=safety,
                    ).review(frame=frame, advice=advice)
                    # A fresh assertion immediately before publication only;
                    # no downstream right to act is minted by this fixture.
                    if self.current_source.verify_current(
                        life_ref=self.life_ref, frame=frame, advice=advice,
                    ) is not True:
                        raise ValueError("synthetic control context changed before commit")
                    if review.motor_authority != "NONE":
                        raise ValueError("motor authority never permitted")
                    control_review = asdict(review)
                    control_receipt = (asdict(control_ledger.receipt)
                                       if control_ledger.receipt is not None else None)
                    safety_finding = (asdict(safety.finding)
                                      if safety.finding is not None else None)
                    control_uc = control_ledger.spent
                    balance = control_ledger.remaining
            event = {"seq": seq, "claim": _claim_map(claim), "claim_digest": digest,
                     "request": request, "intake_receipt_ref": intake_ref,
                     "intention_kind": kind, "owner_snapshot": owner.export_state(),
                     "frame": frame_map, "advice": advice_map,
                     "intake_uc": INTAKE_UC, "competition_uc": comp_uc}
            if self.control_enabled:
                event.update(control_review=control_review,
                             control_receipt=control_receipt,
                             safety_finding=safety_finding, control_uc=control_uc)
            body = _json(event)
            next_hash = _chain(head, body, schema=self.schema)
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
