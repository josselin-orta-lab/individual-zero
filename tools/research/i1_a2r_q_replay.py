"""A2-R: independent full 12-feature Q/TD reconstruction from signed M11 events.

This reader never imports I1, births an actor, changes Q or infers a
benefit. The caller MUST cold-verify the native M11 chain/owner image first
and independently attest all birth TD/world/need parameters from the locked
source. This module checks the COMPLETE vector recursion, learned Stage8
values, Competition read-through and final causal Q snapshot, including
uncredited lethal steps and censoring without synthetic terminal TD.
"""
from __future__ import annotations

from math import isfinite
from i1_a2r_m11_cold import (
    HORIZON, MODES, NEEDS, body, numeric, physical_steps, reward,
)

FEATURES = (
    "bias", "energy", "food", "water", "integrity", "x", "y", "is_night",
    "goal_drink", "goal_eat", "goal_recover_energy", "goal_restore_integrity",
)
GOALS = {None, "drink", "eat", "recover_energy", "restore_integrity"}
TD_VERSION = "p31-stage8-reference-v1"
TOL = 2e-9


def _check(actual, expected, label):
    a, b = numeric(actual), numeric(expected)
    if abs(a - b) > TOL * max(1., abs(a), abs(b)):
        raise ValueError(f"{label}: observed={a!r} reconstructed={b!r}")
    return abs(a - b)


def birth_contract(born_td, world_clock):
    """Verify separately-attested pristine config, never trust log parameters."""
    if type(born_td) is not dict or type(world_clock) is not dict:
        raise ValueError("missing A2-R pristine frozen TD/world contract")
    if born_td.get("version") != TD_VERSION:
        raise ValueError("unknown preregistered TD implementation")
    if tuple(born_td.get("feature_names", ())) != FEATURES:
        raise ValueError("wrong P-32 feature order or dimension")
    beta, eta, lam = (numeric(born_td.get(k))
                      for k in ("beta", "eta", "lambda_e"))
    if (beta, eta, lam) != (.8, .05, .8):
        raise ValueError("A2-R different TD parameters")
    scales = tuple(numeric(born_td.get(k))
                   for k in ("position_scale_x", "position_scale_y"))
    if scales != (31., 31.):
        raise ValueError("A2-R unregistered position scaling")
    if (type(born_td.get("feature_version")) is not str
            or not born_td["feature_version"]):
        raise ValueError("missing born P-32 feature schema")
    day = world_clock.get("day_steps")
    night = world_clock.get("night_steps")
    onset = world_clock.get("night_start_step")
    if (type(day) is not int or day != 300 or type(night) is not int
            or night != 100 or type(onset) is not int
            or not 0 <= onset <= 200):
        raise ValueError("A2-R unregistered physical day/night cycle")
    return beta, eta, lam, scales


