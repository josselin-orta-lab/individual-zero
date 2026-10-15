"""A2.30-X: independent read-only audit of ORIGINAL W archives.

No import of W runner, WorldBody, Stage6, Oracle, Bench or predictor. This
module cannot prove WorldBody.apply actually happened: it verifies the
recorded action/perception chains and bounded claims against sealed data.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

ORIGINAL_W_RUN = 38753518412
ORIGINAL_W_SHA = "aecb8d1172846620c3038a4bc10e7716ec7bde1e"
ARCHIVE_HASHES = {
    "a230w-acted-physical-worlds.json":
        "999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889",
    "a230w-passive-positive-controls.json":
        "dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666",
    "a230w-summary.json":
        "859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9",
}
ACTUAL_FOODS = (35.0,45.0)
ACTUAL_POSITIONS = ((5,5),(7,7))
LATENT_BENCH_LABELS = {
    "benign", "toxin_7", "toxin_30", "toxin_100", "gain_zero",
}
PROBE_NAMES = ("immediate","wait_twice","collect_first","west_return")
PROBE_PRESETS = {
    "immediate":[],
    "wait_twice":[("attendre",{}),("attendre",{})],
    "collect_first":[("collecter",{"target":"berry_a"})],
    "west_return":[
        ("se_deplacer",{"direction":"west"}),
        ("se_deplacer",{"direction":"east"}),
    ],
}
EXPECTED_COSTS = {
    "immediate":(0.0,0.0,0.0,0.0),
    "wait_twice":(-1.0,-1.0,-0.4,0.0),
    "collect_first":(-0.75,-0.5,-0.2,0.0),
    "west_return":(-2.0,-1.0,-0.4,0.0),
}
ACCEPTABLE_STATE_KEYS = {
    "schema_version","x","y","body","inventory",
    "current_water_source","current_resources","adjacent",
    "known_shelter_here","is_night",
}
BODY_KEYS=("energy","food","water","integrity")


def hash_object(x):
    return sha256_hex(canonical_causal_bytes(x))


def validate_state(state):
    if (not isinstance(state,dict) or set(state)!=ACCEPTABLE_STATE_KEYS
        or set(state["body"])!=set(BODY_KEYS)
        or set(state["inventory"])!={
            "berry_a","berry_b","wood","stone","tool"
        }
        or state["schema_version"]!="stage6-simulation-state-v1"):
        raise ValueError("non-first-person field in accessible state")
    if not isinstance(state["adjacent"],list) or len(state["adjacent"])!=4:
        raise ValueError("bad authorized local perception")
    directions=set()
    for n in state["adjacent"]:
        if set(n)!={"creature","direction","passable","resources",
                     "water_source","x","y"}:
            raise ValueError("latent or nonperceptible adjacent field")
        if n["direction"] in directions:
            raise ValueError("duplicate adjacent direction")
        directions.add(n["direction"])
    if directions!={"north","south","east","west"}:
        raise ValueError("not four visible neighbors")


def history_key(recorded):
    """Alternate pure-data representation to reconstruct equivalence classes."""
    if not isinstance(recorded,list) or not recorded:
        raise ValueError("missing preregistered history")
    for time,frame in enumerate(recorded,1):
        if (set(frame)!={"state","t_monde"} or frame["t_monde"]!=time):
            raise ValueError("future observation inserted before decision")
        validate_state(frame["state"])
    return json.dumps(recorded,sort_keys=True,separators=(",",":"))


def from_sealed_zip_extract(root):
    decoded={}
    for file,expected in ARCHIVE_HASHES.items():
        hits=list(Path(root).rglob(file))
        if len(hits)!=1:
            raise ValueError("source missing or ambiguous "+file)
        raw=hits[0].read_bytes()
        if sha256(raw).hexdigest()!=expected:
            raise ValueError("original source SHA mismatch "+file)
        decoded[file]=raw
    return decoded


def rebuild(acted,control,original_summary):
    """Every metric independently rebuilt from original per-step data."""
    if (len(acted)!=80 or len(control)!=12
        or original_summary.get("schema")!="a230w-prospective-unobservable-food-risk-v1"
        or original_summary.get("sha_of_analysis_code")!=ORIGINAL_W_SHA
        or original_summary.get("new_i0_births")!=0
        or original_summary.get("new_i0_autonomous_steps")!=0
        or original_summary.get("can_deploy_predictor") is not False):
        raise ValueError("incorrect immutable W cohort or source identity")

    seen=set()
    history_groups=defaultdict(list)
    per_probe=Counter()
    physical_steps=0
    probe_steps=0
    physical_terminals=0
    physical_successes=0
    physical_insufficient=0
    probe_costs=defaultdict(set)
    for sample in acted:
        probe=sample["probe"]
        variant=sample["latent_external_bench_only"]
        food=sample["initial_food"]
        pos=tuple(sample["initial_position"])
        world_id=sample["world_id"]
        if (world_id in seen or probe not in PROBE_NAMES
            or variant not in LATENT_BENCH_LABELS or food not in ACTUAL_FOODS
            or pos not in ACTUAL_POSITIONS or world_id!=(
                f"a230w:{probe}:{variant}:food{int(food)}:x{pos[0]}y{pos[1]}"
            )):
            raise ValueError("duplicate/unregistered physical world")
        seen.add(world_id)
        history=sample["predecision_lived_history"]
        hkey=history_key(history)
        if (len(history)!=len(PROBE_PRESETS[probe])+1
            or hash_object(history)!=sample["predecision_history_sha256"]
            or history[-1]["state"]!=sample["decision_state"]
            or hash_object(sample["decision_state"])!=sample["decision_state_sha256"]
            or sample["no_i0_instance_or_autonomous_command"] is not True
            or sample["no_oracle_feedback_to_i0"] is not True
            or sample["certifies_safe_from_probe"] is not False):
            raise ValueError("foreign future knowledge or fake safety before food")
        recipe=PROBE_PRESETS[probe]+(
            [("manger",{"target":"berry_a"})] if probe=="collect_first"
            else [("collecter",{"target":"berry_a"}),
                  ("manger",{"target":"berry_a"})]
        )
        steps=sample["physical_commands_and_receipts_external_only"]
        if (len(steps)!=len(recipe)
            or sample["physical_total_steps"]!=len(recipe)
            or sample["physical_probe_steps"]!=len(PROBE_PRESETS[probe])):
            raise ValueError("altered preregistered physical action chronology")
        previous=history[0]["state"]
        for step,(row,command) in enumerate(zip(steps,recipe),1):
            if (row["t_monde"]!=step
                or row["phase"]!=(
                    "preexposure_probe" if step<=len(PROBE_PRESETS[probe])
                    else "external_food_outcome_only"
                )
                or row["command"]!={"primitive":command[0],
                                    "parameters":command[1]}
                or row["sha256"]!=hash_object({
                    k:v for k,v in row.items() if k!="sha256"
                })
                or row["before"]!=previous):
                raise ValueError("forged or noncontiguous physical world receipt")
            validate_state(row["after_for_external_bench"])
            if row["terminal_external_only"] and step!=len(steps):
                raise ValueError("physical action continued after death")
            if step<=len(PROBE_PRESETS[probe]):
                if (row["terminal_external_only"]
                    or history[step]["state"]!=row["after_for_external_bench"]):
                    raise ValueError("hidden lethal exposure in purported safe probe")
            previous=row["after_for_external_bench"]
        died=steps[-1]["terminal_external_only"]
        if (sample["physical_terminal_step_external_only"]!=(
                len(steps) if died else None)
            or sample["physically_alive_after_ingestion"] is died
            or sample["postterminal_lived_capture_count"]!=0
            or sample["lived_post_ingestion_if_survivor"]!=(
                None if died else previous
            )):
            raise ValueError("physical mortality improperly experienced as lived")
        # The hidden label here is a BENCH RECEIPT CONSISTENCY CHECK, not
        # included in hkey or any predicted action.
        harmful=round(float(
            previous["body"]["integrity"]-
            steps[-1]["before"]["body"]["integrity"]
        ),8)
        expected_harm={
            "benign":0.0,"toxin_7":-7.0,"toxin_30":-30.0,
            "toxin_100":-100.0,"gain_zero":0.0,
        }[variant]
        if harmful!=expected_harm:
            raise ValueError("original hidden effect contradicts physical output")
        actual_gain=round(float(
            previous["body"]["food"]-
            sample["decision_state"]["body"]["food"]
        ),8)
        success=not died and actual_gain>=5.0
        if (abs(actual_gain-
                sample["physical_food_gain_from_predecision_external_only"])
                >1e-8 or success is not
                sample["physical_food_goal_and_survival_external_only"]):
            raise ValueError("physical food success label was fabricated")
        probe_delta=tuple(round(float(
            sample["decision_state"]["body"][field]-
            history[0]["state"]["body"][field]
        ),8) for field in BODY_KEYS)
        if (probe_delta!=EXPECTED_COSTS[probe] or
            sample["physical_probe_effect"]!=dict(zip(BODY_KEYS,probe_delta))):
            raise ValueError("recomputed bodily probe acquisition cost changed")
        probe_costs[probe].add(probe_delta)
        physical_steps+=len(steps)
        probe_steps+=len(PROBE_PRESETS[probe])
        per_probe[(probe,"worlds")]+=1
        per_probe[(probe,"actions")]+=len(steps)
        per_probe[(probe,"probe_actions")]+=len(PROBE_PRESETS[probe])
        if died:
            physical_terminals+=1
            per_probe[(probe,"terminal")]+=1
        elif success:
            physical_successes+=1
            per_probe[(probe,"success")]+=1
        else:
            physical_insufficient+=1
            per_probe[(probe,"insufficient")]+=1
        history_groups[(probe,hkey)].append({
            "world_id":world_id,"variant":variant,
            "food_success":success,"terminal":died,
        })

    if (len(history_groups)!=16 or physical_steps!=240
        or probe_steps!=100 or physical_terminals!=16
        or physical_successes!=48 or physical_insufficient!=16):
        raise ValueError("independent first-person cohort totals differ")
    for probe in PROBE_NAMES:
        if (tuple(per_probe[(probe,k)] for k in
                  ("worlds","success","terminal","insufficient"))
            !=(20,12,4,4) or probe_costs[probe]!={EXPECTED_COSTS[probe]}):
            raise ValueError("preregistered physical contrast or costs diverged")
    total_identical_pairs=0
    for (probe,hkey),group in history_groups.items():
        if (len(group)!=5 or {x["variant"] for x in group}
            !=LATENT_BENCH_LABELS):
            raise ValueError("incomplete matched latent-family observable history")
        if (sum(x["food_success"] for x in group)!=3 or
            sum(x["terminal"] for x in group)!=1):
            raise ValueError("same perceived history no longer conflicts")
        total_identical_pairs+=10
    if total_identical_pairs!=160:
        raise ValueError("pairwise matched causal witness count differs")

    # Positive controls are reconstructed from first-person state fields;
    # hidden physics is NOT a feature and cannot be a food safety label.
    visible=defaultdict(dict)
    for row in control:
        loc=(row["food"],tuple(row["position"]))
        v=row["control"]
        id_=row["world_id"]
        if (id_ in seen or row["food"] not in ACTUAL_FOODS
            or loc[1] not in ACTUAL_POSITIONS
            or v not in ("resource_berry_a","resource_berry_b","west_blocked")
            or row["physical_steps"]!=0
            or row["no_food_safety_claim"] is not True
            or row["visible_state_sha256"]!=hash_object(row["visible_state"])
            or id_!=f"a230w-control:{v}:food{int(row['food'])}:"
                    f"x{loc[1][0]}y{loc[1][1]}"):
            raise ValueError("forged visible control or its signature")
        if v in visible[loc]:
            raise ValueError("duplicate visible condition")
        validate_state(row["visible_state"])
        seen.add(id_)
        visible[loc][v]=row["visible_state"]
    if len(visible)!=4 or len(seen)!=92:
        raise ValueError("positive controls/world identity count corrupted")
    positive_species=0
    positive_obstacles=0
    for root,triplet in visible.items():
        if set(triplet)!={"resource_berry_a","resource_berry_b","west_blocked"}:
            raise ValueError("positive controls missing at a visible state")
        benign=triplet["resource_berry_a"]
        alternative=triplet["resource_berry_b"]
        blocked=triplet["west_blocked"]
        if (benign["current_resources"]!=["berry_a"]
            or alternative["current_resources"]!=["berry_b"]
            or benign["body"]!=alternative["body"]
            or benign["current_resources"]!=blocked["current_resources"]
            or benign["body"]!=blocked["body"]):
            raise ValueError("visible positive resource distinction disappeared")
        def west_passable(s):
            return next(n["passable"] for n in s["adjacent"]
                        if n["direction"]=="west")
        if not west_passable(benign) or west_passable(blocked):
            raise ValueError("visible obstacle positive control no longer works")
        positive_species+=int(benign!=alternative)
        positive_obstacles+=int(benign!=blocked)
    if (positive_species,positive_obstacles)!=(4,4):
        raise ValueError("visible positive control discrimination missing")
    # Exhaustive enumeration independent of the W producer's scoring.
    safe_count=0
    safe_positive_count=0
    count=0
    for policy in product((0,1),repeat=len(history_groups)):
        count+=1
        chosen=sum(policy)
        # Each chosen observable context is linked to one fatal physical
        # alternative, three surviving food goals and one insufficient case.
        fatal_worlds=chosen
        food_goal_worlds=3*chosen
        if fatal_worlds==0:
            safe_count+=1
            if food_goal_worlds>0:
                safe_positive_count+=1
    if (count,safe_count,safe_positive_count)!=(65536,1,0):
        raise ValueError("bounded physical policy certificate no longer holds")
    score={
        "schema":"a230x-independent-W-archive-witness-v1",
        "source_original_run":ORIGINAL_W_RUN,
        "source_original_sha":ORIGINAL_W_SHA,
        "sealed_physical_actions_checked":physical_steps,
        "original_acted_worlds":len(acted),
        "original_passive_visible_worlds":len(control),
        "recomputed_observation_classes":len(history_groups),
        "recomputed_indistinguishable_hidden_pairs":total_identical_pairs,
        "new_worlds_executed":0,
        "new_physical_steps_executed":0,
        "external_deaths_checked":physical_terminals,
        "surviving_food_goals_checked":physical_successes,
        "surviving_insufficient_food_checked":physical_insufficient,
        "positive_visible_species_differences":positive_species,
        "positive_visible_obstacle_differences":positive_obstacles,
        "finite_deterministic_policies":count,
        "finite_zero_death_policies":safe_count,
        "finite_zero_death_and_food_policies":safe_positive_count,
        "probe_cost_per_world":{
            name:dict(zip(BODY_KEYS,next(iter(probe_costs[name]))))
            for name in PROBE_NAMES
        },
        "stages":{probe:{
            "worlds":per_probe[(probe,"worlds")],
            "original_physical_actions":per_probe[(probe,"actions")],
            "original_probe_actions":per_probe[(probe,"probe_actions")],
            "surviving_food_goals":per_probe[(probe,"success")],
            "terminals":per_probe[(probe,"terminal")],
            "insufficient_food":per_probe[(probe,"insufficient")],
        } for probe in PROBE_NAMES},
        "oracle_feedback_to_i0":False,
        "can_infer_general_safe_foraging_policy":False,
        "physical_application_proven_from_archives_alone":False,
        "real_i0_subjective_agency_measured":False,
        "stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
    }
    claims={
        "actually_applied_worldbody_steps":physical_steps,
        "external_terminal_ingestions":physical_terminals,
        "fully_committed_food_successes":physical_successes,
        "fully_committed_insufficient_results":physical_insufficient,
        "preexposure_observation_equivalence_classes":len(history_groups),
        "hidden_cause_pairs_same_first_person_history":total_identical_pairs,
        "hidden_cause_pairs_separated_before_ingestion":0,
        "positive_visible_berry_kind_differences":positive_species,
        "positive_visible_obstacle_differences":positive_obstacles,
        "bounded_deterministic_policies_enumerated":count,
        "zero_death_policies_in_bounded_domain":safe_count,
        "zero_death_and_positive_food_policies":safe_positive_count,
    }
    for key,value in claims.items():
        if original_summary.get(key)!=value:
            raise ValueError("W aggregate source claim disagrees with independent audit: "+key)
    return score


def execute(a,b,out):
    x=from_sealed_zip_extract(a)
    y=from_sealed_zip_extract(b)
    if x!=y:
        raise ValueError("two original Python runs disagree in recorded JSON bytes")
    data={key:json.loads(value) for key,value in x.items()}
    score=rebuild(
        data["a230w-acted-physical-worlds.json"],
        data["a230w-passive-positive-controls.json"],
        data["a230w-summary.json"],
    )
    score.update({
        "analysis_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "original_source_file_hashes":ARCHIVE_HASHES,
        "python_311_312_original_archives_byte_identical":True,
    })
    out.mkdir(parents=True,exist_ok=False)
    (out/"a230x-summary.json").write_text(
        json.dumps(score,sort_keys=True,indent=2)+"\n"
    )
    print("A230X_SUMMARY "+json.dumps(score,sort_keys=True),flush=True)
    return score


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-py311",type=Path,required=True)
    p.add_argument("--original-py312",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    execute(args.original_py311,args.original_py312,args.output_dir)


if __name__=="__main__":
    main()
