"""A2.30-R: independent WorldBody replay of original P physical receipts.

Does NOT import the P experimental runner, its outcome model, Q auditor,
EquipmentCorpusRecorder, Stage6/12 runtime, Oracle or Bench. Uses new DETACHED
WorldBody instances to verify what physical engine does on original fixed
commands, matching the original P archive *exactly*. These are TECHNICAL
replays of the same deterministic cells, not independent scientific samples.
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
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.world import (
    BerryEffect, BodyState, Position, PRIMITIVE_ACTIONS, ToolRecipe,
    WorldBody, WorldLayout, WorldPhysicsConfig,
)

ORIGINAL_RUN = 38730415503
P_SHA = "3ab03a90b38d6c968cddcd9ed699c3f089d0544c"
HASHES={
    "a230p-training-manifest.json":
        "f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e",
    "a230p-heldout-physical-results.json":
        "570713d9a44c55a13482dba3d5e9b2f8095df8ba8f487f22d5aa917db8bc3514",
    "a230p-summary.json":
        "45167e3bd7be3827f2839208aa8bfe2e316e6b4f110106b94d68bf32a3fea0e0",
}
TRAIN_FOODS=(30.0,40.0)
TEST_FOODS=(35.0,45.0)
TRAIN_POSITIONS=((2,2),(4,4))
TEST_POSITIONS=((5,5),(7,7))
TRAIN_VARIANTS={
    "MOV":("clear","lethal_east","danger_east_40","danger_east_20"),
    "EAT":("benign","toxin_7","toxin_100","gain_zero"),
    "WAIT":("baseline","food_decay_25","water_decay_22","danger_here_40"),
}
OOD_VARIANTS={
    "MOV":("danger_east_30","danger_east_55"),
    "EAT":("toxin_30","gain_25"),
    "WAIT":("food_decay_15","danger_here_55"),
}
EXPECTED={"train":(48,132),"heldout_ID":(48,132),
          "heldout_hidden_OOD":(24,64),"heldout_unknown_context":(8,24)}


def digest(x):
    return sha256_hex(canonical_causal_bytes(x))


def independently_configure(family,variant,food,coords):
    """Re-derived as explicit pure physics, not via the P runner's builder."""
    initial=Position(*coords)
    if family not in TRAIN_VARIANTS:
        raise ValueError("unknown preregistered family")
    reference=WorldPhysicsConfig(
        version="stage12-a230l-standalone-physics-v1",
        width=32,height=32,day_steps=300,night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0,food=60.0,water=20.0,integrity=100.0
        ),
        initial_position=Position(2,2),
        food_decay_per_step=0.0,water_decay_per_step=0.0,
        action_energy_costs={k:0.0 for k in sorted(PRIMITIVE_ACTIONS)},
        sleep_energy_gain=0.0,rest_integrity_gain=0.0,
        drink_water_gain=40.0,
        berry_effects={
            "berry_a":BerryEffect(10.0,0.0),
            "berry_b":BerryEffect(5.0,-100.0),
        },
        creature_damage=0.0,danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1,1,2),
    )
    costs=dict(reference.action_energy_costs)
    costs.update({
        "se_deplacer":1.0,"attendre":0.5,
        "collecter":0.75,"manger":0.5,
    })
    physics=replace(
        reference,
        version="a230p-standalone-worldphysics-v1",
        initial_position=initial,
        initial_body=replace(reference.initial_body,food=float(food)),
        food_decay_per_step=0.5,water_decay_per_step=0.2,
        action_energy_costs=costs,
        sleep_energy_gain=0.0,rest_integrity_gain=0.0,
    )
    layout=WorldLayout(
        resources=((initial,"berry_a",2),) if family=="EAT" else (),
    )
    if family=="MOV":
        east=initial.moved("east")
        if variant=="lethal_east":
            layout=replace(layout,lethal_zones=frozenset({east}))
        elif variant.startswith("danger_east_"):
            amount=float(variant.rsplit("_",1)[1])
            physics=replace(physics,danger_zone_damage=amount)
            layout=replace(layout,danger_zones=frozenset({east}))
        elif variant=="blocked_east":
            layout=replace(layout,obstacles=frozenset({east}))
        elif variant not in ("clear","west_virgin"):
            raise ValueError("unseen MOV scenario")
    elif family=="EAT":
        berries=dict(physics.berry_effects)
        if variant.startswith("toxin_"):
            damage=-float(variant.rsplit("_",1)[1])
            berries["berry_a"]=replace(
                berries["berry_a"],integrity_delta=damage
            )
        elif variant=="gain_zero":
            berries["berry_a"]=replace(
                berries["berry_a"],food_gain=0.0
            )
        elif variant=="gain_25":
            berries["berry_a"]=replace(
                berries["berry_a"],food_gain=25.0
            )
        elif variant!="benign":
            raise ValueError("unseen EAT scenario")
        physics=replace(physics,berry_effects=berries)
    else:
        if variant=="food_decay_25":
            physics=replace(physics,food_decay_per_step=2.5)
        elif variant=="food_decay_15":
            physics=replace(physics,food_decay_per_step=1.5)
        elif variant=="water_decay_22":
            physics=replace(physics,water_decay_per_step=2.2)
        elif variant.startswith("danger_here_"):
            damage=float(variant.rsplit("_",1)[1])
            physics=replace(physics,danger_zone_damage=damage)
            layout=replace(layout,danger_zones=frozenset({initial}))
        elif variant!="baseline":
            raise ValueError("unseen WAIT scenario")
    physics.validate()
    layout.validate(physics)
    return physics,layout


