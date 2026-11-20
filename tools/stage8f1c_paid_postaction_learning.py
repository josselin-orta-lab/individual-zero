"""F1C synthetic one-tick native post-action learning custody; never run_life.

This deliberately exercises the existing Mind/World learning transaction,
NOT a new learning rule or an admitted F1 life policy. Its two principal
arms take the SAME action and pay the SAME post-action work. The shadow arm
executes the actual update on a detached Mind and discards only retention.
F1B's separate F1-versus-discard decision-cost comparison remains intact.
"""
from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite, isclose
from pathlib import Path
from random import Random

from i3.modules.body import CognitiveBudget, CognitiveWork, CognitiveFundingError, cognitive_cost
from i3.modules.mind import EffectsModel
from i3.modules.stage8f1_paid_microdecision_mind import MICRO_WORK, PaidMicrodecisionMind
from tools import stage8f1_matched_native_funding as F1B

SCHEMA = "i3-stage8f1c-native-synthetic-paid-postaction-learning/v0"
BASE = "dd0d36a61cfce44c38efc2846a8c25f978da7266"
F1_SOURCE = "4014a59027cc53bcfb6e7a9c6e6c827e017711b9"
F1B_ORIGINAL_SHA256 = "9e645b8aed70c5cf68047c2cd25ddd50d4d9a5441a147d9c6a11531aec91c65a"
NEGATIVE = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
WORK = ("cycles", "simulated_steps", "memory_items", "replays")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def digest(obj):
    return sha256(canonical(obj)).hexdigest()


def _stable(obj):
    """Typed COMPLETE private-state serialization; no repr or address-based fields.

    This is observation, not a reconstructible native checkpoint. Neither the
    candidate nor the native controller gets access to this laboratory record.
    """
    if obj is None or type(obj) in (bool, int, str):
        return obj
    if type(obj) is float:
        if not isfinite(obj):
            raise ValueError("non-finite native private state")
        return obj
    if type(obj) is tuple:
        return {"__tuple__": [_stable(v) for v in obj]}
    if type(obj) is list:
        return [_stable(v) for v in obj]
    if isinstance(obj, deque):
        return {"__deque__": [_stable(v) for v in obj],
                "maxlen": obj.maxlen}
    if type(obj) is dict:
        pairs = [[_stable(k), _stable(v)] for k, v in obj.items()]
        pairs.sort(key=lambda row: canonical(row[0]))
        return {"__dict__": pairs}
    if isinstance(obj, Random):
        return {"__random_state__": _stable(obj.getstate())}
    if type(obj) is EffectsModel:
        return {"__effects_model__": _stable(vars(obj))}
    raise TypeError("unserializable private Mind field: " + type(obj).__name__)


def seal_mind(mind):
    full = {"class": type(mind).__name__, "private": _stable(vars(mind))}
    return {"data": full, "sha256": digest(full)}


def paid_bill(laws, work, audit):
    cost = cognitive_cost(laws, work)
    for k, value in zip(("energy", "vigilance"), cost):
        row = audit[k]
        if not all(isclose(row[field], expected, rel_tol=0, abs_tol=1e-10)
                   for field, expected in (("requested", value),
                                           ("paid", value), ("unpaid", 0.))):
            raise AssertionError("native World failed to fund the exact two-currency bill")


