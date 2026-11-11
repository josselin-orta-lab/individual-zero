"""Falsify assumed cost-neutrality of a passive readout for future learning.

Stage 2.1 SOFTWARE ONLY, not a biological life or an action controller.
Uses the unchanged native BodyLaws, CognitiveBudget, transition and
Mind.prepare_learning methods on explicitly synthetic bodies. The same
motor action is already chosen before optional computation can be booked.
No World, no run_life, no learned-state writeback or forecast is executed.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost,
    debit_cognition, transition, validate_body)
from ..modules.genome import midpoint
from ..modules.mind import Mind
from .stage2_action_phase_readout_budget import proposed_readout_work

SCHEMA = "i3-stage2.1-readout-next-learning-affordability-software/v1"
ACTION = "attendre"
PARAM = None
DECISION = CognitiveWork(cycles=3, memory_items=12)
CASES = (
    ("energy_boundary", (0.56, 60., 60., 90., 80.)),
    ("vigilance_boundary", (5., 60., 60., 90., 0.55)),
    ("both_funded", (5., 60., 60., 90., 5.)),
    ("optional_denied", (0.49, 60., 60., 90., 80.)),
)


def _digest(obj):
    return sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False,
        default=str).encode()).hexdigest()


def _source_seal(mind: Mind):
    """Keep this a source-control readout, not cognition for a living mind."""
    return _digest({
        "genes": (mind.theta, mind.p, mind.w, mind.alpha, mind.m_max),
        "buffer": list(mind.buffer), "values": mind.values,
        "effects": repr(mind.effects.stats),
        "map": repr(mind.map), "hist": repr(mind.hist),
        "last": mind.last,
        "rng": repr(mind.rng.getstate()),
        "budget_rng": repr(mind._budget_rng.getstate()),
    })


def _original_mind(body):
    mind = Mind(midpoint(), 100061)
    mind.last = (body, (ACTION,), ACTION, PARAM)
    return mind


def _authorize_optional(budget: CognitiveBudget, *, action: str, n: int):
    """Pure work admission, without any optional readout or source scan."""
    extra = proposed_readout_work(n)
    energy, vigilance = cognitive_cost(budget.laws, extra)
    if (budget.remaining[0] < energy or
            budget.remaining[4] < vigilance or
            (action != "dormir" and
             budget.remaining[0] - energy < ACTION_COSTS[action])):
        return False
    if not budget.try_spend(extra):
        raise RuntimeError("native budget rejected an affordable ticket")
    return True


def examine(body, *, extra_requested):
    """Inspect two physical budget projections; never instantiate a World."""
    if type(extra_requested) is not bool:
        raise TypeError("explicit optional readout arm required")
    before = validate_body(body)
    laws = BodyLaws()
    mind = _original_mind(before)
    source_before = _source_seal(mind)
    decision = CognitiveBudget(before, laws)
    if not decision.try_spend(DECISION):
        raise RuntimeError("fixed reference decision not funded")
    original = decision.work
    extra = proposed_readout_work(len(mind.buffer))
    granted = False
    if extra_requested:
        granted = _authorize_optional(
            decision, action=ACTION, n=len(mind.buffer))
        if not granted and decision.work != original:
            raise RuntimeError("denied readout allocated phantom work")
        if not granted and _source_seal(mind) != source_before:
            raise RuntimeError("denied readout modified personal state")

    # All physical changes come from unchanged PURE native body law, not an
    # invented future or an external World. No resource or action changes.
    after, reasons = transition(before, ACTION, laws, decision.work)
    if reasons:
        raise RuntimeError("fixed nonterminal affordability fixture became terminal")
    base_energy, base_vigilance = cognitive_cost(laws, original)
    all_energy, all_vigilance = cognitive_cost(laws, decision.work)
    added_cost = (all_energy-base_energy, all_vigilance-base_vigilance)
    if extra_requested and not granted and (
            added_cost != (0., 0.) or decision.work != original):
        raise RuntimeError("denied readout changed physical payment")
    if extra_requested and granted and (
            decision.work.cycles != original.cycles + extra.cycles or
            decision.work.memory_items !=
            original.memory_items + extra.memory_items):
        raise RuntimeError("readout reserved wrong native work categories")

    # The ACTUAL reference allocation method is called, but no TD update
    # or subsequent bodily debit is executed in this synthetic software.
    learning = CognitiveBudget(after, laws)
    replays = mind.prepare_learning(
        {"body": after, "dead": reasons}, learning)
    funded = replays is not None
    if funded and (learning.work.cycles < 2 or replays != 0):
        raise RuntimeError("reference waiting action acquired unexpected replay")
    if not funded and learning.work != CognitiveWork():
        raise RuntimeError("unauthorized learning leaked partial base work")

    # Report the hypothetical pure resulting body if the base model would
    # be charged, never claim this bill was debited in an actual World.
    projected = None
    if funded:
        projected, account = debit_cognition(after, laws, learning.work)
        if any(account[c]["unpaid"] != 0 for c in account):
            raise RuntimeError("native learning work contains unpaid amount")
    if source_before != _source_seal(mind):
        raise RuntimeError("modeling optional work mutated individual learned state")
    return {
        "extra_requested": extra_requested,
        "optional_status": (
            "NOT_REQUESTED" if not extra_requested else
            "MODEL_AUTHORIZED" if granted else "NO_FUNDED_READOUT"),
        "source_unchanged": True,
        "chosen_action_unchanged": ACTION,
        "original_decision_work": asdict(original),
        "optional_ticket": asdict(extra),
        "cumulative_decision_work": asdict(decision.work),
        "paid_model_decision_energy": all_energy,
        "paid_model_decision_vigilance": all_vigilance,
        "additional_modeled_energy": added_cost[0],
        "additional_modeled_vigilance": added_cost[1],
        "post_action_body": list(after),
        "post_action_terminal": list(reasons),
        "next_base_learning_model_authorized": funded,
        "next_base_learning_work": asdict(learning.work),
        "next_sleep_replays_reserved": replays,
        "next_learning_pure_projected_body": (
            list(projected) if projected is not None else None),
        "world_created": False,
        "world_cognitive_debit_attested": False,
    }


def audit():
    rows = []
    for name, body in CASES:
        original = examine(body, extra_requested=False)
        proposed = examine(body, extra_requested=True)
        if original["chosen_action_unchanged"] != proposed["chosen_action_unchanged"]:
            raise RuntimeError("action comparison is not paired")
        rows.append({
            "case": name,
            "before_body": list(body),
            "original": original,
            "readout": proposed,
            "base_learning_lost_after_readout": (
                original["next_base_learning_model_authorized"] and
                proposed["optional_status"] == "MODEL_AUTHORIZED" and
                not proposed["next_base_learning_model_authorized"]),
        })
    by = {r["case"]: r for r in rows}
    failures = []
    for case in ("energy_boundary", "vigilance_boundary"):
        r = by[case]
        if not r["base_learning_lost_after_readout"]:
            failures.append(case)
    r = by["both_funded"]
    if (r["readout"]["optional_status"] != "MODEL_AUTHORIZED" or
            not r["original"]["next_base_learning_model_authorized"] or
            not r["readout"]["next_base_learning_model_authorized"]):
        failures.append("both_funded")
    r = by["optional_denied"]
    if (r["readout"]["optional_status"] != "NO_FUNDED_READOUT" or
            r["readout"]["additional_modeled_energy"] != 0 or
            r["readout"]["additional_modeled_vigilance"] != 0 or
            not r["original"]["next_base_learning_model_authorized"] or
            not r["readout"]["next_base_learning_model_authorized"] or
            r["original"]["post_action_body"] != r["readout"]["post_action_body"]):
        failures.append("optional_denied")
    return {
        "schema": SCHEMA,
        "status": ("SOFTWARE_PHASE_AFFORDABILITY_GATE_PASS" if not failures
                   else "SOFTWARE_PHASE_AFFORDABILITY_FALSIFIER_FAILED"),
        "predeclared_cases": len(CASES),
        "learning_lost_in_boundary_cases": sum(
            r["base_learning_lost_after_readout"] for r in rows),
        "failed_declared_gates": failures,
        "rows": rows,
        "native_reference_next_learning_allocator_used": True,
        "readout_predictions_executed": 0,
        "worlds_opened": 0,
        "actually_lived_readout_debits": 0,
        "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_READOUT_LEARNING_AFFORDABILITY_RESULT="+json.dumps(
        audit(), sort_keys=True))
