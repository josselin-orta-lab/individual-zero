"""I3 engineering-only two-phase step custody; NOT born-state M11 or a World.

A PREPARED step is persisted before a motor is attempted. A crash before its
post-paid-learning receipt is sealed permanently blocks automatic continuation.
Receipts are caller assertions, not measured physical evidence. A local hash
chain has no off-machine anti-rollback anchor. This module NEVER runs a life.
"""
from __future__ import annotations

from contextlib import closing
from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path
import re
import secrets
import sqlite3

from i3.runtime.birth_reservation import Reservation, inspect as inspect_birth

SCHEMA = "i3-engineering-step-ledger/v2"
ANCHOR_MODE = "SEPARATE_LOCAL_WITNESS_V1"
REMOTE_MODE = "REMOTE_MONOTONIC_ENGINEERING_V1"
LEGACY_MODE = "UNANCHORED"
INTENT_SCHEMA = "i3-engineering-step-intent/v1"
RECEIPT_SCHEMA = "i3-engineering-post-paid-learning/v1"
APP_ID = 0x4933534C  # I3SL
DB_NAME = "i3_engineering_steps.sqlite3"
HEX = re.compile(r"[0-9a-f]{64}\Z")
DEATH_CAUSES = {"zero_food", "zero_water", "zero_integrity"}
STATUS = "ENGINEERING_CUSTODY_ONLY_NO_M11"


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_json(value).encode("utf-8")).hexdigest()


