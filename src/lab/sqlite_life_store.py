"""Birth-only SQLite custody for a future transactional I0 (M-11 foundation).

This module is deliberately NOT wired to Stage10/11 run_step yet: doing so before
all owners and WorldBody publish as one unit would falsely certify M-11.
It provides a tested atomic primitive and a persistent unresolved-intent fence.
No Oracle, evaluation bench, snapshots of older lives or physics changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Callable, Mapping, Sequence
from unicodedata import normalize
from urllib.parse import quote

from .determinism import canonical_causal_bytes, sha256_hex
from .journal import GENESIS_HASH

_HEX = re.compile(r"[0-9a-f]{64}\Z")
_TERMINAL = frozenset({"dead", "technical_halt", "experiment_stopped"})
_LIFECYCLES = _TERMINAL | {"active", "safety_block"}
_SCHEMA = "i0-sqlite-life-custody-v1"


class RecoveryBlocked(RuntimeError):
    """No old live state may be loaded after an uncertain or terminal intent."""


@dataclass(frozen=True, slots=True)
class LifeReceipt:
    individual_id: str
    generation: int
    status: str
    journal_count: int
    journal_head: str
    state_hash: str
    pending_intent: bool

    @property
    def may_recover(self) -> bool:
        return self.status == "active" and not self.pending_intent


def _canonical_state(state: Mapping[str, object], identity: str) -> bytes:
    """Require enough explicit custodians for an eventual integrated consumer.

    Presence is not proof that every required cognitive owner was included.
    Full owner inventory and semantic restore will be a separate runtime gate.
    """
    if (
        not isinstance(state, Mapping)
        or state.get("individual_id") != identity
        or not isinstance(state.get("world"), Mapping)
        or not isinstance(state.get("scheduler"), Mapping)
        or not isinstance(state.get("owners"), Mapping)
        or not state["owners"]
    ):
        raise ValueError("state requires identity, world, scheduler and nonempty owners")
    return canonical_causal_bytes(state)


def _validate_identity(identity: str) -> None:
    if type(identity) is not str or not identity or normalize("NFC", identity) != identity:
        raise ValueError("a nonempty NFC individual identity is required")


class _TerminalSequence:
    """Validate the journal's irreversible terminal suffix at write and audit."""

    def __init__(self) -> None:
        self.pending: tuple[int, str] | None = None
        self.sealed = False

    def accept(self, event: Mapping[str, object]) -> None:
        if self.sealed:
            raise ValueError("terminal death: no occurrence after fatal closure")
        kind = event.get("kind")
        if self.pending is not None:
            data = event.get("data")
            if not (
                kind == "step_closed"
                and type(event.get("t_monde")) is int
                and event["t_monde"] == self.pending[0]
                and type(event.get("attempt_ref")) is str
                and event["attempt_ref"] == self.pending[1]
                and isinstance(data, Mapping)
                and data.get("outcome") == "dead"
                and type(data.get("applied_command_count")) is int
                and data["applied_command_count"] == 1
                and type(data.get("world_advance_count")) is int
                and data["world_advance_count"] == 1
            ):
                raise ValueError("terminal death requires its matching unique closure")
            self.pending = None
            self.sealed = True
            return
        if kind == "step_closed":
            data = event.get("data")
            if isinstance(data, Mapping) and data.get("outcome") == "dead":
                raise ValueError("terminal death closure without prior fatal receipt")
        if kind == "individual_death_confirmed":
            if (
                type(event.get("t_monde")) is not int
                or event["t_monde"] < 1
                or type(event.get("attempt_ref")) is not str
                or not event["attempt_ref"]
            ):
                raise ValueError("terminal death requires a valid world attempt")
            self.pending = (event["t_monde"], event["attempt_ref"])

    def finalize(self, status: str) -> None:
        if self.pending is not None:
            raise ValueError("terminal death is missing its technical closure")
        if status == "dead" and not self.sealed:
            raise ValueError("dead status without terminal death and closure")
        if self.sealed and status != "dead":
            raise ValueError("terminal death requires dead lifecycle status")


