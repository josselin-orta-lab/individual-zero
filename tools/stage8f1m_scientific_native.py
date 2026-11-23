"""F1M scientific-only native actor: remote reservation BEFORE M01..M32 birth.

Different from DEV_M producer. This module cannot execute M seeds by CLI
or import. The only admission is a GitHub-protected, verified, first-run claim.
The experiment never supplies motor actions. Preserve original native parts
after every source/arm, including partial evidence if the job fails.
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
from tools import stage8f1l_paid_content_body_value_dev as L
from tools import stage8f1m_dev_residual_mediation as M
from tools import stage8f1m_one_shot_reservation as R
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA="i3-stage8f1m-scientific-one-shot-residual-causal-T60/v0"
PHASE="F1M_HELDOUT_RELEASE"
_ADMISSION=object()


def release_grid():
    """Static prereg on main; never invoke any M World before remote claim."""
    from tools import stage8f1m_prereg_static_guard as frozen
    verified=frozen.check_files()
    grid=json.loads(Path(R.GRID_PATH).read_bytes())
    if (verified["roots"]!=32 or verified["ecologies"]!=8
            or [r["id"] for r in grid["origins"]]!=R.ROOT_IDS
            or [r["seed"] for r in grid["origins"]]!=R.SEEDS
            or grid["arms"]!=R.ARMS):
        raise PermissionError("M scientific population differs from Git prereg")
    return grid


def _new_world(grid, origin, admission):
    if admission is not _ADMISSION:
        raise PermissionError("M scientific World requires remote first-only admission")
    if (origin not in grid["origins"]
            or origin["id"] not in R.ROOT_IDS
            or origin["seed"]!=R.SEEDS[R.ROOT_IDS.index(origin["id"])]):
        raise PermissionError("unregistered M WorldSpec, seed or origin")
    e=next(x for x in grid["ecologies"] if x["id"]==origin["ecology"])
    world=grid["world"]
    return World(WorldSpec(
        name="F1M_HELDOUT_ORIGIN_"+origin["id"]+"_"+e["id"],
        width=world["width"],height=world["height"],
        spawn=tuple(world["spawn"]),body=tuple(origin["body"]),
        water={tuple(e["water"]):WaterSource(
            gain=e["water_gain"],stock=e["water_stock"],
            max_stock=e["water_max_stock"],
            restock_every=e["water_restock_every"])},
        food={tuple(e["food"]):FoodPatch(
            token=e["token"],quantity=e["food_quantity"],
            max_quantity=e["food_max_quantity"],
            restock_every=e["food_restock_every"])},
        token_effects={e["token"]:(e["food_gain"],e["integrity_delta"])},
        changes=(),laws=BodyLaws()))


def _paid_source(grid, origin, admission):
    """Only experiment's actual T1..T4, never synthetic or replayed."""
    world=_new_world(grid,origin,admission)
    mind=F1JFixedRoundMind(midpoint(),origin["seed"])
    if (world.t!=0 or world.dead or mind.effects.stats or mind.buffer
            or any(any(v!=0. for v in row) for row in mind.values)):
        raise AssertionError("artificial innate memory, TD, episodic or body state")
    genesis={"world":D0._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps=[]; t1_stats={}; error=None
    for tick in range(1,5):
        if world.dead:
            break
        try:
            steps.append(L.paid_step(world,mind))
            if tick==1:
                t1_stats=deepcopy(mind.effects.stats)
        except (ValueError,KeyError,RuntimeError,AssertionError) as exc:
            error={"tick":tick,"type":type(exc).__name__,"message":str(exc)}
            break
    valid=(error is None and len(steps)==4 and world.t==4
           and not world.dead and bool(t1_stats)
           and all(s["postaction"]["status"]=="PAID_LEARNED" for s in steps))
    record={"genesis":genesis,"source_steps":steps,
        "paid_t1_mean_anchor":[{"key":list(k),"stat":deepcopy(v)}
            for k,v in sorted(t1_stats.items(),key=lambda x:repr(x[0]))],
        "source_valid":valid,"source_error":error,
        "tick4_world":D0._snapshot_world(world),
        "tick4_mind":C.seal_mind(mind)}
    record["source_receipt_sha256"]=C.digest(record)
    return world,mind,t1_stats,record


def _followup(world,mind,mode,horizon):
    result=L.followup(world,mind,"full",None,horizon)
    result["policy"]="F1M_HELDOUT_"+mode
    return result


def _first_native_lock(path,claim):
    """O_EXCL and fsync precede EVERY first native World.step of M cohort."""
    data={"schema":"i3-stage8f1m-first-native-start-lock/v0",
          "run_id":claim["workflow_run_id"],
          "head_sha":claim["head_sha"],
          "root_ids":R.ROOT_IDS,
          "one_scientific_attempt_only":True}
    with Path(path).open("xb") as out:
        out.write(C.canonical(data)+b"\n")
        out.flush()
        os.fsync(out.fileno())


def _one(grid, origin, writer, admission):
    world,mind,t1,source=_paid_source(grid, origin, admission)
    row={"origin":origin,"source":source,"content_t5":{},
         "arms":{},"shams":{},"sham_arms":{},"comparison":{}}
    writer.part(origin["id"], "source", source)
    if not source["source_valid"]:
        writer.finalize_case(row)
        return row
    t5_states={}
    for content in M.CONTENT:
        w,m=deepcopy(world),deepcopy(mind)
        mode="full" if content=="recent" else "stale_owned_t1_means"
        t5=L.paid_step(w,m,mode,t1 if content=="stale" else None)
        row["content_t5"][content]=t5
        writer.part(origin["id"], content+"_t5", t5)
        t5_states[content]=(w,m)
    sham_w,sham_m=deepcopy(world),deepcopy(mind)
    sham_t5=L.paid_step(sham_w,sham_m,"full_sham")
    row["shams"]["t5_recent_full_sham"]=sham_t5
    writer.part(origin["id"], "recent_sham_t5", sham_t5)
    row["comparison"]["t5_full_sham_neutral"]=(L.semantic_sham_step(sham_t5)==
                             L.semantic_sham_step(row["content_t5"]["recent"]))
    row["comparison"]["equal_t5_real_decision_cost"]=M.t5_pair_cost(
         row["content_t5"]["recent"],row["content_t5"]["stale"])
    for content in CONTENT:
        a_world,a_mind=t5_states[content]
        for mode in M.RESIDUAL:
            key=content+"/"+mode
            world_i,mind_i=deepcopy(a_world),deepcopy(a_mind)
            fork=M.residual_intervention(mind_i,mode)
            row["arms"][key]={"fork":fork,
                   "followup":_followup(world_i,mind_i,key,grid["final_tick"])}
            writer.part(origin["id"], key.replace("/", "_"), row["arms"][key])
            # Repeat the SAME nonmotor operation, with a freshly cloned native
            # T5 state. No fictitious CognitiveWork or physics, no seeded L life.
            world_s,mind_s=deepcopy(a_world),deepcopy(a_mind)
            fork_sham=M.residual_intervention(mind_s,mode)
            same=(fork==fork_sham)
            sham=_followup(world_s,mind_s,key,grid["final_tick"])
            ref=row["arms"][key]["followup"]
            row["sham_arms"][key]=sham
            writer.part(origin["id"], key.replace("/", "_")+"_sham", sham)
            same=(same and sham["steps"]==ref["steps"]
                  and sham["last_world"]==ref["last_world"]
                  and sham["last_mind"]==ref["last_mind"]
                  and sham["metrics"]==ref["metrics"])
            row["shams"][key+"_neutral"]=same
        carry=row["arms"][content+"/carry"]["followup"]
        zero=row["arms"][content+"/zero"]["followup"]
        if carry["steps"] and zero["steps"]:
            x,y=carry["steps"][0],zero["steps"][0]
            row["comparison"][content]={
              "equal_t6_real_decision_cost":M.t6_pair_cost(x,y),
              "winner_changed":(
                x["decision_info"]["observer"]["competition_witness"]["winner_before_control"]!=
                y["decision_info"]["observer"]["competition_witness"]["winner_before_control"]),
              "motor_changed":(x["action"],x["param"])!=(y["action"],y["param"]),
              "carry_t6_motor":[x["action"],x["param"]],
              "zero_t6_motor":[y["action"],y["param"]],
              "carry_t6_winner":x["decision_info"]["observer"]["competition_witness"]["winner_before_control"],
              "zero_t6_winner":y["decision_info"]["observer"]["competition_witness"]["winner_before_control"],
              "carry_t6_work":x["cognitive_work"],"zero_t6_work":y["cognitive_work"],
              "carry_t6_billing":x["requested_native_cost"],
              "zero_t6_billing":y["requested_native_cost"],
              "t6_body_delta_after_paid_learning":[
                  v-w for v,w in zip(x["postaction"]["body_after_any_learning"],
                                     y["postaction"]["body_after_any_learning"])],
              "t6_body_delta_after_motor":[
                  v-w for v,w in zip(x["native_motor"]["body"],
                                     y["native_motor"]["body"])],
              "body":M.body_comparison(carry,zero),
            }
        else:
            row["comparison"][content]={"error":"MISSING_NATIVE_T6"}
    row["case_sha256"]=C.digest({k:v for k,v in row.items()
                                  if k!="case_sha256"})
    writer.finalize_case(row)
    return row



def produce_release(reservation_file,writer):
    path=Path(reservation_file)
    claim=R.verify_remote(R.load_receipt(path))
    grid=release_grid()
    if not callable(getattr(writer,"part",None)):
        raise PermissionError("F1M native per-part original evidence writer required")
    if not callable(getattr(writer,"finalize_case",None)):
        raise PermissionError("F1M native per-root checkpoint writer required")
    _first_native_lock(path.with_suffix(".NATIVE_START_LOCK"),claim)
    row_metadata=[]
    for origin in grid["origins"]:
        # Each M-root only once, after remote claim and no bypass check.
        R.verify_remote(R.load_receipt(path))
        row=_one(grid,origin,writer,_ADMISSION)
        row_metadata.append({
            "origin":origin,
            "case_sha256":row.get("case_sha256"),
            "source_valid":row["source"]["source_valid"],
            "comparison":row["comparison"],
            "sham_t5_neutral":row["comparison"].get("t5_full_sham_neutral"),
        })
        del row
    return {"schema":SCHEMA,"phase":PHASE,
            "source_main_prereg_commit":R.PREEXPOSURE,
            "grid_blob_sha":R.GRID_BLOB,
            "protocol_blob_sha":R.PROTOCOL_BLOB,
            "origin_ids":R.ROOT_IDS,"seeds":R.SEEDS,
            "source_policy":"F1JFixedRoundMind",
            "arms":R.ARMS,"source_ticks":4,
            "content_tick":5,"residual_fork_tick":6,"final_tick":60,
            "original_scientific_native_passes":1,
            "no_motor_override":True,
            "scientific_verdict":None,
            "producer_only_status":"F1M_ORIGINAL_UNAUDITED",
            "rows":row_metadata}
