"""Standalone I3 engineering CAS authority: independently hosted ONLY if deployed so.

This reference process is local loopback test instrumentation. Its SQLite DB
must live on a separate host and on protected, independently managed storage
before it could support actual off-host anti-rollback. No scientific World,
engine registration, M11 credential authority or production service is created.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import re
import sqlite3

from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import SCHEMA, canonical

APP_ID = 0x4933524D  # I3RM
HEX = re.compile(r"[0-9a-f]{64}\Z")
DB_SCHEMA = "i3-remote-cas-authority-store/v2"
AUDIT_SCHEMA = "i3-remote-cas-authority-audit/v1"

_ROW_KEYS = ("claim_json", "horizon", "sequence", "head", "phase",
             "terminal", "pending_seq", "pending_intent")


def _hex(item):
    if type(item) is not str or HEX.fullmatch(item) is None:
        raise ValueError("64-character lowercase hex digest required")
    return item


def _integer(item, minimum=0, maximum=2**63-1):
    if type(item) is not int or not minimum <= item <= maximum:
        raise ValueError("bounded integer required")
    return item


def _claim(item):
    if type(item) is not dict or set(item) != {
            "identity_sha256", "source_sha256", "genome_sha256", "world_sha256",
            "life_seed", "birth_index"}:
        raise ValueError("invalid claim shape")
    birth = make_reservation(birth_index=_integer(item["birth_index"]),
                             life_seed=_integer(item["life_seed"]),
                             source_sha256=_hex(item["source_sha256"]),
                             world_sha256=_hex(item["world_sha256"]),
                             genome_sha256=_hex(item["genome_sha256"]))
    if birth.identity_sha256 != _hex(item["identity_sha256"]):
        raise ValueError("birth identity fingerprint mismatch")
    return item



def _audit_event(identity: str, operation: str, row: tuple) -> dict:
    """Deterministic state transition, kept separate from the live CAS row."""
    return {"schema": AUDIT_SCHEMA, "identity": identity,
            "operation": operation, "state": dict(zip(_ROW_KEYS, row))}


def _audit_hash(previous: str, payload: str) -> str:
    return sha256((previous + "\n" + payload).encode("utf-8")).hexdigest()



class AuthorityStore:
    """Local backend for a separately run service, with one SQLite CAS writer."""

    def __init__(self, database: Path, authority_id: str):
        self.database = Path(database)
        self.authority_id = _hex(authority_id)
        if (not self.database.parent.is_dir() or self.database.parent.is_symlink()
                or self.database.is_symlink() or
                (self.database.exists() and not self.database.is_file())):
            raise PermissionError("separate authority database path invalid")
        with closing(sqlite3.connect(self.database, isolation_level=None, timeout=5)) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=FULL")
            c.execute("BEGIN IMMEDIATE")
            try:
                app = c.execute("PRAGMA application_id").fetchone()[0]
                objects = set(c.execute("SELECT type,name FROM sqlite_master "
                                        "WHERE name NOT LIKE 'sqlite_%'").fetchall())
                if app == 0 and not objects:
                    c.execute(f"PRAGMA application_id={APP_ID}")
                    c.execute("CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK (id=1), "
                              "schema TEXT NOT NULL, authority_id TEXT NOT NULL)")
                    c.execute("INSERT INTO metadata VALUES (1,?,?)", (DB_SCHEMA, authority_id))
                    c.execute("CREATE TABLE histories ("
                              "identity TEXT PRIMARY KEY, claim_json TEXT NOT NULL, "
                              "horizon INTEGER NOT NULL, sequence INTEGER NOT NULL, "
                              "head TEXT NOT NULL, phase TEXT NOT NULL, "
                              "terminal TEXT NOT NULL, pending_seq INTEGER, "
                              "pending_intent TEXT)")
                    c.execute("CREATE TABLE audit ("
                              "ordinal INTEGER PRIMARY KEY, "
                              "previous_sha256 TEXT NOT NULL, "
                              "event_json TEXT NOT NULL, "
                              "event_sha256 TEXT NOT NULL)")
                elif (app != APP_ID or objects != {("table", "metadata"),
                                                   ("table", "histories"),
                                                   ("table", "audit")}
                      or c.execute("SELECT schema,authority_id FROM metadata "
                                   "WHERE id=1").fetchall() != [(DB_SCHEMA, authority_id)]):
                    raise PermissionError("foreign or mismatched remote authority store")
                self._check_audit(c)  # startup: never run on tampered partial history
                c.execute("COMMIT")
            except BaseException:
                c.execute("ROLLBACK")
                raise

    def _genesis(self) -> str:
        # Deliberately public: this is local consistency, NOT an off-host anchor.
        return sha256(("I3RM-v2-local-audit:" + self.authority_id).encode()).hexdigest()

    def _append_audit(self, conn, identity: str, operation: str, row: tuple) -> None:
        previous = conn.execute(
            "SELECT ordinal,event_sha256 FROM audit ORDER BY ordinal DESC LIMIT 1"
        ).fetchone()
        ordinal = 1 if previous is None else previous[0] + 1
        previous_sha = self._genesis() if previous is None else previous[1]
        event = canonical(_audit_event(identity, operation, row)).decode("utf-8")
        conn.execute("INSERT INTO audit VALUES (?,?,?,?)",
                     (ordinal, previous_sha, event, _audit_hash(previous_sha, event)))

    def _check_audit(self, conn) -> None:
        """Check every transition AND the final stored state, fail closed.

        Full scans are intentional at this bounded research stage. O(total events)
        per command is not a production throughput claim, and full-db rollback
        can still consistently remove BOTH the event chain and live head.
        """
        objects = set(conn.execute("SELECT type,name FROM sqlite_master "
                                   "WHERE name NOT LIKE 'sqlite_%'").fetchall())
        metadata = conn.execute("SELECT schema,authority_id FROM metadata "
                                "WHERE id=1").fetchall()
        if (conn.execute("PRAGMA application_id").fetchone()[0] != APP_ID
                or objects != {("table", "metadata"), ("table", "histories"),
                               ("table", "audit")}
                or metadata != [(DB_SCHEMA, self.authority_id)]):
            raise PermissionError("authority schema or identity changed after initialization")
        expected_prev = self._genesis()
        latest = {}
        rows = conn.execute("SELECT ordinal,previous_sha256,event_json,event_sha256 "
                            "FROM audit ORDER BY ordinal").fetchall()
        for expected_ordinal, (ordinal, previous, payload, digest) in enumerate(rows, 1):
            if (type(ordinal) is not int or ordinal != expected_ordinal
                    or previous != expected_prev
                    or type(payload) is not str
                    or digest != _audit_hash(previous, payload)):
                raise PermissionError("remote audit transition chain is inconsistent")
            try:
                event = json.loads(payload)
                if (canonical(event).decode("utf-8") != payload
                        or type(event) is not dict
                        or set(event) != {"schema", "identity", "operation", "state"}
                        or event["schema"] != AUDIT_SCHEMA
                        or type(event["identity"]) is not str
                        or not HEX.fullmatch(event["identity"])
                        or event["operation"] not in ("register", "prepare", "commit")
                        or type(event["state"]) is not dict
                        or set(event["state"]) != set(_ROW_KEYS)):
                    raise ValueError("bad remote audit event shape")
            except (ValueError, TypeError, KeyError) as exc:
                raise PermissionError("remote audit event invalid") from exc
            identity, operation, state = event["identity"], event["operation"], event["state"]
            old = latest.get(identity)
            if (type(state["claim_json"]) is not str
                    or type(state["horizon"]) is not int
                    or not 1 <= state["horizon"] <= 100
                    or type(state["sequence"]) is not int
                    or not 0 <= state["sequence"] <= state["horizon"]
                    or type(state["head"]) is not str
                    or not HEX.fullmatch(state["head"])
                    or state["phase"] not in ("COMMITTED", "PREPARED")
                    or state["terminal"] not in ("OPEN", "DEAD", "CENSORED")):
                raise PermissionError("invalid audited remote state")
            if operation == "register":
                if (old is not None or state["sequence"] != 0
                        or state["phase"] != "COMMITTED"
                        or state["terminal"] != "OPEN"
                        or state["pending_seq"] is not None
                        or state["pending_intent"] is not None):
                    raise PermissionError("invalid remote genesis transition")
                try:
                    if canonical(_claim(json.loads(state["claim_json"]))).decode() != state["claim_json"]:
                        raise ValueError("noncanonical claim")
                    if json.loads(state["claim_json"])["identity_sha256"] != identity:
                        raise ValueError("claim identity mismatch")
                except (TypeError, KeyError, ValueError) as exc:
                    raise PermissionError("invalid audited claim") from exc
            elif operation == "prepare":
                if (old is None or old["phase"] != "COMMITTED"
                        or old["terminal"] != "OPEN"
                        or old["sequence"] >= old["horizon"]
                        or any(state[k] != old[k] for k in (
                            "claim_json", "horizon", "sequence", "head", "terminal"))
                        or state["phase"] != "PREPARED"
                        or type(state["pending_seq"]) is not int
                        or state["pending_seq"] != old["sequence"] + 1
                        or type(state["pending_intent"]) is not str
                        or not HEX.fullmatch(state["pending_intent"])):
                    raise PermissionError("invalid audited prepare transition")
            else:
                if (old is None or old["phase"] != "PREPARED"
                        or old["terminal"] != "OPEN"
                        or state["claim_json"] != old["claim_json"]
                        or state["horizon"] != old["horizon"]
                        or state["sequence"] != old["pending_seq"]
                        or state["sequence"] != old["sequence"] + 1
                        or state["phase"] != "COMMITTED"
                        or state["pending_seq"] is not None
                        or state["pending_intent"] is not None
                        or (state["sequence"] == state["horizon"]
                            and state["terminal"] == "OPEN")
                        or (state["sequence"] < state["horizon"]
                            and state["terminal"] == "CENSORED")):
                    raise PermissionError("invalid audited commit transition")
            latest[identity] = state
            expected_prev = digest
        current = {}
        for record in conn.execute("SELECT identity,claim_json,horizon,sequence,head,"
                                   "phase,terminal,pending_seq,pending_intent FROM histories"):
            identity, *state = record
            if identity in current:
                raise PermissionError("duplicate authority identity")
            current[identity] = dict(zip(_ROW_KEYS, state))
        if current != latest:
            raise PermissionError("authority head disagrees with its audit chain")

    def apply(self, envelope: dict) -> dict:
        if (type(envelope) is not dict or envelope.get("schema") != SCHEMA
                or envelope.get("authority_id") != self.authority_id
                or envelope.get("operation") not in
                {"register", "verify", "prepare", "commit"}):
            raise PermissionError("foreign remote witness envelope")
        op = envelope["operation"]
        fields = {
            "register": {"schema", "authority_id", "operation", "claim", "horizon", "head_sha256"},
            "verify": {"schema", "authority_id", "operation", "claim"},
            "prepare": {"schema", "authority_id", "operation", "claim", "sequence",
                        "previous_head_sha256", "intent_sha256"},
            "commit": {"schema", "authority_id", "operation", "claim", "sequence",
                       "previous_head_sha256", "intent_sha256", "head_sha256", "terminal"},
        }[op]
        if set(envelope) != fields:
            raise PermissionError("remote request has unexpected fields")
        claim = _claim(envelope["claim"])
        with closing(sqlite3.connect(self.database, isolation_level=None, timeout=5)) as c:
            c.execute("PRAGMA synchronous=FULL")
            c.execute("BEGIN IMMEDIATE")
            try:
                self._check_audit(c)
                row = c.execute("SELECT claim_json,horizon,sequence,head,phase,terminal,"
                                "pending_seq,pending_intent FROM histories WHERE identity=?",
                                (claim["identity_sha256"],)).fetchone()
                if op == "register":
                    horizon = _integer(envelope["horizon"], 1, 100)
                    head = _hex(envelope["head_sha256"])
                    if row is not None:
                        raise PermissionError("engineering identity already registered: no reset")
                    c.execute("INSERT INTO histories VALUES (?,?,?,?,?,?,?,?,?)",
                              (claim["identity_sha256"], canonical(claim).decode(),
                               horizon, 0, head, "COMMITTED", "OPEN", None, None))
                    row = (canonical(claim).decode(), horizon, 0, head,
                           "COMMITTED", "OPEN", None, None)
                else:
                    if row is None or row[0] != canonical(claim).decode():
                        raise PermissionError("unknown or foreign engineering identity")
                    _, horizon, old_seq, old_head, phase, terminal, pending_seq, pending_hash = row
                    if op == "prepare":
                        seq = _integer(envelope["sequence"], 1, horizon)
                        prev = _hex(envelope["previous_head_sha256"])
                        intent_hash = _hex(envelope["intent_sha256"])
                        if (phase != "COMMITTED" or terminal != "OPEN"
                                or seq != old_seq + 1 or prev != old_head):
                            raise PermissionError("remote PREPARED CAS refused")
                        c.execute("UPDATE histories SET phase='PREPARED', pending_seq=?,"
                                  "pending_intent=? WHERE identity=?",
                                  (seq, intent_hash, claim["identity_sha256"]))
                        row = (row[0], horizon, old_seq, old_head,
                               "PREPARED", terminal, seq, intent_hash)
                    if op == "commit":
                        seq = _integer(envelope["sequence"], 1, horizon)
                        prev = _hex(envelope["previous_head_sha256"])
                        intent_hash = _hex(envelope["intent_sha256"])
                        head = _hex(envelope["head_sha256"])
                        new_terminal = envelope["terminal"]
                        if (type(new_terminal) is not str or new_terminal not in
                                ("OPEN", "DEAD", "CENSORED") or
                                (seq == horizon and new_terminal == "OPEN") or
                                (seq < horizon and new_terminal == "CENSORED") or
                                phase != "PREPARED" or terminal != "OPEN" or
                                old_seq + 1 != seq or prev != old_head or
                                pending_seq != seq or pending_hash != intent_hash):
                            raise PermissionError("remote COMMITTED CAS refused")
                        c.execute("UPDATE histories SET sequence=?,head=?,phase='COMMITTED',"
                                  "terminal=?,pending_seq=NULL,pending_intent=NULL "
                                  "WHERE identity=?", (seq, head, new_terminal,
                                                       claim["identity_sha256"]))
                        row = (row[0], horizon, seq, head,
                               "COMMITTED", new_terminal, None, None)
                if op != "verify":
                    self._append_audit(c, claim["identity_sha256"], op, row)
                    self._check_audit(c)  # a failed audit never commits the CAS change
                result = {"schema": SCHEMA, "authority_id": self.authority_id,
                          "identity_sha256": claim["identity_sha256"],
                          "sequence": row[2], "head_sha256": row[3],
                          "phase": row[4], "terminal": row[5],
                          "pending_sequence": row[6], "pending_intent_sha256": row[7]}
                c.execute("COMMIT")
                return result
            except BaseException:
                c.execute("ROLLBACK")
                raise


def serve_test_loopback(database: Path, authority_id: str, secret: bytes,
                        *, port: int = 0):
    """Explicit *test-only* loopback server; TLS/auth deployment is NOT supplied."""
    if type(secret) is not bytes or len(secret) < 32:
        raise ValueError("server authentication key must be at least 32 bytes")
    store = AuthorityStore(database, authority_id)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/v1/command":
                self.send_error(404)
                return
            nonce = self.headers.get("X-I3-Nonce", "")
            signature = self.headers.get("X-I3-Signature", "")
            length = self.headers.get("Content-Length", "")
            if (not re.fullmatch(r"[0-9a-f]{32}", nonce)
                    or not HEX.fullmatch(signature)
                    or not length.isascii() or not length.isdigit()
                    or not 1 <= int(length) <= 8192):
                self.send_error(403)
                return
            data = self.rfile.read(int(length))
            expected = hmac.new(secret, b"Q\n" + nonce.encode() + b"\n" + data,
                                sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                self.send_error(403)
                return
            try:
                request = json.loads(data)
                if canonical(request) != data:
                    raise ValueError("noncanonical request")
                response = store.apply(request)
                raw = canonical(response)
            except (ValueError, PermissionError, TypeError, KeyError, sqlite3.Error):
                # No decision, result or state oracle is exposed to a bad caller.
                self.send_error(409)
                return
            mac = hmac.new(secret, b"R\n" + nonce.encode() + b"\n200\n" + raw,
                           sha256).hexdigest()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("X-I3-Signature", mac)
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, format, *args):
            return

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def _main():
    parser = argparse.ArgumentParser(description="I3 isolated local authority test server")
    parser.add_argument("--database", required=True)
    parser.add_argument("--authority-id", required=True)
    parser.add_argument("--key-hex", required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    key = bytes.fromhex(args.key_hex)
    srv = serve_test_loopback(Path(args.database), args.authority_id, key, port=args.port)
    try:
        srv.serve_forever(poll_interval=.05)
    finally:
        srv.server_close()


if __name__ == "__main__":
    _main()
