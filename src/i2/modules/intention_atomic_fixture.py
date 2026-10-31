"""ACID *fixture* for I2 intention custody. No living engine or M11 authority.

A single SQLite transaction debits a **synthetic** UC account, evaluates the
existing pure semantic-intention owner, and publishes its state and audit row.
An external observation port must approve a committed first-person claim, but
its honesty is not established here. The source verification is read-only and
must not itself consume state. This fixture is deliberately NOT an adapter for
IntentionIngress's external UC debit port, which cannot share this COMMIT.

The hash chain is an accidental-corruption witness, NOT a signed external
anchor or a substitute for M11. Reopening a fixture is not recovery of a life.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3

from .intention_continuity import (
    FirstPersonCapture, IntentionContinuity, POLICY, _ref,
)
from .intention_ingress import (
    INTAKE_OPERATION, INTAKE_UC, ObservationAuthority, ObservationClaim,
)

SCHEMA = "i2-atomic-intention-fixture-v1"
ZERO_HASH = "0" * 64
_EVENT_FIELDS = frozenset({
    "seq", "claim", "claim_digest", "request", "receipt_ref", "kind",
    "owner_snapshot", "owner_digest", "units",
})
_CLAIM_FIELDS = frozenset({
    "life_ref", "source_event_ref", "subjective_evidence_refs", "capture",
})
_CAPTURE_FIELDS = frozenset({
    "step", "ref", "goal_ref", "accessible_semantics", "contradicted_semantics",
})
_REQUEST_FIELDS = frozenset({"method", "semantic_ref", "evidence_ref", "ttl_steps"})
_FAULTS = frozenset({"after_debit", "after_policy", "before_commit", "after_commit"})


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":"))


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode("ascii")).hexdigest()


def _chain(previous: str, event_json: str) -> str:
    return sha256((SCHEMA + "\n" + previous + "\n" + event_json).encode("ascii")).hexdigest()


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


def _receipt_ref(life_ref: str, digest: str, seq: int) -> str:
    return "fixture:uc:" + sha256(
        (SCHEMA + "\x1f" + life_ref + "\x1f" + str(seq) + "\x1f" + digest).encode("ascii")
    ).hexdigest()


def _apply_policy(owner: IntentionContinuity, claim: ObservationClaim,
                  request: dict[str, object], receipt_ref: str) -> str:
    try:
        if request["method"] == "open":
            result = owner.open(capture=claim.capture,
                                semantic_ref=request["semantic_ref"],
                                evidence_ref=request["evidence_ref"],
                                ttl_steps=request["ttl_steps"], work_ref=receipt_ref)
        else:
            result = owner.observe(capture=claim.capture, work_ref=receipt_ref)
        return result.kind
    except ValueError:
        # A validated, *paid* but disallowed cognitive request gets an audit
        # row. It consumes the physical capture and is not refunded/retried.
        return "policy_rejected"


@dataclass(frozen=True, slots=True)
class FixtureReceipt:
    """A test fixture record, NEVER a Scheduler or M11 UC receipt."""
    seq: int
    capture_ref: str
    claim_digest: str
    receipt_ref: str
    kind: str
    units: int
    owner_digest: str
    chain_head: str


class FaultInjected(RuntimeError):
    """Deliberate software fault before SQLite COMMIT; not a power-cut test."""


class CommitAcknowledgmentLost(RuntimeError):
    """COMMIT succeeded but caller did not receive the normal acknowledgment."""


class AtomicIntentionFixture:
    """One synthetic-life SQLite proof of atomic UC debit and owner update.

    This cannot mint a living identity, a motor candidate or an M11 state.
    Every operation uses BEGIN IMMEDIATE; failures before COMMIT roll back.
    A lost acknowledgment after COMMIT must be resolved with lookup(), NOT
    by re-running a possibly paid cognitive computation.
    """

    def __init__(self, *, path: Path, life_ref: str,
                 observation_authority: ObservationAuthority) -> None:
        self._path = Path(path)
        self.life_ref = _ref(life_ref, "fixture life ref")
        if not callable(getattr(observation_authority, "verify", None)):
            raise ValueError("independent read-only observation source required")
        self._source = observation_authority

    @classmethod
    def create(cls, *, path: Path, life_ref: str, synthetic_uc: int,
               observation_authority: ObservationAuthority) -> AtomicIntentionFixture:
        if type(synthetic_uc) is not int or not 0 <= synthetic_uc <= 1000000:
            raise ValueError("invalid synthetic budget")
        obj = cls(path=path, life_ref=life_ref,
                  observation_authority=observation_authority)
        if obj._path.is_symlink() or not obj._path.parent.is_dir():
            raise ValueError("invalid fixture location")
        # Fail closed rather than overwriting another fixture.
        fd = os.open(obj._path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        os.close(fd)
        try:
            conn = obj._connect()
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=FULL")
                conn.executescript("""
                    CREATE TABLE identity (
                        id INTEGER PRIMARY KEY CHECK(id = 1),
                        schema_id TEXT NOT NULL, life_ref TEXT NOT NULL,
                        policy TEXT NOT NULL, synthetic_capacity INTEGER NOT NULL
                    );
                    CREATE TABLE account (
                        id INTEGER PRIMARY KEY CHECK(id = 1),
                        remaining_uc INTEGER NOT NULL CHECK(remaining_uc >= 0),
                        consumed_step INTEGER NOT NULL,
                        consumed_capture_ref TEXT,
                        owner_json TEXT NOT NULL, chain_head TEXT NOT NULL,
                        committed INTEGER NOT NULL
                    );
                    CREATE TABLE events (
                        seq INTEGER PRIMARY KEY, step INTEGER NOT NULL UNIQUE,
                        capture_ref TEXT NOT NULL UNIQUE,
                        claim_digest TEXT NOT NULL UNIQUE,
                        event_json TEXT NOT NULL,
                        previous_hash TEXT NOT NULL,
                        event_hash TEXT NOT NULL UNIQUE
                    );
                """)
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("INSERT INTO identity VALUES (1, ?, ?, ?, ?)",
                             (SCHEMA, obj.life_ref, POLICY, synthetic_uc))
                conn.execute("INSERT INTO account VALUES (1, ?, -1, NULL, ?, ?, 0)",
                             (synthetic_uc, _canonical(IntentionContinuity().export_state()), ZERO_HASH))
                conn.execute("COMMIT")
            finally:
                conn.close()
        except Exception:
            # This directory is disposable test data, never an individual's WAL.
            # The caller owns cleanup of sidecars when initialization fails.
            raise
        obj.audit()
        return obj

    @classmethod
    def reopen(cls, *, path: Path, life_ref: str,
               observation_authority: ObservationAuthority) -> AtomicIntentionFixture:
        obj = cls(path=path, life_ref=life_ref,
                  observation_authority=observation_authority)
        if obj._path.is_symlink() or not obj._path.is_file():
            raise ValueError("missing or linked fixture; cannot recreate")
        obj.audit()
        return obj

    def _connect(self, *, readonly: bool = False) -> sqlite3.Connection:
        # mode=rw/ro explicitly rejects absent database creation.
        uri = self._path.resolve().as_uri() + ("?mode=ro" if readonly else "?mode=rw")
        conn = sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5.0)
        conn.execute("PRAGMA busy_timeout=5000")
        if not readonly:
            # Connection-local setting: WAL durability requires FULL on every writer.
            conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _verify(self, conn: sqlite3.Connection) -> tuple[int, int, str, IntentionContinuity, int]:
        """Replay the entire synthetic chain without consulting external authority."""
        meta = conn.execute("SELECT schema_id, life_ref, policy, synthetic_capacity FROM identity WHERE id=1").fetchone()
        if (meta is None or meta[0:3] != (SCHEMA, self.life_ref, POLICY)
                or type(meta[3]) is not int or meta[3] < 0):
            raise ValueError("fixture identity/schema mismatch")
        account = conn.execute("SELECT remaining_uc, consumed_step, consumed_capture_ref, owner_json, chain_head, committed FROM account WHERE id=1").fetchone()
        if account is None:
            raise ValueError("fixture account absent")
        remaining, last_step, last_capture, owner_json, head, count = account
        if (any(type(v) is not int for v in (remaining, last_step, count))
                or type(meta[3]) is not int
                or type(owner_json) is not str or type(head) is not str):
            raise ValueError("invalid fixture account types")
        owner = IntentionContinuity()
        previous = ZERO_HASH
        observed_step = -1
        observed_capture = None
        n = 0
        for seq, step, capture_ref, claim_digest, text, old, recorded in conn.execute(
            "SELECT seq, step, capture_ref, claim_digest, event_json, previous_hash, event_hash FROM events ORDER BY seq"
        ):
            n += 1
            if seq != n or old != previous or _chain(old, text) != recorded:
                raise ValueError("broken fixture event chain")
            e = json.loads(text)
            if type(e) is not dict or set(e) != _EVENT_FIELDS or _canonical(e) != text:
                raise ValueError("noncanonical fixture event")
            c = _parse_claim(e["claim"])
            request = e["request"]
            if type(request) is not dict or set(request) != _REQUEST_FIELDS:
                raise ValueError("invalid fixture operation")
            request = _request(**request)
            digest = c.digest()
            if (c.life_ref != self.life_ref or c.capture.step <= observed_step
                    or c.capture.ref == observed_capture
                    or c.capture.step != step or c.capture.ref != capture_ref
                    or e["seq"] != seq or claim_digest != digest
                    or e["claim_digest"] != digest or e["units"] != INTAKE_UC
                    or e["receipt_ref"] != _receipt_ref(self.life_ref, digest, seq)):
                raise ValueError("fixture event fields inconsistent")
            if request["method"] == "open" and request["evidence_ref"] not in c.subjective_evidence_refs:
                raise ValueError("unobserved origin evidence")
            kind = _apply_policy(owner, c, request, e["receipt_ref"])
            snapshot = owner.export_state()
            if e["kind"] != kind or e["owner_snapshot"] != snapshot or e["owner_digest"] != _digest(snapshot):
                raise ValueError("fixture policy replay mismatch")
            previous, observed_step, observed_capture = recorded, step, capture_ref
        if (head != previous or count != n or remaining != meta[3] - n * INTAKE_UC
                or last_step != observed_step or last_capture != observed_capture
                or _canonical(owner.export_state()) != owner_json):
            raise ValueError("fixture account/custody mismatch")
        return remaining, observed_step, head, owner, n

    def audit(self) -> dict[str, object]:
        """Untrusted local integrity assessment; cannot authenticate M11."""
        if self._path.is_symlink() or not self._path.is_file():
            raise ValueError("fixture missing or linked")
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            remaining, step, head, owner, count = self._verify(conn)
            return {"schema": SCHEMA, "life_ref": self.life_ref,
                    "committed": count, "remaining_synthetic_uc": remaining,
                    "last_consumed_step": step, "chain_head": head,
                    "intention": owner.export_state()["current"],
                    "m11_authenticated": False, "real_scheduler_uc": False,
                    "motor_authority": False}
        finally:
            conn.close()

    def _process(self, *, claim: ObservationClaim, request: dict[str, object],
                 fault_at: str | None = None) -> FixtureReceipt:
        if fault_at is not None and fault_at not in _FAULTS:
            raise ValueError("unrecognized test fault location")
        if type(claim) is not ObservationClaim:
            raise ValueError("observation claim required")
        claim.validate()
        if claim.life_ref != self.life_ref:
            raise ValueError("foreign fixture life")
        if request["method"] == "open" and request["evidence_ref"] not in claim.subjective_evidence_refs:
            raise ValueError("origin evidence is not in subjective claim")
        digest = claim.digest()
        # Port must be a *read-only* source of already committed first-person
        # evidence. Here tests use a synthetic allowlist; this is not M11.
        attested = self._source.verify(life_ref=self.life_ref, claim=claim, digest=digest)
        if attested is not True:
            raise ValueError("source did not attest the synthetic observation")
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            remaining, step, head, owner, count = self._verify(conn)
            if claim.capture.step <= step or conn.execute(
                "SELECT 1 FROM events WHERE capture_ref=? OR claim_digest=?",
                (claim.capture.ref, digest),
            ).fetchone():
                raise ValueError("consumed, replayed or stale capture")
            if remaining < INTAKE_UC:
                raise ValueError("synthetic UC exhausted")
            # Nothing about owner cognition is evaluated until the *same*
            # ACID transaction has debited the synthetic UC account.
            conn.execute("UPDATE account SET remaining_uc=remaining_uc-? WHERE id=1",
                         (INTAKE_UC,))
            if fault_at == "after_debit":
                raise FaultInjected("injected before owner consideration")
            seq = count + 1
            ticket = _receipt_ref(self.life_ref, digest, seq)
            kind = _apply_policy(owner, claim, request, ticket)
            state = owner.export_state()
            if fault_at == "after_policy":
                raise FaultInjected("injected after owner consideration")
            event = {"seq": seq, "claim": _claim_map(claim), "claim_digest": digest,
                     "request": request, "receipt_ref": ticket, "kind": kind,
                     "owner_snapshot": state, "owner_digest": _digest(state),
                     "units": INTAKE_UC}
            event_json = _canonical(event)
            next_hash = _chain(head, event_json)
            conn.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (seq, claim.capture.step, claim.capture.ref, digest,
                          event_json, head, next_hash))
            conn.execute("UPDATE account SET consumed_step=?, consumed_capture_ref=?, owner_json=?, chain_head=?, committed=? WHERE id=1",
                         (claim.capture.step, claim.capture.ref, _canonical(state), next_hash, seq))
            if fault_at == "before_commit":
                raise FaultInjected("injected before COMMIT")
            conn.execute("COMMIT")
            if fault_at == "after_commit":
                raise CommitAcknowledgmentLost("COMMIT succeeded; inspect existing receipt")
            return FixtureReceipt(seq, claim.capture.ref, digest, ticket, kind,
                                  INTAKE_UC, event["owner_digest"], next_hash)
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    def open(self, *, claim: ObservationClaim, semantic_ref: str,
             evidence_ref: str, ttl_steps: int,
             _fault_at: str | None = None) -> FixtureReceipt:
        return self._process(claim=claim, request=_request(
            "open", semantic_ref, evidence_ref, ttl_steps), fault_at=_fault_at)

    def observe(self, *, claim: ObservationClaim,
                _fault_at: str | None = None) -> FixtureReceipt:
        return self._process(claim=claim, request=_request("observe"), fault_at=_fault_at)

    def lookup(self, *, capture_ref: str) -> FixtureReceipt | None:
        """Resolve a lost COMMIT acknowledgment without charging again."""
        _ref(capture_ref, "capture ref")
        conn = self._connect(readonly=True)
        try:
            conn.execute("BEGIN")
            self._verify(conn)
            row = conn.execute("SELECT seq, claim_digest, event_json, event_hash FROM events WHERE capture_ref=?",
                               (capture_ref,)).fetchone()
            if row is None:
                return None
            seq, digest, text, head = row
            event = json.loads(text)
            return FixtureReceipt(seq, capture_ref, digest, event["receipt_ref"],
                                  event["kind"], event["units"], event["owner_digest"], head)
        finally:
            conn.close()
