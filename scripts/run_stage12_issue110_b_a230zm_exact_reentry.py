"""A2.30-ZM: prospective own-world exact-key motor reentry experiment.

Preregistered at 82cbb06b98d05816038db1fba02ce118cb1c5e7e, before
this code or any ZM physical world. 64 genuinely detached WorldBody worlds,
four observed east/south/west/north moves each (256 physical steps), four
prespecified physical fifth-move predictions (4 more), 64 genuine Stage6
shadow searches. ZERO I0 birth, lived I0 UC, or ingestion.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import subprocess

from i0.equipment import EquipmentCorpus, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout

from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config

POSITIONS=((5,5),(7,7))
LOCAL_B=(False,True)
ENERGY_COSTS=(0.0,1.0)
FOOD_DECAYS=(0.0,0.5)
WATER_DECAYS=(0.0,0.2)
NIGHT_STARTS=(200,3)
PATH=(
    PrimitiveCommand("se_deplacer",{"direction":"east"}),
    PrimitiveCommand("se_deplacer",{"direction":"south"}),
    PrimitiveCommand("se_deplacer",{"direction":"west"}),
    PrimitiveCommand("se_deplacer",{"direction":"north"}),
)
EAST=PATH[0]
EXPECTED_TEST_WORLDS=64
EXPECTED_PHYSICAL_STEPS=260
EXPECTED_FIRST_CYCLE_STEPS=256
EXPECTED_POSITIVE_REPLAYS=4
EXPECTED_PLANNER_SEARCHES=64
ACCESSIBLE={
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
}


def digest(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def visible(world,t):
    captured=SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    state=state_from_capture(capture=captured,is_night=world.is_night(t))
    state.validate()
    obj=state.as_dict()
    if (set(obj)!=ACCESSIBLE
        or set(obj["body"])!={"energy","food","water","integrity"}):
        raise ValueError("first-person state contains hidden or missing variables")
    return state


def recipes():
    for position,b_here,energy,food,water,night in product(
        POSITIONS,LOCAL_B,ENERGY_COSTS,FOOD_DECAYS,WATER_DECAYS,NIGHT_STARTS
    ):
        yield {
            "position":position,"b_here":b_here,
            "energy_cost":energy,"food_decay":food,
            "water_decay":water,"night_start":night,
        }


def make_world(position,b_here,energy_cost,food_decay,water_decay,night_start):
    """All factors specified before exposure; unseen physics stays LAB only."""
    if (tuple(position) not in POSITIONS or b_here not in LOCAL_B
        or energy_cost not in ENERGY_COSTS
        or food_decay not in FOOD_DECAYS
        or water_decay not in WATER_DECAYS
        or night_start not in NIGHT_STARTS):
        raise ValueError("world parameters not in preregistered factorial")
    initial=Position(*position)
    reference=physical_fixture_config()
    costs=dict(reference.action_energy_costs)
    costs["se_deplacer"]=energy_cost
    physics=replace(
        reference,
        version=(
            f"a230zm-motor-reentry-x{initial.x}y{initial.y}"
            f"-b{int(b_here)}-e{int(energy_cost*10)}"
            f"-f{int(food_decay*10)}-w{int(water_decay*10)}"
            f"-n{night_start}"
        ),
        initial_position=initial,
        action_energy_costs=costs,
        food_decay_per_step=food_decay,
        water_decay_per_step=water_decay,
        night_start_step=night_start,
    )
    layout=WorldLayout(
        resources=((initial,"berry_b",2),) if b_here else (),
    )
    physics.validate()
    layout.validate(physics)
    return physics,layout


def stage6_spatial_shadow(current,equipment,position):
    """Actual Stage6 search, NOT an I0 decision or executable safety verdict."""
    goal_x=position[0]+1
    goal_y=position[1]
    simulator=Simulator(
        config=SimulatorConfig(
            version="a230zm-readonly-exact-reentry-simulator-v1",
            r_max=1,h_max=3,
        ),
        equipment=equipment,
    )
    planner=SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="a230zm-readonly-exact-reentry-planner-v1",
            option_ttl_steps=5,max_depth=3,revision_delta=0.0,
            setpoints={
                "energy":65.0,"food":65.0,"water":65.0,"integrity":65.0,
            },
            progressive_subgoals=True,
            progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
        ),
        simulator=simulator,
    )
    response=planner.search(
        initial_state=current,
        target=lambda s:s.x==goal_x and s.y==goal_y,
        progress_measure=None, # no fake food progress licensed by movement
    )
    diagnostic=planner.last_search_diagnostic
    if diagnostic is None:
        raise AssertionError("Stage6 suppressed read-only search diagnostic")
    return {
        "requested_goal":"one_step_spatial_east_only",
        "target_x":goal_x,"target_y":goal_y,
        "input_state_sha256":digest(current.as_dict()),
        "status":response.status,
        "commands":[c.as_dict() for c in response.commands],
        "predictions":[{
            "command":p.command.as_dict(),
            "next_state":p.next_state.as_dict(),
            "terminal":p.terminal,
            "confidence":p.confidence,
        } for p in response.predictions],
        "root_candidate_edges":response.root_candidate_edges,
        "root_available_edges":response.root_available_edges,
        "root_unavailable_edges":response.root_unavailable_edges,
        "expanded_states":response.expanded_states,
        "unavailable_edges_total":response.unavailable_edges,
        "partial_progress":response.partial_progress,
        "diagnostic":diagnostic,
        "no_shadow_action_dispatched":True,
        "not_a_food_goal":True,
        "no_B_ingestion_or_safety_claim":True,
        "real_i0_uc_cost_measured":False,
    }


def play_cell(position,b_here,energy_cost,food_decay,water_decay,night_start):
    physics,layout=make_world(
        position,b_here,energy_cost,food_decay,water_decay,night_start,
    )
    world_id=(
        f"a230zm:x{position[0]}y{position[1]}:b{int(b_here)}"
        f":energy{energy_cost}:food{food_decay}:water{water_decay}"
        f":night{night_start}"
    )
    world=WorldBody(config=physics,layout=layout)
    recorder=EquipmentCorpusRecorder(
        corpus_version="a230zm-world-provenance-"+world_id,
    )
    start=visible(world,1)
    if (start.x,start.y)!=position:
        raise AssertionError("initial physical position not preregistered")
    examples=[]
    physical_receipts=[]
    prior=start
    for step,command in enumerate(PATH,1):
        now=visible(world,step)
        if now!=prior:
            raise AssertionError("physical and perceptual world chronology diverged")
        if command not in SimulatorPlanner.candidate_commands(now):
            raise AssertionError("preregistered motor step not perceptually admissible")
        ex=recorder.record_transition(
            world=world,t_monde=step,
            family="a230zm-closed-loop-movement-physically-observed",
            command=command,
        )
        if ex.state!=now or ex.terminal:
            raise AssertionError("preregistered four-move safe loop became invalid")
        seen_after=visible(world,step+1)
        if ex.observed_next_state!=seen_after:
            raise AssertionError("physical output does not match new observable state")
        examples.append(ex)
        physical_receipts.append({
            "step":step,
            "source_world":world_id,
            "physical_example":ex.as_dict(),
            "physical_example_sha256":digest(ex.as_dict()),
            "command":command.as_dict(),
            "state_before":now.as_dict(),
            "state_after":seen_after.as_dict(),
            "terminal":False,
        })
        prior=seen_after
    end=prior
    same=end==start
    no_drift=(
        energy_cost==0.0 and food_decay==0.0
        and water_decay==0.0 and night_start==200
    )
    if same!=no_drift:
        raise AssertionError("preregistered full-state reentry condition contradicted")
    if (end.x,end.y)!=(start.x,start.y):
        raise AssertionError("four-move loop failed to return spatially")
    if (end.current_resources!=start.current_resources
        or end.inventory!=start.inventory
        or end.known_shelter_here!=start.known_shelter_here):
        raise AssertionError("closed movement mutated unrelated resources/affordances")
    before_body=start.body
    after_body=end.body
    bodily_changes={
        name:round(float(after_body[name])-float(before_body[name]),9)
        for name in ("energy","food","water","integrity")
    }
    expected_drift={
        "energy":round(-4*energy_cost,9),
        "food":round(-4*food_decay,9),
        "water":round(-4*water_decay,9),
        "integrity":0.0,
    }
    if bodily_changes!=expected_drift or end.is_night != (night_start==3):
        raise AssertionError("physical body/night drift violated locked factorial")
    corpus=EquipmentCorpus(
        version=f"a230zm-own-world-four-physical-moves-{world_id}",
        examples=tuple(examples),
    )
    equipment=train_exact_transition_table(
        corpus=corpus,equipment_version=f"E-a230zm-{world_id}",
    )
    # FIRST action was genuinely lived but may not be reusable at t5.
    first_digest=equipment.input_digest(start,EAST)
    returned_digest=equipment.input_digest(end,EAST)
    known=None
    try:
        known=equipment.predict(state=end,command=EAST)
    except LookupError:
        pass
    if (known is not None)!=same or (first_digest==returned_digest)!=same:
        raise AssertionError("exact lookup failed to respect COMPLETE first-person key")
    if known is not None and (
        known.terminal
        or known.next_state!=examples[0].observed_next_state
        or known.command!=EAST
    ):
        raise AssertionError("correct re-entry prediction diverged from physical memory")
    plan=stage6_spatial_shadow(end,equipment,position)
    if plan["input_state_sha256"]!=digest(end.as_dict()):
        raise AssertionError("shadow searched a different first-person state")
    if same:
        if (plan["status"]!="plan_found"
            or plan["root_available_edges"]!=1
            or plan["commands"]!=[EAST.as_dict()]
            or len(plan["predictions"])!=1
            or plan["predictions"][0]["terminal"] is not False
            or plan["predictions"][0]["next_state"]!=
                examples[0].observed_next_state.as_dict()):
            raise AssertionError("positive reentrant one-step spatial plan absent")
    else:
        if (plan["status"]!="incomplete_model"
            or plan["root_available_edges"]!=0
            or plan["root_unavailable_edges"]!=plan["root_candidate_edges"]
            or plan["commands"] or plan["predictions"]):
            raise AssertionError("unmatched full-body/night state falsely reused a motor edge")
    physical_positive=None
    if no_drift:  # precommitted positive control, not chosen by outcome
        if known is None:
            raise AssertionError("positive fifth move lacks first physical evidence")
        pre=visible(world,5)
        if pre!=end:
            raise AssertionError("physical positive check started from altered root")
        witnessed=recorder.record_transition(
            world=world,t_monde=5,
            family="a230zm-preregistered-fifth-move-positive-control",
            command=EAST,
        )
        after=visible(world,6)
        if (witnessed.state!=pre
            or witnessed.terminal
            or witnessed.observed_next_state!=after
            or known.next_state!=after):
            raise AssertionError("known first-person prediction failed independent fifth act")
        physical_positive={
            "step":5,
            "source_world":world_id,
            "physical_example":witnessed.as_dict(),
            "physical_example_sha256":digest(witnessed.as_dict()),
            "predicted_next_state":known.next_state.as_dict(),
            "observed_next_state":after.as_dict(),
            "exact_prediction_equals_fifth_physical_outcome":True,
            "not_trained_on_fifth_action_before_prediction":True,
        }
    return {
        "world_id":world_id,
        "factor_position":list(position),
        "factor_berry_B_local_visible":b_here,
        "factor_movement_energy_cost":energy_cost,
        "factor_food_decay":food_decay,
        "factor_water_decay":water_decay,
        "factor_night_start":night_start,
        "world_physics_sha256_external_only":physics.digest(),
        "world_layout_sha256_external_only":digest(layout.as_dict()),
        "initial_firstperson":start.as_dict(),
        "returned_firstperson":end.as_dict(),
        "firstperson_initial_sha256":digest(start.as_dict()),
        "firstperson_return_sha256":digest(end.as_dict()),
        "all_four_physical_movements":physical_receipts,
        "old_first_step_input_sha256":first_digest,
        "new_first_step_input_sha256":returned_digest,
        "same_coordinates_after_cycle":True,
        "same_visible_resources_after_cycle":True,
        "body_deltas_after_four_steps":bodily_changes,
        "initial_is_night":start.is_night,
        "returned_is_night":end.is_night,
        "full_firstperson_state_reentered":same,
        "first_move_exact_known_at_return":known is not None,
        "old_transition_only_own_world_physical":True,
        "trained_examples":len(examples),
        "training_world_id":world_id,
        "equipment_sha256":equipment.artifact_digest,
        "planner_stage6_shadow":plan,
        "precommitted_fifth_positive_physical_control":physical_positive,
        "no_berry_B_ingestion":True,
        "no_postmortem_experience":True,
        "model_certifies_safety":False,
        "actual_i0_births":0,
        "actual_i0_autonomous_steps":0,
        "real_i0_UC_cost_measured":False,
        "no_stage6_shadow_action_dispatched":True,
    }


def audit_read_only_output(worlds):
    """Score receipts from a separate pure read path, no physics or model."""
    if len(worlds)!=EXPECTED_TEST_WORLDS:
        raise ValueError("incomplete prospective world factorial")
    seen=set()
    totals=Counter()
    by_mechanism=defaultdict(Counter)
    for row in worlds:
        fact=(
            tuple(row["factor_position"]),
            row["factor_berry_B_local_visible"],
            row["factor_movement_energy_cost"],
            row["factor_food_decay"],
            row["factor_water_decay"],
            row["factor_night_start"],
        )
        if fact in seen:
            raise ValueError("duplicate original physical factorial combination")
        seen.add(fact)
        if row["world_id"]!=(
            f"a230zm:x{fact[0][0]}y{fact[0][1]}:b{int(fact[1])}"
            f":energy{fact[2]}:food{fact[3]}:water{fact[4]}:night{fact[5]}"
        ):
            raise ValueError("scientific source world identity no longer matches")
        start=row["initial_firstperson"]
        returned=row["returned_firstperson"]
        if (set(start)!=ACCESSIBLE or set(returned)!=ACCESSIBLE
            or row["firstperson_initial_sha256"]!=digest(start)
            or row["firstperson_return_sha256"]!=digest(returned)
            or row["same_coordinates_after_cycle"] is not True
            or row["same_visible_resources_after_cycle"] is not True
            or (start["x"],start["y"])!=fact[0]
            or (returned["x"],returned["y"])!=fact[0]
            or (("berry_b" in start["current_resources"]) is not fact[1])
            or returned["current_resources"]!=start["current_resources"]
            or returned["inventory"]!=start["inventory"]
            or row["initial_is_night"]!=start["is_night"]
            or row["returned_is_night"]!=returned["is_night"]
            or row["returned_is_night"]!=(fact[5]==3)
            or row["full_firstperson_state_reentered"]!=(start==returned)
            or row["old_first_step_input_sha256"]==row["new_first_step_input_sha256"]
               !=(start==returned)):
            raise ValueError("false perceptual/physical reentry or provenance")
        expected={
            "energy":-4*fact[2],
            "food":-4*fact[3],
            "water":-4*fact[4],
            "integrity":0.0,
        }
        if any(abs(row["body_deltas_after_four_steps"][k]-v)>1e-8
               for k,v in expected.items()):
            raise ValueError("visible metabolic/energy drift misreported")
        positive=(
            fact[2]==0.0 and fact[3]==0.0
            and fact[4]==0.0 and fact[5]==200
        )
        if (positive != (start==returned)
            or row["first_move_exact_known_at_return"] is not positive
            or row["old_transition_only_own_world_physical"] is not True
            or row["training_world_id"]!=row["world_id"]
            or row["trained_examples"]!=4
            or row["no_berry_B_ingestion"] is not True
            or row["no_postmortem_experience"] is not True
            or row["model_certifies_safety"] is not False
            or row["actual_i0_births"]!=0
            or row["actual_i0_autonomous_steps"]!=0
            or row["real_i0_UC_cost_measured"] is not False
            or row["no_stage6_shadow_action_dispatched"] is not True):
            raise ValueError("fabricated known state, I0 agency, safety or UC")
        receipts=row["all_four_physical_movements"]
        if len(receipts)!=4:
            raise ValueError("non-four-step real loop")
        for i,rx in enumerate(receipts):
            ex=rx["physical_example"]
            if (rx["step"]!=i+1
                or rx["source_world"]!=row["world_id"]
                or ex["command"]!=PATH[i].as_dict()
                or rx["command"]!=ex["command"]
                or rx["physical_example_sha256"]!=digest(ex)
                or rx["state_before"]!=ex["state"]
                or rx["state_after"]!=ex["observed_next_state"]
                or rx["terminal"] is not False
                or ex["terminal"] is not False):
                raise ValueError("corrupted original motor causal/terminal receipt")
            if i==0 and ex["state"]!=start:
                raise ValueError("first movement didn't physically start at root")
            if i>0 and receipts[i-1]["state_after"]!=rx["state_before"]:
                raise ValueError("noncontiguous physically lived motor loop")
        if receipts[-1]["state_after"]!=returned:
            raise ValueError("terminal physical loop does not reach returned perception")
        shadow=row["planner_stage6_shadow"]
        if (shadow["input_state_sha256"]!=digest(returned)
            or shadow["no_shadow_action_dispatched"] is not True
            or shadow["not_a_food_goal"] is not True
            or shadow["no_B_ingestion_or_safety_claim"] is not True
            or shadow["real_i0_uc_cost_measured"] is not False
            or shadow["target_x"]!=fact[0][0]+1
            or shadow["target_y"]!=fact[0][1]
            or shadow["requested_goal"]!="one_step_spatial_east_only"):
            raise ValueError("shadow used future/Oracle/food instead of spatial target")
        if positive:
            if (shadow["status"]!="plan_found"
                or shadow["root_available_edges"]!=1
                or shadow["commands"]!=[EAST.as_dict()]
                or len(shadow["predictions"])!=1):
                raise ValueError("reentry positive Stage6 plan absent")
        else:
            if (shadow["status"]!="incomplete_model"
                or shadow["root_available_edges"]!=0
                or shadow["root_unavailable_edges"]!=shadow["root_candidate_edges"]
                or shadow["commands"] or shadow["predictions"]):
                raise ValueError("unseen firstperson full root pretended model-known")
        positive_check=row["precommitted_fifth_positive_physical_control"]
        if positive != (positive_check is not None):
            raise ValueError("fifth physical act selected by posthoc outcome")
        if positive_check is not None:
            if (positive_check["step"]!=5
                or positive_check["source_world"]!=row["world_id"]
                or positive_check["physical_example_sha256"]!=digest(
                    positive_check["physical_example"]
                )
                or positive_check["physical_example"]["state"]!=returned
                or positive_check["physical_example"]["command"]!=EAST.as_dict()
                or positive_check["physical_example"]["terminal"] is not False
                or positive_check["predicted_next_state"]!=
                   positive_check["observed_next_state"]
                or positive_check["observed_next_state"]!=
                   positive_check["physical_example"]["observed_next_state"]
                or shadow["predictions"][0]["next_state"]!=
                   positive_check["observed_next_state"]
                or positive_check["not_trained_on_fifth_action_before_prediction"] is not True):
                raise ValueError("fifth physical move contradicts first-person prediction")
        totals["worlds"]+=1
        totals["original_actions"]+=len(receipts)
        totals["fifth_physical_check_actions"]+=positive_check is not None
        totals["exact_full_state_reentries"]+=positive
        totals["nonidentical_full_state_returns"]+=not positive
        totals["spatial_goal_plans_found"]+=shadow["status"]=="plan_found"
        totals["no_root_known_status"]+=shadow["status"]=="incomplete_model"
        totals["actual_stage6_searches"]+=1
        factor_label=(
            "all_zero_day" if positive else
            "night_context_changed" if fact[5]==3 and
                fact[2]==0 and fact[3]==0 and fact[4]==0 else
            "visible_body_drift"
        )
        by_mechanism[factor_label]["worlds"]+=1
        by_mechanism[factor_label]["known_root"]+=shadow["root_available_edges"]>0
    if len(seen)!=64 or (
        totals["original_actions"]+totals["fifth_physical_check_actions"]
    )!=EXPECTED_PHYSICAL_STEPS or (
        totals["original_actions"]!=EXPECTED_FIRST_CYCLE_STEPS
        or totals["fifth_physical_check_actions"]!=EXPECTED_POSITIVE_REPLAYS
        or totals["exact_full_state_reentries"]!=4
        or totals["nonidentical_full_state_returns"]!=60
        or totals["spatial_goal_plans_found"]!=4
        or totals["no_root_known_status"]!=60
        or totals["actual_stage6_searches"]!=EXPECTED_PLANNER_SEARCHES
    ):
        raise ValueError("prespecified motor-reentry cohorts/metrics did not materialize")
    return {
        "schema":"a230zm-exact-firstperson-reentry-v1",
        "independent_detached_WorldBody_worlds":64,
        "real_physically_applied_closed_loop_steps":256,
        "real_fifth_control_physical_steps":4,
        "real_physical_steps_total":260,
        "actual_stage6_shadow_searches":64,
        "spatially_returned_to_initial_cell":64,
        "exact_firstperson_state_reentered":totals["exact_full_state_reentries"],
        "same_location_but_changed_full_state":
            totals["nonidentical_full_state_returns"],
        "first_move_exact_key_known_at_return":
            totals["exact_full_state_reentries"],
        "stage6_one_step_spatial_plans_found":
            totals["spatial_goal_plans_found"],
        "stage6_incomplete_model":
            totals["no_root_known_status"],
        "physically_revalidated_predictions":
            totals["fifth_physical_check_actions"],
        "terminal_physical_worlds":0,
        "Berry_B_ingestions":0,
        "new_I0_births":0,
        "new_I0_autonomous_steps":0,
        "real_I0_UC_measured":False,
        "firstperson_safe_motor_generalization_proven":False,
        "external_laboratory_probes_only":True,
        "same_site_is_not_same_state_in_other_60_worlds":True,
        "by_mechanism":{
            key:dict(value) for key,value in sorted(by_mechanism.items())
        },
        "stage12":"PARTIAL","issue110":"OPEN",
        "scientific_verdict":"A2.30 PARTIELLE",
        "cognitive_deployment":"NO-GO",
    }


def experiment(folder):
    folder.mkdir(parents=True,exist_ok=False)
    rows=[play_cell(**cell) for cell in recipes()]
    results=audit_read_only_output(rows)
    results.update({
        "code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True,
        ).strip(),
        "physical_worlds_sha256":digest(rows),
        "both_python_jobs_repeat_same_cells_not_new_scientific_samples":True,
        "normative_mvp_or_i0_runtime_changed":False,
    })
    (folder/"a230zm-physical-loop-worlds.json").write_text(
        json.dumps(rows,sort_keys=True,indent=2)+"\n"
    )
    (folder/"a230zm-summary.json").write_text(
        json.dumps(results,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZM_SUMMARY "+json.dumps(results,sort_keys=True),flush=True)
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    experiment(a.output_dir)


if __name__=="__main__":
    main()
