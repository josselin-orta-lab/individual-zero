"""A2.13: physical-only adversarial state-projection safety experiment.

No agent, Oracle, causal label, policy or simulator correction is fed back into I0.
All compared effects come from independently applied WorldBody transitions.
"""
from __future__ import annotations
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess

from i0.equipment import FrozenTableEquipment
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import BodyState, Position, WorldBody, WorldLayout

SEEDS=tuple(range(41,49))
FAMILIES=("BODY_CAP","INVENTORY","ADJACENT_PASSABILITY","NIGHT_CREATURE",
          "HIDDEN_TOXICITY","HIDDEN_EXTERNAL_HAZARD")
PROJECTIONS={
    "drop_body":("body",),
    "drop_inventory":("inventory",),
    "drop_adjacent":("adjacent",),
    "drop_night":("is_night",),
    "drop_absolute_position":("x","y"),
}

def projected_digest(state, command, dropped):
    data=state.as_dict()
    for field in dropped:
        del data[field]
    return sha256_hex(canonical_causal_bytes(
        {"state":data,"command":command.as_dict()}))

def sample_inputs(seed, family):
    index=FAMILIES.index(family)
    rng=random.Random(seed*1009+(index+1)*100003)
    p=Position(rng.randint(5,24),rng.randint(5,24))
    food=float(rng.randint(39,55))
    water=float(rng.randint(55,80))
    return p,food,water

def make_world(base,p,food,water,*,berry=True,toxic=False,danger=False,
               creature=False,obstacle=False):
    initial=replace(base.initial_body,food=food,water=water,integrity=90.0,
                    energy=85.0)
    effect=base.berry_effects["berry_a"]
    berries={**base.berry_effects,
             "berry_a":replace(effect,food_gain=30.0,
                               integrity_delta=(-15.0 if toxic else 0.0))}
    cfg=replace(base,initial_position=p,initial_body=initial,
                berry_effects=berries)
    layout=WorldLayout(
        resources=((p,"berry_a",1),) if berry else (),
        creatures=frozenset({p.moved("south")}) if creature else frozenset(),
        obstacles=frozenset({p.moved("east")}) if obstacle else frozenset(),
        danger_zones=frozenset({p}) if danger else frozenset(),
    )
    return WorldBody(config=cfg,layout=layout)

def witnessed(world,t,command):
    before=state_from_capture(
        capture=SymbolicPerception().capture(
            local_state=world.capture_local(t_monde=t).as_dict(),
            telemetry=world.telemetry()),
        is_night=world.is_night(t))
    result=world.apply(command,t_monde=t)
    return {
        "state":before,
        "command":command,
        "input_digest":FrozenTableEquipment.input_digest(before,command),
        "result":{
            "position_after":result.position_after.as_dict(),
            "body_after":result.body_after.as_dict(),
            "inventory_after":dict(sorted(world.inventory().items())),
            "terminal":result.lethal,
            "effects":dict(result.effects),
        },
        "transition_sha256":sha256_hex(canonical_causal_bytes(result.as_dict())),
    }

def generate_pair(family,seed,base):
    p,food,water=sample_inputs(seed,family)
    if family=="BODY_CAP":
        # Same local world and command; only physiology differs. Both
        # independently collect before eating. One saturates food at 100.
        left=make_world(base,p,food,water)
        right=make_world(base,p,float(95+seed%4),water)
        prep=PrimitiveCommand("collecter",{"target":"berry_a"})
        witnessed(left,1,prep);witnessed(right,1,prep)
        cmd=PrimitiveCommand("manger",{"target":"berry_a"})
        return witnessed(left,2,cmd),witnessed(right,2,cmd)
    if family=="INVENTORY":
        left=make_world(base,p,food,water,berry=True)
        right=make_world(base,p,food,water,berry=False)
        prep=PrimitiveCommand("collecter",{"target":"berry_a"})
        witnessed(left,1,prep);witnessed(right,1,prep)
        cmd=PrimitiveCommand("manger",{"target":"berry_a"})
        return witnessed(left,2,cmd),witnessed(right,2,cmd)
    if family=="ADJACENT_PASSABILITY":
        left=make_world(base,p,food,water,obstacle=False)
        right=make_world(base,p,food,water,obstacle=True)
        cmd=PrimitiveCommand("se_deplacer",{"direction":"east"})
        return witnessed(left,1,cmd),witnessed(right,1,cmd)
    if family=="NIGHT_CREATURE":
        left=make_world(base,p,food,water,creature=True)
        right=make_world(base,p,food,water,creature=True)
        cmd=PrimitiveCommand("attendre")
        night=base.night_start_step+1
        assert not left.is_night(1) and right.is_night(night)
        return witnessed(left,1,cmd),witnessed(right,night,cmd)
    if family=="HIDDEN_TOXICITY":
        left=make_world(base,p,food,water,toxic=False)
        right=make_world(base,p,food,water,toxic=True)
        prep=PrimitiveCommand("collecter",{"target":"berry_a"})
        witnessed(left,1,prep);witnessed(right,1,prep)
        cmd=PrimitiveCommand("manger",{"target":"berry_a"})
        return witnessed(left,2,cmd),witnessed(right,2,cmd)
    if family=="HIDDEN_EXTERNAL_HAZARD":
        left=make_world(base,p,food,water,danger=False)
        right=make_world(base,p,food,water,danger=False)
        prep=PrimitiveCommand("collecter",{"target":"berry_a"})
        witnessed(left,1,prep);witnessed(right,1,prep)
        # The external physical intervention is hidden from local perception.
        right.apply_scenario_event("set_danger_zone",
            {"position":p.as_dict(),"active":True})
        cmd=PrimitiveCommand("manger",{"target":"berry_a"})
        return witnessed(left,2,cmd),witnessed(right,2,cmd)
    raise ValueError("unknown preregistered family")

