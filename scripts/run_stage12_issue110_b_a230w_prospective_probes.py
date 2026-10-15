"""A2.30-W prospective pre-exposure information experiment.

This is PHYSICAL LABORATORY ONLY. No I0 is instantiated and no action is
selected by a Stage6 policy. Every probe is preregistered *before* building
the 80 acted worlds. Hidden berry effects are never added to observation
histories. Terminal captures are external receipts, not living experiences.

Preregitstration: docs/research/stage12-issue110-b-a230w-prospective-safe-probes-prereg-2026-10-15.fr.md
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.world import WorldBody, WorldLayout
from run_stage12_issue110_b_a230p_joint_prefix_experiment import build_physics

FOODS = (35.0, 45.0)
POSITIONS = ((5, 5), (7, 7))
HIDDEN_VARIANTS = ("benign", "toxin_7", "toxin_30", "toxin_100", "gain_zero")
PROBES = ("immediate", "wait_twice", "collect_first", "west_return")
CONTROL_VARIANTS = ("resource_berry_a", "resource_berry_b", "west_blocked")
WAIT = PrimitiveCommand("attendre")
COLLECT = PrimitiveCommand("collecter", {"target": "berry_a"})
EAT = PrimitiveCommand("manger", {"target": "berry_a"})
WEST = PrimitiveCommand("se_deplacer", {"direction": "west"})
EAST = PrimitiveCommand("se_deplacer", {"direction": "east"})
PREFLIGHT = {
    "immediate": (),
    "wait_twice": (WAIT, WAIT),
    "collect_first": (COLLECT,),
    "west_return": (WEST, EAST),
}
EXPECTED_PROBE_STEPS = {
    "immediate": 0, "wait_twice": 40, "collect_first": 20,
    "west_return": 40,
}
EXPECTED_ACTIONS = 240
EXPECTED_WORLDS = 80
EXPECTED_PASSIVE_CONTROLS = 12
EXPECTED_TERMINALS = 16
ACCESSIBLE_KEYS = frozenset({
    "schema_version", "x", "y", "body", "inventory",
    "current_resources", "current_water_source", "adjacent",
    "known_shelter_here", "is_night",
})


def digest(value):
    return sha256_hex(canonical_causal_bytes(value))


def observe(world, t_monde, perception):
    sensed = perception.capture(
        local_state=world.capture_local(t_monde=t_monde).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(
        capture=sensed, is_night=world.is_night(t_monde),
    ).as_dict()


def observation_key(visible_history):
    """Only complete first-person histories; refuses post-event/hidden input."""
    if not isinstance(visible_history, list) or not visible_history:
        raise ValueError("no accessible observation history")
    for idx,entry in enumerate(visible_history,1):
        if (not isinstance(entry,dict)
            or set(entry)!={"t_monde","state"}
            or entry["t_monde"]!=idx
            or not isinstance(entry["state"],dict)
            or set(entry["state"])!=ACCESSIBLE_KEYS):
            raise ValueError("history contains hidden/future/incomplete observation")
        body=entry["state"]["body"]
        if set(body)!={"energy","food","water","integrity"}:
            raise ValueError("observed body missing an authorized component")
    return digest(visible_history)


def receipt(phase,step,command,before,after,terminal):
    claim={
        "phase":phase,
        "t_monde":step,
        "command":command.as_dict(),
        "before":before,
        "after_for_external_bench":after,
        "terminal_external_only":terminal,
    }
    return {**claim,"sha256":digest(claim)}


def apply_one(world,perception,t,command,phase,last_live):
    before=observe(world,t,perception)
    if before!=last_live:
        raise AssertionError("non-contiguous accessible step")
    applied=world.apply(command,t_monde=t)
    after=observe(world,t+1,perception)
    return receipt(phase,t,command,before,after,applied.lethal),after,applied.lethal


def sample_world(probe,variant,food,position):
    if probe not in PROBES or variant not in HIDDEN_VARIANTS:
        raise ValueError("unpreregistered probe/hidden cause")
    config,layout=build_physics(
        "EAT",variant,food=food,position=position,
    )
    world=WorldBody(config=config,layout=layout)
    perception=SymbolicPerception()
    identity=(f"a230w:{probe}:{variant}:food{int(food)}:"
              f"x{position[0]}y{position[1]}")
    initial=observe(world,1,perception)
    history=[{"t_monde":1,"state":initial}]
    physical=[]
    last=initial
    step=0
    for cmd in PREFLIGHT[probe]:
        step+=1
        rx,last,terminal=apply_one(
            world,perception,step,cmd,"preexposure_probe",last,
        )
        physical.append(rx)
        if terminal:
            world.freeze_terminal_state()
            raise AssertionError("preregistered nondangerous probe became terminal")
        history.append({"t_monde":step+1,"state":last})
    predecision_key=observation_key(history)
    if len(history)!=len(PREFLIGHT[probe])+1:
        raise AssertionError("first-person observations lost during probe")
    decision_state=last
    freeze_digest=digest(decision_state)
    probe_deltas={
        k:round(float(decision_state["body"][k]-
                      initial["body"][k]),8)
        for k in ("energy","food","water","integrity")
    }
    probe_receipt_count=len(physical)
    # Critically, the following suffix is selected by the experiment protocol,
    # NEVER by the shadow model and NEVER by the latent cause.
    food_prefix=(EAT,) if probe=="collect_first" else (COLLECT,EAT)
    alive_after_ingestion=False
    post_ingestion_bench=None
    terminal_at=None
    lived_post_ingestion=None
    for cmd in food_prefix:
        step+=1
        rx,last,terminal=apply_one(
            world,perception,step,cmd,"external_food_outcome_only",last,
        )
        physical.append(rx)
        if cmd==EAT:
            post_ingestion_bench=last
            alive_after_ingestion=not terminal
            lived_post_ingestion=last if not terminal else None
        if terminal:
            terminal_at=step
            world.freeze_terminal_state()
            break
    if post_ingestion_bench is None or step!=len(physical):
        raise AssertionError("food outcome not recorded")
    successful=bool(
        alive_after_ingestion and
        (post_ingestion_bench["body"]["food"]-
         decision_state["body"]["food"])>=5.0
    )
    return {
        "world_id":identity,
        "probe":probe,
        "latent_external_bench_only":variant,
        "initial_food":food,
        "initial_position":list(position),
        "config_digest_external_only":config.digest(),
        "layout_digest_external_only":digest(layout.as_dict()),
        "predecision_lived_history":history,
        "predecision_history_sha256":predecision_key,
        "decision_state":decision_state,
        "decision_state_sha256":freeze_digest,
        "physical_probe_effect":probe_deltas,
        "physical_probe_steps":probe_receipt_count,
        "physical_total_steps":len(physical),
        "physical_commands_and_receipts_external_only":physical,
        "physical_terminal_step_external_only":terminal_at,
        "physically_alive_after_ingestion":alive_after_ingestion,
        "physical_food_gain_from_predecision_external_only":round(
            float(post_ingestion_bench["body"]["food"]-
                  decision_state["body"]["food"]),8
        ),
        "physical_food_goal_and_survival_external_only":successful,
        "lived_post_ingestion_if_survivor":lived_post_ingestion,
        "postterminal_lived_capture_count":0,
        "no_i0_instance_or_autonomous_command":True,
        "no_oracle_feedback_to_i0":True,
    }


def passive_control(control,food,position):
    if control not in CONTROL_VARIANTS:
        raise ValueError("unregistered visible control")
    config,base=build_physics(
        "EAT","benign",food=food,position=position,
    )
    if control=="resource_berry_b":
        changed=replace(
            base, resources=((config.initial_position,"berry_b",2),),
        )
    elif control=="west_blocked":
        changed=replace(
            base, obstacles=frozenset({config.initial_position.moved("west")}),
        )
    else:
        changed=base
    world=WorldBody(config=config,layout=changed)
    state=observe(world,1,SymbolicPerception())
    return {
        "world_id":f"a230w-control:{control}:food{int(food)}:"
                   f"x{position[0]}y{position[1]}",
        "control":control,
        "food":food,
        "position":list(position),
        "visible_state":state,
        "visible_state_sha256":digest(state),
        "config_digest_external_only":config.digest(),
        "layout_digest_external_only":digest(changed.as_dict()),
        "physical_steps":0,
        "no_food_safety_claim":True,
    }


def validate_and_score(acted,controls):
    """Finite-evidence scorer used for preregistered technical guards.

    Every latent label is BENCH-ONLY, never passed to observation_key.
    This is an empirical matched-world impossibility statement, not a
    general causal or planning theorem.
    """
    if len(acted)!=80 or len(controls)!=12:
        raise ValueError("wrong preregistered laboratory world counts")
    seen=set()
    families=Counter()
    steps_by_probe=Counter()
    classes=defaultdict(list)
    outcomes=Counter()
    costs=defaultdict(set)
    all_physical=0
    for row in acted:
        name=row["world_id"]
        if name in seen:
            raise ValueError("duplicate physical world identifier")
        seen.add(name)
        probe=row["probe"]
        latent=row["latent_external_bench_only"]
        food=row["initial_food"]
        position=tuple(row["initial_position"])
        if (probe not in PROBES or latent not in HIDDEN_VARIANTS
            or food not in FOODS or position not in POSITIONS
            or name != f"a230w:{probe}:{latent}:food{int(food)}:"
                       f"x{position[0]}y{position[1]}"):
            raise ValueError("physical world identity is not preregistered")
        histories=row["predecision_lived_history"]
        history_key=observation_key(histories)
        if (len(histories)!=len(PREFLIGHT[probe])+1
            or histories[-1]["state"]!=row["decision_state"]
            or digest(row["decision_state"])!=row["decision_state_sha256"]
            or history_key!=row["predecision_history_sha256"]
            or row["postterminal_lived_capture_count"]!=0
            or row["no_i0_instance_or_autonomous_command"] is not True
            or row["no_oracle_feedback_to_i0"] is not True):
            raise ValueError("first-person/future/hidden history leak")
        receipts=row["physical_commands_and_receipts_external_only"]
        if (len(receipts)!=row["physical_total_steps"]
            or row["physical_probe_steps"]!=len(PREFLIGHT[probe])
            or len(receipts)!=row["physical_probe_steps"]+
                (1 if probe=="collect_first" else 2)):
            raise ValueError("precommitted physical action count corrupted")
        prev=histories[0]["state"]
        for idx,receipt_row in enumerate(receipts,1):
            source={k:v for k,v in receipt_row.items() if k!="sha256"}
            if (receipt_row["t_monde"]!=idx or digest(source)!=receipt_row["sha256"]
                or source["before"]!=prev
                or source["phase"]!=(
                    "preexposure_probe" if idx<=row["physical_probe_steps"]
                    else "external_food_outcome_only"
                )):
                raise ValueError("physical receipts or state chain altered")
            expected_command=(
                PREFLIGHT[probe]+
                ((EAT,) if probe=="collect_first" else (COLLECT,EAT))
            )[idx-1]
            if source["command"]!=expected_command.as_dict():
                raise ValueError("post-hoc command replaced ex-ante prefix")
            if (source["terminal_external_only"]
                and idx!=len(receipts)):
                raise ValueError("terminal WorldBody was continued")
            if idx<=row["physical_probe_steps"]:
                if (source["terminal_external_only"]
                    or histories[idx]["state"]!=source["after_for_external_bench"]):
                    raise ValueError("probe outcome concealed/terminalized")
            prev=source["after_for_external_bench"]
        if (row["physical_terminal_step_external_only"]!=
            (len(receipts) if receipts[-1]["terminal_external_only"] else None)
            or row["physically_alive_after_ingestion"] is
            receipts[-1]["terminal_external_only"]
            or row["lived_post_ingestion_if_survivor"]!=(
                prev if row["physically_alive_after_ingestion"] else None
            )):
            raise ValueError("postmortem receipt masquerades as lived observation")
        actual_gain=round(
            float(prev["body"]["food"]-
                  row["decision_state"]["body"]["food"]),8
        )
        success=(row["physically_alive_after_ingestion"] and actual_gain>=5.0)
        if (abs(actual_gain-row["physical_food_gain_from_predecision_external_only"])
            >1e-8 or success is not
            row["physical_food_goal_and_survival_external_only"]):
            raise ValueError("physical food success or future truth falsified")
        initial=histories[0]["state"]
        measured={
            k:round(float(row["decision_state"]["body"][k]-
                          initial["body"][k]),8)
            for k in ("energy","food","water","integrity")
        }
        if measured!=row["physical_probe_effect"]:
            raise ValueError("physical acquisition cost falsified")
        costs[probe].add(tuple(measured[k] for k in (
            "energy","food","water","integrity"
        )))
        classes[(probe,history_key)].append(row)
        families[probe]+=1
        steps_by_probe[probe]+=len(receipts)
        all_physical+=len(receipts)
        if success:
            outcomes[(probe,"food_goal_and_survival")]+=1
        elif not row["physically_alive_after_ingestion"]:
            outcomes[(probe,"terminal")]+=1
        else:
            outcomes[(probe,"insufficient")]+=1

    if (set(families)!=set(PROBES) or
        any(families[p]!=20 for p in PROBES) or
        len(classes)!=16 or
        any(len(v)!=5 for v in classes.values()) or
        all_physical!=EXPECTED_ACTIONS):
        raise ValueError("wrong independent probe cells or equivalence partitions")
    for p in PROBES:
        if sum(row["physical_probe_steps"] for row in acted
               if row["probe"]==p)!=EXPECTED_PROBE_STEPS[p]:
            raise ValueError("physical probe steps differ from preregistration")
        if tuple(outcomes[(p,k)] for k in
                 ("food_goal_and_survival","terminal","insufficient")
                )!=(12,4,4):
            raise ValueError("hidden physical food outcomes changed")
    for (probe,_),siblings in classes.items():
        if {x["latent_external_bench_only"] for x in siblings}!=set(
            HIDDEN_VARIANTS
        ):
            raise ValueError("one hidden berry effect missing from equivalent history")
        if tuple(sum(
            x["physical_food_goal_and_survival_external_only"]
            for x in siblings
        ) for _ in (1,))!=(3,):
            raise ValueError("matched histories no longer contain three safe meals")
        if sum(not x["physically_alive_after_ingestion"]
               for x in siblings)!=1:
            raise ValueError("matched histories missing one terminal world")
    # Engineering positive controls: on each of the four exact food/position
    # roots, a truly perceptible change must change the first-person state.
    passive=defaultdict(dict)
    for row in controls:
        id_=row["world_id"]
        if id_ in seen:
            raise ValueError("duplicated physical control world")
        seen.add(id_)
        context=(row["food"],tuple(row["position"]))
        if (row["control"] not in CONTROL_VARIANTS
            or row["food"] not in FOODS
            or context[1] not in POSITIONS
            or row["physical_steps"]!=0
            or row["no_food_safety_claim"] is not True
            or row["visible_state_sha256"]!=digest(row["visible_state"])
            or id_ != f"a230w-control:{row['control']}:food{int(row['food'])}:"
                       f"x{context[1][0]}y{context[1][1]}"):
            raise ValueError("invalid passive control receipt")
        observation_key([{"t_monde":1,"state":row["visible_state"]}])
        if row["control"] in passive[context]:
            raise ValueError("duplicate control for same visible context")
        passive[context][row["control"]]=row
    if len(passive)!=4 or any(
        set(block)!=set(CONTROL_VARIANTS) for block in passive.values()
    ):
        raise ValueError("positive control fixture incomplete")
    for context,variants in passive.items():
        base=variants["resource_berry_a"]["visible_state"]
        berry=variants["resource_berry_b"]["visible_state"]
        blocked=variants["west_blocked"]["visible_state"]
        if (base["current_resources"]!=["berry_a"] or
            berry["current_resources"]!=["berry_b"] or
            blocked["current_resources"]!=["berry_a"] or
            base==berry or base==blocked or
            base["body"]!=berry["body"] or
            base["body"]!=blocked["body"]):
            raise ValueError("visible resource positive control not discriminable")
        def west_passable(x):
            return next(n["passable"] for n in x["adjacent"]
                        if n["direction"]=="west")
        if (west_passable(base) is not True
            or west_passable(blocked) is not False):
            raise ValueError("visible obstacle positive control not discriminable")
    EXPECTED_COSTS={
        "immediate":(0.0,0.0,0.0,0.0),
        "wait_twice":(-1.0,-1.0,-0.4,0.0),
        "collect_first":(-0.75,-0.5,-0.2,0.0),
        "west_return":(-2.0,-1.0,-0.4,0.0),
    }
    for probe in PROBES:
        if costs[probe]!={EXPECTED_COSTS[probe]}:
            raise ValueError("unexpected physical information acquisition costs")
    # 16 observable equivalence classes, each with 3 benign/effective,
    # 1 terminal, and 1 ineffective physical outcome. No hidden variant is
    # an input to a policy on the first-person histories.
    safety_frontier=Counter()
    zero_death_count=0
    positive_food_with_no_death=0
    for actions in product((False,True),repeat=len(classes)):
        commits=sum(actions)
        outcomes_if_commit={"physical_food_success":3*commits,
                            "terminal_possible":commits,
                            "insufficient":commits}
        safety_frontier[commits]+=1
        if outcomes_if_commit["terminal_possible"]==0:
            zero_death_count+=1
            if outcomes_if_commit["physical_food_success"]>0:
                positive_food_with_no_death+=1
    if (sum(safety_frontier.values())!=65536
        or zero_death_count!=1
        or positive_food_with_no_death!=0):
        raise ValueError("bounded first-person physical policy theorem changed")
    return {
        "schema":"a230w-prospective-unobservable-food-risk-v1",
        "physically_independent_acted_worlds":len(acted),
        "passive_positive_control_worlds":len(controls),
        "total_laboratory_world_instances":len(acted)+len(controls),
        "actually_applied_worldbody_steps":all_physical,
        "physical_probe_steps":sum(EXPECTED_PROBE_STEPS.values()),
        "physical_food_suffix_steps":all_physical-sum(EXPECTED_PROBE_STEPS.values()),
        "external_terminal_ingestions":sum(
            outcomes[(p,"terminal")] for p in PROBES
        ),
        "preexposure_observation_equivalence_classes":len(classes),
        "latent_worlds_per_first_person_class":5,
        "hidden_cause_pairs_same_first_person_history":len(classes)*10,
        "hidden_cause_pairs_separated_before_ingestion":0,
        "positive_visible_berry_kind_differences":4,
        "positive_visible_obstacle_differences":4,
        "bounded_deterministic_policies_enumerated":65536,
        "zero_death_policies_in_bounded_domain":zero_death_count,
        "zero_death_and_positive_food_policies":positive_food_with_no_death,
        "fully_committed_food_successes":sum(
            outcomes[(p,"food_goal_and_survival")] for p in PROBES
        ),
        "fully_committed_deaths":sum(
            outcomes[(p,"terminal")] for p in PROBES
        ),
        "fully_committed_insufficient_results":sum(
            outcomes[(p,"insufficient")] for p in PROBES
        ),
        "probe_cost_delta_per_world":{
            k:dict(zip(("energy","food","water","integrity"),
                       next(iter(costs[k]))))
            for k in PROBES
        },
        "per_probe":{p:{
            "worlds":families[p],
            "all_physical_steps":steps_by_probe[p],
            "probe_steps":EXPECTED_PROBE_STEPS[p],
            "food_goal_and_survival":outcomes[(p,"food_goal_and_survival")],
            "externally_terminal":outcomes[(p,"terminal")],
            "insufficient":outcomes[(p,"insufficient")],
            "distinguishing_hidden_food_physics_preexposure":0,
        } for p in PROBES},
        "never_used_latent_label_in_observation_class":True,
        "perception_unchanged_from_mvp":True,
        "allowed_observation_does_not_prove_safety":True,
        "simulated_bench_command_never_I0_choice":True,
        "oracle_feedback_to_i0":False,
        "new_i0_births":0,
        "new_i0_autonomous_steps":0,
        "uc_cost_evaluated":False,
        "can_deploy_predictor":False,
        "a230":"PARTIELLE","stage12":"PARTIAL","issue110":"OPEN",
    }


def experiment(directory):
    directory.mkdir(parents=True,exist_ok=False)
    acted=[
        sample_world(probe,variant,food,pos)
        for probe in PROBES
        for variant in HIDDEN_VARIANTS
        for food in FOODS
        for pos in POSITIONS
    ]
    controls=[
        passive_control(control,food,pos)
        for control in CONTROL_VARIANTS
        for food in FOODS
        for pos in POSITIONS
    ]
    results=validate_and_score(acted,controls)
    results["sha_of_analysis_code"]=subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True
    ).strip()
    results["physical_trace_corpus_sha256"]=digest(acted)
    results["visible_control_corpus_sha256"]=digest(controls)
    for name,document in (
        ("a230w-acted-physical-worlds.json",acted),
        ("a230w-passive-positive-controls.json",controls),
        ("a230w-summary.json",results),
    ):
        (directory/name).write_text(
            json.dumps(document,sort_keys=True,indent=2)+"\n"
        )
    print("A230W_SUMMARY "+json.dumps(results,sort_keys=True),flush=True)
    return results


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    experiment(args.output_dir)


if __name__=="__main__":
    main()