def _full_action_and_learning(mode):
    if mode not in ("retain", "discard_after_compute"):
        raise ValueError("unknown retention mode")
    world, original = F1B.make_state(F1B.STATES[0])
    mind = F1B.cloned_mind(PaidMicrodecisionMind, original)
    body_before = list(world.body)
    capture = world.capture()
    before_decision = seal_mind(mind)
    allowance = CognitiveBudget(world.body, world.laws)
    action, param, decision_work, info = mind.decide(capture, allowance)
    if (action != "dormir" or param is not None or
            info["funding"] != "F1_PAID_SELF_SELECTED_ACTION" or
            decision_work != MICRO_WORK or allowance.work != decision_work):
        raise AssertionError("only the original voluntarily selected F1 sleep is admitted")
    native = world.step(action, param, decision_work)
    paid_bill(world.laws, decision_work, native["cognitive_accounting"])
    if native["dead"] or world.t != 1:
        raise AssertionError("learning source must be a real, surviving native action")
    motor = {"t": native["t"], "body": list(native["body"]),
             "dead": list(native["dead"]), "moved": native["moved"],
             "cognitive_accounting": deepcopy(native["cognitive_accounting"])}
    body_before_learning = list(world.body)

    # Same ordered transaction as run_life, but WITHOUT invoking run_life.
    # Observation/position does not grant a free effect-model update.
    mind.observe_outcome(native)
    before_learning = seal_mind(mind)
    learning = CognitiveBudget(world.body, world.laws)
    prepaid_replays = mind.prepare_learning(native, learning)
    if prepaid_replays is None or learning.work == CognitiveWork():
        raise AssertionError("native learning update unexpectedly unfunded")
    learning_work = learning.work
    learning_remaining = list(learning.remaining)
    audit = world.pay_cognition(learning_work)  # actual debit BEFORE update
    paid_bill(world.laws, learning_work, audit)
    native["body"] = world.body   # real runtime convention: learned delta is AFTER charge
    body_after_learning = list(world.body)
    target = mind if mode == "retain" else deepcopy(mind)
    executed_replays = target.learn_from_outcome(native, replay_limit=prepaid_replays)
    if executed_replays != prepaid_replays or world.t != 1:
        raise AssertionError("unpaid replays or a hidden additional time step")
    computed = seal_mind(target)
    persisted = seal_mind(mind)
    if computed["sha256"] == before_learning["sha256"]:
        raise AssertionError("no measurable actual learned outcome")
    if mode == "retain":
        if persisted != computed:
            raise AssertionError("retained learning must belong to the living Mind")
    else:
        if persisted != before_learning:
            raise AssertionError("discard-only comparator changed persistent private state")

    # A deliberately unaffordable payment on a detached post-action World
    # must fail WITHOUT a body mutation or an implicit learned update.
    rejected_world = deepcopy(world)
    refused_before = list(rejected_world.body)
    try:
        rejected_world.pay_cognition(CognitiveWork(cycles=1_000_000))
    except CognitiveFundingError:
        pass
    else:
        raise AssertionError("unaffordable second learning grant was accepted")
    if list(rejected_world.body) != refused_before:
        raise AssertionError("failed learning allocation changed actual body reserves")

    receipt = {
        "mode": mode, "source_case": "learned_beneficial_sleep",
        "capture": json.loads(canonical(capture)),
        "capture_sha256": F1B.digest(capture),
        "before_body": body_before,
        "private_before_decision": before_decision,
        "action": action, "param": param, "decision_funding": info["funding"],
        "decision_work": asdict(decision_work),
        "native_motor_step": motor,
        "body_before_postaction_learning": body_before_learning,
        "private_before_postaction_learning": before_learning,
        "learning_work": asdict(learning_work),
        "prepaid_replays": prepaid_replays,
        "executed_replays": executed_replays,
        "learning_allowance_remaining": learning_remaining,
        "paid_postaction_learning": deepcopy(audit),
        "body_after_paid_learning": body_after_learning,
        "private_computed_postaction": computed,
        "private_persisted_postaction": persisted,
        "unaffordable_extra_payment_rejected_without_mutation": True,
    }
    receipt["receipt_sha256"] = digest(receipt)
    return receipt


