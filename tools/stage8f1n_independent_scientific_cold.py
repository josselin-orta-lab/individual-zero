"""F1N heldout one-shot independent Python3.12 cold audit. No engine imports.

Reconstruct original native physical work, paid T5 own-margin memory write,
T6 paid read and fixed-round thresholds, authentic personal learning, 48 sham
controls and T60 bodily outcomes exclusively from the original 336 gzips.
The registered M, A and B verdicts remain SEPARATE from the producer.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1n_independent_dev_cold as DEV
from tools import stage8f1n_prereg_static_guard as FROZEN

ROOT_IDS = tuple(FROZEN.ROOT_IDS)
PARTS = tuple(FROZEN.PARTS)
SCHEMA = "i3-stage8f1n-independent-scientific-cold-T60/v0"


def check(condition, message):
    if not condition:
        raise AssertionError("F1N SCIENCE COLD: " + message)


def science_grid():
    FROZEN.check_files()
    grid = json.loads(FROZEN.GRID.read_bytes())
    FROZEN.verify_grid(grid)
    return grid


def origin_world(grid, origin):
    """Derive exact original WorldSpec from frozen grid, without World class."""
    check(origin in grid["origins"] and origin["id"] in ROOT_IDS,
          "unregistered F1N original origin")
    world = K.origin_world(grid, origin)
    world["world_spec"]["name"] = (
        "F1N_HELDOUT_ORIGIN_" + origin["id"] + "_" + origin["ecology"])
    return world


def verify_followup(rec, origin_world, origin_mind, mode):
    check(rec["policy"] == "F1N_HELDOUT_" + mode,
          "DEV_N or substituted scientific continuation")
    world, mind = deepcopy(origin_world), deepcopy(origin_mind)
    rounds = 0
    for tick, step in enumerate(rec["steps"], 6):
        check(tick <= 60 and step["t"] == tick,
              "noncontiguous or extra T60 source")
        world, mind, used = DEV.verify_step(
            step, world, mind, tick, mode if tick == 6 else "off")
        rounds += used
    check(rec["last_mind"] == mind, "invented terminal personal state")
    K.world_eq(rec["last_world"], world, "original real T60 World")
    check(rec["metrics"] == K.metrics(
        rec["steps"], world, rec["metrics"]["native_error"], 60),
        "forged real T60 body/ticks/billing")
    check(world["dead"] or world["t"] == 60 or
          rec["metrics"]["native_error"] is not None,
          "early stop without death or registered native error")
    check(rec["trajectory_sha256"] == I.h({
        k:v for k,v in rec.items() if k != "trajectory_sha256"}),
        "mutated original trajectory digest")
    return world, mind, rounds


def _t6_compare(a, b):
    left, right = a["followup"], b["followup"]
    if not left["steps"] or not right["steps"]:
        return {"error": "MISSING_NATIVE_T6"}
    x, y = left["steps"][0], right["steps"][0]
    equal = (x["before_world"] == y["before_world"] and
             x["capture"] == y["capture"] and
             x["cognitive_work"] == y["cognitive_work"] and
             x["requested_native_cost"] == y["requested_native_cost"] and
             x["decision_remaining"] == y["decision_remaining"] and
             x["native_motor"]["cognitive_accounting"] ==
                 y["native_motor"]["cognitive_accounting"] and
             x["cognitive_work"]["memory_items"] > 0 and
             all(record["paid"] == record["requested"] and
                 record["unpaid"] == 0.0 for step in (x,y)
                 for record in step["native_motor"]["cognitive_accounting"].values()))
    w1 = x["decision_info"]["observer"]["competition_witness"]
    w2 = y["decision_info"]["observer"]["competition_witness"]
    return {"equal_t6_real_decision_cost": equal,
            "t6_margin_witness": w1["f1n_margin_read"],
            "t6_masked_witness": w2["f1n_margin_read"],
            "thresholds_changed": w1["thresholds"] != w2["thresholds"],
            "winner_changed": w1["winner_before_control"] != w2["winner_before_control"],
            "motor_changed": (x["action"],x["param"]) != (y["action"],y["param"]),
            "margin_motor": [x["action"],x["param"]],
            "masked_motor": [y["action"],y["param"]],
            "margin_first_work": x["cognitive_work"],
            "masked_first_work": y["cognitive_work"],
            "delta_lived_ticks": len(left["steps"]) - len(right["steps"]),
            "delta_body": [u-v for u,v in zip(
                left["metrics"]["terminal_body"],
                right["metrics"]["terminal_body"])]}


def cold_root(grid, meta, parts):
    """One original root at a time, memory bounded to seven gzip payloads."""
    origin = meta["origin"]
    check(origin in grid["origins"] and set(parts) == set(PARTS),
          "unexpected N source or missing original part")
    root = origin["id"]
    world = origin_world(grid, origin)
    src = parts["source_t1_t4"]
    K.world_eq(src["genesis"]["world"], world, "genuine initial F1N birth")
    mind = src["genesis"]["mind"]
    fields = DEV.fields(mind)
    check(fields["f1n_owned_margin"] is None and
          fields["f1n_pending_margin"] is None and
          fields["f1n_mode"] == "off" and
          fields["f1n_read_used"] is False and
          K.effects(DEV._normalize(mind)) == {} and
          fields["buffer"] == {"__deque__":[], "maxlen":None} and
          all(all(q == 0 for q in row) for row in fields["values"]),
          "unfunded prenatal memory or fictitious private state")
    count_steps = count_rounds = 0
    check(len(src["steps"]) <= 4, "extra source steps after T4")
    for tick, step in enumerate(src["steps"],1):
        world, mind, rounds = DEV.verify_step(step,world,mind,tick)
        count_steps += 1
        count_rounds += rounds
    valid = (len(src["steps"]) == 4 and src["error"] is None and
             src["valid"] is True and world["t"] == 4 and not world["dead"] and
             all(s["postaction"]["status"] == "PAID_LEARNED" for s in src["steps"]))
    check(src["world_t4"] == world and src["mind_t4"] == mind and
          src["valid"] is valid and meta["source_valid"] is valid,
          "invalid or forged T1..T4 source integrity")
    row = {"root":root, "ecology":origin["ecology"], "seed":origin["seed"],
           "source_valid":valid,"shams_neutral":False,
           "all_native_continuations":False,"t6_equal_paid":False,
           "motor_changed":False,"delta_lived_ticks":None,
           "both_alive_at_T60":False,"body_delta":None,
           "pareto":"NOT_COMPARABLE_HORIZON", "q":None,
           "reused_scored_key":None}
    if not valid:
        for kind in PARTS[1:]:
            marker = parts[kind]
            check(marker.get("status") == "NOT_EXECUTED_UNFUNDED_OR_INCOMPLETE_SOURCE" and
                  marker.get("native_world_steps_created") == 0,
                  "fabricated World.step after unfunded or incomplete source")
        check(meta["comparison"] == {"error":"UNFUNDED_OR_INCOMPLETE_SOURCE"} and
              meta["shams_neutral"] is False,
              "invalid source was selectively excluded")
        return row, count_steps, count_rounds

    t5 = {}
    for kind, sham in (("self_paid_t5",False),("self_paid_t5_sham",True)):
        doc = parts[kind]
        step = doc["step"]
        w,m,rounds = DEV.verify_step(step,world,mind,5,sham=sham)
        count_steps += 1; count_rounds += rounds
        w,m = DEV.verified_paid_t5_write(doc["write"],step)
        check(doc["t5_world"] == w and doc["t5_mind"] == m,
              "self-owned paid T5 margin not retained")
        t5[kind] = doc
    original, sham5 = t5["self_paid_t5"],t5["self_paid_t5_sham"]
    neutral5 = (original["write"] == sham5["write"] and
                original["t5_world"] == sham5["t5_world"] and
                original["t5_mind"] == sham5["t5_mind"] and
                {k:v for k,v in original["step"].items()
                 if k not in ("readout_mode","receipt_sha256")} ==
                {k:v for k,v in sham5["step"].items()
                 if k not in ("readout_mode","receipt_sha256")})
    base_world, base_mind = original["t5_world"],original["t5_mind"]
    arms={}
    shams=[]
    for mode in ("margin","masked"):
        received = parts[mode + "_t6_t60"]
        control = parts[mode + "_t6_t60_sham"]
        after = DEV.verify_fork(received["fork"],base_mind,mode)
        after_sham = DEV.verify_fork(control["fork"],base_mind,mode)
        check(after == after_sham,"fork sham changed private values")
        final_state, final_mind, used = verify_followup(
            received["followup"],base_world,after,mode)
        count_steps += len(received["followup"]["steps"])
        count_rounds += used
        sham_state, sham_mind, sham_used = verify_followup(
            control["followup"],base_world,after_sham,mode)
        count_steps += len(control["followup"]["steps"])
        count_rounds += sham_used
        shams.append(received == control and
                     final_state == sham_state and final_mind == sham_mind)
        arms[mode] = received
    compared = _t6_compare(arms["margin"],arms["masked"])
    check(compared == meta["comparison"],
          "producer altered comparator after native motor decision")
    neutral = neutral5 and all(shams)
    check(meta["shams_neutral"] is neutral,
          "source sham labels not linked to original native traces")
    row.update({"shams_neutral":neutral,
                "all_native_continuations":all(
                    len(arms[m]["followup"]["steps"]) > 0 and
                    arms[m]["followup"]["metrics"]["native_error"] is None
                    for m in arms),
                "t6_equal_paid":compared.get("equal_t6_real_decision_cost") is True,
                "motor_changed":compared.get("motor_changed") is True,
                "delta_lived_ticks": compared.get("delta_lived_ticks"),
                "body_delta":compared.get("delta_body"),
                "both_alive_at_T60":all(
                    arms[m]["followup"]["metrics"]["alive_at_horizon"] is True
                    for m in arms),
                "q":DEV.map_val(DEV.fields(base_mind)["f1n_owned_margin"])["q"],
                "reused_scored_key":compared["t6_margin_witness"]["own_key_scored"]})
    if (row["both_alive_at_T60"] and row["delta_lived_ticks"] == 0 and
            row["body_delta"] is not None):
        v = row["body_delta"]
        if all(x >= -1e-10 for x in v) and any(x > 1e-10 for x in v):
            row["pareto"] = "MARGIN_FIVE_CHANNEL_DOMINANCE"
        elif all(x <= 1e-10 for x in v) and any(x < -1e-10 for x in v):
            row["pareto"] = "MASKED_FIVE_CHANNEL_DOMINANCE"
        else:
            row["pareto"] = "FIVE_CHANNELS_EQUAL_OR_TRADEOFF"
    return row, count_steps, count_rounds


def classify(rows):
    """Frozen F1N rules: 8 roots / 3 ecologies M and A; 12 roots B."""
    ids = list(ROOT_IDS)
    if len(rows) != 48 or [r.get("root") for r in rows] != ids:
        return {"status":"INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "reason":"not exactly 48 original independently audited N roots"}
    if any(not r["source_valid"] or not r["shams_neutral"] for r in rows):
        return {"status":"INCONCLUSIVE_PAID_SOURCE_OR_SHAM",
                "reason":"self-acquired source/memory work or native sham invalid"}
    if any(not r["all_native_continuations"] for r in rows):
        return {"status":"INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "reason":"T6..T60 original branch incomplete or failed"}
    if any(not r["t6_equal_paid"] for r in rows):
        return {"status":"INCONCLUSIVE_REAL_DECISION_COST",
                "reason":"one or more 48 T6 cognitive prices unequal"}
    motor = [r for r in rows if r["motor_changed"]]
    gains = [r for r in rows if r["delta_lived_ticks"] > 0]
    losses = [r for r in rows if r["delta_lived_ticks"] < 0]
    survivor_equal = not gains and not losses
    positive_body = [r for r in rows if r["pareto"] ==
                     "MARGIN_FIVE_CHANNEL_DOMINANCE"]
    inverse_body = [r for r in rows if r["pareto"] ==
                    "MASKED_FIVE_CHANNEL_DOMINANCE"]
    all_body_comparable = all(r["both_alive_at_T60"] for r in rows)
    m_ok = len(motor) >= 8 and len({r["ecology"] for r in motor}) >= 3
    a_ok = len(gains) >= 8 and len({r["ecology"] for r in gains}) >= 3 and not losses
    b_ok = (survivor_equal and all_body_comparable and
            len(positive_body) >= 12 and
            len({r["ecology"] for r in positive_body}) >= 3 and
            not inverse_body)
    b = ("BODY_ONLY_NOT_SURVIVAL_ADAPTATION" if b_ok else
         "NOT_APPLICABLE_SURVIVAL_DIFFERS" if not survivor_equal else
         "NOT_APPLICABLE_NOT_ALL_ALIVE_T60" if not all_body_comparable else
         "NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_BODY_PARETO_SUPPORT")
    return {"status":"F1N_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS",
            "motor_verdict":("REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT"
               if m_ok else "NO_REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT"),
            "survival_verdict":("LOCAL_T60_OWN_MARGIN_SURVIVAL_ADAPTIVE_ADVANTAGE"
               if a_ok else "NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_SURVIVAL_ADVANTAGE"),
            "body_verdict":b,
            "independent_roots":48,
            "paired_comparisons":48,
            "ecologies_covered":len({r["ecology"] for r in rows}),
            "motor_changed_roots":len(motor),
            "motor_changed_ecologies":len({r["ecology"] for r in motor}),
            "survival_positive_roots":len(gains),
            "survival_positive_ecologies":len({r["ecology"] for r in gains}),
            "survival_negative_roots":len(losses),
            "body_pareto_margin_roots":len(positive_body),
            "body_pareto_masked_roots":len(inverse_body),
            "all_shams_and_paid_costs_valid":True,
            "stage2_promotion":False}