def features(capture, goal, *, world_clock, born_td):
    if goal not in GOALS or type(capture) is not dict or capture.get("kind") != "perceptual_capture":
        raise ValueError("invalid first-person P-32 context")
    t, data = capture.get("t_monde"), capture.get("data")
    if (type(t) is not int or not 1 <= t <= HORIZON
            or type(data) is not dict or data.get("capture_t_monde") != t):
        raise ValueError("P-32 capture outside true A2-R world occurrence")
    b = body(data.get("dual_scope_visible_body"))
    pos = data.get("position")
    if (type(pos) is not dict or set(pos) != {"x", "y"}
            or any(type(pos[k]) is not int or not 0 <= pos[k] <= 31 for k in ("x", "y"))):
        raise ValueError("P-32 position is invalid")
    step_in_day = (t - 1) % world_clock["day_steps"]
    night = world_clock["night_start_step"] <= step_in_day < (
        world_clock["night_start_step"] + world_clock["night_steps"])
    return (
        1., b["energy"] / 100., b["food"] / 100.,
        b["water"] / 100., b["integrity"] / 100.,
        pos["x"] / numeric(born_td["position_scale_x"]),
        pos["y"] / numeric(born_td["position_scale_y"]),
        float(night),
        float(goal == "drink"), float(goal == "eat"),
        float(goal == "recover_energy"), float(goal == "restore_integrity"),
    )


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _state_check(replayed, published, *, generation, final_status, rewards):
    """Reject a numerically correct log replay with a different M11 Q image."""
    if type(published) is not dict:
        raise ValueError("no authenticated final M11 TD state")
    if (published.get("config_version") != TD_VERSION
            or published.get("feature_version") != replayed["feature_version"]):
        raise ValueError("M11 final Q schema differs from frozen birth")
    for field in ("weights", "traces"):
        actual = published.get(field)
        expected = replayed[field]
        if type(actual) is not dict or set(actual) != set(expected):
            raise ValueError("M11 final " + field + " signature set mismatch")
        for sig, row in expected.items():
            vec = actual[sig]
            if type(vec) is not list or len(vec) != 12:
                raise ValueError("M11 final " + field + " vector dimension mismatch")
            for i, v in enumerate(vec):
                _check(v, row[i], "M11 final " + field + " " + sig)
    if (type(published.get("update_counts")) is not dict
            or published["update_counts"] != replayed["counts"]):
        raise ValueError("M11 final Q update counts mismatch")

    pending = published.get("pending")
    last = replayed["last_effective_decision"]
    if last is None:
        if pending is not None:
            raise ValueError("spurious pending Q without an applied decision")
        return 0
    if type(pending) is not dict or type(pending.get("state")) is not dict:
        raise ValueError("M11 final pending Q segment missing")
    d = last
    if (pending.get("decision_t_monde") != d["step"]
            or pending.get("signature") != d["signature"]):
        raise ValueError("M11 pending Q decision origin mismatch")
    st = pending["state"]
    if (st.get("active_goal_type") != d["goal"]
            or st.get("temporal_context") != d["time"]
            or st.get("x") != d["x"] or st.get("y") != d["y"]):
        raise ValueError("M11 pending Q feature context mismatch")
    for k in NEEDS:
        _check(st.get("body", {}).get(k), d["body"][k], "M11 pending body " + k)
    # The actual Stage8 returns before append_experienced_reward if death
    # prevents a successful physical command. Do not fabricate terminal TD.
    end = generation if final_status == "active" else generation - 1
    expected_rewards = [rewards[t] for t in range(d["step"], end + 1)]
    actual_rewards = pending.get("rewards")
    if type(actual_rewards) is not list or len(actual_rewards) != len(expected_rewards):
        raise ValueError("M11 pending TD rewards count mismatch")
    for a, b in zip(actual_rewards, expected_rewards):
        _check(a, b, "M11 pending reward")
    return len(expected_rewards)


