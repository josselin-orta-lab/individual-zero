"""A2.30-ZK: preregistered 66-world noningestive own-world motor probes.

The LAB preselects commands from visible SimulationState only. No Stage12 I0
is born, acted upon, taught or resumed. 64 independent test WorldBody worlds
+ 2 historical A-reference demonstrators, 28 applied physics steps, and 80
genuine SimulatorPlanner.search calls in READ-ONLY shadow. Four terminal
movements are external bench receipts, NEVER lived postmortem memory.

Protocol frozen BEFORE code at a7b724a4b7b70d6fe3e352ff9eba6e768850e3c6.
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
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody

from run_stage12_issue110_b_a230zg_lived_root_shadow import (
    PROFILES, B_COLLECT, EAT_B, MOVE_E, MOVE_N, COLLECT_A, EAT_A,
    first_person, digest, reference_birth_world, benign_B_fixture,
    physically_demonstrate, stage6_shadow, verify_original_birth_sources,
)

LAYOUTS=("B_NONE","B_LOCAL","B_EAST","B_EAST_BLOCKED")
HIDDEN_B=("benign","toxic_lethal")
HIDDEN_EAST=("east_clear","east_hidden_lethal")
PROTOCOLS=("ABSTAIN","VISIBLE_PROBE")
EXPECTED_LAB_WORLDS=64
EXPECTED_EXTERNAL_A_WORLDS=2
EXPECTED_A_STEPS=8
EXPECTED_TEST_STEPS=20
EXPECTED_TERMINALS=4
EXPECTED_INITIAL_PROBES=16
EXPECTED_SURVIVED_PROBES=12
EXPECTED_NO_PROBES=48
EXPECTED_SHADOWS=80
EXPECTED_LIVING_FOLLOWUPS=12
EXPECTED_SECOND_FOLLOWUPS=4
BERRY_B_EFFECTS={
    "benign":(30.0,0.0),
    "toxic_lethal":(30.0,-100.0),
}
ACCESSIBLE_KEYS={
    "schema_version","x","y","body","inventory",
    "current_resources","current_water_source","adjacent",
    "known_shelter_here","is_night",
}


def assert_visible(raw):
    if (type(raw) is not dict or set(raw)!=ACCESSIBLE_KEYS
        or set(raw["body"])!={"energy","food","water","integrity"}
        or len(raw["adjacent"])!=4):
        raise ValueError("hidden or future information in first-person choice")
    return raw


def make_trial_world(profile,layout_name,hidden_B,hidden_east):
    """World-only hidden variants; no access from perceptual decision."""
    if (profile not in PROFILES or layout_name not in LAYOUTS
        or hidden_B not in HIDDEN_B or hidden_east not in HIDDEN_EAST):
        raise ValueError("not a preregistered physical recipe")
    config,layout=reference_birth_world(profile)
    if layout_name in ("B_LOCAL","B_EAST","B_EAST_BLOCKED"):
        config,layout=benign_B_fixture(
            config,layout,
            "B_LOCAL" if layout_name=="B_LOCAL" else "B_EAST",
        )
    if layout_name=="B_EAST_BLOCKED":
        east=config.initial_position.moved("east")
        layout=replace(
            layout,obstacles=frozenset(set(layout.obstacles)|{east}),
        )
    old_B=config.berry_effects["berry_b"]
    gain,damage=BERRY_B_EFFECTS[hidden_B]
    config=replace(
        config,
        version=config.version+"-ZI-"+hidden_B+"-"+hidden_east+"-v1",
        berry_effects={
            **config.berry_effects,
            "berry_b":replace(
                old_B,food_gain=gain,integrity_delta=damage,
            ),
        },
    )
    if hidden_east=="east_hidden_lethal":
        east=config.initial_position.moved("east")
        layout=replace(
            layout,lethal_zones=frozenset(set(layout.lethal_zones)|{east}),
        )
    config.validate()
    layout.validate(config)
    return config,layout


def fixed_perceptual_probe(state,protocol,history):
    """Frozen LAB first-person rule, not I0's option policy or motor command."""
    assert_visible(state)
    if protocol not in PROTOCOLS:
        raise ValueError("not a preregistered motor-probe arm")
    if any(c not in (MOVE_E,B_COLLECT) for c in history):
        raise ValueError("alien command or future action in probe history")
    if protocol=="ABSTAIN":
        return None,"preregistered_abstain"
    east=[x for x in state["adjacent"] if x["direction"]=="east"]
    if len(east)!=1:
        raise ValueError("missing observable east direction")
    if not history:
        if "berry_b" in state["current_resources"]:
            return B_COLLECT,"firstperson_local_B"
        if "berry_b" in east[0]["resources"]:
            return (MOVE_E,"firstperson_visible_open_east_B") if (
                east[0]["passable"]
            ) else (None,"visible_obstacle_veto")
        return None,"no_visible_B"
    if history==(MOVE_E,) and "berry_b" in state["current_resources"]:
        return B_COLLECT,"postmove_locally_visible_B"
    return None,"fixed_probe_finished"


