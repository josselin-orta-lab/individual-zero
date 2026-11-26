"""F1N DEV ONLY: native paid T5-owned margin, equal-priced T6 fork and T60 shams.

Only two disjoint DEV_N cohorts may be born here. This module has no scientific
admission token, no N01..N48 birth, no release and no one-shot claim operation.
Every recorded motor is actually selected by F1NMarginMind / native ActionControl
and applied by World.step. All receipts are gzip-preserved after each part.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import gzip
import io
import json
from pathlib import Path

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1l_paid_content_body_value_dev as L
from tools import stage8f1n_prereg_static_guard as N
from tools.stage8f1n_paid_margin_mind import F1NMarginMind

SCHEMA = "i3-stage8f1n-dev-owned-margin-native-T60/v0"
PART_SCHEMA = "i3-stage8f1n-native-incremental-receipt/v0"
PHASE = "DEV_ONLY_NEVER_F1N_SCIENTIFIC"
DEV_A_SEEDS = tuple(range(202611269101, 202611269109))
DEV_B_SEEDS = tuple(range(202611269121, 202611269129))
EXPOSED_F1N = frozenset(N.SEEDS)
PARTS = tuple(N.PARTS)
ARMS = ("margin", "masked")


def dev_grid(cohort="A", full=True):
    """Literal DEV fixtures, never reserved N roots or F1M/M seeds."""
    if cohort not in ("A", "B") or type(full) is not bool:
        raise ValueError("unregistered F1N DEV population")
    ecologies = [
        {"id":"DEV_N_spring_south", "water":[0,2], "water_gain":19,
         "water_stock":3, "water_max_stock":3, "water_restock_every":6,
         "food":[2,0], "token":"dev-n-tuber", "food_gain":22,
         "integrity_delta":0.8, "food_quantity":3,
         "food_max_quantity":3, "food_restock_every":5},
        {"id":"DEV_N_bitter_pond", "water":[2,2], "water_gain":23,
         "water_stock":2, "water_max_stock":2, "water_restock_every":5,
         "food":[0,0], "token":"dev-n-bitter", "food_gain":26,
         "integrity_delta":-0.8, "food_quantity":2,
         "food_max_quantity":2, "food_restock_every":6},
    ]
    seeds=DEV_A_SEEDS if cohort=="A" else DEV_B_SEEDS
    originals=[]
    for idx,seed in enumerate(seeds):
        j=idx%4
        originals.append({"id":f"DEV_N{cohort}{idx+1:02d}",
                          "ecology":ecologies[idx//4]["id"],
                          "seed":seed,
                          "body":[66+j,72-j,42+0.4*j,92-0.3*j,94-0.2*j]})
    if not full:
        originals=[originals[0],originals[4]]
    return {"schema":"i3-stage8f1n-dev-grid/v0",
            "phase":PHASE, "cohort":cohort,"origin_count":len(originals),
            "world":{"width":3,"height":3,"spawn":[1,1],
                     "laws":"BodyLaws() i3-body-laws-v2","changes":[]},
            "ecologies":ecologies,"origins":originals,
            "final_tick":60,"source_ticks":4,"t5_tick":5,
            "t6_margin_fork":6,"arms":list(ARMS)}


def dev_source_gate(grid):
    N.check_files()  # PREEXPOSURE-ONLY Git source pins; no N births.
    cohort=grid.get("cohort")
    expected=(dev_grid(cohort,True),dev_grid(cohort,False))
    if grid not in expected:
        raise PermissionError("DEV_N accepts only two fixed development populations")
    ids={o["id"] for o in grid["origins"]}
    seeds={o["seed"] for o in grid["origins"]}
    excluded=set(N.SEEDS)|set(range(202611239701,202611239733))
    excluded|=set(range(202611239601,202611239619))
    excluded|=set(range(202611229501,202611229609))
    if (not all(s in DEV_A_SEEDS+DEV_B_SEEDS for s in seeds) or
            bool(seeds&excluded) or len(ids)!=len(seeds) or
            not all(i.startswith("DEV_N"+cohort) for i in ids)):
        raise PermissionError("scientific F1N or historical DEV identity contamination")
    return True


def dev_world(grid,origin):
    if (origin not in grid["origins"] or
            origin["seed"] not in DEV_A_SEEDS+DEV_B_SEEDS or
            not origin["id"].startswith("DEV_N")):
        raise PermissionError("F1N HELDOUT N01..N48 cannot be instantiated")
    e=next(x for x in grid["ecologies"] if x["id"]==origin["ecology"])
    return World(WorldSpec(
        name="F1N_DEV_ORIGIN_"+origin["id"]+"_"+e["id"],
        width=3,height=3,spawn=(1,1),body=tuple(origin["body"]),
        water={tuple(e["water"]): WaterSource(
            gain=e["water_gain"],stock=e["water_stock"],
            max_stock=e["water_max_stock"],restock_every=e["water_restock_every"])},
        food={tuple(e["food"]): FoodPatch(
            token=e["token"],quantity=e["food_quantity"],
            max_quantity=e["food_max_quantity"],restock_every=e["food_restock_every"])},
        token_effects={e["token"]:(e["food_gain"],e["integrity_delta"])},
        changes=(),laws=BodyLaws()))


def source(world,mind):
    if (world.t!=0 or world.dead or mind.effects.stats or mind.buffer or
        mind.f1n_owned_margin is not None or
        any(any(v!=0.0 for v in row) for row in mind.values)):
        raise AssertionError("invented DEV_N prenatal personal knowledge")
    genesis={"world":D._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps=[];error=None
    for tick in range(1,5):
        if world.dead:
            break
        try:
            step=L.paid_step(world,mind)
            steps.append(step)
        except (ValueError,AssertionError,RuntimeError,KeyError) as e:
            error={"tick":tick,"type":type(e).__name__,"message":str(e)}
            break
    valid=(len(steps)==4 and error is None and world.t==4 and
           not world.dead and
           all(step["postaction"]["status"]=="PAID_LEARNED" for step in steps))
    return {"genesis":genesis,"steps":steps,"error":error,"valid":valid,
            "world_t4":D._snapshot_world(world),"mind_t4":C.seal_mind(mind)}


def pay_owned_t5_memory(world,mind,step):
    """One genuine PRIVATE write after the actual motor and paid learning.

    The laboratory never derives q from witness data; q originates in the
    individual's F1N _compete method and is held pending until real payment.
    """
    if world.t!=5 or world.dead or step["t"]!=5:
        raise RuntimeError("cannot mint a T5 margin before native paid life")
    if step["postaction"]["status"]!="PAID_LEARNED":
        raise RuntimeError("no paid personal T5 outcome for memory")
    pending=mind.f1n_pending_margin
    if type(pending) is not dict or set(pending)!={"key","q","crossed","paid_rounds"}:
        raise AssertionError("F1N own decision did not produce a margin")
    if step["decision_info"].get("funding")!="FUNDED":
        raise AssertionError("F1N original choice not actually financed")
    before_world=D._snapshot_world(world)
    before_mind=C.seal_mind(mind)
    native_admitted=(step["decision_info"].get("option")==pending["key"]
                     and step["action"] is not None
                     and step["decision_info"]["observer"]["competition_witness"]
                         ["winner_before_control"]==pending["key"])
    q=float(pending["q"] if pending["crossed"] and native_admitted else 0.0)
    if not 0.0<=q<=1.0:
        raise ValueError("unbounded owned threshold margin")
    work=CognitiveWork(memory_items=1)
    grant=CognitiveBudget(world.body,world.laws)
    grant.spend(work)  # preauthorization BEFORE actually storing the item
    bill=world.pay_cognition(grant.work)
    C.paid_bill(world.laws,grant.work,bill)
    mind.f1n_owned_margin={"source_tick":5,"key":pending["key"],"q":q}
    mind.f1n_pending_margin=None
    rec={"source":"own_paid_t5_native_competition",
         "authentic_admitted_winner":native_admitted,
         "own_final_q":q,"own_final_key":pending["key"],
         "genuinely_executed_work":asdict(work),
         "actual_paid_memory_bill":deepcopy(bill),
         "memory_budget_remaining":list(grant.remaining),
         "world_before_write":before_world,
         "mind_before_write":before_mind,
         "world_after_write":D._snapshot_world(world),
         "mind_after_write":C.seal_mind(mind),
         "no_observer_to_policy":True,"no_world_step_during_write":True}
    rec["sha256"]=C.digest(rec)
    return rec


def t5(world,mind,sham=False):
    step=L.paid_step(world,mind,"full_sham" if sham else "full")
    write=pay_owned_t5_memory(world,mind,step)
    if sham:
        # No-op sham copy after genuine payment, no action override.
        mind.f1n_owned_margin=deepcopy(mind.f1n_owned_margin)
    return {"step":step,"write":write,
            "t5_world":D._snapshot_world(world),
            "t5_mind":C.seal_mind(mind)}


def fork(mind,mode):
    before=C.seal_mind(mind)
    mind.arm_paid_t6_read(mode)
    after=C.seal_mind(mind)
    return {"mode":mode,"before_mind":before,"after_mind":after,
            "same_original_personal_record":deepcopy(mind.f1n_owned_margin),
            "keys_and_scores_untouched":True,"no_motor_override":True}


def followup(world,mind,mode):
    if mode not in ARMS or world.t!=5:
        raise ValueError("unregistered DEV_N future or non-native fork time")
    rec=L.followup(world,mind,"full",None,60)
    rec["policy"]="F1N_DEV_"+mode
    rec["trajectory_sha256"]=C.digest({k:v for k,v in rec.items()
                                          if k!="trajectory_sha256"})
    return rec


def compare(arms):
    if set(arms)!=set(ARMS):
        return {"error":"SOURCE_INCOMPLETE"}
    x=arms["margin"]["followup"]
    y=arms["masked"]["followup"]
    if not x["steps"] or not y["steps"]:
        return {"error":"MISSING_NATIVE_T6"}
    a,b=x["steps"][0],y["steps"][0]
    # T6 starts from a CLONED true T5 world, not the zero/intervened body.
    real_parity=(a["before_world"]==b["before_world"]
        and a["capture"]==b["capture"]
        and a["cognitive_work"]==b["cognitive_work"]
        and a["requested_native_cost"]==b["requested_native_cost"]
        and a["decision_remaining"]==b["decision_remaining"]
        and a["native_motor"]["cognitive_accounting"]==
            b["native_motor"]["cognitive_accounting"]
        and a["cognitive_work"]["memory_items"]>0
        and all(row["paid"]==row["requested"] and row["unpaid"]==0.0
                for step in (a,b) for row in
                step["native_motor"]["cognitive_accounting"].values()))
    wa=a["decision_info"]["observer"]["competition_witness"]
    wb=b["decision_info"]["observer"]["competition_witness"]
    return {"equal_t6_real_decision_cost":real_parity,
            "t6_margin_witness":wa["f1n_margin_read"],
            "t6_masked_witness":wb["f1n_margin_read"],
            "thresholds_changed":wa["thresholds"]!=wb["thresholds"],
            "winner_changed":wa["winner_before_control"]!=wb["winner_before_control"],
            "motor_changed":(a["action"],a["param"])!=(b["action"],b["param"]),
            "margin_motor":[a["action"],a["param"]],
            "masked_motor":[b["action"],b["param"]],
            "margin_first_work":a["cognitive_work"],
            "masked_first_work":b["cognitive_work"],
            "delta_lived_ticks":len(x["steps"])-len(y["steps"]),
            "delta_body":[v-w for v,w in zip(x["metrics"]["terminal_body"],
                                             y["metrics"]["terminal_body"])]}


def compressed(obj):
    raw=C.canonical(obj)
    data=io.BytesIO()
    with gzip.GzipFile(filename="",mode="wb",fileobj=data,mtime=0,
                       compresslevel=9) as gz:
        gz.write(raw)
    return raw,data.getvalue()


class DEVWriter:
    """Every DEV native part written exactly once with hash receipt."""
    def __init__(self,directory,grid):
        self.base=Path(directory)
        self.base.mkdir(parents=True,exist_ok=False)
        self.grid=grid
        self.entries=[]
        self.cases=[]

    def part(self,root,kind,payload):
        index=len(self.cases)
        if (index>=len(self.grid["origins"]) or
            root!=self.grid["origins"][index]["id"] or
            kind!=PARTS[len(self.entries)%len(PARTS)]):
            raise RuntimeError("F1N original part out of order")
        obj={"schema":PART_SCHEMA,"id":root,"part":kind,"native":payload}
        raw,gz=compressed(obj)
        rel=f"{root}/{kind}.json.gz"
        dest=self.base/rel
        dest.parent.mkdir(exist_ok=True)
        with dest.open("xb") as fp:
            fp.write(gz)
        self.entries.append({"path":rel,"id":root,"part":kind,
                             "raw_sha256":C.digest(obj),
                             "gzip_sha256":__import__("hashlib").sha256(gz).hexdigest(),
                             "raw_bytes":len(raw),"gzip_bytes":len(gz)})

    def case(self,origin,comparison,source_valid,shams_neutral):
        self.cases.append({"origin":origin,"comparison":comparison,
                           "source_valid":source_valid,"shams_neutral":shams_neutral})
        if len(self.entries)!=len(self.cases)*len(PARTS):
            raise RuntimeError("F1N incomplete native parts or reordered case")
        tmp={"completed":len(self.cases),"roots":[r["origin"]["id"]
                                                    for r in self.cases],
             "entries":deepcopy(self.entries)}
        with (self.base/f"_checkpoint_{len(self.cases):02d}.json").open("xb") as fp:
            fp.write(C.canonical(tmp)+b"\n")

    def finish(self):
        summary={"source_valid":sum(c["source_valid"] for c in self.cases),
                 "shams_neutral":sum(c["shams_neutral"] for c in self.cases),
                 "t6_equal_cost":sum(c["comparison"].get(
                                  "equal_t6_real_decision_cost",False)
                                      for c in self.cases),
                 "motor_changed":sum(c["comparison"].get("motor_changed",False)
                                     for c in self.cases)}
        result={"schema":SCHEMA,"phase":PHASE,"grid":self.grid,
                "case_count":len(self.cases),"parts_per_root":len(PARTS),
                "original_parts":len(self.entries),"parts":list(PARTS),
                "entries":self.entries,"cases":self.cases,"summary":summary,
                "scientific_verdict":None,
                "f1n_heldout_world_steps_created":0,
                "source_single_native_pass":True,
                "no_imposed_motor":True,"no_retroactive_cost_padding":True}
        with (self.base/"F1N_DEV_NATIVE_INDEX.json").open("xb") as fp:
            fp.write(C.canonical(result)+b"\n")
        return result


def _one(grid,origin,writer):
    world=dev_world(grid,origin)
    mind=F1NMarginMind(midpoint(),origin["seed"])
    src=source(world,mind)
    writer.part(origin["id"],"source_t1_t4",src)
    if not src["valid"]:
        raise RuntimeError("DEV_N source incomplete, partial receipt already saved: "+origin["id"])
    saved_w,saved_m=deepcopy(world),deepcopy(mind)
    t5w,t5m=deepcopy(saved_w),deepcopy(saved_m)
    tick5=t5(t5w,t5m,sham=False)
    writer.part(origin["id"],"self_paid_t5",tick5)
    sw,sm=deepcopy(saved_w),deepcopy(saved_m)
    sham5=t5(sw,sm,sham=True)
    writer.part(origin["id"],"self_paid_t5_sham",sham5)
    neutral=(L.semantic_sham_step(tick5["step"])==
             L.semantic_sham_step(sham5["step"]) and
             tick5["write"]==sham5["write"] and
             tick5["t5_world"]==sham5["t5_world"] and
             tick5["t5_mind"]==sham5["t5_mind"])
    arms={}
    shams={}
    for mode in ARMS:
        aw,am=deepcopy(t5w),deepcopy(t5m)
        f=fork(am,mode)
        native={"fork":f,"followup":followup(aw,am,mode)}
        writer.part(origin["id"],mode+"_t6_t60",native)
        arms[mode]=native
        sw,sm=deepcopy(t5w),deepcopy(t5m)
        fs=fork(sm,mode)
        sham={"fork":fs,"followup":followup(sw,sm,mode)}
        writer.part(origin["id"],mode+"_t6_t60_sham",sham)
        x,y=native["followup"],sham["followup"]
        shams[mode]=(f==fs and x==y)
    comparison=compare(arms)
    neutral=neutral and all(shams.values())
    writer.case(origin,comparison,src["valid"],neutral)
    return comparison


def produce(cohort="A",full=True,output_dir=None):
    grid=dev_grid(cohort,full)
    dev_source_gate(grid)
    writer=DEVWriter(output_dir,grid)
    for origin in grid["origins"]:
        _one(grid,origin,writer)
    return writer.finish()


def main():
    ap=argparse.ArgumentParser(description="F1N DEVELOPMENT ONLY; no heldout births")
    ap.add_argument("--cohort",choices=("A","B"),required=True)
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke",action="store_true")
    mode.add_argument("--full",action="store_true")
    ap.add_argument("--output-dir",required=True)
    opt=ap.parse_args()
    report=produce(opt.cohort,opt.full,output_dir=opt.output_dir)
    print(json.dumps({"phase":report["phase"],"cohort":opt.cohort,
                      "cases":report["case_count"],"parts":report["original_parts"],
                      "summary":report["summary"],"no_F1N_science_births":True},sort_keys=True))


if __name__=="__main__":
    main()