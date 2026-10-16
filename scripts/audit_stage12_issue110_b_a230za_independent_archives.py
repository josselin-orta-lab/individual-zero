"""A2.30-ZA independent audit of sealed Z first-person and Stage6 archives.

No WorldBody, I0 runtime, Stage6 planner, Equipment trainer, experiment
runner or Oracle import. Rebuild candidate commands, empirical exact root
keys and temporal policy decisions from original accessible JSON fields.
This is an archive consistency audit, NOT a physical replay or new cohort.
Preregistration committed dd c2cfe before this audit implementation.
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

ORIGINAL_Z_SHA = "0d9fd7cd511640103498f037b84cae915169356e"
ORIGINAL_Z_RUN = 38760713470
ARCHIVE_SHA = {
    "a230z-physical-worlds.json":
        "09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d",
    "a230z-summary.json":
        "170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c",
}
LAYOUTS = (
    "A_ONLY","B_LOCAL","B_EAST_BLOCKED",
    "B_EAST_ADJACENT","B_EAST_TWO_STEPS",
)
PROTOCOLS = ("OBSERVED_ONLY","SINGLE_EAST_PROBE")
FOODS = (35.0,45.0)
POSITIONS = ((5,5),(7,7))
A_VARIANTS = ("benign","toxin_7","toxin_30","toxin_100","gain_zero")
B_VARIANTS = ("benign","toxin_7","toxin_100","gain_zero")
EXPECTED_ARM = {
    ("A_ONLY","OBSERVED_ONLY"):(20,0),
    ("A_ONLY","SINGLE_EAST_PROBE"):(20,20),
    ("B_LOCAL","OBSERVED_ONLY"):(16,32),
    ("B_LOCAL","SINGLE_EAST_PROBE"):(16,32),
    ("B_EAST_BLOCKED","OBSERVED_ONLY"):(16,0),
    ("B_EAST_BLOCKED","SINGLE_EAST_PROBE"):(16,0),
    ("B_EAST_ADJACENT","OBSERVED_ONLY"):(16,48),
    ("B_EAST_ADJACENT","SINGLE_EAST_PROBE"):(16,48),
    ("B_EAST_TWO_STEPS","OBSERVED_ONLY"):(16,0),
    ("B_EAST_TWO_STEPS","SINGLE_EAST_PROBE"):(16,64),
}
ACCESSIBLE = {
    "schema_version","x","y","body","inventory",
    "current_water_source","current_resources","adjacent",
    "known_shelter_here","is_night",
}
BODY_KEYS = {"energy","food","water","integrity"}
INV_KEYS = {"berry_a","berry_b","wood","stone","tool"}


def digest(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def read_original(root: Path) -> dict[str,bytes]:
    sealed={}
    for name, expected in ARCHIVE_SHA.items():
        paths=list(root.rglob(name))
        if len(paths)!=1:
            raise ValueError("historical JSON missing or ambiguously nested: "+name)
        raw=paths[0].read_bytes()
        if sha256(raw).hexdigest()!=expected:
            raise ValueError("historical Z archive SHA-256 changed: "+name)
        sealed[name]=raw
    return sealed


def read_archives(py311:Path,py312:Path):
    left=read_original(py311)
    right=read_original(py312)
    if left!=right:
        raise ValueError("Python 3.11 and 3.12 scientific artifacts differ")
    return (
        json.loads(left["a230z-physical-worlds.json"]),
        json.loads(left["a230z-summary.json"]),
    )


def state_check(state):
    """Full accessible Stage6 state only, never causal ground truth."""
    if not isinstance(state,dict) or set(state)!=ACCESSIBLE:
        raise ValueError("hidden/future/partial field in first-person state")
    if set(state["body"])!=BODY_KEYS or set(state["inventory"])!=INV_KEYS:
        raise ValueError("first-person bodily or inventory state is incomplete")
    if (type(state["x"]) is not int or type(state["y"]) is not int or
        not (1<=state["x"]<=30 and 1<=state["y"]<=30)):
        raise ValueError("malformed first-person location")
    adjacent=state["adjacent"]
    if (not isinstance(adjacent,list) or len(adjacent)!=4 or
        {n["direction"] for n in adjacent}!={"north","south","east","west"}):
        raise ValueError("first-person neighbors incomplete or duplicated")
    for n in adjacent:
        if set(n)!={"direction","x","y","passable","resources","water_source","creature"}:
            raise ValueError("not a recognized visible adjacent-cell payload")
        if not isinstance(n["passable"],bool):
            raise ValueError("nonboolean visible passability")
    for key in BODY_KEYS:
        val=state["body"][key]
        if type(val) not in (int,float) or not (0.0<=val<=100.0):
            raise ValueError("bodily variable outside authorized range")


def east_neighbor(state):
    return next(n for n in state["adjacent"] if n["direction"]=="east")


def move_east():
    return {"primitive":"se_deplacer","parameters":{"direction":"east"}}


def collect_b():
    return {"primitive":"collecter","parameters":{"target":"berry_b"}}


def eat_b():
    return {"primitive":"manger","parameters":{"target":"berry_b"}}


def independently_decide(state,protocol,previous_commands):
    """Pure first-person accessible food decision, never sees latent outcome."""
    state_check(state)
    if protocol not in PROTOCOLS:
        raise ValueError("unknown experiment policy")
    if not isinstance(previous_commands,list):
        raise ValueError("unrecorded prior actions")
    if any(c not in (move_east(),collect_b(),eat_b()) for c in previous_commands):
        raise ValueError("unknown act in personal action history")
    if eat_b() in previous_commands:
        return None,"already_consumed_one_berry_b"
    if state["inventory"]["berry_b"]>0:
        return eat_b(),"held_berry_b_accessible"
    if "berry_b" in state["current_resources"]:
        return collect_b(),"local_berry_b_visible"
    neighbor=east_neighbor(state)
    if "berry_b" in neighbor["resources"]:
        return (
            (move_east(),"eastern_berry_b_visible_passable")
            if neighbor["passable"] else
            (None,"eastern_berry_b_visible_but_blocked")
        )
    if (protocol=="SINGLE_EAST_PROBE" and not previous_commands
        and neighbor["passable"]):
        return move_east(),"one_blind_eastern_probe"
    return None,"no_visible_accessible_berry_b_abstain"


def independent_candidate_commands(state):
    """Reimplement Stage6 candidate set without importing SimulatorPlanner."""
    state_check(state)
    commands=[]
    for n in state["adjacent"]:
        if n["passable"]:
            commands.append({
                "primitive":"se_deplacer",
                "parameters":{"direction":n["direction"]},
            })
    for resource in sorted(set(state["current_resources"])):
        commands.append({
            "primitive":"collecter","parameters":{"target":resource},
        })
    for berry in ("berry_a","berry_b"):
        if state["inventory"][berry]>0:
            commands.append({
                "primitive":"manger","parameters":{"target":berry},
            })
    if state["current_water_source"]:
        commands.append({"primitive":"boire","parameters":{}})
    if state["inventory"]["stone"]>0:
        commands.append({"primitive":"poser_une_pierre","parameters":{}})
    if state["inventory"]["wood"]>0 and state["inventory"]["stone"]>0:
        commands.append({"primitive":"fabriquer_outil","parameters":{}})
    commands.extend((
        {"primitive":"dormir","parameters":{}},
        {"primitive":"attendre","parameters":{}},
    ))
    return commands


def frozen_world_expected_ids():
    return {
        (layout,protocol,variant,food,position)
        for layout in LAYOUTS
        for protocol in PROTOCOLS
        for variant in (A_VARIANTS if layout=="A_ONLY" else B_VARIANTS)
        for food in FOODS for position in POSITIONS
    }


def _check_world(row):
    layout=row["layout_external_only"]
    policy=row["protocol_precommitted"]
    latent=row["latent_berry_effect_external_only"]
    food=row["initial_food"]
    loc=tuple(row["initial_position"])
    if (layout not in LAYOUTS or policy not in PROTOCOLS or
        latent not in (A_VARIANTS if layout=="A_ONLY" else B_VARIANTS)
        or food not in FOODS or loc not in POSITIONS):
        raise ValueError("non-preregistered physical world/cell")
    name=f"a230z:{layout}:{policy}:{latent}:food{int(food)}:x{loc[0]}y{loc[1]}"
    if row["world_id"]!=name:
        raise ValueError("physical world identifier invalid")
    if (not isinstance(row["config_sha256_external_only"],str)
        or len(row["config_sha256_external_only"])!=64
        or not isinstance(row["layout_sha256_external_only"],str)
        or len(row["layout_sha256_external_only"])!=64):
        raise ValueError("missing original laboratory physical provenance")
    first=row["initial_first_person"]
    state_check(first)
    if (first["x"],first["y"],float(first["body"]["food"]))!=(
        loc[0],loc[1],food):
        raise ValueError("initial accessible state diverges from cohort")
    if row["initial_first_person_sha256"]!=digest(first):
        raise ValueError("first-person initial hash corrupted")
    if (row["lived_postterminal_capture"] is not None or
        row["certifies_food_safety"] is not False or
        row["actual_I0_UC_cost"] is not None or
        row["no_oracle_information_in_policy"] is not True or
        row["no_stage6_shadow_action_dispatched"] is not True or
        row["no_i0_birth_or_autonomous_step"] is not True):
        raise ValueError("fabricated safety, Oracle, UC or postmortem living memory")

    recs=row["physical_steps_external"]
    decisions=row["perceptual_policy_choices"]
    if (len(recs)!=row["physical_step_count"] or len(recs)>4 or
        not decisions):
        raise ValueError("invalid physical/decision step count")
    perceived_states=[{"t_monde":1,"state":first}]
    after=first
    for i,record in enumerate(recs,1):
        example=record["physical_example"]
        if (record["t_monde"]!=i
            or record["state_before"]!=example["state"]
            or record["physical_after_external_only"]!=example["observed_next_state"]
            or record["terminal_external_only"]!=example["terminal"]
            or record["command"]!=example["command"]
            or example["family"]!="a230z_physically_executed_alternative"
            or record["physical_example_sha256"]!=digest(example)
            or record["not_dispatched_by_shadow"] is not True):
            raise ValueError("physical receipt invalid/forged")
        if record["state_before"]!=after:
            raise ValueError("physically observed transitions do not chain")
        if i>1 and recs[i-2]["terminal_external_only"]:
            raise ValueError("physical action after terminality")
        if record["command"] not in independent_candidate_commands(after):
            raise ValueError("lab command did not meet accessible Stage6 candidate condition")
        nxt=record["physical_after_external_only"]
        state_check(nxt)
        if record["terminal_external_only"] != (
            float(nxt["body"]["integrity"])<=0.0
        ):
            # In this preregistered fixture only berry poisoning is lethal.
            raise ValueError("terminal flag conflicts with zero-integrity physical consequence")
        after=nxt
        if not record["terminal_external_only"]:
            perceived_states.append({"t_monde":i+1,"state":nxt})
    if perceived_states!=row["lived_states_while_alive"]:
        raise ValueError("postmortem was read as lived, or living history missing")
    terminal_step=(
        len(recs) if recs and recs[-1]["terminal_external_only"] else None
    )
    if row["physical_terminal_step_external_only"]!=terminal_step:
        raise ValueError("external terminal step invented/omitted")
    if (len(decisions) != len(recs)+(0 if terminal_step is not None else 1)
        or any(choice["t_monde"]!=i for i,choice in enumerate(decisions,1))):
        raise ValueError("missing or fabricated decision, possibly after death")
    decisions_past=[]
    for i,choice in enumerate(decisions):
        state=choice["input_accessible_state"]
        state_check(state)
        if (choice["input_sha256"]!=digest(state)
            or choice["previous_actually_executed_commands"]!=decisions_past
            or choice["external_hidden_configuration_not_used"] is not True
            or choice["certifies_safe"] is not False):
            raise ValueError("hidden/future input or false safety in policy choice")
        if state!=perceived_states[i]["state"]:
            raise ValueError("decision used a state unavailable at that time")
        expected,reason=independently_decide(state,policy,decisions_past)
        if (choice["command"]!=expected
            or choice["decision_reason_from_observation_only"]!=reason):
            raise ValueError("decision contradicted authorized first-person policy")
        if i<len(recs):
            if choice["command"]!=recs[i]["command"]:
                raise ValueError("recorded physical action differs from predecision")
            decisions_past=decisions_past+[choice["command"]]
        elif choice["command"] is not None:
            raise ValueError("extra unexecuted shadow act became a physical decision")

    ate=bool(recs and recs[-1]["command"]==eat_b())
    if row["ingested_berry_b_external"] is not ate:
        raise ValueError("physical ingestion receipt inconsistent with claim")
    prior_eat=recs[-1]["state_before"] if ate else None
    bench_after=recs[-1]["physical_after_external_only"] if ate else None
    if (row["pre_ingestion_lived_state"]!=prior_eat
        or row["post_ingestion_external_only"]!=bench_after):
        raise ValueError("future ingestion result treated as prior sensation")
    success=bool(
        ate and terminal_step is None and
        bench_after["body"]["food"]-prior_eat["body"]["food"]>=5.0
    )
    insufficient=bool(ate and terminal_step is None and not success)
    if (row["food_success_with_survival_external"] is not success
        or row["insufficient_food_with_survival_external"] is not insufficient):
        raise ValueError("physical food success/insufficiency mislabeled")
    previous_body=first["body"]
    last_body=(recs[-1]["physical_after_external_only"]["body"]
               if recs else previous_body)
    measured={
        k:round(last_body[k]-previous_body[k],8) for k in BODY_KEYS
    }
    if row["physical_body_delta_external"]!=measured:
        raise ValueError("physical energy/food/water/integrity costs misreported")
    return {
        "layout":layout,"protocol":policy,"latent":latent,
        "food":food,"position":loc,
        "id":name,"steps":len(recs),"ingested":ate,"terminal":terminal_step,
        "goal":success,"insufficient":insufficient,
        "preexposure_choices":[
            c for c in decisions if (
                c["command"] is not None and
                c["command"]!=eat_b()
            )
        ],
        "preingestion_snapshot":prior_eat,
        "prior_decisions":decisions,
        "physical_receipts":recs,
        "shadow":row["stage6_shadow"],
        "initial":first,
    }


def _shadow_check(row,source):
    """Independent exact-root evaluator from archived first-person evidence."""
    shadow=row["shadow"]
    if row["ingested"] is False:
        if shadow is not None:
            raise ValueError("Stage6 shadow exists without an ingestion opportunity")
        return None
    if shadow is None or row["terminal"] not in (None,len(row["physical_receipts"])):
        raise ValueError("absent Stage6 shadow or invalid terminal chronology")
    t=row["steps"]
    history=row["physical_receipts"][:t-1]
    examples=[p["physical_example"] for p in history]
    if (shadow["t_monde"]!=t
        or shadow["actual_own_history_step_count"]!=len(history)
        or shadow["actual_own_history_step_indices"]!=list(range(1,t))
        or shadow["own_physical_examples"]!=examples
        or shadow["input_first_person"]!=row["preingestion_snapshot"]
        or shadow["input_first_person_sha256"]!=digest(row["preingestion_snapshot"])
        or shadow["history_corpus_sha256"]!=digest({
            "version":f"z-own-past-{row['id']}-t{t}",
            "examples":examples,
        })):
        raise ValueError("first-person Stage6 history contaminated with future or foreign world")
    if (shadow["model_kind"]!="own_prior_experience_only_exact_shadow"
        or shadow["no_shadow_command_dispatched"] is not True
        or shadow["true_I0_UC_used"] is not None
        or shadow["not_a_lived_I0_memory"] is not True
        or shadow["oracle_fed_to_shadow"] is not False
        or shadow["r_eff"]!=1 or shadow["max_depth"]!=3
        or abs(shadow["target_food"]-(row["preingestion_snapshot"]["body"]["food"]+5.0))>1e-8):
        raise ValueError("Stage6 shadow misrepresented as I0 plan, UC, Oracle or future outcome")
    seen={digest({"state":p["state"],"command":p["command"]}) for p in examples}
    candidates=independent_candidate_commands(row["preingestion_snapshot"])
    available=sum(
        digest({"state":row["preingestion_snapshot"],"command":c}) in seen
        for c in candidates
    )
    diagnostic=shadow["stage6_diagnostic"]
    n=len(candidates)
    if (shadow["stage6_root_candidate_edges"]!=n
        or shadow["stage6_root_available_edges"]!=available
        or shadow["stage6_root_unavailable_edges"]!=n-available
        or diagnostic["root_candidate_edges"]!=n
        or diagnostic["root_available_edges"]!=available
        or diagnostic["root_unavailable_edges"]!=n-available
        or diagnostic["root_model_diagnostic"]!=
            ("no_predictable_first_step" if n>0 and available==0
             else "at_least_one_predictable_first_step" if available>0
             else "not_classified")
        or diagnostic["status"]!=shadow["stage6_status"]
        or shadow["stage6_candidate_commands_only"]):
        raise ValueError("Stage6 root exact-key prediction fabricated")
    if n<1 or available!=0 or shadow["stage6_status"]!="incomplete_model":
        raise ValueError("historical Stage6 root status differs from physical evidence")
    return {"candidate_count":n,"root_exact_known":available}


def independently_review(worlds,summary):
    if (len(worlds)!=168 or summary.get("analysis_code_sha")!=ORIGINAL_Z_SHA
        or summary.get("schema")!="a230z-accessible-alternative-food-physical-v1"):
        raise ValueError("wrong original experiment schema/code version")
    expected=frozen_world_expected_ids()
    obs={}
    rows=[]
    for source in worlds:
        row=_check_world(source)
        key=(row["layout"],row["protocol"],row["latent"],
             row["food"],row["position"])
        if key not in expected or key in obs:
            raise ValueError("duplicate/extra physical world in frozen matrix")
        obs[key]=row
        rows.append(row)
        _shadow_check(row,source)
    if set(obs)!=expected:
        raise ValueError("original physical world matrix incomplete")
    per_arm=defaultdict(Counter)
    total=Counter()
    firstperson_groups=defaultdict(list)
    for row in rows:
        k=(row["layout"],row["protocol"])
        c=per_arm[k]
        c["worlds"]+=1
        c["physical_steps"]+=row["steps"]
        c["ingestions"]+=row["ingested"]
        c["terminals"]+=row["terminal"] is not None
        c["food_successes"]+=row["goal"]
        c["insufficient"]+=row["insufficient"]
        c["abstained_from_food"]+=not row["ingested"]
        for stat in c:
            if c[stat]<0:
                raise AssertionError("impossible negative sample")
        total["worlds"]+=1
        total["physical_actions"]+=row["steps"]
        total["ingestions"]+=row["ingested"]
        total["terminal"]+=row["terminal"] is not None
        total["goal"]+=row["goal"]
        total["insufficient"]+=row["insufficient"]
        total["abstained"]+=not row["ingested"]
        firstperson_groups[(
            row["layout"],row["protocol"],row["food"],row["position"]
        )].append(row)
    for arm,(n,steps) in EXPECTED_ARM.items():
        if (per_arm[arm]["worlds"],per_arm[arm]["physical_steps"])!=(n,steps):
            raise ValueError("original physical factor/step count diverged")
        original=summary["per_arm"].get("/".join(arm))
        if original!=dict(per_arm[arm]):
            raise ValueError("original per-arm results disagree with independent recount")

    groups_with_lethal=0
    for (layout,policy,food,pos),items in firstperson_groups.items():
        latent_expected=A_VARIANTS if layout=="A_ONLY" else B_VARIANTS
        if {w["latent"] for w in items}!=set(latent_expected):
            raise ValueError("one matched hidden-cause cell omitted")
        def prior_signature(row):
            choices=row["prior_decisions"]
            idx=next((i for i,c in enumerate(choices) if c["command"]==eat_b()),None)
            prefix=choices if idx is None else choices[:idx+1]
            return [(
                c["t_monde"],c["input_accessible_state"],c["command"]
            ) for c in prefix]
        if any(prior_signature(item)!=prior_signature(items[0])
               for item in items[1:]):
            raise ValueError("hidden food effect entered preexposure observations")
        if items[0]["ingested"]:
            if (sum(x["terminal"] is not None for x in items)!=1 or
                sum(x["goal"] for x in items)!=2 or
                sum(x["insufficient"] for x in items)!=1):
                raise ValueError("observationally aliased food risk mischaracterized")
            groups_with_lethal+=1
    remote_pairs=0
    for policy,food,pos in product(PROTOCOLS,FOODS,POSITIONS):
        local=obs[("A_ONLY",policy,"benign",food,pos)]
        remote=obs[("B_EAST_TWO_STEPS",policy,"benign",food,pos)]
        if local["initial"]!=remote["initial"]:
            raise ValueError("remote B prematurely included in first-person perception")
        remote_pairs+=1

    if (
        (total["worlds"],total["physical_actions"],total["ingestions"],
         total["terminal"],total["goal"],total["insufficient"],total["abstained"])
        != (168,244,80,20,40,20,88)
        or len(firstperson_groups)!=40
        or groups_with_lethal!=20
        or remote_pairs!=8
    ):
        raise ValueError("original preregistered metrics were changed")
    for key,value in {
        "original_physical_worlds":168,
        "original_physical_actions":244,
        "unique_initial_firstperson_hidden_groups":40,
        "remote_B_truly_unseen_initial_paired_groups":8,
        "ingestions_of_berry_b":80,
        "terminal_physical_ingestions":20,
        "surviving_food_gain_at_least_5":40,
        "surviving_food_gain_insufficient":20,
        "abstentions_from_berry_b_ingestion":88,
        "known_alternative_with_hidden_lethal_possibility_groups":20,
        "shadow_queries_actual_Stage6_algorithm":80,
        "shadow_status_counts":{"incomplete_model":80},
        "new_living_I0_births":0,
        "new_autonomous_I0_steps":0,
        "normative_mvp_modified":False,
        "oracle_to_i0_feedback":False,
        "stage6_production_plan_success_proven":False,
        "food_safety_proven":False,
        "actual_I0_UC_cost_measured":False,
        "stage12":"PARTIAL",
        "issue110":"OPEN",
    }.items():
        if summary.get(key)!=value:
            raise ValueError("original Z summary contradicted physical archive: "+key)
    if summary["world_data_sha256"]!=digest(worlds):
        raise ValueError("original physical corpus digest altered")
    if summary["frozen_matrix_sha256"]!=digest({
        "layouts":LAYOUTS,"policies":PROTOCOLS,"foods":FOODS,
        "positions":POSITIONS,"A_hidden":A_VARIANTS,
        "B_hidden":B_VARIANTS,"expected_physical_steps":244,
    }):
        raise ValueError("physical matrix fingerprint inconsistent")
    return {
        "schema":"a230za-independent-archive-consistency-v1",
        "source_z_sha":ORIGINAL_Z_SHA,
        "source_z_run":ORIGINAL_Z_RUN,
        "source_original_worlds":168,
        "source_original_physical_steps":244,
        "independently_recounted_berry_b_ingestions":80,
        "independently_recounted_physical_terminalities":20,
        "independently_recounted_surviving_food_successes":40,
        "independently_recounted_surviving_insufficient":20,
        "independently_recounted_abstentions":88,
        "observable_aliased_initial_groups":len(firstperson_groups),
        "observationally_aliased_B_groups_containing_terminal":groups_with_lethal,
        "far_B_invisible_initial_matched_controls":remote_pairs,
        "stage6_root_exactly_unavailable_80_of_80":80,
        "conditional_safe_food_certificate_possible_for_fixed_B_policy":False,
        "first_person_policy_from_archive_independently_recomputed":True,
        "real_worldbody_apply_proved_by_JSON_alone":False,
        "new_i0_lives":0,"new_physical_worlds":0,"new_physical_steps":0,
        "actual_I0_UC_measured":False,"oracle_to_i0_feedback":False,
        "stage12":"PARTIAL","issue110":"OPEN","cognitive_deployment":"NO-GO",
        "original_per_arm":{"/".join(k):dict(c) for k,c in sorted(per_arm.items())},
    }


def run(a:Path,b:Path,output:Path):
    worlds,summary=read_archives(a,b)
    result=independently_review(worlds,summary)
    result.update({
        "reviewer_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "original_artifact_sha256":ARCHIVE_SHA,
        "py311_py312_archives_identical_bytes":True,
        "original_Z_matrix_168_superseded_unexecuted_68_before_code":True,
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230za-recheck.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZA_SUMMARY "+json.dumps({
        k:v for k,v in result.items()
        if k not in ("original_artifact_sha256","original_per_arm")
    },sort_keys=True),flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-py311",type=Path,required=True)
    p.add_argument("--source-py312",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    run(args.source_py311,args.source_py312,args.output_dir)


if __name__=="__main__":
    main()