def build_A_reference_models():
    """Reconstruct the exact original A prebirth models from separate physics."""
    manifests=[]
    models={}
    examples={}
    for profile in PROFILES:
        config,layout=reference_birth_world(profile)
        row,physical=physically_demonstrate(
            name="A_REFERENCE-"+profile,
            config=config,layout=layout,
            commands=(MOVE_N,MOVE_E,COLLECT_A,EAT_A),
            corpus_version="issue110-lived-north-east-food-physical-v1",
        )
        if len(physical)!=4:
            raise AssertionError("prebirth model training steps altered")
        corpus=EquipmentCorpus(
            version="issue110-lived-north-east-food-physical-v1",
            examples=physical,
        )
        models[profile]=train_exact_transition_table(
            corpus=corpus,
            equipment_version="E-stage12-issue110-lived-state-food-physical-v1",
        )
        examples[profile]=physical
        manifests.append(row)
    if len(manifests)!=EXPECTED_EXTERNAL_A_WORLDS or sum(
        m["physical_step_count"] for m in manifests
    )!=EXPECTED_A_STEPS:
        raise AssertionError("preregistered external A training count violated")
    return manifests,models,examples


def verified_archive_roots(lives,models):
    roots={}
    for life in lives:
        profile=life["profile"]
        layout=life["layout"]
        hidden=life["hidden_B_external_only"]
        if (profile not in PROFILES
            or layout not in ("B_NONE","B_LOCAL","B_EAST")
            or hidden not in HIDDEN_B):
            raise ValueError("original I0 birth factor was changed")
        if models[profile].artifact_digest!=life["equipment_sha256_A_only"]:
            raise AssertionError("recreated A prebirth model differs from real birth")
        ident=(profile,layout,hidden)
        if ident in roots:
            raise AssertionError("same original I0 born twice")
        roots[ident]=assert_visible(life["initial_accessible_projection"])
    if len(roots)!=12:
        raise AssertionError("expected 12 original first-person roots")
    return roots


def try_exact(model,state,command):
    """Measured exact prediction presence, NOT physical safety."""
    try:
        return model.predict(state=state,command=command)
    except LookupError:
        return None


