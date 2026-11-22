"""F1L independent DEV_ONLY cold verifier: Python 3.12 stdlib, NO i3 engine.

This module never imports F1L's producer, Mind, World or BodyLaws.
Reconstruct real F1J evidence rounds, own T1 means/paid learning,
native water/food/physiology, and the time-limited T5 masking.
Only DEV_L engineering receipts are accepted; NOT an F1L scientific result.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
from hashlib import sha1
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1j_independent_fixed_round_cold_audit as J
from tools import stage8f1k_independent_policy_value_cold_audit as K

SCHEMA = "i3-stage8f1l-development-only-personal-content-T60/v0"
ARMS = ("full", "full_sham", "stale_owned_t1_means")
GRID = ("docs/research/studies/stage8f1-paid-microdecision/"
        "STAGE8F1L_HELDOUT_EQUAL_PAID_MEMORY_CONTENT_GRID_2026-11-22.json")
PROTOCOL = ("docs/research/studies/stage8f1-paid-microdecision/"
            "STAGE8F1L_EQUAL_PAID_CONTENT_BODY_VALUE_PREEXPOSURE_2026-11-22.md")
GRID_BLOB = "e336c12640a9143f026afafd8de44af6a46c4c97"
PROTOCOL_BLOB = "4c89ced38db82b8edf688c44bccd81601abda057"
PREREG_MAIN = "620e58a6b149ccb8169463a33eee9bd81d4ebd22"
SEEDS = list(range(202611229601, 202611229609))
SOURCE_BLOBS = {
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
    "tools/stage8f1h_prospective_native_body_value.py":
        "02c5ece502729e3fa341f17cfa9cdc03e8c50bf4",
    "tools/stage8f1c_paid_postaction_learning.py":
        "c3d00fe078cac0ad9487ac39c2c8c7e081f32313",
    "tools/stage8f1d_next_decision_retention.py":
        "19f10a02b73759b52856e177ac3731f5826281c6",
}


def check(value, message):
    K.check(value, "F1L COLD: " + message)


def blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def dev_grid(full):
    """A separately authored, exact, fully independent DEV-only source grid."""
    ecologies = [
        {"id": "DEV_L_west_springs", "water": [0, 1], "water_gain": 17,
         "water_stock": 3, "water_max_stock": 3, "water_restock_every": 4,
         "food": [2, 2], "token": "dev-f1l-cress", "food_gain": 16,
         "integrity_delta": 1.25, "food_quantity": 3,
         "food_max_quantity": 3, "food_restock_every": 5},
        {"id": "DEV_L_east_tuber", "water": [2, 1], "water_gain": 25,
         "water_stock": 2, "water_max_stock": 2, "water_restock_every": 3,
         "food": [0, 2], "token": "dev-f1l-tuber", "food_gain": 29,
         "integrity_delta": -0.75, "food_quantity": 2,
         "food_max_quantity": 2, "food_restock_every": 6},
    ]
    origins = [{
        "id": "DEV_L%02d" % (i + 1),
        "ecology": ecologies[i // 4]["id"],
        "seed": SEEDS[i],
        "body": [60 + i % 4, 69 - i % 4, 34 + (i % 4) * 0.5,
                 93 - (i % 4) * 0.3, 96 - (i % 4) * 0.2],
    } for i in range(8)]
    if not full:
        origins = [origins[0], origins[4]]
    return {
        "schema": "i3-stage8f1l-dev-%s/v0" % ("t60" if full else "smoke"),
        "phase": "DEV_ONLY",
        "world": {"width": 3, "height": 3, "spawn": [1, 1],
                  "laws": "BodyLaws() i3-body-laws-v2", "changes": []},
        "ecologies": ecologies, "origins": origins,
        "personal_history_ticks": 4, "fork_tick": 5,
        "final_tick": 60 if full else 9, "arms": list(ARMS),
    }


def source_gate():
    """Byte-locked prereg and original reference, without importing motor code."""
    for path, expected in SOURCE_BLOBS.items():
        check(blob(Path(path).read_bytes()) == expected,
              "original reference implementation changed: " + path)
    check(blob(Path(GRID).read_bytes()) == GRID_BLOB and
          blob(Path(PROTOCOL).read_bytes()) == PROTOCOL_BLOB,
          "postexposure rewrite of preregistered F1L sources")
    heldout = json.loads(Path(GRID).read_bytes())
    check(heldout["scientific_exposure_authorized"] is False and
          heldout["frozen_prior_results"]["F1K"] ==
          "INCONCLUSIVE_NO_REAL_SURCHARGE" and
          heldout["arms"] == list(ARMS) and
          [r["seed"] for r in heldout["origins"]] ==
          list(range(202611229501, 202611229533)) and
          len(heldout["ecologies"]) == 8,
          "F1L scientific holdout was silently reallocated")
    return True


def origin_world(grid, root):
    state = K.origin_world(grid, root)
    state["world_spec"]["name"] = (
        "F1L_DEV_ORIGIN_" + root["id"] + "_" + root["ecology"])
    return state


def seal_after_mutation(seal):
    seal["sha256"] = I.h(seal["data"])
    return seal


def substitute_own_means(before, prior):
    """Cold, engine-free replay of only personally acquired T1 means."""
    copied = deepcopy(before)
    current = K.effects(copied)
    keys = sorted(set(current) & set(prior), key=repr)
    check(bool(keys), "T5 mask had no personally acquired T1 mean keys")
    for key in keys:
        check(len(current[key]) == 3 and len(prior[key]) == 3
              and len(current[key][1]) == len(prior[key][1]) == 5,
              "non-original personal mean shape")
        current[key][1][:] = deepcopy(prior[key][1])
    return seal_after_mutation(copied), [list(x) for x in keys]


def restore_owned_effects(exposed_after_decision, before_decision):
    restored = deepcopy(exposed_after_decision)
    authentic = deepcopy(K.private(before_decision)["effects"])
    pairs = restored["data"]["private"]["__dict__"]
    found = 0
    for entry in pairs:
        if entry[0] == "effects":
            entry[1] = authentic
            found += 1
    check(found == 1, "missing original EffectsModel for restoration")
    return seal_after_mutation(restored)


def verify_step(step, world, mind, *, arm, t1=None, horizon=60):
    """Recompute the motor, real two-coin cost, F1J rounds and paid learning."""
    tick = world["t"] + 1
    check(step["t"] == tick and tick <= horizon and not world["dead"] and
          step["before_mind"] == mind and
          step["no_experimental_action_override"] is True,
          "noncontiguous native steps, altered private brain, imposed motor")
    K.world_eq(step["before_world"], world, "predecision")
    K.private(mind, "F1JFixedRoundMind")
    check(step["capture"] == K.perceive(world) and
          step["capture_sha256"] == I.h(step["capture"]),
          "fake first-person sensory capture")
    expected_mode = arm if tick == 5 else "full"
    check(step["readout_mode"] == expected_mode,
          "unexpected or prolonged post-T5 memory intervention")
    prior_mind = K.private(mind)
    exposed = deepcopy(mind)
    masked_keys = []
    if expected_mode == "stale_owned_t1_means":
        check(type(t1) is dict and bool(t1),
              "mask has no verified T1 same-person source")
        exposed, masked_keys = substitute_own_means(mind, t1)
    check(step["temporary_prior_mean_keys"] == masked_keys and
          step["exposed_mind_during_decision"] == exposed,
          "forged or cross-person memory readout")
    after_exposed = step["after_decision_exposed_mind"]
    K.private(after_exposed, "F1JFixedRoundMind")
    check(step["after_restoration_before_motor"] ==
          restore_owned_effects(after_exposed, mind),
          "readout mask was not restored BEFORE native bodily World.step")
    restored = step["after_restoration_before_motor"]
    f = K.private(restored)
    check(f["values"] == prior_mind["values"] and
          f["buffer"] == prior_mind["buffer"],
          "TD or episodic buffer modified instead of owned means")
    info = step["decision_info"]
    if info.get("funding") == "FUNDED":
        last = f["last"]
        check(type(last) is dict and set(last) == {"__tuple__"} and
              len(last["__tuple__"]) == 4 and
              last["__tuple__"][0] == {"__tuple__": world["body"]} and
              last["__tuple__"][2] == step["action"] and
              last["__tuple__"][3] == step["param"],
              "native motor was not the individual's actual decision")
        observer = info["observer"]
        witness = observer["competition_witness"]
        check(observer["admitted_action"] == step["action"] and
              witness["status"] == "ACTION_ADMITTED" and
              witness["final_admitted_action"] == step["action"] and
              witness["final_admitted_option"] == info["option"],
              "experimenter overrode chosen motor action")
    else:
        check(step["action"] is None and step["param"] is None,
              "unfunded choice was forcibly executed")
    cost = I.cost(step["cognitive_work"])
    check(cost == step["requested_native_cost"],
          "fabricated cognitive invoice")
    I.check_bill(step["native_motor"]["cognitive_accounting"],
                 cost, "F1L real World.step two-coin payment")
    remaining = list(world["body"])
    remaining[0] -= cost["energy"]
    remaining[4] -= cost["vigilance"]
    I.body_equal(step["decision_remaining"], remaining,
                 "real predecision paid budget")
    rounds = J.cold_paid_fixed_competition(step)["audited_rounds"]
    state, summary = K.physical(
        world, step["action"], step["param"], step["cognitive_work"],
        step["native_motor"]["cognitive_accounting"])
    for k in ("t", "dead", "moved"):
        check(step["native_motor"][k] == summary[k],
              "forged native motor " + k)
    I.body_equal(step["native_motor"]["body"], summary["body"],
                 "body after real action")
    K.world_eq(step["after_motor_world"], state, "postmotor")
    newworld, newmind = K.paid_learning(step, state)
    K.verify_paid_personal_learning(step)
    K.world_eq(step["after_paid_learning_world"], newworld,
               "after authentic funded learning")
    check(step["receipt_sha256"] == I.h({
        k: v for k, v in step.items() if k != "receipt_sha256"}),
        "modified individual native receipt")
    return newworld, newmind, rounds


def metrics(steps, world, error, horizon):
    return K.metrics(steps, world, error, horizon)


def comparable(full, sham, stale, source_valid):
    if not source_valid:
        return {
            "source_valid": False, "sham_neutral": False,
            "equal_t5_decision_cost": False, "motor_changed": None,
            "delta_lived_ticks": None, "pareto": None,
            "arm_valid": False,
        }
    check(all(x["steps"] for x in (full, sham, stale)),
          "missing T5 original arm for paid source")
    stripped = lambda step: {
        k: v for k, v in step.items()
        if k not in ("readout_mode", "receipt_sha256")}
    neutral = (full["metrics"] == sham["metrics"] and
               full["last_world"] == sham["last_world"] and
               full["last_mind"] == sham["last_mind"] and
               len(full["steps"]) == len(sham["steps"]) and
               all(stripped(a) == stripped(b)
                   for a, b in zip(full["steps"], sham["steps"])))
    valid = neutral and all(
        arm["metrics"]["native_error"] is None
        for arm in (full, sham, stale))
    if not valid:
        return {
            "source_valid": True, "sham_neutral": neutral,
            "equal_t5_decision_cost": False, "motor_changed": None,
            "delta_lived_ticks": None, "pareto": None,
            "arm_valid": False,
        }
    a, b = full["steps"][0], stale["steps"][0]
    equal = all(a[k] == b[k] for k in (
        "before_world", "before_mind", "capture", "capture_sha256",
        "cognitive_work", "requested_native_cost", "decision_remaining",
    )) and (a["native_motor"]["cognitive_accounting"] ==
            b["native_motor"]["cognitive_accounting"])
    delta = (full["metrics"]["lived_ticks_t5_t60"] -
             stale["metrics"]["lived_ticks_t5_t60"])
    pareto = "NOT_EQUAL_SURVIVAL"
    if (delta == 0 and full["metrics"]["alive_at_horizon"] and
            stale["metrics"]["alive_at_horizon"]):
        x, y = full["metrics"]["terminal_body"], stale["metrics"]["terminal_body"]
        if all(u >= v - 1e-9 for u, v in zip(x, y)) and any(
                u > v + 1e-9 for u, v in zip(x, y)):
            pareto = "FULL_FIVE_CHANNEL_DOMINANCE"
        elif all(v >= u - 1e-9 for u, v in zip(x, y)) and any(
                v > u + 1e-9 for u, v in zip(x, y)):
            pareto = "STALE_FIVE_CHANNEL_DOMINANCE"
        elif all(abs(u - v) <= 1e-9 for u, v in zip(x, y)):
            pareto = "FIVE_CHANNELS_EQUAL"
        else:
            pareto = "MIXED_BODILY_TRADEOFF"
    return {
        "source_valid": True, "sham_neutral": neutral,
        "equal_t5_decision_cost": equal,
        "motor_changed": (a["action"], a["param"]) !=
                         (b["action"], b["param"]),
        "delta_lived_ticks": delta, "pareto": pareto,
        "arm_valid": True,
    }


def audit(report):
    """Never issues an F1L scientific result or any heldout L birth."""
    source_gate()
    grid = dev_grid(full=report.get("final_tick") == 60)
    roots = grid["origins"]
    check(report.get("schema") == SCHEMA and
          report.get("phase") == "DEV_ONLY" and
          report.get("producer_only_status") == "DEV_ONLY_NOT_SCIENTIFIC" and
          report.get("scientific_verdict") is None and
          report.get("origin_count") == len(roots) and
          report.get("origin_ids") == [r["id"] for r in roots] and
          report.get("preregistered_main") == PREREG_MAIN and
          report.get("grid_blob_sha") == GRID_BLOB and
          report.get("protocol_blob_sha") == PROTOCOL_BLOB and
          report.get("source_policy") == "F1JFixedRoundMind" and
          report.get("arms") == list(ARMS) and
          report.get("source_ticks") == 4 and
          report.get("fork_tick") == 5 and
          report.get("final_tick") == grid["final_tick"] and
          report.get("no_motor_override") is True and
          report.get("run_life_used") is False and
          report.get("historical_F1K") == "INCONCLUSIVE_NO_REAL_SURCHARGE" and
          len(report.get("rows", [])) == len(roots),
          "DEV receipt reclassified, reserved L roots appeared, or status forged")
    seen_rounds = seen_steps = drinks = meals = 0
    all_paid_sources = all_shams = all_equal = 0
    entries = []
    for root, row in zip(roots, report["rows"]):
        check(row["origin"] == root and
              row["source"]["origin"] == root,
              "forged or reordered independent DEV root")
        src = row["source"]
        world = origin_world(grid, root)
        K.world_eq(src["genesis"]["world"], world, "empty birth world")
        mind = src["genesis"]["mind"]
        private = K.private(mind, "F1JFixedRoundMind")
        check(K.effects(mind) == {} and
              private["buffer"] == {"__deque__": [], "maxlen": None} and
              all(all(v == 0 for v in x) for x in private["values"]),
              "synthetic initial personal memories, TD or episodic buffer")
        t1 = None
        for i, step in enumerate(src["source_steps"], 1):
            check(i <= 4 and step["t"] == i,
                  "personal source tick duplicated/omitted")
            world, mind, rounds = verify_step(
                step, world, mind, arm="full", horizon=4)
            seen_steps += 1
            seen_rounds += rounds
            if i == 1:
                t1 = K.effects(step["after_paid_learning_mind"])
        K.world_eq(src["source_tick4_world"], world, "retained source world")
        check(src["source_tick4_mind"] == mind, "source memory was discarded")
        owned = ([{"key": list(k), "stat": deepcopy(v)}
                  for k, v in sorted(t1.items(), key=lambda x: repr(x[0]))]
                 if t1 is not None else [])
        check(src["paid_t1_mean_anchor"] == owned,
              "T1 personal means or statistics were invented by producer")
        source_valid = (len(src["source_steps"]) == 4 and
                        world["t"] == 4 and not world["dead"] and
                        src["source_error"] is None and
                        bool(t1) and all(
                            s["postaction"]["status"] == "PAID_LEARNED"
                            for s in src["source_steps"]))
        check(src["valid_paid_personal_source"] is source_valid and
              src["run_life_used"] is False and
              src["source_receipt_sha256"] == I.h({
                  k: v for k, v in src.items()
                  if k != "source_receipt_sha256"}),
              "unpaid source or falsified first-person history")
        all_paid_sources += int(source_valid)
        if source_valid:
            arms = row["arms"]
            check(set(arms) == set(ARMS),
                  "one original experimental arm was excluded")
            for arm in ARMS:
                entry = arms[arm]
                check(entry["policy"] == arm and entry["steps"],
                      "one native continuation was omitted")
                current, memory = deepcopy(world), deepcopy(mind)
                for step in entry["steps"]:
                    current, memory, rounds = verify_step(
                        step, current, memory, arm=arm, t1=t1,
                        horizon=grid["final_tick"])
                    seen_steps += 1
                    seen_rounds += rounds
                    drinks += int(step["action"] == "boire")
                    meals += int(step["action"] == "manger")
                K.world_eq(entry["last_world"], current,
                           "terminal world & resources")
                check(entry["last_mind"] == memory and
                      (current["t"] == grid["final_tick"] or
                       current["dead"] or
                       entry["metrics"]["native_error"] is not None),
                      "invented unobserved terminal states")
                check(metrics(entry["steps"], current,
                              entry["metrics"]["native_error"],
                              grid["final_tick"]) == entry["metrics"],
                      "bodily persistence or learning costs miscounted")
                check(entry["trajectory_sha256"] == I.h({
                    k: v for k, v in entry.items()
                    if k != "trajectory_sha256"}),
                    "original native trajectory hash altered")
            cold = comparable(*(arms[k] for k in ARMS), True)
            all_shams += int(cold["sham_neutral"])
            all_equal += int(cold["equal_t5_decision_cost"])
        else:
            check(row["arms"] == {},
                  "unfunded origins were replaced with selected arms")
            cold = comparable(None, None, None, False)
        check(row["comparison"] == cold and
              row["case_sha256"] == I.h({
                  k: v for k, v in row.items() if k != "case_sha256"}),
              "re-signed original outcome or cost comparison tampered")
        entries.append({"root": root["id"], "ecology": root["ecology"],
                        **cold})
    chain = I.h({
        "phase": "DEV_ONLY",
        "grid_blob_sha": GRID_BLOB,
        "protocol_blob_sha": PROTOCOL_BLOB,
        "cases": [r["case_sha256"] for r in report["rows"]],
    })
    check(report["provenance_sha256"] == chain,
          "native receipts provenance chain broken")
    return {
        "schema": "i3-stage8f1l-cold-stdlib-no-engine-dev/v0",
        "phase": "DEV_ONLY",
        "cold_status": "DEV_ONLY_NOT_SCIENTIFIC",
        "original_sha256": I.h(report),
        "preregistered_blobs_and_controller_verified": True,
        "roots": len(roots),
        "personal_paid_sources_verified": all_paid_sources,
        "whole_trajectory_shams_verified": all_shams,
        "T5_equal_real_decision_cost_pairs": all_equal,
        "native_world_steps_verified": seen_steps,
        "substantive_competition_rounds_verified": seen_rounds,
        "real_drinks_verified": drinks,
        "real_meals_verified": meals,
        "per_root": entries,
        "scientific_F1L_holdout_exposures": 0,
        "historical_F1K": "INCONCLUSIVE_NO_REAL_SURCHARGE",
        "provenance_sha256": chain,
    }


def main():
    p = argparse.ArgumentParser(description="F1L read-only engine-free cold audit")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    raw = Path(args.input).read_bytes()
    if args.input.endswith(".gz"):
        raw = gzip.decompress(raw)
    report = json.loads(raw)
    result = audit(report)
    with Path(args.output).open("xb") as f:
        f.write(json.dumps(result, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":")).encode("utf-8"))
    print(json.dumps({
        "cold_status": result["cold_status"],
        "roots": result["roots"],
        "personal_paid_sources_verified": result["personal_paid_sources_verified"],
        "T5_equal_real_decision_cost_pairs": result["T5_equal_real_decision_cost_pairs"],
        "native_world_steps_verified": result["native_world_steps_verified"],
        "substantive_competition_rounds_verified":
            result["substantive_competition_rounds_verified"],
        "scientific_F1L_holdout_exposures": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
