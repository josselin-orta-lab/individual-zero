"""Separate-local-directory, two-phase I3 rollback witness (engineering ONLY).

If the I3 ledger is rolled back *without* rolling back this separately stored
witness, its old head cannot be resumed. The witness is not external, signed,
M11, globally monotonic or safe from a common-mode rollback of BOTH stores.

PREPARED witness is durable before any genuine native World.step is allowed.
A crash between ledger PREPARED and witness PREPARED leaves the ledger blocked;
a crash between witness PREPARED and witness COMMITTED leaves the witness
blocked. Never guess whether the motor executed in either case.
"""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

from i3.runtime.birth_reservation import Reservation
from i3.runtime.engineering_step_ledger import inspect, inspect_pending

APP_ID = 0x49335754  # I3WT
DB_NAME = "i3_engineering_witness.sqlite3"
SCHEMA = "i3-separate-local-rollback-witness/v1"
MODE = "SEPARATE_LOCAL_WITNESS_V1"
STATUS = "LOCAL_ROLLBACK_DETECTION_ONLY_NOT_M11"
HEX = re.compile(r"[0-9a-f]{64}\Z")


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False)


def _hash(value):
    return sha256(_json(value).encode("utf-8")).hexdigest()


def _root(anchor_directory: Path, ledger_directory: Path) -> Path:
    root, ledger = Path(anchor_directory), Path(ledger_directory)
    if root.is_symlink() or not root.is_dir() or ledger.is_symlink() or not ledger.is_dir():
        raise PermissionError("preexisting non-symlink engineering directories required")
    trusted, living = root.resolve(), ledger.resolve()
    if (trusted == living or trusted in living.parents or
            living in trusted.parents):
        raise PermissionError("rollback witness must have a nonnested storage directory")
    path = root / DB_NAME
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise PermissionError("foreign/symlink witness database")
    return path


def validate_location(anchor_directory: Path, ledger_directory: Path) -> None:
    """Reject a shared/symlinked storage root before consuming a birth slot."""
    _root(anchor_directory, ledger_directory)


def _conn(anchor_directory: Path, ledger_directory: Path, mode: str):
    path = _root(anchor_directory, ledger_directory)
    if mode != "rwc" and not path.is_file():
        raise PermissionError("rollback witness does not exist")
    return sqlite3.connect(path.absolute().as_uri() + "?mode=" + mode,
                           uri=True, isolation_level=None, timeout=5)


def _schema(conn, *, create=False):
    app = conn.execute("PRAGMA application_id").fetchone()[0]
    objects = set(conn.execute("SELECT type,name FROM sqlite_master "
                               "WHERE name NOT LIKE 'sqlite_%'").fetchall())
    if create:
        if app != 0 or objects:
            raise PermissionError("witness already initialized or foreign")
        conn.execute(f"PRAGMA application_id={APP_ID}")
        conn.execute("CREATE TABLE witness ("
                     "id INTEGER PRIMARY KEY CHECK(id=1), "
                     "schema TEXT NOT NULL, identity TEXT NOT NULL, "
                     "source TEXT NOT NULL, world TEXT NOT NULL, "
                     "genome TEXT NOT NULL, seed INTEGER NOT NULL, "
                     "birth_index INTEGER NOT NULL, horizon INTEGER NOT NULL, "
                     "sequence INTEGER NOT NULL, head TEXT NOT NULL, "
                     "phase TEXT NOT NULL, terminal TEXT NOT NULL, "
                     "pending_sequence INTEGER, pending_intent TEXT)")
    elif app != APP_ID or objects != {("table", "witness")}:
        raise PermissionError("foreign/modified witness schema")


