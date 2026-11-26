"""F1N scientific native producer: only AFTER remote verified one-shot claim.

No CLI to instantiate heldout N01..N48 directly. Only the protected GitHub
reservation entrypoint calls produce_release. F1N DEV factories explicitly
exclude these roots; this module instantiates exactly the frozen WorldSpecs.
All motors are voluntary Mind.decide and actually paid World.step actions.
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
from tools import stage8f1l_paid_content_body_value_dev as L
from tools import stage8f1n_dev_native_transport as DEV
from tools import stage8f1n_prereg_static_guard as FROZEN
from tools import stage8f1n_one_shot_reservation as R
from tools.stage8f1n_paid_margin_mind import F1NMarginMind

SCHEMA = "i3-stage8f1n-scientific-first-only-owned-margin-native-T60/v0"
PHASE = "F1N_HELDOUT_RELEASE"
_ADMISSION = object()


def science_grid():
    """Only the original literal prereg file, not a generated ecology."""
    FROZEN.check_files()
    grid = json.loads(Path(R.GRID_PATH).read_bytes())
    FROZEN.verify_grid(grid)
    if ([r["id"] for r in grid["origins"]] != R.ROOT_IDS or
        [r["seed"] for r in grid["origins"]] != R.SEEDS or
        len(grid["ecologies"]) != 8 or
        not all(sum(x["ecology"] == ec["id"] for x in grid["origins"]) == 6
                for ec in grid["ecologies"])):
        raise PermissionError("frozen F1N identities/ecologies differ")
    return grid


def _new_science_world(grid, origin, admission):
    if admission is not _ADMISSION:
        raise PermissionError("N scientific WorldSpec requires verified remote first-only claim")
    if (origin not in grid["origins"] or
        origin["id"] not in R.ROOT_IDS or
        origin["seed"] != R.SEEDS[R.ROOT_IDS.index(origin["id"])]):
        raise PermissionError("unregistered F1N origin or seed")
    e = next(x for x in grid["ecologies"] if x["id"] == origin["ecology"])
    w = grid["world"]
    return World(WorldSpec(
        name="F1N_HELDOUT_ORIGIN_" + origin["id"] + "_" + e["id"],
        width=w["width"], height=w["height"], spawn=tuple(w["spawn"]),
        body=tuple(origin["body"]),
        water={tuple(e["water"]): WaterSource(
            gain=e["water_gain"], stock=e["water_stock"],
            max_stock=e["water_max_stock"], restock_every=e["water_restock_every"])},
        food={tuple(e["food"]): FoodPatch(
            token=e["token"], quantity=e["food_quantity"],
            max_quantity=e["food_max_quantity"], restock_every=e["food_restock_every"])},
        token_effects={e["token"]: (e["food_gain"], e["integrity_delta"])},
        changes=(), laws=BodyLaws()))


def _followup(world, mind, mode):
    trace = L.followup(world, mind, "full", None, 60)
    trace["policy"] = "F1N_HELDOUT_" + mode
    trace["trajectory_sha256"] = C.digest({k:v for k,v in trace.items()
                                            if k != "trajectory_sha256"})
    return trace


def _first_native_lock(path, claim):
    data = {"schema": "i3-stage8f1n-first-native-start-lock/v0",
            "run_id": claim["workflow_run_id"],
            "head_sha": claim["head_sha"],
            "root_ids": R.ROOT_IDS,
            "one_scientific_attempt_only": True}
    with Path(path).open("xb") as fd:
        fd.write(C.canonical(data) + b"\n")
        fd.flush()
        os.fsync(fd.fileno())


def one_case(grid, origin, writer, admission):
    world = _new_science_world(grid, origin, admission)
    mind = F1NMarginMind(midpoint(), origin["seed"])
    src = DEV.source(world, mind)
    writer.part(origin["id"], "source_t1_t4", src)
    if not src["valid"]:
        # Remaining parts are explicit NOT_EXECUTED placeholders, never fake
        # World.step receipts; the independent cold returns INCONCLUSIVE.
        comparison = {"error": "UNFUNDED_OR_INCOMPLETE_SOURCE"}
        writer.finish_incomplete(origin, src, comparison)
        return {"origin": origin, "comparison": comparison, "source_valid": False,
                "shams_neutral": False}
    sw, sm = deepcopy(world), deepcopy(mind)
    w5, m5 = deepcopy(sw), deepcopy(sm)
    tick5 = DEV.t5(w5, m5, sham=False)
    writer.part(origin["id"], "self_paid_t5", tick5)
    ws, ms = deepcopy(sw), deepcopy(sm)
    sham5 = DEV.t5(ws, ms, sham=True)
    writer.part(origin["id"], "self_paid_t5_sham", sham5)
    neutral = (L.semantic_sham_step(tick5["step"]) ==
               L.semantic_sham_step(sham5["step"]) and
               tick5["write"] == sham5["write"] and
               tick5["t5_world"] == sham5["t5_world"] and
               tick5["t5_mind"] == sham5["t5_mind"])
    arms = {}
    for mode in R.ARMS:
        aw, am = deepcopy(w5), deepcopy(m5)
        f = DEV.fork(am, mode)
        original = {"fork": f, "followup": _followup(aw, am, mode)}
        writer.part(origin["id"], mode + "_t6_t60", original)
        arms[mode] = original
        cw, cm = deepcopy(w5), deepcopy(m5)
        shamfork = DEV.fork(cm, mode)
        sham = {"fork": shamfork, "followup": _followup(cw, cm, mode)}
        writer.part(origin["id"], mode + "_t6_t60_sham", sham)
        neutral = neutral and sham == original
    comparison = DEV.compare(arms)
    writer.finalize_case(origin, comparison, src["valid"], neutral)
    return {"origin": origin, "comparison": comparison, "source_valid": True,
            "shams_neutral": neutral}


def produce_release(reservation_file, writer):
    receipt = R.load_receipt(reservation_file)
    claim = R.verify_remote(receipt)
    grid = science_grid()
    if not all(callable(getattr(writer, name, None)) for name in
               ("part", "finalize_case", "finish_incomplete")):
        raise PermissionError("F1N scientific original writer missing")
    _first_native_lock(Path(reservation_file).with_suffix(".NATIVE_START_LOCK"), claim)
    rows=[]
    for origin in grid["origins"]:
        # Recheck the protected claim before EACH first scientific origin.
        R.verify_remote(R.load_receipt(reservation_file))
        row = one_case(grid, origin, writer, _ADMISSION)
        rows.append(row)
    return {"schema": SCHEMA, "phase": PHASE,
            "preregistration_main_sha": R.PREEXPOSURE_COMMIT,
            "frozen_grid_blob": R.GRID_BLOB,
            "frozen_protocol_blob": R.PROTOCOL_BLOB,
            "source_policy": "F1NMarginMind", "origin_ids": R.ROOT_IDS,
            "seeds": R.SEEDS, "arms": R.ARMS,
            "source_ticks": 4, "confidence_record_tick": 5,
            "paid_read_tick": 6, "final_tick": 60,
            "original_scientific_native_passes": 1,
            "no_motor_override": True,
            "scientific_verdict": None,
            "producer_only_status": "F1N_ORIGINAL_UNAUDITED",
            "rows": rows}