def run_case(*,profile,layout_name,hidden_B,hidden_east,protocol,
             baseline,evidence_A,roots):
    world_id=(
        f"a230zk:{profile}:{layout_name}:{hidden_B}:{hidden_east}:{protocol}"
    )
    config,layout=make_trial_world(
        profile,layout_name,hidden_B,hidden_east,
    )
    world=WorldBody(config=config,layout=layout)
    recorder=EquipmentCorpusRecorder(corpus_version=world_id)
    born=first_person(world,1).as_dict()
    assert_visible(born)
    if layout_name!="B_EAST_BLOCKED":
        expected=roots[(profile,layout_name,hidden_B)]
        if born!=expected:
            raise AssertionError("trial initial perception mismatches real I0 birth")
    history=[]
    physical=[]
    choices=[]
    shadows=[]
    hindsight=[]
    lived=[{"t_monde":1,"state":born}]
    terminal_step=None
    physical_external_terminal=None
    snapshots_before=[]
    for t in range(1,4):  # 2 allowed physics + one final alive shadow
        if terminal_step is not None:
            raise AssertionError("postmortem lab loop attempted cognition")
        state=first_person(world,t)
        if state.as_dict()!=lived[-1]["state"]:
            raise AssertionError("first-person physics discontinuous")
        if not history:
            eq=baseline
        else:
            corpus=EquipmentCorpus(
                version=f"a230zk-ownworld-{world_id}-t{t}",
                examples=tuple(evidence_A) + tuple(x["example"] for x in history),
            )
            if any(x["origin_world"]!=world_id or x["example"].terminal
                   for x in history):
                raise AssertionError("foreign or terminal event used for shadow model")
            eq=train_exact_transition_table(
                corpus=corpus,
                equipment_version=f"E-a230zk-ownworld-{world_id}-t{t}",
            )
        actor_commands=tuple(x["example"].command for x in history)
        command,reason=fixed_perceptual_probe(
            state.as_dict(),protocol,actor_commands,
        )
        if t>2 and command is not None:
            raise AssertionError("frozen lab policy exceeded two motor probes")
        choices.append({
            "t_monde":t,
            "firstperson_state":state.as_dict(),
            "firstperson_sha256":digest(state.as_dict()),
            "previous_command_receipts":[
                c.as_dict() for c in actor_commands
            ],
            "preregistered_external_lab_proposal":
                command.as_dict() if command is not None else None,
            "reason_from_accessible_input":reason,
            "external_world_hidden_effect_used_in_choice":False,
            "certifies_safe":False,
            "actual_I0_selected_or_authorized_this_command":False,
        })
        search=stage6_shadow(
            state,eq,
            tag=("A_ONLY_HISTORICAL" if not history
                 else "OWN_WORLD_NONTERMINAL_PAST"),
        )
        prospective_prediction=(
            try_exact(eq,state,command) if command is not None else None
        )
        if command is not None and prospective_prediction is not None:
            raise AssertionError(
                "precommitted novel B action was already predictable at same state"
            )
        if any(
            p["primitive"]=="manger" and
            p["parameters"].get("target")=="berry_b"
            for p in search["predicted_commands"]
        ):
            raise AssertionError("Stage6 predicted ingestion with no B ingestion example")
        shadows.append({
            "t_monde":t,"source_world_id":world_id,
            "visible_state_sha256":digest(state.as_dict()),
            "model_sha256":eq.artifact_digest,
            "own_living_prior_examples":len(history),
            "historical_A_examples":len(evidence_A),
            "lab_next_proposal":command.as_dict() if command else None,
            "lab_next_command_known_in_frozen_exact_model":
                prospective_prediction is not None if command else None,
            "planner":search,
            "no_shadow_dispatch":True,
            "no_real_I0_UC_measured":True,
        })
        if command is None:
            break
        if command not in SimulatorPlanner.candidate_commands(state):
            raise AssertionError("lab policy chose an ineligible Stage6 candidate")
        if command==B_COLLECT and "berry_b" not in state.current_resources:
            raise AssertionError("bench tried collection without visible B")
        if command==MOVE_E and not next(
            n for n in state.adjacent if n.direction=="east"
        ).passable:
            raise AssertionError("bench tried move into a visible obstacle")
        if command.primitive=="manger":
            raise AssertionError("B ingestion categorically forbidden")
        snapshots_before.append(state)
        example=recorder.record_transition(
            world=world,t_monde=t,
            family="a230zk-externally-preregistered-noningestive-probe",
            command=command,
        )
        if example.state!=state:
            raise AssertionError("physical preaction capture was not the first person state")
        record={
            "t_monde":t,
            "world_id":world_id,
            "command":command.as_dict(),
            "preaction_observable":state.as_dict(),
            "physical_example":example.as_dict(),
            "physical_example_sha256":digest(example.as_dict()),
            "terminal_external_only":example.terminal,
            "postaction_external_only":example.observed_next_state.as_dict(),
            "not_autonomous_I0_or_shadow_dispatched":True,
        }
        physical.append(record)
        if example.terminal:
            terminal_step=t
            physical_external_terminal=record["postaction_external_only"]
            world.freeze_terminal_state()
            break
        # At t+1 the experience becomes available ONLY after lived survival.
        history.append({
            "origin_world":world_id,"t":t,"example":example,
        })
        fresh=first_person(world,t+1).as_dict()
        if fresh!=example.observed_next_state.as_dict():
            raise AssertionError("own-world experience contradicts physical next perception")
        lived.append({"t_monde":t+1,"state":fresh})
        # A known PAST edge cannot be mistaken for an available NEXT edge.
        witness=try_exact(eq,state,command)
        if witness is not None:
            raise AssertionError("known past edge appeared BEFORE actual action")
        next_model=trained_from_examples(
            profile,world_id,history,evidence_A,
        )
        known_hindsight=try_exact(next_model,state,command)
        if (known_hindsight is None or
            known_hindsight.next_state!=example.observed_next_state):
            raise AssertionError("physically lived nonterminal transition not learned")
        hindsight.append({
            "physical_step":t,
            "past_state_command_now_exactly_known":True,
            "past_input_hash":FrozenTableEquipment.input_digest(state,command),
            "new_current_state_hash":digest(fresh),
            "past_state_hash":digest(state.as_dict()),
            "current_state_is_different":state.as_dict()!=fresh,
            "not_issued_as_current_firstperson_prediction":True,
        })
    if len(history)!=sum(not row["terminal_external_only"] for row in physical):
        raise AssertionError("nonterminal memory includes missing/terminal transitions")
    if terminal_step is not None:
        if (terminal_step!=len(physical) or
            lived[-1]["t_monde"]>terminal_step or
            physical[-1]["terminal_external_only"] is not True):
            raise AssertionError("postmortem experience or physical continuation fabricated")
    if len(shadows)!=len(choices) or len(physical)!=sum(
        c["preregistered_external_lab_proposal"] is not None for c in choices
    ):
        raise AssertionError("shadow searches and lab motor receipts disagree")
    if any(
        x["planner"]["no_shadow_action_dispatched"] is not True
        for x in shadows
    ):
        raise AssertionError("shadow acted on a real world")
    return {
        "world_id":world_id,
        "profile":profile,
        "layout_external_only":layout_name,
        "hidden_B_external_only":hidden_B,
        "hidden_lethal_zone_external_only":hidden_east,
        "protocol_frozen_before_physics":protocol,
        "physics_config_sha256_external":config.digest(),
        "layout_sha256_external":digest(layout.as_dict()),
        "firstperson_birth_state":born,
        "firstperson_birth_sha256":digest(born),
        "firstperson_history_while_alive":lived,
        "lab_perceptual_choices":choices,
        "real_physical_lab_receipts":physical,
        "real_physical_steps":len(physical),
        "first_action_physically_executed":len(physical)>0,
        "physically_terminal_step_external_only":terminal_step,
        "external_postterminal_state_not_lived":physical_external_terminal,
        "postterminal_firstperson_capture":None,
        "own_world_prior_examples_for_final_living_state":len(history),
        "past_edges_known_only_retrospectively":hindsight,
        "original_prebirth_A_equipment_sha256":baseline.artifact_digest,
        "stage6_shadow_queries":shadows,
        "no_berry_B_ingestion":True,
        "berry_B_safety_certified":False,
        "i0_autonomous_steps":0,
        "i0_births":0,
        "lived_i0_UC_cost":None,
        "oracle_feedback_to_cognitive_policy":False,
        "no_foreign_world_examples_as_own_memory":True,
    }


