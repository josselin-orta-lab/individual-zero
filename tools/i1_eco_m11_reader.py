"""Read-only, audited M11 physical trajectory -> operator ECO-v1 score."""
import json
import sqlite3
from pathlib import Path
from urllib.parse import quote

from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1lab.determinism import canonical_causal_bytes, sha256_hex
from i1lab.journal import GENESIS_HASH
from i1_eco_metrics import evaluate_life


def audited_life_metrics(*, path, individual_id, horizon, setpoints, scales):
    if not isinstance(path, str) or not Path(path).is_absolute():
        raise ValueError("absolute SQLite path required")
    receipt = SQLiteLifeLedger.audit_read_only(
        path=path, expected_individual_id=individual_id)
    if receipt.pending_intent or receipt.status not in ("active", "dead"):
        raise ValueError("not a completed clean physical life")
    uri = "file:" + quote(str(Path(path).resolve()), safe="/") + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        current = connection.execute(
            "SELECT generation, status, journal_count, journal_head "
            "FROM life_current WHERE slot=1").fetchone()
        if current != (receipt.generation, receipt.status,
                       receipt.journal_count, receipt.journal_head):
            raise ValueError("M11 state changed since audit")
        rows = connection.execute(
            "SELECT idx, event_id, previous_hash, event_hash, canonical_bytes "
            "FROM causal_occurrence ORDER BY idx").fetchall()
        if len(rows) != receipt.journal_count:
            raise ValueError("M11 occurrence count changed")
        previous = GENESIS_HASH
        events = []
        for expected, (idx, event_id, prev, event_hash, raw) in enumerate(rows):
            if idx != expected or prev != previous or not isinstance(raw, bytes):
                raise ValueError("M11 occurrence sequence changed since audit")
            document = json.loads(raw.decode("utf-8"))
            if (type(document) is not dict
                    or canonical_causal_bytes(document) != raw
                    or document.get("index") != idx
                    or document.get("event_id") != event_id
                    or document.get("event_hash") != event_hash
                    or document.get("previous_hash") != previous
                    or type(document.get("causal_event")) is not dict):
                raise ValueError("M11 occurrence bytes changed since audit")
            payload = canonical_causal_bytes({
                "event_id": event_id, "causal_event": document["causal_event"]})
            if sha256_hex(bytes.fromhex(previous) + payload) != event_hash:
                raise ValueError("M11 occurrence hash changed since audit")
            previous = event_hash
            events.append(document["causal_event"])
        if previous != receipt.journal_head:
            raise ValueError("M11 head changed since audit")
    finally:
        connection.close()
    by_step = {}
    accepted = {"command_experienced", "world_transition_experienced", "step_closed"}
    for e in events:
        if e.get("kind") not in accepted:
            continue
        t = e.get("t_monde")
        attempt = e.get("attempt_ref")
        if type(t) is not int or t < 1 or not isinstance(attempt, str):
            raise ValueError("invalid physical occurrence owner")
        record = by_step.setdefault(t, {"attempt": attempt, "entries": []})
        if record["attempt"] != attempt:
            raise ValueError("multiple attempt owners in physical step")
        record["entries"].append(e)
    if receipt.generation < 1 or len(by_step) != receipt.generation:
        raise ValueError("physical steps do not match M11 generations")
    steps = []
    initial = None
    previous = None
    for t in range(1, receipt.generation + 1):
        record = by_step.get(t)
        if record is None:
            raise ValueError("missing physical step")
        entries = record["entries"]
        if [e["kind"] for e in entries] != [
                "command_experienced", "world_transition_experienced", "step_closed"]:
            raise ValueError("missing, repeated or reordered physical receipts")
        cmd, transition, closed = entries
        outcome = closed.get("data", {}).get("outcome")
        if outcome not in ("normal", "dead"):
            raise ValueError("nonphysical or technical step")
        if (closed["data"].get("applied_command_count") != 1
                or closed["data"].get("world_advance_count") != 1):
            raise ValueError("wrong physical execution count")
        before, after = transition.get("body_before"), transition.get("body_after")
        if previous is not None and before != previous:
            raise ValueError("discontinuous body")
        if initial is None:
            initial = before
        previous = after
        steps.append({"step": t, "body": after,
                      "action": cmd.get("primitive"),
                      "status": "dead" if outcome == "dead" else "active"})
    if receipt.generation != len(steps):
        raise ValueError("generation mismatch")
    if (receipt.status == "dead") != (steps[-1]["status"] == "dead"):
        raise ValueError("death status mismatch")
    score = evaluate_life(initial_body=initial, steps=steps,
                          horizon=horizon, status=receipt.status,
                          setpoints=setpoints, scales=scales)
    return {
        "individual_id": receipt.individual_id,
        "journal_head": receipt.journal_head,
        "journal_count": receipt.journal_count,
        "generation": receipt.generation,
        "custody": "audited_SQLite_M11_read_only",
        "metrics": score,
        "causal_performance": "NOT_ESTABLISHED",
    }
