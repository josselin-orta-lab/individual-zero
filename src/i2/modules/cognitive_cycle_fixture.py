"""I2 inert unified SQLite research fixture, one schema only.

One local synthetic transaction owns intention, Competition UC, Action Control
review, and an absorbing synthetic terminal marker. Cognition-only v1,
optional-control v2 and former v3 layouts are no longer accepted: there is
no migration, compatibility branch or physical actuation.

This is NOT a living engine, Scheduler, WorldBody, M11, or independent
birth/death authority. External attestations remain synthetic test ports.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from typing import Protocol

from .intention_continuity import FirstPersonCapture, IntentionContinuity, IntentionTransition, _ref
from .intention_ingress import ObservationClaim, INTAKE_UC
from .option_reconstruction import reconstruct_candidates, CandidateFrame
from .competition_preview import (
    CompetitionPreview, CompetitionReceipt, SubjectiveValuation,
    OPERATION, UC_PER_CANDIDATE, _frame,
)
from .action_control_boundary import (
    ActionControlBoundary, ControlReceipt, SafetyFinding, ControlReview,
    CONTROL_OPERATION, CONTROL_UC,
)

SCHEMA = "i2-unified-cognitive-lifecycle-fixture-v4"
ZERO_HASH = "0" * 64
_FAULTS = frozenset({"after_intake_debit", "after_intention", "after_competition_debit",
                    "after_control_debit", "after_safety", "before_commit", "after_commit"})
_EVENT_FIELDS = frozenset({
    "seq", "claim", "claim_digest", "request", "intake_receipt_ref", "intention_kind",
    "owner_snapshot", "frame", "advice", "intake_uc", "competition_uc",
    "control_review", "control_receipt", "safety_finding", "control_uc",
})
_TERMINAL_FIELDS = frozenset({
    "kind", "seq", "life_ref", "genesis_ref", "physical_step",
    "terminal_ref", "evidence_ref",
})
_TERMINAL_FAULTS = frozenset({"after_insert", "before_commit", "after_commit"})

# Serialization belongs to the one v4 journal, never to obsolete ledgers.
_CLAIM_FIELDS = frozenset({"life_ref", "source_event_ref", "subjective_evidence_refs", "capture"})
_CAPTURE_FIELDS = frozenset({
    "step", "ref", "goal_ref", "accessible_semantics", "contradicted_semantics",
})
_VALUE_KEYS = frozenset({"candidate_ref", "receipt_ref", "evidence_ref", "value"})
_RECEIPT_KEYS = frozenset(ControlReceipt.__dataclass_fields__)
_SAFETY_KEYS = frozenset(SafetyFinding.__dataclass_fields__)
_REVIEW_KEYS = frozenset({
    "frame_ref", "capture_ref", "physical_step", "status",
    "suggested_candidate_ref", "control_receipt_ref", "safety_evidence_ref",
    "motor_authority",
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


# V4-owned serialization/replay helpers, formerly hosted by three retired SQLite fixtures.
def _claim_map(claim: ObservationClaim) -> dict[str, object]:
    claim.validate()
    c = claim.capture
    return {
        "life_ref": claim.life_ref, "source_event_ref": claim.source_event_ref,
        "subjective_evidence_refs": list(claim.subjective_evidence_refs),
        "capture": {
            "step": c.step, "ref": c.ref, "goal_ref": c.goal_ref,
            "accessible_semantics": list(c.accessible_semantics),
            "contradicted_semantics": list(c.contradicted_semantics),
        },
    }


def _parse_claim(payload: object) -> ObservationClaim:
    if type(payload) is not dict or set(payload) != _CLAIM_FIELDS:
        raise ValueError("invalid claim schema")
    c = payload["capture"]
    if type(c) is not dict or set(c) != _CAPTURE_FIELDS:
        raise ValueError("invalid capture schema")
    if any(type(c[key]) is not list for key in
           ("accessible_semantics", "contradicted_semantics")):
        raise ValueError("invalid capture sequences")
    if type(payload["subjective_evidence_refs"]) is not list:
        raise ValueError("invalid evidence sequence")
    claim = ObservationClaim(
        life_ref=payload["life_ref"],
        source_event_ref=payload["source_event_ref"],
        subjective_evidence_refs=tuple(payload["subjective_evidence_refs"]),
        capture=FirstPersonCapture(
            step=c["step"], ref=c["ref"], goal_ref=c["goal_ref"],
            accessible_semantics=tuple(c["accessible_semantics"]),
            contradicted_semantics=tuple(c["contradicted_semantics"]),
        ),
    )
    claim.validate()
    return claim


def _request(method: str, semantic_ref: str | None = None,
             evidence_ref: str | None = None, ttl_steps: int | None = None) -> dict[str, object]:
    if method not in ("open", "observe"):
        raise ValueError("invalid intention method")
    if method == "open":
        _ref(semantic_ref, "semantic ref")
        _ref(evidence_ref, "evidence ref")
        if type(ttl_steps) is not int or not 1 <= ttl_steps <= 64:
            raise ValueError("invalid intention TTL")
    elif any(x is not None for x in (semantic_ref, evidence_ref, ttl_steps)):
        raise ValueError("observe takes no additional intention proposal")
    return {"method": method, "semantic_ref": semantic_ref,
            "evidence_ref": evidence_ref, "ttl_steps": ttl_steps}

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

def _advice_map(advice: CompetitionAdvice) -> dict[str, object]:
    return {"status": advice.status,
            "suggested_candidate_ref": advice.suggested_candidate_ref,
            "evaluated_candidate_refs": list(advice.evaluated_candidate_refs),
            "receipt_refs": list(advice.receipt_refs),
            "values": [{"candidate_ref": v.candidate_ref, "receipt_ref": v.receipt_ref,
                        "evidence_ref": v.evidence_ref, "value": v.value}
                       for v in advice.valuation_records]}

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

def _control_ref(life: str, frame: CandidateFrame, candidate: str, seq: int) -> str:
    return "synthetic:control:" + _digest([SCHEMA, life, frame.frame_ref,
                                        frame.claim_digest, candidate, seq])

class _AcceptedCurrent:
    """For local replay only. NOT M11 authentication."""
    def verify_current(self, *, life_ref: str, frame: CandidateFrame,
                       advice: CompetitionAdvice) -> bool:
        return True


class _ControlLedger:
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

    def bind_frame(self, frame: CandidateFrame) -> _ControlLedger:
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

class ObservationSource(Protocol):
    def verify(self, *, life_ref: str, claim: ObservationClaim, digest: str) -> bool: ...


class ValuationSource(Protocol):
    def evaluate_batch(self, *, frame: CandidateFrame,
                       receipts: tuple[CompetitionReceipt, ...]) -> tuple[SubjectiveValuation, ...]: ...


class TerminalSource(Protocol):
    """Caller-supplied terminal claim; tests use a mock, not WorldBody/M11."""
    def verify_terminal(self, *, life_ref: str, genesis_ref: str,
                        physical_step: int, terminal_ref: str, evidence_ref: str,
                        previous_head: str) -> bool: ...


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


@dataclass(frozen=True, slots=True)
class SyntheticTerminalReceipt:
    """Local seal receipt, NOT authenticated death or a physical operation."""

    seq: int
    life_ref: str
    genesis_ref: str
    physical_step: int
    terminal_ref: str
    evidence_ref: str
    chain_head: str
    motor_authority: str = "NONE"


def _terminal_record(*, seq: int, life_ref: str, genesis_ref: str,
                     physical_step: int, terminal_ref: str,
                     evidence_ref: str) -> dict[str, object]:
    return {"kind": "synthetic_terminal", "seq": seq, "life_ref": life_ref,
            "genesis_ref": genesis_ref, "physical_step": physical_step,
            "terminal_ref": terminal_ref, "evidence_ref": evidence_ref}


def _terminal_receipt(record: dict[str, object], head: str) -> SyntheticTerminalReceipt:
    return SyntheticTerminalReceipt(
        seq=record["seq"], life_ref=record["life_ref"],
        genesis_ref=record["genesis_ref"], physical_step=record["physical_step"],
        terminal_ref=record["terminal_ref"], evidence_ref=record["evidence_ref"],
        chain_head=head)


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
        control_status=None if data["control_review"] is None else data["control_review"]["status"],
        control_uc=data["control_uc"],
        control_receipt_ref=(None if data["control_receipt"] is None
                             else data["control_receipt"]["ref"]),
        control_suggested_candidate_ref=(None if data["control_review"] is None
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
                 current_source: object, safety_source: object,
                 genesis_ref: str, terminal_source: TerminalSource) -> None:
        self.path = Path(path)
        self.life_ref = _ref(life_ref, "synthetic life")
        self.genesis_ref = _ref(genesis_ref, "caller-declared synthetic genesis")
        if (not callable(getattr(observation_source, "verify", None)) or
                not callable(getattr(valuation_source, "evaluate_batch", None)) or
                not callable(getattr(current_source, "verify_current", None)) or
                not callable(getattr(safety_source, "check", None)) or
                not callable(getattr(terminal_source, "verify_terminal", None))):
            raise ValueError("all synthetic observation, control and terminal ports required")
        self.observation_source = observation_source
        self.valuation_source = valuation_source
        self.current_source = current_source
        self.safety_source = safety_source
        self.terminal_source = terminal_source
        self.schema = SCHEMA

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               observation_source: ObservationSource,
               valuation_source: ValuationSource,
               current_source: object, safety_source: object,
               genesis_ref: str, terminal_source: TerminalSource) -> CognitiveCycleFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("invalid synthetic UC capacity")
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source,
                  current_source=current_source, safety_source=safety_source,
                  genesis_ref=genesis_ref, terminal_source=terminal_source)
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
            conn.execute("""CREATE TABLE lifecycle (
                id INTEGER PRIMARY KEY CHECK(id=1),
                genesis_ref TEXT NOT NULL, terminal_step INTEGER,
                terminal_ref TEXT, terminal_digest TEXT, terminal_hash TEXT)""")
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO identity VALUES (1,?,?,?)", (obj.schema, obj.life_ref, synthetic_uc))
            conn.execute("INSERT INTO lifecycle VALUES (1,?,NULL,NULL,NULL,NULL)",
                         (obj.genesis_ref,))
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
               current_source: object, safety_source: object,
               genesis_ref: str, terminal_source: TerminalSource) -> CognitiveCycleFixture:
        obj = cls(path=path, life_ref=life_ref,
                  observation_source=observation_source, valuation_source=valuation_source,
                  current_source=current_source, safety_source=safety_source,
                  genesis_ref=genesis_ref, terminal_source=terminal_source)
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

    def _lifecycle(self, conn: sqlite3.Connection) -> tuple | None:
        row = conn.execute(
            "SELECT genesis_ref, terminal_step, terminal_ref, terminal_digest, terminal_hash "
            "FROM lifecycle WHERE id=1"
        ).fetchone()
        if row is None or row[0] != self.genesis_ref:
            raise ValueError("synthetic genesis identity mismatch")
        if row[1] is None and any(field is not None for field in row[2:]):
            raise ValueError("partial synthetic terminal marker")
        if row[1] is not None and any(field is None for field in row[2:]):
            raise ValueError("incomplete synthetic terminal marker")
        return row

    def _verify(self, conn: sqlite3.Connection) -> tuple[int, int, int, str, IntentionContinuity]:
        meta = conn.execute("SELECT schema_id, life_ref, capacity FROM identity WHERE id=1").fetchone()
        if (meta is None or meta[:2] != (self.schema, self.life_ref) or
                type(meta[2]) is not int or not 0 <= meta[2] <= 1000000):
            raise ValueError("synthetic life identity or schema mismatch")
        account = conn.execute("SELECT remaining_uc,last_step,committed,owner_json,chain_head "
                               "FROM account WHERE id=1").fetchone()
        if account is None:
            raise ValueError("synthetic state absent")
        lifecycle_row = self._lifecycle(conn)
        terminal_seen = None
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
            if terminal_seen is not None:
                raise ValueError("events after synthetic terminal seal")
            data = json.loads(body)
            if type(data) is dict and data.get("kind") == "synthetic_terminal":
                if set(data) != _TERMINAL_FIELDS or _json(data) != body:
                    raise ValueError("noncanonical terminal event")
                _ref(data["terminal_ref"], "terminal event reference")
                _ref(data["evidence_ref"], "terminal evidence reference")
                if (not data["terminal_ref"].startswith("terminal:") or
                        data["life_ref"] != self.life_ref or
                        data["genesis_ref"] != self.genesis_ref or
                        type(data["physical_step"]) is not int or
                        step != data["physical_step"] or step <= last_step or
                        ref != data["terminal_ref"] or
                        data["seq"] != seq or _digest(data) != digest):
                    raise ValueError("synthetic terminal identity or chronology mismatch")
                terminal_seen = (step, ref, digest, event_hash)
                chain, last_step = event_hash, step
                capture_refs.add(ref)
                digests.add(digest)
                continue
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
        expected = None if terminal_seen is None else terminal_seen
        actual = None if lifecycle_row[1] is None else lifecycle_row[1:]
        if expected != actual:
            raise ValueError("terminal marker and journal disagree")
        if account != (balance, last_step, count, _json(owner.export_state()), chain):
            raise ValueError("synthetic account, intention or head mismatch")
        return balance, last_step, count, chain, owner

    def audit(self) -> dict[str, object]:
        """Read-only full-policy replay, not a signed record or M11 attestation."""
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            remaining, step, count, head, owner = self._verify(conn)
            report = {"schema": self.schema, "life_ref": self.life_ref,
                    "control_review_included": True,
                    "remaining_synthetic_uc": remaining, "last_step": step,
                    "committed": count, "chain_head": head,
                    "intention": owner.export_state()["current"],
                    "m11_authenticated": False, "scheduler_uc_authenticated": False,
                    "motor_authority": "NONE"}
            row = self._lifecycle(conn)
            report.update(genesis_ref=self.genesis_ref,
                          synthetic_terminal=row[1] is not None,
                          terminal_step=row[1], terminal_ref=row[2],
                          physiological_death_attested=False)
            return report
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
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            balance, last_step, count, head, owner = self._verify(conn)
            if self._lifecycle(conn)[1] is not None:
                raise ValueError("terminal synthetic identity cannot process cognition")
            if claim.capture.ref.startswith("terminal:"):
                raise ValueError("terminal event reference cannot be a capture")
            if self.observation_source.verify(
                    life_ref=self.life_ref, claim=claim, digest=digest) is not True:
                raise ValueError("unattested synthetic observation")
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

    def seal_terminal(self, *, physical_step: int, terminal_ref: str,
                      evidence_ref: str, _fault_at: str | None = None) -> SyntheticTerminalReceipt:
        """Append an irreversible *local synthetic* terminal marker in one COMMIT.

        Never calls a real physiology owner; the injected test port has no M11
        authority. Reopening this database is for inspection, never rebirth.
        """
        if _fault_at is not None and _fault_at not in _TERMINAL_FAULTS:
            raise ValueError("unsupported terminal test fault")
        if type(physical_step) is not int or physical_step < 0:
            raise ValueError("invalid terminal step")
        terminal_ref = _ref(terminal_ref, "terminal reference")
        evidence_ref = _ref(evidence_ref, "terminal evidence")
        if not terminal_ref.startswith("terminal:"):
            raise ValueError("terminal ref must use dedicated namespace")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            balance, last_step, count, head, owner = self._verify(conn)
            if self._lifecycle(conn)[1] is not None:
                raise ValueError("synthetic terminal seal already committed")
            if physical_step <= last_step:
                raise ValueError("terminal step must follow the last committed step")
            if self.terminal_source.verify_terminal(
                    life_ref=self.life_ref, genesis_ref=self.genesis_ref,
                    physical_step=physical_step, terminal_ref=terminal_ref,
                    evidence_ref=evidence_ref, previous_head=head) is not True:
                raise ValueError("synthetic terminal source not attested")
            seq = count + 1
            event = _terminal_record(
                seq=seq, life_ref=self.life_ref, genesis_ref=self.genesis_ref,
                physical_step=physical_step, terminal_ref=terminal_ref,
                evidence_ref=evidence_ref)
            body = _json(event)
            digest = _digest(event)
            next_hash = _chain(head, body, schema=self.schema)
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                         (seq, physical_step, terminal_ref, digest, body, head, next_hash))
            conn.execute("UPDATE account SET last_step=?, committed=?, chain_head=? WHERE id=1",
                         (physical_step, seq, next_hash))
            conn.execute("UPDATE lifecycle SET terminal_step=?, terminal_ref=?, "
                         "terminal_digest=?, terminal_hash=? WHERE id=1",
                         (physical_step, terminal_ref, digest, next_hash))
            if _fault_at == "after_insert":
                raise FaultInjected("terminal seal inserted but COMMIT not reached")
            if _fault_at == "before_commit":
                raise FaultInjected("terminal seal not yet committed")
            conn.execute("COMMIT")
            if _fault_at == "after_commit":
                raise CommitAcknowledgmentLost("terminal seal committed; inspect, do not reseal")
            return _terminal_receipt(event, next_hash)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def terminal_lookup(self) -> SyntheticTerminalReceipt | None:
        """Read-only terminal resolution, never authorizing process resumption."""
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            self._verify(conn)
            row = self._lifecycle(conn)
            if row[1] is None:
                return None
            body = conn.execute(
                "SELECT event_json FROM events WHERE capture_ref=?", (row[2],)
            ).fetchone()[0]
            return _terminal_receipt(json.loads(body), row[4])
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
            if e.get("kind") == "synthetic_terminal":
                raise ValueError("terminal record has no cognitive receipt")
            claim = _parse_claim(e["claim"])
            return _make_receipt(seq, claim, e, head)
        finally:
            conn.close()