def _terminal_no_learning():
    world, original = F1B.make_state(F1B.STATES[6])
    mind = F1B.cloned_mind(PaidMicrodecisionMind, original)
    body_before = list(world.body)
    allowance = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(world.capture(), allowance)
    if action is not None or info["funding"] != "F1_PAID_VOLUNTARY_ABSTENTION":
        raise AssertionError("terminal case forced a forbidden rescue action")
    native = world.step(action, param, work)
    paid_bill(world.laws, work, native["cognitive_accounting"])
    if list(native["dead"]) != ["zero_food"] or not world.dead:
        raise AssertionError("actual vital death was hidden")
    before_attempt = list(world.body)
    learning = CognitiveBudget(world.body, world.laws)
    if mind.prepare_learning(native, learning) is not None:
        raise AssertionError("postmortem learning was authorized")
    try:
        world.pay_cognition(CognitiveWork(cycles=1))
    except RuntimeError:
        pass
    else:
        raise AssertionError("world permitted cognition after irreversible death")
    if list(world.body) != before_attempt or learning.work != CognitiveWork():
        raise AssertionError("postmortem payment changed body or allowance")
    return {
        "source_case": "terminal_food_not_rescued", "before_body": body_before,
        "action": action, "decision_work": asdict(work),
        "motor_body": list(native["body"]),
        "native_cognitive_accounting": deepcopy(native["cognitive_accounting"]),
        "death_causes": list(native["dead"]),
        "prepaid_learning_work": asdict(learning.work),
        "postmortem_payment_rejected_without_mutation": True,
        "native_world_steps": world.t,
    }


def produce():
    retained = _full_action_and_learning("retain")
    discarded = _full_action_and_learning("discard_after_compute")
    fields_equal = ("capture_sha256", "before_body", "private_before_decision",
                    "action", "param", "decision_work", "native_motor_step",
                    "body_before_postaction_learning",
                    "private_before_postaction_learning", "learning_work",
                    "prepaid_replays", "executed_replays",
                    "learning_allowance_remaining", "paid_postaction_learning",
                    "body_after_paid_learning", "private_computed_postaction")
    if any(retained[k] != discarded[k] for k in fields_equal):
        raise AssertionError("paid retention pair does not have identical native inputs and work")
    if (retained["private_persisted_postaction"] != retained["private_computed_postaction"]
            or discarded["private_persisted_postaction"] != discarded["private_before_postaction_learning"]
            or retained["private_persisted_postaction"] == discarded["private_persisted_postaction"]):
        raise AssertionError("retention counterfactual did not isolate memory")
    terminal = _terminal_no_learning()
    report = {
        "schema": SCHEMA, "status": "NATIVE_SYNTHETIC_POSTACTION_RECEIPTS_AWAITING_COLD_AUDIT",
        "evidence_class": "DEVELOPMENT_ONLY_SYNTHETIC_ONE_TICK_NOT_HISTORICAL_G2",
        "source_base_main_sha": BASE, "source_f1_sha": F1_SOURCE,
        "f1b_original_native_receipt_sha256": F1B_ORIGINAL_SHA256,
        "frozen_negative_stage8e2": NEGATIVE,
        "arms": {"retain": retained, "discard_after_compute": discarded},
        "terminal_no_learning": terminal,
        "native_world_step_calls_per_report": 3,
        "native_full_lives_created": 0, "new_scientific_cohorts": 0,
        "run_life_executed": False,
        "native_whole_life_evidence_head": "NOT_CLAIMED",
        "historical_g2_mind_snapshots": "NOT_ARCHIVED_NOT_RECONSTRUCTED",
    }
    report["provenance_chain_sha256"] = digest({
        "source": BASE,
        "receipts": [retained["receipt_sha256"], discarded["receipt_sha256"]],
        "terminal": terminal})
    return report


def main():
    parser = argparse.ArgumentParser(description="Synthetic post-action learning without life births")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = produce()
    with Path(args.output).open("xb") as stream:
        stream.write(canonical(report))
    print(json.dumps({"status": report["status"],
                      "native_one_tick_steps": report["native_world_step_calls_per_report"],
                      "full_lives": 0,
                      "sha256": digest(report)}, sort_keys=True))


if __name__ == "__main__":
    main()
