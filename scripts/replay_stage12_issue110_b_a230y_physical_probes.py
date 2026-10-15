"""A2.30-Y: PHYSICAL WorldBody replay of preregistered W.

Only original W artifacts as source of RECEIPTS, not as a guide to choose
commands. All commands and latent physical fixture knobs are reconstructed
from the precommitted protocol, via an independent WorldPhysicsConfig builder
created for A2.30-R (which never imported the W scientific runner).

This is a TECHNICAL REPLAY of identical conditions, *not* a new scientific
cohort and *not* an I0 life. Stage6/Stage12/Oracle are never run.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes,sha256_hex
from lab.world import WorldBody
from replay_stage12_issue110_b_a230r_physical import independently_configure

PREREGISTERED_SOURCE_RUN=38753518412
PREREGISTERED_SOURCE_SHA="aecb8d1172846620c3038a4bc10e7716ec7bde1e"
SOURCE_HASHES={
    "a230w-acted-physical-worlds.json":
        "999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889",
    "a230w-passive-positive-controls.json":
        "dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666",
    "a230w-summary.json":
        "859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9",
}
VALID_FOOD=(35.0,45.0)
VALID_POS=((5,5),(7,7))
VALID_LATENTS={"benign","toxin_7","toxin_30","toxin_100","gain_zero"}
VALID_PROBES=("immediate","wait_twice","collect_first","west_return")
WAIT=PrimitiveCommand("attendre")
COLLECT=PrimitiveCommand("collecter",{"target":"berry_a"})
EAT=PrimitiveCommand("manger",{"target":"berry_a"})
WEST=PrimitiveCommand("se_deplacer",{"direction":"west"})
EAST=PrimitiveCommand("se_deplacer",{"direction":"east"})
PROBE_PROGRAM={
    "immediate":(),
    "wait_twice":(WAIT,WAIT),
    "collect_first":(COLLECT,),
    "west_return":(WEST,EAST),
}
VISIBLE_CONTROLS={"resource_berry_a","resource_berry_b","west_blocked"}


def hash_object(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def authorized_capture(world,t,perception):
    captured=perception.capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(
        capture=captured,is_night=world.is_night(t)
    ).as_dict()


def reconstruct_program(probe):
    if probe not in PROBE_PROGRAM:
        raise ValueError("unknown preregistered pre-exposure probe")
    sequence=PROBE_PROGRAM[probe]
    return sequence+(
        (EAT,) if probe=="collect_first" else (COLLECT,EAT)
    )


def replay_world(archived):
    latent=archived["latent_external_bench_only"]
    probe=archived["probe"]
    food=archived["initial_food"]
    pos=tuple(archived["initial_position"])
    identity=archived["world_id"]
    if (latent not in VALID_LATENTS or probe not in VALID_PROBES
        or food not in VALID_FOOD or pos not in VALID_POS
        or identity!=f"a230w:{probe}:{latent}:food{int(food)}:"
                     f"x{pos[0]}y{pos[1]}"
        or archived["no_oracle_feedback_to_i0"] is not True
        or archived["no_i0_instance_or_autonomous_command"] is not True
        or archived["certifies_safe_from_probe"] is not False):
        raise ValueError("wrong original source world or ungrounded safety claim")
    config,layout=independently_configure("EAT",latent,food,pos)
    if (config.digest()!=archived["config_digest_external_only"]
        or hash_object(layout.as_dict())!=archived["layout_digest_external_only"]):
        raise ValueError("original physics/layout digest mismatched BEFORE actions")
    if (not isinstance(archived["predecision_lived_history"],list)
        or archived["predecision_lived_history"][0]["t_monde"]!=1):
        raise ValueError("first-person history missing")
    expected=reconstruct_program(probe)
    receipts=archived["physical_commands_and_receipts_external_only"]
    if (len(expected)!=len(receipts)
        or len(receipts)!=archived["physical_total_steps"]
        or archived["physical_probe_steps"]!=len(PROBE_PROGRAM[probe])):
        raise ValueError("wrong expected preregistered command length")
    world=WorldBody(config=config,layout=layout)
    perceptor=SymbolicPerception()
    original=authorized_capture(world,1,perceptor)
    if archived["predecision_lived_history"][0]["state"]!=original:
        raise ValueError("initial first-person state differs in independent physics")
    observed_history=[{"t_monde":1,"state":original}]
    first_person_before_decision=None
    terminal_at=None
    output=None
    for step,command in enumerate(expected,1):
        before=authorized_capture(world,step,perceptor)
        result=world.apply(command,t_monde=step)
        after=authorized_capture(world,step+1,perceptor)
        archived_row=receipts[step-1]
        claimed={
            "phase":(
                "preexposure_probe"
                if step<=len(PROBE_PROGRAM[probe])
                else "external_food_outcome_only"
            ),
            "t_monde":step,
            "command":command.as_dict(),
            "before":before,
            "after_for_external_bench":after,
            "terminal_external_only":result.lethal,
        }
        if (archived_row!={**claimed,"sha256":hash_object(claimed)}
            or (step>1 and
                before!=receipts[step-2]["after_for_external_bench"])):
            raise ValueError(
                f"independent physical outcome differs on {identity} step {step}"
            )
        if step<=len(PROBE_PROGRAM[probe]):
            if result.lethal:
                raise ValueError("nominal pre-exposure probe became lethal")
            observed_history.append({
                "t_monde":step+1,"state":after,
            })
        if step==len(PROBE_PROGRAM[probe]):
            first_person_before_decision=after
        output=after
        if result.lethal:
            terminal_at=step
            world.freeze_terminal_state()
            break
    if first_person_before_decision is None:
        # The immediate arm executes no probe, so the initial t1 observation
        # is the living decision state and has no probe cost.
        first_person_before_decision=original
    if (observed_history!=archived["predecision_lived_history"]
        or first_person_before_decision!=archived["decision_state"]
        or hash_object(first_person_before_decision)!=
            archived["decision_state_sha256"]
        or hash_object(observed_history)!=archived["predecision_history_sha256"]):
        raise ValueError("original first-person timing or decision capture diverged")
    if (terminal_at!=archived["physical_terminal_step_external_only"]
        or archived["physically_alive_after_ingestion"] is
            (terminal_at is not None)
        or archived["postterminal_lived_capture_count"]!=0
        or archived["lived_post_ingestion_if_survivor"]!=(
            output if terminal_at is None else None
        )):
        raise ValueError("original terminal state was forged as lived")
    if output is None:
        raise ValueError("no physical ingestion outcome replayed")
    actual_food_gain=round(float(
        output["body"]["food"]-
        first_person_before_decision["body"]["food"]
    ),8)
    success=terminal_at is None and actual_food_gain>=5.0
    if (abs(actual_food_gain-
            archived["physical_food_gain_from_predecision_external_only"])>1e-8
        or success is not
            archived["physical_food_goal_and_survival_external_only"]):
        raise ValueError("independent food goal physically disagrees")
    cost={
        k:round(float(
            first_person_before_decision["body"][k]-
            original["body"][k]
        ),8) for k in ("energy","food","water","integrity")
    }
    if cost!=archived["physical_probe_effect"]:
        raise ValueError("probe physical effect differs from claimed")
    return {
        "world_id":identity,"probe":probe,"technical_physical_steps":len(receipts),
        "terminal_step":terminal_at,"food_goal_with_survival":success,
        "physical_body_and_perception_identical":True,
    }


def replay_passive(row):
    food=row["food"]
    pos=tuple(row["position"])
    control=row["control"]
    id_=row["world_id"]
    if (food not in VALID_FOOD or pos not in VALID_POS
        or control not in VISIBLE_CONTROLS
        or id_!=f"a230w-control:{control}:food{int(food)}:"
                 f"x{pos[0]}y{pos[1]}"
        or row["physical_steps"]!=0
        or row["no_food_safety_claim"] is not True):
        raise ValueError("unregistered positive-control world")
    config,layout=independently_configure("EAT","benign",food,pos)
    if control=="resource_berry_b":
        layout=replace(
            layout, resources=((config.initial_position,"berry_b",2),)
        )
    if control=="west_blocked":
        layout=replace(
            layout, obstacles=frozenset({
                config.initial_position.moved("west")
            })
        )
    if (config.digest()!=row["config_digest_external_only"]
        or hash_object(layout.as_dict())!=row["layout_digest_external_only"]):
        raise ValueError("visible physical control layout changed")
    world=WorldBody(config=config,layout=layout)
    perception=SymbolicPerception()
    sensed=authorized_capture(world,1,perception)
    if (sensed!=row["visible_state"]
        or hash_object(sensed)!=row["visible_state_sha256"]):
        raise ValueError("physical visible control was falsely reported")
    return id_


def audit_source(acted,passive,summary):
    if (summary.get("schema")!="a230w-prospective-unobservable-food-risk-v1"
        or summary.get("sha_of_analysis_code")!=PREREGISTERED_SOURCE_SHA
        or len(acted)!=80 or len(passive)!=12):
        raise ValueError("not original W physical source cohort")
    identities=set()
    per_probe=Counter()
    counts=Counter()
    for row in acted:
        observed=replay_world(row)
        identity=observed["world_id"]
        if identity in identities:
            raise ValueError("physical source world appears more than once")
        identities.add(identity)
        counts["worlds"]+=1
        counts["steps"]+=observed["technical_physical_steps"]
        counts["terminal"]+=observed["terminal_step"] is not None
        counts["food_goal"]+=observed["food_goal_with_survival"]
        per_probe[(observed["probe"],"worlds")]+=1
        per_probe[(observed["probe"],"steps")]+=observed[
            "technical_physical_steps"
        ]
    for row in passive:
        ident=replay_passive(row)
        if ident in identities:
            raise ValueError("duplicate visible control fixture")
        identities.add(ident)
        counts["passive"]+=1
    expected_probe_steps={
        "immediate":40, "wait_twice":80,
        "collect_first":40, "west_return":80,
    }
    if (dict((p,per_probe[(p,"steps")]) for p in VALID_PROBES)
        !=expected_probe_steps
        or any(per_probe[(p,"worlds")]!=20 for p in VALID_PROBES)
        or dict(counts)!={
            "worlds":80, "steps":240, "terminal":16,
            "food_goal":48, "passive":12,
        }
        or len(identities)!=92):
        raise ValueError("physical replay aggregate no longer matches preregistration")
    return {
        "schema":"a230y-independent-WorldBody-technical-replay-v1",
        "original_W_run":PREREGISTERED_SOURCE_RUN,
        "original_W_sha":PREREGISTERED_SOURCE_SHA,
        "original_scientific_conditions":92,
        "new_independent_scientific_conditions":0,
        "technical_replay_worlds":92,
        "technical_replay_acted_worlds":80,
        "technical_replay_passive_controls":12,
        "technical_replay_physical_actions":240,
        "technical_replay_external_terminals":16,
        "technical_replay_food_goals":48,
        "physical_outcome_differences":0,
        "terminal_revivals":0,
        "new_i0_births":0,
        "new_i0_autonomous_steps":0,
        "oracle_to_i0_feedback":False,
        "replays_same_deterministic_worldbody_not_independent_natural_truth":True,
        "stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
    }


def load_sealed(directory):
    original={}
    for file,expected_hash in SOURCE_HASHES.items():
        matches=list(directory.rglob(file))
        if len(matches)!=1:
            raise ValueError("missing/ambiguous historical physical source")
        body=matches[0].read_bytes()
        if sha256(body).hexdigest()!=expected_hash:
            raise ValueError("sealed original W source hash mismatch")
        original[file]=json.loads(body)
    return original


def execute(original,output):
    data=load_sealed(original)
    result=audit_source(
        data["a230w-acted-physical-worlds.json"],
        data["a230w-passive-positive-controls.json"],
        data["a230w-summary.json"],
    )
    result["physical_replay_code_sha"]=subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True
    ).strip()
    result["source_hashes"]=SOURCE_HASHES
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230y-replay-summary.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n"
    )
    print("A230Y_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k!="source_hashes"
    },sort_keys=True),flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-W",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    execute(args.original_W,args.output_dir)


if __name__=="__main__":
    main()
