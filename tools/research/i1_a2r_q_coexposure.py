"""Descriptive first-person M11 census of naturally co-offered learned Q options.

This is an operator-only postflight diagnostic. It never supplies a candidate,
Q estimate, motor action or other signal to I1. A paid Competition opportunity
is NOT a causal Q intervention or proof that an alternative was safe/admissible.
"""
from __future__ import annotations

from collections import Counter
from math import isclose

from i1_a2r_m11_cold import numeric

_Q_SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
_CONTROL_SCOPE = "A2R_COLD_NATIVE_ACTION_CONTROL_PATH_NOT_L3"
_STAGE8_SCOPE = "A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3"
_LOCAL_SCOPE = "A2R_NATIVE_LOCAL_AFFORDANCE_ARITHMETIC_NOT_L3"
_SCOPE = "A2R_NATIVE_PAID_Q_COEXPOSURE_DESCRIPTIVE_NOT_L3"


def _key(item):
    if type(item) is not dict:
        raise ValueError("non-dictionary M11 opportunity occurrence")
    key = item.get("step"), item.get("cycle"), item.get("option")
    if (type(key[0]) is not int or key[0] < 1
            or type(key[1]) is not int or key[1] < 1
            or type(key[2]) is not str or not key[2]):
        raise ValueError("invalid M11 opportunity occurrence key")
    return key


def _close(a, b):
    x, y = numeric(a), numeric(b)
    return isclose(x, y, rel_tol=2e-9, abs_tol=2e-9)


