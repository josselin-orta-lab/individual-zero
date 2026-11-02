"""I2 four-reserve physical journal under an EXISTING cognition SQLite connection.

The v5 fixture owns the connection and COMMIT. There is no independent life,
external motor, scheduler, memory migration or I1 runtime. Pure native action
transitions are applied only by a caller already holding an admitted control
event. Atomic rollback is inherited from that SAME transaction.
"""
import json
import sqlite3
from hashlib import sha256

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_consequence_bridge import admitted_consequence
from i2.modules.native_owner_support import (
    _json, saved_body, saved_traits, current_evidence,
)

SCHEMA = "i2-native-physical-journal-v1"


def initialize_native_body(conn: sqlite3.Connection, *,
                           body: Body, traits: BirthTemperament) -> None:
    """Create the native body within the *existing* SQLite cognition file."""
    if not conn.in_transaction:
        raise ValueError("native genesis requires an active owner transaction")
    if type(body) is not Body or type(traits) is not BirthTemperament:
        raise ValueError("exact native body and birth traits required")
    if min(body.food, body.water, body.integrity) <= 0:
        raise ValueError("terminal native genesis")
    conn.execute("""CREATE TABLE native_physiology (
        id INTEGER PRIMARY KEY CHECK(id=1),
        revision INTEGER NOT NULL, body_json TEXT NOT NULL,
        traits_json TEXT NOT NULL, head TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE native_physical_events (
        seq INTEGER PRIMARY KEY,
        admitted_action TEXT NOT NULL, admission_ref TEXT NOT NULL UNIQUE,
        cognition_hash TEXT NOT NULL UNIQUE,
        before_json TEXT NOT NULL, after_json TEXT NOT NULL,
        net_physiological_relief REAL NOT NULL,
        terminal INTEGER NOT NULL CHECK(terminal IN (0,1)),
        previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL UNIQUE)""")
    conn.execute("INSERT INTO native_physiology VALUES(1,0,?,?,?)",
                 (_json(body.as_dict()), _json(traits.as_dict()), "genesis"))


def native_snapshot(conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        "SELECT revision,body_json,traits_json,head FROM native_physiology "
        "WHERE id=1").fetchone()
    if row is None:
        raise ValueError("no native physical genesis")
    revision, raw, raw_traits, head = row
    body, traits = saved_body(raw), saved_traits(raw_traits)
    return {"revision": revision, "body": body, "traits": traits, "head": head,
            "current_evidence": current_evidence(body, traits)}


def commit_admitted_physics(conn: sqlite3.Connection, *,
                            action: str, admission_ref: str,
                            cognition_hash: str,
                            berry_food_gain: float = 0.0,
                            berry_integrity_delta: float = 0.0,
                            drink_water_gain: float = 0.0) -> dict:
    """Apply the pre-admitted action in the v5 caller's *same transaction*.

    Admission is additionally checked against the committed cognitive event:
    this method does not trust the action or receipt asserted by its caller.
    The existing controller remains the only admission authority.
    """
    if not conn.in_transaction:
        raise ValueError("native effect requires owner transaction")
    if (type(admission_ref) is not str or not admission_ref or
            type(cognition_hash) is not str or len(cognition_hash) != 64):
        raise ValueError("missing bound action admission or cognitive hash")
    event_row = conn.execute(
        "SELECT seq,event_json FROM events WHERE event_hash=?",
        (cognition_hash,)).fetchone()
    if event_row is None:
        raise ValueError("native action has no committed cognitive source")
    seq, saved_event = event_row
    event = json.loads(saved_event)
    frame, review = event["frame"], event["control_review"]
    if frame is None or review is None or review["status"] != "REVIEWED_NOT_ADMITTED":
        raise ValueError("native action not admitted by cognitive control")
    candidates = [c["semantic_ref"] for c in frame["candidates"]
                  if c["candidate_ref"] == review["suggested_candidate_ref"]]
    safety, control = event["safety_finding"], event["control_receipt"]
    if (len(candidates) != 1 or candidates[0] != action or
            safety is None or safety["veto"] is not False or
            control is None or control["ref"] != review["control_receipt_ref"]):
        raise ValueError("no current paid safe admission for native effect")
    if admission_ref != (
            "internal:i2:native-admission:" +
            sha256(_json([seq, cognition_hash, action]).encode()).hexdigest()):
        raise ValueError("forged native admission reference")
    snapshot = native_snapshot(conn)
    if seq != snapshot["revision"] + 1:
        raise ValueError("stale, repeated or skipped native action")
    body, traits = snapshot["body"], snapshot["traits"]
    if min(body.food, body.water, body.integrity) <= 0:
        raise ValueError("terminal native physiology cannot act")
    result = admitted_consequence(
        before=body, temperament=traits, action=action,
        admitted=True, applied=True, berry_food_gain=berry_food_gain,
        berry_integrity_delta=berry_integrity_delta,
        drink_water_gain=drink_water_gain)
    before_json = _json(body.as_dict())
    after_json = _json(result.after.as_dict())
    relief = (sum(result.needs_before.pressures.values()) -
              sum(result.needs_after.pressures.values()))
    payload = _json([SCHEMA, seq, action, admission_ref, cognition_hash,
                     before_json, after_json, relief, result.terminal,
                     snapshot["head"]])
    head = sha256(payload.encode("ascii")).hexdigest()
    conn.execute("INSERT INTO native_physical_events VALUES(?,?,?,?,?,?,?,?,?,?)",
                 (seq, action, admission_ref, cognition_hash, before_json,
                  after_json, relief, int(result.terminal),
                  snapshot["head"], head))
    conn.execute("UPDATE native_physiology SET revision=?,body_json=?,head=? "
                 "WHERE id=1", (seq, after_json, head))
    return {"revision": seq, "body": result.after.as_dict(),
            "terminal": result.terminal, "cognitive_hash": cognition_hash,
            "physical_hash": head, "m11_authenticated": False}


def audit_native_body(conn: sqlite3.Connection) -> dict:
    """Recompute physical before/after bindings and validate the native chain.

    This local audit detects mutations, not coordinated replacement of the
    whole SQLite file; it is not an independent M11 attestation.
    """
    current = native_snapshot(conn)
    rows = conn.execute(
        "SELECT * FROM native_physical_events ORDER BY seq").fetchall()
    if len(rows) != current["revision"]:
        raise ValueError("native physical journal revision mismatch")
    previous = "genesis"
    first_before = None
    prior_after = None
    for index, row in enumerate(rows, start=1):
        (seq, action, admission_ref, cognitive_hash, before, after,
         relief, terminal, prev, digest) = row
        if seq != index or prev != previous or (prior_after is not None
                                                and before != prior_after):
            raise ValueError("native physical chain discontinuity")
        saved_body(before)
        saved_body(after)
        payload = _json([SCHEMA, seq, action, admission_ref, cognitive_hash,
                         before, after, relief, bool(terminal), prev])
        if sha256(payload.encode("ascii")).hexdigest() != digest:
            raise ValueError("native physical event changed")
        first_before = before if first_before is None else first_before
        prior_after, previous = after, digest
    if (previous != current["head"] or
            (prior_after is not None and
             prior_after != _json(current["body"].as_dict()))):
        raise ValueError("native physical head changed")
    return {"revision": current["revision"],
            "body": current["body"].as_dict(),
            "traits": current["traits"].as_dict(),
            "chain_head": current["head"],
            "m11_authenticated": False,
            "native_cognition_integration": "HOOK_READY_NOT_YET_WIRED"}
