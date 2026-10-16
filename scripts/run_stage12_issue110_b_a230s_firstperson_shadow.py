"""A2.30-S: external first-person information and shadow Stage6 experiment.

PREREGISTERED at ea7b1374212e0fd6888b8e37a181c1bea40908e2
before S code or results. Uses only new detached WorldBody instances.
Planner is called in SHADOW, with precisely the physical examples of that
ONE world's own already accessible transitions; never I0 memory or Oracle.
No actions from the planner are dispatched to any world.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import json
from pathlib import Path
import subprocess

from i0.equipment import EquipmentCorpus, FrozenTableEquipment, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout

from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config

FOODS=(40.0,45.0)
POSITIONS=((2,2),(4,4))
FOOD_VARIANTS=("benign","toxic_mild","toxic_lethal","exogenous_confounded")
FOOD_FOLLOWUPS=("wait","repeat_eat")
MOVE_VARIANTS=("clear","danger_40","danger_55","lethal_east")
MOVE_FOLLOWUPS=("wait","escape")
EXPECTED_WORLDS=72
EXPECTED_ACTED_WORLDS=64
EXPECTED_PHYSICAL_STEPS=196
SHADOW_TARGET_FOOD=65.0
SHADOW_MAX_DEPTH=3

COLLECT=PrimitiveCommand("collecter",{"target":"berry_a"})
EAT=PrimitiveCommand("manger",{"target":"berry_a"})
WAIT=PrimitiveCommand("attendre")
EAST=PrimitiveCommand("se_deplacer",{"direction":"east"})
WEST=PrimitiveCommand("se_deplacer",{"direction":"west"})


def content_sha(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def fresh_config(food,at,*,berry_damage=0.0,danger_damage=7.0):
    ref=physical_fixture_config()
    cost=dict(ref.action_energy_costs)
    cost.update({
        "collecter":0.75, "manger":0.5, "attendre":0.5,
        "se_deplacer":1.0,
    })
    berry=dict(ref.berry_effects)
    berry["berry_a"]=replace(berry["berry_a"],integrity_delta=berry_damage)
    cfg=replace(
        ref,version="stage12-a230s-detached-observation-v1",
        initial_position=Position(*at),
        initial_body=replace(ref.initial_body,food=float(food)),
        food_decay_per_step=0.5,
        water_decay_per_step=0.2,
        rest_integrity_gain=0.0,
        action_energy_costs=cost,
        berry_effects=berry,
        danger_zone_damage=danger_damage,
    )
    cfg.validate()
    return cfg


def config_world(kind,variant,food,at):
    if kind=="food":
        if variant not in FOOD_VARIANTS:
            raise ValueError("non-preregistered food latent world")
        damage={
            "benign":0.0,"toxic_mild":-7.0,
            "toxic_lethal":-100.0,"exogenous_confounded":0.0,
        }[variant]
        cfg=fresh_config(food,at,berry_damage=damage,danger_damage=7.0)
        layout=WorldLayout(resources=((Position(*at),"berry_a",2),))
    elif kind=="movement":
        if variant not in MOVE_VARIANTS:
            raise ValueError("non-preregistered movement latent world")
        cfg=fresh_config(food,at,danger_damage={
            "clear":7.0,"danger_40":40.0,
            "danger_55":55.0,"lethal_east":7.0,
        }[variant])
        east=Position(*at).moved("east")
        layout=WorldLayout(
            danger_zones=(
                frozenset({east}) if variant in ("danger_40","danger_55")
                else frozenset()
            ),
            lethal_zones=(
                frozenset({east}) if variant=="lethal_east"
                else frozenset()
            ),
        )
    else:
        raise ValueError("unsupported family")
    layout.validate(cfg)
    return cfg,layout


def firstperson(world: WorldBody, t: int):
    perception=SymbolicPerception()
    sensed=perception.capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(capture=sensed,is_night=world.is_night(t))


def shadow_food_search(*, snapshots, world_id, t_query):
    """Only already-experienced evidence from the SAME world.

    This is an IDEALIZED lab memory created from first-person transitions,
    not a cognition-facing change or an I0 memory claim.
    """
    if not snapshots or max(x["step"] for x in snapshots)>=t_query:
        raise AssertionError("future physical consequence leaked into Stage6 shadow")
    examples=tuple(x["example"] for x in snapshots)
    for event in examples:
        event.validate()
    corpus=EquipmentCorpus(
        version=f"a230s-shadow-history-{world_id}-t{t_query}",
        examples=examples,
    )
    equipment=train_exact_transition_table(
        corpus=corpus,equipment_version=f"lab-a230s-history-{world_id}-t{t_query}",
    )
    simulator=Simulator(
        config=SimulatorConfig(
            version="lab-a230s-simulator-v1",r_max=1,h_max=SHADOW_MAX_DEPTH,
        ),
        equipment=equipment,
    )
    planner=SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="lab-a230s-readonly-shadow-v1",
            option_ttl_steps=5,max_depth=SHADOW_MAX_DEPTH,
            revision_delta=0.0,
            setpoints={
                "energy":65.0,"food":SHADOW_TARGET_FOOD,
                "water":65.0,"integrity":65.0,
            },
            progressive_subgoals=True,
        ),
        simulator=simulator,
    )
    # The search is informational ONLY; its commands are never executed.
    current=snapshots[-1]["example"].observed_next_state
    result=planner.search(
        initial_state=current,
        target=lambda state:float(state.body["food"])>=SHADOW_TARGET_FOOD,
        progress_measure="food",
    )
    diag=planner.last_search_diagnostic
    if diag is None:
        raise AssertionError("Stage6 shadow diagnostic missing")
    return {
        "t_query":t_query,
        "previous_observed_steps":[row["step"] for row in snapshots],
        "history_examples_count":len(examples),
        "history_corpus_sha256":corpus.digest(),
        "snapshot_input_sha256":content_sha(current.as_dict()),
        "model_kind":"own_past_firstperson_only_exact_shadow",
        "food_goal_setpoint":SHADOW_TARGET_FOOD,
        "max_depth":SHADOW_MAX_DEPTH,
        "h_eff":SHADOW_MAX_DEPTH,"r_eff":1,
        "stage6_status":result.status,
        "stage6_root_candidate_edges":result.root_candidate_edges,
        "stage6_root_available_edges":result.root_available_edges,
        "stage6_root_unavailable_edges":result.root_unavailable_edges,
        "stage6_unavailable_edges":result.unavailable_edges,
        "stage6_expanded_states":result.expanded_states,
        "stage6_commands_only_proposed":[c.as_dict() for c in result.commands],
        "stage6_diagnostic":diag,
        "no_shadow_command_dispatched":True,
    }


def command_prefix(kind,followup):
    if kind=="food":
        if followup not in FOOD_FOLLOWUPS:
            raise ValueError("unexpected food followup")
        return (COLLECT,COLLECT,EAT,WAIT if followup=="wait" else EAT)
    if kind=="movement":
        if followup not in MOVE_FOLLOWUPS:
            raise ValueError("unexpected movement followup")
        return (EAST,WAIT if followup=="wait" else WEST,WAIT)
    raise ValueError("unknown action family")


def run_one(*,kind,variant,followup,food,at):
    name=f"a230s:{kind}:{variant}:{followup}:f{int(food)}:x{at[0]}y{at[1]}"
    config,layout=config_world(kind,variant,food,at)
    world=WorldBody(config=config,layout=layout)
    recorder=EquipmentCorpusRecorder(corpus_version="a230s-physical-"+name)
    commands=command_prefix(kind,followup)
    snapshots=[]
    shadow=[]
    external=[]
    first_eat_input_capture_before_event=None
    hidden_intervention_visible_change=None
    before_firstperson=firstperson(world,1)
    for t,command in enumerate(commands,1):
        if snapshots and snapshots[-1]["example"].terminal:
            raise AssertionError("attempted action after terminal event")
        if kind=="food" and t==3:
            # Crucial causal intervention: exogenous danger is set only
            # AFTER both collecter commands, but BEFORE first ingestion.
            first_eat_input_capture_before_event=firstperson(world,t)
            if variant=="exogenous_confounded":
                world.apply_scenario_event("set_danger_zone",{
                    "position":{"x":at[0],"y":at[1]},
                    "active":True,
                })
                external.append({
                    "between_physical_steps":[2,3],
                    "world_event":"set_danger_zone",
                    "position":{"x":at[0],"y":at[1]},
                    "active":True,
                    "not_an_i0_command":True,
                    "not_visible_in_capture":True,
                })
                hidden_intervention_visible_change=(
                    first_eat_input_capture_before_event.as_dict()!=
                    firstperson(world,t).as_dict()
                )
                if hidden_intervention_visible_change:
                    raise AssertionError("hidden event is visible to I0")
            shadow.append(shadow_food_search(
                snapshots=snapshots,world_id=name,t_query=t,
            ))
        example=recorder.record_transition(
            world=world,t_monde=t,
            family=f"laboratory_firstperson_{kind}",
            command=command,
        )
        snapshots.append({"step":t,"example":example})
        if kind=="food" and t==3 and not example.terminal:
            shadow.append(shadow_food_search(
                snapshots=snapshots,world_id=name,t_query=t+1,
            ))
        if example.terminal:
            world.freeze_terminal_state()
            break
    if not snapshots or any(row["example"].terminal
        for row in snapshots[:-1]):
        raise AssertionError("a terminal past event has a future transition")
    physical=[
        {
            "step":entry["step"],
            "state_before":entry["example"].state.as_dict(),
            "command":entry["example"].command.as_dict(),
            "state_after":entry["example"].observed_next_state.as_dict(),
            "terminal":entry["example"].terminal,
            "physical_example_sha256":content_sha(entry["example"].as_dict()),
            "physical_example":entry["example"].as_dict(),
        }
        for entry in snapshots
    ]
    return {
        "id":name, "kind":kind,"variant_lab_only":variant,
        "followup_precommitted":followup,
        "initial_food":float(food),
        "initial_position":list(at),
        "initial_accessible":before_firstperson.as_dict(),
        "initial_accessible_sha256":content_sha(before_firstperson.as_dict()),
        "first_eat_accessible_before_hidden_event":(
            first_eat_input_capture_before_event.as_dict()
            if first_eat_input_capture_before_event else None
        ),
        "hidden_event_changed_capture":hidden_intervention_visible_change,
        "external_environment_interventions":external,
        "config_sha256":config.digest(),
        "layout_sha256":content_sha(layout.as_dict()),
        "intended_prefix":[c.as_dict() for c in commands],
        "physical_records":physical,
        "physical_step_count":len(physical),
        "first_terminal_step":next(
            (record["step"] for record in physical if record["terminal"]),None
        ),
        "shadow_food":shadow,
        "new_I0_birth":False,
        "shadow_only":True,
        "oracle_information_in_cognitive_search":False,
    }


def passive_cases():
    results=[]
    for kind in ("food_resource_visible","movement_obstacle_visible"):
        for at in POSITIONS:
            for present in (False,True):
                config=fresh_config(40.0,at)
                pos=Position(*at)
                layout=(
                    WorldLayout(
                        resources=((pos,"berry_a",1),) if present else ()
                    )
                    if kind=="food_resource_visible" else
                    WorldLayout(
                        obstacles=(
                            frozenset({pos.moved("east")})
                            if present else frozenset()
                        ),
                    )
                )
                world=WorldBody(config=config,layout=layout)
                capture=firstperson(world,1)
                # Read ONLY first-person state, with no world action.
                cue=(
                    "berry_a" in capture.current_resources
                    if kind=="food_resource_visible" else
                    not next(
                        x.passable for x in capture.adjacent
                        if x.direction=="east"
                    )
                )
                if cue!=present:
                    raise AssertionError("visible resource/obstacle not distinguished")
                results.append({
                    "id":f"a230s:passive:{kind}:x{at[0]}y{at[1]}:{int(present)}",
                    "cue_kind":kind,
                    "intended_visible_indicator":present,
                    "detected_from_accessible_state":cue,
                    "capture":capture.as_dict(),
                    "config_sha256":config.digest(),
                    "layout_sha256":content_sha(layout.as_dict()),
                    "world_steps_applied":0,
                    "new_i0_birth":False,
                })
    if len(results)!=8:
        raise AssertionError("passive controls total not preregistered")
    return results


def comparison_witness(rows):
    """Controls are correlated external worlds, NOT I0 causal inference."""
    index={(x["kind"],x["variant_lab_only"],x["followup_precommitted"],
            x["initial_food"],tuple(x["initial_position"])):x for x in rows}
    firstpair=0
    afterpair=0
    waiting_contrast=0
    repeat_ambiguous=0
    movement_retreat_survival=0
    movement_wait_death=0
    hidden_move_inputs_equal=0
    for food in FOODS:
        for at in POSITIONS:
            for followup in FOOD_FOLLOWUPS:
                mild=index[("food","toxic_mild",followup,food,at)]
                conf=index[("food","exogenous_confounded",followup,food,at)]
                first_m=mild["physical_records"][2]
                first_c=conf["physical_records"][2]
                if first_m["state_before"]!=first_c["state_before"]:
                    raise AssertionError("confounded worlds differ BEFORE eating")
                if first_m["command"]!=first_c["command"]:
                    raise AssertionError("not same actually executed ingestion")
                if (first_m["state_after"]!=first_c["state_after"]
                    or first_m["terminal"]!=first_c["terminal"]):
                    raise AssertionError("confounded worlds distinguishable after eating")
                firstpair+=1
                afterpair+=1
                last_m=mild["physical_records"][3]
                last_c=conf["physical_records"][3]
                if followup=="wait":
                    if (last_m["state_after"]["body"]["integrity"] != 93
                        or last_c["state_after"]["body"]["integrity"] != 86):
                        raise AssertionError("wait followup fails to distinguish hidden causes")
                    waiting_contrast+=1
                else:
                    if last_m["state_after"]!=last_c["state_after"]:
                        raise AssertionError("second ingestion unexpectedly differentiated causes")
                    repeat_ambiguous+=1
            for variant in MOVE_VARIANTS:
                waiting=index[("movement",variant,"wait",food,at)]
                escaping=index[("movement",variant,"escape",food,at)]
                if (waiting["physical_records"][0]["state_before"]!=
                    escaping["physical_records"][0]["state_before"]
                    or waiting["physical_records"][0]["state_after"]!=
                    escaping["physical_records"][0]["state_after"]):
                    raise AssertionError("counterfactual bodies differ before followup")
                hidden_move_inputs_equal+=1
                if variant in ("danger_40","danger_55"):
                    if (waiting["first_terminal_step"] is None
                        or escaping["first_terminal_step"] is not None):
                        raise AssertionError("precommitted move/retreat contrast not reproduced")
                    movement_wait_death+=1
                    movement_retreat_survival+=1
    return {
        "paired_food_first_ingestion_same_accessible_input":firstpair,
        "paired_food_after_ingestion_identical_accessible_output":afterpair,
        "mild_toxin_vs_exogenous_wait_distinguished":waiting_contrast,
        "mild_toxin_vs_exogenous_repeat_eat_still_indistinguishable":
            repeat_ambiguous,
        "movement_paired_equal_first_step_outcomes":hidden_move_inputs_equal,
        "hazardous_wait_future_terminal_worlds":movement_wait_death,
        "paired_precommitted_retreat_survives":movement_retreat_survival,
        "does_not_identify_individual_subjective_cause":True,
    }


def execute(output: Path):
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    for kind,variants,followups in (
        ("food",FOOD_VARIANTS,FOOD_FOLLOWUPS),
        ("movement",MOVE_VARIANTS,MOVE_FOLLOWUPS),
    ):
        for variant in variants:
            for followup in followups:
                for food in FOODS:
                    for at in POSITIONS:
                        records.append(run_one(
                            kind=kind,variant=variant,followup=followup,
                            food=food,at=at,
                        ))
    controls=passive_cases()
    if (len(records),len(controls))!=(64,8):
        raise AssertionError("not 64 acted and 8 passive worlds")
    ids=[x["id"] for x in records]+[x["id"] for x in controls]
    if len(set(ids))!=EXPECTED_WORLDS:
        raise AssertionError("repeated physical worlds")
    steps=sum(x["physical_step_count"] for x in records)
    if steps!=EXPECTED_PHYSICAL_STEPS:
        raise AssertionError("physical steps changed from preregistration")
    food_rows=[r for r in records if r["kind"]=="food"]
    move_rows=[r for r in records if r["kind"]=="movement"]
    if (sum(x["physical_step_count"] for x in food_rows),
        sum(x["physical_step_count"] for x in move_rows))!=(120,76):
        raise AssertionError("food/movement stage physical-step total wrong")
    comparisons=comparison_witness(records)
    stage6=[q for r in food_rows for q in r["shadow_food"]]
    status_counts=Counter(q["stage6_status"] for q in stage6)
    before=[q for q in stage6 if q["t_query"]==3]
    after=[q for q in stage6 if q["t_query"]==4]
    if len(before)!=32 or len(after)!=24:
        raise AssertionError("wrong shadow stage6 actual pre/post alive counts")
    if not all(
        all(step<q["t_query"] for step in q["previous_observed_steps"])
        and q["no_shadow_command_dispatched"]
        for q in stage6
    ):
        raise AssertionError("Stage6 shadow violated causal timestamp")
    terminal=Counter()
    total_eats=0
    for x in records:
        if x["first_terminal_step"] is not None:
            terminal[x["kind"]]+=1
        total_eats+=sum(row["command"]["primitive"]=="manger"
                        for row in x["physical_records"])
    if total_eats!=44:
        raise AssertionError("wrong number of physically applied food consumptions")
    summary={
        "schema":"a230s-firstperson-controlled-information-v1",
        "analysis_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "acted_detached_worlds":len(records),
        "passive_observation_only_worlds":len(controls),
        "independent_lab_world_instances":len(ids),
        "actual_lab_physical_steps":steps,
        "food_physical_steps":120,
        "movement_physical_steps":76,
        "actually_executed_eat_commands":total_eats,
        "physically_terminal_worlds":dict(terminal),
        "shadow_stage6_queries":len(stage6),
        "shadow_food_before_first_ingestion_queries":len(before),
        "shadow_food_after_first_ingestion_queries":len(after),
        "shadow_stage6_statuses":dict(status_counts),
        "shadow_no_predictable_first_step":sum(
            q["stage6_diagnostic"]["root_model_diagnostic"]
            =="no_predictable_first_step" for q in stage6
        ),
        "shadow_first_step_known":sum(
            q["stage6_root_available_edges"]>0 for q in stage6
        ),
        "body_goal_setpoint":SHADOW_TARGET_FOOD,
        "shadow_max_depth":SHADOW_MAX_DEPTH,
        "first_person_observation_only":True,
        "shadow_prior_actions_exact_model_not_actual_I0_learning":True,
        "no_shadow_commands_physically_executed":True,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "not_deployable_to_I0":True,
        "oracle_feedback_to_I0":False,
        "mvp_spec_modified":False,
        "subjective_causal_attribution_demonstrated":False,
        "comparison":comparisons,
        "stage12":"PARTIAL",
        "issue110":"OPEN",
    }
    (output/"a230s-acted-worlds.json").write_text(
        json.dumps(records,indent=2,sort_keys=True)+"\n"
    )
    (output/"a230s-passive-worlds.json").write_text(
        json.dumps(controls,indent=2,sort_keys=True)+"\n"
    )
    (output/"a230s-summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n"
    )
    print("A230S_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    execute(args.output_dir)


if __name__=="__main__":
    main()