class SQLiteLifeLedger:
    """One SQLite WAL current generation plus append-only canonical occurrences.

    A committed intent is a durable *fence*, not proof of a physical effect.
    If a process dies before the corresponding state+journal COMMIT, reopening
    the last generation as active is forbidden. The operator may only halt it.

    SQLite atomicity covers ONLY data committed through this connection. A live
    WorldBody, Scheduler or memory owner must NEVER mutate publicly before
    a coordinated private candidate is committed and published.
    """

    def __init__(self, connection: sqlite3.Connection, *, path: str,
                 fault: Callable[[str], None] | None = None) -> None:
        # Process-lifetime owner lock: a second live writer cannot open the
        # same identity while the first runtime is between transactions.
        flags = os.O_CREAT | os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path + ".writer.lock", flags, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            connection.close()
            raise RecoveryBlocked("individual already has an active process writer") from exc
        self._lock_fd: int | None = fd
        self._db = connection
        self.path = path
        self._fault = fault
        self._poisoned = False

    @staticmethod
    def _connect(path: str) -> sqlite3.Connection:
        uri = "file:" + quote(path, safe="/") + "?mode=rw"
        db = sqlite3.connect(uri, uri=True, isolation_level=None, timeout=0.0)
        try:
            mode = db.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            if mode.lower() != "wal":
                raise RuntimeError("SQLite WAL mode was not enabled")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=0")
            if db.execute("PRAGMA synchronous").fetchone()[0] != 2:
                raise RuntimeError("SQLite FULL synchronous required")
        except BaseException:
            db.close()
            raise
        return db

    @classmethod
    def birth(cls, *, path: str, individual_id: str,
              initial_state: Mapping[str, object],
              fault: Callable[[str], None] | None = None) -> "SQLiteLifeLedger":
        _validate_identity(individual_id)
        if type(path) is not str or not os.path.isabs(path):
            raise ValueError("birth requires an absolute SQLite path")
        payload = _canonical_state(initial_state, individual_id)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o600)
        os.close(fd)
        directory = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        db = cls._connect(path)
        instance = cls(db, path=path, fault=fault)
        try:
            db.execute("BEGIN IMMEDIATE")
            db.executescript(
                """CREATE TABLE life_current (
                    slot INTEGER PRIMARY KEY CHECK(slot = 1),
                    schema_version TEXT NOT NULL,
                    individual_id TEXT NOT NULL,
                    generation INTEGER NOT NULL CHECK(generation >= 0),
                    status TEXT NOT NULL,
                    state_bytes BLOB NOT NULL,
                    state_hash TEXT NOT NULL,
                    journal_count INTEGER NOT NULL CHECK(journal_count >= 0),
                    journal_head TEXT NOT NULL
                );
                CREATE TABLE causal_occurrence (
                    idx INTEGER PRIMARY KEY CHECK(idx >= 0),
                    event_id TEXT NOT NULL UNIQUE,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE,
                    canonical_bytes BLOB NOT NULL
                );
                CREATE TABLE pending_intent (
                    slot INTEGER PRIMARY KEY CHECK(slot = 1),
                    individual_id TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    intent_ref TEXT NOT NULL
                );"""
            )
            # executescript performs an implicit COMMIT. Birth is never
            # recoverable until a complete genesis record exists; if the
            # process exits here, a later open fails closed.
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO life_current VALUES (1, ?, ?, 0, 'active', ?, ?, 0, ?)",
                (_SCHEMA, individual_id, payload, sha256_hex(payload), GENESIS_HASH),
            )
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            instance.close()
            raise
        return instance

    @classmethod
    def open_existing(cls, *, path: str,
                      expected_individual_id: str,
                      fault: Callable[[str], None] | None = None) -> "SQLiteLifeLedger":
        _validate_identity(expected_individual_id)
        if type(path) is not str or not os.path.isabs(path) or not Path(path).is_file():
            raise ValueError("existing SQLite life path required; never create a past identity")
        db = cls._connect(path)
        store = cls(db, path=path, fault=fault)
        try:
            receipt = store.audit()
            if receipt.individual_id != expected_individual_id:
                raise RecoveryBlocked("individual identity mismatch")
        except BaseException:
            store.close()
            raise
        return store

    @classmethod
    def audit_read_only(cls, *, path: str, expected_individual_id: str) -> LifeReceipt:
        """Consistent external snapshot without acquiring I0's writer lease.

        No live runtime, Oracle or evaluation bench is constructed. An in-flight
        commit is seen entirely before or entirely after, never half-updated.
        """
        _validate_identity(expected_individual_id)
        if type(path) is not str or not os.path.isabs(path) or not Path(path).is_file():
            raise ValueError("existing absolute SQLite audit path required")
        uri = "file:" + quote(path, safe="/") + "?mode=ro"
        db = sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5.0)
        try:
            db.execute("PRAGMA query_only=ON")
            db.execute("BEGIN")
            reader = object.__new__(cls)
            reader._db = db
            reader._poisoned = False
            receipt = reader.audit()
            if receipt.individual_id != expected_individual_id:
                raise RecoveryBlocked("individual identity mismatch")
            return receipt
        finally:
            if db.in_transaction:
                db.execute("ROLLBACK")
            db.close()

    def __enter__(self) -> "SQLiteLifeLedger":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._db.close()
        if self._lock_fd is not None:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            os.close(self._lock_fd)
            self._lock_fd = None

    def _pulse(self, point: str) -> None:
        if self._fault is not None:
            self._fault(point)

    def _ready(self) -> None:
        if self._poisoned:
            raise RecoveryBlocked("I/O/commit outcome uncertain; close and investigate")

    def audit(self) -> LifeReceipt:
        """Read and validate the latest current state AND every retained event."""
        row = self._db.execute(
            "SELECT schema_version, individual_id, generation, status, "
            "state_bytes, state_hash, journal_count, journal_head "
            "FROM life_current WHERE slot = 1"
        ).fetchone()
        if row is None:
            raise RecoveryBlocked("genesis is incomplete or absent")
        schema, identity, generation, status, data, digest, count, head = row
        if schema != _SCHEMA:
            raise RecoveryBlocked("unrecognized SQLite life schema")
        _validate_identity(identity)
        if type(generation) is not int or generation < 0 or status not in _LIFECYCLES:
            raise RecoveryBlocked("invalid current life generation/status")
        if not isinstance(data, bytes) or sha256_hex(data) != digest:
            raise RecoveryBlocked("current state checksum mismatch")
        try:
            decoded = json.loads(data.decode("utf-8"))
            if canonical_causal_bytes(decoded) != data:
                raise ValueError("noncanonical state")
            _canonical_state(decoded, identity)
        except (UnicodeError, ValueError, TypeError) as exc:
            raise RecoveryBlocked("current state encoding is invalid") from exc
        previous = GENESIS_HASH
        expected = 0
        terminal = _TerminalSequence()
        for idx, event_id, prev, event_hash, raw in self._db.execute(
            "SELECT idx, event_id, previous_hash, event_hash, canonical_bytes "
            "FROM causal_occurrence ORDER BY idx"
        ):
            if idx != expected or prev != previous or not isinstance(raw, bytes):
                raise RecoveryBlocked("missing/reordered causal occurrence")
            if type(event_id) is not str or not event_id or normalize("NFC", event_id) != event_id:
                raise RecoveryBlocked("invalid causal event identity")
            try:
                document = json.loads(raw.decode("utf-8"))
                if (
                    canonical_causal_bytes(document) != raw
                    or set(document) != {
                        "index", "event_id", "previous_hash", "event_hash", "causal_event"
                    }
                    or document["index"] != idx
                    or document["event_id"] != event_id
                    or document["previous_hash"] != prev
                    or document["event_hash"] != event_hash
                    or not isinstance(document["causal_event"], dict)
                ):
                    raise ValueError("invalid canonical record")
                payload = canonical_causal_bytes(
                    {"event_id": event_id, "causal_event": document["causal_event"]}
                )
            except (UnicodeError, TypeError, ValueError) as exc:
                raise RecoveryBlocked("invalid canonical causal occurrence") from exc
            try:
                terminal.accept(document["causal_event"])
            except ValueError as exc:
                raise RecoveryBlocked(str(exc)) from exc
            actual = sha256_hex(bytes.fromhex(previous) + payload)
            if not _HEX.fullmatch(event_hash) or actual != event_hash:
                raise RecoveryBlocked("causal chain checksum mismatch")
            previous = actual
            expected += 1
        try:
            terminal.finalize(status)
        except ValueError as exc:
            raise RecoveryBlocked(str(exc)) from exc
        if count != expected or head != previous:
            raise RecoveryBlocked("current state and causal journal are not atomic")
        intent = self._db.execute(
            "SELECT individual_id, generation, intent_ref "
            "FROM pending_intent WHERE slot = 1"
        ).fetchone()
        if intent is not None and (
            len(intent) != 3 or intent[0] != identity
            or intent[1] != generation + 1 or not intent[2]
        ):
            raise RecoveryBlocked("invalid durable pending intent fence")
        return LifeReceipt(identity, generation, status, count, head, digest, intent is not None)

    def recover_current_bytes(self, *, expected_individual_id: str) -> bytes:
        """Only latest committed nonterminal bytes, never a selectable snapshot.

        Full runtime reconstruction is intentionally NOT implemented here.
        """
        self._ready()
        receipt = self.audit()
        if receipt.individual_id != expected_individual_id:
            raise RecoveryBlocked("individual identity mismatch")
        if not receipt.may_recover:
            raise RecoveryBlocked("terminal or unresolved intent forbids resuming I0")
        return self._db.execute(
            "SELECT state_bytes FROM life_current WHERE slot = 1"
        ).fetchone()[0]

    def begin_intent(self, *, expected_generation: int, intent_ref: str) -> None:
        """Durably fence the identity BEFORE any potentially published effect."""
        self._ready()
        if type(intent_ref) is not str or not intent_ref or normalize("NFC", intent_ref) != intent_ref:
            raise ValueError("nonempty NFC intent_ref required")
        try:
            self._db.execute("BEGIN IMMEDIATE")
            receipt = self.audit()
            if (not receipt.may_recover or receipt.generation != expected_generation):
                raise RecoveryBlocked("stale generation or unresolved/terminal identity")
            self._db.execute(
                "INSERT INTO pending_intent VALUES (1, ?, ?, ?)",
                (receipt.individual_id, expected_generation + 1, intent_ref),
            )
            self._pulse("intent_before_commit")
            self._db.execute("COMMIT")
            self._pulse("intent_after_commit")
        except BaseException:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            self._poisoned = True
            raise

    def commit_generation(
        self, *, expected_generation: int, expected_head: str,
        intent_ref: str, current_state: Mapping[str, object],
        events: Sequence[Mapping[str, object]], status: str = "active",
    ) -> LifeReceipt:
        """One atomic commit of current state, causal suffix and terminal bit.

        The physical/cognitive candidate must remain private until this returns.
        Any exception poisons this handle, including an after-COMMIT exception.
        """
        self._ready()
        if status not in _LIFECYCLES:
            raise ValueError("invalid lifecycle status")
        try:
            self._db.execute("BEGIN IMMEDIATE")
            receipt = self.audit()
            pending = self._db.execute(
                "SELECT generation, intent_ref FROM pending_intent WHERE slot = 1"
            ).fetchone()
            if (
                receipt.status != "active"
                or receipt.generation != expected_generation
                or receipt.journal_head != expected_head
                or pending != (expected_generation + 1, intent_ref)
            ):
                raise RecoveryBlocked("stale or unowned current generation")
            payload = _canonical_state(current_state, receipt.individual_id)
            head = receipt.journal_head
            index = receipt.journal_count
            terminal = _TerminalSequence()
            if receipt.status == "dead":
                raise RecoveryBlocked("terminal life may not advance")
            for entry in events:
                if not isinstance(entry, Mapping):
                    raise ValueError("event must be a canonical journal entry mapping")
                raw = dict(entry)
                if set(raw) != {
                    "index", "event_id", "previous_hash", "event_hash", "causal_event"
                }:
                    raise ValueError("incomplete technical journal record")
                event_id, causal = raw["event_id"], raw["causal_event"]
                if (
                    type(raw["index"]) is not int or raw["index"] != index
                    or type(event_id) is not str or not event_id
                    or normalize("NFC", event_id) != event_id
                    or raw["previous_hash"] != head or not isinstance(causal, Mapping)
                ):
                    raise ValueError("invalid appended occurrence order or provenance")
                event_hash = sha256_hex(bytes.fromhex(head) + canonical_causal_bytes(
                    {"event_id": event_id, "causal_event": causal}
                ))
                if raw["event_hash"] != event_hash:
                    raise ValueError("technical journal hash mismatch")
                terminal.accept(causal)
                self._pulse("before_event_insert")
                self._db.execute(
                    "INSERT INTO causal_occurrence VALUES (?, ?, ?, ?, ?)",
                    (index, event_id, head, event_hash, canonical_causal_bytes(raw)),
                )
                self._pulse("after_event_insert")
                head = event_hash
                index += 1
            terminal.finalize(status)
            self._pulse("before_current_update")
            self._db.execute(
                "UPDATE life_current SET generation=?, status=?, state_bytes=?, "
                "state_hash=?, journal_count=?, journal_head=? WHERE slot=1",
                (expected_generation + 1, status, payload, sha256_hex(payload), index, head),
            )
            self._db.execute("DELETE FROM pending_intent WHERE slot=1")
            self._pulse("after_current_update")
            self._pulse("before_commit")
            self._db.execute("COMMIT")
            self._pulse("after_commit")
            return self.audit()
        except BaseException:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            self._poisoned = True
            raise

    def seal_uncertain(self) -> LifeReceipt:
        """Operator-side permanent halt; never reconstruct a partial event."""
        self._ready()
        receipt = self.audit()
        if not receipt.pending_intent:
            raise RecoveryBlocked("no unresolved intent to seal")
        try:
            self._db.execute("BEGIN IMMEDIATE")
            self._db.execute(
                "UPDATE life_current SET status='technical_halt' WHERE slot=1 AND status='active'"
            )
            self._db.execute("COMMIT")
        except BaseException:
            if self._db.in_transaction:
                self._db.execute("ROLLBACK")
            self._poisoned = True
            raise
        return self.audit()

    def export_canonical_journal(self) -> bytes:
        """Lossless export, including after death or technical halt."""
        self.audit()
        records = (bytes(row[0]) for row in self._db.execute(
            "SELECT canonical_bytes FROM causal_occurrence ORDER BY idx"
        ))
        return b"\n".join(records)
