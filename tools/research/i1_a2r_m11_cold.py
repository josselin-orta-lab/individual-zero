"""A2-R read-only M11 preflight and mechanism evidence; NEVER a birth launcher.

Independent of the A1-C H48 replay and of the experimental birth selector.
This module consumes authenticated M11 events and checks provenance and
chronology. A caller still must independently attest source SHA, birth
weights/setpoints, the complete 96-life archive and the 12-feature Q replay
before the preregistered A2-R statistics can be invoked.
"""
from __future__ import annotations

import json
from hashlib import sha256
from math import isfinite
from pathlib import Path
import sqlite3
from urllib.parse import quote

NEEDS = ("energy", "food", "water", "integrity")
MODES = ("CANONICAL_ABS", "RESEARCH_DEFICIT")
REWARD_STATE_KEY = "i1_a2r_reward_policy"
REWARD_STATE_SCHEMA = "i1-a2r-reward-deficit-owner-v1"
REWARD_SUFFIX = "+i1-a2r-deficit-reward-v1"
HORIZON = 192
TOL = 2e-9


def numeric(value):
    """Decode only strict, canonical signed M11 floating-point values."""
    if type(value) is dict and set(value) == {"$f64"}:
        raw = value["$f64"]
        if type(raw) is not str:
            raise ValueError("invalid M11 f64")
        try:
            result = float.fromhex(raw)
        except (ValueError, OverflowError) as exc:
            raise ValueError("invalid M11 f64") from exc
        if result.hex().lower() != raw:
            raise ValueError("noncanonical M11 f64")
    elif type(value) in (float, int):
        result = float(value)
    else:
        raise ValueError("non-numeric M11 value")
    if not isfinite(result):
        raise ValueError("nonfinite M11 value")
    return result


def body(value):
    if type(value) is not dict or set(value) != set(NEEDS):
        raise ValueError("M11 physical body requires exactly four needs")
    decoded = {name: numeric(value[name]) for name in NEEDS}
    if any(not 0 <= v <= 100 for v in decoded.values()):
        raise ValueError("M11 physical body outside 0..100")
    return decoded


def reward(before, after, *, setpoints, weights, mode):
    """Recompute physical reward, never choose an action or affect TD."""
    if mode not in MODES:
        raise ValueError("unregistered A2-R mode")
    b, a = body(before), body(after)
    if type(setpoints) is not dict or type(weights) is not dict:
        raise ValueError("missing independently checked born reward parameters")
    if set(setpoints) != set(NEEDS) or set(weights) != set(NEEDS):
        raise ValueError("incomplete born reward parameters")
    s = {k: numeric(setpoints[k]) for k in NEEDS}
    w = {k: numeric(weights[k]) for k in NEEDS}
    if any(not 0 <= s[k] <= 100 or not 0 <= w[k] <= 10 for k in NEEDS):
        raise ValueError("invalid born reward parameters")
    if mode == "CANONICAL_ABS":
        return sum(w[k] * (abs(b[k] - s[k]) - abs(a[k] - s[k])) for k in NEEDS)
    return sum(w[k] * (max(0., s[k] - b[k]) -
                       max(0., s[k] - a[k])) for k in NEEDS)


def check_owner_state(state, *, mode):
    """Verify the actual signed M11 Value/Needs owner, not an operator label."""
    if mode not in MODES or type(state) is not dict:
        raise ValueError("unknown reward mode or M11 owner")
    config = state.get("config_version")
    td = state.get("td_values")
    if (type(config) is not str or not config
            or type(td) is not dict or type(td.get("config_version")) is not str
            or type(td.get("weights")) is not dict):
        raise ValueError("missing M11 Value/Needs + TD owner state")
    deficit = config.endswith(REWARD_SUFFIX)
    marker = state.get(REWARD_STATE_KEY)
    if mode == "RESEARCH_DEFICIT":
        if not deficit or marker != REWARD_STATE_SCHEMA:
            raise ValueError("research reward mode lacks M11 owner contract")
    elif deficit or REWARD_STATE_KEY in state:
        raise ValueError("canonical mode contains a research owner marker")
    return {"owner_config_version": config,
            "td_config_version": td["config_version"],
            "td_feature_version": td.get("feature_version"),
            "td_signature_count": len(td["weights"]),
            "mode": mode}


