"""A2.17b: observable equivalence can hide an externally caused displacement.

This is an external physical laboratory, not an autonomous 600-step agent life.
"""
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path
import argparse
import json
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import WorldBody, WorldLayout, Position

SEEDS=tuple(range(81,89))
CONDITIONS=("normal_move","forced_failure","forced_failure_external_relocation")

def trial(config,seed,condition):
    rng=random.Random(seed*991)
    origin=Position(rng.randint(5,20),rng.randint(5,20))
    target=origin.moved("east")
    world=WorldBody(config=replace(config,initial_position=origin),
                    layout=WorldLayout(water_sources=frozenset({target})))
    observe=SymbolicPerception()
    before=observe.capture(
        local_state=world.capture_local(t_monde=1).as_dict(),
        telemetry=world.telemetry())
    cmd=PrimitiveCommand("se_deplacer",{"direction":"east"})
    owner=GoalAgencyService()
    commitment=owner.preregister(
        assessment_ref=f"assessment:{seed}:{condition}",
        intent_ref=f"intent:{seed}:{condition}",
        life_id=f"physical-only:{seed}:{condition}",
        goal_ref="goal:water",option_ref="option:move",
        command_hash=sha256_hex(canonical_causal_bytes(cmd.as_dict())),
        world_step=1,measure="spatial_distance",
        command=cmd,capture=before,
        spatial_target=(target.x,target.y,"water"))
    if condition!="normal_move":
        world.apply_scenario_event("set_action_failure_schedule",{
            "primitive":"se_deplacer","schedule":[True]})
    actual=world.apply(cmd,t_monde=1)
    physical_after_command=world.position.as_dict()
    relocation=None
    if condition=="forced_failure_external_relocation":
        relocation={"operation":"set_position","position":target.as_dict()}
        world.apply_scenario_event("set_position",{"position":target.as_dict()})
    after=observe.capture(
        local_state=world.capture_local(t_monde=2).as_dict(),
        telemetry=world.telemetry())
    judgment=owner.evaluate(
        capture=after,world_step=2,cue_ref=f"perceived:2:{seed}:{condition}",
        paid=True)
    if judgment is None or judgment.cue_ref is None:
        raise AssertionError("first-person perception or payment absent")
    if condition=="normal_move":
        assert actual.effects.get("movement")=="moved"
        assert physical_after_command==target.as_dict()
    else:
        assert actual.effects.get("scenario_forced_failure")=="se_deplacer"
        assert physical_after_command==origin.as_dict()
    expected_position=(origin if condition=="forced_failure" else target)
    assert (after.x,after.y)==(expected_position.x,expected_position.y)
    return {
        "seed":seed,"condition":condition,"pre_percept":asdict(before),
        "post_percept":asdict(after),
        "pre_percept_sha256":sha256_hex(canonical_causal_bytes(asdict(before))),
        "post_percept_sha256":sha256_hex(canonical_causal_bytes(asdict(after))),
        "owner_commitment_hash":sha256_hex(canonical_causal_bytes(commitment.as_dict())),
        "physical_command_transition_sha256":sha256_hex(canonical_causal_bytes(actual.as_dict())),
        "physical_action_effects":dict(actual.effects),
        "physical_after_command":physical_after_command,
        "operator_external_relocation":relocation,
        "subjective_agency":judgment.subjective_agency,
        "subjective_reason":judgment.reason,
        "cue_ref":judgment.cue_ref,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    config=build_stage11_reference_runtime().world.config
    counter={"normal_move":{"self":0},"forced_failure":{"unknown":0},
             "forced_failure_external_relocation":{"self":0}}
    errors=0
    for seed in SEEDS:
        entries={condition:trial(config,seed,condition)
                 for condition in CONDITIONS}
        normal=entries["normal_move"]
        confounded=entries["forced_failure_external_relocation"]
        if (normal["pre_percept"]!=confounded["pre_percept"] or
            normal["post_percept"]!=confounded["post_percept"]):
            raise AssertionError("external relocation not perceptually equivalent")
        for condition,row in entries.items():
            expected=("unknown" if condition=="forced_failure" else "self")
            if row["subjective_agency"]!=expected:
                errors+=1
            counter[condition][expected]+=int(row["subjective_agency"]==expected)
            (args.output_dir/f"{condition}-{seed}.json").write_text(
                json.dumps(row,indent=2,sort_keys=True)+"\n")
    summary={
        "schema":"stage12-a217b-subjective-physical-confounding-v1",
        "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],
                                             text=True).strip(),
        "seeds":list(SEEDS),"physical_worlds":24,
        "voluntary_physical_command_attempts":24,
        "external_relocations":8,
        "perceptually_indistinguishable_confounded_pairs":8,
        "judgements":counter,"unexpected_judgements":errors,
        "stage12":"PARTIAL","operator_reception":False,
        "runtime_policy_changed":False,
    }
    (args.output_dir/"a217b-summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A217B_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    return 0 if errors==0 else 2

if __name__=="__main__":
    raise SystemExit(main())
