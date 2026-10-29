"""Read-only, audited M11 physical trajectory -> operator ECO-v1 score."""
import json
import sqlite3
from pathlib import Path
from urllib.parse import quote

from i1lab.sqlite_life_store import SQLiteLifeLedger
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
            "SELECT canonical_bytes FROM causal_occurrence ORDER BY idx").fetchall()
        if len(rows) != receipt.journal_count:
            raise ValueError("M11 occurrence count changed")
        events = [json.loads(raw)["causal_event"] for (raw,) in rows]
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
    if len(by_step) != receipt.generation:
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
