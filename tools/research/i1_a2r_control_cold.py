"""Independent A2-R M11 Competition -> Action Control -> applied command audit.

Validates the chronology and command identity of already signed M11 receipts,
the cold Q/TD decision replay and a source-reconstructed birth policy version.
It DOES NOT recompute every safety predicate or prove counterfactual Q motor
mediation, nor certify absence of a rollback from truncated histories.
"""
from __future__ import annotations

import re
from math import exp, isclose

from i1_a2r_m11_cold import numeric, physical_steps

_RULES = {
    "known_lethal_zone": ("option", "lethal_zone_movement", "semantic_prohibition"),
    "known_toxic_item": ("option", "toxic_item_consumption", "semantic_prohibition"),
    "protected_integrity_violation": (
        "option", "protected_invariant_violation", "protected_invariant"),
    "protocol_mask": ("protocol", "rollback_sequence_mask", "protocol"),
}
_Q_SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
_BIRTH_SCOPE = "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SOURCES = frozenset(("decision", "reflex", "stage3_wait_stub"))


def _verify_native_equation(traces, *, cycle, born_calibration):
    """Recompute source-born accumulator equations from signed before states.

    Before values remain native receipts, NOT independently restored owner
    state. Native selection/retention of candidates remains unproven.
    """
    fields = ("urgency_max", "urgency_scale_cycles", "leak", "gain",
              "noise_sigma", "base_threshold", "threshold_floor", "inertia")
    if type(born_calibration) is not dict or any(
            key not in born_calibration for key in fields):
        raise ValueError("missing source-born Competition calibration")
    p = {key: numeric(born_calibration[key]) for key in fields}
    if (p["noise_sigma"] != 0 or p["urgency_max"] < 1
            or p["urgency_scale_cycles"] <= 0
            or not 0 <= p["leak"] < 1 or p["gain"] <= 0
            or p["threshold_floor"] <= 0
            or p["base_threshold"] <= p["threshold_floor"]
            or not 0 <= p["inertia"] <=
            p["base_threshold"] - p["threshold_floor"]):
        raise ValueError("unverifiable Competition formula or nonzero noise")
    urgency = 1 + (p["urgency_max"] - 1) * (
        1 - exp(-(cycle - 1) / p["urgency_scale_cycles"]))
    verified = 0
    for trace in traces.values():
        before = numeric(trace.get("accumulator_before"))
        after = numeric(trace.get("accumulator_after"))
        threshold = numeric(trace.get("threshold"))
        evidence = trace.get("evidence")
        if evidence is None:
            if not isclose(before, after, rel_tol=2e-9, abs_tol=2e-9):
                raise ValueError("unevaluated native accumulator was modified")
            continue
        e = numeric(evidence)
        expected = max(0., (1-p["leak"])*before + urgency*p["gain"]*e)
        if not isclose(after, expected, rel_tol=2e-9, abs_tol=2e-9):
            raise ValueError("native Competition accumulator recurrence mismatch")
        permitted = (p["base_threshold"],
                     max(p["threshold_floor"],
                         p["base_threshold"]-p["inertia"]))
        if not any(isclose(threshold, v, rel_tol=2e-9, abs_tol=2e-9)
                   for v in permitted):
            raise ValueError("Competition threshold differs from source birth")
        verified += 1
    return verified


