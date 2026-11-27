"""F1O DEV cold reader: stdlib and existing engine-free physics/learning auditors.
No native producer, Mind, World, BodyLaws, or i3 imports.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from math import fsum, isfinite
from pathlib import Path
import subprocess
import sys

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1j_independent_fixed_round_cold_audit as J
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1o_prereg_static_guard as F

PHASE = "F1O_DEV_ONLY_NO_SCIENTIFIC_BIRTH"
ORDERS = (("masked", "corrected"), ("corrected", "masked"))
FIELDS = ("cycles", "simulated_steps", "memory_items", "replays")


def check(ok, why):
    if not ok:
        raise ValueError("F1O cold: "+why)


def sha(raw):
    return sha256(raw).hexdigest()


def records(seal):
    rows = K.private(seal, "F1JFixedRoundMind")["_f1o_errors"]
    check(type(rows) is list and len(rows) <= 8, "invalid private memory")
    out = [dict(x["__dict__"]) for x in rows]
    for t, r in enumerate(out, 1):
        check(set(r) == {"t","key","body","error"} and r["t"] == t
              and type(r["key"]) is list and 1 <= len(r["key"]) <= 2
              and all(type(v) is str or v is None for v in r["key"])
              and len(r["body"]) == len(r["error"]) == 5
              and all(isfinite(v) and 0 <= v <= 100 for v in r["body"])
              and all(isfinite(v) and -100 <= v <= 100 for v in r["error"]),
              "unbounded or nonpersonal record")
    return out


def invoice(rec, world, blocks):
    K.world_eq(rec["before"], world, "before F1O preauthorized work")
    total = dict.fromkeys(FIELDS, 0)
    check(len(rec["authorizations"]) == len(blocks), "missing authorization")
    for authorization, block in zip(rec["authorizations"], blocks):
        check(authorization["block"] == block, "incorrect priced block")
        total = {k: total[k]+block[k] for k in FIELDS}
        check(authorization["cumulative"] == total, "incorrect cumulative grant")
        cost = I.cost(total)
        remaining = world["body"][:]
        remaining[0] -= cost["energy"]
        remaining[4] -= cost["vigilance"]
        check(min(remaining) >= -1e-10, "nonexistent reserves")
        I.body_equal(authorization["remaining"], remaining, "preauthorized grant")
    check(rec["work"] == total, "incorrect total paid work")
    I.check_bill(rec["bill"], I.cost(total), "actual F1O debit")
    end = deepcopy(world)
    end["body"] = remaining
    K.world_eq(rec["after"], end, "actual F1O corporeal payment")
    return rec["after"]


def expected_world(grid, origin):
    e = next(x for x in grid["ecologies"] if x["id"] == origin["ecology"])
    adapted = dict(e, water=e["water_position"], food=e["food_position"],
                   token=e["food_token"])
    world = K.origin_world({"ecologies": [adapted]}, origin)
    world["world_spec"]["name"] = "F1O_DEV_"+origin["id"]+"_"+e["id"]
    return world


def check_forecast(witness, mode, private, stats, history, t, body, action, param):
    last = private["last"]["__tuple__"]
    check(last[2:] == [action,param] and last[0]["__tuple__"] == body,
          "forecast on nonadmitted motor or incorrect perceived body")
    key = ("se_deplacer",) if action == "se_deplacer" else tuple(last[1]["__tuple__"])
    check(key[0] == action and witness["key"] == list(key) and witness["body"] == body,
          "forged key/body")
    labels = [key, (key[0], None), ("*",)]
    queried = [{"key":list(k),"stat":stats.get(k)} for k in labels]
    check(witness["consultations"] == queried, "missing or fictitious native table accesses")
    mean = next((x["stat"][1] for x in queried if x["stat"] and x["stat"][0]>0.), [0.]*5)
    ranked = []
    inspection = []
    for r in history:
        check(r["t"] < t, "future memory used")
        distance = fsum(abs(x-y) for x,y in zip(body,r["body"]))
        same = tuple(r["key"]) == key
        inspection.append({"t":r["t"],"same_key":same,"distance":distance})
        if same:
            ranked.append((distance,-r["t"],r))
    chosen = min(ranked,key=lambda q:q[:2])[2] if ranked else None
    error = chosen["error"] if chosen else [0.]*5
    applied = error if mode == "corrected" else [0.]*5
    check(witness["inspections"] == inspection and witness["selected_tick"] ==
          (chosen["t"] if chosen else None), "wrong private context selection or inspection")
    check(witness["mean"] == mean and witness["selected_error"] == error
          and witness["applied_error"] == applied, "wrong mean/masking")
    pred = [min(100.,max(0., b+m+.5*e)) for b,m,e in zip(body,mean,applied)]
    I.body_equal(witness["prediction"],pred,"one-step clipped forecast")
    return pred


def life(obj, origin, grid, cohort, order):
    check(obj["phase"] == PHASE and obj["origin"] == origin and obj["cohort"] == cohort
          and obj["order"] == list(order) and obj["failure"] is None
          and len(obj["steps"]) == 24, "incomplete native origin (no replacement)")
    world = expected_world(grid,origin)
    K.world_eq(obj["genesis"]["world"],world,"frozen DEV genesis")
    world = obj["genesis"]["world"]
    mind = obj["genesis"]["mind"]
    fields = K.private(mind,"F1JFixedRoundMind")
    check(not K.effects(mind) and not fields["buffer"]["__deque__"]
          and fields["last"] is None and not records(mind)
          and fields["observer_full_competition"] is (cohort=="A")
          and fields["observer_decision_diagnostics"] is (cohort=="A")
          and all(v == 0. for row in fields["values"] for v in row),
          "invented prenatal learning or wrong diagnostics flag")
    gains = []
    for t,row in enumerate(obj["steps"],1):
        check(row["t"] == t and row["before_mind"] == mind and world["t"] == t-1
              and not world["dead"], "broken native chain")
        hist = records(mind)
        check(len(hist)==min(t-1,8),"wrong history length")
        block = {"cycles":1,"simulated_steps":1,"memory_items":3+len(hist),"replays":0}
        pre = invoice(row["prepayment"],world,[block,block])
        K.world_eq(row["before_world"],pre,"decision following forecast payment")
        check(row["capture"]==K.perceive(pre) and row["capture_sha256"]==I.h(row["capture"]),
              "not actual private capture after prepayment")
        after = row["after_restoration_before_motor"]
        p = K.private(after,"F1JFixedRoundMind")
        check(row["decision_info"]["funding"]=="FUNDED" and row["action"] is not None
              and row["mind_after_forecasts"]==after and records(after)==hist
              and K.effects(after)==K.effects(mind), "unfunded motor or forecasts interfered")
        work = row["cognitive_work"]
        cost = I.cost(work)
        check(cost==row["requested_native_cost"],"native decision bill")
        remaining = pre["body"][:]
        remaining[0]-=cost["energy"]
        remaining[4]-=cost["vigilance"]
        I.body_equal(row["decision_remaining"],remaining,"native decision allowance")
        if cohort=="A":
            J.cold_paid_fixed_competition(row)
        else:
            check("observer" not in row["decision_info"]
                  and work["cycles"]==3+row["decision_info"]["cycles"],
                  "observer-disabled native decision accounting")
        check(set(row["forecasts"])==set(ORDERS[0])
              and row["forecast_seal"]==I.h(row["forecasts"]), "unsealed paired forecast")
        pred = {mode:check_forecast(row["forecasts"][mode],mode,p,K.effects(after),hist,
                                    t,pre["body"],row["action"],row["param"])
                for mode in ORDERS[0]}
        state,summary = K.physical(pre,row["action"],row["param"],work,
                                  row["native_motor"]["cognitive_accounting"])
        for k in ("t","dead","moved"):
            check(row["native_motor"][k]==summary[k],"native motor mismatch")
        I.body_equal(row["native_motor"]["body"],summary["body"],"actual motor body")
        K.world_eq(row["after_motor_world"],state,"native motor")
        learned,learned_mind=K.paid_learning(row,state)
        K.verify_paid_personal_learning(row)
        check(row["postaction"]["status"]=="PAID_LEARNED" and not learned["dead"]
              and records(learned_mind)==hist,"invalid or unowned native learning")
        K.world_eq(row["after_paid_learning_world"],learned,"real learning body")
        I.body_equal(row["target"],learned["body"],"actual pre-write target")
        expected = deepcopy(hist)
        if t<=8:
            write = {"cycles":1,"simulated_steps":0,"memory_items":1,"replays":0}
            end=invoice(row["write"],learned,[write])
            expected.append({"t":t,"key":row["forecasts"]["masked"]["key"],
                             "body":pre["body"],"error":[y-x for y,x in
                                 zip(learned["body"],pred["masked"])]})
        else:
            check(row["write"] is None,"memory not frozen T9..24")
            end=learned
            y=learned["body"]
            gains.append(fsum(abs(a-b)-abs(c-b) for a,b,c in
                              zip(pred["masked"],y,pred["corrected"]))/5.)
        K.world_eq(row["end_world"],end,"postwrite native body")
        end_fields=K.private(row["end_mind"])
        prev_fields=K.private(learned_mind)
        check(records(row["end_mind"])==expected
              and {k:v for k,v in end_fields.items() if k!="_f1o_errors"}==
                  {k:v for k,v in prev_fields.items() if k!="_f1o_errors"},
              "memory write was forged or modified native state")
        world=row["end_world"]
        mind=row["end_mind"]
    return fsum(gains)/16


def audit(directory, cohort):
    grid,_=F.check_files()
    base=Path(directory)
    index=json.loads((base/"index.json").read_bytes())
    tree=subprocess.check_output(["git","rev-parse","HEAD^{tree}"],text=True).strip()
    check(cohort in ("A","B") and index["phase"]==PHASE and index["cohort"]==cohort
          and index["source_tree"]==tree and index["frozen_grid"]==F.GRID_BLOB
          and index["frozen_protocol"]==F.PROTOCOL_BLOB and index["science_verdict"] is None
          and len(index["entries"])==16,"incorrect source provenance")
    check(index["failures"]==0,"native completeness gate failed; preserve originals")
    expected_files={"index.json"}
    gains=[]
    pos=0
    for origin in grid["dev_allocations"][cohort]:
        pair=[]
        for order in ORDERS:
            name=origin["id"]+"-"+order[0]+".json.gz"
            entry=index["entries"][pos]
            pos+=1
            expected_files.update((name,f"checkpoint-{pos:02d}.json"))
            check(entry["path"]==name and entry["root"]==origin["id"]
                  and entry["order"]==list(order),"original order or identity altered")
            checkpoint=json.loads((base/f"checkpoint-{pos:02d}.json").read_bytes())
            check(checkpoint=={"source_tree":tree,"entries":index["entries"][:pos]},
                  "incomplete checkpoint custody")
            zipped=(base/name).read_bytes()
            raw=gzip.decompress(zipped)
            check(len(zipped)==entry["gzip_bytes"] and len(raw)==entry["raw_bytes"]
                  and sha(zipped)==entry["gzip_sha256"] and sha(raw)==entry["raw_sha256"],
                  "original compressed/raw bytes mismatch")
            obj=json.loads(raw)
            check(I.c(obj)==raw,"noncanonical original")
            gain=life(obj,origin,grid,cohort,order)
            pair.append(obj)
        check({k:v for k,v in pair[0].items() if k!="order"}==
              {k:v for k,v in pair[1].items() if k!="order"},
              "reverse order changed native trajectory, outputs, payment or private state")
        gains.append(gain)
    check({p.name for p in base.iterdir()}==expected_files,"missing or unexpected originals")
    check(not any(x=="i3" or x.startswith("i3.") for x in sys.modules),"engine imported by cold")
    return {"status":"DEV_ONLY_COLD_PASS_NOT_SCIENCE","cohort":cohort,"source_tree":tree,
            "roots":8,"seed_set":[o["seed"] for o in grid["dev_allocations"][cohort]],
            "original_gzip_verified":16,"native_steps":384,"paired_forecasts":384,
            "evaluation_pairs_unique":128,"paid_writes":128,"order_shams":8,
            "observer_diagnostics":cohort=="A","science_verdict":None,
            "scientific_births":0,"descriptive_dev_gains":gains}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cohort", choices=("A","B"),required=True)
    p.add_argument("--original-dir",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    report=audit(a.original_dir,a.cohort)
    with Path(a.output).open("xb") as fp:
        fp.write(I.c(report))
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
