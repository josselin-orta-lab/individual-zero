"""A2.30-ZE: prospective, detached exact-key coverage ablation of real Stage6.

Only non-ingestion physical demonstration commands are executed, in independent
training worlds. Test worlds are sensed but NEVER physically transitioned.
Both exact-model arms and all planner commands remain entirely LAB SHADOW.
No I0 instance, no active runtime memory, no presumed berry_b safety, no UC.
Preregistered before code at 10fea5ee4825f81e44c5bbe1865bb4441a43f76d.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import subprocess

from i0.equipment import (
    EquipmentCorpus, FrozenTableEquipment, train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout
from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config

FOODS=(35.0,45.0)
HIDDENS=("benign","toxic_lethal")
KNOWN_LAYOUTS=("B_LOCAL","B_EAST")
NEGATIVE_LAYOUTS=("B_NONE","B_EAST_BLOCKED")
TRAIN_POSITION=(5,5)
OOD_POSITION=(7,7)
EXPECTED_TRAIN_WORLDS=9
EXPECTED_TEST_WORLDS=24
EXPECTED_STEPS=13
MOVE_E=PrimitiveCommand("se_deplacer",{"direction":"east"})
COLLECT_B=PrimitiveCommand("collecter",{"target":"berry_b"})
COLLECT_A=PrimitiveCommand("collecter",{"target":"berry_a"})
EAT_B=PrimitiveCommand("manger",{"target":"berry_b"})


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def observed(world,step=1):
    capture=SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry(),
    )
    state=state_from_capture(capture=capture,is_night=world.is_night(step))
    state.validate()
    return state


def physics(*,layout_name:str,food:float,position:tuple[int,int],
            hidden:str):
    """World-only hidden berry effect; no code path from physics to planning."""
    if layout_name not in KNOWN_LAYOUTS+NEGATIVE_LAYOUTS+("A_REFERENCE",):
        raise ValueError("unregistered physical layout")
    if hidden not in HIDDENS:
        raise ValueError("unregistered hidden berry effect")
    if position not in (TRAIN_POSITION,OOD_POSITION,(3,3)):
        raise ValueError("unregistered position")
    base=physical_fixture_config()
    at=Position(*position)
    effects=dict(base.berry_effects)
    effects["berry_a"]=replace(effects["berry_a"],
                                food_gain=10.0,integrity_delta=0.0)
    effects["berry_b"]=replace(
        effects["berry_b"],food_gain=12.0,
        integrity_delta=0.0 if hidden=="benign" else -100.0,
    )
    costs=dict(base.action_energy_costs)
    costs.update({
        "se_deplacer":1.0,"collecter":0.75,
        "manger":0.5,"attendre":0.5,
    })
    config=replace(
        base,version="stage12-a230ze-standalone-physics-v1",
        initial_position=at,
        initial_body=replace(base.initial_body,food=float(food)),
        berry_effects=effects,action_energy_costs=costs,
        food_decay_per_step=0.5,water_decay_per_step=0.2,
        rest_integrity_gain=0.0,
    )
    east=at.moved("east")
    resources=((at,"berry_a",2),)
    if layout_name=="B_LOCAL":
        resources+=((at,"berry_b",2),)
    elif layout_name in ("B_EAST","B_EAST_BLOCKED"):
        resources+=((east,"berry_b",2),)
    layout=WorldLayout(
        resources=resources,
        obstacles=(frozenset({east}) if layout_name=="B_EAST_BLOCKED"
                   else frozenset()),
    )
    config.validate()
    layout.validate(config)
    return config,layout


def training_world(*,name,layout,food,hidden,position):
    config,layout_obj=physics(
        layout_name=layout,food=food,hidden=hidden,position=position,
    )
    world=WorldBody(config=config,layout=layout_obj)
    recorder=EquipmentCorpusRecorder(corpus_version="a230ze-"+name)
    root=observed(world,1)
    commands=(
        (COLLECT_A,) if layout=="A_REFERENCE" else
        (COLLECT_B,) if layout=="B_LOCAL" else
        (MOVE_E,COLLECT_B)
    )
    if any(x==EAT_B or x.primitive=="manger" for x in commands):
        raise AssertionError("ingestion is categorically forbidden")
    examples=[]
    for i,command in enumerate(commands,1):
        now=observed(world,i)
        if command==COLLECT_B and "berry_b" not in now.current_resources:
            raise AssertionError("demonstrator collects nonvisible B resource")
        if command==MOVE_E and not next(x for x in now.adjacent
                                       if x.direction=="east").passable:
            raise AssertionError("demonstrator moved into a visible obstacle")
        ex=recorder.record_transition(
            world=world,t_monde=i,family="a230ze-physical-prefix-"+layout,
            command=command,
        )
        if ex.state != now:
            raise AssertionError("uncertain preaction state is not first-person")
        if ex.terminal or ex.command==EAT_B:
            raise AssertionError("hidden food injury or ingestion occurred")
        examples.append(ex)
    return {
        "source_world_id":name,
        "layout_external_only":layout,
        "hidden_effect_external_only":hidden,
        "root_accessible":root.as_dict(),
        "physics_config_sha256_external_only":config.digest(),
        "layout_sha256_external_only":digest(layout_obj.as_dict()),
        "physical_steps":len(examples),
        "observed_physical_examples":[ex.as_dict() for ex in examples],
        "physical_example_sha256":[digest(ex.as_dict()) for ex in examples],
        "no_ingestion_in_training":True,
        "no_terminal":True,
    }, examples


def test_world(*,name,layout,food,hidden,position):
    config,layout_obj=physics(
        layout_name=layout,food=food,hidden=hidden,position=position,
    )
    world=WorldBody(config=config,layout=layout_obj)
    root=observed(world,1)
    return {
        "world_id":name,
        "layout_external_only":layout,
        "hidden_effect_external_only":hidden,
        "food_initial":food,
        "position":list(position),
        "first_person_state":root.as_dict(),
        "physical_config_sha256_external_only":config.digest(),
        "physical_layout_sha256_external_only":digest(layout_obj.as_dict()),
        "physical_steps_executed_in_heldout_world":0,
        "no_oracle_feedback_to_model":True,
    },root


def test_recipes():
    opposite={"benign":"toxic_lethal","toxic_lethal":"benign"}
    for layout,food,trained_hidden in product(KNOWN_LAYOUTS,FOODS,HIDDENS):
        base=f"{layout}-food{int(food)}-source{trained_hidden}"
        hidden=opposite[trained_hidden]
        for cohort,position in (
            ("same_observable_input",TRAIN_POSITION),
            ("unseen_coordinates",OOD_POSITION),
        ):
            yield {
                "name":f"ze-test-{cohort}-{base}-heldout{hidden}",
                "layout":layout,"food":food,"hidden":hidden,
                "position":position,"cohort":cohort,
                "paired_source":f"ze-train-{base}",
            }
    for layout,food,hidden in product(NEGATIVE_LAYOUTS,FOODS,HIDDENS):
        yield {
            "name":f"ze-test-negative-{layout}-food{int(food)}-{hidden}",
            "layout":layout,"food":food,"hidden":hidden,
            "position":TRAIN_POSITION,"cohort":"unavailable_or_blocked",
            "paired_source":None,
        }


def frozen_models(demonstrations):
    """Frozen before ANY target world is instantiated."""
    source=[]
    for item in demonstrations:
        from i0.equipment import EquipmentCorpusExample
        for ex in item["observed_physical_examples"]:
            state=decode_state(ex["state"])
            after=decode_state(ex["observed_next_state"])
            command=PrimitiveCommand(
                ex["command"]["primitive"],ex["command"]["parameters"]
            )
            row=EquipmentCorpusExample(
                family=ex["family"],state=state,command=command,
                observed_next_state=after,terminal=ex["terminal"],
            )
            row.validate()
            if row.command==EAT_B or row.command.primitive=="manger":
                raise AssertionError("ingestion knowledge illegally trained")
            source.append(row)
    a_only=[x for x in source if x.family.endswith("A_REFERENCE")]
    if len(a_only)!=1 or len(source)!=EXPECTED_STEPS:
        raise AssertionError("frozen physical training corpus size changed")
    models={}
    for label,examples in (
        ("A_ONLY",tuple(a_only)),
        ("A_PLUS_B_KNOWN_PREFIX",tuple(source)),
    ):
        corpus=EquipmentCorpus(
            version=f"a230ze-train-{label}-v1",
            examples=examples,
        )
        models[label]=train_exact_transition_table(
            corpus=corpus,equipment_version=f"E-a230ze-{label}-v1",
        )
    return models


def decode_state(raw):
    """Exact visible-state decode, never hidden WorldPhysicsConfig."""
    from i0.equipment import SimulationNeighbor,SimulationState
    if set(raw)!={
        "schema_version","x","y","body","inventory",
        "current_water_source","current_resources","adjacent",
        "known_shelter_here","is_night",
    }:
        raise ValueError("secret or missing state feature in model")
    s=SimulationState(
        schema_version=raw["schema_version"],x=raw["x"],y=raw["y"],
        body=raw["body"],inventory=raw["inventory"],
        current_water_source=raw["current_water_source"],
        current_resources=tuple(raw["current_resources"]),
        adjacent=tuple(SimulationNeighbor(
            direction=n["direction"],x=n["x"],y=n["y"],
            passable=n["passable"],water_source=n["water_source"],
            resources=tuple(n["resources"]),creature=n["creature"],
        ) for n in raw["adjacent"]),
        known_shelter_here=raw["known_shelter_here"],
        is_night=raw["is_night"],
    )
    if s.as_dict()!=raw:
        raise ValueError("unreconstructible accessible preaction")
    return s


def stage6_shadow(root, equipment, label):
    """Real production Stage6 search code, only its outputs are archived."""
    planner=SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="a230ze-shadow-only-stage6-v1",option_ttl_steps=5,
            max_depth=3,revision_delta=0.0,
            setpoints={
                "energy":65.0,"food":float(root.body["food"])+5.0,
                "water":65.0,"integrity":65.0,
            },
            progressive_subgoals=True,
            progressive_evaluation_prefix=False,
        ),
        simulator=Simulator(
            config=SimulatorConfig(
                version="a230ze-shadow-only-simulator-v1",
                r_max=1,h_max=3,
            ),equipment=equipment,
        ),
    )
    target=float(root.body["food"])+5.0
    result=planner.search(
        initial_state=root,
        target=lambda s:float(s.body["food"])>=target,
        progress_measure="food",
    )
    diag=planner.last_search_diagnostic
    if diag is None:
        raise AssertionError("real Stage6 failed to report root edges")
    if any(p.command.primitive=="manger" for p in result.predictions):
        raise AssertionError("B or other ingestion was fabricated")
    return {
        "arm":label,"status":result.status,
        "partial_progress":result.partial_progress,
        "commands":[c.as_dict() for c in result.commands],
        "predicted_commands":[p.command.as_dict()
                              for p in result.predictions],
        "root_available_edges":result.root_available_edges,
        "root_candidate_edges":result.root_candidate_edges,
        "root_unavailable_edges":result.root_unavailable_edges,
        "unavailable_edges_total":result.unavailable_edges,
        "diagnostic":diag,
        "no_physical_command_dispatched":True,
        "has_any_ingestion_prediction":False,
        "guarantees_berry_b_safe":False,
        "true_I0_UC_measured":None,
    }


def run(output_dir:Path):
    output_dir.mkdir(parents=True,exist_ok=False)
    experiments=[]
    ref, ref_examples = training_world(
        name="ze-train-A-reference",layout="A_REFERENCE",food=60.0,
        hidden="benign",position=(3,3),
    )
    experiments.append(ref)
    samples=list(ref_examples)
    for layout,food,hidden in product(KNOWN_LAYOUTS,FOODS,HIDDENS):
        name=f"ze-train-{layout}-food{int(food)}-source{hidden}"
        e,physical=training_world(
            name=name,layout=layout,food=food,hidden=hidden,
            position=TRAIN_POSITION,
        )
        experiments.append(e)
        samples.extend(physical)
    if len(experiments)!=EXPECTED_TRAIN_WORLDS or len(samples)!=EXPECTED_STEPS:
        raise AssertionError("physical demonstrator world/step count violated")
    all_train_ids={x["source_world_id"] for x in experiments}
    if len(all_train_ids)!=len(experiments):
        raise AssertionError("same training world physically reused")
    training_manifest={
        "schema":"a230ze-actual-physical-training-v1",
        "training_worlds":len(experiments),"physical_training_steps":len(samples),
        "model_examples_physically_observed":len(samples),
        "demonstrations":experiments,
        "training_exact_inputs_sha256":[
            FrozenTableEquipment.input_digest(e.state,e.command)
            for e in samples
        ],
        "raw_examples_sha256":[digest(e.as_dict()) for e in samples],
        "source_hidden_variants_only_for_lab":list(HIDDENS),
        "all_training_commands_non_ingestive":all(
            row.command.primitive!="manger" for row in samples
        ),
    }
    models=frozen_models(experiments)
    if models["A_ONLY"].artifact_digest==models[
        "A_PLUS_B_KNOWN_PREFIX"].artifact_digest:
        raise AssertionError("same exact model used in both comparison arms")
    # FROZEN MODEL SEMANTICS: Now and only now create new target worlds.
    print("A230ZE_MODEL_FROZEN "+json.dumps({
        "training_worlds":len(experiments),"actual_physical_steps":len(samples),
        "source_hidden_variants_ignored_by_model":True,
        "A_only_sha256":models["A_ONLY"].artifact_digest,
        "A_plus_B_sha256":models["A_PLUS_B_KNOWN_PREFIX"].artifact_digest,
    },sort_keys=True),flush=True)
    heldout=[]
    for recipe in test_recipes():
        spec={k:v for k,v in recipe.items()
              if k in ("name","layout","food","hidden","position")}
        info,root=test_world(**spec)
        if info["world_id"] in all_train_ids:
            raise AssertionError("test world identity used for physical training")
        scenario=recipe["cohort"]
        if scenario=="same_observable_input":
            source=next(x for x in experiments if
                        x["source_world_id"]==recipe["paired_source"])
            if source["root_accessible"]!=info["first_person_state"]:
                raise AssertionError("heldout hidden variation visibly changed input")
            if source["hidden_effect_external_only"]==info[
                    "hidden_effect_external_only"]:
                raise AssertionError("same latent outcome was used for training/test")
        elif scenario=="unseen_coordinates":
            source=next(x for x in experiments if
                        x["source_world_id"]==recipe["paired_source"])
            if (source["root_accessible"]["x"],
                source["root_accessible"]["y"])==tuple(info["position"]):
                raise AssertionError("unseen position was actually in training")
        baseline=stage6_shadow(root,models["A_ONLY"],"A_ONLY")
        enriched=stage6_shadow(
            root,models["A_PLUS_B_KNOWN_PREFIX"],"A_PLUS_B_KNOWN_PREFIX",
        )
        expected=(
            "partial_progress" if scenario=="same_observable_input"
            else "incomplete_model"
        )
        if (baseline["status"]!="incomplete_model" or
            baseline["root_available_edges"]!=0 or
            enriched["status"]!=expected or
            enriched["root_available_edges"]!=
                (1 if scenario=="same_observable_input" else 0)):
            raise AssertionError(
                f"preregistered Stage6 exact-key witness failed: {scenario} "
                f"{baseline['status']}/{enriched['status']}"
            )
        if scenario=="same_observable_input":
            command=enriched["commands"]
            expected_first=COLLECT_B.as_dict() if info[
                "layout_external_only"]=="B_LOCAL" else MOVE_E.as_dict()
            if (len(command)!=1 or command[0]!=expected_first
                or not enriched["partial_progress"]):
                raise AssertionError("partial option did not start with demonstrated action")
        else:
            if enriched["commands"] or baseline["commands"]:
                raise AssertionError("unknown first root produced invented command")
        info.update({
            "cohort":scenario,"paired_physical_demonstrator":recipe["paired_source"],
            "baseline_A_only":baseline,
            "enriched_demonstrated_prefix":enriched,
            "hidden_B_effect_still_unidentified":True,
            "no_B_ingestion_or_test_physics":True,
            "operator_approved_cognitive_model_installation":False,
        })
        heldout.append(info)
    if len(heldout)!=EXPECTED_TEST_WORLDS or len({
        x["world_id"] for x in heldout
    })!=EXPECTED_TEST_WORLDS:
        raise AssertionError("test world count wrong")
    by_cohort=defaultdict(list)
    for e in heldout:by_cohort[e["cohort"]].append(e)
    expected_cohorts={
        "same_observable_input":8,
        "unseen_coordinates":8,
        "unavailable_or_blocked":8,
    }
    if {k:len(v) for k,v in by_cohort.items()}!=expected_cohorts:
        raise AssertionError("cohort split drifted from preregistration")
    metrics={}
    for name,items in sorted(by_cohort.items()):
        metrics[name]={
            "test_worlds":len(items),
            "test_physical_actions":sum(
                x["physical_steps_executed_in_heldout_world"] for x in items
            ),
            "baseline_incomplete":sum(
                x["baseline_A_only"]["status"]=="incomplete_model" for x in items
            ),
            "enriched_partial_progress":sum(
                x["enriched_demonstrated_prefix"]["status"]=="partial_progress"
                for x in items
            ),
            "enriched_incomplete":sum(
                x["enriched_demonstrated_prefix"]["status"]=="incomplete_model"
                for x in items
            ),
            "enriched_known_root":sum(
                x["enriched_demonstrated_prefix"]["root_available_edges"]>0
                for x in items
            ),
            "false_eat_prediction":sum(
                x["enriched_demonstrated_prefix"][
                    "has_any_ingestion_prediction"] for x in items
            ),
        }
        print("A230ZE_COHORT "+json.dumps({
            "cohort":name,**metrics[name]
        },sort_keys=True),flush=True)
    summary={
        "schema":"a230ze-independent-exact-coverage-shadow-v1",
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "new_I0_births":0,
        "new_I0_autonomous_world_steps":0,
        "detached_worlds_total":len(experiments)+len(heldout),
        "detached_physical_training_worlds":len(experiments),
        "detached_physical_training_steps":len(samples),
        "heldout_worlds_with_no_physical_actions":len(heldout),
        "heldout_physical_actions":0,
        "A_only_equipment_sha256":models["A_ONLY"].artifact_digest,
        "enriched_exact_equipment_sha256":models[
            "A_PLUS_B_KNOWN_PREFIX"].artifact_digest,
        "model_inputs_observed_before_test_world_creation":True,
        "model_examples_all_from_independent_source_worlds":True,
        "model_contains_no_B_ingestion":True,
        "model_contains_no_safety_certificate":True,
        "no_commands_dispatched_by_stage6":True,
        "oracle_or_hidden_B_effect_fed_to_model":False,
        "actual_I0_UC_measured":False,
        "actual_I0_food_goal_success_proven":False,
        "Stage6_production_model_accepted":False,
        "stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
        "cohorts":metrics,
    }
    if (summary["detached_worlds_total"]!=33
        or summary["detached_physical_training_steps"]!=13
        or sum(v["enriched_partial_progress"] for v in metrics.values())!=8):
        raise AssertionError("total preregistered positive controls failed")
    (output_dir/"a230ze-training-manifest.json").write_text(
        json.dumps(training_manifest,indent=2,sort_keys=True)+"\n")
    (output_dir/"a230ze-heldout-shadows.json").write_text(
        json.dumps(heldout,indent=2,sort_keys=True)+"\n")
    (output_dir/"a230ze-summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A230ZE_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    run(args.output_dir)


if __name__=="__main__":
    main()