def _native_crossed_rank(traces, *, step, cycle, signatures):
    """Reconstruct only the published-margin ranking, NOT its causal inputs.

    Tie-breaking uses the original Stage8 learning signature, checked by the
    independent cold Q replay. Accumulator values still belong to the native
    Competition receipt, so this is NOT an independent rank/state replay.
    """
    ranked = []
    for option, trace in traces.items():
        key = (step, cycle, option)
        if key not in signatures:
            raise ValueError("ranked candidate has no cold Stage8 signature")
        before = numeric(trace.get("accumulator_before"))
        after = numeric(trace.get("accumulator_after"))
        threshold = numeric(trace.get("threshold"))
        if threshold <= 0 or before < 0 or after < 0:
            raise ValueError("invalid Competition accumulator or threshold")
        raw_evidence = trace.get("evidence")
        if raw_evidence is None:
            if trace["crossed"] or after != before:
                raise ValueError("unevaluated candidate mutated or crossed")
        else:
            evidence = numeric(raw_evidence)
            if (not -1 <= evidence <= 1
                    or trace["crossed"] != (after >= threshold)):
                raise ValueError("Competition threshold crossing conflicts with trace")
        if trace["crossed"]:
            ranked.append((-(after - threshold) / threshold,
                           signatures[key], option))
    return tuple(row[2] for row in sorted(ranked))


def audit_native_action_control(events, *, q_replay, birth):
    """Reconcile ALL physical commands, decision admissions and ordered vetoes.

    Inputs MUST be the immutable M11 stream from inspect_m11 and the separately
    fully cold-verified Q replay. We check the order in which crossed candidates
    were actually challenged against signed margins and Stage8 identities.
    The safety reason itself is only a receipt:
    learned Causal Model facts, primitive protocol masks and candidate ranking
    are NOT independently reconstructed by this observer.
    """
    if (type(events) is not list or type(q_replay) is not dict
            or type(birth) is not dict
            or q_replay.get("scope") != _Q_SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or q_replay.get("adaptive_learning_go") != "NOT_ESTABLISHED"
            or q_replay.get("birth_source_provenance_verified") is not False
            or birth.get("scope") != _BIRTH_SCOPE
            or birth.get("q_at_birth_empty") is not True
            or birth.get("identity") != q_replay.get("m11_identity")
            or birth.get("mode") != q_replay.get("mode")):
        raise ValueError("Action Control proof requires cold Q and source-born identity")
    version = birth.get("action_control_policy_version")
    if type(version) is not str or not version:
        raise ValueError("missing independently pinned Action Control policy version")
    calibration = birth.get("competition_calibration")
    generation = q_replay.get("generation")
    status = q_replay.get("status")
    steps = physical_steps(events, generation=generation, status=status)
    actual = {s["step"]: s for s in steps}
    expected_decisions = {}
    original_signatures = {}
    observations = q_replay.get("stage8_observations")
    if type(observations) is not list:
        raise ValueError("missing cold Stage8 candidate identities for ranking")
    for observation in observations:
        if (type(observation) is not dict
                or type(observation.get("step")) is not int
                or type(observation.get("cycle")) is not int
                or type(observation.get("option")) is not str
                or not observation["option"]
                or type(observation.get("signature")) is not str
                or not observation["signature"]):
            raise ValueError("invalid cold Stage8 candidate identity")
        key = (observation["step"], observation["cycle"],
               observation["option"])
        if key in original_signatures:
            raise ValueError("duplicated cold Stage8 candidate identity")
        original_signatures[key] = observation["signature"]
    if type(q_replay.get("decisions")) is not list:
        raise ValueError("missing cold native Q decision occurrences")
    for row in q_replay["decisions"]:
        if (type(row) is not dict or type(row.get("step")) is not int
                or type(row.get("cycle")) is not int
                or type(row.get("option")) is not str
                or row["step"] not in actual or row["step"] in expected_decisions):
            raise ValueError("duplicated or invalid cold native motor decision")
        expected_decisions[row["step"]] = (
            row["cycle"], row["option"])

    competition = {}
    competition_orders = {}
    latest_competition = {}
    control = {}
    experienced = {}
    vetoes = []
    admitted_decisions = {}
    decision_attempts = {}
    reflex_or_other = []
    attempts = 0
    for order, ev in enumerate(events):
        if type(ev) is not dict:
            raise ValueError("non-dictionary original M11 event")
        kind, t, data = ev.get("kind"), ev.get("t_monde"), ev.get("data")
        if kind == "competition_cycle":
            cycle = ev.get("cycle")
            if (type(t) is not int or t not in actual
                    or type(cycle) is not int or cycle < 1
                    or type(data) is not dict or type(data.get("traces")) is not list
                    or (t, cycle) in competition
                    or (t in latest_competition
                        and cycle <= latest_competition[t][0])):
                raise ValueError("invalid Competition chronological occurrence")
            traces = {}
            for tr in data["traces"]:
                if (type(tr) is not dict or type(tr.get("option_ref")) is not str
                        or not tr["option_ref"] or
                        type(tr.get("crossed")) is not bool
                        or tr["option_ref"] in traces):
                    raise ValueError("invalid or duplicate Competition trace")
                traces[tr["option_ref"]] = tr
            competition[(t, cycle)] = traces
            competition_orders[(t, cycle)] = order
            latest_competition[t] = (cycle, order)
        elif kind in ("command_admitted", "command_vetoed"):
            if (type(t) is not int or t not in actual or type(data) is not dict
                    or data.get("source") not in _SOURCES
                    or type(data.get("primitive")) is not str
                    or not data["primitive"]
                    or type(data.get("command_hash")) is not str
                    or _SHA256.fullmatch(data["command_hash"]) is None
                    or data.get("policy_version") != version):
                raise ValueError("unsigned/foreign Action Control decision receipt")
            if kind == "command_admitted":
                if any(data.get(f) is not None for f in (
                        "reason", "scope", "rule_id", "rule_type")):
                    raise ValueError("admitted command has a veto restriction")
            else:
                reason = data.get("reason")
                if reason not in _RULES or tuple(
                        data.get(f) for f in ("scope", "rule_id", "rule_type")
                ) != _RULES[reason]:
                    raise ValueError("inconsistent Action Control veto receipt")
            attempts += 1
            control.setdefault(t, []).append((kind, data, order))
            if data["source"] != "decision":
                if kind == "command_admitted":
                    reflex_or_other.append((t, data["source"]))
                continue
            option = data.get("option_ref")
            if type(option) is not str or not option:
                raise ValueError("decision Action Control receipt has no option")
            latest = latest_competition.get(t)
            if latest is None or latest[1] >= order:
                raise ValueError("decision Action Control attempted before Competition")
            cycle = latest[0]
            trace = competition[(t, cycle)].get(option)
            if trace is None:
                raise ValueError("Action Control option absent from current Competition")
            decision_attempts.setdefault((t, cycle), []).append(
                (kind, option))
            if kind == "command_vetoed":
                if not trace["crossed"] and option != "permanent:attendre":
                    raise ValueError("vetoed nonfallback option did not cross threshold")
                vetoes.append({
                    "step": t, "cycle": cycle, "option": option,
                    "reason": data["reason"],
                    "crossed": trace["crossed"],
                })
            else:
                if t in admitted_decisions:
                    raise ValueError("multiple admitted decision commands in one M11 step")
                admitted_decisions[t] = (cycle, option, data, order)
        elif kind == "command_experienced":
            if (type(t) is not int or t not in actual or t in experienced
                    or type(ev.get("command_hash")) is not str
                    or _SHA256.fullmatch(ev["command_hash"]) is None):
                raise ValueError("missing or repeated original physical command")
            experienced[t] = (ev, order)

    if set(experienced) != set(actual):
        raise ValueError("missing physical command experiences")
    recurrence_verified = sum(
        _verify_native_equation(traces, cycle=key[1],
                                born_calibration=calibration)
        for key, traces in competition.items()
    )
    native_ranked = {
        key: _native_crossed_rank(
            traces, step=key[0], cycle=key[1],
            signatures=original_signatures)
        for key, traces in competition.items()
    }
    native_keys = {
        (step, cycle, option)
        for (step, cycle), traces in competition.items()
        for option in traces
    }
    if set(original_signatures) != native_keys:
        raise ValueError("cold Stage8 candidates and Competition traces differ")
    attempted_crossed = 0
    unproven_fallbacks = 0
    for key, sequence in decision_attempts.items():
        ranked = native_ranked[key]
        for index, (_kind, option) in enumerate(sequence):
            if index < len(ranked):
                if option != ranked[index]:
                    raise ValueError(
                        "Action Control skipped a higher-ranked crossed option")
                attempted_crossed += 1
            else:
                # Stage4 may retry the engaged plan and then permanent wait
                # after exhausting ranked options at the last cycle. The
                # signed trace is NOT proof that these fallback options were
                # truly engaged or that the budget legally reached c_max.
                if len(sequence) > len(ranked) + 2:
                    raise ValueError("more than two unverified fallback attempts")
                unproven_fallbacks += 1
    # Both journal emitters attach the world-step attempt reference. The
    # matching physical receipt is the independent anchor: a signed event
    # from a different attempt at the same step must never be joined.
    for ev in events:
        if ev.get("kind") not in (
                "competition_cycle", "command_admitted", "command_vetoed"):
            continue
        step = ev.get("t_monde")
        if (step not in experienced
                or ev.get("attempt_ref") !=
                   experienced[step][0].get("attempt_ref")):
            raise ValueError("Action Control and physical attempt owners differ")
    if any(position >= experienced[step][1]
           for (step, _cycle), position in competition_orders.items()):
        raise ValueError("Competition was recorded after physical execution")
    if set(admitted_decisions) != set(expected_decisions):
        raise ValueError("decision admission set differs from independently cold Q")
    other_executed = 0
    for t, (physical, position) in experienced.items():
        candidates = [
            (kind, data) for kind, data, order in control.get(t, [])
            if kind == "command_admitted" and order < position
            and data["command_hash"] == physical["command_hash"]]
        if len(candidates) != 1:
            raise ValueError("physical M11 command lacks UNIQUE prior Action Control admission")
        _, data = candidates[0]
        if (data["primitive"] != physical.get("primitive")
                or data["primitive"] != actual[t]["action"]):
            raise ValueError("original physical primitive differs from admitted command")
        if any(order > position for _, _, order in control.get(t, [])):
            raise ValueError("control attempts happened after the physical action")
        if data["source"] != "decision":
            if t in expected_decisions:
                raise ValueError("reflex/stub execution disguised as learned decision")
            other_executed += 1
        else:
            current = admitted_decisions.get(t)
            if (current is None or current[2] is not data
                    or current[:2] != expected_decisions[t]):
                raise ValueError("executed decision not the admitted Competition winner")
            if not competition[(t, current[0])][current[1]]["crossed"]:
                if current[1] != "permanent:attendre":
                    raise ValueError("unthresholded non-wait motor execution")
            if current[3] >= position:
                raise ValueError("command admitted after physical execution")

    for t, history in control.items():
        admitted = [(k, d, pos) for k,d,pos in history if k == "command_admitted"]
        # Distinct earlier control admissions may represent an interrupted
        # rollback. Without an independently replayed rollback, fail closed.
        if len(admitted) != 1:
            raise ValueError("unreplayed extra Action Control admission or rollback")
        if history[-1][0] != "command_admitted":
            raise ValueError("veto follows the physical winning admission")
        for kind, data, pos in history:
            if (kind == "command_vetoed" and data["source"] == "decision"
                    and t in admitted_decisions
                    and pos >= admitted_decisions[t][3]):
                raise ValueError("ranked decision veto occurred after winning admission")

    return {
        "scope": "A2R_COLD_NATIVE_ACTION_CONTROL_PATH_NOT_L3",
        "physical_experiences_with_prior_admission": len(experienced),
        "native_q_decisions_joined_to_admission": len(admitted_decisions),
        "control_attempts_checked": attempts,
        "ranked_option_veto_receipts_reconciled": len(vetoes),
        "veto_examples": vetoes[:8],
        "veto_occurrences": vetoes,
        "admitted_decision_occurrences": [
            {"step": step, "cycle": entry[0], "option": entry[1],
             "primitive": entry[2]["primitive"],
             "command_hash": entry[2]["command_hash"]}
            for step, entry in sorted(admitted_decisions.items())
        ],
        "nondecision_motor_sources": other_executed,
        "policy_version_matches_source_birth": True,
        "all_motor_receipts_matched": True,
        "native_crossing_and_rank_prefix_consistent": True,
        "native_accumulator_equations_verified": recurrence_verified,
        "native_before_states_not_independently_restored": True,
        "crossed_ranked_control_attempts": attempted_crossed,
        "unproven_fallback_attempts": unproven_fallbacks,
        "native_rank_is_not_independent_state_replay": True,
        "veto_truth_independently_recomputed": False,
        "full_rank_order_independently_recomputed": False,
        "Q_to_action_counterfactual_proven": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }


def audit_native_wait_continuity(
    events, *, q_replay, birth, control, final_competition,
):
    """Check the permanently offered wait candidate's persisted continuity.

    This source-specific proof starts only AFTER the M11 event chain, cold Q,
    the Action Control motor join and source-born birth were audited. Its
    calculations cannot recover arbitrary option semantic refreshes, prior
    engaged owners, unlogged mutations or true safety predicates.
    """
    from math import isclose

    if (type(events) is not list or type(q_replay) is not dict
            or type(birth) is not dict or type(control) is not dict
            or type(final_competition) is not dict
            or q_replay.get("scope") != _Q_SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or q_replay.get("m11_identity") != birth.get("identity")
            or q_replay.get("mode") != birth.get("mode")
            or birth.get("scope") != _BIRTH_SCOPE
            or control.get("scope") != "A2R_COLD_NATIVE_ACTION_CONTROL_PATH_NOT_L3"
            or control.get("all_motor_receipts_matched") is not True
            or control.get("native_crossing_and_rank_prefix_consistent") is not True):
        raise ValueError("wait continuity needs verified signed M11 motor inputs")
    calibration = birth.get("competition_calibration")
    if type(calibration) is not dict:
        raise ValueError("missing source-born Competition calibration")
    residual = numeric(calibration.get("residual"))
    if not 0 < residual < 1:
        raise ValueError("invalid born residual")
    if final_competition.get("config_version") != calibration.get("version"):
        raise ValueError("final Competition owner has foreign source version")
    def close(a, b):
        return isclose(numeric(a), numeric(b), rel_tol=2e-9, abs_tol=2e-9)

    wait = "permanent:attendre"
    steps = {}
    disturbances = []
    for order, ev in enumerate(events):
        if type(ev) is not dict:
            raise ValueError("invalid native event in wait continuity")
        kind, t, data = ev.get("kind"), ev.get("t_monde"), ev.get("data")
        if (kind == "command_vetoed" and type(data) is dict
                and data.get("option_ref") == wait
                and data.get("scope") == "option"):
            disturbances.append(order)
        if (type(kind) is str and kind.endswith("option_registration")
                and type(data) is dict and data.get("option_ref") == wait
                and data.get("registered") is True):
            disturbances.append(order)
        if kind != "competition_cycle":
            continue
        if (type(t) is not int or type(ev.get("cycle")) is not int
                or type(data) is not dict or type(data.get("traces")) is not list):
            raise ValueError("invalid wait Competition occurrence")
        candidates = [
            row for row in data["traces"]
            if type(row) is dict and row.get("option_ref") == wait
        ]
        if len(candidates) != 1:
            raise ValueError("native Competition omitted permanent wait")
        row = candidates[0]
        before = numeric(row.get("accumulator_before"))
        after = numeric(row.get("accumulator_after"))
        threshold = numeric(row.get("threshold"))
        if before < 0 or after < 0 or threshold <= 0:
            raise ValueError("invalid persistent wait accumulator")
        current = (order, ev["cycle"], before, after, threshold)
        if t in steps and ev["cycle"] <= steps[t][-1][1]:
            raise ValueError("wait Competition cycle not monotonic")
        steps.setdefault(t, []).append(current)
    if any(i >= j for i,j in zip(sorted(steps),list(sorted(steps))[1:])):
        raise ValueError("wait Competition step order invalid")
    def disturbed(start, end):
        return any(start < pos < end for pos in disturbances)
    within_checked = adjacent_checked = quarantined = 0
    for t, rows in sorted(steps.items()):
        for earlier, later in zip(rows, rows[1:]):
            if disturbed(earlier[0], later[0]):
                quarantined += 1
            elif not close(earlier[3], later[2]):
                raise ValueError("persistent wait accumulator changed between paid cycles")
            else:
                within_checked += 1

    admissions = control.get("admitted_decision_occurrences")
    if type(admissions) is not list:
        raise ValueError("missing authenticated admitted decisions")
    winners = {}
    for row in admissions:
        if (type(row) is not dict or type(row.get("step")) is not int
                or type(row.get("cycle")) is not int
                or type(row.get("option")) is not str
                or row["step"] in winners):
            raise ValueError("invalid wait-continuity decision identity")
        winners[row["step"]] = row
    for t in sorted(steps):
        if t + 1 not in steps or t not in winners:
            continue
        former, latter = steps[t][-1], steps[t+1][0]
        if disturbed(former[0], latter[0]):
            quarantined += 1
            continue
        if winners[t]["cycle"] != former[1]:
            raise ValueError("decision not anchored to final step Competition cycle")
        expected = (0.0 if winners[t]["option"] == wait
                    else former[3] * residual)
        if not close(expected, latter[2]):
            raise ValueError("wait accumulation continuity broken after physical decision")
        adjacent_checked += 1

    anchor_checked = False
    generation = q_replay.get("generation")
    if (type(generation) is not int or generation < 1
            or q_replay.get("status") not in ("active", "dead")):
        raise ValueError("wait continuity has invalid M11 terminal generation")
    if generation in steps and generation in winners and q_replay["status"] == "active":
        final = steps[generation][-1]
        if not any(pos > final[0] for pos in disturbances):
            winner = winners[generation]
            if (winner["cycle"] != final[1]
                    or final_competition.get("cycle") != final[1]
                    or final_competition.get("engaged_option_id") != winner["option"]):
                raise ValueError("sealed Competition owner winner/cycle differs from action")
            registry = final_competition.get("registry")
            if type(registry) is not list:
                raise ValueError("missing sealed Competition registry")
            matches = [
                row for row in registry
                if type(row) is dict and type(row.get("proposal")) is dict
                and type(row["proposal"].get("option")) is dict
                and row["proposal"]["option"].get("id") == wait
            ]
            if len(matches) != 1:
                raise ValueError("sealed Competition lacks unique persistent wait")
            actual = matches[0]
            expected = (final[3] if winner["option"] == wait
                        else final[3] * residual)
            if (not close(actual.get("accumulator"), expected)
                    or not close(actual.get("last_threshold"), final[4])):
                raise ValueError("signed last wait cycle conflicts with sealed owner")
            anchor_checked = True

    return {
        "scope": "A2R_NATIVE_PERMANENT_WAIT_CONTINUITY_ONLY_NOT_L3",
        "same_step_wait_carry_checks": within_checked,
        "adjacent_applied_step_wait_carry_checks": adjacent_checked,
        "wait_continuity_links_quarantined": quarantined,
        "sealed_last_wait_owner_join_verified": anchor_checked,
        "non_wait_owner_state_independently_replayed": False,
        "historical_engagement_and_registrations_replayed": False,
        "veto_truth_independently_recomputed": False,
        "Q_to_action_counterfactual_proven": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }
