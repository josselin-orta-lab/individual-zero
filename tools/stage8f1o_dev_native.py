"""F1O DEV only: two paid, private one-step forecasts, never a motor input."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import gzip
from hashlib import sha256
import json
from math import fsum
import os
from pathlib import Path
import subprocess

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1h_prospective_native_body_value as H
from tools import stage8f1o_prereg_static_guard as F

PHASE = "F1O_DEV_ONLY_NO_SCIENTIFIC_BIRTH"
ORDERS = (("masked", "corrected"), ("corrected", "masked"))
FIELDS = ("cycles", "simulated_steps", "memory_items", "replays")


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def create_dev(cohort, origin):
    grid, _ = F.check_files()
    require(cohort in ("A", "B") and origin in grid["dev_allocations"][cohort]
            and origin["id"].startswith("DEV_O" + cohort)
            and origin["seed"] not in F.SEEDS, "reserved or unregistered origin")
    e = next(x for x in grid["ecologies"] if x["id"] == origin["ecology"])
    world = World(WorldSpec(
        name="F1O_DEV_" + origin["id"] + "_" + e["id"],
        width=3, height=3, spawn=(1, 1), body=tuple(origin["body"]),
        water={tuple(e["water_position"]): WaterSource(
            gain=e["water_gain"], stock=e["water_stock"],
            max_stock=e["water_max_stock"], restock_every=e["water_restock_every"])},
        food={tuple(e["food_position"]): FoodPatch(
            token=e["food_token"], quantity=e["food_quantity"],
            max_quantity=e["food_max_quantity"], restock_every=e["food_restock_every"])},
        token_effects={e["food_token"]: (e["food_gain"], e["integrity_delta"])},
        changes=(), laws=BodyLaws()))
    mind = F1JFixedRoundMind(midpoint(), origin["seed"])
    # A retains the native optional observer; B exercises the identical
    # controller with both observer diagnostics explicitly disabled.
    mind.observer_full_competition = cohort == "A"
    mind.observer_decision_diagnostics = cohort == "A"
    mind._f1o_errors = []
    require(world.t == 0 and not world.dead and not mind.effects.stats
            and not mind.buffer and mind.last is None
            and all(v == 0. for row in mind.values for v in row), "nonempty genesis")
    return world, mind


def paid_forecast(mind, mode, tick):
    """One substantive block, called only following authorization and debit.
    Reads only actual Mind.last, its native stats and its own error memory.
    No world, observer, RNG, future result or policy write is accessible here.
    """
    require(mode in ("masked", "corrected"), "unknown forecast")
    body, key, action, _ = mind.last
    key = ("se_deplacer",) if action == "se_deplacer" else tuple(key)
    require(key[0] == action, "foreign action key")
    keys = (key, (key[0], None), ("*",))
    consultations = []
    for k in keys:
        item = mind.effects.stats.get(k)
        consultations.append({"key": list(k), "stat": deepcopy(item)})
    mean = next((tuple(row["stat"][1]) for row in consultations
                 if row["stat"] is not None and row["stat"][0] > 0.), (0.,)*5)
    inspected = []
    best = None
    rank = None
    for rec in mind._f1o_errors:
        require(rec["t"] < tick, "future personal error")
        distance = fsum(abs(a-b) for a,b in zip(body, rec["body"]))
        same = tuple(rec["key"]) == key
        inspected.append({"t": rec["t"], "same_key": same, "distance": distance})
        if same and (rank is None or (distance, -rec["t"]) < rank):
            rank = (distance, -rec["t"])
            best = rec
    residual = tuple(best["error"]) if best is not None else (0.,)*5
    applied = residual if mode == "corrected" else (0.,)*5
    prediction = [min(100., max(0., b+m+0.5*e))
                  for b,m,e in zip(body, mean, applied)]
    return {"key": list(key), "body": list(body), "consultations": consultations,
            "inspections": inspected, "mean": list(mean),
            "selected_tick": best["t"] if best is not None else None,
            "selected_error": list(residual), "applied_error": list(applied),
            "prediction": prediction}


def pay(world, blocks):
    start = D._snapshot_world(world)
    grant = CognitiveBudget(world.body, world.laws)
    authorizations = []
    for block in blocks:
        grant.spend(block)
        authorizations.append({"block": asdict(block), "cumulative": asdict(grant.work),
                               "remaining": list(grant.remaining)})
    bill = world.pay_cognition(grant.work)
    C.paid_bill(world.laws, grant.work, bill)
    end = D._snapshot_world(world)
    require(start["t"] == end["t"] and list(world.body) == list(grant.remaining),
            "cognition moved time or wrong body")
    return {"before": start, "authorizations": authorizations, "work": asdict(grant.work),
            "bill": deepcopy(bill), "after": end}


def native_tick(world, mind, order, row):
    t = world.t+1
    require(not world.dead and 1 <= t <= 24 and order in ORDERS, "bad tick/order")
    row["t"] = t
    row["before_mind"] = C.seal_mind(mind)
    n = len(mind._f1o_errors)
    require(n == min(t-1, 8), "incorrect private memory history")
    block = CognitiveWork(cycles=1, simulated_steps=1, memory_items=3+n)
    row["prepayment"] = pay(world, (block, block))
    row["before_world"] = D._snapshot_world(world)
    cap = world.capture()
    row["capture"] = json.loads(C.canonical(cap))
    row["capture_sha256"] = C.digest(cap)
    grant = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(cap, grant)
    row.update(action=action, param=param, decision_info=json.loads(C.canonical(info)),
               cognitive_work=asdict(work), decision_remaining=list(grant.remaining),
               requested_native_cost=dict(zip(("energy", "vigilance"),
                                              cognitive_cost(world.laws, work))),
               after_restoration_before_motor=C.seal_mind(mind))
    require(world.t == t-1 and work == grant.work and action is not None
            and info["funding"] == "FUNDED" and mind.last is not None,
            "missing native funded admitted action")
    body, _, a, p = mind.last
    require(tuple(body) == tuple(world.body) and (a,p) == (action,param),
            "not the native admitted choice")
    row["forecasts"] = {}
    for mode in order:
        row["forecasts"][mode] = paid_forecast(mind, mode, t)
    row["forecast_seal"] = C.digest(row["forecasts"])
    row["mind_after_forecasts"] = C.seal_mind(mind)
    require(row["mind_after_forecasts"] == row["after_restoration_before_motor"],
            "forecast altered private policy or RNG")
    # No forecast output is passed to the native controller or physical motor.
    raw = world.step(action, param, work)
    row["native_motor"] = {"t": raw["t"], "body": list(raw["body"]),
                           "dead": list(raw["dead"]), "moved": raw["moved"],
                           "cognitive_accounting": deepcopy(raw["cognitive_accounting"])}
    C.paid_bill(world.laws, work, raw["cognitive_accounting"])
    row["after_motor_world"] = D._snapshot_world(world)
    require(world.t == t and not world.dead, "incomplete/dead native life")
    row["postaction"] = H._pay_new_learning(world, mind, raw)
    row["after_paid_learning_mind"] = C.seal_mind(mind)
    row["after_paid_learning_world"] = D._snapshot_world(world)
    require(row["postaction"]["status"] == "PAID_LEARNED", "learning not actually paid")
    y = list(world.body)
    row["target"] = y
    row["write"] = None
    if t <= 8:
        row["write"] = pay(world, (CognitiveWork(cycles=1, memory_items=1),))
        masked = row["forecasts"]["masked"]
        # Own observed error only, created after the separately paid write.
        mind._f1o_errors.append({"t": t, "key": masked["key"][:], "body": list(body),
                                "error": [a-b for a,b in zip(y, masked["prediction"])]})
    row["end_world"] = D._snapshot_world(world)
    row["end_mind"] = C.seal_mind(mind)
    require(world.t == t, "memory write advanced time")


def life(cohort, origin, order):
    world, mind = create_dev(cohort, origin)
    result = {"phase": PHASE, "origin": origin, "cohort": cohort,
              "order": list(order), "genesis": {"world": D._snapshot_world(world),
                                                "mind": C.seal_mind(mind)},
              "steps": [], "failure": None}
    for t in range(1,25):
        row = {"t": t}
        result["steps"].append(row)
        try:
            native_tick(world, mind, order, row)
        except Exception as exc:
            result["failure"] = {"tick": t, "type": type(exc).__name__, "message": str(exc),
                                 "world": D._snapshot_world(world), "mind": C.seal_mind(mind)}
            break
    return result


def write_once(path, data):
    with path.open("xb") as fp:
        fp.write(data)
        fp.flush()
        os.fsync(fp.fileno())


def produce(cohort, directory):
    grid, _ = F.check_files()
    require(cohort in ("A", "B"), "only DEV cohorts")
    tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
    base = Path(directory)
    base.mkdir(parents=True, exist_ok=False)
    entries = []
    failures = 0
    for origin in grid["dev_allocations"][cohort]:
        for order in ORDERS:
            obj = life(cohort, origin, order)
            raw = C.canonical(obj)
            zipped = gzip.compress(raw, compresslevel=6, mtime=0)
            name = origin["id"] + "-" + order[0] + ".json.gz"
            write_once(base/name, zipped)
            entries.append({"path": name, "root": origin["id"], "order": list(order),
                            "raw_sha256": sha256(raw).hexdigest(),
                            "gzip_sha256": sha256(zipped).hexdigest(),
                            "raw_bytes": len(raw), "gzip_bytes": len(zipped)})
            failures += obj["failure"] is not None
            # Append-only checkpoints retain all originals already committed.
            write_once(base/f"checkpoint-{len(entries):02d}.json",
                       C.canonical({"source_tree": tree, "entries": entries}))
    index = {"phase": PHASE, "cohort": cohort, "source_tree": tree,
             "entries": entries, "failures": failures, "science_verdict": None,
             "frozen_grid": F.GRID_BLOB, "frozen_protocol": F.PROTOCOL_BLOB}
    write_once(base/"index.json", C.canonical(index))
    print(json.dumps({"cohort": cohort, "source_tree": tree, "originals": len(entries),
                      "native_failures": failures, "scientific_births": 0}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser(description=PHASE)
    ap.add_argument("--cohort", choices=("A","B"), required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    produce(args.cohort, args.output_dir)


if __name__ == "__main__":
    main()
