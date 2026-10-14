"""A2.17b: lab-only proximal collection cue against distal food confounding.

WorldBody.apply supplies the real physical effects; the candidate classifier
receives only first-person captures and the prior command, never scenario truth.
"""
from dataclasses import replace
import argparse
import json
from pathlib import Path
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.determinism import sha256_hex, canonical_causal_bytes
from lab.world import Position, WorldBody, WorldLayout

SEEDS=tuple(range(81,89))
CONDITIONS=("present","absent","forced_failure","failure_external_food_gain",
            "success_external_food_loss")

def capture(world,t):
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry())

def proximal_collection_cue(*, command, before, after):
    """Probe only, NOT a replacement for GoalAgencyService's distal judgement."""
    target=command.parameters.get("target")
    if command.primitive!="collecter" or target not in ("berry_a","berry_b"):
        return "unknown"
    b=before.inventory.get(target)
    a=after.inventory.get(target)
    if (type(b) is int and type(a) is int and a>b
            and (before.x,before.y)==(after.x,after.y)):
        return "self_proximal_candidate"
    return "unknown"

def scenario(base,seed,condition):
    rng=random.Random(seed*809+CONDITIONS.index(condition)*101)
    p=Position(rng.randint(5,22),rng.randint(5,22))
    has_resource=condition not in ("absent",)
    layout=WorldLayout(resources=((p,"berry_a",1),) if has_resource else ())
    world=WorldBody(config=replace(base,initial_position=p),layout=layout)
    before=capture(world,1)
    cmd=PrimitiveCommand("collecter",{"target":"berry_a"})
    owner=GoalAgencyService()
    owner.preregister(
        assessment_ref=f"assessment:{seed}:{condition}",
        intent_ref=f"intent:{seed}:{condition}",life_id=f"life:{seed}:{condition}",
        goal_ref="goal:food",option_ref="option:collect",
        command_hash=sha256_hex(canonical_causal_bytes(cmd.as_dict())),
        world_step=1,measure="food",command=cmd,capture=before)
    if condition in ("forced_failure","failure_external_food_gain"):
        world.apply_scenario_event("set_action_failure_schedule",
            {"primitive":"collecter","schedule":[True]})
    applied=world.apply(cmd,t_monde=1)
    if condition=="failure_external_food_gain":
        world.apply_scenario_event("set_body",
            {"food":min(99.0,before.body["food"]+12.0)})
    if condition=="success_external_food_loss":
        world.apply_scenario_event("set_body",
            {"food":max(0.0,before.body["food"]-12.0)})
    after=capture(world,2)
    judged=owner.evaluate(capture=after,world_step=2,
                          cue_ref=f"physical:capture:{seed}:2",paid=True)
    candidate=proximal_collection_cue(command=cmd,before=before,after=after)
    return {
        "seed":seed,"condition":condition,
        "physical_transition_hash":sha256_hex(
            canonical_causal_bytes(applied.as_dict())),
        "before_inventory":before.inventory.get("berry_a",0),
        "after_inventory":after.inventory.get("berry_a",0),
        "before_food":before.body["food"],
        "after_food":after.body["food"],
        "physical_effects":dict(applied.effects),
        "first_person_owner_judgement":judged.subjective_agency,
        "proximal_probe":candidate,
        "distal_agency_inferred":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    cfg=build_stage11_reference_runtime().world.config
    rows=[]
    for condition in CONDITIONS:
        for seed in SEEDS:
            row=scenario(cfg,seed,condition)
            (args.output_dir/f"{condition}-{seed}.json").write_text(
                json.dumps(row,indent=2,sort_keys=True)+"\n")
            rows.append(row)
    count={}
    for c in CONDITIONS:
        subset=[row for row in rows if row["condition"]==c]
        count[c]={
            "worlds":len(subset),
            "owner_unknown":sum(row["first_person_owner_judgement"]=="unknown"
                                for row in subset),
            "proximal_self_candidates":sum(
                row["proximal_probe"]=="self_proximal_candidate"
                for row in subset),
            "external_food_increase":sum(row["after_food"]>row["before_food"]
                                         for row in subset),
        }
    summary={"schema":"a217b-proximal-distal-physical-v1",
             "code_sha":subprocess.check_output(
                 ["git","rev-parse","HEAD"],text=True).strip(),
             "seeds":list(SEEDS),"physical_worlds":len(rows),
             "actual_physical_transitions":len(rows),
             "conditions":count,"runtime_policy_changed":False,
             "subjective_distal_agency_accepted":False,
             "stage12":"PARTIAL","operator_accepted":False}
    (args.output_dir/"a217b-summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A217B_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    assert len(rows)==40
    assert all(v["owner_unknown"]==8 for v in count.values())
    assert count["present"]["proximal_self_candidates"]==8
    assert count["success_external_food_loss"]["proximal_self_candidates"]==8
    for condition in ("absent","forced_failure","failure_external_food_gain"):
        assert count[condition]["proximal_self_candidates"]==0
    assert count["failure_external_food_gain"]["external_food_increase"]==8
    assert count["success_external_food_loss"]["external_food_increase"]==0

if __name__=="__main__":
    main()