def frozen_prefix(family,variant):
    if family=="MOV":
        direction="west" if variant=="west_virgin" else "east"
        return (
            PrimitiveCommand("se_deplacer",{"direction":direction}),
            PrimitiveCommand("attendre"),PrimitiveCommand("attendre"),
        )
    if family=="EAT":
        return (
            PrimitiveCommand("collecter",{"target":"berry_a"}),
            PrimitiveCommand("manger",{"target":"berry_a"}),
            PrimitiveCommand("attendre"),
        )
    if family=="WAIT":
        return (PrimitiveCommand("attendre"),)*3
    raise ValueError("bad preregistered prefix")


def observe(world,t_monde,perception):
    sensed=perception.capture(
        local_state=world.capture_local(t_monde=t_monde).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(
        capture=sensed,is_night=world.is_night(t_monde)
    )


def physical_cumulative(first,last):
    delta={"dx":float(last.x-first.x),"dy":float(last.y-first.y)}
    for v in ("energy","food","water","integrity"):
        delta["body."+v]=float(last.body[v]-first.body[v])
    for v in ("berry_a","berry_b","wood","stone","tool"):
        delta["inventory."+v]=float(
            last.inventory.get(v,0)-first.inventory.get(v,0)
        )
    return delta


def replay_one(witness,receipt,stage):
    if (
        receipt["world_id"]!=witness["world_id"]
        or receipt["stage"]!=stage
        or stage not in EXPECTED
        or receipt["family"] not in TRAIN_VARIANTS
        or tuple(receipt["initial_position"]) not in (
            TRAIN_POSITIONS if stage=="train" else TEST_POSITIONS
        )
        or receipt["initial_food"] not in (
            TRAIN_FOODS if stage=="train" else TEST_FOODS
        )
        or receipt["oracle_feedback_to_i0"] is not False
    ):
        raise ValueError("untrusted physical source or mismatched original stratum")
    family=receipt["family"]
    variant=receipt["hidden_variant_for_lab_only"]
    if stage in ("train","heldout_ID"):
        allowed=TRAIN_VARIANTS[family]
    elif stage=="heldout_hidden_OOD":
        allowed=OOD_VARIANTS[family]
    else:
        allowed=("blocked_east","west_virgin") if family=="MOV" else ()
    if variant not in allowed:
        raise ValueError("latent physics variant not preregistered for stratum")
    physics,layout=independently_configure(
        family,variant,receipt["initial_food"],
        tuple(receipt["initial_position"])
    )
    if (physics.digest()!=receipt["physical_config_sha256"]
        or digest(layout.as_dict())!=receipt["physical_layout_sha256"]):
        raise ValueError("original physical configuration/layout digest diverged")
    prefix=frozen_prefix(family,variant)
    if witness["commands"]!=[c.as_dict() for c in prefix]:
        raise ValueError("original world reported a different command prefix")
    world=WorldBody(config=physics,layout=layout)
    perception=SymbolicPerception()
    expected_examples=receipt["observed_physical_examples"]
    first=None
    used=0
    died_at=None
    for t,command in enumerate(prefix,1):
        before=observe(world,t,perception)
        if first is None:
            first=before
        result=world.apply(command,t_monde=t)
        after=observe(world,t+1,perception)
        candidate={
            "family":"physical_a230p_"+family,
            "state":before.as_dict(),
            "command":command.as_dict(),
            "observed_next_state":after.as_dict(),
            "terminal":result.lethal,
        }
        if t>len(expected_examples):
            raise ValueError("recorded fewer physical actions than engine replay")
        archived=expected_examples[t-1]
        if (archived["t_monde"]!=t
            or archived["physical_example"]!=candidate
            or archived["physical_example_sha256"]!=digest(candidate)):
            raise ValueError(
                f"independent physical replay differs on {receipt['world_id']} step {t}"
            )
        step=witness["steps"][t-1]
        projected=physical_cumulative(first,after)
        if (step["terminal"]!=result.lethal
            or set(step["cumulative_delta"])!=set(projected)
            or any(abs(step["cumulative_delta"][k]-projected[k])>1e-8
                   for k in projected)):
            raise ValueError("physical replay and published bodily witness diverge")
        used+=1
        if result.lethal:
            died_at=t
            world.freeze_terminal_state()
            break
    if (used!=receipt["applied_steps"]
        or used!=len(witness["steps"])
        or used!=len(expected_examples)
        or died_at!=receipt["terminal_step"]
        or died_at!=witness["first_terminal_step"]):
        raise ValueError("terminal chronology or world step count diverged")
    return {"world_id":receipt["world_id"],"family":family,"stage":stage,
            "replayed_steps":used,"terminal_step":died_at,
            "canonical_physical_receipts_equal":True}


def read_locked_source(source:Path):
    contents={}
    for name,expected in HASHES.items():
        hits=list(source.rglob(name))
        if len(hits)!=1:
            raise ValueError("locked P source missing or ambiguous")
        body=hits[0].read_bytes()
        if sha256(body).hexdigest()!=expected:
            raise ValueError("original physical source artifact hash altered")
        contents[name]=json.loads(body)
    return contents


def audit_technical_replay(training,heldout,summary):
    if (summary.get("code_sha")!=P_SHA
        or summary.get("schema")!="a230p-physical-joint-trajectories-v1"
        or len(training["training_witnesses"])!=48
        or len(heldout)!=80):
        raise ValueError("not a valid preregistered P source")
    evidence=[]
    ids=set()
    stage_counts=Counter()
    world_counts=Counter()
    for w,receipt in zip(
        training["training_witnesses"],training["source_lab_physics"]
    ):
        output=replay_one(w,receipt,"train")
        if output["world_id"] in ids:
            raise ValueError("duplicate world in technical replay")
        ids.add(output["world_id"])
        evidence.append(output)
        stage_counts["train"]+=output["replayed_steps"]
        world_counts["train"]+=1
    for row in heldout:
        stage=row["stage"]
        if stage=="train":
            raise ValueError("test life contaminated by training")
        output=replay_one(row["witness"],row["source_lab_physics"],stage)
        if output["world_id"] in ids or row["world_id"]!=output["world_id"]:
            raise ValueError("duplicate original world")
        ids.add(output["world_id"])
        evidence.append(output)
        stage_counts[stage]+=output["replayed_steps"]
        world_counts[stage]+=1
    if len(ids)!=128:
        raise ValueError("not 128 original detached world conditions")
    for stage,(n,steps) in EXPECTED.items():
        if world_counts[stage]!=n or stage_counts[stage]!=steps:
            raise ValueError("replay physical count deviates from preregistered matrix")
    if sum(stage_counts.values())!=352:
        raise ValueError("terminalized replay returned wrong physical step total")
    return {
        "original_independent_world_conditions":128,
        "original_independent_world_step_receipts_checked":352,
        "technical_replay_world_instances":128,
        "technical_replay_physical_steps":352,
        "new_independent_scientific_samples":0,
        "new_i0_births":0,
        "new_i0_autonomous_steps":0,
        "terminal_revivals":0,
        "physical_outcome_differences":0,
        "physical_receipt_sha_mismatches":0,
        "oracular_information_fed_to_i0":False,
        "standalone_physics_engine_replay_not_external_world_truth":True,
        "stages":{
            s:{"worlds":world_counts[s],"steps":stage_counts[s]}
            for s in EXPECTED
        },
    }


def execute(source:Path,output:Path):
    originals=read_locked_source(source)
    study=audit_technical_replay(
        originals["a230p-training-manifest.json"],
        originals["a230p-heldout-physical-results.json"],
        originals["a230p-summary.json"],
    )
    study.update({
        "schema":"stage12-a230r-independent-technical-replay-v1",
        "original_P_action_run":ORIGINAL_RUN,
        "original_P_sha":P_SHA,
        "replay_source_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "archive_sha256":HASHES,
        "stage12":"PARTIAL",
        "issue110":"OPEN",
        "cognitive_model_deployment":False,
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230r-summary.json").write_text(
        json.dumps(study,sort_keys=True,indent=2)+"\n"
    )
    print("A230R_SUMMARY "+json.dumps(
        {k:v for k,v in study.items() if k!="archive_sha256"},
        sort_keys=True
    ),flush=True)
    return study


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    execute(args.source_dir,args.output_dir)


if __name__=="__main__":
    main()