def trained_from_examples(profile,world_id,history,evidence_A):
    if (profile not in PROFILES or not history
        or any(x["origin_world"]!=world_id or x["example"].terminal
               for x in history)):
        raise ValueError("non-firstperson or terminal shadow memory")
    corpus=EquipmentCorpus(
        version=f"a230zk-ownworld-{world_id}-n{len(history)}",
        examples=tuple(evidence_A)+tuple(x["example"] for x in history),
    )
    return train_exact_transition_table(
        corpus=corpus,
        equipment_version=f"E-a230zk-ownworld-{world_id}-n{len(history)}",
    )


def recipes():
    for profile,layout_name,hidden_B,hidden_east,protocol in product(
        PROFILES,LAYOUTS,HIDDEN_B,HIDDEN_EAST,PROTOCOLS,
    ):
        yield {
            "profile":profile,"layout_name":layout_name,
            "hidden_B":hidden_B,"hidden_east":hidden_east,
            "protocol":protocol,
        }


def score_worlds(worlds,manifest,original_roots):
    """Post hoc, strictly external scorer; not available to decisions."""
    if len(worlds)!=EXPECTED_LAB_WORLDS or len({
        w["world_id"] for w in worlds
    })!=EXPECTED_LAB_WORLDS:
        raise ValueError("precommitted world factorial population incomplete")
    if (manifest["detached_A_reference_worlds"]!=2 or
        manifest["real_physical_A_reference_steps"]!=EXPECTED_A_STEPS
        or manifest["models_originate_from_reference_A_worlds"] is not True):
        raise ValueError("prebirth A reference provenance altered")
    grouped=defaultdict(list)
    twin_groups=defaultdict(list)
    totals=Counter()
    by_layout=defaultdict(Counter)
    root_snapshots=0
    post_living=0
    third_living=0
    for row in worlds:
        layout=row["layout_external_only"]
        protocol=row["protocol_frozen_before_physics"]
        profile=row["profile"]
        hidden_B=row["hidden_B_external_only"]
        hidden_east=row["hidden_lethal_zone_external_only"]
        if (layout not in LAYOUTS or protocol not in PROTOCOLS
            or profile not in PROFILES or hidden_B not in HIDDEN_B
            or hidden_east not in HIDDEN_EAST):
            raise ValueError("unknown physical world, hidden cause or protocol")
        key=(profile,layout,hidden_B,hidden_east,protocol)
        if key in grouped:
            raise ValueError("duplicated factorial cell")
        grouped[key].append(row)
        if (row["postterminal_firstperson_capture"] is not None
            or row["no_berry_B_ingestion"] is not True
            or row["berry_B_safety_certified"] is not False
            or row["lived_i0_UC_cost"] is not None
            or row["i0_autonomous_steps"]!=0 or row["i0_births"]!=0
            or row["oracle_feedback_to_cognitive_policy"] is not False
            or row["no_foreign_world_examples_as_own_memory"] is not True):
            raise ValueError("injected first-person, Oracle, safety or UC claim")
        root=assert_visible(row["firstperson_birth_state"])
        if row["firstperson_birth_sha256"]!=digest(root):
            raise ValueError("initial first-person hash tampered")
        if layout!="B_EAST_BLOCKED":
            if root!=original_roots[(profile,layout,hidden_B)]:
                raise ValueError("not exactly the original I0 birth root")
            root_snapshots+=1
        receipts=row["real_physical_lab_receipts"]
        shadows=row["stage6_shadow_queries"]
        choices=row["lab_perceptual_choices"]
        lived=row["firstperson_history_while_alive"]
        if (len(receipts)!=row["real_physical_steps"]
            or len(choices)!=len(shadows)
            or len(shadows)!=len(lived)
            or not shadows or
            row["first_action_physically_executed"]!=(len(receipts)>0)
            or row["own_world_prior_examples_for_final_living_state"]!=sum(
                not receipt["terminal_external_only"] for receipt in receipts
            )):
            raise ValueError("inconsistent physical/shadow/living timeline")
        for i,choice in enumerate(choices):
            if (choice["t_monde"]!=i+1
                or choice["firstperson_state"]!=lived[i]["state"]
                or choice["firstperson_sha256"]!=digest(choice["firstperson_state"])
                or choice["external_world_hidden_effect_used_in_choice"] is not False
                or choice["certifies_safe"] is not False
                or choice["actual_I0_selected_or_authorized_this_command"] is not False):
                raise ValueError("future or hidden state was used for probe choice")
            history_cmds=tuple(PrimitiveCommand(
                primitive=x["primitive"],parameters=x["parameters"]
            ) for x in choice["previous_command_receipts"])
            cmd,reason=fixed_perceptual_probe(
                choice["firstperson_state"],protocol,history_cmds,
            )
            if (choice["preregistered_external_lab_proposal"]!=(
                cmd.as_dict() if cmd else None)
                or choice["reason_from_accessible_input"]!=reason):
                raise ValueError("frozen first-person probe replaced by hidden choice")
            shadow=shadows[i]
            if (shadow["visible_state_sha256"]!=choice["firstperson_sha256"]
                or shadow["t_monde"]!=i+1
                or shadow["source_world_id"]!=row["world_id"]
                or shadow["own_living_prior_examples"]!=i
                or shadow["historical_A_examples"]!=4
                or shadow["lab_next_proposal"]!=choice["preregistered_external_lab_proposal"]
                or shadow["lab_next_command_known_in_frozen_exact_model"] not in (False,None)
                or shadow["no_shadow_dispatch"] is not True
                or shadow["no_real_I0_UC_measured"] is not True
                or shadow["planner"]["berry_b_safety_certified"] is not False
                or shadow["planner"]["no_shadow_action_dispatched"] is not True
                or shadow["planner"]["actual_i0_uc_measured"] is not False):
                raise ValueError("shadow leaked future, motor dispatch or lived I0 UC")
            totals["stage6_shadows"]+=1
        for i,record in enumerate(receipts):
            source=record["physical_example"]
            if (record["t_monde"]!=i+1 or record["world_id"]!=row["world_id"]
                or record["physical_example_sha256"]!=digest(source)
                or record["command"]!=source["command"]
                or record["preaction_observable"]!=source["state"]
                or record["postaction_external_only"]!=source["observed_next_state"]
                or record["terminal_external_only"]!=source["terminal"]
                or record["not_autonomous_I0_or_shadow_dispatched"] is not True
                or choices[i]["preregistered_external_lab_proposal"]!=record["command"]):
                raise ValueError("physical action receipt / history mutated")
            if i and source["state"]!=receipts[i-1]["postaction_external_only"]:
                raise ValueError("inconsistent first-person sequential causal closure")
            if source["terminal"] and i!=len(receipts)-1:
                raise ValueError("physical step occurred after death")
            if source["command"]["primitive"]=="manger":
                raise ValueError("undocumented physical B ingestion")
        t=row["physically_terminal_step_external_only"]
        if t is None:
            if (any(r["terminal_external_only"] for r in receipts)
                or row["external_postterminal_state_not_lived"] is not None):
                raise ValueError("spurious external death or terminal history")
        else:
            if (t!=len(receipts) or not receipts[-1]["terminal_external_only"]
                or row["external_postterminal_state_not_lived"]!=
                   receipts[-1]["postaction_external_only"]
                or len(lived)!=t):
                raise ValueError("terminal event treated as lived future")
        if t is not None and any(
            x["t_monde"]>t for x in shadows
        ):
            raise ValueError("postmortem cognitive search fabricated")
        if len(row["past_edges_known_only_retrospectively"])!=sum(
            not record["terminal_external_only"] for record in receipts
        ):
            raise ValueError("past-key training contradicts lived physical examples")
        for h in row["past_edges_known_only_retrospectively"]:
            if (h["past_state_command_now_exactly_known"] is not True
                or h["not_issued_as_current_firstperson_prediction"] is not True
                or h["current_state_is_different"] is not True):
                raise ValueError("hindsight was passed off as current prediction")
        totals["test_actions"]+=len(receipts)
        totals["terminal_worlds"]+=t is not None
        totals["initial_probes"]+=len(receipts)>0
        totals["never_probed"]+=len(receipts)==0
        totals["surviving_probes"]+=len(receipts)>0 and t is None
        totals["postfirst_shadows"]+=len(shadows)>=2
        totals["postsecond_shadows"]+=len(shadows)>=3
        key_lp=(layout,protocol)
        by_layout[key_lp]["worlds"]+=1
        by_layout[key_lp]["actions"]+=len(receipts)
        by_layout[key_lp]["terminals"]+=t is not None
        twin_groups[(profile,layout,hidden_B,protocol)].append(row)
        if len(receipts)>0:
            first=receipts[0]
            if (layout=="B_LOCAL" and first["command"]!=B_COLLECT.as_dict()
                or layout=="B_EAST" and first["command"]!=MOVE_E.as_dict()):
                raise ValueError("first noningestive probe contradicts visible resource")
        if t is not None and (layout!="B_EAST"
                or hidden_east!="east_hidden_lethal"
                or protocol!="VISIBLE_PROBE"
                or t!=1):
            raise ValueError("physical motor death occurred in nonpreregistered arm")
        if protocol=="ABSTAIN" and len(receipts)!=0:
            raise ValueError("abstention was not respected")
        if layout in ("B_NONE","B_EAST_BLOCKED") and len(receipts)!=0:
            raise ValueError("world without visible passable B was physically probed")
        if layout=="B_LOCAL" and protocol=="VISIBLE_PROBE" and len(receipts)!=1:
            raise ValueError("local B probe did not collect exactly once")
        if layout=="B_EAST" and protocol=="VISIBLE_PROBE":
            if len(receipts)!=(1 if hidden_east=="east_hidden_lethal" else 2):
                raise ValueError("east movement/death and collection not as preregistered")
    if len(grouped)!=64 or len(twin_groups)!=32:
        raise ValueError("missing preregistered experimental recipe")
    fatal_twin_pairs=0
    for key,pair in twin_groups.items():
        if {x["hidden_lethal_zone_external_only"] for x in pair}!=set(HIDDEN_EAST):
            raise ValueError("hidden hazard pairing incomplete")
        if (pair[0]["firstperson_birth_state"]!=pair[1]["firstperson_birth_state"]
            or pair[0]["lab_perceptual_choices"][0]["preregistered_external_lab_proposal"]!=
                pair[1]["lab_perceptual_choices"][0]["preregistered_external_lab_proposal"]):
            raise ValueError("hidden lethal zone leaked into first-person decision")
        profile,layout,hidden_B,protocol=key
        if layout=="B_EAST" and protocol=="VISIBLE_PROBE":
            safe=next(r for r in pair if r["hidden_lethal_zone_external_only"]=="east_clear")
            fatal=next(r for r in pair if r["hidden_lethal_zone_external_only"]=="east_hidden_lethal")
            if (safe["real_physical_lab_receipts"][0]["preaction_observable"]!=
                fatal["real_physical_lab_receipts"][0]["preaction_observable"]
                or safe["real_physical_lab_receipts"][0]["command"]!=
                   fatal["real_physical_lab_receipts"][0]["command"]
                or safe["real_physical_lab_receipts"][0]["terminal_external_only"]
                or not fatal["real_physical_lab_receipts"][0]["terminal_external_only"]
                or safe["real_physical_lab_receipts"][0]["postaction_external_only"]==
                   fatal["real_physical_lab_receipts"][0]["postaction_external_only"]):
                raise ValueError("hidden motor lethality not witnessed on identical input")
            fatal_twin_pairs+=1
    if fatal_twin_pairs!=4:
        raise ValueError("four exact-observation hidden movement controls missing")
    totals_dict=dict(totals)
    if (
        totals["test_actions"]!=EXPECTED_TEST_STEPS or
        totals["terminal_worlds"]!=EXPECTED_TERMINALS or
        totals["initial_probes"]!=EXPECTED_INITIAL_PROBES or
        totals["never_probed"]!=EXPECTED_NO_PROBES or
        totals["surviving_probes"]!=EXPECTED_SURVIVED_PROBES or
        totals["stage6_shadows"]!=EXPECTED_SHADOWS or
        totals["postfirst_shadows"]!=EXPECTED_LIVING_FOLLOWUPS or
        totals["postsecond_shadows"]!=EXPECTED_SECOND_FOLLOWUPS or
        root_snapshots!=48
    ):
        raise ValueError(
            "preregistered physical or shadow numbers failed: "+str(totals_dict)
        )
    return {
        "schema":"a230zk-ownworld-motor-bootstrap-physical-v1",
        "independent_test_worlds":64,
        "independent_A_prebirth_reference_worlds":2,
        "independent_total_worlds":66,
        "original_I0_births_read_only":12,
        "original_I0_autonomous_steps_not_replayed":384,
        "firstperson_initial_root_matches_historical_I0":root_snapshots,
        "actual_A_reference_physical_steps":8,
        "real_test_physical_steps":totals["test_actions"],
        "total_new_physical_steps":8+totals["test_actions"],
        "physical_terminal_worlds":totals["terminal_worlds"],
        "worlds_with_initial_motor_probe":totals["initial_probes"],
        "worlds_without_motor_probe":totals["never_probed"],
        "worlds_surviving_motor_probe":totals["surviving_probes"],
        "real_Stage6_shadow_searches":totals["stage6_shadows"],
        "postfirst_living_stage6_searches":totals["postfirst_shadows"],
        "postsecond_living_stage6_searches":totals["postsecond_shadows"],
        "paired_observationally_identical_hidden_motor_deaths":fatal_twin_pairs,
        "berry_B_ingestions":0,
        "new_I0_births":0,"new_I0_autonomous_steps":0,
        "I0_UC_measured":False,
        "all_lab_commands_preregistered_from_perception_only":True,
        "all_terminal_outcomes_external_only":True,
        "all_own_world_examples_nonterminal_and_physically_observed":True,
        "models_predict_no_berry_B_food_safety":True,
        "cognitive_deployment":"NO-GO",
        "Stage12":"PARTIAL","issue110":"OPEN","a230":"PARTIELLE",
        "by_layout_policy":{
            f"{lay}/{policy}":dict(by_layout[(lay,policy)])
            for lay,policy in product(LAYOUTS,PROTOCOLS)
        },
    }