def _read(conn):
    _schema(conn)
    rows = conn.execute("SELECT schema,identity,source,world,genome,seed,"
                        "birth_index,horizon,sequence,head,phase,terminal,"
                        "pending_sequence,pending_intent FROM witness WHERE id=1").fetchall()
    if len(rows) != 1 or conn.execute("SELECT count(*) FROM witness").fetchone()[0] != 1:
        raise PermissionError("missing or duplicate rollback witness")
    (schema, identity, source, world, genome, seed, index, horizon, sequence,
     head, phase, terminal, pending_seq, pending_intent) = rows[0]
    if schema != SCHEMA or any(type(h) is not str or HEX.fullmatch(h) is None
                               for h in (identity, source, world, genome, head)):
        raise PermissionError("wrong witness identity/schema/hash")
    if (type(seed) is not int or not 0 <= seed <= 2**63 - 1
            or type(index) is not int or not 0 <= index <= 2**63 - 1
            or type(horizon) is not int or not 1 <= horizon <= 100
            or type(sequence) is not int or not 0 <= sequence <= horizon
            or terminal not in ("OPEN", "DEAD", "CENSORED")
            or phase not in ("COMMITTED", "PREPARED")):
        raise PermissionError("invalid witness header")
    if phase == "PREPARED":
        if (terminal != "OPEN" or type(pending_seq) is not int
                or pending_seq != sequence + 1 or pending_seq > horizon
                or type(pending_intent) is not str
                or HEX.fullmatch(pending_intent) is None):
            raise PermissionError("invalid prepared witness")
    elif pending_seq is not None or pending_intent is not None:
        raise PermissionError("committed witness retains unresolved intent")
    return {"identity": identity, "source": source, "world": world,
            "genome": genome, "seed": seed, "birth_index": index,
            "horizon": horizon, "sequence": sequence, "head": head,
            "phase": phase, "terminal": terminal,
            "pending_sequence": pending_seq, "pending_intent": pending_intent}


def _bound(witness, claim: Reservation, ledger):
    if (type(claim) is not Reservation or
            witness["identity"] != claim.identity_sha256 or
            witness["source"] != claim.source_sha256 or
            witness["world"] != claim.world_sha256 or
            witness["genome"] != claim.genome_sha256 or
            witness["seed"] != claim.life_seed or
            witness["birth_index"] != claim.birth_index or
            witness["horizon"] != ledger["horizon"] or
            ledger["witness_mode"] != MODE):
        raise PermissionError("witness not bound to exact engineering birth")


def _transaction(anchor_directory, ledger_directory, action):
    try:
        with closing(_conn(anchor_directory, ledger_directory, "rw")) as conn:
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                result = action(conn)
                conn.execute("COMMIT")
                return result
            except BaseException:
                conn.execute("ROLLBACK")
                raise
    except (sqlite3.Error, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise PermissionError("witness storage or custody mismatch") from exc


def register(anchor_directory, ledger_directory, claim: Reservation, ledger) -> dict:
    """Register exactly one empty engineering genesis in a *separate* store."""
    if (ledger["sequence"] != 0 or ledger["terminal"] != "OPEN"
            or ledger["prepared"] is not None or ledger["witness_mode"] != MODE):
        raise PermissionError("witness may only register an empty reserved ledger")
    if type(claim) is not Reservation:
        raise PermissionError("engineering reservation required")
    try:
        with closing(_conn(anchor_directory, ledger_directory, "rwc")) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                _schema(conn, create=True)
                conn.execute("INSERT INTO witness VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                             (SCHEMA, claim.identity_sha256, claim.source_sha256,
                              claim.world_sha256, claim.genome_sha256,
                              claim.life_seed, claim.birth_index, ledger["horizon"],
                              0, ledger["head_sha256"], "COMMITTED", "OPEN", None, None))
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
    except (sqlite3.Error, ValueError, TypeError) as exc:
        raise PermissionError("cannot initialize separate engineering witness") from exc
    return verify(anchor_directory, ledger_directory, claim, ledger)


