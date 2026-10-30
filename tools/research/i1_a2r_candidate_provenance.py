"""Conservative read-only candidate birth/transition provenance for A2-R M11.

Classify ambiguous states as quarantined. Never infer a full Competition replay.
"""
from __future__ import annotations

from math import isclose

from i1_a2r_m11_cold import numeric

_WAIT = "permanent:attendre"
_REGISTRATION = frozenset((
    "option_registration", "stage11_geographic_option_registration",
    "i1_lived_site_option_registration", "i1_place_memory_option_registration",
    "i1_local_opportunity_registration",
))


def audit_candidate_provenance(events, *, birth, q_replay, control):
    if (type(events) is not list or type(birth) is not dict
            or type(q_replay) is not dict or type(control) is not dict
            or birth.get("scope") != "SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE"
            or q_replay.get("scope") != "A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3"
            or q_replay.get("full_q_replay_verified") is not True
            or control.get("all_motor_receipts_matched") is not True
            or birth.get("identity") != q_replay.get("m11_identity")
            or birth.get("mode") != q_replay.get("mode")):
        raise ValueError("candidate audit needs source birth and cold-verified M11")
    initial = birth.get("initial_competition")
    if (type(initial) is not dict or initial.get("cycle") != 0
            or initial.get("engaged_option_id") is not None
            or initial.get("registry") != []):
        raise ValueError("candidate audit requires pristine empty Competition registry")

    seen = set()
    by_cycle = {}
    registered = {}
    all_registrations = []
    carry_events = {}
    reconsidered = set()
    last_paid_cycle = None
    for i, event in enumerate(events):
        if type(event) is not dict:
            raise ValueError("malformed signed candidate event")
        kind, step, cycle, data = (
            event.get("kind"), event.get("t_monde"),
            event.get("cycle"), event.get("data"))
        if kind in _REGISTRATION:
            if (type(step) is not int or type(cycle) is not int
                    or type(data) is not dict or type(data.get("option_ref")) is not str
                    or type(data.get("registered")) is not bool):
                raise ValueError("invalid candidate registration receipt")
            all_registrations.append((i, step, cycle, data["option_ref"]))
            if data["registered"]:
                registered.setdefault((step, cycle, data["option_ref"]), []).append(i)
        elif kind == "i1_place_memory_intention_reconsidered":
            if (type(step) is not int or type(cycle) is not int
                    or type(data) is not dict
                    or type(data.get("next_option_ref")) is not str
                    or not data["next_option_ref"]):
                raise ValueError("invalid memory continuation receipt")
            key = (step, cycle, data["next_option_ref"])
            reconsidered.add(key)
            carry_events.setdefault(key, []).append((i, data))
        elif kind == "competition_cycle":
            if (type(step) is not int or type(cycle) is not int
                    or type(data) is not dict or type(data.get("traces")) is not list
                    or (step, cycle) in by_cycle
                    or (last_paid_cycle is not None
                        and (step, cycle) <= last_paid_cycle)):
                raise ValueError("invalid Competition chronology")
            last_paid_cycle = (step, cycle)
            current = {}
            for trace in data["traces"]:
                if (type(trace) is not dict or type(trace.get("option_ref")) is not str
                        or not trace["option_ref"] or trace["option_ref"] in current):
                    raise ValueError("invalid Competition candidate")
                current[trace["option_ref"]] = (trace, i)
            by_cycle[(step, cycle)] = current

    first_zero = 0
    repeat_quarantine = 0
    memory_quarantine = 0
    missing_registration = 0
    rows = []
    for (step, cycle), traces in sorted(by_cycle.items()):
        for option, (trace, order) in sorted(traces.items()):
            before = numeric(trace.get("accumulator_before"))
            if before < 0:
                raise ValueError("negative candidate pre-accumulation")
            if option == _WAIT:
                continue
            key = step, cycle, option
            fresh = option not in seen
            receipts = registered.get(key, ())
            receipts_prior = [i for i in receipts if i < order]
            if receipts and len(receipts_prior) != len(receipts):
                raise ValueError("candidate registration after its Competition evaluation")
            if fresh and not receipts_prior:
                category = "quarantined_no_registration"
                missing_registration += 1
            elif fresh and key in reconsidered:
                category = "quarantined_memory_carry"
                memory_quarantine += 1
            elif fresh and before == 0.0 and receipts_prior:
                category = "first_seen_zero_consistent_not_owner_replayed"
                first_zero += 1
            else:
                category = "quarantined_prior_state_or_refresh"
                repeat_quarantine += 1
            rows.append({"step": step, "cycle": cycle, "option": option,
                         "classification": category})
            seen.add(option)

    # Memory continuity is written before a source-owned Competition cycle.
    # Its receipt's raw credit is an upper bound, not a proven motor signal.
    memory_bounds_checked = 0
    for (step, cycle, option), memories in carry_events.items():
        trace = by_cycle.get((step, cycle), {}).get(option)
        if trace is None:
            # A missing cycle may have been UC-degraded; never invent a read.
            continue
        if len(memories) != 1 or memories[0][0] >= trace[1]:
            raise ValueError("memory continuation not uniquely before Competition")
        raw = memories[0][1].get("carried_evidence")
        carry = numeric(raw)
        cal = birth.get("competition_calibration")
        if type(cal) is not dict:
            raise ValueError("missing source-born Competition credit bounds")
        residual = numeric(cal.get("residual"))
        base_threshold = numeric(cal.get("base_threshold"))
        before = numeric(trace[0].get("accumulator_before"))
        if (not 0 < residual < 1 or base_threshold <= 0
                or not 0 < before <= min(carry, base_threshold * residual) + 2e-9
                or before >= base_threshold):
            raise ValueError("memory candidate credit exceeds source-born upper bound")
        memory_bounds_checked += 1

    # A registered candidate can be edited or replaced between two paid
    # cycles. Check only uninterrupted, same-step, consecutive cycle reads.
    # This is a receipt-level carry witness, NOT a complete owner-state replay.
    stable_carry = 0
    quarantined_carry = 0
    cycles_by_step = {}
    for (step, cycle), traces in by_cycle.items():
        cycles_by_step.setdefault(step, []).append((cycle, traces))
    for step, cycles in cycles_by_step.items():
        for (old_cycle, old), (new_cycle, new) in zip(cycles, cycles[1:]):
            common = set(old) & set(new) - {_WAIT}
            for option in common:
                old_trace, old_order = old[option]
                new_trace, new_order = new[option]
                if new_cycle != old_cycle + 1:
                    quarantined_carry += 1
                    continue
                mutations = any(
                    old_order < order < new_order and ref == option
                    for order, _t, _c, ref in all_registrations
                ) or any(
                    old_order < order < new_order
                    and (ev.get("kind") in (
                        "active_goal_changed", "command_admitted",
                        "command_vetoed", "command_experienced",
                        "i1_place_memory_intention_reconsidered",
                        "step_closed")
                        or (type(ev.get("kind")) is str
                            and ev["kind"].startswith(
                                "i1_place_memory_intention_reconsidered")))
                    for order, ev in enumerate(events)
                )
                if mutations:
                    quarantined_carry += 1
                    continue
                before = numeric(new_trace.get("accumulator_before"))
                after = numeric(old_trace.get("accumulator_after"))
                if not isclose(before, after, rel_tol=2e-9, abs_tol=2e-9):
                    raise ValueError("uninterrupted candidate carry differs between paid cycles")
                stable_carry += 1

    # An option absent from a later paid cycle can be pruned, invalidated,
    # capacity-evicted or replaced. None is reconstructed from mere absence.
    return {
        "scope": "A2R_CANDIDATE_PROVENANCE_BOUNDARY_ONLY_NOT_L3",
        "first_seen_zero_consistent": first_zero,
        "memory_carry_quarantined": memory_quarantine,
        "prior_state_or_refresh_quarantined": repeat_quarantine,
        "missing_registration_quarantined": missing_registration,
        "uninterrupted_same_step_candidate_carries_checked": stable_carry,
        "candidate_carries_quarantined": quarantined_carry,
        "source_bounded_memory_credits_checked": memory_bounds_checked,
        "occurrences": rows,
        "non_wait_owner_state_independently_replayed": False,
        "registration_semantics_independently_replayed": False,
        "full_rank_order_independently_recomputed": False,
        "Q_to_action_counterfactual_proven": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }
