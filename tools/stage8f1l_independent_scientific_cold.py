"""F1L heldout cold audit: stdlib Python 3.12, no World, Mind or native producer.

An independent reconstruction of the complete 32-root T60 histories. Reuses
the already adversarially-tested F1L DEV cold *physics/paid-cost primitives*,
NOT its DEV-only population verifier, and never imports scientific native code.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha1
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1l_independent_paid_content_cold_audit as L
from tools import stage8f1l_one_shot_reservation as R

SCHEMA = "i3-stage8f1l-scientific-first-original-personal-content-T60/v0"
PHASE = "F1L_HELDOUT_RELEASE"


def check(ok, what):
    K.check(ok, "F1L SCIENCE COLD: " + what)


def frozen_grid():
    """Read the frozen public manifest as DATA, without instantiating a seed."""
    L.source_gate()
    grid = json.loads(Path(R.GRID_PATH).read_bytes())
    check([r["id"] for r in grid["origins"]] == R.ROOT_IDS
          and [r["seed"] for r in grid["origins"]] == R.SEEDS
          and len(grid["ecologies"]) == 8
          and grid["arms"] == R.ARMS
          and grid["final_tick"] == 60
          and grid["source_genome"] == "midpoint()"
          and grid["source_policy"].endswith(".F1JFixedRoundMind"),
          "unfrozen experiment or population")
    return grid


def start_world(grid, origin):
    world = K.origin_world(grid, origin)
    world["world_spec"]["name"] = (
        "F1L_HELDOUT_ORIGIN_" + origin["id"] + "_" + origin["ecology"])
    return world


def _incomplete_comparison(arms):
    """Match recorded invalid continuation; never invent an unexecuted step."""
    full, sham, stale = (arms[x] for x in R.ARMS)
    stripped = lambda step: {
        k: v for k, v in step.items()
        if k not in ("readout_mode", "receipt_sha256")}
    neutral = (full["metrics"] == sham["metrics"]
               and full["last_world"] == sham["last_world"]
               and full["last_mind"] == sham["last_mind"]
               and len(full["steps"]) == len(sham["steps"])
               and all(stripped(a) == stripped(b)
                       for a, b in zip(full["steps"], sham["steps"])))
    return {
        "source_valid": True, "sham_neutral": neutral,
        "equal_t5_decision_cost": False, "motor_changed": None,
        "delta_lived_ticks": None, "pareto": None,
        "arm_valid": False,
    }


def _classify(per_root):
    """Strict pre-registered five gates, then ITT and five-body Pareto only."""
    if any(not x["source_valid"] or not x["arm_valid"] for x in per_root):
        return "INCONCLUSIVE_UNFUNDED_PERSONAL_SOURCE"
    if any(not x["sham_neutral"] for x in per_root):
        return "INVALID_FULL_SHAM"
    if any(not x["equal_t5_decision_cost"] for x in per_root):
        return "INCONCLUSIVE_CONTENT_DECISION_COST_GATE"
    check(len(per_root) == 32, "intent-to-treat denominator altered")
    gains = [x for x in per_root if x["delta_lived_ticks"] > 0]
    losses = [x for x in per_root if x["delta_lived_ticks"] < 0]
    if (len(gains) >= 6 and len({x["ecology"] for x in gains}) >= 3
            and not losses):
        return "LOCAL_T60_RECENT_PERSONAL_CONTENT_SURVIVAL_GAIN_EQUAL_DECISION_COST"
    if all(x["delta_lived_ticks"] == 0 for x in per_root):
        positives = [x for x in per_root
                     if x["pareto"] == "FULL_FIVE_CHANNEL_DOMINANCE"]
        reverse = [x for x in per_root
                   if x["pareto"] == "STALE_FIVE_CHANNEL_DOMINANCE"]
        if (len(positives) >= 8
                and len({x["ecology"] for x in positives}) >= 3
                and not reverse):
            return "LOCAL_T60_RECENT_CONTENT_PARETO_GAIN_NO_SURVIVAL_GAIN"
    return "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE"


def audit(report):
    grid = frozen_grid()
    roots = grid["origins"]
    check(report.get("schema") == SCHEMA
          and report.get("phase") == PHASE
          and report.get("producer_only_status") ==
          "F1L_ORIGINAL_UNAUDITED_NO_CLAIM"
          and report.get("scientific_verdict") is None
          and report.get("origin_count") == 32
          and report.get("origin_ids") == R.ROOT_IDS
          and report.get("worlds") == [e["id"] for e in grid["ecologies"]]
          and report.get("preregistered_main") == R.PREEXPOSURE
          and report.get("grid_blob_sha") == R.GRID_BLOB
          and report.get("protocol_blob_sha") == R.PROTOCOL_BLOB
          and report.get("source_policy") == "F1JFixedRoundMind"
          and report.get("arms") == R.ARMS
          and report.get("source_ticks") == 4
          and report.get("fork_tick") == 5
          and report.get("final_tick") == 60
          and report.get("no_motor_override") is True
          and report.get("run_life_used") is False
          and report.get("historical_F1K") ==
          "INCONCLUSIVE_NO_REAL_SURCHARGE"
          and len(report.get("rows", [])) == 32,
          "unregistered source, missing first originals or forged result")

    seen_steps = seen_rounds = drinks = meals = 0
    source_count = sham_count = cost_count = 0
    per_root = []
    for root, row in zip(roots, report["rows"]):
        check(row["origin"] == root and row["source"]["origin"] == root,
              "duplicated, replaced or out-of-order individual")
        src = row["source"]
        world = start_world(grid, root)
        K.world_eq(src["genesis"]["world"], world, "original source genesis")
        mind = src["genesis"]["mind"]
        private = K.private(mind, "F1JFixedRoundMind")
        check(K.effects(mind) == {}
              and private["buffer"] == {"__deque__": [], "maxlen": None}
              and all(all(v == 0 for v in x) for x in private["values"]),
              "innate personal memory/TD/buffer inserted")
        t1 = None
        check(len(src["source_steps"]) <= 4,
              "personal source contains extra paid ticks")
        for tick, step in enumerate(src["source_steps"], 1):
            check(step["t"] == tick, "personal source time jumps")
            world, mind, rounds = L.verify_step(
                step, world, mind, arm="full", horizon=4)
            seen_steps += 1
            seen_rounds += rounds
            if tick == 1:
                t1 = K.effects(step["after_paid_learning_mind"])
        K.world_eq(src["source_tick4_world"], world, "source body/stock")
        check(src["source_tick4_mind"] == mind,
              "source acquired memory not retained")
        owned = ([{"key": list(k), "stat": deepcopy(v)}
                  for k, v in sorted(t1.items(), key=lambda x: repr(x[0]))]
                 if t1 is not None else [])
        check(src["paid_t1_mean_anchor"] == owned,
              "invented/cross-individual T1 mean")
        valid = (len(src["source_steps"]) == 4 and world["t"] == 4
                 and not world["dead"] and src["source_error"] is None
                 and bool(t1)
                 and all(s["postaction"]["status"] == "PAID_LEARNED"
                         for s in src["source_steps"]))
        check(src["valid_paid_personal_source"] is valid
              and src["run_life_used"] is False
              and src["source_receipt_sha256"] == I.h({
                  k: v for k, v in src.items()
                  if k != "source_receipt_sha256"}),
              "invalid source was hidden or source receipt changed")
        source_count += int(valid)
        if valid:
            arms = row["arms"]
            check(set(arms) == set(R.ARMS),
                  "missing allocated motor arm on a paid source")
            for arm in R.ARMS:
                entry = arms[arm]
                check(entry["policy"] == arm, "arm label switched")
                current, memory = deepcopy(world), deepcopy(mind)
                for step in entry["steps"]:
                    current, memory, rounds = L.verify_step(
                        step, current, memory, arm=arm, t1=t1, horizon=60)
                    seen_steps += 1
                    seen_rounds += rounds
                    drinks += int(step["action"] == "boire")
                    meals += int(step["action"] == "manger")
                K.world_eq(entry["last_world"], current,
                           "terminal world or natural resource stock")
                check(entry["last_mind"] == memory
                      and (current["t"] == 60 or current["dead"]
                           or entry["metrics"]["native_error"] is not None),
                      "invented continuation after end")
                check(L.metrics(entry["steps"], current,
                                entry["metrics"]["native_error"], 60) ==
                      entry["metrics"],
                      "wrong native T60 physiological/learning outcomes")
                check(entry["trajectory_sha256"] == I.h({
                    k: v for k, v in entry.items()
                    if k != "trajectory_sha256"}),
                    "arm receipt modified")
            if (all(a["steps"] for a in arms.values())
                    and all(a["metrics"]["native_error"] is None
                            for a in arms.values())):
                cold = L.comparable(*(arms[k] for k in R.ARMS), True)
            else:
                cold = _incomplete_comparison(arms)
            sham_count += int(cold["sham_neutral"])
            cost_count += int(cold["equal_t5_decision_cost"])
        else:
            check(row["arms"] == {},
                  "extra source arms created without paid experience")
            cold = L.comparable(None, None, None, False)
        check(row["comparison"] == cold
              and row["case_sha256"] == I.h({
                  k: v for k, v in row.items() if k != "case_sha256"}),
              "changed original or reclassified result")
        details = {
            "root": root["id"], "ecology": root["ecology"],
            **cold,
            "source_error": src["source_error"],
            "t5_action_full": (row["arms"]["full"]["steps"][0]["action"]
                               if valid and row["arms"]["full"]["steps"]
                               else None),
            "t5_action_stale": (row["arms"]["stale_owned_t1_means"]["steps"][0]["action"]
                                if valid and row["arms"]["stale_owned_t1_means"]["steps"]
                                else None),
            "paid_learning_full": (row["arms"]["full"]["metrics"]["paid_learning"]
                                   if valid else None),
            "paid_learning_stale": (row["arms"]["stale_owned_t1_means"]["metrics"]["paid_learning"]
                                    if valid else None),
            "terminal_full_body": (row["arms"]["full"]["metrics"]["terminal_body"]
                                   if valid else None),
            "terminal_stale_body": (row["arms"]["stale_owned_t1_means"]["metrics"]["terminal_body"]
                                    if valid else None),
        }
        per_root.append(details)
    chain = I.h({
        "phase": PHASE, "grid_blob_sha": R.GRID_BLOB,
        "protocol_blob_sha": R.PROTOCOL_BLOB,
        "cases": [r["case_sha256"] for r in report["rows"]],
    })
    check(report["provenance_sha256"] == chain, "original cases provenance broken")
    verdict = _classify(per_root)
    return {
        "schema": "i3-stage8f1l-independent-scientific-cold-stdlib/v0",
        "phase": PHASE, "cold_status": "COLD_VERIFIED_32_FIRST_ONLY",
        "cold_verdict": verdict,
        "original_sha256": I.h(report),
        "preregistered_blobs_and_controller_verified": True,
        "roots": 32,
        "personal_paid_sources_verified": source_count,
        "whole_trajectory_shams_verified": sham_count,
        "T5_equal_real_decision_cost_pairs": cost_count,
        "native_world_steps_verified": seen_steps,
        "substantive_competition_rounds_verified": seen_rounds,
        "real_drinks_verified": drinks, "real_meals_verified": meals,
        "survival_delta_vector_all_32": [
            p["delta_lived_ticks"] for p in per_root],
        "survival_gain_count": sum(p["delta_lived_ticks"] is not None
                                   and p["delta_lived_ticks"] > 0
                                   for p in per_root),
        "survival_loss_count": sum(p["delta_lived_ticks"] is not None
                                   and p["delta_lived_ticks"] < 0
                                   for p in per_root),
        "survival_equal_count": sum(p["delta_lived_ticks"] == 0
                                    for p in per_root),
        "per_root": per_root, "provenance_sha256": chain,
        "historical_F1K": "INCONCLUSIVE_NO_REAL_SURCHARGE",
        "stage2_not_promoted": True,
    }
