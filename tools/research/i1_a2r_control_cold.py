"""Independent A2-R M11 Competition -> Action Control -> applied command audit.

Validates the chronology and command identity of already signed M11 receipts,
the cold Q/TD decision replay and a source-reconstructed birth policy version.
It DOES NOT recompute every safety predicate or prove counterfactual Q motor
mediation, nor certify absence of a rollback from truncated histories.
"""
from __future__ import annotations

from i1_a2r_m11_cold import physical_steps

_RULES = {
    "known_lethal_zone": ("option", "lethal_zone_movement", "semantic_prohibition"),
    "known_toxic_item": ("option", "toxic_item_consumption", "semantic_prohibition"),
    "protected_integrity_violation": (
        "option", "protected_invariant_violation", "protected_invariant"),
    "protocol_mask": ("protocol", "rollback_sequence_mask", "protocol"),
}
_Q_SCOPE = "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
_BIRTH_SCOPE = "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE"


def audit_native_action_control(events, *, q_replay, birth):
    """Reconcile ALL physical commands, decision admissions and ordered vetoes.

    Inputs MUST be the immutable M11 stream from inspect_m11 and the separately
    fully cold-verified Q replay. The safety reason itself is only a receipt:
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
    generation = q_replay.get("generation")
    status = q_replay.get("status")
    steps = physical_steps(events, generation=generation, status=status)
    actual = {s["step"]: s for s in steps}
    expected_decisions = {}
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
    latest_competition = {}
    control = {}
    experienced = {}
    vetoes = []
    admitted_decisions = {}
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
            latest_competition[t] = (cycle, order)
        elif kind in ("command_admitted", "command_vetoed"):
            if (type(t) is not int or t not in actual or type(data) is not dict
                    or type(data.get("source")) is not str or not data["source"]
                    or type(data.get("primitive")) is not str
                    or not data["primitive"]
                    or type(data.get("command_hash")) is not str
                    or not data["command_hash"]
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
            if kind == "command_vetoed":
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
                    or not ev["command_hash"]):
                raise ValueError("missing or repeated original physical command")
            experienced[t] = (ev, order)

    if set(experienced) != set(actual):
        raise ValueError("missing physical command experiences")
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
        "nondecision_motor_sources": other_executed,
        "policy_version_matches_source_birth": True,
        "all_motor_receipts_matched": True,
        "veto_truth_independently_recomputed": False,
        "full_rank_order_independently_recomputed": False,
        "Q_to_action_counterfactual_proven": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }
