"""A2.17: true physical action/observation controls; no inferred external blame.

Uses physically applied WorldBody actions, separate random world births,
owner-local first-person commitments, and independently reports their effects.
Does not change the cognitive model or feed ground truth to it.
"""
from dataclasses import replace
import argparse
import json
from pathlib import Path
import random

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout


def capture(world, step):
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry())


def make_world(config, position, has_berry, *, obstacle=False):
    return WorldBody(config=replace(config,initial_position=position),
        layout=WorldLayout(
            resources=((position,"berry_a",1),) if has_berry else (),
            obstacles=frozenset({position.moved("east")}) if obstacle else frozenset(),
        ))


def run_case(config, *, family, seed):
    rng=random.Random(seed*101+17)
    origin=Position(rng.randint(6,19),rng.randint(6,19))
    is_collect=family in ("collect_present","collect_absent","collect_removed")
    has_berry=family in ("collect_present","collect_removed")
    world=make_world(config,origin,has_berry,
                     obstacle=(family=="move_blocked"))
    first=capture(world,1)
    command=(PrimitiveCommand("collecter",{"target":"berry_a"})
             if is_collect else PrimitiveCommand("se_deplacer",{"direction":"east"}))
    service=GoalAgencyService()
    spatial=None
    if family in ("move_free","move_blocked","move_new_block"):
        # The spatial goal needs a genuine perceptual target. Use a water
        # resource on the adjacent cell in physically separate worlds.
        world=WorldBody(config=replace(config,initial_position=origin),
            layout=WorldLayout(
                water_sources=frozenset({origin.moved("east")}),
                obstacles=frozenset({origin.moved("east")})
                          if family=="move_blocked" else frozenset(),
            ))
        first=capture(world,1)
        spatial=(origin.x+1,origin.y,"water")
    commitment=service.preregister(
        assessment_ref="assessment:1",intent_ref="intent:1",
        life_id="life:1",goal_ref="goal:1",option_ref="option:1",
        command_hash="digest:observed",world_step=1,
        measure="food" if is_collect else "spatial_distance",
        command=command,capture=first,spatial_target=spatial)
    if family=="move_new_block":
        world.apply_scenario_event("set_obstacle",{
            "position":origin.moved("east").as_dict(),"active":True})
    if family=="collect_removed":
        # Removal is physical world intervention; this is NOT a causal
        # truth made accessible to I0. Only its next percept is used.
        world.apply_scenario_event("remove_resource",{
            "position":origin.as_dict(),"kind":"berry_a"})
    result=world.apply(command,t_monde=1)
    next_capture=capture(world,2)
    judged=service.evaluate(capture=next_capture,world_step=2,
                            cue_ref="observed:perceptual:2",paid=True)
    return {
        "family":family,"seed":seed,"judgement":judged.subjective_agency,
        "judgement_reason":judged.reason,"mechanism":commitment.mechanism,
        "physical_effects":dict(result.effects),
        "physical_delta":{"x":result.position_after.x-origin.x,
                          "y":result.position_after.y-origin.y},
        "cue_ref_attested":judged.cue_ref is not None,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    config=build_stage11_reference_runtime().world.config
    families=("collect_present","collect_absent","collect_removed",
              "move_free","move_blocked","move_new_block")
    rows=[run_case(config,family=f,seed=s) for f in families
          for s in range(61,69)]
    by_family={}
    for f in families:
        records=[r for r in rows if r["family"]==f]
        by_family[f]={"agency":sorted(set(r["judgement"] for r in records)),
                      "reasons":sorted(set(r["judgement_reason"] for r in records)),
                      "n":len(records)}
    report={"schema":"a217-physical-first-person-contrast-v1",
            "worlds":len(rows),"families":by_family,
            "rows":rows,"stage12":"PARTIAL","operator_accepted":False}
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("A217_SUMMARY "+json.dumps({"worlds":len(rows),"families":by_family},
                                    sort_keys=True),flush=True)
    assert len(rows)==48
    assert all(r["judgement"]=="unknown" for r in rows if r["family"].startswith("collect_"))
    assert all(r["judgement"]=="self" for r in rows if r["family"]=="move_free")
    assert all(r["judgement"]=="world" for r in rows if r["family"]=="move_blocked")
    assert all(r["judgement"]=="world" for r in rows if r["family"]=="move_new_block")


if __name__=="__main__":
    main()