def replay_q(events, *, generation, status, mode, setpoints, weights,
             born_td, world_clock, final_td_state=None):
    """Pure full native Q recurrence, with optional final M11 snapshot parity.

    A missing snapshot may be used only in adversarial unit tests; such a
    result cannot claim full_q_replay_verified. Real-life entrypoints MUST
    provide state from the cold authenticated M11 current image.
    """
    if type(events) is not list or mode not in MODES:
        raise ValueError("invalid M11 A2-R replay input")
    beta, eta, lam, _ = birth_contract(born_td, world_clock)
    steps = physical_steps(events, generation=generation, status=status)
    physical = {row["step"]: row for row in steps}
    rewards = {
        t: reward(row["before"], row["after"], setpoints=setpoints,
                  weights=weights, mode=mode)
        for t, row in physical.items()
    }
    captures, proposals, competition, decisions, recurrences = {}, {}, {}, [], []
    bank, elig, counts = {}, {}, {}
    goal = None
    latest_capture = None
    last_update_step = 0
    residual = 0.
    native_q_checks = stage8 = links = learned = 0
    # Consequences can be read from complete signed M11 ledger, but event
    # sequence itself remains the authority for Q read/write chronology.
    for ev in events:
        if type(ev) is not dict:
            raise ValueError("invalid signed M11 event")
        kind, t, cycle, data = ev.get("kind"), ev.get("t_monde"), ev.get("cycle"), ev.get("data")
        if kind == "perceptual_capture":
            if t in captures:
                raise ValueError("duplicate perceived world capture")
            feature = features(ev, goal, world_clock=world_clock, born_td=born_td)
            if (t not in physical or
                    body(data["dual_scope_visible_body"]) != physical[t]["before"]):
                raise ValueError("first-person capture disagrees with applied body")
            captures[t] = ev
            latest_capture = ev
        elif kind == "active_goal_changed":
            if type(data) is not dict:
                raise ValueError("malformed M11 goal event")
            after = data.get("after")
            if after is not None and type(after) is not dict:
                raise ValueError("invalid M11 goal transition")
            goal = None if after is None else after.get("goal_type")
            if goal not in GOALS:
                raise ValueError("goal outside frozen P-32 feature contract")
        elif kind == "stage8_option_evaluation":
            if (type(t) is not int or not 1 <= t <= generation
                    or type(cycle) is not int or cycle < 1
                    or type(data) is not dict or latest_capture is None
                    or latest_capture["t_monde"] != t):
                raise ValueError("Stage8 read without authentic current perception")
            option, sig = data.get("option_ref"), data.get("learning_signature")
            if type(option) is not str or not option or type(sig) is not str or not sig:
                raise ValueError("missing Stage8 option/signature")
            key = (t, cycle, option)
            if key in proposals:
                raise ValueError("duplicate Stage8 evaluation")
            learned_now = counts.get(sig, 0) > 0
            if data.get("learned_value_status") != ("learned" if learned_now else "unlearned"):
                raise ValueError("Stage8 Q status conflicts with native TD update history")
            if learned_now:
                phi = features(latest_capture, goal, world_clock=world_clock, born_td=born_td)
                qval = _dot(bank[sig], phi)
                residual = max(residual, _check(
                    data.get("learned_value"), qval, "M11 Stage8 learned Q"))
                native_q_checks += 1
                learned += 1
            elif data.get("learned_value") is not None:
                raise ValueError("Stage8 publishes Q without prior learning")
            proposals[key] = {"signature": sig, "data": data}
            stage8 += 1
        elif kind == "competition_cycle":
            key = (t, cycle)
            if (type(t) is not int or type(cycle) is not int
                    or type(data) is not dict or type(data.get("traces")) is not list
                    or key in competition):
                raise ValueError("duplicate or malformed Competition cycle")
            seen = {}
            for trace in data["traces"]:
                if type(trace) is not dict or type(trace.get("option_ref")) is not str:
                    raise ValueError("malformed Competition trace")
                option = trace["option_ref"]
                original = proposals.get((t, cycle, option))
                if original is None or option in seen or type(trace.get("crossed")) is not bool:
                    raise ValueError("Competition option lacks Stage8 provenance")
                a, b = original["data"].get("evidence"), trace.get("evidence")
                if (a is None) != (b is None):
                    raise ValueError("Competition evidence presence differs from Stage8")
                if a is not None:
                    residual = max(residual, _check(
                        a, b, "Stage8-to-Competition evidence"))
                seen[option] = trace
                links += 1
            expected = {o for (s, c, o) in proposals if (s, c) == key}
            if set(seen) != expected:
                raise ValueError("Competition omitted a Stage8 option")
            competition[key] = seen
        elif kind == "command_admitted":
            if type(data) is not dict or data.get("source") != "decision":
                continue
            if type(t) is not int or type(data.get("option_ref")) is not str:
                raise ValueError("invalid decision admission")
            if not (latest_capture is not None and latest_capture["t_monde"] == t):
                raise ValueError("decision without same-step lived perception")
            matches = [
                (c, p) for (step, c, opt), p in proposals.items()
                if step == t and opt == data["option_ref"]
                and (step, c) in competition]
            if not matches or t in {d["step"] for d in decisions}:
                raise ValueError("decision has no unique Stage8/Competition path")
            chosen_cycle, chosen = matches[-1]
            trace = competition[(t, chosen_cycle)][data["option_ref"]]
            if not trace["crossed"] and data["option_ref"] != "permanent:attendre":
                raise ValueError("subthreshold nonfallback motor option")
            if (data.get("primitive") != physical[t]["action"]
                    or (data.get("command_hash") is not None and
                        data.get("command_hash") != next(
                            (ev2.get("command_hash") for ev2 in events
                             if ev2.get("kind") == "command_experienced"
                             and ev2.get("t_monde") == t), None))):
                raise ValueError("admitted decision does not match applied command")
            f = features(latest_capture, goal, world_clock=world_clock, born_td=born_td)
            body_now = body(latest_capture["data"]["dual_scope_visible_body"])
            pos = latest_capture["data"]["position"]
            step_in_day = (t - 1) % world_clock["day_steps"]
            time = "night" if world_clock["night_start_step"] <= step_in_day < (
                world_clock["night_start_step"] + world_clock["night_steps"]) else "day"
            decisions.append({
                "step": t, "cycle": chosen_cycle, "signature": chosen["signature"],
                "option": data["option_ref"], "features": f,
                "body": body_now, "x": pos["x"], "y": pos["y"],
                "goal": goal, "time": time,
                "competition_options": len(competition[(t, chosen_cycle)]),
            })
        elif kind == "td_update_published":
            if (type(data) is not dict or type(t) is not int
                    or len(decisions) < 2 or t <= last_update_step):
                raise ValueError("TD without two consecutive authenticated decisions")
            prev, nxt = decisions[-2:]
            if (t != nxt["step"] or physical[t]["status"] != "active"
                    or type(data.get("segment_length")) is not int
                    or data["segment_length"] != nxt["step"] - prev["step"]
                    or data.get("previous_signature") != prev["signature"]
                    or data.get("next_signature") != nxt["signature"]
                    or data.get("td_version") != TD_VERSION):
                raise ValueError("TD update does not follow a live chosen segment")
            n = nxt["step"] - prev["step"]
            ret = sum(beta ** i * rewards[v] for i, v in enumerate(
                range(prev["step"], nxt["step"])))
            qp = _dot(bank.get(prev["signature"], [0.] * 12), prev["features"])
            qn = _dot(bank.get(nxt["signature"], [0.] * 12), nxt["features"])
            delta = ret + beta ** n * qn - qp
            for field, expected in (("return_g", ret), ("q_previous", qp),
                                    ("q_next", qn), ("delta", delta)):
                residual = max(residual, _check(
                    data.get(field), expected, "M11 TD " + field))
            decay = (beta * lam) ** n
            for sig in elig:
                elig[sig] = [v * decay for v in elig[sig]]
            s = prev["signature"]
            old = elig.setdefault(s, [0.] * 12)
            elig[s] = [a + b for a, b in zip(old, prev["features"])]
            active = sorted(sig for sig, row in elig.items() if any(row))
            declared = data.get("updated_signatures")
            if (type(declared) is not list or len(declared) != len(set(declared))
                    or declared != active):
                raise ValueError("M11 TD eligibility signature list differs")
            for sig in active:
                z = elig[sig]
                w = bank.get(sig, [0.] * 12)
                bank[sig] = [a + eta * delta * e for a, e in zip(w, z)]
                counts[sig] = counts.get(sig, 0) + 1
            recurrences.append({"step": t, "segment_start": prev["step"],
                                "length": n, "previous_signature": s,
                                "next_signature": nxt["signature"],
                                "return_g": ret, "delta": delta,
                                "signatures_updated": tuple(active)})
            last_update_step = t
    # No update may be silently dropped from the ordinary live decision path.
    effective = [d for d in decisions if physical[d["step"]]["status"] == "active"]
    required_updates = [d["step"] for d in effective[1:]]
    if [r["step"] for r in recurrences] != required_updates:
        raise ValueError("missing or spurious native TD update(s)")
    if any((step, cycle) not in competition for step, cycle, _ in proposals):
        raise ValueError("Stage8 cycle omitted by Competition")
    if len(competition) == 0 and proposals:
        raise ValueError("Stage8 Q never reached Competition")
    if final_td_state is not None:
        replayed = {
            "weights": bank, "traces": elig, "counts": counts,
            "feature_version": born_td["feature_version"],
            "last_effective_decision": effective[-1] if effective else None,
        }
        pending_count = _state_check(
            replayed, final_td_state, generation=generation,
            final_status=status, rewards=rewards)
    else:
        pending_count = None
    return {
        "scope": "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
        "generation": generation, "status": status, "mode": mode,
        "td_updates": len(recurrences), "td_recurrences": recurrences,
        "native_q_checks": native_q_checks,
        "stage8_read_count": stage8, "stage8_competition_links": links,
        "learned_stage8_reads": learned,
        "applied_decisions": len(effective),
        "uncredited_lethal_step": status == "dead",
        "pending_rewards_checked": pending_count,
        "max_numeric_residual": residual,
        "q_weights": bank, "q_update_counts": counts,
        "decisions": decisions,
        "stage8_observations": [
            {"step": t, "cycle": c, "option": option,
             "signature": row["signature"],
             "status": row["data"]["learned_value_status"],
             "q": (None if row["data"]["learned_value"] is None
                   else numeric(row["data"]["learned_value"])),
             "competitors": len(competition.get((t, c), {}))}
            for (t, c, option), row in proposals.items()
        ],
        "full_q_replay_verified": final_td_state is not None,
        "birth_source_provenance_verified": False,
        "mechanism_exposed": False,
        "adaptive_learning_go": "NOT_ESTABLISHED",
    }


def cold_replay_m11(*, path, identity, mode, setpoints, weights,
                    born_td, world_clock, allow_incomplete=False):
    """Independently checked M11 ledger + final signed native Q image.

    Birth constants are caller-provided and NOT independently proven here:
    the preregistered 96-life cohort gate must check immutable source/preset
    SHA and both arms' born temperament/config. Even full Q replay cannot by
    itself authorize an experiment or mark L3.
    """
    from hashlib import sha256
    import json
    from pathlib import Path
    import sqlite3
    from urllib.parse import quote
    from i1_a2r_m11_cold import inspect_m11
    from i1lab.determinism import canonical_causal_bytes

    evidence = inspect_m11(path=path, identity=identity, mode=mode,
                           allow_incomplete=allow_incomplete)
    file = Path(path)
    db = sqlite3.connect(
        "file:" + quote(str(file.resolve()), safe="/") + "?mode=ro", uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        rec = db.execute(
            "SELECT generation,status,state_bytes,state_hash,journal_head "
            "FROM life_current WHERE slot=1").fetchone()
        anchor = evidence["receipt"]
        if (rec is None or (rec[0], rec[1], rec[3], rec[4]) !=
                (anchor["generation"], anchor["status"], anchor["state_hash"],
                 anchor["journal_head"]) or type(rec[2]) is not bytes
                or sha256(rec[2]).hexdigest() != rec[3]):
            raise ValueError("cold M11 image moved since source audit")
        image = json.loads(rec[2])
        if canonical_causal_bytes(image) != rec[2]:
            raise ValueError("changed M11 current causal image")
    finally:
        db.close()
    owner = image["owners"]["value_needs"]
    if not isinstance(owner, dict) or not isinstance(owner.get("td_values"), dict):
        raise ValueError("no final M11 Value/Needs TD owner")
    result = replay_q(
        evidence["events"], generation=anchor["generation"],
        status=anchor["status"], mode=mode, setpoints=setpoints,
        weights=weights, born_td=born_td, world_clock=world_clock,
        final_td_state=owner["td_values"])
    return {
        **result,
        "m11_journal_head": anchor["journal_head"],
        "m11_state_hash": anchor["state_hash"],
        "m11_identity": identity,
        "m11_owner_version": evidence["owner"]["owner_config_version"],
        "birth_source_provenance_verified": False,
        "study_admissible": bool(evidence["analysis_admissible"]),
    }