def verify(anchor_directory, ledger_directory, claim: Reservation, ledger=None):
    """Check against an independent local snapshot. Reject any pending phase."""
    if ledger is None:
        ledger = inspect(ledger_directory, claim)
    try:
        with closing(_conn(anchor_directory, ledger_directory, "ro")) as conn:
            witness = _read(conn)
    except (sqlite3.Error, ValueError, TypeError) as exc:
        raise PermissionError("invalid rollback witness") from exc
    _bound(witness, claim, ledger)
    if (witness["phase"] != "COMMITTED" or
            witness["sequence"] != ledger["sequence"] or
            witness["head"] != ledger["head_sha256"] or
            witness["terminal"] != ledger["terminal"]):
        raise PermissionError("witness rejects rollback, pending motor, or stale ledger")
    return {"status": STATUS, "sequence": witness["sequence"],
            "head_sha256": witness["head"], "terminal": witness["terminal"],
            "durable_m11": False, "off_host_monotonic": False}


def prepared(anchor_directory, ledger_directory, claim: Reservation,
             *, previous_ledger: dict, intent: dict):
    """Publish PREPARED witness AFTER ledger PREPARED, BEFORE any motor."""
    current = inspect_pending(ledger_directory, claim)
    pending = current["prepared"]
    if (pending is None or current["head_sha256"] != previous_ledger["head_sha256"]
            or current["sequence"] != previous_ledger["sequence"]
            or pending["seq"] != current["sequence"] + 1
            or pending["intent"] != intent):
        raise PermissionError("ledger PREPARED intent is inconsistent")
    expected = _hash({"schema": SCHEMA, "identity": claim.identity_sha256,
                      "seq": pending["seq"], "previous": current["head_sha256"],
                      "intent": intent})

    def action(conn):
        witness = _read(conn)
        _bound(witness, claim, current)
        if (witness["phase"] != "COMMITTED" or witness["terminal"] != "OPEN"
                or witness["sequence"] != previous_ledger["sequence"]
                or witness["head"] != previous_ledger["head_sha256"]):
            raise PermissionError("stale or terminal local witness")
        conn.execute("UPDATE witness SET phase='PREPARED',pending_sequence=?,"
                     "pending_intent=? WHERE id=1 AND phase='COMMITTED'",
                     (pending["seq"], expected))
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise PermissionError("witness was concurrently modified")
        return {"status": "WITNESSED_PREPARED_NO_MOTOR_RECEIPT", "sequence": pending["seq"]}

    return _transaction(anchor_directory, ledger_directory, action)


def committed(anchor_directory, ledger_directory, claim: Reservation,
              *, previous_ledger: dict, intent: dict):
    """Advance the witness only after the native ledger fully COMMITTED."""
    ledger = inspect(ledger_directory, claim)
    if (ledger["sequence"] != previous_ledger["sequence"] + 1
            or not ledger["events"] or ledger["events"][-1]["intent"] != intent):
        raise PermissionError("no exactly-next committed original")
    fingerprint = _hash({"schema": SCHEMA, "identity": claim.identity_sha256,
                         "seq": ledger["sequence"],
                         "previous": previous_ledger["head_sha256"],
                         "intent": intent})

    def action(conn):
        witness = _read(conn)
        _bound(witness, claim, ledger)
        if (witness["phase"] != "PREPARED" or
                witness["sequence"] != previous_ledger["sequence"] or
                witness["head"] != previous_ledger["head_sha256"] or
                witness["pending_sequence"] != ledger["sequence"] or
                witness["pending_intent"] != fingerprint):
            raise PermissionError("prepared witness lost or mismatched")
        conn.execute("UPDATE witness SET sequence=?,head=?,phase='COMMITTED',"
                     "terminal=?,pending_sequence=NULL,pending_intent=NULL "
                     "WHERE id=1 AND phase='PREPARED'",
                     (ledger["sequence"], ledger["head_sha256"], ledger["terminal"]))
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise PermissionError("witness commit raced")
        return {"status": STATUS, "sequence": ledger["sequence"],
                "head_sha256": ledger["head_sha256"], "terminal": ledger["terminal"],
                "durable_m11": False, "off_host_monotonic": False}

    return _transaction(anchor_directory, ledger_directory, action)