def _integer(value: object, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum or value > 2**63 - 1:
        raise ValueError(f"invalid {name}")
    return value


def _hash(value: object, name: str) -> str:
    if type(value) is not str or HEX.fullmatch(value) is None:
        raise ValueError(f"invalid {name}")
    return value


def _body(value: object) -> list[float]:
    if type(value) not in (tuple, list) or len(value) != 5:
        raise ValueError("exact five-channel body required")
    if any(type(x) not in (int, float) or not isfinite(x) or x < 0 or x > 100
           for x in value):
        raise ValueError("invalid body channel")
    return list(value)


def _money(value: object) -> dict:
    if type(value) is not dict or set(value) != {"energy", "vigilance"}:
        raise ValueError("exact two-currency payment required")
    for amount in value.values():
        if type(amount) not in (int, float) or not isfinite(amount) or amount < 0:
            raise ValueError("nonnegative finite payment required")
    return dict(value)


def _intent(raw: object, seq: int, previous_body: list) -> dict:
    if type(raw) is not dict or set(raw) != {
            "schema", "tick_before", "body_before", "action", "param",
            "decision_work"}:
        raise ValueError("exact engineering step intent required")
    if (raw["schema"] != INTENT_SCHEMA or type(raw["tick_before"]) is not int
            or raw["tick_before"] != seq - 1):
        raise ValueError("stale or foreign step intent")
    if _body(raw["body_before"]) != previous_body:
        raise ValueError("prior post-paid-learning body does not match")
    if raw["action"] is not None and (
            type(raw["action"]) is not str or raw["action"] not in (
                "se_deplacer", "collecter", "manger", "boire", "dormir", "attendre")):
        raise ValueError("invalid motor action")
    if raw["param"] is not None and type(raw["param"]) is not str:
        raise ValueError("invalid motor parameter")
    if type(raw["decision_work"]) is not dict or set(raw["decision_work"]) != {
            "cycles", "simulated_steps", "memory_items", "replays"}:
        raise ValueError("invalid decision work")
    for key, value in raw["decision_work"].items():
        _integer(value, key)
    return {**raw, "body_before": _body(raw["body_before"])}


def _receipt(raw: object, seq: int, intent: dict, horizon: int) -> dict:
    if type(raw) is not dict or set(raw) != {
            "schema", "phase", "tick", "action", "param", "body_after_motor",
            "body_after_paid_learning", "decision_paid", "learning_paid",
            "death_causes", "world_state_sha256", "mind_state_sha256"}:
        raise ValueError("exact post-paid-learning receipt required")
    if (raw["schema"] != RECEIPT_SCHEMA or raw["phase"] != "POST_PAID_LEARNING"
            or type(raw["tick"]) is not int or raw["tick"] != seq or seq > horizon
            or raw["action"] != intent["action"]
            or raw["param"] != intent["param"]):
        raise ValueError("step/intent/phase mismatch")
    after_motor = _body(raw["body_after_motor"])
    after_learning = _body(raw["body_after_paid_learning"])
    _money(raw["decision_paid"])
    learned_cost = _money(raw["learning_paid"])
    # Learning is the second native payment, after the physical motor.
    # It cannot alter food, water or integrity and must debit E and V exactly.
    if (after_learning[1:4] != after_motor[1:4]
            or not isclose(after_learning[0],
                           after_motor[0] - learned_cost["energy"],
                           rel_tol=1e-10, abs_tol=1e-8)
            or not isclose(after_learning[4],
                           after_motor[4] - learned_cost["vigilance"],
                           rel_tol=1e-10, abs_tol=1e-8)):
        raise ValueError("post-learning body does not settle the two currencies")
    causes = raw["death_causes"]
    if (type(causes) is not list or len(causes) != len(set(causes))
            or any(type(c) is not str or c not in DEATH_CAUSES for c in causes)):
        raise ValueError("invalid terminal causes")
    required_causes = {name for name, i in (
        ("zero_food", 1), ("zero_water", 2), ("zero_integrity", 3))
        if after_motor[i] == 0}
    if set(causes) != required_causes:
        raise ValueError("death causes contradict physical motor body")
    if causes and (learned_cost["energy"] or learned_cost["vigilance"]):
        raise ValueError("postmortem cognition must not be charged")
    _hash(raw["world_state_sha256"], "world_state_sha256")
    _hash(raw["mind_state_sha256"], "mind_state_sha256")
    return raw


def _state(receipt: dict, horizon: int) -> str:
    if receipt["death_causes"]:
        return "DEAD"
    return "CENSORED" if receipt["tick"] == horizon else "OPEN"


def _path(directory: Path) -> Path:
    if directory.is_symlink() or not directory.is_dir():
        raise PermissionError("existing isolated engineering directory required")
    path = directory / DB_NAME
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise PermissionError("foreign or symlinked engineering ledger")
    return path


def _connection(directory: Path, *, mode: str):
    path = _path(Path(directory))
    if mode != "rwc" and not path.is_file():
        raise PermissionError("engineering step ledger does not exist")
    return sqlite3.connect(path.absolute().as_uri() + "?mode=" + mode,
                           uri=True, isolation_level=None, timeout=5)


def _check_schema(conn, *, create: bool) -> None:
    app = conn.execute("PRAGMA application_id").fetchone()[0]
    objects = conn.execute("SELECT type,name FROM sqlite_master WHERE "
                           "name NOT LIKE 'sqlite_%'").fetchall()
    if create:
        if app != 0 or objects:
            raise PermissionError("step ledger already exists or is foreign")
        conn.execute(f"PRAGMA application_id={APP_ID}")
        conn.execute("CREATE TABLE session (id INTEGER PRIMARY KEY CHECK(id=1), "
                     "identity TEXT NOT NULL, birth_index INTEGER NOT NULL, "
                     "horizon INTEGER NOT NULL, initial_body TEXT NOT NULL, "
                     "last_seq INTEGER NOT NULL, head TEXT NOT NULL, status TEXT NOT NULL, "
                     "witness_mode TEXT NOT NULL)")
        conn.execute("CREATE TABLE steps (seq INTEGER PRIMARY KEY, "
                     "prev_head TEXT NOT NULL, phase TEXT NOT NULL, "
                     "intent_json TEXT NOT NULL, receipt_json TEXT, step_head TEXT, "
                     "seal_token_hash TEXT)")
    elif app != APP_ID or set(objects) != {("table", "session"), ("table", "steps")}:
        raise PermissionError("foreign or structurally modified engineering ledger")


def _parse(text: str) -> object:
    data = json.loads(text)
    if _json(data) != text:
        raise PermissionError("noncanonical ledger record")
    return data


def _read(conn, *, allow_prepared: bool = False) -> dict:
    _check_schema(conn, create=False)
    rows = conn.execute("SELECT id,identity,birth_index,horizon,initial_body,"
                        "last_seq,head,status,witness_mode FROM session").fetchall()
    if len(rows) != 1 or rows[0][0] != 1:
        raise PermissionError("invalid unique session header")
    _, identity, index, horizon, first_body, last_seq, head, status, mode = rows[0]
    _hash(identity, "identity")
    _integer(index, "birth_index")
    _integer(horizon, "horizon", minimum=1)
    _integer(last_seq, "last_seq")
    if (last_seq > horizon or status not in ("OPEN", "DEAD", "CENSORED")
            or mode not in (ANCHOR_MODE, LEGACY_MODE, REMOTE_MODE)):
        raise PermissionError("invalid session terminal/sequence")
    initial_body = _body(_parse(first_body))
    previous = _digest({"schema": SCHEMA, "identity": identity,
                        "birth_index": index, "horizon": horizon,
                        "initial_body": initial_body, "witness_mode": mode})
    expected_body = initial_body
    committed = []
    prepared = None
    for seq, prev, phase, it, rec, entry_head, seal_token_hash in conn.execute(
            "SELECT seq,prev_head,phase,intent_json,receipt_json,step_head,seal_token_hash "
            "FROM steps ORDER BY seq"):
        if type(seq) is not int or seq != len(committed) + 1 or seq > horizon:
            raise PermissionError("gap or duplicate engineering sequence")
        if prev != previous:
            raise PermissionError("broken previous-step hash link")
        intent = _intent(_parse(it), seq, expected_body)
        if phase == "PREPARED":
            if (prepared is not None or rec is not None or entry_head is not None
                    or type(seal_token_hash) is not str
                    or HEX.fullmatch(seal_token_hash) is None):
                raise PermissionError("invalid prepared record")
            prepared = {"seq": seq, "intent": intent, "prev_head": prev,
                        "seal_token_hash": seal_token_hash}
            continue
        if (prepared is not None or phase != "COMMITTED" or rec is None
                or seal_token_hash is not None):
            raise PermissionError("unsealed step occurs before committed step")
        receipt = _receipt(_parse(rec), seq, intent, horizon)
        computed = _digest({"schema": SCHEMA, "previous": prev,
                            "sequence": seq, "intent": intent, "receipt": receipt})
        if entry_head != computed:
            raise PermissionError("altered sealed step digest")
        committed.append({"seq": seq, "intent": intent, "receipt": receipt,
                          "head": computed})
        previous = computed
        expected_body = receipt["body_after_paid_learning"]
        if _state(receipt, horizon) != "OPEN" and seq < last_seq:
            raise PermissionError("step was committed after terminal")
    if len(committed) != last_seq or previous != head or (
            committed and status != _state(committed[-1]["receipt"], horizon)) or (
            not committed and status != "OPEN"):
        raise PermissionError("session head/status diverges from step chain")
    if prepared is not None and (prepared["seq"] != last_seq + 1
                                 or status != "OPEN"):
        raise PermissionError("prepared sequence inconsistent with header")
    if prepared is not None and not allow_prepared:
        raise PermissionError("uncertain prepared motor: fail-closed, no recovery")
    return {"schema": SCHEMA, "status": STATUS, "birth_index": index,
            "identity_sha256": identity, "horizon": horizon,
            "witness_mode": mode,
            "sequence": last_seq, "head_sha256": head, "terminal": status,
            "last_body": expected_body, "events": committed,
            "prepared": prepared, "durable_m11": False,
            "scientific_world_authorized": False}


def _bound(view: dict, claim: Reservation) -> None:
    if (view["identity_sha256"] != claim.identity_sha256
            or view["birth_index"] != claim.birth_index):
        raise PermissionError("reservation does not match engineering ledger")


def _check_claim(directory: Path, claim: Reservation) -> None:
    if type(claim) is not Reservation:
        raise ValueError("typed engineering reservation required")
    existing = inspect_birth(directory, claim.birth_index)
    if (existing["identity_sha256"] != claim.identity_sha256
            or existing["life_seed"] != claim.life_seed
            or existing["source_sha256"] != claim.source_sha256
            or existing["world_sha256"] != claim.world_sha256
            or existing["genome_sha256"] != claim.genome_sha256):
        raise PermissionError("source/world/genome/seed claim mismatch")


def _write(directory: Path, work):
    try:
        with closing(_connection(directory, mode="rw")) as conn:
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                out = work(conn)
                conn.execute("COMMIT")
                return out
            except BaseException:
                conn.execute("ROLLBACK")
                raise
    except (sqlite3.DatabaseError, json.JSONDecodeError, TypeError,
            ValueError) as exc:
        raise PermissionError("corrupt or conflicting engineering step ledger") from exc


def initialize(directory: Path, claim: Reservation, *, horizon: int,
               initial_body: list | tuple,
               witness_mode: str = LEGACY_MODE) -> dict:
    """Initialize local engineering custody after a separate consumed birth claim."""
    _integer(horizon, "horizon", minimum=1)
    if witness_mode not in (ANCHOR_MODE, LEGACY_MODE, REMOTE_MODE):
        raise ValueError("unknown engineering witness mode")
    body = _body(initial_body)
    if any(body[i] == 0 for i in (1, 2, 3)):
        raise ValueError("cannot initialize a live ledger with a dead body")
    _check_claim(directory, claim)
    try:
        with closing(_connection(directory, mode="rwc")) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("BEGIN IMMEDIATE")
            try:
                _check_schema(conn, create=True)
                head = _digest({"schema": SCHEMA, "identity": claim.identity_sha256,
                                "birth_index": claim.birth_index, "horizon": horizon,
                                "initial_body": body, "witness_mode": witness_mode})
                conn.execute("INSERT INTO session VALUES (1,?,?,?,?,?,?,?,?)",
                             (claim.identity_sha256, claim.birth_index, horizon,
                              _json(body), 0, head, "OPEN", witness_mode))
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
    except (sqlite3.DatabaseError, ValueError) as exc:
        raise PermissionError("cannot initialize I3 engineering step ledger") from exc
    return inspect(directory, claim)


def inspect(directory: Path, claim: Reservation) -> dict:
    """Cold read: full-chain validation; refuses an uncertain PREPARED motor."""
    _check_claim(directory, claim)
    try:
        with closing(_connection(directory, mode="ro")) as conn:
            view = _read(conn)
    except (sqlite3.DatabaseError, ValueError, TypeError,
            json.JSONDecodeError) as exc:
        raise PermissionError("corrupted engineering ledger") from exc
    _bound(view, claim)
    return view


def inspect_pending(directory: Path, claim: Reservation) -> dict:
    """Read a pending intent ONLY for pre-motor witness synchronization.

    This does not grant permission to resume or to re-execute an uncertain
    motor. Ordinary public inspect() continues to refuse pending steps.
    """
    _check_claim(directory, claim)
    try:
        with closing(_connection(directory, mode="ro")) as conn:
            view = _read(conn, allow_prepared=True)
    except (sqlite3.DatabaseError, ValueError, TypeError,
            json.JSONDecodeError) as exc:
        raise PermissionError("corrupted pending engineering ledger") from exc
    _bound(view, claim)
    return view


def prepare(directory: Path, claim: Reservation, *, expected_head: str,
            intent: dict) -> dict:
    """Persist one pre-motor intent. Incomplete state poisons continuation."""
    _check_claim(directory, claim)
    _hash(expected_head, "expected_head")

    def operation(conn):
        view = _read(conn)
        _bound(view, claim)
        if view["terminal"] != "OPEN" or view["head_sha256"] != expected_head:
            raise PermissionError("stale writer or terminal session")
        seq = view["sequence"] + 1
        if seq > view["horizon"]:
            raise PermissionError("horizon already reached")
        safe_intent = _intent(intent, seq, view["last_body"])
        token = secrets.token_hex(32)  # never stored in plaintext; lose on crash
        token_hash = sha256(token.encode("ascii")).hexdigest()
        conn.execute("INSERT INTO steps VALUES (?,?,'PREPARED',?,NULL,NULL,?)",
                     (seq, view["head_sha256"], _json(safe_intent), token_hash))
        return {"status": "PREPARED_UNCERTAIN_MOTOR", "sequence": seq,
                "prior_head_sha256": expected_head, "recoverable": False,
                "seal_token": token}

    return _write(directory, operation)


def seal(directory: Path, claim: Reservation, *, expected_head: str,
         seal_token: str, receipt: dict) -> dict:
    """Atomically settle a prepared receipt and head AFTER paid learning."""
    _check_claim(directory, claim)
    _hash(expected_head, "expected_head")
    if type(seal_token) is not str or re.fullmatch(r"[0-9a-f]{64}", seal_token) is None:
        raise PermissionError("missing or invalid in-process seal token")

    def operation(conn):
        view = _read(conn, allow_prepared=True)
        _bound(view, claim)
        pending = view["prepared"]
        if pending is None or view["head_sha256"] != expected_head:
            raise PermissionError("no matching prepared intent or stale writer")
        if sha256(seal_token.encode("ascii")).hexdigest() != pending["seal_token_hash"]:
            raise PermissionError("prepared step belongs to another process or attempt")
        seq = pending["seq"]
        record = _receipt(receipt, seq, pending["intent"], view["horizon"])
        event_head = _digest({"schema": SCHEMA, "previous": expected_head,
                              "sequence": seq, "intent": pending["intent"],
                              "receipt": record})
        terminal = _state(record, view["horizon"])
        conn.execute("UPDATE steps SET phase='COMMITTED', receipt_json=?, step_head=?, "
                     "seal_token_hash=NULL "
                     "WHERE seq=? AND phase='PREPARED'",
                     (_json(record), event_head, seq))
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            raise PermissionError("prepared step changed concurrently")
        conn.execute("UPDATE session SET last_seq=?, head=?, status=? WHERE id=1",
                     (seq, event_head, terminal))
        return {"schema": SCHEMA, "status": STATUS, "sequence": seq,
                "head_sha256": event_head, "terminal": terminal,
                "durable_m11": False, "scientific_world_authorized": False}

    return _write(directory, operation)
