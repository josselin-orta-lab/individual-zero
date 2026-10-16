"""A2.30-P: standalone physical experimental cohort for delayed joint hazards.

PREREGISTERED before code at fbc735bfef3f0b285c4eb1989a3547f5b7710957.
128 DISTINCT detached WorldBody worlds, 352 expected physical applications.
No I0 birth, no WorldBody state or Oracle fed into the frozen model, no
continued transition after death, no Stage6 or Stage12 decision execution.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import subprocess

from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout
from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config
from audit_stage12_issue110_b_a230p_joint_trajectories import (
    JointStep, LaboratoryJointPrefixModel, PhysicalPrefixWitness,
    cumulative_observable_deltas, score_heldout,
)

TRAIN_FOOD = (30.0,40.0)
TRAIN_POSITIONS = ((2,2),(4,4))
TEST_FOOD = (35.0,45.0)
TEST_POSITIONS = ((5,5),(7,7))
FAMILIES = ("MOV","EAT","WAIT")
TRAIN_VARIANTS = {
    "MOV": ("clear","lethal_east","danger_east_40","danger_east_20"),
    "EAT": ("benign","toxin_7","toxin_100","gain_zero"),
    "WAIT": ("baseline","food_decay_25","water_decay_22","danger_here_40"),
}
OOD_VARIANTS = {
    "MOV": ("danger_east_30","danger_east_55"),
    "EAT": ("toxin_30","gain_25"),
    "WAIT": ("food_decay_15","danger_here_55"),
}
STAGE_COUNTS = {
    "train": (48,132),
    "heldout_ID": (48,132),
    "heldout_hidden_OOD": (24,64),
    "heldout_unknown_context": (8,24),
}
EXPECTED_TOTAL_WORLDS = 128
EXPECTED_TOTAL_PHYSICAL_STEPS = 352

MOVE = PrimitiveCommand("se_deplacer", {"direction":"east"})
MOVE_WEST = PrimitiveCommand("se_deplacer", {"direction":"west"})
WAIT = PrimitiveCommand("attendre")
COLLECT = PrimitiveCommand("collecter", {"target":"berry_a"})
EAT = PrimitiveCommand("manger", {"target":"berry_a"})


def committed_prefix(family: str, *, west: bool=False):
    if family=="MOV":
        return (MOVE_WEST if west else MOVE, WAIT, WAIT)
    if family=="EAT":
        return (COLLECT,EAT,WAIT)
    if family=="WAIT":
        return (WAIT,WAIT,WAIT)
    raise ValueError("unknown fixed protocol family")


def build_physics(family: str, variant: str, *,
                  food: float, position: tuple[int,int]):
    """All latent knobs belong solely to a standalone physical Lab scenario."""
    at=Position(*position)
    reference=physical_fixture_config()
    config=replace(
        reference, version="a230p-standalone-worldphysics-v1",
        initial_position=at,
        initial_body=replace(reference.initial_body,food=float(food)),
        food_decay_per_step=0.5,
        water_decay_per_step=0.2,
        action_energy_costs={
            **reference.action_energy_costs,
            "se_deplacer":1.0, "attendre":0.5,
            "collecter":0.75, "manger":0.5,
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
    )
    layout=WorldLayout(
        resources=((at,"berry_a",2),) if family=="EAT" else (),
    )
    if family=="MOV":
        if variant=="lethal_east":
            layout=replace(layout,lethal_zones=frozenset({at.moved("east")}))
        elif variant.startswith("danger_east_"):
            level=float(variant.split("_")[-1])
            layout=replace(layout,danger_zones=frozenset({at.moved("east")}))
            config=replace(config,danger_zone_damage=level)
        elif variant=="blocked_east":
            layout=replace(layout,obstacles=frozenset({at.moved("east")}))
        elif variant not in ("clear","west_virgin"):
            raise ValueError("unexpected physical movement variant")
    elif family=="EAT":
        effects=dict(config.berry_effects)
        if variant.startswith("toxin_"):
            level=-float(variant.split("_")[-1])
            effects["berry_a"]=replace(effects["berry_a"], integrity_delta=level)
        elif variant=="gain_zero":
            effects["berry_a"]=replace(effects["berry_a"],food_gain=0.0)
        elif variant=="gain_25":
            effects["berry_a"]=replace(effects["berry_a"],food_gain=25.0)
        elif variant!="benign":
            raise ValueError("unexpected physical berry variant")
        config=replace(config,berry_effects=effects)
    elif family=="WAIT":
        if variant in ("food_decay_25","food_decay_15"):
            config=replace(config,food_decay_per_step=(
                2.5 if variant=="food_decay_25" else 1.5
            ))
        elif variant=="water_decay_22":
            config=replace(config,water_decay_per_step=2.2)
        elif variant.startswith("danger_here_"):
            level=float(variant.split("_")[-1])
            layout=replace(layout,danger_zones=frozenset({at}))
            config=replace(config,danger_zone_damage=level)
        elif variant!="baseline":
            raise ValueError("unexpected physical rest variant")
    else:
        raise ValueError("unknown physics family")
    config.validate()
    layout.validate(config)
    return config,layout


def run_physical_world(*, stage: str, family: str, variant: str,
                       food: float, position: tuple[int,int]) -> tuple[
                           PhysicalPrefixWitness, dict
                       ]:
    world_id=f"a230p:{stage}:{family}:{variant}:food{int(food)}:x{position[0]}y{position[1]}"
    config,layout=build_physics(
        family,variant,food=food,position=position
    )
    prefix=committed_prefix(
        family,west=(variant=="west_virgin")
    )
    world=WorldBody(config=config,layout=layout)
    recorder=EquipmentCorpusRecorder(corpus_version=world_id)
    initial=None
    steps=[]
    evidence=[]
    for t_monde,command in enumerate(prefix,1):
        if steps and steps[-1].terminal:
            raise AssertionError("physical world was executed AFTER its death")
        example=recorder.record_transition(
            world=world,t_monde=t_monde,
            family=f"physical_a230p_{family}",command=command,
        )
        if initial is None:
            initial=example.state
        elif example.state!=evidence[-1]["observed_state_after"]:
            # See below: example dict carries exact schema on each step.
            raise AssertionError("physical observation chain not contiguous")
        step=JointStep(
            cumulative_delta=cumulative_observable_deltas(
                initial,example.observed_next_state
            ),
            terminal=example.terminal,
        )
        steps.append(step)
        evidence.append({
            "t_monde":t_monde,
            "physical_example":example.as_dict(),
            "physical_example_sha256":sha256_hex(
                canonical_causal_bytes(example.as_dict())
            ),
            "observed_state_after":example.observed_next_state,
        })
        if example.terminal:
            break
    assert initial is not None
    w=PhysicalPrefixWitness(
        world_id=world_id,initial=initial,commands=prefix,
        steps=tuple(steps),
    )
    w.validate()
    physics={
        "world_id":world_id,
        "stage":stage,
        "family":family,
        "hidden_variant_for_lab_only":variant,
        "initial_food":food,
        "initial_position":list(position),
        "physical_config_sha256":config.digest(),
        "physical_layout_sha256":sha256_hex(
            canonical_causal_bytes(layout.as_dict())
        ),
        "applied_steps":len(steps),
        "terminal_step":w.first_terminal_step,
        "observed_physical_examples":[
            {
                "t_monde":e["t_monde"],
                "physical_example":e["physical_example"],
                "physical_example_sha256":e["physical_example_sha256"],
            }
            for e in evidence
        ],
        "physical_applications_evidenced_by_runner":True,
        "oracle_feedback_to_i0":False,
    }
    return w,physics


def fixed_worlds(stage: str):
    if stage=="train":
        for family in FAMILIES:
            for variant in TRAIN_VARIANTS[family]:
                for food in TRAIN_FOOD:
                    for position in TRAIN_POSITIONS:
                        yield {
                            "stage":stage,"family":family,"variant":variant,
                            "food":food,"position":position,
                        }
    elif stage=="heldout_ID":
        for family in FAMILIES:
            for variant in TRAIN_VARIANTS[family]:
                for food in TEST_FOOD:
                    for position in TEST_POSITIONS:
                        yield {
                            "stage":stage,"family":family,"variant":variant,
                            "food":food,"position":position,
                        }
    elif stage=="heldout_hidden_OOD":
        for family in FAMILIES:
            for variant in OOD_VARIANTS[family]:
                for food in TEST_FOOD:
                    for position in TEST_POSITIONS:
                        yield {
                            "stage":stage,"family":family,"variant":variant,
                            "food":food,"position":position,
                        }
    elif stage=="heldout_unknown_context":
        for variant in ("blocked_east","west_virgin"):
            for food in TEST_FOOD:
                for position in TEST_POSITIONS:
                    yield {
                        "stage":stage,"family":"MOV","variant":variant,
                        "food":food,"position":position,
                    }
    else:
        raise ValueError("unregistered world stage")


def _assert_masked_hazards_are_accessibly_identical(train):
    """Only lab can check this before training; result is NOT injected."""
    indexed={}
    for w,phys in train:
        key=(phys["family"],phys["initial_food"],
             tuple(phys["initial_position"]))
        indexed.setdefault(key,[]).append(w.initial.as_dict())
    for (family,food,pos),states in indexed.items():
        if len(states)!=4 or any(state!=states[0] for state in states[1:]):
            raise AssertionError(
                "hidden-world intervention leaked before the first command"
                +f" {family} food={food} pos={pos}"
            )


def evaluate(output_dir:Path)->dict:
    output_dir.mkdir(parents=True,exist_ok=False)
    physical_manifest=[]
    examples=[]
    cumulative_steps=0
    for recipe in fixed_worlds("train"):
        w,phys=run_physical_world(**recipe)
        physical_manifest.append(phys)
        examples.append((w,phys))
        cumulative_steps+=phys["applied_steps"]
    if (len(examples),cumulative_steps)!=STAGE_COUNTS["train"]:
        raise AssertionError("original preregistered physical train count invalid")
    _assert_masked_hazards_are_accessibly_identical(examples)
    frozen=LaboratoryJointPrefixModel([pair[0] for pair in examples])
    if frozen.training_worlds!=48 or frozen.contexts!=3:
        raise AssertionError("train group/latent branch provenance inconsistent")
    train_witnesses=[w.as_dict() for w,_ in examples]
    print("A230P_TRAIN " + json.dumps({
        "separate_physical_worlds":len(examples),
        "physical_steps":cumulative_steps,
        "frozen_contexts":frozen.contexts,
        "number_of_empirical_joint_branches_by_context":{
            family:len(frozen.forecast(
                initial=next(x.initial for x,p in examples
                             if p["family"]==family),
                commands=committed_prefix(family),
            ).branches) for family in FAMILIES
        },
        "corpus_sha256":sha256_hex(canonical_causal_bytes(
            train_witnesses
        )),
    },sort_keys=True),flush=True)
    # All model fields are frozen here. NO model updates after tests begin.
    measures=[]
    stage_counts={}
    seen={w.world_id for w,_ in examples}
    for stage in (
        "heldout_ID","heldout_hidden_OOD","heldout_unknown_context"
    ):
        counts=Counter()
        total_steps=0
        for recipe in fixed_worlds(stage):
            w,phys=run_physical_world(**recipe)
            if w.world_id in seen:
                raise AssertionError("training/test physical world identity reused")
            seen.add(w.world_id)
            total_steps+=phys["applied_steps"]
            forecast=frozen.forecast(
                initial=w.initial, commands=w.commands
            )
            outcome=score_heldout(forecast,w)
            # Comparator: only the first step observed in the SAME training
            # worlds. No hindsight from heldout world is in this comparison.
            firststep_terminal_seen=forecast.first_step_terminal_in_training
            receipt={
                "world_id":w.world_id,
                "stage":stage,"family":phys["family"],
                "hidden_variant_for_lab_only":phys[
                    "hidden_variant_for_lab_only"
                ],
                "physical_steps":len(w.steps),
                "witness":w.as_dict(),
                "model":{
                    "status":forecast.status,
                    "context_key":forecast.context_key,
                    "risk_label":forecast.risk_label,
                    "supported_physical_worlds":forecast.evidence_worlds,
                    "empirical_branches":[x.as_dict() for x in forecast.branches],
                    "observed_terminal_steps":list(
                        forecast.observed_terminal_steps
                    ),
                    "single_step_baseline_witnessed_terminal":
                        firststep_terminal_seen,
                    "certifies_safe":forecast.certifies_safe,
                    "unseen_hidden_hazard_not_excluded":
                        forecast.could_have_unobserved_hidden_hazard,
                },
                "result":outcome,
                "source_lab_physics":phys,
                "no_i0_command_was_executed":True,
            }
            forecast.validate()
            if forecast.certifies_safe or not forecast.could_have_unobserved_hidden_hazard:
                raise AssertionError("fabricated safety conclusion")
            measures.append(receipt)
            counts["available"]+=bool(outcome["covered"])
            counts["abstained"]+=not outcome["covered"]
            counts["joint_matches"]+=outcome["joint_branch_witnessed"] is True
            counts["novel_branches"]+=outcome["novel_joint_branch"] is True
            counts["terminal_worlds"]+=w.first_terminal_step is not None
            counts["late_terminal_worlds"]+= (
                w.first_terminal_step is not None and
                w.first_terminal_step>1
            )
            counts["late_terminal_absent_from_first_step_witness"]+=(
                w.first_terminal_step is not None and
                w.first_terminal_step>1 and
                not firststep_terminal_seen and
                bool(outcome["covered"])
            )
            counts["terminal_step_outside_empirical_set"]+=(
                bool(outcome["covered"])
                and outcome["terminal_step_in_empirical_set"] is False
                and w.first_terminal_step is not None
            )
        n=len([x for x in measures if x["stage"]==stage])
        if (n,total_steps)!=STAGE_COUNTS[stage]:
            raise AssertionError(
                f"heldout physical counts drifted: {stage} {n} {total_steps}"
            )
        stage_counts[stage]={
            "worlds":n,"physical_steps":total_steps,
            **dict(counts),
        }
        print("A230P_STRATUM " +json.dumps({
            "stage":stage, **stage_counts[stage],
        },sort_keys=True),flush=True)
    if len(measures)!=80 or len(seen)!=128:
        raise AssertionError("failed physical disjoint holdout")
    manifest={
        "schema":"a230p-detached-physical-training-v1",
        "physical_training_worlds":48,
        "physical_training_steps":cumulative_steps,
        "model_context_count":frozen.contexts,
        "training_witnesses":train_witnesses,
        "source_lab_physics":physical_manifest,
        "training_witness_corpus_sha256":sha256_hex(
            canonical_causal_bytes(train_witnesses)
        ),
        "all_physical_worlds_distinct":True,
    }
    (output_dir/"a230p-training-manifest.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2)+"\n"
    )
    (output_dir/"a230p-heldout-physical-results.json").write_text(
        json.dumps(measures,sort_keys=True,indent=2)+"\n"
    )
    summary={
        "schema":"a230p-physical-joint-trajectories-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "new_i0_births":0,
        "new_autonomous_i0_steps":0,
        "training_physical_worlds":48,
        "training_physical_steps":cumulative_steps,
        "heldout_physical_worlds":len(measures),
        "heldout_physical_steps":sum(x["physical_steps"] for x in measures),
        "physical_worlds_total":len(seen),
        "physical_steps_total":cumulative_steps+sum(
            x["physical_steps"] for x in measures
        ),
        "models_frozen_before_any_test_world":True,
        "training_witness_corpus_sha256":manifest[
            "training_witness_corpus_sha256"
        ],
        "model_kind":"lab_joint_witness_catalogue_not_EquipmentModel",
        "supports_complete_next_state":False,
        "certifies_any_action_safe":False,
        "guarantees_exhaustive_latent_hazards":False,
        "deployable_to_i0":False,
        "oracle_feedback_to_i0":False,
        "mvp_norm_changed":False,
        "stage12":"PARTIAL",
        "issue110":"OPEN",
        "strata":stage_counts,
    }
    if (summary["physical_worlds_total"]!=EXPECTED_TOTAL_WORLDS
        or summary["physical_steps_total"]!=EXPECTED_TOTAL_PHYSICAL_STEPS):
        raise AssertionError("P physically committed cohort count mismatch")
    (output_dir/"a230p-summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n"
    )
    print("A230P_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    evaluate(args.output_dir)


if __name__=="__main__":
    main()
