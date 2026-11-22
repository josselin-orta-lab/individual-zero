"""F1L scientific native producer: inaccessible until remote one-shot admission.

No heldout individual is born on import. No CLI development or scientific shortcut.
The DEV-only producer remains guarded against L seeds; shared paid-step machinery
is reused unchanged, but only this separate module can construct L-origin worlds.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

from i3.modules.body import BodyLaws
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D0
from tools import stage8f1l_paid_content_body_value_dev as D
from tools import stage8f1l_one_shot_reservation as R
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA = "i3-stage8f1l-scientific-first-original-personal-content-T60/v0"
PHASE = "F1L_HELDOUT_RELEASE"
ARMS = tuple(R.ARMS)
_ADMISSION = object()


def release_grid():
    grid = D.verify_readonly_prereg()
    if ([r["id"] for r in grid["origins"]] != R.ROOT_IDS
            or [r["seed"] for r in grid["origins"]] != R.SEEDS
            or grid["arms"] != R.ARMS
            or grid["final_tick"] != 60):
        raise PermissionError("scientific F1L frozen grid differs from prereg")
    return grid


def _new_world(grid, origin, admission):
    if admission is not _ADMISSION:
        raise PermissionError("L scientific World requires remote one-shot admission")
    if (origin not in grid["origins"]
            or origin["id"] not in R.ROOT_IDS
            or origin["seed"] != R.SEEDS[R.ROOT_IDS.index(origin["id"])]):
        raise PermissionError("unregistered F1L seed or WorldSpec")
    ecology = next(e for e in grid["ecologies"]
                   if e["id"] == origin["ecology"])
    spec = grid["world"]
    return World(WorldSpec(
        name="F1L_HELDOUT_ORIGIN_" + origin["id"] + "_" + ecology["id"],
        width=spec["width"], height=spec["height"],
        spawn=tuple(spec["spawn"]), body=tuple(origin["body"]),
        water={tuple(ecology["water"]): WaterSource(
            gain=ecology["water_gain"], stock=ecology["water_stock"],
            max_stock=ecology["water_max_stock"],
            restock_every=ecology["water_restock_every"])},
        food={tuple(ecology["food"]): FoodPatch(
            token=ecology["token"], quantity=ecology["food_quantity"],
            max_quantity=ecology["food_max_quantity"],
            restock_every=ecology["food_restock_every"])},
        token_effects={ecology["token"]:
                       (ecology["food_gain"], ecology["integrity_delta"])},
        changes=(), laws=BodyLaws(),
    ))


def _paid_source(grid, origin, admission):
    world = _new_world(grid, origin, admission)
    mind = F1JFixedRoundMind(midpoint(), origin["seed"])
    if (mind.effects.stats or mind.buffer or
            any(any(v != 0. for v in row) for row in mind.values)
            or world.t != 0 or world.dead):
        raise AssertionError("scientific birth is not innocent of artificial memory")
    genesis = {"world": D0._snapshot_world(world), "mind": C.seal_mind(mind)}
    steps, error, t1_stats = [], None, {}
    for tick in range(1, D.T_SOURCE + 1):
        if world.dead:
            break
        try:
            steps.append(D.paid_step(world, mind))
            if tick == 1:
                t1_stats = deepcopy(mind.effects.stats)
        except (ValueError, KeyError, RuntimeError, AssertionError) as exc:
            error = {"attempted_tick": tick, "type": type(exc).__name__,
                     "message": str(exc)}
            break
    valid = (error is None and len(steps) == D.T_SOURCE
             and world.t == D.T_SOURCE and not world.dead
             and bool(t1_stats)
             and all(s["postaction"]["status"] == "PAID_LEARNED"
                     for s in steps))
    record = {
        "origin": origin, "genesis": genesis, "source_steps": steps,
        "paid_t1_mean_anchor": [
            {"key": list(k), "stat": deepcopy(v)}
            for k, v in sorted(t1_stats.items(), key=lambda x: repr(x[0]))
        ],
        "source_tick4_world": D0._snapshot_world(world),
        "source_tick4_mind": C.seal_mind(mind),
        "valid_paid_personal_source": valid, "source_error": error,
        "run_life_used": False,
    }
    record["source_receipt_sha256"] = C.digest(record)
    return world, mind, t1_stats, record


def _first_native_start_lock(path, claim):
    """Exclusive O_EXCL lock, fsync before even the first source can exist."""
    native_claim = {
        "schema": "i3-stage8f1l-first-native-exposure-lock/v0",
        "reservation_run_id": claim["workflow_run_id"],
        "reserved_source_sha": claim["head_sha"],
        "origin_ids": R.ROOT_IDS,
        "no_native_second_attempt": True,
    }
    with path.open("xb") as fd:
        fd.write(C.canonical(native_claim) + b"\n")
        fd.flush()
        os.fsync(fd.fileno())


def produce_release(reservation_file, on_case):
    """Exactly one native cohort, in the original GitHub run, after remote claim."""
    reservation_file = Path(reservation_file)
    receipt = R.load_receipt(reservation_file)
    claim = R.verify_remote(receipt)
    grid = release_grid()
    if not callable(on_case):
        raise PermissionError("per-origin original gzip custody callback is mandatory")
    _first_native_start_lock(
        reservation_file.with_suffix(".NATIVE_START_LOCK"), claim)
    rows = []
    for origin in grid["origins"]:
        # Fail closed on an admin ref/ruleset change between original cases.
        R.verify_remote(receipt)
        world, mind, t1_stats, source_receipt = _paid_source(
            grid, origin, _ADMISSION)
        arms = {}
        if source_receipt["valid_paid_personal_source"]:
            arms = {
                mode: D.followup(
                    deepcopy(world), deepcopy(mind), mode,
                    t1_stats, grid["final_tick"])
                for mode in ARMS
            }
        comparison = D.compare(arms, source_receipt["valid_paid_personal_source"])
        case = {
            "origin": origin, "source": source_receipt,
            "arms": arms, "comparison": comparison,
        }
        case["case_sha256"] = C.digest(case)
        rows.append(case)
        on_case(case)
    report = {
        "schema": SCHEMA, "phase": PHASE,
        "preregistered_main": D.PREREG_MAIN,
        "grid_blob_sha": R.GRID_BLOB, "protocol_blob_sha": R.PROTOCOL_BLOB,
        "origin_count": len(rows), "origin_ids": R.ROOT_IDS,
        "worlds": [e["id"] for e in grid["ecologies"]],
        "source_policy": "F1JFixedRoundMind",
        "arms": list(ARMS), "source_ticks": 4,
        "fork_tick": 5, "final_tick": 60,
        "no_motor_override": True, "run_life_used": False,
        "scientific_verdict": None,
        "producer_only_status": "F1L_ORIGINAL_UNAUDITED_NO_CLAIM",
        "historical_F1K": "INCONCLUSIVE_NO_REAL_SURCHARGE",
        "rows": rows,
    }
    report["provenance_sha256"] = C.digest({
        "phase": PHASE,
        "grid_blob_sha": R.GRID_BLOB,
        "protocol_blob_sha": R.PROTOCOL_BLOB,
        "cases": [row["case_sha256"] for row in rows],
    })
    return report