def one_sided_lethal_control(worlds):
    """Train on benign move ONLY, predict lethal counterpart offline."""
    lookup={(w["profile"],w["layout_external_only"],w["hidden_B_external_only"],
             w["hidden_lethal_zone_external_only"],
             w["protocol_frozen_before_physics"]):w
            for w in worlds}
    result=[]
    for profile,hidden in product(PROFILES,HIDDEN_B):
        safe=lookup[(profile,"B_EAST",hidden,"east_clear","VISIBLE_PROBE")]
        fatal=lookup[(profile,"B_EAST",hidden,"east_hidden_lethal","VISIBLE_PROBE")]
        left=safe["real_physical_lab_receipts"][0]["physical_example"]
        right=fatal["real_physical_lab_receipts"][0]["physical_example"]
        from run_stage12_issue110_b_a230ze_model_coverage import decode_state
        from i0.equipment import EquipmentCorpusExample
        ex=EquipmentCorpusExample(
            family="a230zk-one-sided-unrepresentative-safe-move",
            state=decode_state(left["state"]),
            command=MOVE_E,
            observed_next_state=decode_state(left["observed_next_state"]),
            terminal=False,
        )
        model=train_exact_transition_table(
            corpus=EquipmentCorpus(
                version=f"a230zk-single-safe-{profile}-{hidden}",
                examples=(ex,),
            ),
            equipment_version=f"E-a230zk-unrepresentative-{profile}-{hidden}",
        )
        hazardous=decode_state(right["state"])
        observed=model.predict(state=hazardous,command=MOVE_E)
        if (left["state"]!=right["state"]
            or left["command"]!=right["command"]
            or left["terminal"] is not False
            or right["terminal"] is not True
            or observed.terminal is not False
            or observed.next_state.as_dict()!=left["observed_next_state"]
            or observed.next_state.as_dict()==right["observed_next_state"]
            or observed.confidence!=1.0):
            raise AssertionError("hidden lethal motor context was detectable in model")
        result.append({
            "source_safe_world":safe["world_id"],
            "heldout_hidden_lethal_world":fatal["world_id"],
            "same_firstperson_input_and_primitive":True,
            "model_trained_on_one_safe_physical_move_only":True,
            "nominal_exact_table_confidence":observed.confidence,
            "predicted_terminal":observed.terminal,
            "physically_terminal_external":right["terminal"],
            "safety_calibration_inferred":False,
            "not_a_live_I0_prediction_or_command":True,
        })
    if len(result)!=4:
        raise AssertionError("four precommitted lethal shadow controls missing")
    return result