def summarize_paid_q_coexposure(events, *, q_replay, controller,
                                stage8, local):
    """Report eligible-Q competitor sets without asserting motor causality.

    All inputs come from already authenticated, independently cold-replayed
    journals. Their scopes and the per-occurrence joins are checked here,
    but this function does NOT independently establish custody of its inputs.
    """
    if (type(events) is not list
            or any(type(x) is not dict for x in (q_replay, controller, stage8, local))
            or q_replay.get("scope") != _Q_SCOPE
            or q_replay.get("full_q_replay_verified") is not True
            or q_replay.get("adaptive_learning_go") != "NOT_ESTABLISHED"
            or controller.get("scope") != _CONTROL_SCOPE
            or controller.get("all_motor_receipts_matched") is not True
            or controller.get("native_crossing_and_rank_prefix_consistent") is not True
            or stage8.get("scope") != _STAGE8_SCOPE
            or stage8.get("same_full_m11_q_replay") is not True
            or local.get("scope") != _LOCAL_SCOPE
            or type(q_replay.get("stage8_observations")) is not list
            or type(stage8.get("unreplayed_evaluations")) is not list
            or type(local.get("verified_evaluations")) is not list
            or type(controller.get("admitted_decision_occurrences")) is not list):
        raise ValueError("Q coexposure requires complete already-cold-verified owners")
    observations = {}
    for row in q_replay["stage8_observations"]:
        key = _key(row)
        if key in observations or row.get("status") not in ("learned", "unlearned"):
            raise ValueError("duplicate or invalid cold Q observation")
        q = row.get("q")
        if (row["status"] == "learned" and q is None or
                row["status"] == "unlearned" and q is not None):
            raise ValueError("learned Q availability differs from TD replay")
        if q is not None:
            numeric(q)
        observations[key] = row
    total = q_replay.get("stage8_read_count")
    recomputed = stage8.get("stage8_evaluations_recomputed")
    unsupported_count = stage8.get("stage8_other_evaluations_unreplayed")
    if (any(type(v) is not int or v < 0 for v in
            (total, recomputed, unsupported_count))
            or total != len(observations)
            or total != recomputed + unsupported_count
            or unsupported_count != len(stage8["unreplayed_evaluations"])):
        raise ValueError("cold Q census differs from Stage8 source equations")

    unsupported = set()
    for row in stage8["unreplayed_evaluations"]:
        k = _key(row)
        if k in unsupported or k not in observations:
            raise ValueError("duplicate or foreign unreplayed Stage8 path")
        unsupported.add(k)
    local_keys = set()
    for row in local["verified_evaluations"]:
        k = _key(row)
        if k in local_keys or k not in unsupported:
            raise ValueError("local Q path is missing from unreplayed Stage8 families")
        local_keys.add(k)
    if (type(local.get("native_local_affordance_recomputed")) is not int
            or len(local_keys) != local["native_local_affordance_recomputed"]):
        raise ValueError("local affine Q audit was not exhaustive")

    stage8_events = {}
    competitions = {}
    for order, event in enumerate(events):
        if type(event) is not dict:
            raise ValueError("malformed authenticated M11 event")
        kind, step, cycle = (event.get("kind"), event.get("t_monde"),
                             event.get("cycle"))
        if kind == "stage8_option_evaluation":
            data = event.get("data")
            k = _key({"step":step, "cycle":cycle,
                      "option":data.get("option_ref") if type(data) is dict else None})
            if k in stage8_events or k not in observations:
                raise ValueError("duplicate/foreign signed Stage8 observation")
            signed = observations[k]
            if (data.get("learning_signature") != signed.get("signature")
                    or data.get("learned_value_status") != signed.get("status")
                    or ((data.get("learned_value") is None) != (signed.get("q") is None))
                    or (signed.get("q") is not None and
                        not _close(data["learned_value"], signed["q"]))):
                raise ValueError("published Stage8 Q not equal to cold replay")
            stage8_events[k] = (data, order)
        elif kind == "competition_cycle":
            if (type(step) is not int or step < 1
                    or type(cycle) is not int or cycle < 1
                    or type(event.get("data")) is not dict
                    or type(event["data"].get("traces")) is not list
                    or (step, cycle) in competitions):
                raise ValueError("invalid or duplicated paid Competition cycle")
            traces = {}
            for trace in event["data"]["traces"]:
                if type(trace) is not dict:
                    raise ValueError("malformed Competition candidate trace")
                k = _key({"step":step,"cycle":cycle,"option":trace.get("option_ref")})
                if k in traces or k not in stage8_events:
                    raise ValueError("Competition trace without prior cold Stage8")
                evaluated, earlier = stage8_events[k]
                if earlier >= order:
                    raise ValueError("Competition preceded signed Stage8")
                evidence = trace.get("evidence")
                if ((evidence is None) != (evaluated.get("evidence") is None)
                        or (evidence is not None and
                            not _close(evidence, evaluated.get("evidence")))):
                    raise ValueError("Competition signal differs from signed Stage8")
                if type(trace.get("crossed")) is not bool:
                    raise ValueError("invalid Competition crossing")
                before, after, threshold = (
                    numeric(trace.get("accumulator_before")),
                    numeric(trace.get("accumulator_after")),
                    numeric(trace.get("threshold")))
                if before < 0 or after < 0 or threshold <= 0:
                    raise ValueError("invalid native Competition candidate margin")
                traces[k] = trace
            competitions[(step, cycle)] = traces
    if (set(observations) != set(stage8_events)
            or set(observations) != {key for opts in competitions.values()
                                   for key in opts}):
        raise ValueError("M11 paid Competition and cold Q occurrences differ")

    admitted = {}
    for entry in controller["admitted_decision_occurrences"]:
        if (type(entry) is not dict or type(entry.get("step")) is not int
                or type(entry.get("cycle")) is not int
                or type(entry.get("option")) is not str
                or entry["step"] in admitted
                or (entry["step"], entry["cycle"], entry["option"]) not in observations):
            raise ValueError("physical decision lacks exact paid Q/Competition path")
        admitted[entry["step"]] = entry
    if (controller.get("native_q_decisions_joined_to_admission") != len(admitted)
            or type(controller.get("nondecision_motor_sources")) is not int):
        raise ValueError("physical admission count differs from cold controller")

    kinds = Counter()
    cycles_with_learned = 0
    cycles_with_learned_and_alternative = 0
    cycles_with_two_learned = 0
    cycles_with_two_math_checked = 0
    cycles_with_learned_crossing = 0
    learned_crossed_and_admitted = 0
    learned_admitted = 0
    learned_paid_reads = 0
    learned_math_checked = 0
    learned_with_no_evidence = 0
    examples = []
    for (step, cycle), traces in sorted(competitions.items()):
        evaluated, learned, math_checked, crossed = [], [], [], []
        for key, trace in traces.items():
            data = stage8_events[key][0]
            has_evidence = trace.get("evidence") is not None
            if (has_evidence and data.get("status") != "evaluated"
                    or not has_evidence and data.get("status") != "not_evaluated"):
                raise ValueError("Stage8 evaluated status is inconsistent")
            if has_evidence:
                evaluated.append(key)
            if observations[key]["status"] == "learned":
                if not has_evidence:
                    learned_with_no_evidence += 1
                    continue
                learned.append(key)
                learned_paid_reads += 1
                if key not in unsupported or key in local_keys:
                    math_checked.append(key)
                    learned_math_checked += 1
                if trace["crossed"]:
                    crossed.append(key)
        if not learned:
            category = "NO_EVALUATED_LEARNED_Q"
        elif len(evaluated) == 1:
            category = "LEARNED_Q_NO_EVALUATED_ALTERNATIVE"
        elif len(learned) == 1:
            category = "LEARNED_Q_WITH_NONLEARNED_ALTERNATIVE"
        else:
            category = "MULTIPLE_LEARNED_Q_CANDIDATES"
        kinds[category] += 1
        if learned:
            cycles_with_learned += 1
        if learned and len(evaluated) >= 2:
            cycles_with_learned_and_alternative += 1
        if len(learned) >= 2:
            cycles_with_two_learned += 1
        if len(math_checked) >= 2:
            cycles_with_two_math_checked += 1
        if crossed:
            cycles_with_learned_crossing += 1
        winner = admitted.get(step)
        selected = None if winner is None or winner["cycle"] != cycle else winner["option"]
        if selected is not None and (step, cycle, selected) in learned:
            learned_admitted += 1
            if (step, cycle, selected) in crossed:
                learned_crossed_and_admitted += 1
        if learned and len(examples) < 12:
            best = max(learned, key=lambda k: numeric(traces[k]["accumulator_after"])
                       / numeric(traces[k]["threshold"]))
            ratio = numeric(traces[best]["accumulator_after"]) / numeric(
                traces[best]["threshold"])
            examples.append({
                "step":step, "cycle":cycle, "classification":category,
                "evaluated_options":len(evaluated),
                "learned_evaluated_options":len(learned),
                "learned_evidence_equations_recomputed":len(math_checked),
                "learned_options_crossed":len(crossed),
                "largest_learned_threshold_ratio":ratio,
                "physically_admitted_option":selected,
                "learned_admitted":selected is not None and
                        (step, cycle, selected) in learned,
            })
    return {
        "scope":_SCOPE,
        "paid_competition_cycles":len(competitions),
        "stage8_cold_learned_reads":sum(
            row["status"] == "learned" for row in observations.values()),
        "learned_paid_evaluations":learned_paid_reads,
        "learned_paid_evaluations_with_recomputed_formula":learned_math_checked,
        "learned_q_without_evaluated_evidence":learned_with_no_evidence,
        "paid_cycles_with_learned_q":cycles_with_learned,
        "paid_cycles_with_learned_q_and_evaluated_alternative":
            cycles_with_learned_and_alternative,
        "paid_cycles_with_two_learned_q_candidates":cycles_with_two_learned,
        "paid_cycles_with_two_formula_checked_learned_candidates":
            cycles_with_two_math_checked,
        "paid_cycles_with_learned_q_crossing":cycles_with_learned_crossing,
        "physically_admitted_learned_q_options":learned_admitted,
        "physically_admitted_crossed_learned_q_options":
            learned_crossed_and_admitted,
        "nondecision_physical_steps":controller["nondecision_motor_sources"],
        "cycle_classifications":{name:kinds[name] for name in (
            "NO_EVALUATED_LEARNED_Q",
            "LEARNED_Q_NO_EVALUATED_ALTERNATIVE",
            "LEARNED_Q_WITH_NONLEARNED_ALTERNATIVE",
            "MULTIPLE_LEARNED_Q_CANDIDATES")},
        "examples":examples,
        "examples_truncated":max(0,cycles_with_learned-len(examples)),
        "competitor_safety_independently_recomputed":False,
        "full_competition_owner_state_replayed":False,
        "P40_and_Q_causal_contributions_isolated":False,
        "Q_to_action_counterfactual_proven":False,
        "study_admissible":False,
        "general_L3":"NOT_ESTABLISHED",
    }
