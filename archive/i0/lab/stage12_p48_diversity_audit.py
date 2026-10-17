"""Read-only A2.5 physical diversity, food and P-48 signal census.

Never imported by I0. A journal proves consistency of logged observations,
not external physical truth or subjective causal responsibility.
"""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
import json

from .independent_journal_audit import audit_export_bytes


def _number(raw: object) -> float:
    if type(raw) is dict and set(raw) == {"$f64"}:
        try:
            value = float.fromhex(raw["$f64"])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("invalid canonical physical number") from exc
        if value.hex() != raw["$f64"]:
            raise ValueError("noncanonical physical number")
    elif type(raw) in (int, float):
        value = float(raw)
    else:
        raise ValueError("physical food value absent or not numerical")
    if not isfinite(value):
        raise ValueError("nonfinite physical value")
    return value


def _position(raw: object) -> tuple[int, int]:
    if (type(raw) is not dict or set(raw) != {"x", "y"}
            or any(type(raw[k]) is not int for k in ("x", "y"))):
        raise ValueError("noncanonical physical position")
    return raw["x"], raw["y"]


def summarize_stage12_p48_diversity_events(events: list[dict]) -> dict:
    """Summarize independently archived *events*, without assigning agency.

    A same-frontier signal can legitimately be shared by different candidate
    options. It is an information source, not several independent outcomes.
    """
    commands = {}
    transitions = {}
    initial = None
    signal_users = defaultdict(set)
    value_users = defaultdict(set)
    signal_events = 0
    all_p48_signals = set()
    interest_rows = 0
    seen_evaluations = set()
    for event in events:
        kind = event.get("kind")
        t = event.get("t_monde")
        if kind == "perceptual_capture" and t == 1 and initial is None:
            data = event.get("data", {})
            initial = _position(data.get("position"))
        if kind in ("command_experienced", "world_transition_experienced"):
            if type(t) is not int or t < 1:
                raise ValueError("physical event lacks world step")
            target = commands if kind == "command_experienced" else transitions
            if t in target:
                raise ValueError("duplicate physical command or transition")
            target[t] = event
        if kind != "stage11_intrinsic_evaluation":
            continue
        data = event.get("data")
        cycle = event.get("cycle")
        if (type(t) is not int or type(cycle) is not int
                or type(data) is not dict):
            raise ValueError("intrinsic event lacks phase or data")
        option = data.get("option_ref")
        ids = data.get("signal_ids")
        if (type(option) is not str or not option
                or type(ids) is not list
                or any(type(s) is not str or not s for s in ids)):
            raise ValueError("intrinsic event has ungrounded signal reference")
        key = (t, cycle, option)
        if key in seen_evaluations:
            raise ValueError("duplicate per-cycle intrinsic option evaluation")
        seen_evaluations.add(key)
        if len(set(ids)) != len(ids):
            raise ValueError("a single option repeats a P-48/source signal")
        signal_events += 1
        p48 = [s for s in ids if s.startswith("exploration:")]
        if p48:
            interest_rows += 1
        for signal in p48:
            signal_users[(t, cycle, signal)].add(option)
            all_p48_signals.add(signal)
        value = data.get("intrinsic_value")
        if value is not None:
            score = _number(value)
            if not 0 <= score <= 1:
                raise ValueError("P-48 value outside calibrated unit interval")
            value_users[(t, cycle, score.hex())].add(option)

    if commands.keys() != transitions.keys():
        raise ValueError("physical commands and transitions do not pair")
    if not transitions:
        raise ValueError("no executed physical transition")
    if sorted(transitions) != list(range(1, len(transitions) + 1)):
        raise ValueError("noncontiguous physical world steps")
    positions = set(() if initial is None else (initial,))
    path = []
    prev = initial
    prev_food = None
    attempted_moves = applied_moves = blocked_moves = 0
    attempted_eats = confirmed_eats = food_net_increase_steps = 0
    for t in sorted(transitions):
        command, transition = commands[t], transitions[t]
        if command.get("attempt_ref") != transition.get("attempt_ref"):
            raise ValueError("command/transition attempt mismatch")
        primitive = command.get("primitive")
        pos = _position(transition.get("position_after"))
        body = transition.get("body_after")
        if not isinstance(body, dict):
            raise ValueError("physical transition lacks measured body")
        food = _number(body.get("food"))
        effects = transition.get("effects")
        if not isinstance(effects, dict):
            raise ValueError("physical transition lacks effect receipt")
        movement = effects.get("movement")
        if primitive == "se_deplacer":
            attempted_moves += 1
            if movement == "moved":
                applied_moves += 1
                if prev is not None and pos == prev:
                    raise ValueError("moved receipt without displacement")
            elif movement == "blocked":
                blocked_moves += 1
                if prev is not None and pos != prev:
                    raise ValueError("blocked receipt with displacement")
            elif movement is not None:
                raise ValueError("unknown physical movement receipt")
        elif movement is not None:
            raise ValueError("nonmovement primitive claims movement")
        ate = effects.get("ate")
        if primitive == "manger":
            attempted_eats += 1
            if ate in ("berry_a", "berry_b"):
                confirmed_eats += 1
            elif ate is not None and ate != "unavailable":
                raise ValueError("unknown physical ingestion receipt")
        elif ate is not None:
            raise ValueError("non-eating command claims ingestion")
        if prev_food is not None and food > prev_food:
            food_net_increase_steps += 1
        positions.add(pos)
        path.append({"step": t, "x": pos[0], "y": pos[1],
                     "command": primitive, "movement": movement,
                     "food_after": food})
        prev, prev_food = pos, food
    shared = [
        {"step": t, "cycle": cycle, "signal_id": signal,
         "options": sorted(users)}
        for (t, cycle, signal), users in sorted(signal_users.items())
        if len(users) > 1
    ]
    numerical_ties = sum(len(users) > 1 for users in value_users.values())
    return {
        "schema": "stage12-a2-physical-diversity-p48-food-v1",
        "world_steps": len(transitions),
        "physically_distinct_sites": len(positions),
        "initial_position_captured": initial is not None,
        "positions": path,
        "attempted_moves": attempted_moves,
        "confirmed_moves": applied_moves,
        "blocked_moves": blocked_moves,
        "attempted_eats": attempted_eats,
        "physically_confirmed_eats": confirmed_eats,
        "net_food_increase_steps_after_first": food_net_increase_steps,
        "food_delta_first_step_excluded": True,
        "intrinsic_evaluation_receipts": signal_events,
        "p48_interest_receipts": interest_rows,
        "distinct_p48_source_signals": len(all_p48_signals),
        "cross_option_shared_signal_groups": len(shared),
        "cross_option_shared_signals": shared,
        "equal_numeric_interest_groups": numerical_ties,
        "within_option_repeated_signal_ids": 0,
        "subjective_agency_inferred_from_p48": False,
        "complete_food_goal_achievement_attested": False,
    }


def audit_stage12_p48_diversity(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> dict:
    """Validate a canonical journal, then summarize without reading WorldBody."""
    audit = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count
    )
    result = summarize_stage12_p48_diversity_events([
        json.loads(line)["causal_event"] for line in content.splitlines()
    ])
    if result["world_steps"] != audit.world_steps_closed:
        raise ValueError("P-48 census and independent closed-step audit differ")
    return {**result, "journal_head": audit.head_hash,
            "journal_occurrences": audit.occurrences,
            "independent_chain_audit_passed": True}
