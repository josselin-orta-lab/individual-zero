"""Falsifiable, read-only 12-feature A1-C TD/Q/Stage8/Competition replay.

Frozen source: Actions 40944104333, SHA 26f7929b6db43f68e78b0cc0d9c67e7444f924c6.
M11 hash custody is a separate mandatory prerequisite. No new births, simulated
physics, action overrides, reward tuning or automatic scientific GO.
"""
from math import isfinite

FROZEN_SOURCE_SHA = "26f7929b6db43f68e78b0cc0d9c67e7444f924c6"
FROZEN_RUN_ID = 40944104333
FROZEN_TD_VERSION = "p31-stage8-reference-v1"
FROZEN_FEATURES = (
    "bias", "energy", "food", "water", "integrity", "x", "y", "is_night",
    "goal_drink", "goal_eat", "goal_recover_energy", "goal_restore_integrity",
)
VALID_GOALS = {None, "drink", "eat", "recover_energy", "restore_integrity"}
VALID_MODES = {"canonical", "td_read_masked"}


def numeric(value):
    if type(value) is dict and set(value) == {"$f64"}:
        result = float.fromhex(value["$f64"])
        if result.hex().lower() != value["$f64"]:
            raise ValueError("non-canonical M11 float")
    elif type(value) in (int, float):
        result = float(value)
    else:
        raise ValueError("non-numeric M11 value")
    if not isfinite(result):
        raise ValueError("non-finite M11 value")
    return result


def _close(actual, calculated, label):
    if abs(actual - calculated) > 2e-10 * max(1., abs(actual), abs(calculated)):
        raise ValueError("%s M11=%r replay=%r" % (label, actual, calculated))
    return abs(actual - calculated)