def analyze_pair(left,right,family,seed):
    same_command=left["command"].as_dict()==right["command"].as_dict()
    if not same_command:
        raise AssertionError("preregistered commands not paired")
    same_input=left["input_digest"]==right["input_digest"]
    different_result=left["result"]!=right["result"]
    projections={}
    for name,dropped in PROJECTIONS.items():
        same_projection=(
            projected_digest(left["state"],left["command"],dropped)
            ==projected_digest(right["state"],right["command"],dropped))
        projections[name]={
            "same_projected_key":same_projection,
            "contradictory_outcome_collision":(same_projection and different_result\n                                                and not same_input),\n            "irreducible_hidden_ambiguity":(same_projection and different_result\n                                             and same_input)}
    expected={"BODY_CAP":"drop_body",
              "INVENTORY":"drop_inventory",
              "ADJACENT_PASSABILITY":"drop_adjacent",
              "NIGHT_CREATURE":"drop_night"}
    if family in expected:
        if not projections[expected[family]]["contradictory_outcome_collision"]:
            raise AssertionError("expected physical projection counterexample absent")
        if same_input:
            raise AssertionError("visible-state control failed")
    else:
        if not (same_input and different_result):
            raise AssertionError("hidden-cause observational equivalence not reproduced")
    return {
        "seed":seed,"family":family,
        "same_complete_observable_input":same_input,
        "different_physical_outcome":different_result,
        "left_input_sha256":left["input_digest"],
        "right_input_sha256":right["input_digest"],
        "left_transition_sha256":left["transition_sha256"],
        "right_transition_sha256":right["transition_sha256"],
        "projections":projections,
        "left_physical_result":left["result"],
        "right_physical_result":right["result"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    # Baseline config is read from the actual public fixture, not an Oracle.
    base=build_stage11_reference_runtime().world.config
    rows=[]
    for family in FAMILIES:
        for seed in SEEDS:
            left,right=generate_pair(family,seed,base)
            row=analyze_pair(left,right,family,seed)
            rows.append(row)
            (args.output_dir/f"{family.lower()}-{seed}.json").write_text(
                json.dumps(row,indent=2,sort_keys=True)+"\n")
    verdict={}
    for name in PROJECTIONS:
        contradictions=sum(
            int(x["projections"][name]["contradictory_outcome_collision"])
            for x in rows)
        verdict[name]={"contradictions":contradictions,
                       "verdict":"UNSAFE" if contradictions else "INCONCLUSIVE"}
    result={
        "schema":"a213-physical-projection-counterexamples-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True).strip(),
        "families":list(FAMILIES),"seeds":list(SEEDS),
        "paired_worlds":len(rows),"separate_physical_worlds":len(rows)*2,
        "hidden_equivalent_contradictions":sum(
            x["same_complete_observable_input"] and x["different_physical_outcome"]
            for x in rows),
        "projection_verdicts":verdict,
        "stage12":"PARTIAL","operator_accepted":False,
        "normative_specification_changed":False,
    }
    (args.output_dir/"a213-summary.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("A213_SUMMARY "+json.dumps(result,sort_keys=True),flush=True)
    return 0 if (len(rows)==48
             and result["hidden_equivalent_contradictions"]==16
             and all(verdict[key]["verdict"]=="UNSAFE" for key in
                     ("drop_body","drop_inventory","drop_adjacent","drop_night"))
             ) else 2

if __name__=="__main__":
    raise SystemExit(main())
