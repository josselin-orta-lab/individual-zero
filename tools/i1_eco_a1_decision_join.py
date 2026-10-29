"""Independent M11 chain -> A1 decision-read consistency, never a GO oracle.

Rows from the Q read scope are EXTERNAL, not signed by M11. Every permitted
row is reconciled with an actual journal occurrence, with strict chronology
and a previous committed TD update where a learned Q is claimed. This proves
M11 consistency, not independent capture of the pre-mask Q float and not a
causal benefit. A cold journal cannot by itself authenticate a monkeypatch.
"""
from collections import defaultdict
import json
import math
from pathlib import Path
import sqlite3
from urllib.parse import quote


def _read_canonical_events(*, path, identity, audit):
    from i1lab.determinism import canonical_causal_bytes, sha256_hex
    from i1lab.journal import GENESIS_HASH
    from i1lab.sqlite_life_store import SQLiteLifeLedger

    db = Path(path)
    if (not db.is_absolute() or not db.is_file()
            or db.is_symlink()):
        raise ValueError("A1 M11 source must be an existing non-symlinked file")
    receipt = SQLiteLifeLedger.audit_read_only(
        path=str(db), expected_individual_id=identity)
    if (receipt.pending_intent or receipt.status not in ("active", "dead")
            or receipt.generation != audit["generation"]
            or receipt.journal_head != audit["journal_head"]
            or receipt.journal_count != audit["journal_count"]
            or receipt.individual_id != identity):
        raise ValueError("A1 M11 custody receipt changed")
    conn = sqlite3.connect(
        "file:" + quote(str(db.resolve()), safe="/") + "?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        conn.execute("BEGIN")
        current = conn.execute(
            "SELECT generation, status, journal_count, journal_head "
            "FROM life_current WHERE slot=1").fetchone()
        if current != (receipt.generation, receipt.status,
                       receipt.journal_count, receipt.journal_head):
            raise ValueError("A1 M11 changed during cold audit")
        rows = conn.execute(
            "SELECT idx, event_id, previous_hash, event_hash, canonical_bytes "
            "FROM causal_occurrence ORDER BY idx").fetchall()
        if len(rows) != receipt.journal_count:
            raise ValueError("A1 M11 event count changed during cold audit")
        events = []
        previous = GENESIS_HASH
        for index, (idx, eid, prev, digest, raw) in enumerate(rows):
            if (idx != index or prev != previous
                    or type(raw) is not bytes):
                raise ValueError("A1 broken M11 occurrence chronology")
            doc = json.loads(raw.decode("utf-8"))
            if (type(doc) is not dict
                    or canonical_causal_bytes(doc) != raw
                    or doc.get("index") != idx or doc.get("event_id") != eid
                    or doc.get("event_hash") != digest
                    or doc.get("previous_hash") != prev
                    or type(doc.get("causal_event")) is not dict):
                raise ValueError("A1 changed canonical M11 event bytes")
            payload = canonical_causal_bytes({
                "event_id": eid, "causal_event": doc["causal_event"]})
            if sha256_hex(bytes.fromhex(previous) + payload) != digest:
                raise ValueError("A1 M11 event chain corruption")
            previous = digest
            events.append(doc["causal_event"])
        if previous != receipt.journal_head:
            raise ValueError("A1 M11 journal head changed")
    finally:
        conn.close()
    return events


def _numeric(cell):
    if cell is None:
        return None
    if type(cell) is dict and set(cell) == {"$f64"}:
        if type(cell["$f64"]) is not str:
            raise ValueError("invalid M11 float representation")
        value = float.fromhex(cell["$f64"])
        if value.hex().lower() != cell["$f64"]:
            raise ValueError("noncanonical M11 float")
    elif type(cell) in (int, float):
        value = float(cell)
    else:
        raise ValueError("invalid M11 numeric payload")
    if not math.isfinite(value):
        raise ValueError("nonfinite M11 numeric payload")
    return value


def _signature(command):
    if type(command) is not dict or set(command) != {"primitive", "parameters"}:
        raise ValueError("M11 selected affordance command schema mismatch")
    if (type(command["primitive"]) is not str
            or type(command["parameters"]) is not dict):
        raise ValueError("M11 selected affordance malformed")
    suffix = ":".join(
        f"{key}={command['parameters'][key]}"
        for key in sorted(command["parameters"])) or "here"
    return "i1:affordance:" + command["primitive"] + ":" + suffix


def verify_decision_alignment(*, events, reads, adapters, mode, generation):
    """Pure, fail-closed M11 consistency check over read-only journal evidence.

    Does not infer that masking improves outcomes or that an external observer
    log is itself an M11 occurrence. Returns only evidence-link counts.
    """
    if (mode not in ("canonical", "td_read_masked")
            or type(events) is not list or type(reads) is not list
            or type(adapters) is not list
            or type(generation) is not int or generation < 1):
        raise ValueError("invalid A1 alignment inputs")
    masked = mode == "td_read_masked"
    kinds = {
        "stage8_option_evaluation": {},
        "competition_cycle": {},
        "i1_local_opportunity_proposed": {},
        "i1_unknown_affordance_proposed": {},
    }
    td_published = defaultdict(list)
    commands = {}
    experienced = {}
    for event in events:
        if type(event) is not dict:
            raise ValueError("invalid cold M11 event")
        kind, step, cycle = (event.get("kind"),
                             event.get("t_monde"), event.get("cycle"))
        if (type(step) is not int or not 1 <= step <= generation):
            raise ValueError("event outside M11 generations")
        data = event.get("data")
        if kind in kinds:
            if type(cycle) is not int or cycle < 1 or type(data) is not dict:
                raise ValueError("missing M11 decision cycle")
            key = ((step, cycle, data.get("option_ref"))
                   if kind == "stage8_option_evaluation" else
                   (step, cycle))
            if key in kinds[kind]:
                raise ValueError("duplicate committed decision occurrence")
            kinds[kind][key] = data
        if kind == "td_update_published":
            if type(data) is not dict or type(data.get("updated_signatures")) is not list:
                raise ValueError("invalid committed TD update")
            for signature in data["updated_signatures"]:
                if type(signature) is not str or not signature:
                    raise ValueError("invalid committed TD signature")
                td_published[signature].append(step)
        if kind == "command_admitted":
            if step in commands or type(data) is not dict:
                raise ValueError("duplicate or invalid command admission")
            commands[step] = (data.get("option_ref"),
                              data.get("primitive"), data.get("command_hash"))
        if kind == "command_experienced":
            if step in experienced:
                raise ValueError("duplicate experienced command")
            experienced[step] = (event.get("primitive"), event.get("command_hash"))
    if (set(commands) != set(range(1, generation + 1))
            or set(experienced) != set(commands)
            or any(commands[t][1:] != experienced[t] for t in commands)):
        raise ValueError("M11 decision admission/physical experience mismatch")
    for r in reads:
        if (type(r) is not dict
                or r.get("source") not in (
                    "planning_local", "planning_goal", "stage8_direct")
                or type(r.get("step")) is not int
                or not 1 <= r["step"] <= generation
                or type(r.get("cycle")) is not int or r["cycle"] < 1
                or type(r.get("signature")) is not str or not r["signature"]
                or r.get("original_status") not in ("learned", "unlearned")
                or type(r.get("masked")) is not bool
                or type(r.get("update_count")) is not int):
            raise ValueError("malformed external Q read observer")
        if r["masked"] != (masked and r["original_status"] == "learned"):
            raise ValueError("A1 Q intervention return misreported")
        if r["original_status"] == "learned":
            if (type(r.get("original_value")) not in (int, float)
                    or type(r.get("original_evidence")) not in (int, float)
                    or not math.isfinite(r["original_value"])
                    or not math.isfinite(r["original_evidence"])
                    or r["update_count"] < 1):
                raise ValueError("invalid observed learned TD receipt")
            if not any(s < r["step"] for s in td_published[r["signature"]]):
                raise ValueError("learned Q has no prior committed TD update")
        elif (r.get("original_value") is not None
              or r.get("original_evidence") is not None
              or r["update_count"] != 0):
            raise ValueError("unlearned TD read has invented value")
    by_source = defaultdict(list)
    stage8_observed = set()
    stage8_linked = 0
    comp = kinds["competition_cycle"]
    for r in reads:
        source = r["source"]
        step_cycle = (r["step"], r["cycle"])
        if source != "stage8_direct":
            by_source[(source, *step_cycle)].append(r)
            continue
        key = (r["step"], r["cycle"], r.get("option_ref"))
        if (type(r.get("option_ref")) is not str or not r["option_ref"]
                or key in stage8_observed
                or key not in kinds["stage8_option_evaluation"]):
            raise ValueError("unanchored or duplicated direct Stage8 Q read")
        published = kinds["stage8_option_evaluation"][key]
        delivered = ("unlearned" if r["masked"] else r["original_status"])
        if (published.get("learning_signature") != r["signature"]
                or published.get("learned_value_status") != delivered
                or _numeric(published.get("learned_value")) != (
                    r["original_value"] if delivered == "learned" else None)):
            raise ValueError("Stage8 decision not consistent with M11 Q use")
        if key[:2] not in comp or not any(
            trace.get("option_ref") == key[2]
            for trace in comp[key[:2]].get("traces", ())
        ):
            raise ValueError("Stage8 did not reach committed Competition")
        stage8_observed.add(key)
        stage8_linked += 1

    winner_links = 0
    for source, kind in (
        ("planning_local", "i1_local_opportunity_proposed"),
        ("planning_goal", "i1_unknown_affordance_proposed"),
    ):
        proposals = kinds[kind]
        for step_cycle, candidate in proposals.items():
            candidates = by_source.pop((source, *step_cycle), [])
            if not candidates:
                raise ValueError("M11 Planning proposal has no external Q read")
            if len({x["signature"] for x in candidates}) != len(candidates):
                raise ValueError("duplicate Q read of a Planning candidate")
            signature = (candidate.get("learning_signature")
                         if source == "planning_local" else
                         _signature(candidate["command"]))
            winners = [x for x in candidates if x["signature"] == signature]
            if len(winners) != 1:
                raise ValueError("M11 Planning winner not found among Q reads")
            chosen = winners[0]
            delivered = ("unlearned" if chosen["masked"] else
                         chosen["original_status"])
            if (candidate.get("learned_value_status") != delivered
                    or source == "planning_goal" and
                    _numeric(candidate.get("learned_value")) != (
                        chosen["original_value"] if delivered == "learned"
                        else None)):
                raise ValueError("M11 Planning Q choice and observer disagree")
            winner_links += 1
    # A Planning cycle may inspect candidates yet legitimately publish no
    # proposal (insufficient UC, already represented, or aborted planning).
    # Unselected reads remain observer-only and cannot count as exposure.
    unselected_reads = sum(len(v) for v in by_source.values())

    adapter_links = 0
    for a in adapters:
        if (type(a) is not dict
                or a.get("source") != "stage8_pending_adapter"
                or type(a.get("step")) is not int
                or type(a.get("cycle")) is not int
                or type(a.get("option_ref")) is not str
                or type(a.get("signature")) is not str
                or type(a.get("masked")) is not bool
                or a["masked"] != masked
                or a.get("delivered_status") not in ("learned", "unlearned")):
            raise ValueError("invalid A1 pending Stage8 observer")
        key = (a["step"], a["cycle"], a["option_ref"])
        if key in stage8_observed or key not in kinds["stage8_option_evaluation"]:
            raise ValueError("M11 pending adapter not linked to unique Stage8")
        stage = kinds["stage8_option_evaluation"][key]
        if (stage.get("learning_signature") != a["signature"]
                or stage.get("learned_value_status") !=
                   a["delivered_status"]):
            raise ValueError("M11 pending adapter status differs")
        if key[:2] not in comp or not any(
            trace.get("option_ref") == key[2]
            for trace in comp[key[:2]].get("traces", ())
        ):
            raise ValueError("pending Stage8 option not in Competition")
        if not any(
            p.get("option_ref") == key[2]
            for name in ("i1_local_opportunity_proposed",
                         "i1_unknown_affordance_proposed")
            for point, p in kinds[name].items()
            if point == key[:2]
        ):
            raise ValueError("pending Stage8 has no M11 Planning origin")
        stage8_observed.add(key)
        adapter_links += 1
    # Every learned Stage8 evidence occurrence must be accounted for by a
    # verified read or adapter (no untracked learned-value consumer).
    if any(
        data.get("learned_value_status") == "learned" and key not in stage8_observed
        for key, data in kinds["stage8_option_evaluation"].items()
    ):
        raise ValueError("unobserved M11 learned Stage8 evaluation")
    if masked and any(
        data.get("learned_value_status") == "learned"
        for data in kinds["stage8_option_evaluation"].values()
    ):
        raise ValueError("learned TD leaked into masked Stage8")
    learned = sum(r["original_status"] == "learned" for r in reads)
    masked_count = sum(r["masked"] for r in reads)
    return {
        "schema": "individual-zero-i1-eco-a1-decision-alignment/1",
        "read_count": len(reads),
        "learned_read_count": learned,
        "masked_read_count": masked_count,
        "prior_td_anchored_learned_reads": learned,
        "planning_winners_joined": winner_links,
        "planning_reads_without_published_option": unselected_reads,
        "stage8_direct_joined": stage8_linked,
        "pending_adapters_joined": adapter_links,
        "committed_competition_cycles": len(comp),
        "first_masked_read_step": min(
            (r["step"] for r in reads if r["masked"]), default=None),
        "scope": "M11_ANCHORED_EXTERNAL_OBSERVER_NOT_INDEPENDENT_CAUSAL_GO",
    }


def audited_a1_decision_alignment(*, path, identity, audited, reads,
                                  adapters, mode):
    events = _read_canonical_events(path=path, identity=identity, audit=audited)
    return verify_decision_alignment(
        events=events, reads=reads, adapters=adapters,
        mode=mode, generation=audited["generation"])


def _physical_prefix(events, *, generation):
    """Only source-verified motor and WorldBody events, with exact wire values.

    Distinct M11 identities have different attempt IDs, option IDs, and
    journal hashes: never compare those. Compare exactly the command semantics,
    body, position, and physical effects before the first read intervention.
    """
    by_step = {}
    required = ("command_admitted", "command_experienced",
                "world_transition_experienced", "step_closed")
    for e in events:
        if e.get("kind") not in required:
            continue
        step = e.get("t_monde")
        if type(step) is not int or not 1 <= step <= generation:
            raise ValueError("A1 physical prefix outside audited generation")
        slot = by_step.setdefault(step, {})
        kind = e["kind"]
        if kind in slot:
            raise ValueError("A1 repeated physical M11 occurrence")
        slot[kind] = e
    if set(by_step) != set(range(1, generation + 1)):
        raise ValueError("A1 physical prefix missing a committed generation")
    prefix = []
    previous_after = None
    for step in range(1, generation + 1):
        slot = by_step[step]
        if set(slot) != set(required):
            raise ValueError("A1 incomplete physical M11 step")
        admitted = slot["command_admitted"].get("data", {})
        experienced = slot["command_experienced"]
        transition = slot["world_transition_experienced"]
        closed = slot["step_closed"].get("data", {})
        if (type(admitted) is not dict or
                type(experienced.get("parameters")) is not dict or
                admitted.get("primitive") != experienced.get("primitive") or
                admitted.get("command_hash") != experienced.get("command_hash") or
                type(transition.get("body_before")) is not dict or
                type(transition.get("body_after")) is not dict or
                type(transition.get("position_after")) is not dict or
                closed.get("outcome") not in ("normal", "dead")):
            raise ValueError("A1 physical prefix has inconsistent M11 events")
        if (previous_after is not None and
                transition["body_before"] != previous_after):
            raise ValueError("A1 physical prefix has discontinuous body")
        previous_after = transition["body_after"]
        prefix.append({
            "primitive": experienced["primitive"],
            "parameters": experienced["parameters"],
            "command_hash": experienced["command_hash"],
            "body_before": transition["body_before"],
            "body_after": transition["body_after"],
            "position_after": transition["position_after"],
            "effects": transition.get("effects"),
            "outcome": closed["outcome"],
        })
    return prefix


def audited_a1_physical_prefix(*, path, identity, audited):
    """Re-read full M11 custody; do not trust the external life report."""
    return _physical_prefix(
        _read_canonical_events(path=path, identity=identity, audit=audited),
        generation=audited["generation"],
    )


def guard_preintervention_prefix(*, canonical, masked, first_masked_step):
    """Disallow differences *before* the only intended TD-read intervention.

    If there was never an actual masked learned read, all overlapping
    physical steps must match; otherwise unrelated ID/engine effects spoil
    any causal contrast. A first read at step N permits motor differences
    starting at N, but never at an earlier step.
    """
    if (type(canonical) is not list or type(masked) is not list or
            not canonical or not masked):
        raise ValueError("A1 missing authenticated physical prefixes")
    if first_masked_step is not None and (
        type(first_masked_step) is not int or
        not 1 <= first_masked_step <= len(masked)):
        raise ValueError("A1 invalid first TD intervention step")
    compare_until = (first_masked_step - 1
                     if first_masked_step is not None else
                     min(len(canonical), len(masked)))
    for i in range(compare_until):
        if i >= len(canonical) or i >= len(masked) or (
                canonical[i] != masked[i]):
            raise ValueError(
                "A1 UNMATCHED_PREINTERVENTION_PHYSICAL_PREFIX at step " +
                str(i + 1))
    if first_masked_step is None and len(canonical) != len(masked):
        raise ValueError("A1 diverged despite never using the TD intervention")
    return {
        "prefix_steps_equal": compare_until,
        "first_masked_step": first_masked_step,
        "verdict": ("NO_MASKED_EXPOSURE" if first_masked_step is None else
                    "PREINTERVENTION_PHYSICAL_PREFIX_MATCHED"),
    }
