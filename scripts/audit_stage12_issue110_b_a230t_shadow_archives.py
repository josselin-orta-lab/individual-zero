"""A2.30-T: independent read-only recalculation of frozen S-shadow archives.

No imports from S experiment runner, Stage6, Simulator, FrozenTableEquipment,
WorldBody or the Oracle. Observations, their source-time direction, and the
registered physical examples are audited from archived bytes. This is an
internal-consistency audit, NOT a new physical reproduction or I0 experience.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes,sha256_hex

ORIGINAL_S_RUN=38740664255
ORIGINAL_S_SHA="0046d8b2b30f44fe5e4fd0b4b165c88e724a8881"
EXPECTED_HASHES={
    "a230s-acted-worlds.json":
        "b905535a67c72b912e0b384dbc7e189e8446ee4954631e559928bd922edd0e36",
    "a230s-passive-worlds.json":
        "2863bb4e4d820cb3cc9b7492a0264e23f888e6b12e6225313f3c40766f8c27e6",
    "a230s-summary.json":
        "969de41c916df3210f8c9e0c1f033edc769bd49536f7fd20b14eaee03deee048",
}
FOODS=(40.0,45.0)
POSITIONS=((2,2),(4,4))
VARIANTS={
    "food":("benign","toxic_mild","toxic_lethal","exogenous_confounded"),
    "movement":("clear","danger_40","danger_55","lethal_east"),
}
FOLLOWUPS={"food":("wait","repeat_eat"),"movement":("wait","escape")}


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def from_archive(directory:Path):
    loaded={}
    for name,expected in EXPECTED_HASHES.items():
        files=list(directory.rglob(name))
        if len(files)!=1:
            raise ValueError("original S artifact is missing or ambiguous: "+name)
        raw=files[0].read_bytes()
        if sha256(raw).hexdigest()!=expected:
            raise ValueError("original S SHA-256 changed: "+name)
        loaded[name]=raw
    return loaded


def candidate_commands(state):
    """Independent enumeration of the visible Stage6 root action alphabet."""
    results=[]
    for n in state["adjacent"]:
        if n["passable"]:
            results.append({
                "primitive":"se_deplacer",
                "parameters":{"direction":n["direction"]},
            })
    for target in sorted(set(state["current_resources"])):
        results.append({
            "primitive":"collecter","parameters":{"target":target},
        })
    for berry in ("berry_a","berry_b"):
        if state["inventory"].get(berry,0)>0:
            results.append({
                "primitive":"manger","parameters":{"target":berry},
            })
    if state["current_water_source"]:
        results.append({"primitive":"boire","parameters":{}})
    if state["inventory"].get("stone",0)>0:
        results.append({"primitive":"poser_une_pierre","parameters":{}})
    if (state["inventory"].get("wood",0)>0 and
        state["inventory"].get("stone",0)>0):
        results.append({"primitive":"fabriquer_outil","parameters":{}})
    results.append({"primitive":"dormir","parameters":{}})
    results.append({"primitive":"attendre","parameters":{}})
    return results


def validate_shadow(world,query):
    if world["kind"]!="food":
        raise ValueError("movement should never feed shadow planner")
    t=query["t_query"]
    if t not in (3,4) or (t==4 and world["first_terminal_step"] is not None):
        raise ValueError("Stage6 used terminal or unregistered future state")
    prefix=world["physical_records"][:t-1]
    if (query["previous_observed_steps"]!=list(range(1,t))
        or query["history_examples_count"]!=len(prefix)
        or query["model_kind"]!="own_past_firstperson_only_exact_shadow"
        or query["food_goal_setpoint"]!=65.0
        or (query["h_eff"],query["r_eff"],query["max_depth"])!=(3,1,3)
        or query["no_shadow_command_dispatched"] is not True):
        raise ValueError("Stage6 shadow model crossed the causal time boundary")
    seen=[record["physical_example"] for record in prefix]
    corpus={
        "version":f"a230s-shadow-history-{world['id']}-t{t}",
        "examples":seen,
    }
    if digest(corpus)!=query["history_corpus_sha256"]:
        raise ValueError("shadow history corpus includes future or wrong source")
    snapshot=prefix[-1]["state_after"]
    if digest(snapshot)!=query["snapshot_input_sha256"]:
        raise ValueError("shadow planner initial state is not last accessible state")
    if float(snapshot["body"]["food"])>=65.0:
        raise ValueError("shadow target already satisfied unexpectedly")
    known_inputs={
        digest({"state":x["state"],"command":x["command"]})
        for x in seen
    }
    commands=candidate_commands(snapshot)
    known=sum(
        digest({"state":snapshot,"command":action}) in known_inputs
        for action in commands
    )
    unavailable=len(commands)-known
    d=query["stage6_diagnostic"]
    if (query["stage6_root_candidate_edges"]!=len(commands)
        or query["stage6_root_available_edges"]!=known
        or query["stage6_root_unavailable_edges"]!=unavailable
        or d["root_candidate_edges"]!=len(commands)
        or d["root_available_edges"]!=known
        or d["root_unavailable_edges"]!=unavailable):
        raise ValueError("independent root known/action count disagrees with shadow")
    if known==0:
        if (query["stage6_status"]!="incomplete_model"
            or query["stage6_commands_only_proposed"]!=[]
            or query["stage6_expanded_states"]!=1
            or query["stage6_unavailable_edges"]!=len(commands)
            or d!={
                "status":"incomplete_model","expanded_states":1,
                "unavailable_edges":len(commands),"partial_progress":False,
                "root_candidate_edges":len(commands),"root_available_edges":0,
                "root_unavailable_edges":len(commands),
                "root_model_diagnostic":"no_predictable_first_step",
            }):
            raise ValueError("unknown Stage6 root misrepresented as found plan")
    else:
        # A known root requires an actual planner-path audit; never assume
        # the lack of a plan from this independent root-only calculation.
        raise ValueError("outside preregistered root-zero proof domain")
    return {"known":known,"candidates":len(commands),
            "before":t==3,"after":t==4}


def validate_physical_world(row):
    kind=row["kind"]
    if (kind not in VARIANTS
        or row["variant_lab_only"] not in VARIANTS[kind]
        or row["followup_precommitted"] not in FOLLOWUPS[kind]
        or row["initial_food"] not in FOODS
        or tuple(row["initial_position"]) not in POSITIONS
        or row["id"]!=(
            f"a230s:{kind}:{row['variant_lab_only']}:"
            f"{row['followup_precommitted']}:f{int(row['initial_food'])}:"
            f"x{row['initial_position'][0]}y{row['initial_position'][1]}"
        )):
        raise ValueError("nonpreregistered scenario/world identifier")
    if (row["new_I0_birth"] is not False or row["shadow_only"] is not True
        or row["oracle_information_in_cognitive_search"] is not False
        or len(row["config_sha256"])!=64
        or len(row["layout_sha256"])!=64):
        raise ValueError("untrusted physical/world cognitive provenance")
    steps=row["physical_records"]
    if not steps or row["physical_step_count"]!=len(steps):
        raise ValueError("wrong counted WorldBody physical steps")
    if row["initial_accessible"]!=steps[0]["state_before"]:
        raise ValueError("physical first-person birth state mismatch")
    if digest(row["initial_accessible"])!=row["initial_accessible_sha256"]:
        raise ValueError("first accessible observation SHA corrupted")
    terminal_steps=[]
    for index,item in enumerate(steps,1):
        ex=item["physical_example"]
        if (item["step"]!=index
            or item["command"]!=row["intended_prefix"][index-1]
            or ex["command"]!=item["command"]
            or ex["family"]!="laboratory_firstperson_"+kind
            or item["state_before"]!=ex["state"]
            or item["state_after"]!=ex["observed_next_state"]
            or item["terminal"]!=ex["terminal"]
            or item["physical_example_sha256"]!=digest(ex)):
            raise ValueError("physical example/command SHA mismatch")
        if index>1 and item["state_before"]!=steps[index-2]["state_after"]:
            raise ValueError("noncontiguous first-person transition sequence")
        if ex["terminal"]:
            terminal_steps.append(index)
    actual_terminal=terminal_steps[0] if terminal_steps else None
    if (len(terminal_steps)>1 or
        (actual_terminal is not None and actual_terminal!=len(steps))
        or row["first_terminal_step"]!=actual_terminal
        or (actual_terminal is None and len(steps)!=len(row["intended_prefix"]))):
        raise ValueError("postterminal future, false death or premature stop")
    if kind=="food":
        if len(row["shadow_food"])!=(1 if actual_terminal is not None else 2):
            raise ValueError("postdeath/omitted Stage6 shadow sample")
        if row["first_eat_accessible_before_hidden_event"]!=steps[2]["state_before"]:
            raise ValueError("exogenous event became visible before eating")
        if row["variant_lab_only"]=="exogenous_confounded":
            events=row["external_environment_interventions"]
            if (len(events)!=1 or events[0]!={
                "between_physical_steps":[2,3],
                "world_event":"set_danger_zone",
                "position":{"x":row["initial_position"][0],
                            "y":row["initial_position"][1]},
                "active":True,
                "not_an_i0_command":True,
                "not_visible_in_capture":True,
            } or row["hidden_event_changed_capture"] is not False):
                raise ValueError("wrong hidden intervention or leakage")
        elif (row["external_environment_interventions"]!=[]
              or row["hidden_event_changed_capture"] is not None):
            raise ValueError("invented causal external intervention")
        samples=[validate_shadow(row,q) for q in row["shadow_food"]]
    else:
        if (row["shadow_food"] or
            row["external_environment_interventions"]
            or row["first_eat_accessible_before_hidden_event"] is not None):
            raise ValueError("movement data incorrectly fed food shadow")
        samples=[]
    return {"world_id":row["id"],"kind":kind,"variant":row["variant_lab_only"],
            "followup":row["followup_precommitted"],
            "food":row["initial_food"],
            "position":tuple(row["initial_position"]),
            "physical_steps":len(steps),
            "terminal_step":actual_terminal,"food_shadow":samples}


def audit_independent(acted,passive,summary):
    if (summary.get("schema")!="a230s-firstperson-controlled-information-v1"
        or summary.get("analysis_code_sha")!=ORIGINAL_S_SHA
        or summary.get("new_I0_births")!=0
        or summary.get("new_I0_autonomous_steps")!=0
        or summary.get("not_deployable_to_I0") is not True):
        raise ValueError("not preregistered S source or false deployment claim")
    if len(acted)!=64 or len(passive)!=8:
        raise ValueError("S scientific cohort incomplete")
    records=[]
    IDs=set()
    indexed={}
    total=0
    for row in acted:
        info=validate_physical_world(row)
        if info["world_id"] in IDs:
            raise ValueError("scientific world ID repeated")
        IDs.add(info["world_id"])
        records.append(info)
        indexed[(info["kind"],info["variant"],info["followup"],
                 info["food"],info["position"])]=row
        total+=info["physical_steps"]
    passive_counts=Counter()
    for row in passive:
        if row["id"] in IDs or row["world_steps_applied"]!=0:
            raise ValueError("passive world duplicated or physically acted")
        IDs.add(row["id"])
        kind=row["cue_kind"]
        if kind=="food_resource_visible":
            actual="berry_a" in row["capture"]["current_resources"]
        elif kind=="movement_obstacle_visible":
            actual=not next(c["passable"] for c in row["capture"]["adjacent"]
                           if c["direction"]=="east")
        else:
            raise ValueError("unknown passive control")
        if (actual!=row["intended_visible_indicator"]
            or actual!=row["detected_from_accessible_state"]):
            raise ValueError("passive visible control gave false knowledge")
        passive_counts[kind]+=1
    if (len(IDs),total,passive_counts)!=(
        72,196,Counter({
            "food_resource_visible":4,
            "movement_obstacle_visible":4,
        })):
        raise ValueError("wrong passive/physical counts")
    ambiguous=0
    waiting=0
    repeated=0
    first_move_equal=0
    hazardous_wait_terminal=0
    escaping_survives=0
    for food in FOODS:
        for pos in POSITIONS:
            for followup in FOLLOWUPS["food"]:
                mild=indexed[("food","toxic_mild",followup,food,pos)]
                conf=indexed[("food","exogenous_confounded",followup,food,pos)]
                a=mild["physical_records"][2]
                c=conf["physical_records"][2]
                if (a["state_before"]!=c["state_before"]
                    or a["command"]!=c["command"]
                    or a["state_after"]!=c["state_after"]
                    or a["terminal"]!=c["terminal"]):
                    raise ValueError("claimed causal aliasing was false")
                ambiguous+=1
                last_a=mild["physical_records"][3]["state_after"]
                last_c=conf["physical_records"][3]["state_after"]
                if followup=="wait":
                    if (last_a["body"]["integrity"]!=93
                        or last_c["body"]["integrity"]!=86):
                        raise ValueError("inconclusive/costless wait claimed informative")
                    waiting+=1
                else:
                    if last_a!=last_c:
                        raise ValueError("repeat eating distinguished causes unexpectedly")
                    repeated+=1
            for variant in VARIANTS["movement"]:
                a=indexed[("movement",variant,"wait",food,pos)]
                c=indexed[("movement",variant,"escape",food,pos)]
                if a["physical_records"][0]!=c["physical_records"][0]:
                    raise ValueError("paired movement early effects differ")
                first_move_equal+=1
                if variant in ("danger_40","danger_55"):
                    if (a["first_terminal_step"] is None
                        or c["first_terminal_step"] is not None):
                        raise ValueError("physical retreat counterfactual invalid")
                    hazardous_wait_terminal+=1
                    escaping_survives+=1
    shadows=[s for r in records for s in r["food_shadow"]]
    before=sum(x["before"] for x in shadows)
    after=sum(x["after"] for x in shadows)
    statuses=Counter(q["stage6_status"] for x in acted for q in x["shadow_food"])
    deaths=Counter(x["kind"] for x in records if x["terminal_step"] is not None)
    ingestions=sum(
        item["command"]["primitive"]=="manger"
        for row in acted for item in row["physical_records"]
    )
    measurements={
        "acted_detached_worlds":64,
        "passive_observation_only_worlds":8,
        "independent_lab_world_instances":len(IDs),
        "actual_lab_physical_steps":total,
        "food_physical_steps":sum(x["physical_steps"] for x in records
                                  if x["kind"]=="food"),
        "movement_physical_steps":sum(x["physical_steps"] for x in records
                                      if x["kind"]=="movement"),
        "actually_executed_eat_commands":ingestions,
        "physically_terminal_worlds":dict(deaths),
        "shadow_stage6_queries":len(shadows),
        "shadow_food_before_first_ingestion_queries":before,
        "shadow_food_after_first_ingestion_queries":after,
        "shadow_stage6_statuses":dict(statuses),
        "shadow_no_predictable_first_step":sum(x["known"]==0 for x in shadows),
        "shadow_first_step_known":sum(x["known"]>0 for x in shadows),
    }
    for key,value in measurements.items():
        if summary.get(key)!=value:
            raise ValueError("S summary vs first-person evidence mismatch: "+key)
    comparisons={
        "paired_food_first_ingestion_same_accessible_input":ambiguous,
        "paired_food_after_ingestion_identical_accessible_output":ambiguous,
        "mild_toxin_vs_exogenous_wait_distinguished":waiting,
        "mild_toxin_vs_exogenous_repeat_eat_still_indistinguishable":repeated,
        "movement_paired_equal_first_step_outcomes":first_move_equal,
        "hazardous_wait_future_terminal_worlds":hazardous_wait_terminal,
        "paired_precommitted_retreat_survives":escaping_survives,
        "does_not_identify_individual_subjective_cause":True,
    }
    if comparisons!=summary["comparison"]:
        raise ValueError("S confounding or spatial counterfactual was falsified")
    if (measurements["shadow_stage6_queries"]!=56
        or measurements["shadow_no_predictable_first_step"]!=56
        or ingestions!=44 or deaths!={"food":8,"movement":16}):
        raise ValueError("unexpected original S result outside audit domain")
    return {
        "schema":"stage12-a230t-independent-s-shadow-archive-v1",
        "original_S_run":ORIGINAL_S_RUN,
        "original_S_code_sha":ORIGINAL_S_SHA,
        "original_worlds_archived":72,
        "original_physical_steps_archived":196,
        "new_independent_worlds":0,
        "new_physical_steps":0,
        "new_I0_births":0,
        "all_original_56_shadow_root_proofs_recomputed":True,
        "external_shadow_plan_status":"incomplete_model",
        "paired_causal_aliases":ambiguous,
        "discriminating_waits":waiting,
        "uninformative_second_ingestions":repeated,
        "precommitted_retreated_survivors":escaping_survives,
        "oracular_knowledge_in_shadow":False,
        "Stage6_cognitive_change_deployed":False,
        "WorldBody_physics_independently_replayed":False,
        "stage12":"PARTIAL",
        "metrics":measurements,
    }


def execute(dir_a:Path,dir_b:Path,out:Path):
    a=from_archive(dir_a)
    b=from_archive(dir_b)
    if a!=b:
        raise ValueError("Python 3.11 and 3.12 original S outputs differ")
    audit=audit_independent(
        json.loads(a["a230s-acted-worlds.json"]),
        json.loads(a["a230s-passive-worlds.json"]),
        json.loads(a["a230s-summary.json"]),
    )
    audit.update({
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "source_json_sha256":EXPECTED_HASHES,
        "original_python_archives_identical_bytes":True,
    })
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230t-summary.json").write_text(
        json.dumps(audit,indent=2,sort_keys=True)+"\n"
    )
    print("A230T_SUMMARY "+json.dumps({
        k:v for k,v in audit.items() if k not in ("metrics","source_json_sha256")
    },sort_keys=True),flush=True)
    return audit


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-311",required=True,type=Path)
    ap.add_argument("--source-312",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    args=ap.parse_args()
    execute(args.source_311,args.source_312,args.output_dir)


if __name__=="__main__":
    main()
