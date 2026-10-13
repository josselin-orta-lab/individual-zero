"""Read-only Stage10 indexed-WAL audit. Never authorizes Stage12 recovery.

Exit 0 = valid canonical journal with complete paid index publication pairs
and no unclosed physical step. Exit 2 = corrupt WAL, exit 3 = valid but
unfinished or inconsistent publication/step. Does not instantiate I0.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unicodedata import normalize

CHARGE = "stage10_consolidation_index_maintenance_charged"
ACTIVATE = "stage10_consolidation_version_activated"
RETIRE = "stage10_consolidation_index_retired"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")

def verify(path: Path):
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ValueError("empty or unterminated WAL")
    previous = "0" * 64
    seen = set()
    events = []
    for i, line in enumerate(raw.splitlines()):
        entry = json.loads(line)
        eid = entry["event_id"]
        if (canonical(entry) != line or entry["index"] != i
                or not isinstance(eid, str) or eid in seen
                or normalize("NFC", eid) != eid
                or entry["previous_hash"] != previous):
            raise ValueError(f"invalid canonical provenance at record {i}")
        seen.add(eid)
        expected = sha256(bytes.fromhex(previous) + canonical({
            "event_id": eid, "causal_event": entry["causal_event"],
        })).hexdigest()
        if expected != entry["event_hash"]:
            raise ValueError(f"SHA-256 chain mismatch at record {i}")
        previous = expected
        events.append(entry["causal_event"])
    open_steps = []
    charges, published, retired = {}, {}, {}
    anomalies = []
    terminal_stops = []
    fatal_events = []
    all_published_refs = set()
    all_versions = set()
    for i, event in enumerate(events):
        kind = event.get("kind")
        data = event.get("data", {})
        if kind == "step_opened":
            if open_steps:
                anomalies.append(f"nested physical step at {i}")
            open_steps.append((event.get("t_monde"), event.get("attempt_ref")))
        elif kind == "step_closed":
            if not open_steps or open_steps[-1] != (
                    event.get("t_monde"), event.get("attempt_ref")):
                anomalies.append(f"invalid physical step closure at {i}")
            else:
                open_steps.pop()
        if kind == "experiment_stopped":
            terminal_stops.append((i, event))
        elif kind == "individual_death_confirmed":
            fatal_events.append((i, event))
        if kind not in (CHARGE, ACTIVATE, RETIRE):
            continue
        if not isinstance(data, dict):
            anomalies.append(f"invalid record data at {i}")
            continue
        ref = data.get("consolidation_id")
        if not isinstance(ref, str) or not ref:
            anomalies.append(f"missing consolidation ID at {i}")
            continue
        if kind == CHARGE:
            if ref in charges:
                anomalies.append(f"duplicate indexed charge {ref}")
            charges[ref] = (i, data)
            if (data.get("operation") != "index_maintenance"
                    or not isinstance(data.get("episode_refs"), list)
                    or type(data.get("count")) is not int or data["count"] < 1
                    or data["count"] != len(data["episode_refs"])
                    or len(set(data["episode_refs"])) != data["count"]
                    or any(type(x) is not str or not x for x in data["episode_refs"])
                    or type(data.get("requested_uc")) is not int
                    or data["requested_uc"] != data["count"]
                    or not 0 <= data.get("consumed_step_uc", -1) <= 100
                    or not 0 <= data.get("consumed_period_uc", -1) <= 600):
                anomalies.append(f"invalid index maintenance price {ref}")
        elif kind == ACTIVATE:
            if ref in published:
                anomalies.append(f"duplicate h activation {ref}")
            published[ref] = (i, data)
            batch = data.get("batch")
            version = data.get("new_history_version")
            if (type(batch) is not list or not batch
                    or any(type(x) is not str or not x for x in batch)
                    or len(set(batch)) != len(batch)):
                anomalies.append(f"invalid published batch {ref}")
            elif all_published_refs.intersection(batch):
                anomalies.append(f"republished episode in h {ref}")
            else:
                all_published_refs.update(batch)
            if type(version) is not str or not version or version in all_versions:
                anomalies.append(f"duplicate or invalid h version {ref}")
            else:
                all_versions.add(version)
        else:
            if ref in retired:
                anomalies.append(f"duplicate indexed retirement {ref}")
            retired[ref] = (i, data)
    for ref, (ci, charged) in charges.items():
        if ref not in published or ref not in retired:
            anomalies.append(f"unfinished indexed publication {ref}")
            continue
        hi, h = published[ref]
        ri, retirement = retired[ref]
        if not (
            hi == ci + 1 and ri == hi + 1
            and charged["episode_refs"] == h.get("batch") == retirement.get("episode_refs")
            and charged.get("source_history_version") == h.get("source_history_version")
            and h.get("new_history_version") == retirement.get("new_history_version")
            and retirement.get("maintenance_charge_uc") == charged["requested_uc"]
            and retirement.get("pending_after")
            == charged.get("pending_before", -1) - charged["count"]
        ):
            anomalies.append(f"inconsistent paid index triplet {ref}")
    if charges:
        for ref in published:
            if ref not in charges:
                anomalies.append(f"indexed h without charged maintenance {ref}")
    for ref in retired:
        if ref not in charges:
            anomalies.append(f"index retired without charge {ref}")
    if open_steps:
        anomalies.append(f"{len(open_steps)} unfinished physical step(s)")

    # A valid WAL prefix is not the last atomically committed current life.
    # An abrupt exit after step_closed has no open step but is NOT a clean
    # experiment stop. Never accept that prefix as a complete archive.
    if terminal_stops and fatal_events:
        anomalies.append("operator stop and physical death both claimed")
    if terminal_stops:
        if (len(terminal_stops) != 1
                or terminal_stops[0][0] != len(events) - 1
                or terminal_stops[0][1].get("data", {}).get("physical_death") is not False):
            anomalies.append("invalid, repeated or nonfinal operator stop")
    elif fatal_events:
        if len(fatal_events) != 1:
            anomalies.append("repeated physical death receipt")
        if (events[-1].get("kind") != "step_closed"
                or events[-1].get("data", {}).get("outcome") != "dead"
                or events[-1].get("t_monde") != fatal_events[-1][1].get("t_monde")
                or fatal_events[-1][0] != len(events) - 2):
            anomalies.append("physical death missing immediate terminal closure")
    else:
        anomalies.append("no terminal evidence: valid WAL prefix is not a completed life")
    terminal_kind = ("experiment_stopped" if terminal_stops
                     else "physical_death" if fatal_events else None)
    return {
        "schema": "issue133-stage10-index-wal-readonly-audit-v1",
        "records": len(events), "head_sha256": previous,
        "indexed_payments": len(charges),
        "indexed_retirements": len(retired),
        "outstanding_physical_steps": len(open_steps),
        "terminal_kind": terminal_kind,
        "terminal_evidence_complete": terminal_kind is not None and not anomalies,
        "publication_boundary_complete": not anomalies,
        "recovery_certified": False,
        "may_resume_stage12": False,
        "problems": anomalies,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wal", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.wal)
    except (ValueError, KeyError, TypeError, OSError, UnicodeError, OverflowError) as err:
        print(json.dumps({"integrity_ok": False, "error": str(err),
                          "may_resume_stage12": False,
                          "recovery_certified": False}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["publication_boundary_complete"] else 3

if __name__ == "__main__":
    raise SystemExit(main())
