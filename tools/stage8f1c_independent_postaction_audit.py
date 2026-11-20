"""Cold F1C receipt audit: Python standard library ONLY, no engine imports.

Recompute the native one-tick sleep and fatal-null physics, decision and
learning costs, all state seals, observed effect-model arithmetic and the
matched compute-and-discard intervention. Never instantiate World or Mind.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path

SCHEMA = "i3-stage8f1c-native-synthetic-paid-postaction-learning/v0"
BASE = "dd0d36a61cfce44c38efc2846a8c25f978da7266"
F1 = "4014a59027cc53bcfb6e7a9c6e6c827e017711b9"
F1B_SHA = "9e645b8aed70c5cf68047c2cd25ddd50d4d9a5441a147d9c6a11531aec91c65a"
NEGATIVE = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
MICRO = {"cycles": 1, "simulated_steps": 0, "memory_items": 64, "replays": 0}
LEARN = {"cycles": 2, "simulated_steps": 32, "memory_items": 3, "replays": 1}
CURRENCIES = ("energy", "vigilance")
NAMES = ("retain", "discard_after_compute")
TOL = 1e-9


def c(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def h(obj):
    return sha256(c(obj)).hexdigest()


def check(condition, reason):
    if not condition:
        raise ValueError(reason)


def near(a, b):
    return (type(a) in (int, float) and type(b) in (int, float)
            and isfinite(a) and isfinite(b)
            and isclose(a, b, abs_tol=TOL, rel_tol=1e-11))


def body_equal(actual, expected, description):
    check(type(actual) is list and len(actual) == 5
          and all(near(x, y) for x, y in zip(actual, expected)),
          "native body balance invalid: " + description)


def cost(work):
    check(type(work) is dict and set(work) == {
        "cycles", "simulated_steps", "memory_items", "replays"}
        and all(type(v) is int and v >= 0 for v in work.values()),
        "non-native or negative cognitive work")
    cy, sim, mem, replay = (work[k] for k in
                            ("cycles", "simulated_steps", "memory_items", "replays"))
    return {"energy": cy * .02 + sim * .002 + mem * .0002 + replay * .005,
            "vigilance": cy * .05 + sim * .002 + replay * .01}


def check_bill(audit, expected, name):
    check(type(audit) is dict and set(audit) == set(CURRENCIES),
          "missing native two-currency bill: " + name)
    for coin in CURRENCIES:
        row = audit[coin]
        check(type(row) is dict and set(row) == {"requested", "paid", "unpaid"}
              and near(row["requested"], expected[coin])
              and near(row["paid"], expected[coin])
              and near(row["unpaid"], 0.0),
              "unpaid or invented native cognition: " + name + "/" + coin)


def clamp(value):
    return min(100.0, max(0.0, value))


def native_step(before, decision_work, action):
    """Independent BodyLaws v2 one-tick arithmetic for sleep or inactivity."""
    check(action in ("dormir", None), "forbidden motor action in frozen F1C")
    debit = cost(decision_work)
    energy, food, water, integrity, vigilance = before
    check(energy >= debit["energy"] and vigilance >= debit["vigilance"],
          "unfunded decision")
    energy -= debit["energy"]
    vigilance -= debit["vigilance"]
    food = clamp(food - .2)
    water = clamp(water - .4)
    hydrated = water >= .05
    if action == "dormir":
        gain = (min(3.0, max(0.0, 100.0 - energy), food / .05)
                if hydrated else 0.0)
        energy += gain
        food -= gain * .05
        vigilance += 4.0
        if hydrated:
            repair = min(.2, max(0.0, 100.0 - integrity), food / .10)
            integrity += repair
            food -= repair * .10
    after = [clamp(v) for v in (energy, food, water, integrity, vigilance)]
    dead = [label for label, i in (("zero_food", 1),
                                    ("zero_water", 2),
                                    ("zero_integrity", 3)) if after[i] <= 0]
    return after, dead, debit


def private_fields(sealed):
    check(type(sealed) is dict and set(sealed) == {"data", "sha256"}
          and h(sealed["data"]) == sealed["sha256"], "private snapshot hash mismatch")
    record = sealed["data"]
    check(type(record) is dict and record.get("class") == "PaidMicrodecisionMind"
          and type(record.get("private")) is dict
          and set(record["private"]) == {"__dict__"},
          "unrecognized complete private Mind witness")
    pairs = record["private"]["__dict__"]
    check(type(pairs) is list and all(type(row) is list and len(row) == 2
          and type(row[0]) is str for row in pairs), "corrupt Mind fields")
    fields = dict(pairs)
    check(len(fields) == len(pairs) and
          {"effects", "values", "buffer", "rng", "_budget_rng", "last",
           "intention", "theta", "p", "w", "gammas"} <= set(fields),
          "partial private snapshot cannot establish matched initial state")
    return fields


def observed_stats(sealed):
    fields = private_fields(sealed)
    effects = fields["effects"]
    check(type(effects) is dict and set(effects) == {"__effects_model__"},
          "not a real EffectsModel witness")
    em = dict(effects["__effects_model__"]["__dict__"])
    check(set(em) == {"stats"}, "unknown effects layout")
    stats = em["stats"]["__dict__"]
    out = {}
    for key, state in stats:
        check(type(key) is dict and set(key) == {"__tuple__"}
              and type(key["__tuple__"]) is list
              and type(state) is list and len(state) == 3,
              "invalid native effects statistics")
        out[tuple(key["__tuple__"])] = state
    check(len(out) == len(stats), "duplicate effects key")
    return out


def learned_delta_verified(pre, post, before_body, after_body):
    old = observed_stats(pre)
    new = observed_stats(post)
    check(set(new) == set(old) == {("dormir",), ("*",)},
          "unexpected learned effects or missing personal prior")
    delta = [x - y for x, y in zip(after_body, before_body)]
    for key in (("dormir",), ("*",)):
        n, mean, count = old[key]
        nx, mx, cx = new[key]
        check(near(n, 1.) and count == 1 and near(nx, n + 1.)
              and cx == count + 1 and len(mean) == len(mx) == 5,
              "missing individually experienced effect observation")
        check(all(near(mx[i], mean[i] + (delta[i] - mean[i]) / (n + 1.))
                  for i in range(5)), "effect model learned a fabricated consequence")
    fb = private_fields(pre)
    fa = private_fields(post)
    check(fb["values"] != fa["values"], "no TD value update persisted")
    check(fb["buffer"] != fa["buffer"]
          and len(fb["buffer"]["__deque__"]) == 0
          and len(fa["buffer"]["__deque__"]) == 1,
          "no trace of the funded outcome/replay buffer")
    return delta


def audit(report, input_sha=None):
    check(type(report) is dict and report.get("schema") == SCHEMA
          and report.get("source_base_main_sha") == BASE
          and report.get("source_f1_sha") == F1
          and report.get("f1b_original_native_receipt_sha256") == F1B_SHA
          and report.get("frozen_negative_stage8e2") == NEGATIVE
          and report.get("status") == "NATIVE_SYNTHETIC_POSTACTION_RECEIPTS_AWAITING_COLD_AUDIT"
          and report.get("evidence_class") ==
            "DEVELOPMENT_ONLY_SYNTHETIC_ONE_TICK_NOT_HISTORICAL_G2"
          and report.get("native_world_step_calls_per_report") == 3
          and report.get("native_full_lives_created") == 0
          and report.get("new_scientific_cohorts") == 0
          and report.get("run_life_executed") is False
          and report.get("native_whole_life_evidence_head") == "NOT_CLAIMED"
          and report.get("historical_g2_mind_snapshots") ==
            "NOT_ARCHIVED_NOT_RECONSTRUCTED"
          and type(report.get("arms")) is dict
          and set(report["arms"]) == set(NAMES),
          "invalid F1C evidence class, provenance, or admission boundary")

    retained, shadow = (report["arms"][x] for x in NAMES)
    exact_matches = ("capture_sha256", "before_body", "private_before_decision",
                     "action", "param", "decision_work", "native_motor_step",
                     "body_before_postaction_learning",
                     "private_before_postaction_learning", "learning_work",
                     "prepaid_replays", "executed_replays",
                     "learning_allowance_remaining", "paid_postaction_learning",
                     "body_after_paid_learning", "private_computed_postaction")
    for field in exact_matches:
        check(retained[field] == shadow[field],
              "unmatched physical, memory or funding counterfactual: " + field)
    for name, record in report["arms"].items():
        without_seal = {k: v for k, v in record.items() if k != "receipt_sha256"}
        check(h(without_seal) == record.get("receipt_sha256"),
              "original F1C native receipt modified")
        check(record["mode"] == name and record["source_case"] == "learned_beneficial_sleep"
              and record["action"] == "dormir" and record["param"] is None
              and record["decision_funding"] == "F1_PAID_SELF_SELECTED_ACTION"
              and record["decision_work"] == MICRO
              and record["capture"]["body"] == record["before_body"]
              and h(record["capture"]) == record["capture_sha256"],
              "not the frozen first-person native F1 microchoice")
        private_fields(record["private_before_decision"])
        private_fields(record["private_before_postaction_learning"])
        private_fields(record["private_computed_postaction"])
        private_fields(record["private_persisted_postaction"])
        step = record["native_motor_step"]
        check(step["t"] == 1 and step["dead"] == [] and step["moved"] is False,
              "wrong native one-tick result")
        physical_body, dead, decision_bill = native_step(
            record["before_body"], record["decision_work"], "dormir")
        body_equal(step["body"], physical_body, "World.step after chosen sleep")
        check(step["dead"] == dead, "native physical death concealed")
        check_bill(step["cognitive_accounting"], decision_bill, "World.step decision")

        check(record["learning_work"] == LEARN and
              record["prepaid_replays"] == record["executed_replays"] == 1,
              "a replay or outcome update was not pre-authorized")
        before_learning = record["body_before_postaction_learning"]
        body_equal(before_learning, step["body"], "pre-learning physiological boundary")
        learning_bill = cost(record["learning_work"])
        check_bill(record["paid_postaction_learning"], learning_bill, "World.pay_cognition")
        actual_paid = list(before_learning)
        actual_paid[0] -= learning_bill["energy"]
        actual_paid[4] -= learning_bill["vigilance"]
        check(actual_paid[0] >= 0 and actual_paid[4] >= 0,
              "learning borrowed future food or sleep energy")
        body_equal(record["body_after_paid_learning"], actual_paid,
                   "actual native postaction resource debit")
        body_equal(record["learning_allowance_remaining"], actual_paid,
                   "preauthorized budget must equal World debit")
        check(record["unaffordable_extra_payment_rejected_without_mutation"] is True,
              "unfunded extra cognition was not rejected")

    check(retained["private_persisted_postaction"] ==
          retained["private_computed_postaction"] ==
          shadow["private_computed_postaction"],
          "different computations or fabricated retained learned state")
    check(shadow["private_persisted_postaction"] ==
          shadow["private_before_postaction_learning"],
          "shadow-discard illegally retained the learned update")
    check(retained["private_persisted_postaction"] !=
          shadow["private_persisted_postaction"],
          "the paid update made no observed, isolated change")
    deltas = learned_delta_verified(
        retained["private_before_postaction_learning"],
        retained["private_persisted_postaction"],
        retained["before_body"], retained["body_after_paid_learning"])

    terminal = report["terminal_no_learning"]
    check(terminal["source_case"] == "terminal_food_not_rescued"
          and terminal["action"] is None and terminal["decision_work"] == MICRO
          and terminal["native_world_steps"] == 1
          and terminal["postmortem_payment_rejected_without_mutation"] is True
          and terminal["prepaid_learning_work"] == {
              "cycles": 0, "simulated_steps": 0, "memory_items": 0, "replays": 0},
          "death did not stop postaction learning")
    mortal_body, death, terminal_bill = native_step(
        terminal["before_body"], terminal["decision_work"], None)
    body_equal(terminal["motor_body"], mortal_body, "fatal native World.step")
    check(terminal["death_causes"] == death == ["zero_food"],
          "real terminal death was censored")
    check_bill(terminal["native_cognitive_accounting"], terminal_bill,
               "terminal World.step")
    chain = h({"source": BASE,
               "receipts": [retained["receipt_sha256"], shadow["receipt_sha256"]],
               "terminal": terminal})
    check(report["provenance_chain_sha256"] == chain,
          "complete original action-payment-learning chain altered")

    learning_bill = cost(LEARN)
    return {
        "schema": "i3-stage8f1c-independent-cold-paid-learning-audit/v0",
        "status": "SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS",
        "source_report_sha256": input_sha or h(report),
        "paired_native_action_and_learning_cases": 1,
        "native_world_step_receipts_verified": 3,
        "paid_learning_computations": 2,
        "retained_paid_updates": 1,
        "equal_paid_discarded_updates": 1,
        "learning_replays_actually_executed_each": 1,
        "learning_energy_paid_each": learning_bill["energy"],
        "learning_vigilance_paid_each": learning_bill["vigilance"],
        "effect_delta_observed_from_native_body": deltas,
        "terminal_death_preserved": True,
        "full_lives": 0, "scientific_cohorts": 0,
        "historical_g2_memory_equivalence": "NOT_DEMONSTRATED",
        "causal_gamma_verdict": NEGATIVE,
    }


def main():
    p = argparse.ArgumentParser(description="Cold independent stdlib F1C reducer")
    p.add_argument("source")
    p.add_argument("output")
    args = p.parse_args()
    raw = Path(args.source).read_bytes()
    result = audit(json.loads(raw), sha256(raw).hexdigest())
    with Path(args.output).open("xb") as f:
        f.write(c(result))
    print(json.dumps({"status": result["status"],
                      "native_receipts": result["native_world_step_receipts_verified"],
                      "learning_energy": result["learning_energy_paid_each"],
                      "sha256": h(result)}, sort_keys=True))


if __name__ == "__main__":
    main()
