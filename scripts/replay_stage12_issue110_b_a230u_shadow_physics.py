"""A2.30-U: independent physical replay of original S-shadow research.

Different runner and explicitly derived physics from the protocol, no import
of the original S runner, its shadow Stage6, or EquipmentCorpusRecorder.
WorldBody.apply happens on detached NEW technical worlds only. These are the
same deterministic experimental conditions, NOT fresh scientific samples.
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
from lab.world import (
    BerryEffect,BodyState,Position,PRIMITIVE_ACTIONS,ToolRecipe,
    WorldBody,WorldLayout,WorldPhysicsConfig,
)

EXPECTED={
    "a230s-acted-worlds.json":
        "b905535a67c72b912e0b384dbc7e189e8446ee4954631e559928bd922edd0e36",
    "a230s-passive-worlds.json":
        "2863bb4e4d820cb3cc9b7492a0264e23f888e6b12e6225313f3c40766f8c27e6",
    "a230s-summary.json":
        "969de41c916df3210f8c9e0c1f033edc769bd49536f7fd20b14eaee03deee048",
}
ORIGINAL_S_RUN=38740664255
SOURCE_SHA="0046d8b2b30f44fe5e4fd0b4b165c88e724a8881"
KINDS={
    "food":("benign","toxic_mild","toxic_lethal","exogenous_confounded"),
    "movement":("clear","danger_40","danger_55","lethal_east"),
}
FOODS=(40.0,45.0)
POSITIONS=((2,2),(4,4))
STRATEGIES={"food":("wait","repeat_eat"),"movement":("wait","escape")}


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def standalone_config(*,food,position,berry_damage=0.0,danger_damage=7.0):
    """A2.30-L physical fixture restated without importing its initializer."""
    base=WorldPhysicsConfig(
        version="stage12-a230l-standalone-physics-v1",
        width=32,height=32,day_steps=300,night_steps=100,night_start_step=200,
        initial_body=BodyState(energy=50.0,food=60.0,water=20.0,integrity=100.0),
        initial_position=Position(2,2),
        food_decay_per_step=0.0,water_decay_per_step=0.0,
        action_energy_costs={k:0.0 for k in sorted(PRIMITIVE_ACTIONS)},
        sleep_energy_gain=0.0,rest_integrity_gain=0.0,drink_water_gain=40.0,
        berry_effects={
            "berry_a":BerryEffect(10.0,0.0),
            "berry_b":BerryEffect(5.0,-100.0),
        },
        creature_damage=0.0,danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1,1,2),
    )
    costs=dict(base.action_energy_costs)
    costs.update({
        "collecter":0.75,"manger":0.5,"attendre":0.5,
        "se_deplacer":1.0,
    })
    effects=dict(base.berry_effects)
    effects["berry_a"]=replace(
        effects["berry_a"],integrity_delta=berry_damage
    )
    config=replace(
        base,version="stage12-a230s-detached-observation-v1",
        initial_position=Position(*position),
        initial_body=replace(base.initial_body,food=float(food)),
        food_decay_per_step=0.5,
        water_decay_per_step=0.2,
        rest_integrity_gain=0.0,
        action_energy_costs=costs,
        berry_effects=effects,
        danger_zone_damage=danger_damage,
    )
    config.validate()
    return config


def independently_world(kind,variant,food,at):
    if kind=="food" and variant in KINDS["food"]:
        berry={
            "benign":0.0, "toxic_mild":-7.0,
            "toxic_lethal":-100.0,"exogenous_confounded":0.0
        }[variant]
        config=standalone_config(food=food,position=at,
                                 berry_damage=berry,danger_damage=7.0)
        layout=WorldLayout(resources=((Position(*at),"berry_a",2),))
    elif kind=="movement" and variant in KINDS["movement"]:
        damage={
            "clear":7.0,"danger_40":40.0,
            "danger_55":55.0,"lethal_east":7.0,
        }[variant]
        config=standalone_config(
            food=food,position=at,danger_damage=damage
        )
        to_east=Position(*at).moved("east")
        layout=WorldLayout(
            danger_zones=(frozenset({to_east}) if
                          variant in ("danger_40","danger_55") else frozenset()),
            lethal_zones=(frozenset({to_east}) if
                          variant=="lethal_east" else frozenset()),
        )
    else:
        raise ValueError("unregistered physical world")
    layout.validate(config)
    return config,layout


def planned_prefix(kind,followup):
    if kind=="food" and followup in STRATEGIES["food"]:
        return (
            PrimitiveCommand("collecter",{"target":"berry_a"}),
            PrimitiveCommand("collecter",{"target":"berry_a"}),
            PrimitiveCommand("manger",{"target":"berry_a"}),
            (PrimitiveCommand("attendre") if followup=="wait"
             else PrimitiveCommand("manger",{"target":"berry_a"})),
        )
    if kind=="movement" and followup in STRATEGIES["movement"]:
        return (
            PrimitiveCommand("se_deplacer",{"direction":"east"}),
            (PrimitiveCommand("attendre") if followup=="wait" else
             PrimitiveCommand("se_deplacer",{"direction":"west"})),
            PrimitiveCommand("attendre"),
        )
    raise ValueError("new commands not preregistered")


def capture(world,t):
    observer=SymbolicPerception()
    sensed=observer.capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(capture=sensed,is_night=world.is_night(t)).as_dict()


def replay_active(original):
    kind=original["kind"]
    variant=original["variant_lab_only"]
    followup=original["followup_precommitted"]
    food=original["initial_food"]
    at=tuple(original["initial_position"])
    if (kind not in KINDS or variant not in KINDS[kind]
        or followup not in STRATEGIES[kind]
        or food not in FOODS or at not in POSITIONS):
        raise ValueError("scenario not in preregistered experimental matrix")
    prefix=planned_prefix(kind,followup)
    if original["intended_prefix"]!=[c.as_dict() for c in prefix]:
        raise ValueError("original reported different commands")
    config,layout=independently_world(kind,variant,food,at)
    if (config.digest()!=original["config_sha256"]
        or digest(layout.as_dict())!=original["layout_sha256"]):
        raise ValueError("WorldPhysics configuration or hidden layout differs")
    world=WorldBody(config=config,layout=layout)
    if capture(world,1)!=original["initial_accessible"]:
        raise ValueError("initial cognition-facing capture not physically reproduced")
    archived=original["physical_records"]
    external_events=[]
    count=0
    death=None
    for step,command in enumerate(prefix,1):
        if kind=="food" and step==3:
            before_hidden=capture(world,step)
            if before_hidden!=original["first_eat_accessible_before_hidden_event"]:
                raise ValueError("original first-eat cognitive snapshot incorrect")
            if variant=="exogenous_confounded":
                event={
                    "between_physical_steps":[2,3],
                    "world_event":"set_danger_zone",
                    "position":{"x":at[0],"y":at[1]},
                    "active":True,
                    "not_an_i0_command":True,
                    "not_visible_in_capture":True,
                }
                # This WORLD intervention, not a command from I0, is
                # independently replayed. Its secret is never passed to Stage6.
                world.apply_scenario_event("set_danger_zone",{
                    "position":{"x":at[0],"y":at[1]},"active":True
                })
                external_events.append(event)
                if capture(world,step)!=before_hidden:
                    raise ValueError("hidden danger leaked to perception before eating")
        before=capture(world,step)
        outcome=world.apply(command,t_monde=step)
        after=capture(world,step+1)
        actual={
            "family":"laboratory_firstperson_"+kind,
            "state":before,
            "command":command.as_dict(),
            "observed_next_state":after,
            "terminal":outcome.lethal,
        }
        if step>len(archived):
            raise ValueError("physics produced extra nonterminal step")
        record=archived[step-1]
        if (record["step"]!=step
            or record["physical_example"]!=actual
            or record["physical_example_sha256"]!=digest(actual)
            or record["state_before"]!=before
            or record["state_after"]!=after
            or record["command"]!=command.as_dict()
            or record["terminal"]!=outcome.lethal):
            raise ValueError(f"physical replay divergent in {original['id']} at {step}")
        count+=1
        if outcome.lethal:
            death=step
            world.freeze_terminal_state()
            break
    if (count!=len(archived) or
        count!=original["physical_step_count"]
        or death!=original["first_terminal_step"]
        or external_events!=original["external_environment_interventions"]):
        raise ValueError("physical death, timing or external event trace diverged")
    return {"world_id":original["id"],"steps":count,"kind":kind,
            "death":death,"physical_examples_equal":True}


def replay_passive(original):
    kind=original["cue_kind"]
    pos=tuple(original["capture"][k] for k in ("x","y"))
    if pos not in POSITIONS or original["world_steps_applied"]!=0:
        raise ValueError("passive control world changed shape")
    cfg=standalone_config(food=40.0,position=pos)
    here=Position(*pos)
    if kind=="food_resource_visible":
        source=bool(original["intended_visible_indicator"])
        layout=WorldLayout(resources=((here,"berry_a",1),) if source else ())
    elif kind=="movement_obstacle_visible":
        source=bool(original["intended_visible_indicator"])
        layout=WorldLayout(
            obstacles=frozenset({here.moved("east")}) if source else frozenset()
        )
    else:
        raise ValueError("unknown preregistered passive control")
    if (cfg.digest()!=original["config_sha256"]
        or digest(layout.as_dict())!=original["layout_sha256"]):
        raise ValueError("passive physics or layout digest not valid")
    world=WorldBody(config=cfg,layout=layout)
    if capture(world,1)!=original["capture"]:
        raise ValueError("passive perceptual capture false")
    cue=(
        "berry_a" in original["capture"]["current_resources"]
        if kind=="food_resource_visible" else
        not next(n["passable"] for n in original["capture"]["adjacent"]
                 if n["direction"]=="east")
    )
    if cue!=source or original["detected_from_accessible_state"]!=source:
        raise ValueError("passive cognitive observation falsely labelled")
    return {"world_id":original["id"],"steps":0,
            "passive_only":True}


def read_source(folder:Path):
    sources={}
    for name,d in EXPECTED.items():
        files=list(folder.rglob(name))
        if len(files)!=1:
            raise ValueError("original archived S physical source missing/ambiguous")
        data=files[0].read_bytes()
        if sha256(data).hexdigest()!=d:
            raise ValueError("frozen original source SHA changed: "+name)
        sources[name]=json.loads(data)
    return sources


def replay_all(acted,passive,summary):
    if (summary.get("schema")!="a230s-firstperson-controlled-information-v1"
        or summary.get("analysis_code_sha")!=SOURCE_SHA
        or len(acted)!=64 or len(passive)!=8):
        raise ValueError("not the preregistered original S firstperson battery")
    seen=set()
    cases=[]
    for row in acted:
        event=replay_active(row)
        if event["world_id"] in seen:
            raise ValueError("same world replayed twice")
        seen.add(event["world_id"])
        cases.append(event)
    for row in passive:
        event=replay_passive(row)
        if event["world_id"] in seen:
            raise ValueError("passive/physical world identity reused")
        seen.add(event["world_id"])
        cases.append(event)
    steps=sum(c["steps"] for c in cases)
    deaths=Counter(c["kind"] for c in cases
                   if c.get("death") is not None)
    if (len(seen),steps,dict(deaths))!=(72,196,{"food":8,"movement":16}):
        raise ValueError("replay differs in mortal physical/observational cohort")
    if summary["actual_lab_physical_steps"]!=steps:
        raise ValueError("published physical step total differs from replay")
    return {
        "original_P_source_run":ORIGINAL_S_RUN,
        "original_S_source_sha":SOURCE_SHA,
        "physical_technical_worlds_reinstantiated":len(seen),
        "physical_technical_steps_replayed":steps,
        "original_acting_worlds_replayed":64,
        "original_passive_worlds_recaptured":8,
        "original_24_terminal_worlds_verified":sum(deaths.values()),
        "physical_replay_differences":0,
        "postterminal_actions":0,
        "new_independent_scientific_conditions":0,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "oracle_to_I0_feedback":False,
        "original_stage6_shadow_unchanged":True,
        "physical_model_not_natural_world_truth":True,
        "stage12":"PARTIAL",
    }


def execute(source:Path,output:Path):
    x=read_source(source)
    res=replay_all(
        x["a230s-acted-worlds.json"],
        x["a230s-passive-worlds.json"],
        x["a230s-summary.json"],
    )
    res.update({
        "schema":"a230u-standalone-physical-replay-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "original_json_sha256":EXPECTED,
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230u-summary.json").write_text(
        json.dumps(res,sort_keys=True,indent=2)+"\n"
    )
    print("A230U_SUMMARY "+json.dumps({
        k:v for k,v in res.items() if k!="original_json_sha256"
    },sort_keys=True),flush=True)
    return res


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",required=True,type=Path)
    parser.add_argument("--output-dir",required=True,type=Path)
    opts=parser.parse_args()
    execute(opts.source_dir,opts.output_dir)


if __name__=="__main__":
    main()
