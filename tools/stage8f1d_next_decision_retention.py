"""F1D: original-F1C anchored, two-tick *synthetic* native decision continuation.

No run_life, cohort, birth or modified decision policy. The target is the
actual second Mind.decide from a real F1C paid post-action learned update,
versus exactly the same paid computation executed and discarded. Do not
require a positive motor result: unchanged action IS an admissible negative.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from i3.modules.body import CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.stage8f1_paid_microdecision_mind import (
    MICRO_WORK, PaidMicrodecisionMind,
)
from tools import stage8f1_matched_native_funding as F1B
from tools import stage8f1c_paid_postaction_learning as F1C
from tools import stage8f1c_independent_postaction_audit as F1C_COLD

SCHEMA = "i3-stage8f1d-source-anchored-synthetic-next-decision/v0"
F1C_ORIGINAL_SHA = "e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d"
SOURCE_HEAD = "6c4d433110f9960bd96b4b5716c214e0465f9214"
F1C_COLD_SHA = "754a4c06eeae546f1fe8900375323752056c1b660e1af89d6b4688419a8e1588"
FROZEN_NEGATIVE = F1C.NEGATIVE
MODES = ("retain", "discard_after_compute")


def read_f1c_exact(path):
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != F1C_ORIGINAL_SHA:
        raise ValueError("F1C ORIGINAL bytes do not match the registered source")
    report = json.loads(raw)
    # An independent, arithmetic-only F1C re-reduction, before any World call.
    verified = F1C_COLD.audit(report, F1C_ORIGINAL_SHA)
    if verified["status"] != "SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS":
        raise AssertionError("original learned event did not pass cold F1C audit")
    return report


def _matched_state(mode, original):
    """Execute F1C once more, requiring exact private and native receipt parity."""
    row = original["arms"][mode]
    world, initial = F1B.make_state(F1B.STATES[0])
    mind = F1B.cloned_mind(PaidMicrodecisionMind, initial)
    cap = world.capture()
    if (json.loads(F1C.canonical(cap)) != row["capture"] or
            F1C.seal_mind(mind) != row["private_before_decision"]):
        raise AssertionError("F1C source pre-decision first-person snapshot mismatch")
    decision = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(cap, decision)
    if (action != row["action"] or param != row["param"] or
            asdict(work) != row["decision_work"] or work != decision.work or
            info["funding"] != row["decision_funding"] or work != MICRO_WORK):
        raise AssertionError("F1C original first voluntary choice was not reconstructed")
    outcome = world.step(action, param, work)
    if (world.t != 1 or outcome["dead"] or
            list(outcome["body"]) != row["native_motor_step"]["body"] or
            outcome["cognitive_accounting"] !=
            row["native_motor_step"]["cognitive_accounting"]):
        raise AssertionError("source first native physics does not match archived F1C")
    mind.observe_outcome(outcome)
    if F1C.seal_mind(mind) != row["private_before_postaction_learning"]:
        raise AssertionError("F1C original pre-learning Mind mismatch")
    learning = CognitiveBudget(world.body, world.laws)
    prepaid = mind.prepare_learning(outcome, learning)
    if (prepaid is None or prepaid != row["prepaid_replays"] or
            asdict(learning.work) != row["learning_work"] or
            list(learning.remaining) != row["learning_allowance_remaining"]):
        raise AssertionError("F1C post-action preauthorization changed")
    receipt = world.pay_cognition(learning.work)
    if (receipt != row["paid_postaction_learning"] or
            list(world.body) != row["body_after_paid_learning"]):
        raise AssertionError("F1C post-action native two-currency bill changed")
    outcome["body"] = world.body
    target = mind if mode == "retain" else deepcopy(mind)
    replayed = target.learn_from_outcome(outcome, replay_limit=prepaid)
    if (replayed != row["executed_replays"] or
            F1C.seal_mind(target) != row["private_computed_postaction"] or
            F1C.seal_mind(mind) != row["private_persisted_postaction"]):
        raise AssertionError("historical paid learning retention could not be reconstructed")
    if world.t != 1 or world.dead:
        raise AssertionError("source continuation did not reach living next decision")
    return world, mind


def _snapshot_world(world):
    """Observer-only representation of the selected empty synthetic F1B world."""
    return {
        "t": world.t,
        "body": list(world.body),
        "position": list(world.pos),
        "inventory": sorted([[k, v] for k, v in world.inventory.items()]),
        "dead": list(world.dead),
        "water_cells": sorted([[list(k), v.gain, v.stock, v.max_stock, v.restock_every]
                               for k, v in world.water.items()]),
        "food_cells": sorted([[list(k), v.token, v.quantity, v.max_quantity,
                              v.restock_every] for k, v in world.food.items()]),
        "hidden_effects": sorted([[k, list(v)] for k, v in world.effects.items()]),
        "world_spec": {
            "name": world.spec.name,
            "width": world.spec.width, "height": world.spec.height,
            "spawn": list(world.spec.spawn),
            "laws": asdict(world.laws),
        },
    }


def _run_second_decision(mode, world, mind, original):
    prior = original["arms"][mode]
    captured = world.capture()
    before_world = _snapshot_world(world)
    before_mind = F1C.seal_mind(mind)
    if (before_world["t"] != 1 or before_world["dead"] or
            before_mind != prior["private_persisted_postaction"] or
            list(world.body) != prior["body_after_paid_learning"]):
        raise AssertionError("second decision not anchored at exact F1C paid outcome")
    # Experimenter-only forecast witness. The decision itself still reads ONLY
    # Mind's own private EffectsModel through its existing paid score path.
    predictor = mind.effects.predict(("dormir",))
    prediction = {"mean_delta": list(predictor[0]), "uncertainty": predictor[1]}

    allowance = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(captured, allowance)
    if work != allowance.work:
        raise AssertionError("second Mind.decide cost not funded in its own allowance")
    promised = dict(zip(("energy", "vigilance"), cognitive_cost(world.laws, work)))
    if world.t != 1:
        raise AssertionError("next decision advanced the physical World without its native step")
    # The chosen action may be ANY naturally admitted command. No rescue,
    # intervention, precomputed option, or forced sleep/wait is introduced.
    outcome = world.step(action, param, work)
    if world.t != 2:
        raise AssertionError("not exactly one subsequent native physical tick")
    for coin in ("energy", "vigilance"):
        bill = outcome["cognitive_accounting"][coin]
        if (abs(bill["requested"]-promised[coin]) > 1e-10 or
                abs(bill["paid"]-promised[coin]) > 1e-10 or bill["unpaid"] != 0.):
            raise AssertionError("next decision lacked native two-currency payment")
    record = {
        "mode": mode,
        "f1c_original_receipt_sha256": prior["receipt_sha256"],
        "f1c_original_persisted_mind_sha256":
            prior["private_persisted_postaction"]["sha256"],
        "before_world": before_world,
        "before_mind": before_mind,
        "next_capture": json.loads(F1C.canonical(captured)),
        "next_capture_sha256": F1C.digest(captured),
        "observer_only_sleep_forecast": prediction,
        "action": action, "param": param,
        "decision_info": json.loads(F1C.canonical(info)),
        "decision_work": asdict(work),
        "decision_allowance_remaining": list(allowance.remaining),
        "expected_native_cognitive_debit": promised,
        "mind_after_decision": F1C.seal_mind(mind),
        "actual_native_step": {
            "t": outcome["t"], "body": list(outcome["body"]),
            "moved": outcome["moved"], "dead": list(outcome["dead"]),
            "cognitive_accounting": deepcopy(outcome["cognitive_accounting"]),
        },
        "after_world": _snapshot_world(world),
        "next_learning_performed": False,
    }
    record["receipt_sha256"] = F1C.digest(record)
    return record


def classify(retain, discard):
    mot_different = (retain["action"], retain["param"]) != (
        discard["action"], discard["param"])
    work_equal = retain["decision_work"] == discard["decision_work"]
    bill_equal = (retain["expected_native_cognitive_debit"] ==
                  discard["expected_native_cognitive_debit"])
    if not mot_different:
        return "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
    if work_equal and bill_equal:
        return "NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED"
    return "NEXT_MOTOR_DECISION_DIFFERENCE_WITH_UNEQUAL_COGNITION"


def produce(original):
    instances = {}
    for mode in MODES:
        instances[mode] = _matched_state(mode, original)
    if _snapshot_world(instances["retain"][0]) != _snapshot_world(instances["discard_after_compute"][0]):
        raise AssertionError("next decision worlds are not physically paired")
    if instances["retain"][0].capture() != instances["discard_after_compute"][0].capture():
        raise AssertionError("next decision first-person perceptions are not paired")
    a = dict(F1C.seal_mind(instances["retain"][1])["data"]["private"]["__dict__"])
    b = dict(F1C.seal_mind(instances["discard_after_compute"][1])["data"]["private"]["__dict__"])
    if set(a) != set(b) or {k for k in a if a[k] != b[k]} != {
            "effects", "values", "buffer"}:
        raise AssertionError("post-action arms differ outside the originally paid learned state")

    rows = {mode: _run_second_decision(mode, *instances[mode], original)
            for mode in MODES}
    retain, discard = (rows[x] for x in MODES)
    for field in ("before_world", "next_capture", "next_capture_sha256"):
        if retain[field] != discard[field]:
            raise AssertionError("unpaired second decision "+field)
    original_status = classify(retain, discard)
    report = {
        "schema": SCHEMA,
        "evidence_class": "SOFTWARE_ONLY_SYNTHETIC_TWO_TICKS_NO_G2_HISTORY",
        "source_anchor_main_sha": SOURCE_HEAD,
        "f1c_original_json_sha256": F1C_ORIGINAL_SHA,
        "f1c_independent_cold_json_sha256": F1C_COLD_SHA,
        "f1c_provenance_chain_sha256": original["provenance_chain_sha256"],
        "frozen_stage8e2": FROZEN_NEGATIVE,
        "source_case": "learned_beneficial_sleep",
        "causal_intervention": "real_postaction_learned_state_retained_vs_paid_computed_discarded",
        "predecision_different_mind_fields": ["buffer", "effects", "values"],
        "next_step_bodies_world_capture_equal": True,
        "next_decision_same_native_world_laws": True,
        "arms": rows,
        "observed_motor_effect_classification": original_status,
        "next_option_same": retain["decision_info"].get("option")==discard["decision_info"].get("option"),
        "next_work_exactly_equal": retain["decision_work"] == discard["decision_work"],
        "next_native_cognitive_debit_exactly_equal":
            retain["expected_native_cognitive_debit"] == discard["expected_native_cognitive_debit"],
        "executed_native_world_step_calls": 4,
        "run_life_executed": False,
        "new_native_lives": 0,
        "new_scientific_cohorts": 0,
        "learned_state_was_personally_acquired_before_next_decision": True,
        "historical_g2_memory_equivalence": "NOT_DEMONSTRATED",
        "whole_life_native_custody": "NOT_CLAIMED",
        "gain_in_survival_or_heritability": "NOT_TESTED",
    }
    report["provenance_chain_sha256"] = F1C.digest({
        "source": SOURCE_HEAD,
        "f1c_json": F1C_ORIGINAL_SHA,
        "f1c_chain": report["f1c_provenance_chain_sha256"],
        "next_receipts": [rows[k]["receipt_sha256"] for k in MODES],
    })
    return report


def main():
    p = argparse.ArgumentParser(description="Native F1D first-person subsequent decision, no lives")
    p.add_argument("--f1c-original", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    original = read_f1c_exact(args.f1c_original)
    report = produce(original)
    with Path(args.output).open("xb") as out:
        out.write(F1C.canonical(report))
    print(json.dumps({"observed_classification":report["observed_motor_effect_classification"],
                      "second_actions":{k: [v["action"],v["param"]]
                                          for k,v in report["arms"].items()},
                      "native_two_tick_calls":report["executed_native_world_step_calls"],
                      "new_lives":report["new_native_lives"],
                      "sha256":F1C.digest(report)},sort_keys=True))


if __name__ == "__main__":
    main()