def physical_steps(events, *, generation, status):
    """Join physically applied command, transition and close once per step."""
    if (type(events) is not list or type(generation) is not int
            or not 1 <= generation <= HORIZON or status not in ("active", "dead")):
        raise ValueError("invalid M11 physical horizon or terminal state")
    by_step = {}
    for ev in events:
        if type(ev) is not dict:
            raise ValueError("invalid M11 event")
        kind = ev.get("kind")
        if kind not in ("command_experienced",
                        "world_transition_experienced", "step_closed"):
            continue
        t, attempt = ev.get("t_monde"), ev.get("attempt_ref")
        if type(t) is not int or not 1 <= t <= generation or type(attempt) is not str:
            raise ValueError("M11 physical event outside its attempt")
        row = by_step.setdefault(t, {"attempt": attempt, "events": []})
        if row["attempt"] != attempt:
            raise ValueError("multiple attempt owners in one world step")
        row["events"].append(ev)
    if set(by_step) != set(range(1, generation + 1)):
        raise ValueError("missing authenticated M11 physical steps")
    result = []
    previous = None
    for t in range(1, generation + 1):
        evs = by_step[t]["events"]
        if [e.get("kind") for e in evs] != [
                "command_experienced", "world_transition_experienced",
                "step_closed"]:
            raise ValueError("duplicate or reordered physical M11 receipts")
        cmd, transition, closed = evs
        data = closed.get("data")
        if (type(data) is not dict
                or data.get("applied_command_count") != 1
                or data.get("world_advance_count") != 1
                or data.get("outcome") not in ("normal", "dead")
                or type(cmd.get("primitive")) is not str):
            raise ValueError("M11 physical step not uniquely applied")
        before, after = body(transition.get("body_before")), body(transition.get("body_after"))
        if previous is not None and previous != before:
            raise ValueError("M11 body continuity broken")
        previous = after
        result.append({"step": t, "action": cmd["primitive"],
                       "parameters": cmd.get("parameters"),
                       "before": before, "after": after,
                       "status": "dead" if data["outcome"] == "dead" else "active"})
    if (result[-1]["status"] == "dead") != (status == "dead"):
        raise ValueError("M11 terminal status conflicts with physical ledger")
    if any(v["status"] == "dead" for v in result[:-1]):
        raise ValueError("dead individual executed again")
    return result


def _close(a, b):
    return abs(a - b) <= TOL * max(1., abs(a), abs(b))


def evidence_life(events, *, generation, status, mode, setpoints, weights,
                  beta=0.8):
    """Mechanistic observations only; this does not validate adaptive L3.

    TD return_G is checked on each genuine segment and full Stage8-to-
    Competition evidence is joined to the actual admitted motor option.
    Q weights/12-feature recurrence are *not* reconstructed here and thus
    remain an explicit further scientific gate.
    """
    steps = physical_steps(events, generation=generation, status=status)
    returns = {
        row["step"]: reward(row["before"], row["after"],
                            setpoints=setpoints, weights=weights, mode=mode)
        for row in steps
    }
    if numeric(beta) != .8:
        raise ValueError("A2-R born beta not established at preregistered value")
    evaluations = {}
    competitions = {}
    decisions = []
    verified_links = td_returns = learned = 0
    for ev in events:
        kind, t, cycle, data = (
            ev.get("kind"), ev.get("t_monde"), ev.get("cycle"), ev.get("data"))
        if kind == "stage8_option_evaluation":
            if type(t) is not int or type(cycle) is not int or type(data) is not dict:
                raise ValueError("malformed M11 Stage8 evaluation")
            key = (t, cycle, data.get("option_ref"))
            if key in evaluations or type(key[2]) is not str:
                raise ValueError("duplicate or missing Stage8 option")
            if data.get("learned_value_status") == "learned":
                numeric(data.get("learned_value"))
                learned += 1
            elif data.get("learned_value_status") != "unlearned" or data.get("learned_value") is not None:
                raise ValueError("learned Q claimed without M11 source")
            evaluations[key] = data
        elif kind == "competition_cycle":
            if (type(t) is not int or type(cycle) is not int
                    or type(data) is not dict or type(data.get("traces")) is not list
                    or (t, cycle) in competitions):
                raise ValueError("duplicate or malformed M11 Competition")
            trace = {}
            for item in data["traces"]:
                if type(item) is not dict or type(item.get("option_ref")) is not str:
                    raise ValueError("malformed Competition evidence")
                ref = item["option_ref"]
                candidate = evaluations.get((t, cycle, ref))
                if candidate is None or ref in trace or type(item.get("crossed")) is not bool:
                    raise ValueError("Competition without unique Stage8 evidence")
                left, right = candidate.get("evidence"), item.get("evidence")
                if (left is None) != (right is None):
                    raise ValueError("Stage8 and Competition evidence presence mismatch")
                if left is not None and not _close(numeric(left), numeric(right)):
                    raise ValueError("Competition diverges from Stage8 evidence")
                trace[ref] = item
                verified_links += 1
            expected = {o for (s, c, o) in evaluations if (s, c) == (t, cycle)}
            if set(trace) != expected:
                raise ValueError("Competition omitted an evaluated option")
            competitions[(t, cycle)] = trace
        elif kind == "command_admitted" and type(data) is dict and data.get("source") == "decision":
            if type(t) is not int or type(data.get("option_ref")) is not str:
                raise ValueError("malformed M11 chosen option")
            options = [(c, v) for (s, c, o), v in evaluations.items()
                       if s == t and o == data["option_ref"] and (s, c) in competitions]
            if not options:
                raise ValueError("decision motor option absent from Stage8 Competition")
            c, d = options[-1]
            trace = competitions[(t, c)][data["option_ref"]]
            if not trace["crossed"] and data["option_ref"] != "permanent:attendre":
                raise ValueError("subthreshold non-fallback motor option")
            decisions.append({"step": t, "signature": d["learning_signature"],
                              "option": data["option_ref"], "cycle": c})
        elif kind == "td_update_published":
            if (type(data) is not dict or len(decisions) < 2
                    or type(t) is not int or type(data.get("segment_length")) is not int):
                raise ValueError("TD update without two authenticated decisions")
            prev, nxt = decisions[-2:]
            if (t != nxt["step"] or data["previous_signature"] != prev["signature"]
                    or data["next_signature"] != nxt["signature"]
                    or data["segment_length"] != nxt["step"] - prev["step"]):
                raise ValueError("TD update does not link authentic choices")
            expected = sum((beta ** index) * returns[step]
                           for index, step in enumerate(
                               range(prev["step"], nxt["step"])))
            if not _close(numeric(data.get("return_g")), expected):
                raise ValueError("M11 TD return differs from experienced physical reward")
            td_returns += 1
    if not competitions and evaluations:
        raise ValueError("Stage8 evidence never reached Competition")
    if any((s, c) not in competitions for (s, c, _) in evaluations):
        raise ValueError("unmatched Stage8 evaluation cycle")
    if len({d["step"] for d in decisions}) != len(decisions):
        raise ValueError("duplicate decision per physical step")
    return {
        "scope": "A2R_COLD_MECHANISTIC_PRECHECK_NOT_FULL_Q_NOT_L3",
        "physical_steps": steps, "physical_rewards": returns,
        "decisions": decisions, "td_returns_checked": td_returns,
        "stage8_competition_links": verified_links,
        "learned_stage8_publications": learned,
        "full_q_replay_verified": False,
        "adaptive_learning_go": "NOT_ESTABLISHED",
    }


def inspect_m11(*, path, identity, mode, allow_incomplete=False):
    """Cold SQLite read; incomplete test lives cannot enter cohort statistics."""
    from i1lab.sqlite_life_store import SQLiteLifeLedger
    from i1lab.determinism import canonical_causal_bytes
    from i1_eco_a1_decision_join import _read_canonical_events

    file = Path(path)
    if (not file.is_absolute() or file.is_symlink() or not file.is_file()
            or mode not in MODES or type(identity) is not str or not identity):
        raise ValueError("existing absolute, immutable-scoped M11 identity required")
    receipt = SQLiteLifeLedger.audit_read_only(
        path=str(file), expected_individual_id=identity)
    if receipt.pending_intent or receipt.status not in ("active", "dead"):
        raise ValueError("pending or technically halted M11 individual")
    if (type(allow_incomplete) is not bool
            or not 1 <= receipt.generation <= HORIZON
            or (not allow_incomplete and receipt.status == "active"
                and receipt.generation != HORIZON)):
        raise ValueError("M11 life cannot enter frozen A2-R horizon")
    connection = sqlite3.connect(
        "file:" + quote(str(file.resolve()), safe="/") + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        current = connection.execute(
            "SELECT generation,status,journal_count,journal_head,state_bytes,state_hash "
            "FROM life_current WHERE slot=1").fetchone()
        if (current is None or current[:4] != (
                receipt.generation, receipt.status, receipt.journal_count,
                receipt.journal_head) or type(current[4]) is not bytes
                or sha256(current[4]).hexdigest() != receipt.state_hash
                or current[5] != receipt.state_hash):
            raise ValueError("M11 state differs from authenticated head")
        decoded = json.loads(current[4])
        if canonical_causal_bytes(decoded) != current[4]:
            raise ValueError("noncanonical M11 owner image")
    finally:
        connection.close()
    if (type(decoded) is not dict or type(decoded.get("owners")) is not dict
            or type(decoded.get("owner_ids")) is not list
            or decoded["owner_ids"].count("value_and_needs") != 1):
        raise ValueError("missing unique Value/Needs in M11 owner roster")
    owner = check_owner_state(decoded["owners"].get("value_and_needs"), mode=mode)
    if type(decoded.get("runtime_local")) is not dict or type(
            decoded["runtime_local"].get("runtime_contract")) is not str:
        raise ValueError("missing M11 frozen birth-constructor contract")
    events = _read_canonical_events(
        path=str(file), identity=identity,
        audit={"generation": receipt.generation,
               "journal_head": receipt.journal_head,
               "journal_count": receipt.journal_count})
    steps = physical_steps(events, generation=receipt.generation,
                           status=receipt.status)
    return {
        "receipt": {"identity": identity, "status": receipt.status,
                    "generation": receipt.generation,
                    "journal_head": receipt.journal_head,
                    "journal_count": receipt.journal_count,
                    "state_hash": receipt.state_hash},
        "owner": owner,
        "final_exploration": decoded["owners"].get("exploration"),
        "final_competition": decoded["owners"].get("competition"),
        "runtime_contract": decoded["runtime_local"]["runtime_contract"],
        "events": events, "physical_steps": steps,
        "analysis_admissible": not allow_incomplete,
        "scope": "L1_PARTIAL_M11_PREFLIGHT" if allow_incomplete else "COLD_M11_READ_ONLY",
    }


def compare_pre_reward(*, canonical, candidate, setpoints, weights):
    """No physical divergence can precede the first different reward signal.

    Complete causal mediation requires a separate full vector TD/Q replay.
    This function never declares the preregistered mechanism_exposed true.
    """
    if (type(canonical) is not dict or type(candidate) is not dict
            or canonical.get("scope") != "A2R_COLD_MECHANISTIC_PRECHECK_NOT_FULL_Q_NOT_L3"
            or candidate.get("scope") != "A2R_COLD_MECHANISTIC_PRECHECK_NOT_FULL_Q_NOT_L3"):
        raise ValueError("unattested A2-R arm proof")
    a, b = canonical["physical_steps"], candidate["physical_steps"]
    if not a or not b or a[0]["before"] != b[0]["before"]:
        raise ValueError("different physical birth conditions")
    first_reward = first_motor = None
    for index in range(min(len(a), len(b))):
        left, right = a[index], b[index]
        same = (left["action"], left["parameters"], left["before"], left["after"]) == (
            right["action"], right["parameters"], right["before"], right["after"])
        if not same:
            if first_reward is None:
                raise ValueError("physical policy diverged before any changed reward")
            first_motor = index + 1
            break
        delta = reward(left["before"], left["after"], setpoints=setpoints,
                       weights=weights, mode="CANONICAL_ABS") - reward(
            right["before"], right["after"], setpoints=setpoints,
            weights=weights, mode="RESEARCH_DEFICIT")
        if first_reward is None and not _close(delta, 0.):
            first_reward = index + 1
    if first_motor is None and len(a) != len(b):
        if first_reward is None:
            raise ValueError("difference in survival precedes intervention")
        first_motor = min(len(a), len(b)) + 1
    return {
        "reward_difference_observed": first_reward is not None,
        "first_reward_difference_step": first_reward,
        "first_motor_difference_step": first_motor,
        "pre_reward_prefix_equal": True,
        "mechanism_exposed": False,
        "full_q_replay_verified": False,
        "interpretation": "Q_TO_COMPETITION_CAUSAL_MEDIATION_NOT_YET_ASSESSED",
    }