def p32_features(capture, goal):
    if goal not in VALID_GOALS or capture.get("kind") != "perceptual_capture":
        raise ValueError("not an authenticated P-32 context")
    data = capture["data"]
    step = data["capture_t_monde"]
    if type(step) is not int or not 1 <= step <= 48 or step != capture["t_monde"]:
        raise ValueError("P-32 capture outside frozen horizon")
    raw = data["dual_scope_visible_body"]
    pos = data["position"]
    if set(raw) != {"energy", "food", "water", "integrity"} or set(pos) != {"x", "y"}:
        raise ValueError("incomplete first-person P-32 state")
    if any(type(pos[k]) is not int or not 0 <= pos[k] <= 31 for k in ("x", "y")):
        raise ValueError("outside physical world")
    body = {k: numeric(v) for k, v in raw.items()}
    if any(not 0 <= n <= 100 for n in body.values()):
        raise ValueError("invalid body")
    # A1-C H48, source-specific P-32 day/night configuration: all 48 are day.
    values = {
        "bias": 1., "energy": body["energy"] / 100.,
        "food": body["food"] / 100., "water": body["water"] / 100.,
        "integrity": body["integrity"] / 100.,
        "x": pos["x"] / 31., "y": pos["y"] / 31.,
        "is_night": 0.,
        "goal_drink": float(goal == "drink"),
        "goal_eat": float(goal == "eat"),
        "goal_recover_energy": float(goal == "recover_energy"),
        "goal_restore_integrity": float(goal == "restore_integrity"),
    }
    return tuple(values[n] for n in FROZEN_FEATURES)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def replay_life(events, *, born_td, mode):
    """Check native TD numerics, Q publications and Stage8/Competition links.

    Returns post-meal *update-only* impact on collection Q at the TD next
    decision state. This is not a proven physical benefit. In the masked arm
    native Q updates continue, while Stage8 shows "unlearned".
    """
    if type(events) is not list or mode not in VALID_MODES:
        raise ValueError("invalid A1-C M11 input")
    if type(born_td) is not dict or born_td.get("version") != FROZEN_TD_VERSION:
        raise ValueError("TD configuration not attested for frozen source")
    beta, lam, eta = (numeric(born_td.get(k)) for k in ("beta", "lambda_e", "eta"))
    if (beta, lam, eta) != (.8, .8, .05):
        raise ValueError("not the exact source-specific born TD")
    weights, traces, counts = {}, {}, {}
    goal, capture = None, None
    published, cycles, competitions = {}, {}, {}
    experienced, transitions = {}, {}
    last_state = last_sig = decision = None
    decisions = updates = stage8 = q_checks = masked = links = crossed = fallbacks = snapshots = 0
    maximal_error = 0.
    meals, postmeal = [], []
    for event in events:
        if type(event) is not dict:
            raise ValueError("invalid M11 event")
        kind, step, cycle = event.get("kind"), event.get("t_monde"), event.get("cycle")
        if type(step) is not int or not 1 <= step <= 48:
            raise ValueError("event outside source horizon")
        data = event.get("data")
        if kind == "perceptual_capture":
            if capture is not None and step <= capture["t_monde"]:
                raise ValueError("out of order capture")
            capture = event
        elif kind == "active_goal_changed":
            if type(data) is not dict:
                raise ValueError("invalid goal transition")
            after = data["after"]
            goal = after["goal_type"] if after is not None else None
            if goal not in VALID_GOALS:
                raise ValueError("unknown active goal")
        elif kind == "stage8_option_evaluation":
            if capture is None or capture["t_monde"] != step:
                raise ValueError("Stage8 has no same-step capture")
            if type(cycle) is not int or cycle < 1 or type(data) is not dict:
                raise ValueError("invalid Stage8 cycle")
            ref, sig = data.get("option_ref"), data.get("learning_signature")
            if not isinstance(ref, str) or not ref or not isinstance(sig, str) or not sig:
                raise ValueError("invalid Stage8 option")
            key = (step, cycle, ref)
            if key in published:
                raise ValueError("duplicate Stage8")
            expected = "learned" if mode == "canonical" and counts.get(sig, 0) else "unlearned"
            if data.get("learned_value_status") != expected:
                raise ValueError("Stage8 learned/masked status inconsistent with TD")
            if expected == "learned":
                q = dot(weights.get(sig, (0.,) * 12), p32_features(capture, goal))
                maximal_error = max(maximal_error, _close(numeric(data["learned_value"]), q, "Stage8 native Q"))
                q_checks += 1
            elif data.get("learned_value") is not None:
                raise ValueError("unlearned or masked Stage8 leaked Q")
            if counts.get(sig, 0) and mode == "td_read_masked":
                masked += 1
            published[key] = sig
            group = cycles.setdefault((step, cycle), {})
            group[ref] = data.get("evidence")
            stage8 += 1
        elif kind == "competition_cycle":
            key = (step, cycle)
            if key in competitions or type(data) is not dict or type(data.get("traces")) is not list:
                raise ValueError("duplicate/invalid Competition cycle")
            group = cycles.get(key, {})
            traces_in = {}
            for trace in data["traces"]:
                if type(trace) is not dict or trace.get("option_ref") not in group:
                    raise ValueError("Competition option without Stage8 evidence")
                ref = trace["option_ref"]
                if ref in traces_in:
                    raise ValueError("duplicate Competition trace")
                left, right = group[ref], trace.get("evidence")
                if (left is None) != (right is None):
                    raise ValueError("Stage8/Competition null evidence mismatch")
                if left is not None:
                    maximal_error = max(maximal_error, _close(numeric(left), numeric(right),
                                                               "Stage8/Competition evidence"))
                if type(trace.get("crossed")) is not bool:
                    raise ValueError("invalid threshold evidence")
                traces_in[ref] = trace
                links += 1
            if set(traces_in) != set(group):
                raise ValueError("Competition omitted an evaluated option")
            competitions[key] = traces_in
        elif kind == "command_admitted":
            if type(data) is not dict:
                raise ValueError("invalid motor admission")
            if data.get("source") != "decision":
                continue
            if capture is None or capture["t_monde"] != step:
                raise ValueError("decision lacking perceptual input")
            ref = data.get("option_ref")
            matches = [((t, c), sig) for (t, c, o), sig in published.items()
                       if t == step and o == ref]
            if not matches:
                raise ValueError("motor admission lacking Stage8 proposal")
            (_, chosen_cycle), sig = matches[-1]
            if (step, chosen_cycle) not in competitions:
                raise ValueError("admitted option lacks Competition trace")
            trace = competitions[(step, chosen_cycle)][ref]
            if trace["crossed"]:
                crossed += 1
            elif ref == "permanent:attendre":
                fallbacks += 1
            else:
                raise ValueError("motor selected non-fallback option below threshold")
            decision = (step, sig, p32_features(capture, goal))
            decisions += 1
            if last_state is None:
                last_sig, last_state = sig, decision[2]
        elif kind == "command_experienced":
            if step in experienced:
                raise ValueError("duplicate experienced command")
            experienced[step] = event
            if event.get("primitive") == "manger":
                berry = event.get("parameters", {}).get("target")
                if berry not in ("berry_a", "berry_b"):
                    raise ValueError("invalid ingestion")
                meals.append((step, berry))
        elif kind == "world_transition_experienced":
            if step in transitions:
                raise ValueError("duplicate physical transition")
            transitions[step] = event
            if capture is not None and capture["t_monde"] == step:
                physical = event["body_before"]
                perceived = capture["data"]["dual_scope_visible_body"]
                if set(physical) != set(perceived):
                    raise ValueError("body custody mismatch")
                for key in perceived:
                    maximal_error = max(maximal_error, _close(numeric(physical[key]),
                                      numeric(perceived[key]), "body capture mismatch"))
        elif kind == "td_update_published":
            if (type(data) is not dict or decision is None or
                    decision[0] != step or last_state is None):
                raise ValueError("TD without corresponding decision")
            _, next_sig, next_state = decision
            if (data.get("previous_signature"), data.get("next_signature")) != (last_sig, next_sig):
                raise ValueError("TD transition does not follow actual decisions")
            if data.get("td_version") != FROZEN_TD_VERSION:
                raise ValueError("TD owner version mismatch")
            n = data.get("segment_length")
            if type(n) is not int or n < 1:
                raise ValueError("invalid segment length")
            qp = dot(weights.get(last_sig, (0.,) * 12), last_state)
            qn = dot(weights.get(next_sig, (0.,) * 12), next_state)
            delta = numeric(data["return_g"]) + beta ** n * qn - qp
            for field, expected in (("q_previous", qp), ("q_next", qn), ("delta", delta)):
                maximal_error = max(maximal_error,
                                    _close(numeric(data[field]), expected, "native TD " + field))
                snapshots += 1
            decay = (beta * lam) ** n
            for sig in traces:
                traces[sig] = [v * decay for v in traces[sig]]
            current = traces.setdefault(last_sig, [0.] * 12)
            traces[last_sig] = [a + b for a, b in zip(current, last_state)]
            declared = data.get("updated_signatures")
            if (type(declared) is not list or len(declared) != len(set(declared)) or
                    set(declared) != {s for s, v in traces.items() if any(v)}):
                raise ValueError("native TD eligibility signature mismatch")
            for sig in sorted(traces):
                v = traces[sig]
                if any(v):
                    old = weights.get(sig, [0.] * 12)
                    weights[sig] = [a + eta * delta * b for a, b in zip(old, v)]
                    counts[sig] = counts.get(sig, 0) + 1
            updates += 1
            last_sig, last_state = next_sig, next_state
            if step - 1 in experienced:
                action = experienced[step - 1]
                berry = action.get("parameters", {}).get("target")
                if action.get("primitive") == "manger" and berry in ("berry_a", "berry_b"):
                    if data["previous_signature"] != "i1:affordance:manger:target=" + berry:
                        raise ValueError("TD ingestion signature unrelated to experienced action")
                    collection = "i1:affordance:collecter:target=" + berry
                    if collection not in declared:
                        raise ValueError("ingestion lacks related collection trace")
                    z = traces[collection]
                    changed = [eta * delta * x for x in z]
                    postmeal.append({
                        "ingestion_step": step - 1, "td_step": step,
                        "berry": berry, "collect_trace_bias": z[0],
                        "collect_trace_l2_norm": sum(x*x for x in z) ** .5,
                        "collect_update_bias": changed[0],
                        "collect_update_q_at_td_next_state": dot(changed, next_state),
                    })
    if set(experienced) != set(range(1, 49)) or set(transitions) != set(experienced):
        raise ValueError("incomplete physical A1-C history")
    if updates != decisions - 1:
        raise ValueError("TD and actual decision counts disagree")
    if len(competitions) != len(cycles) or links != stage8:
        raise ValueError("Stage8 to Competition chain incomplete")
    if len(meals) - len(postmeal) not in (0, 1):
        raise ValueError("unexplained missing postmeal TD")
    if len(meals) - len(postmeal) == 1 and meals[-1][0] != 48:
        raise ValueError("postmeal TD missing before censor")
    return {
        "scope": "FROZEN_A1C_POSTHOC_FULL_VECTOR_M11_Q_NOT_L3",
        "native_m11_q_checks": q_checks,
        "masked_stage8_consistency_checks": masked,
        "td_snapshot_q_and_delta_checks": snapshots,
        "td_updates": updates, "decisions": decisions,
        "stage8_to_competition_links": links,
        "motor_selected_crossed": crossed, "motor_wait_fallback": fallbacks,
        "ingestions": len(meals), "postmeal_td": len(postmeal),
        "max_m11_numeric_residual": maximal_error,
        "postmeal": postmeal,
        "a1c_status": "NO_GO", "general_L3": "NOT_ESTABLISHED",
    }
