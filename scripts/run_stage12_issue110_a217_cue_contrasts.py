"""A2.17 physical contrast: compare accessible cues, not operator causal truth.

This is an isolated Action-Control owner exercise over real WorldBody.apply
transitions, NOT autonomous Stage12 policy learning or 600-step lives.
"""
import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout

SEEDS=tuple(range(71,79))
CONDITIONS=(
    "collect_available",
    "collect_absent",
    "collect_forced_failure",
    "move_success",
    "move_external_obstacle",
    "move_forced_failure",
)

def run_one(config,seed,condition):
    rng=random.Random(seed*811+CONDITIONS.index(condition)*4999)
    origin=Position(rng.randint(4,20),rng.randint(4,20))
    target=origin.moved("east")
    collect=condition.startswith("collect_")
    layout=WorldLayout(
        resources=((origin,"berry_a",1),) if collect and
            condition!="collect_absent" else (),
        water_sources=frozenset({target}) if not collect else frozenset(),
    )
    world=WorldBody(config=replace(config,initial_position=origin),layout=layout)
    perception=SymbolicPerception()
    before=perception.capture(
        local_state=world.capture_local(t_monde=1).as_dict(),
        telemetry=world.telemetry())
    command=(
        PrimitiveCommand("collecter",{"target":"berry_a"}) if collect
        else PrimitiveCommand("se_deplacer",{"direction":"east"})
    )
    owner=GoalAgencyService()
    commitment=owner.preregister(
        assessment_ref=f"assessment:{seed}:{condition}",
        intent_ref=f"intent:{seed}:{condition}",
        life_id=f"physical-test:{seed}:{condition}",
        goal_ref="goal:food" if collect else "goal:water",
        option_ref="option:controlled",
        command_hash=sha256_hex(canonical_causal_bytes(command.as_dict())),
        world_step=1,
        measure="food" if collect else "spatial_distance",
        command=command,capture=before,
        spatial_target=(target.x,target.y,"water") if not collect else None)
    if condition=="move_external_obstacle":
        world.apply_scenario_event("set_obstacle",{
            "position":target.as_dict(),"active":True})
    if condition in ("collect_forced_failure","move_forced_failure"):
        world.apply_scenario_event("set_action_failure_schedule",{
            "primitive":command.primitive,"schedule":[True]})
    effect=world.apply(command,t_monde=1)
    after=perception.capture(
        local_state=world.capture_local(t_monde=2).as_dict(),
        telemetry=world.telemetry())
    # Physical falsification guards: no judgement counts as a useful
    # contrast if the relevant WorldBody action did not really occur.
    if condition=="collect_available":
        assert after.inventory.get("berry_a",0)==before.inventory.get("berry_a",0)+1
        assert effect.effects.get("collected",{}).get("quantity")==1
    elif condition in ("collect_absent","collect_forced_failure"):
        assert after.inventory.get("berry_a",0)==before.inventory.get("berry_a",0)
        if condition=="collect_forced_failure":
            assert effect.effects.get("scenario_forced_failure")=="collecter"
    elif condition=="move_success":
        assert (after.x,after.y)==(target.x,target.y)
        assert effect.effects.get("movement")=="moved"
    else:
        assert (after.x,after.y)==(origin.x,origin.y)
        if condition=="move_external_obstacle":
            assert next(c for c in before.adjacent if c.direction=="east").passable
            assert not next(c for c in after.adjacent if c.direction=="east").passable
            assert effect.effects.get("movement")=="blocked"
        if condition=="move_forced_failure":
            assert effect.effects.get("scenario_forced_failure")=="se_deplacer"
            assert next(c for c in after.adjacent if c.direction=="east").passable
    judgement=owner.evaluate(
        capture=after,world_step=2,
        cue_ref=f"physical-witness:{seed}:{condition}:2",paid=True)
    assert judgement is not None
    return {
        "seed":seed,"condition":condition,
        "before_position":(before.x,before.y),
        "after_position":(after.x,after.y),
        "inventory_before":before.inventory.get("berry_a",0),
        "inventory_after":after.inventory.get("berry_a",0),
        "before_visible_east_passable":next(
            c.passable for c in before.adjacent if c.direction=="east"),
        "after_visible_east_passable":next(
            c.passable for c in after.adjacent if c.direction=="east"),
        "owner_commitment_hash":sha256_hex(
            canonical_causal_bytes(commitment.as_dict())),
        "physical_transition_hash":sha256_hex(
            canonical_causal_bytes(effect.as_dict())),
        "physical_effects":dict(effect.effects),
        "subjective_agency":judgement.subjective_agency,
        "reason":judgement.reason,
        "perceptual_cue_ref":judgement.cue_ref,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    config=build_stage11_reference_runtime().world.config
    outputs=[]
    for seed in SEEDS:
        for condition in CONDITIONS:
            row=run_one(config,seed,condition)
            (args.output_dir/f"{condition}-{seed}.json").write_text(
                json.dumps(row,sort_keys=True,indent=2)+"\n")
            outputs.append(row)
    expected={
        "collect_available":"unknown",
        "collect_absent":"unknown",
        "collect_forced_failure":"unknown",
        "move_success":"self",
        "move_external_obstacle":"world",
        "move_forced_failure":"unknown",
    }
    mismatches=[x for x in outputs
                if x["subjective_agency"]!=expected[x["condition"]]]
    by_condition={
        key:dict(sorted(Counter(x["subjective_agency"] for x in outputs
                                if x["condition"]==key).items()))
        for key in CONDITIONS
    }
    result={
        "schema":"stage12-a217-physical-cue-contract-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True).strip(),
        "seeds":list(SEEDS),"conditions":list(CONDITIONS),
        "physical_worlds":len(outputs),
        "physical_transitions":len(outputs),
        "owner_judgements":len(outputs),
        "by_condition":by_condition,
        "unexpected_judgements":len(mismatches),
        "stage12_verdict":"PARTIAL","operator_reception":False,
        "runtime_policy_changed":False,
    }
    (args.output_dir/"a217-summary.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("A217_SUMMARY "+json.dumps(result,sort_keys=True),flush=True)
    return 0 if len(outputs)==48 and not mismatches else 2

if __name__=="__main__":
    raise SystemExit(main())
