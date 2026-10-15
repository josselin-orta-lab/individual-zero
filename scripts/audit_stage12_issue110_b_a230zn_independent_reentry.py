"""A2.30-ZN: archive-only independent reentry and Stage6 root-count audit.

Original evidence: immutable ZM run 38788052317, Python 3.11/3.12.
Preregistered AFTER known ZM results and BEFORE ZN reviewer code at
dda3bef49b3d09514a63f626de5c6eea0b95c01c.

NOT imported: original ZM runner, WorldBody, Equipment, SimulatorPlanner,
Oracle or I0Runtime. This auditor can verify the fixed receipts, counts and
exact input provenance but CANNOT itself reproduce WorldBody.apply.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes,sha256_hex

ORIGINAL_RUN=38788052317
ORIGINAL_CODE_SHA="daf800007330b420b92578270e0ec4f2ae37e410"
ORIGINAL_CANONICAL_WORLDS_SHA="b253fca92417b7b00f277b958cdf7c37f7ca9dd07b0749ec80c105280a65d6ff"
FILES=("a230zm-physical-loop-worlds.json","a230zm-summary.json")
POSITIONS=((5,5),(7,7))
B_LOCAL=(False,True)
ENERGY=(0.0,1.0)
FOOD=(0.0,0.5)
WATER=(0.0,0.2)
NIGHTS=(200,3)
PATH=tuple({"primitive":"se_deplacer","parameters":{"direction":d}}
           for d in ("east","south","west","north"))
EAST=PATH[0]
STATE_KEYS={
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
}
NEIGHBOR_KEYS={
    "direction","x","y","passable","water_source","resources","creature",
}
BODY_KEYS={"energy","food","water","integrity"}
INV_KEYS={"berry_a","berry_b","wood","stone","tool"}
DIRECTION_DELTAS={"north":(0,-1),"south":(0,1),
                  "east":(1,0),"west":(-1,0)}
PREPLANNED_FACTOR_COUNT=64


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def sealed_source(left,right):
    files={}
    sha={}
    for name in FILES:
        one=list(Path(left).rglob(name))
        two=list(Path(right).rglob(name))
        if len(one)!=1 or len(two)!=1:
            raise ValueError("original ZM archive missing or duplicated: "+name)
        a=one[0].read_bytes()
        b=two[0].read_bytes()
        if a!=b:
            raise ValueError("original ZM 3.11/3.12 archives not byte-identical")
        files[name]=json.loads(a)
        sha[name]=sha256(a).hexdigest()
    rows=files["a230zm-physical-loop-worlds.json"]
    summary=files["a230zm-summary.json"]
    if (digest(rows)!=ORIGINAL_CANONICAL_WORLDS_SHA
        or summary.get("physical_worlds_sha256")!=ORIGINAL_CANONICAL_WORLDS_SHA
        or summary.get("code_sha")!=ORIGINAL_CODE_SHA):
        raise ValueError("locked original ZM SHA/canonical world source altered")
    return rows,summary,sha


def visible(s):
    if (type(s) is not dict or set(s)!=STATE_KEYS
        or set(s["body"])!=BODY_KEYS
        or set(s["inventory"])!=INV_KEYS
        or len(s["adjacent"])!=4
        or {n["direction"] for n in s["adjacent"]}!=set(DIRECTION_DELTAS)
        or any(set(n)!=NEIGHBOR_KEYS for n in s["adjacent"])):
        raise ValueError("nonfirstperson/incomplete/hidden variable in state")
    if any(type(n["passable"]) is not bool for n in s["adjacent"]):
        raise ValueError("improper traversability observation")
    return s


def key(s,cmd):
    return digest({"state":visible(s),"command":cmd})


def candidate_commands(s):
    """Independent, explicit Stage6 candidate recomputation."""
    visible(s)
    result=[]
    for neighbor in s["adjacent"]:
        if neighbor["passable"]:
            result.append({
                "primitive":"se_deplacer",
                "parameters":{"direction":neighbor["direction"]},
            })
    for resource in sorted(set(s["current_resources"])):
        result.append({
            "primitive":"collecter","parameters":{"target":resource},
        })
    for berry in ("berry_a","berry_b"):
        if s["inventory"].get(berry,0)>0:
            result.append({
                "primitive":"manger","parameters":{"target":berry},
            })
    if s["current_water_source"]:
        result.append({"primitive":"boire","parameters":{}})
    if s["inventory"]["stone"]>0:
        result.append({"primitive":"poser_une_pierre","parameters":{}})
    if s["inventory"]["stone"]>0 and s["inventory"]["wood"]>0:
        result.append({"primitive":"fabriquer_outil","parameters":{}})
    result.extend((
        {"primitive":"dormir","parameters":{}},
        {"primitive":"attendre","parameters":{}},
    ))
    return result


def expected_perception(s,position,b_here,t,energy,food,water,night):
    """Check ONLY public sensory effects of a fixed, transparent lab fixture."""
    visible(s)
    where=tuple(position)
    initial=where if isinstance(where,tuple) else tuple(where)
    if (s["x"],s["y"])!=initial:
        raise ValueError("physically reported coordinate outside preregistered path")
    # t1 at rest, movement step n transforms body by fixed known WORLD
    # coefficients; used only by OFFLINE evaluator, never as model features.
    count=t-1
    expected={
        "energy":50.0-count*energy,
        "food":60.0-count*food,
        "water":20.0-count*water,
        "integrity":100.0,
    }
    if any(abs(float(s["body"][k])-v)>1e-9 for k,v in expected.items()):
        raise ValueError("physical cost/metabolism differs from fixed laboratory fixture")
    if s["is_night"] != (night==3 and t>=3):
        raise ValueError("observable day/night timing misrepresented")
    if s["inventory"]!={k:0 for k in INV_KEYS}:
        raise ValueError("unwitnessed collection or ingestion in motor-only protocol")
    if s["current_resources"]!=(
        ["berry_b"] if b_here and initial==tuple(position) else []
    ):
        raise ValueError("visible local berry affordance absent or fabricated")
    # The actual berry is stationary at origin. Verify all neighbor cues as
    # perceived for EVERY step, including the west/south returning route.
    x,y=initial
    for n in s["adjacent"]:
        dx,dy=DIRECTION_DELTAS[n["direction"]]
        coord=(x+dx,y+dy)
        if n["x"]!=coord[0] or n["y"]!=coord[1] or n["passable"] is not True:
            raise ValueError("visible neighbor geometry unexpectedly blocked")
        # A source resource lies only at the world birth position. More
        # detailed resource checks are performed in audit_world using root.
        if not isinstance(n["resources"],list):
            raise ValueError("adjacent berry/resource field not first-person")
    return s


def audit_world(row):
    fact=(
        tuple(row["factor_position"]),
        row["factor_berry_B_local_visible"],
        row["factor_movement_energy_cost"],
        row["factor_food_decay"],
        row["factor_water_decay"],
        row["factor_night_start"],
    )
    p,b,energy,food,water,night=fact
    if (p not in POSITIONS or type(b) is not bool or b not in B_LOCAL
        or energy not in ENERGY or food not in FOOD
        or water not in WATER or night not in NIGHTS):
        raise ValueError("unregistered factorial cell")
    identity=(
        f"a230zm:x{p[0]}y{p[1]}:b{int(b)}:energy{energy}:food{food}"
        f":water{water}:night{night}"
    )
    if (row["world_id"]!=identity
        or row["training_world_id"]!=identity
        or not isinstance(row["world_physics_sha256_external_only"],str)
        or len(row["world_physics_sha256_external_only"])!=64
        or len(row["world_layout_sha256_external_only"])!=64):
        raise ValueError("world or physical source identity falsified")
    root=visible(row["initial_firstperson"])
    back=visible(row["returned_firstperson"])
    if (row["firstperson_initial_sha256"]!=digest(root)
        or row["firstperson_return_sha256"]!=digest(back)
        or (root["x"],root["y"])!=p
        or row["same_coordinates_after_cycle"] is not True
        or row["same_visible_resources_after_cycle"] is not True
        or row["no_berry_B_ingestion"] is not True
        or row["no_postmortem_experience"] is not True
        or row["model_certifies_safety"] is not False
        or row["actual_i0_births"]!=0
        or row["actual_i0_autonomous_steps"]!=0
        or row["real_i0_UC_cost_measured"] is not False
        or row["no_stage6_shadow_action_dispatched"] is not True
        or row["old_transition_only_own_world_physical"] is not True
        or row["trained_examples"]!=4):
        raise ValueError("first-person root/body/agency/safety provenance corrupted")
    if root["is_night"] is not False:
        raise ValueError("initial daylight false, unpreregistered scenario")
    physical=row["all_four_physical_movements"]
    if len(physical)!=4:
        raise ValueError("motor return did not include four real physical examples")
    expected_positions=(
        p,(p[0]+1,p[1]),(p[0]+1,p[1]+1),(p[0],p[1]+1),p
    )
    state_chain=[root]
    training={}
    for idx,rec in enumerate(physical):
        ex=rec["physical_example"]
        before=visible(ex["state"])
        after=visible(ex["observed_next_state"])
        if (rec["step"]!=idx+1
            or rec["source_world"]!=identity
            or rec["physical_example_sha256"]!=digest(ex)
            or rec["command"]!=PATH[idx]
            or ex["command"]!=PATH[idx]
            or rec["state_before"]!=before
            or rec["state_after"]!=after
            or rec["terminal"] is not False
            or ex["terminal"] is not False
            or before!=state_chain[-1]):
            raise ValueError("physical receipt SHA or chronology corrupted")
        if ((before["x"],before["y"])!=expected_positions[idx]
            or (after["x"],after["y"])!=expected_positions[idx+1]):
            raise ValueError("motor loop coordinates inconsistent with four commands")
        # full body and is_night must be independently derivable at all
        # five observation times, not only at the initial/final snapshot.
        for candidate,t,coord in (
            (before,idx+1,expected_positions[idx]),
            (after,idx+2,expected_positions[idx+1]),
        ):
            expected_perception(
                candidate,coord,
                b_here=b,
                t=t,energy=energy,food=food,water=water,night=night,
            )
            actual_resource=(
                ["berry_b"] if b and coord==p else []
            )
            if candidate["current_resources"]!=actual_resource:
                raise ValueError("resource visible only at physical origin")
            for neighbor in candidate["adjacent"]:
                pos=(neighbor["x"],neighbor["y"])
                if neighbor["resources"]!=(
                    ["berry_b"] if b and pos==p else []
                ):
                    raise ValueError("adjacent cue inconsistent with stationary berry")
        k=key(before,PATH[idx])
        if k in training and (
            training[k]["observed_next_state"]!=after
            or training[k]["terminal"]!=ex["terminal"]
        ):
            raise ValueError("physically incompatible identical motor model inputs")
        training[k]=ex
        state_chain.append(after)
    if len(training)!=4 or state_chain[-1]!=back:
        raise ValueError("four own-world examples not complete and contiguous")
    if (back["x"],back["y"])!=p or back["inventory"]!=root["inventory"]:
        raise ValueError("same physical location or inventory not restored")
    expected_change={
        "energy":-4*energy,"food":-4*food,
        "water":-4*water,"integrity":0.0,
    }
    if any(abs(row["body_deltas_after_four_steps"][k]-v)>1e-9
           for k,v in expected_change.items()):
        raise ValueError("reported metabolic drift falsified")
    same=root==back
    positive=energy==0.0 and food==0.0 and water==0.0 and night==200
    if (same!=positive or row["full_firstperson_state_reentered"] is not same
        or row["first_move_exact_known_at_return"] is not same
        or row["old_first_step_input_sha256"]!=key(root,EAST)
        or row["new_first_step_input_sha256"]!=key(back,EAST)):
        raise ValueError("same geographic coordinates falsely treated as same full state")
    cand=candidate_commands(back)
    known_cand=sum(key(back,command) in training for command in cand)
    if (known_cand!=int(same)
        or (key(back,EAST) in training)!=same
        or EAST not in cand):
        raise ValueError("independent exact-root motor-edge count diverged")
    planner=row["planner_stage6_shadow"]
    if (planner["input_state_sha256"]!=digest(back)
        or planner["target_x"]!=p[0]+1
        or planner["target_y"]!=p[1]
        or planner["requested_goal"]!="one_step_spatial_east_only"
        or planner["not_a_food_goal"] is not True
        or planner["no_shadow_action_dispatched"] is not True
        or planner["no_B_ingestion_or_safety_claim"] is not True
        or planner["real_i0_uc_cost_measured"] is not False
        or planner["root_candidate_edges"]!=len(cand)
        or planner["root_available_edges"]!=known_cand
        or planner["root_unavailable_edges"]>
            planner["root_candidate_edges"]-known_cand
        or planner["root_unavailable_edges"]<0):
        raise ValueError("Stage6 root diagnostics or safety receipt fabricated")
    diag=planner["diagnostic"]
    if (diag["status"]!=planner["status"]
        or diag["root_candidate_edges"]!=planner["root_candidate_edges"]
        or diag["root_available_edges"]!=planner["root_available_edges"]
        or diag["root_unavailable_edges"]!=planner["root_unavailable_edges"]):
        raise ValueError("Stage6 root published count differs from diagnostic")
    if positive:
        prediction=planner["predictions"]
        if (planner["status"]!="plan_found"
            or planner["commands"]!=[EAST]
            or len(prediction)!=1
            or prediction[0]["command"]!=EAST
            or prediction[0]["next_state"]!=physical[0][
                "physical_example"]["observed_next_state"]
            or prediction[0]["terminal"] is not False
            or prediction[0]["confidence"]!=1.0
            or diag["root_model_diagnostic"]!="at_least_one_predictable_first_step"):
            raise ValueError("known spatial plan was not independently supported")
    else:
        if (planner["status"]!="incomplete_model"
            or planner["commands"] or planner["predictions"]
            or planner["root_unavailable_edges"]!=len(cand)
            or diag["root_model_diagnostic"]!="no_predictable_first_step"):
            raise ValueError("body/night drift invented a full-state prediction")
    fifth=row["precommitted_fifth_positive_physical_control"]
    if positive!=(fifth is not None):
        raise ValueError("fifth physical test cherry-picked after seeing outcome")
    if fifth is not None:
        ex=fifth["physical_example"]
        if (fifth["step"]!=5 or fifth["source_world"]!=identity
            or fifth["physical_example_sha256"]!=digest(ex)
            or ex["command"]!=EAST
            or ex["state"]!=back
            or ex["terminal"] is not False
            or fifth["observed_next_state"]!=ex["observed_next_state"]
            or fifth["predicted_next_state"]!=ex["observed_next_state"]
            or fifth["predicted_next_state"]!=planner["predictions"][0]["next_state"]
            or fifth["exact_prediction_equals_fifth_physical_outcome"] is not True
            or fifth["not_trained_on_fifth_action_before_prediction"] is not True):
            raise ValueError("physical fifth move does not validate prior exact prediction")
    return {
        "factor_key":fact,
        "body_or_night_changed":not same,
        "same_spatial_site":True,
        "exact_firstperson_reentry":same,
        "Stage6_root_exact_reuse":known_cand,
        "Stage6_spatial_plan_found":planner["status"]=="plan_found",
        "Stage6_incomplete":planner["status"]=="incomplete_model",
        "fifth_act_reproduced_prediction":fifth is not None,
        "physical_receipts_checked":4+int(fifth is not None),
        "night_context_changed":(night==3 and energy==0.0 and food==0.0 and water==0.0),
    }


def audit_all(rows,summary):
    if (len(rows)!=64 or summary.get("schema")!="a230zm-exact-firstperson-reentry-v1"
        or summary.get("code_sha")!=ORIGINAL_CODE_SHA
        or digest(rows)!=ORIGINAL_CANONICAL_WORLDS_SHA
        or summary.get("physical_worlds_sha256")!=ORIGINAL_CANONICAL_WORLDS_SHA
        or summary.get("real_physical_steps_total")!=260
        or summary.get("stage6_one_step_spatial_plans_found")!=4
        or summary.get("stage6_incomplete_model")!=60
        or summary.get("new_I0_births")!=0
        or summary.get("new_I0_autonomous_steps")!=0
        or summary.get("cognitive_deployment")!="NO-GO"
        or summary.get("real_I0_UC_measured") is not False):
        raise ValueError("locked physical ZM cohort/header tampered")
    observations=[audit_world(row) for row in rows]
    keys=[x["factor_key"] for x in observations]
    expected=set(product(POSITIONS,B_LOCAL,ENERGY,FOOD,WATER,NIGHTS))
    if set(keys)!=expected or len(set(keys))!=64:
        raise ValueError("missing or duplicated preregistered physical world")
    count=Counter()
    for w in observations:
        count["worlds"]+=1
        count["physical_receipts"]+=w["physical_receipts_checked"]
        count["exact_reentries"]+=w["exact_firstperson_reentry"]
        count["nonreentries"]+=w["body_or_night_changed"]
        count["spatial_plans"]+=w["Stage6_spatial_plan_found"]
        count["incomplete"]+=w["Stage6_incomplete"]
        count["fifth_outcomes"]+=w["fifth_act_reproduced_prediction"]
        count["night_only_changed"]+=w["night_context_changed"]
    if count!=Counter({
        "worlds":64,
        "physical_receipts":260,
        "exact_reentries":4,
        "nonreentries":60,
        "spatial_plans":4,
        "incomplete":60,
        "fifth_outcomes":4,
        "night_only_changed":4,
    }):
        raise ValueError("observed original physical root proof contradicts matrix")
    return {
        "schema":"a230zn-independent-sealed-exact-state-return-v1",
        "original_run":ORIGINAL_RUN,
        "original_source_code_sha":ORIGINAL_CODE_SHA,
        "original_physical_worlds_checked":count["worlds"],
        "original_motor_receipts_verified":count["physical_receipts"],
        "independent_root_search_counts_reconstructed":count["worlds"],
        "full_firstperson_reentries":count["exact_reentries"],
        "only_spatial_site_reentries":count["nonreentries"],
        "one_step_spatial_plans_supported":count["spatial_plans"],
        "incomplete_model_supported":count["incomplete"],
        "night_context_only_prevented_reuse":count["night_only_changed"],
        "actual_fifth_motor_outcomes_rechecked":count["fifth_outcomes"],
        "cross_python_archives_byte_identical":True,
        "ZG_or_ZK_corpses_ever_resurrected":False,
        "new_physical_worlds":0,
        "new_physical_steps":0,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "true_I0_UC_measured":False,
        "imported_stage6_or_worldbody_in_archive_reviewer":False,
        "model_safe_motor_generalization_proven":False,
        "no_food_ingestion_or_plan_proven":True,
        "stage12":"PARTIAL","issue110":"OPEN",
        "cognitive_deployment":"NO-GO",
    }


def execute(left,right,out):
    rows,source_summary,raw_sha=sealed_source(left,right)
    conclusion=audit_all(rows,source_summary)
    conclusion["original_binary_artifact_sha256"]=raw_sha
    conclusion["independent_reviewer_sha"]=subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True
    ).strip()
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230zn-independent-summary.json").write_text(
        json.dumps(conclusion,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZN_SUMMARY "+json.dumps(conclusion,sort_keys=True),flush=True)
    return conclusion


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-zm-311",type=Path,required=True)
    parser.add_argument("--original-zm-312",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    execute(args.original_zm_311,args.original_zm_312,args.output_dir)


if __name__=="__main__":
    main()
