"""A2.30-ZR: independent pure WorldBody technical reproduction of Z.

Reconstructs a FRESH detached physics world for each of the 168 sealed Z
conditions. It does NOT import the Z producer runner, policy code, Equipment
recorder, Stage6, Oracle, Bench or any living I0 runtime.

244 newly executed technical physical commands are a replay of the SAME
deterministic cells, NOT independent new scientific samples. Always stop
after the first lethal WorldBody.apply. Terminal sensor capture remains
operator-only, never a lived future observation.
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
    BerryEffect, BodyState, Position, PRIMITIVE_ACTIONS,
    ToolRecipe, WorldBody, WorldLayout, WorldPhysicsConfig,
)

SOURCE_RUN = 38760713470
ORIGINAL_SHA = "0d9fd7cd511640103498f037b84cae915169356e"
SOURCES = {
    "a230z-physical-worlds.json":
        "09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d",
    "a230z-summary.json":
        "170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c",
}
KINDS=(
    "A_ONLY","B_LOCAL","B_EAST_BLOCKED","B_EAST_ADJACENT",
    "B_EAST_TWO_STEPS",
)
APPROACHES=("OBSERVED_ONLY","SINGLE_EAST_PROBE")
VALID_A={"benign","toxin_7","toxin_30","toxin_100","gain_zero"}
VALID_B={"benign","toxin_7","toxin_100","gain_zero"}
EAST=PrimitiveCommand("se_deplacer",{"direction":"east"})
COLLECT=PrimitiveCommand("collecter",{"target":"berry_b"})
EAT=PrimitiveCommand("manger",{"target":"berry_b"})


def digest(x):
    return sha256_hex(canonical_causal_bytes(x))


def read_original(dir:Path):
    loaded={}
    for filename,sha in SOURCES.items():
        hits=list(dir.rglob(filename))
        if len(hits)!=1:
            raise ValueError("missing or ambiguous sealed original Z file")
        raw=hits[0].read_bytes()
        if sha256(raw).hexdigest()!=sha:
            raise ValueError("sealed original Z SHA-256 changed")
        loaded[filename]=json.loads(raw)
    return loaded


def reconstruct_physics(kind,latent,initial_food,position):
    """Explicitly rederive the L base fixture and all Z overrides.

    This is written independently of the producer's build_physics. It does
    not read its source or results to choose physics effects.
    """
    if kind not in KINDS:
        raise ValueError("unknown preregistered physical layout")
    if latent not in (VALID_A if kind=="A_ONLY" else VALID_B):
        raise ValueError("unpreregistered latent effect")
    if initial_food not in (35.0,45.0) or tuple(position) not in (
        (5,5),(7,7)
    ):
        raise ValueError("changed preregistered physical initial condition")
    start=Position(*position)
    reference=WorldPhysicsConfig(
        version="stage12-a230l-standalone-physics-v1",
        width=32,height=32,day_steps=300,night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0,food=60.0,water=20.0,integrity=100.0
        ),
        initial_position=Position(2,2),
        food_decay_per_step=0.0,water_decay_per_step=0.0,
        action_energy_costs={key:0.0 for key in sorted(PRIMITIVE_ACTIONS)},
        sleep_energy_gain=0.0,rest_integrity_gain=0.0,
        drink_water_gain=40.0,
        berry_effects={
            "berry_a":BerryEffect(food_gain=10.0,integrity_delta=0.0),
            "berry_b":BerryEffect(food_gain=5.0,integrity_delta=-100.0),
        },
        creature_damage=0.0,danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1,1,2),
    )
    action_costs=dict(reference.action_energy_costs)
    action_costs["se_deplacer"]=1.0
    action_costs["collecter"]=0.75
    action_costs["manger"]=0.5
    action_costs["attendre"]=0.5
    if kind=="A_ONLY":
        a_effect=BerryEffect(
            food_gain=0.0 if latent=="gain_zero" else 10.0,
            integrity_delta={
                "benign":0.0,"toxin_7":-7.0,"toxin_30":-30.0,
                "toxin_100":-100.0,"gain_zero":0.0,
            }[latent],
        )
        b_effect=BerryEffect(food_gain=12.0,integrity_delta=0.0)
    else:
        a_effect=BerryEffect(food_gain=10.0,integrity_delta=-100.0)
        b_effect=BerryEffect(
            food_gain=0.0 if latent=="gain_zero" else 12.0,
            integrity_delta={
                "benign":0.0,"toxin_7":-7.0,
                "toxin_100":-100.0,"gain_zero":0.0,
            }[latent],
        )
    physics=replace(
        reference,
        version="stage12-a230z-alternative-food-pure-world-v1",
        initial_position=start,
        initial_body=replace(reference.initial_body,food=initial_food),
        food_decay_per_step=0.5,water_decay_per_step=0.2,
        rest_integrity_gain=0.0,
        action_energy_costs=action_costs,
        berry_effects={"berry_a":a_effect,"berry_b":b_effect},
    )
    east=start.moved("east")
    resources=[(start,"berry_a",2)]
    if kind=="B_LOCAL":
        resources.append((start,"berry_b",2))
    if kind in ("B_EAST_BLOCKED","B_EAST_ADJACENT"):
        resources.append((east,"berry_b",2))
    if kind=="B_EAST_TWO_STEPS":
        resources.append((east.moved("east"),"berry_b",2))
    layout=WorldLayout(
        resources=tuple(resources),
        obstacles=(frozenset({east}) if kind=="B_EAST_BLOCKED"
                   else frozenset()),
    )
    physics.validate()
    layout.validate(physics)
    return physics,layout


def capture_accessible(body:WorldBody,t:int):
    senses=SymbolicPerception().capture(
        local_state=body.capture_local(t_monde=t).as_dict(),
        telemetry=body.telemetry(),
    )
    return state_from_capture(
        capture=senses, is_night=body.is_night(t),
    )


def independently_choose_action(state,protocol,completed):
    """Only accessible body/neighbor/local resource and past commands."""
    if protocol not in APPROACHES:
        raise ValueError("unknown lab decision program")
    if EAT in completed:
        return None,"already_consumed_one_berry_b"
    if state.inventory.get("berry_b",0)>0:
        return EAT,"held_berry_b_accessible"
    if "berry_b" in state.current_resources:
        return COLLECT,"local_berry_b_visible"
    adjacent=[x for x in state.adjacent if x.direction=="east"]
    if len(adjacent)!=1:
        raise ValueError("missing east local perception")
    east=adjacent[0]
    if "berry_b" in east.resources:
        return (EAST,"eastern_berry_b_visible_passable") if east.passable else (
            None,"eastern_berry_b_visible_but_blocked"
        )
    if protocol=="SINGLE_EAST_PROBE" and not completed and east.passable:
        return EAST,"one_blind_eastern_probe"
    return None,"no_visible_accessible_berry_b_abstain"


def physical_replay_one(source):
    name=source["world_id"]
    kind=source["layout_external_only"]
    policy=source["protocol_precommitted"]
    hidden=source["latent_berry_effect_external_only"]
    position=tuple(source["initial_position"])
    food=source["initial_food"]
    expected_name=(
        f"a230z:{kind}:{policy}:{hidden}:food{int(food)}:"
        f"x{position[0]}y{position[1]}"
    )
    if name!=expected_name or policy not in APPROACHES:
        raise ValueError("physical original world identity mismatch")
    physics,layout=reconstruct_physics(kind,hidden,food,position)
    if (physics.digest()!=source["config_sha256_external_only"]
        or digest(layout.as_dict())!=source["layout_sha256_external_only"]):
        raise ValueError("preregistered physical configuration/layout SHA changed")
    # Crucially create a NEW physical world, do not import or restore
    # any historical I0 or WorldBody life.
    world=WorldBody(config=physics,layout=layout)
    expected_receipts=source["physical_steps_external"]
    expected_choices=source["perceptual_policy_choices"]
    original=source["initial_first_person"]
    initial_capture=capture_accessible(world,1).as_dict()
    if initial_capture!=original or digest(initial_capture)!=source[
        "initial_first_person_sha256"
    ]:
        raise ValueError("independently observed initial perception mismatch")
    commands=[]
    lived=[{"t_monde":1,"state":initial_capture}]
    actual_acts=0
    death_t=None
    before_eat=None
    after_eat=None
    for t in range(1,6):
        state=capture_accessible(world,t)
        perceptible=state.as_dict()
        allowed,reason=independently_choose_action(
            state,policy,tuple(commands)
        )
        if t>len(expected_choices):
            raise ValueError("original action/abstention log truncated")
        claimed=expected_choices[t-1]
        if (claimed["t_monde"]!=t
            or claimed["input_accessible_state"]!=perceptible
            or claimed["input_sha256"]!=digest(perceptible)
            or claimed["previous_actually_executed_commands"]!=[
                x.as_dict() for x in commands
            ]
            or claimed["decision_reason_from_observation_only"]!=reason
            or claimed["command"]!=(
                None if allowed is None else allowed.as_dict()
            )
            or claimed["certifies_safe"] is not False):
            raise ValueError("first-person physical command does not match protocol")
        if allowed is None:
            if t!=len(expected_choices):
                raise ValueError("invented extra decisions after physical abstention")
            break
        if t>4 or t>len(expected_receipts):
            raise ValueError("unrecorded physical action or postmortem attempt")
        before=perceptible
        result=world.apply(allowed,t_monde=t)
        physically_after=capture_accessible(world,t+1).as_dict()
        receipt={
            "family":"a230z_physically_executed_alternative",
            "state":before,
            "command":allowed.as_dict(),
            "observed_next_state":physically_after,
            "terminal":result.lethal,
        }
        archived=expected_receipts[t-1]
        if (archived["t_monde"]!=t
            or archived["command"]!=allowed.as_dict()
            or archived["state_before"]!=before
            or archived["physical_after_external_only"]!=physically_after
            or archived["terminal_external_only"] is not result.lethal
            or archived["physical_example"]!=receipt
            or archived["physical_example_sha256"]!=digest(receipt)):
            raise ValueError("physical WorldBody.apply replay contradicts archived receipt")
        commands.append(allowed)
        actual_acts+=1
        if allowed==EAT:
            before_eat=before
            after_eat=physically_after
        if result.lethal:
            death_t=t
            world.freeze_terminal_state()
            # Never ask a dead WorldBody to act or use its terminal capture
            # for a future subjective decision.
            break
        lived.append({"t_monde":t+1,"state":physically_after})
    if (actual_acts!=len(expected_receipts)
        or actual_acts!=source["physical_step_count"]
        or death_t!=source["physical_terminal_step_external_only"]
        or lived!=source["lived_states_while_alive"]
        or source["lived_postterminal_capture"] is not None):
        raise ValueError("wrong replay lifetime, terminal moment or lived captures")
    if (before_eat!=source["pre_ingestion_lived_state"]
        or after_eat!=source["post_ingestion_external_only"]
        or (before_eat is not None)!=source["ingested_berry_b_external"]):
        raise ValueError("ingestion fixture not witnessed in reproduced physics")
    if after_eat is None:
        achieved=False
        insufficient=False
    else:
        gained=after_eat["body"]["food"]-before_eat["body"]["food"]
        achieved=death_t is None and gained>=5.0
        insufficient=death_t is None and not achieved
    if (source["food_success_with_survival_external"] is not achieved
        or source["insufficient_food_with_survival_external"] is not insufficient):
        raise ValueError("false physical food-goal success or masked harm")
    body=(expected_receipts[-1]["physical_after_external_only"]["body"]
          if expected_receipts else original["body"])
    delta={
        x:round(float(body[x])-float(original["body"][x]),8)
        for x in ("energy","food","water","integrity")
    }
    if delta!=source["physical_body_delta_external"]:
        raise ValueError("physical resource cost diverged")
    return {
        "id":name,
        "layout":kind,
        "protocol":policy,
        "physical_replayed_actions":actual_acts,
        "physically_terminal":death_t is not None,
        "food_success":achieved,
        "physical_lived_histories_equal":True,
        "original_lab_receipts_exactly_reproduced":True,
    }


def repeat_all(original):
    if (len(original["a230z-physical-worlds.json"])!=168
        or original["a230z-summary.json"].get("analysis_code_sha")!=ORIGINAL_SHA):
        raise ValueError("not an authentic original preregistered Z scientific cohort")
    items=original["a230z-physical-worlds.json"]
    reports=[]
    ids=set()
    for source in items:
        found=physical_replay_one(source)
        if found["id"] in ids:
            raise ValueError("same world identifier duplicated in original source")
        ids.add(found["id"])
        reports.append(found)
    evidence={
        "original_unique_scientific_scenarios":len(ids),
        "technical_new_worldbody_instances":len(reports),
        "technical_repeated_worldbody_applications":sum(
            v["physical_replayed_actions"] for v in reports
        ),
        "technical_terminal_transitions":sum(
            v["physically_terminal"] for v in reports
        ),
        "technical_reproduced_food_successes":sum(
            v["food_success"] for v in reports
        ),
        "technical_physical_receipt_discrepancies":0,
        "postterminal_actions_attempted":0,
        "new_independent_scientific_conditions":0,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "real_I0_UC_cost_measured":False,
        "source_physics_not_external_natural_world":True,
        "model_deployed_to_I0":False,
        "stage12":"PARTIAL","issue110":"OPEN",
    }
    if (evidence["technical_new_worldbody_instances"]!=168
        or evidence["technical_repeated_worldbody_applications"]!=244
        or evidence["technical_terminal_transitions"]!=20
        or evidence["technical_reproduced_food_successes"]!=40):
        raise ValueError("replayed physics did not reproduce preregistered counts")
    return evidence


def execute(source:Path,output:Path):
    sealed=read_original(source)
    study=repeat_all(sealed)
    study.update({
        "schema":"a230zr-independent-pure-physics-replay-v1",
        "source_original_run":SOURCE_RUN,
        "original_source_code_sha":ORIGINAL_SHA,
        "source_json_sha256":SOURCES,
        "analysis_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
    })
    output.mkdir(parents=True,exist_ok=False)
    (output/"a230zr-technical-replay.json").write_text(
        json.dumps(study,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZR_SUMMARY "+json.dumps({
        k:v for k,v in study.items() if k!="source_json_sha256"
    },sort_keys=True),flush=True)
    return study


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    args=ap.parse_args()
    execute(args.source_dir,args.output_dir)


if __name__=="__main__":
    main()