def experiment(folder,original311,original312):
    folder.mkdir(parents=True,exist_ok=False)
    original=verify_original_birth_sources(original311,original312)
    manifests,models,examples=build_A_reference_models()
    roots=verified_archive_roots(original,models)
    worlds=[
        run_case(**recipe,baseline=models[recipe["profile"]],
                 evidence_A=examples[recipe["profile"]],roots=roots)
        for recipe in recipes()
    ]
    summary=score_worlds(worlds,{
        "detached_A_reference_worlds":len(manifests),
        "real_physical_A_reference_steps":sum(x["physical_step_count"] for x in manifests),
        "models_originate_from_reference_A_worlds":True,
    },roots)
    controls=one_sided_lethal_control(worlds)
    summary.update({
        "exact_one_sided_lethal_prediction_mismatches":len(controls),
        "learning_old_input_does_not_evidence_next_state_action":True,
        "historical_birth_source_run":38767643472,
        "historical_original_sha":"2a19742df22f27752635203304097134a3009c45",
        "physical_A_reference_model_digest":{
            p:models[p].artifact_digest for p in PROFILES
        },
        "manifest_physical_source_sha256":digest(manifests),
        "all_worlds_sha256":digest(worlds),
        "original_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True,
        ).strip(),
        "cross_python_same_deterministic_recipes_not_statistical_replication":True,
    })
    source={
        "schema":"a230zk-physical-reference-models-v1",
        "A_reference_worlds":manifests,
        "A_model_digest_by_profile":{
            p:models[p].artifact_digest for p in PROFILES
        },
        "exact_mortal_counterfactual_controls":controls,
        "original_births_are_archived_untouched":12,
        "all_own_history_examples_are_from_the_same_test_world":True,
        "never_trained_on_B_ingestion":True,
    }
    (folder/"a230zk-A-physical-source.json").write_text(
        json.dumps(source,sort_keys=True,indent=2)+"\n",
    )
    (folder/"a230zk-ownworld-tests.json").write_text(
        json.dumps(worlds,sort_keys=True,indent=2)+"\n",
    )
    (folder/"a230zk-summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n",
    )
    print("A230ZK_SUMMARY "+json.dumps({
        k:v for k,v in summary.items()
        if k not in ("by_layout_policy","physical_A_reference_model_digest")
    },sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-zb-311",type=Path,required=True)
    ap.add_argument("--original-zb-312",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    experiment(args.output_dir,args.original_zb_311,args.original_zb_312)


if __name__=="__main__":
    main()
