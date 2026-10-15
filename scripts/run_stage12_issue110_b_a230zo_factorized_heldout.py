"""A2.30-ZO: prospective external partial observable-delta learner, 120 worlds.

Protocol sealed BEFORE code/physics at 8f4846826394ed34519710d4774ac8c04f691b8a.
All evidence is WorldBody.apply in detached research worlds, NEVER lived by I0.
Learn only empirical x/y/energy/food/water/inventory B changes. Deliberately
DO NOT predict integrity, mortality, safety, neighbor state or entire
SimulationState, even where numeric forecasts happen to be correct.
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
from i0.modules.stage6_planning import SimulatorPlanner
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout

from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config
from run_stage12_issue110_b_a230zg_lived_root_shadow import first_person

PREREG="8f4846826394ed34519710d4774ac8c04f691b8a"
TRAIN_POS=((5,5),(7,7))
TEST_POS=((9,9),(11,11),(13,13),(15,15))
TRAIN_FOOD=(35.0,45.0)
NOMINAL_BODIES=((35.0,25.0,30.0),(70.0,55.0,65.0))
BOUNDARY_BODY=(0.5,0.25,0.1)
PHASES=(1,201)
ACTIONS=("MOVE_E","COLLECT_B")
HIDDEN_B=("benign","toxic_lethal")
INTERVENTIONS=("hidden_lethal_east","hidden_danger_here",
               "hidden_forced_action_failure")
TRAIN_N=16
NOMINAL_N=64
HIDDEN_N=24
BOUNDARY_N=16
EXPECTED_TOTAL=120
EXPECTED_HAZARD_DEATHS=4
EXPECTED_HAZARD_INJURIES=8
EXPECTED_HAZARD_FORCED_FAILURES=8
DELTA_KEYS=("x","y","energy","food","water","inventory_berry_b")
BODY_KEYS=("energy","food","water","integrity")
MOVE=PrimitiveCommand("se_deplacer",{"direction":"east"})
COLLECT=PrimitiveCommand("collecter",{"target":"berry_b"})
COMMAND={"MOVE_E":MOVE,"COLLECT_B":COLLECT}
VISIBLE_KEYS={
    "schema_version","x","y","body","inventory",
    "current_resources","current_water_source","adjacent",
    "known_shelter_here","is_night",
}


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def visible_only(state):
    if (type(state) is not dict or set(state)!=VISIBLE_KEYS
        or set(state["body"])!=set(BODY_KEYS)
        or len(state["adjacent"])!=4
        or {n["direction"] for n in state["adjacent"]}!=
           {"north","south","east","west"}):
        raise ValueError("hidden or missing feature in first-person model input")
    if any(set(n)!={
        "direction","x","y","passable","water_source","resources","creature"
    } for n in state["adjacent"]):
        raise ValueError("hidden neighbor feature in sensory input")
    return state


def body_delta(bef,aft):
    return {
        "x":int(aft["x"]-bef["x"]),
        "y":int(aft["y"]-bef["y"]),
        "energy":round(float(aft["body"]["energy"])-float(bef["body"]["energy"]),8),
        "food":round(float(aft["body"]["food"])-float(bef["body"]["food"]),8),
        "water":round(float(aft["body"]["water"])-float(bef["body"]["water"]),8),
        "inventory_berry_b":int(aft["inventory"]["berry_b"]-
                                bef["inventory"]["berry_b"]),
    }


def recipe_row(group,position,body,phase,action,hidden_B="benign",
               intervention="none"):
    if group not in ("TRAIN","NOMINAL","HIDDEN","BOUNDARY"):
        raise ValueError("unregistered heldout cohort")
    if (position not in TRAIN_POS+TEST_POS or phase not in PHASES
        or action not in ACTIONS or hidden_B not in HIDDEN_B
        or intervention not in ("none",)+INTERVENTIONS):
        raise ValueError("unregistered physical recipe")
    if (len(body)!=3 or any(type(x) not in (int,float) for x in body)):
        raise ValueError("invalid body-factor tuple")
    name=(
        f"a230zo:{group}:x{position[0]}y{position[1]}:"
        f"e{body[0]}f{body[1]}w{body[2]}:"
        f"t{phase}:{action}:B{hidden_B}:{intervention}"
    )
    return {
        "world_id":name,"cohort":group,"position":tuple(position),
        "body":tuple(float(x) for x in body),
        "t_monde":phase,"action":action,
        "hidden_B":hidden_B,"intervention":intervention,
    }


def registered_recipes():
    train=[
        recipe_row("TRAIN",pos,(50.0,food,40.0),phase,act)
        for pos,food,phase,act in product(
            TRAIN_POS,TRAIN_FOOD,PHASES,ACTIONS
        )
    ]
    nominal=[
        recipe_row("NOMINAL",pos,body,phase,act,h)
        for pos,body,phase,act,h in product(
            TEST_POS,NOMINAL_BODIES,PHASES,ACTIONS,HIDDEN_B
        )
    ]
    hazard=[
        recipe_row("HIDDEN",pos,NOMINAL_BODIES[0],1,act,
                   intervention=hazard)
        for pos,act,hazard in product(TEST_POS,ACTIONS,INTERVENTIONS)
    ]
    boundary=[
        recipe_row("BOUNDARY",pos,BOUNDARY_BODY,phase,act)
        for pos,act,phase in product(TEST_POS,ACTIONS,PHASES)
    ]
    if [len(x) for x in (train,nominal,hazard,boundary)]!=[
        TRAIN_N,NOMINAL_N,HIDDEN_N,BOUNDARY_N
    ]:
        raise AssertionError("preregistered factorial size was changed")
    everything=train+nominal+hazard+boundary
    if len({r["world_id"] for r in everything})!=EXPECTED_TOTAL:
        raise AssertionError("physical world identities not independent")
    return train,nominal,hazard,boundary


def physical_fixture(recipe):
    """All hidden facts are external to learner / frozen predictor."""
    base=physical_fixture_config()
    action=recipe["action"]
    pos=Position(*recipe["position"])
    energy,food,water=recipe["body"]
    costs=dict(base.action_energy_costs)
    costs.update({"se_deplacer":1.0,"collecter":0.75})
    effects=dict(base.berry_effects)
    effects["berry_b"]=replace(
        effects["berry_b"],food_gain=12.0,
        integrity_delta=(
            0.0 if recipe["hidden_B"]=="benign" else -100.0
        ),
    )
    config=replace(
        base,version="a230zo-external-physics-"+recipe["world_id"],
        initial_position=pos,
        initial_body=replace(
            base.initial_body,energy=energy,food=food,water=water,
            integrity=100.0,
        ),
        food_decay_per_step=0.5,water_decay_per_step=0.2,
        action_energy_costs=costs,berry_effects=effects,
        danger_zone_damage=10.0,
    )
    hazard=recipe["intervention"]
    east=pos.moved("east")
    danger=(frozenset({
        east if action=="MOVE_E" else pos
    }) if hazard=="hidden_danger_here" else frozenset())
    lethal=(frozenset({east})
            if hazard=="hidden_lethal_east" else frozenset())
    layout=WorldLayout(
        resources=((pos,"berry_b",2),),
        lethal_zones=lethal,danger_zones=danger,
    )
    config.validate()
    layout.validate(config)
    return config,layout


def check_action_eligible(state,action):
    visible_only(state)
    cmd=COMMAND[action]
    from run_stage12_issue110_b_a230zg_lived_root_shadow import (
        decode_state,
    )
    decoded=decode_state(state)
    if cmd not in SimulatorPlanner.candidate_commands(decoded):
        raise AssertionError("precommitted physical command not visible/eligible")
    if action=="MOVE_E":
        if not next(n for n in state["adjacent"]
                    if n["direction"]=="east")["passable"]:
            raise AssertionError("movements require a visible open east cell")
    else:
        if "berry_b" not in state["current_resources"]:
            raise AssertionError("cannot collect an invisible berry")
    return cmd


def apply_one(recipe):
    config,layout=physical_fixture(recipe)
    world=WorldBody(config=config,layout=layout)
    command=COMMAND[recipe["action"]]
    t=recipe["t_monde"]
    if recipe["intervention"]=="hidden_forced_action_failure":
        # Hidden physical intervention is scheduled BEFORE the first capture.
        world.apply_scenario_event(
            "set_action_failure_schedule",
            {"primitive":command.primitive,"schedule":[True]},
        )
    before=first_person(world,t)
    cmd=check_action_eligible(before.as_dict(),recipe["action"])
    if cmd.primitive=="manger":
        raise AssertionError("ingestion forbidden")
    recorder=EquipmentCorpusRecorder(
        corpus_version="a230zo-"+recipe["world_id"],
    )
    example=recorder.record_transition(
        world=world,t_monde=t,
        family="a230zo-externally-controlled-one-step-"+recipe["action"],
        command=cmd,
    )
    if example.state!=before:
        raise AssertionError("pre-action physical state not first-person")
    # AFTER (including terminal) is an EXTERNAL receipt, not a lived I0 state.
    after=example.observed_next_state.as_dict()
    if example.terminal:
        world.freeze_terminal_state()
    row={
        "world_id":recipe["world_id"],
        "preregistered_cohort":recipe["cohort"],
        "source_or_heldout":(
            "external_train" if recipe["cohort"]=="TRAIN"
            else "previously_unseen_heldout"
        ),
        "position_factor_external":list(recipe["position"]),
        "body_factor_external":list(recipe["body"]),
        "phase_factor_external":t,
        "command_label":recipe["action"],
        "latent_berry_effect_external_only":recipe["hidden_B"],
        "hidden_intervention_external_only":recipe["intervention"],
        "physical_config_sha256_external_only":config.digest(),
        "physical_layout_sha256_external_only":digest(layout.as_dict()),
        "preaction_first_person":before.as_dict(),
        "preaction_sha256":digest(before.as_dict()),
        "action_physically_applied":cmd.as_dict(),
        "physical_example":example.as_dict(),
        "physical_example_sha256":digest(example.as_dict()),
        "postaction_external_only":after,
        "physically_terminal_external_only":example.terminal,
        "postdeath_lived_capture":None,
        "world_sealed_on_terminal":bool(example.terminal),
        "no_i0_birth_or_autonomous_step":True,
        "no_berry_ingestion":True,
        "actual_i0_uc_measured":None,
        "no_oracle_or_hidden_input_to_prediction":True,
        "safety_certificate":None,
    }
    return row,example


def fit_partial_empirical(training_rows):
    """Only visible before/after + action, no body config or hidden labels."""
    if len(training_rows)!=TRAIN_N:
        raise ValueError("training corpus not 16 physically witnessed steps")
    grouped=defaultdict(list)
    for row in training_rows:
        if row["preregistered_cohort"]!="TRAIN":
            raise ValueError("leakage of heldout physical example into training")
        before=visible_only(row["preaction_first_person"])
        ex=row["physical_example"]
        if (row["physical_example_sha256"]!=digest(ex)
            or ex["state"]!=before or ex["terminal"] is not False):
            raise ValueError("invalid prospective source physical receipt")
        if (row["command_label"] not in ACTIONS
            or row["action_physically_applied"]!=COMMAND[
                row["command_label"]].as_dict()
            or ex["command"]!=row["action_physically_applied"]):
            raise ValueError("training command aliasing or tampering")
        after=visible_only(ex["observed_next_state"])
        delta=body_delta(before,after)
        grouped[row["command_label"]].append(delta)
    if set(grouped)!=set(ACTIONS) or any(
        len(grouped[action])!=8 for action in ACTIONS
    ):
        raise ValueError("preregistered action split changed")
    fitted={}
    for action in ACTIONS:
        delta={}
        for key in DELTA_KEYS:
            unique={r[key] for r in grouped[action]}
            if len(unique)!=1:
                delta[key]=None  # unknown component, not arbitrary interpolation
            else:
                delta[key]=next(iter(unique))
        fitted[action]={
            "supported_empirical_deltas":delta,
            "physically_observed_training_examples":len(grouped[action]),
            "unresolved_integrity":None,
            "unresolved_terminality":None,
            "unresolved_new_adjacency":None,
            "unresolved_food_safety":None,
            "general_safety_claim":False,
        }
    return fitted


def partial_forecast(model,state,action):
    """Numerical *forecast*, not a full state, plan or safety guarantee."""
    visible_only(state)
    if (type(model) is not dict or set(model)!=set(ACTIONS)
        or action not in ACTIONS):
        raise ValueError("unsupported predictor or action")
    row=model[action]
    expected={"supported_empirical_deltas",
              "physically_observed_training_examples",
              "unresolved_integrity","unresolved_terminality",
              "unresolved_new_adjacency","unresolved_food_safety",
              "general_safety_claim"}
    if (set(row)!=expected
        or any(row[k] is not None for k in (
            "unresolved_integrity","unresolved_terminality",
            "unresolved_new_adjacency","unresolved_food_safety"
        ))
        or row["general_safety_claim"] is not False):
        raise ValueError("unsafe learned model asserts hazard certainty")
    delta=row["supported_empirical_deltas"]
    if set(delta)!=set(DELTA_KEYS):
        raise ValueError("partial model contains foreign model dimension")
    # Precondition classification uses ONLY first-person accessible cues.
    if action=="COLLECT_B" and "berry_b" not in state["current_resources"]:
        return {
            "status":"abstain_ineligible","estimated":None,
            "integrity":None,"terminal":None,
            "next_adjacency":None,"safe":None,
        }
    east=next(n for n in state["adjacent"] if n["direction"]=="east")
    if action=="MOVE_E" and not east["passable"]:
        return {
            "status":"abstain_ineligible","estimated":None,
            "integrity":None,"terminal":None,
            "next_adjacency":None,"safe":None,
        }
    if any(delta[k] is None for k in DELTA_KEYS):
        return {
            "status":"abstain_unstable_training","estimated":None,
            "integrity":None,"terminal":None,
            "next_adjacency":None,"safe":None,
        }
    for k in ("energy","food","water"):
        if float(state["body"][k])+float(delta[k])<0.0:
            return {
                "status":"abstain_clamp","estimated":None,
                "integrity":None,"terminal":None,
                "next_adjacency":None,"safe":None,
            }
    forecast={
        "x":int(state["x"]+delta["x"]),
        "y":int(state["y"]+delta["y"]),
        "energy":round(float(state["body"]["energy"])+delta["energy"],8),
        "food":round(float(state["body"]["food"])+delta["food"],8),
        "water":round(float(state["body"]["water"])+delta["water"],8),
        "inventory_berry_b":int(
            state["inventory"]["berry_b"]+delta["inventory_berry_b"]
        ),
    }
    # NEVER construct SimulationState from these partial fields.
    return {
        "status":"empirical_partial_not_certified",
        "estimated":forecast,
        "integrity":None,"terminal":None,
        "next_adjacency":None,"safe":None,
    }


def compare_forecast(row,prediction,exact_model):
    if row["preregistered_cohort"]=="TRAIN":
        raise AssertionError("training examples are not heldout measurements")
    source=row["physical_example"]
    before=visible_only(row["preaction_first_person"])
    after=visible_only(row["postaction_external_only"])
    action=row["command_label"]
    if (source["terminal"]!=row["physically_terminal_external_only"]
        or source["state"]!=before
        or source["observed_next_state"]!=after):
        raise ValueError("external physical receipt changed before scoring")
    command=COMMAND[action]
    try:
        exact_model.predict(
            state=__import__(
                "run_stage12_issue110_b_a230zg_lived_root_shadow"
            ).decode_state(before),
            command=command,
        )
    except LookupError:
        exact_known=False
    else:
        exact_known=True
    expected=partial_forecast(prediction,before,action)
    target={
        "x":after["x"],"y":after["y"],
        "energy":after["body"]["energy"],
        "food":after["body"]["food"],
        "water":after["body"]["water"],
        "inventory_berry_b":after["inventory"]["berry_b"],
    }
    match={}
    if expected["estimated"] is not None:
        match={
            k:(
                abs(float(expected["estimated"][k])-float(target[k]))<1e-8
            ) for k in target
        }
    return {
        "original_train_model_firstperson_exact_key_known":exact_known,
        "frozen_empirical_prediction":expected,
        "actual_partial_target_external_only":target,
        "component_match_external_scoring_only":match,
        "all_six_components_match_external_only":(
            all(match.values()) if match else None
        ),
        "physical_terminal_external_only":source["terminal"],
        "physical_integrity_delta_external_only":round(
            float(after["body"]["integrity"])-
            float(before["body"]["integrity"]),8
        ),
        "hidden_cause_never_in_firstperson_prediction":True,
        "no_hazard_or_safe_inferred":True,
    }


def review_results(training,heldout,model,score):
    """Read-only external audit before accepting any aggregate."""
    if (len(training)!=TRAIN_N or len(heldout)!=EXPECTED_TOTAL-TRAIN_N
        or len({x["world_id"] for x in training+heldout})!=EXPECTED_TOTAL):
        raise ValueError("physical world cohort missing/duplicated")
    if len(score)!=len(heldout):
        raise ValueError("heldout score missing cases")
    counters=defaultdict(Counter)
    records={}
    for row in training+heldout:
        if row["world_id"] in records:
            raise ValueError("duplicate actual independent world ID")
        records[row["world_id"]]=row
        ex=row["physical_example"]
        if (row["physical_example_sha256"]!=digest(ex)
            or row["preaction_sha256"]!=digest(row["preaction_first_person"])
            or ex["state"]!=row["preaction_first_person"]
            or ex["observed_next_state"]!=row["postaction_external_only"]
            or ex["terminal"]!=row["physically_terminal_external_only"]
            or row["no_i0_birth_or_autonomous_step"] is not True
            or row["no_berry_ingestion"] is not True
            or row["postdeath_lived_capture"] is not None
            or row["actual_i0_uc_measured"] is not None
            or row["safety_certificate"] is not None
            or row["no_oracle_or_hidden_input_to_prediction"] is not True):
            raise ValueError("unsafe or tampered source physical receipt")
        if row["world_sealed_on_terminal"]!=ex["terminal"]:
            raise ValueError("terminal world not sealed")
        if ex["command"]["primitive"]=="manger":
            raise ValueError("ingestion was performed without preregistration")
    for row,sc in zip(heldout,score):
        group=row["preregistered_cohort"]
        if group not in ("NOMINAL","HIDDEN","BOUNDARY"):
            raise ValueError("unregistered test source in scorer")
        if (sc["hidden_cause_never_in_firstperson_prediction"] is not True
            or sc["no_hazard_or_safe_inferred"] is not True
            or sc["original_train_model_firstperson_exact_key_known"] is not False):
            raise ValueError("future first-person key leak or unsafe certainty")
        pred=sc["frozen_empirical_prediction"]
        if (set(pred)!={
            "status","estimated","integrity","terminal","next_adjacency","safe"
        } or any(pred[k] is not None for k in (
            "integrity","terminal","next_adjacency","safe"
        ))):
            raise ValueError("partial predictor made full safety/terminal prediction")
        real=partial_forecast(
            model,row["preaction_first_person"],row["command_label"]
        )
        if pred!=real:
            raise ValueError("frozen predictor changed on a heldout observation")
        after=row["postaction_external_only"]
        if sc["actual_partial_target_external_only"]!={
            "x":after["x"],"y":after["y"],
            "energy":after["body"]["energy"],
            "food":after["body"]["food"],
            "water":after["body"]["water"],
            "inventory_berry_b":after["inventory"]["berry_b"],
        }:
            raise ValueError("physical heldout consequence was falsified")
        matches={}
        if pred["estimated"] is not None:
            matches={
                k:abs(float(pred["estimated"][k])-
                      float(sc["actual_partial_target_external_only"][k]))<1e-8
                for k in DELTA_KEYS
            }
        if (sc["component_match_external_scoring_only"]!=matches
            or sc["all_six_components_match_external_only"]!=(
                all(matches.values()) if matches else None
            )):
            raise ValueError("heldout scoring hid a prediction error")
        counters[group]["worlds"]+=1
        counters[group]["physical_steps"]+=1
        counters[group]["terminal"]+=row["physically_terminal_external_only"]
        counters[group]["injury"]+=(
            sc["physical_integrity_delta_external_only"]<0
        )
        counters[group]["predicted"]+=pred["status"]=="empirical_partial_not_certified"
        counters[group]["abstain_clamp"]+=pred["status"]=="abstain_clamp"
        counters[group]["all_numeric_exact"]+=(
            sc["all_six_components_match_external_only"] is True
        )
        counters[group]["numeric_mismatch"]+=(
            sc["all_six_components_match_external_only"] is False
        )
        if group=="HIDDEN":
            intervention=row["hidden_intervention_external_only"]
            if intervention not in INTERVENTIONS:
                raise ValueError("hidden laboratory intervention missing")
            counters[intervention]["worlds"]+=1
            counters[intervention]["terminal"]+=row["physically_terminal_external_only"]
            counters[intervention]["injury"]+=sc[
                "physical_integrity_delta_external_only"]<0
            counters[intervention]["numeric_mismatch"]+=(
                sc["all_six_components_match_external_only"] is False
            )
    if (
        counters["NOMINAL"]["worlds"]!=NOMINAL_N
        or counters["NOMINAL"]["all_numeric_exact"]!=NOMINAL_N
        or counters["NOMINAL"]["terminal"]!=0
        or counters["HIDDEN"]["worlds"]!=HIDDEN_N
        or counters["HIDDEN"]["terminal"]!=EXPECTED_HAZARD_DEATHS
        or counters["HIDDEN"]["injury"]!=EXPECTED_HAZARD_INJURIES
        or counters["hidden_forced_action_failure"]["numeric_mismatch"]!=
           EXPECTED_HAZARD_FORCED_FAILURES
        or counters["BOUNDARY"]["worlds"]!=BOUNDARY_N
        or counters["BOUNDARY"]["abstain_clamp"]!=BOUNDARY_N
        or counters["BOUNDARY"]["terminal"]!=0
    ):
        raise ValueError(
            "precommitted physical results contradicted: "+
            str({k:dict(v) for k,v in counters.items()})
        )
    # Latent berry toxicity never changes non-ingestive original perception
    # or numeric consequences; it only changes an unexercised ingestion.
    twins=defaultdict(list)
    for row,sc in zip(heldout,score):
        if row["preregistered_cohort"]=="NOMINAL":
            pair=(tuple(row["position_factor_external"]),
                  tuple(row["body_factor_external"]),
                  row["phase_factor_external"],row["command_label"])
            twins[pair].append((row,sc))
    if len(twins)!=32 or any(len(rows)!=2 for rows in twins.values()):
        raise ValueError("hidden B benign/lethal paired cohort unbalanced")
    for pair,rows in twins.items():
        a,b=rows
        if ({a[0]["latent_berry_effect_external_only"],
             b[0]["latent_berry_effect_external_only"]}!=set(HIDDEN_B)
            or a[0]["preaction_first_person"]!=b[0]["preaction_first_person"]
            or a[0]["postaction_external_only"]!=b[0]["postaction_external_only"]
            or a[1]["frozen_empirical_prediction"]!=b[1]["frozen_empirical_prediction"]):
            raise ValueError("hidden B toxicity leaked into preingestion forecast")
    # The unseen physics of the hidden arms cannot be read from initial state.
    nom_lookup={}
    for row in heldout:
        if row["preregistered_cohort"]=="NOMINAL" and (
            row["latent_berry_effect_external_only"]=="benign"
            and tuple(row["body_factor_external"])==NOMINAL_BODIES[0]
            and row["phase_factor_external"]==1
        ):
            nom_lookup[tuple(row["position_factor_external"]),
                       row["command_label"]]=row["preaction_first_person"]
    for row in heldout:
        if row["preregistered_cohort"]=="HIDDEN":
            if row["preaction_first_person"]!=nom_lookup[
                tuple(row["position_factor_external"]),row["command_label"]
            ]:
                raise ValueError("hidden intervention leaked into initial observation")
    return {
        "original_physical_worlds":EXPECTED_TOTAL,
        "independent_training_worlds":TRAIN_N,
        "nominal_heldout_worlds":NOMINAL_N,
        "hidden_intervention_worlds":HIDDEN_N,
        "clamp_boundary_worlds":BOUNDARY_N,
        "physical_actions_applied":EXPECTED_TOTAL,
        "exact_fullstate_heldout_keys_known":0,
        "nominal_partial_predictions_emitted":counters[
            "NOMINAL"]["predicted"],
        "nominal_six_component_physically_exact":counters[
            "NOMINAL"]["all_numeric_exact"],
        "hazard_numeric_mismatches":counters[
            "HIDDEN"]["numeric_mismatch"],
        "hazard_hidden_motor_deaths":counters[
            "HIDDEN"]["terminal"],
        "hazard_hidden_integrity_injuries":counters[
            "HIDDEN"]["injury"],
        "hazard_forced_primitive_failures":counters[
            "hidden_forced_action_failure"]["numeric_mismatch"],
        "boundary_abstentions":counters[
            "BOUNDARY"]["abstain_clamp"],
        "nominal_hidden_berry_twins_with_identical_observations":len(twins),
        "integrity_predictions_emitted":0,
        "terminality_predictions_emitted":0,
        "next_full_adjacent_state_predictions_emitted":0,
        "safety_certificates_emitted":0,
        "new_I0_births":0,"new_I0_autonomous_steps":0,
        "I0_UC_measured":False,
        "Stage6_fullstate_equipment_promoted":False,
        "all_predictions_are_lab_empirical_not_safe":True,
        "issue110_administratively_closed_not_scientifically_certified":True,
        "Stage12_operator_ready_proven":False,
        "a230":"PARTIELLE",
        "by_cohort":{
            k:dict(v) for k,v in sorted(counters.items())
        },
    }


def experiment(folder):
    folder.mkdir(parents=True,exist_ok=False)
    train_recipes,nominal_recipes,hazard_recipes,boundary_recipes=(
        registered_recipes()
    )
    training_pairs=[apply_one(rec) for rec in train_recipes]
    training=[t for t,_ in training_pairs]
    physical_examples=tuple(t for _,t in training_pairs)
    training_corpus=EquipmentCorpus(
        version="a230zo-external-training-16-v1",
        examples=physical_examples,
    )
    exact=train_exact_transition_table(
        corpus=training_corpus,
        equipment_version="E-a230zo-external-exact-control-v1",
    )
    model=fit_partial_empirical(training)
    trained_hash=digest(model)
    # Crucial ordering: source evidence is complete, frozen, and hashed
    # BEFORE any heldout WorldBody is even constructed.
    heldout=[apply_one(rec)[0] for rec in (
        nominal_recipes+hazard_recipes+boundary_recipes
    )]
    if digest(model)!=trained_hash:
        raise AssertionError("heldout physics retrained a source-only model")
    scores=[
        compare_forecast(row,model,exact)
        for row in heldout
    ]
    outcome=review_results(training,heldout,model,scores)
    outcome.update({
        "schema":"a230zo-partial-observable-empirical-heldout-v1",
        "preregistered_before_code_sha":PREREG,
        "runner_commit_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "training_external_source_sha256":digest(training),
        "training_exact_equipment_sha256":exact.artifact_digest,
        "trained_partial_model_sha256":trained_hash,
        "all_physical_receipts_sha256":digest(training+heldout),
        "heldout_prospective_forecasts_sha256":digest(scores),
        "training_finished_before_heldout_world_creation":True,
        "no_oracle_to_i0":True,
        "no_mortal_i0_replay":True,
        "distinct_python_replays_not_new_scientific_worlds":True,
    })
    (folder/"a230zo-physical-training.json").write_text(
        json.dumps(training,sort_keys=True,indent=2)+"\n"
    )
    (folder/"a230zo-frozen-partial-model.json").write_text(
        json.dumps({
            "model":model,"model_sha256":trained_hash,
            "historical_firstperson_exact_equipment_sha256":
                exact.artifact_digest,
            "model_has_no_production_equipment_contract":True,
        },sort_keys=True,indent=2)+"\n"
    )
    (folder/"a230zo-original-heldout-worlds.json").write_text(
        json.dumps(heldout,sort_keys=True,indent=2)+"\n"
    )
    (folder/"a230zo-prospective-scores.json").write_text(
        json.dumps(scores,sort_keys=True,indent=2)+"\n"
    )
    (folder/"a230zo-summary.json").write_text(
        json.dumps(outcome,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZO_SUMMARY "+json.dumps({
        k:v for k,v in outcome.items() if k!="by_cohort"
    },sort_keys=True),flush=True)
    return outcome


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    experiment(args.output_dir)


if __name__=="__main__":
    main()
