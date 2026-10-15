"""A2.30-ZQ: prospectively preregistered genuine autonomous fatal-motor contrast.

Twenty-four NEW Stage12Runtime-born independent mortal I0 lives, up to 32
world steps each, 12 motor_clear versus hidden-lethal-zone paired contexts.
NO forced primitive, NO transferred examples, NO speculative B safety, and
NO postmortem cognition. Hidden zone coordinates are LAB-ONLY intervention
inputs at birth; no runtime or Stage6/9/12 algorithm is modified.

Protocol sealed BEFORE CODE/PHYSICS at cbd95fc2f0d6a5d66b682b7c97db6782605dbf1b.
Original 12 historical ZB births are read-only hashed comparators, NOT 12
additional ZQ births.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_b_a230zb_autonomous_food as zb
import run_stage12_issue110_first_planning_state as factory
from run_stage12_issue110_b_a230zg_lived_root_shadow import (
    verify_original_birth_sources,
)
from i0.equipment import FrozenTableEquipment
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.world import Position, command_digest

PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST")
B_HIDDEN=("benign","toxic_lethal")
MOTOR=("motor_clear","motor_hidden_lethal")
MAX_WORLD_STEPS=32
CANDIDATE_FATAL_POSITION=Position(3,1)
EXPECTED_LIVES=24
EXPECTED_PAIRS=12
PROSPECTIVE_MAX_WORLD_STEPS=24*32
ROOT_KEYS=frozenset({
    "schema_version","x","y","body","inventory","current_resources",
    "current_water_source","adjacent","known_shelter_here","is_night",
})


def digest(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def recipes():
    return tuple(product(PROFILES,LAYOUTS,B_HIDDEN,MOTOR))


def original_roots(original_311,original_312):
    origins=verify_original_birth_sources(original_311,original_312)
    originals={}
    for row in origins:
        key=(row["profile"],row["layout"],row["hidden_B_external_only"])
        if key in originals:
            raise AssertionError("historical B-born identity reused")
        original=row["initial_accessible_projection"]
        if not isinstance(original,dict) or set(original)!=ROOT_KEYS:
            raise ValueError("original I0 first-person initial state not admissible")
        originals[key]={
            "root":original,
            "equipment_A_digest":row["equipment_sha256_A_only"],
            "historical_birth_id":row["birth_id"],
        }
    if len(originals)!=EXPECTED_PAIRS:
        raise AssertionError("original ZB birth cohort incomplete")
    return originals


def birth(output,profile,layout_name,hidden_B,motor,original):
    """Patch ONLY the pre-birth configuration constructor, never an action."""
    if (profile not in PROFILES or layout_name not in LAYOUTS
        or hidden_B not in B_HIDDEN or motor not in MOTOR):
        raise ValueError("unregistered autonomous mortal birth")
    identity=(
        f"i0:stage12:b:a230zq:{profile}:{layout_name}:{hidden_B}:{motor}"
    )
    if identity==original["historical_birth_id"]:
        raise AssertionError("original lived I0 identity was restored")
    real_stage12=factory.Stage12Runtime
    configured=[]
    def at_birth(**args):
        if (args.get("birth_life_id")!=identity
            or args.get("subjective_goal_agency") is not True
            or args.get("attribution_join") is not True):
            raise AssertionError("incorrect autonomous Stage12 B-owned birth")
        config,layout=zb.birth_effect(
            args["world_config"],args["layout"],layout_name,hidden_B
        )
        if layout.lethal_zones:
            raise AssertionError("baseline world already has lethal zone")
        if motor=="motor_hidden_lethal":
            layout=replace(
                layout,
                lethal_zones=frozenset({CANDIDATE_FATAL_POSITION}),
            )
        config.validate()
        layout.validate(config)
        args.update(
            world_config=config,layout=layout,
            attribution_join=False,dual_scope_agency=True,
            dual_scope_cost_uc=1,
        )
        configured.append({
            "physical_config_sha256_external_only":config.digest(),
            "layout_sha256_external_only":digest(layout.as_dict()),
            "motor_hazard_external_only":motor,
            "lethal_zone_external_only":[CANDIDATE_FATAL_POSITION.as_dict()]
                if motor=="motor_hidden_lethal" else [],
            "at_birth_only":True,
            "no_motor_dispatch_by_lab":True,
        })
        return real_stage12(**args)

    with patch.object(factory,"Stage12Runtime",side_effect=at_birth):
        life,old_config,old_layout,equipment=factory.build_life(
            "near_food_free",70.0,"horizon_three",
            wal_path=str(output/"life.wal"),
            birth_life_id=identity,
            calibration_food_profile=profile,
            planning_depth=3,
            progressive_planning=True,
            progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
            instrumental_geographic_value=False,
            extrinsic_gain_override=1.6,
        )
    if len(configured)!=1:
        raise AssertionError("not exactly one physical birth intervention")
    if (not isinstance(equipment,FrozenTableEquipment)
        or equipment.artifact_digest!=original["equipment_A_digest"]
        or any(kind=="berry_b" for _,kind,_ in old_layout.resources)
        or life.stage3.control.dual_scope is None
        or life._meta_custody.attribution_pairs is not None):
        raise AssertionError("original A-only cognitive and dual-scope birth changed")
    initial=zb.external_authorized_projection(life.stage3.world).as_dict()
    if set(initial)!=ROOT_KEYS:
        raise ValueError("hidden zone or future Oracle leaked into birth perception")
    if initial!=original["root"]:
        raise ValueError("hidden motor treatment changed first-person initial root")
    if initial["x"]!=2 or initial["y"]!=2:
        raise AssertionError("unexpected birth coordinates")
    east=[n for n in initial["adjacent"] if n["direction"]=="east"]
    if (len(east)!=1 or
        ("berry_b" in initial["current_resources"])!=(layout_name=="B_LOCAL")
        or ("berry_b" in east[0]["resources"])!=(layout_name=="B_EAST")):
        raise ValueError("hidden treatment contaminated B visibility")
    for command in (
        PrimitiveCommand("collecter",{"target":"berry_b"}),
        PrimitiveCommand("manger",{"target":"berry_b"}),
    ):
        try:
            equipment.predict(
                state=zb.external_authorized_projection(life.stage3.world),
                command=command,
            )
        except LookupError:
            pass
        else:
            raise AssertionError("A-only prebirth Equipment already knew B")
    Stage12OperatorConsole(
        substrate=life.stage3.substrate,mode="campaign",
        policy_version="stage12-b-a230zq-hidden-motor-v1",
        maximum_world_steps=MAX_WORLD_STEPS,
    )
    return life,identity,equipment.artifact_digest,configured[0],initial


def _visible_capture_from_event(ev):
    """ONLY fields actually published to I0; never hidden physical labels."""
    data=ev["data"]
    body=data.get("dual_scope_visible_body",{})
    adjacent=data.get("agency_visible_adjacent",[])
    return {
        "t_monde":ev["t_monde"],
        "position":data.get("position"),
        "visible_adjacent":adjacent,
        "visible_body":body,
        "visible_inventory":data.get("agency_visible_inventory"),
    }


def verify_life_and_extract(out,life,identity,model_hash,intervention,initial,
                            steps,profile,layout_name,hidden_B,motor):
    # ZB's independent WAL, full causal-chain, P48, Stage12 dual-scope,
    # subjective-proximal and retrospective goal audits are reused UNCHANGED.
    base=zb.audit_finished(
        out,life,identity,model_hash,intervention,initial,
        steps,profile,layout_name,hidden_B,
    )
    raw=(out/"canonical.jsonl").read_bytes()
    events=[json.loads(line)["causal_event"] for line in raw.splitlines()]
    by_kind=Counter(x["kind"] for x in events)
    death=[x for x in events if x["kind"]=="individual_death_confirmed"]
    status=base["mortal_status"]
    if (status=="dead")!=(len(death)==1):
        raise ValueError("mortal terminal status and durable death receipt differ")
    if len(death)>1:
        raise ValueError("terminal death event duplicated")
    physical_commands={
        e["t_monde"]:e for e in events if e["kind"]=="command_experienced"
    }
    transition_by_step={
        e["t_monde"]:e for e in events if e["kind"]=="world_transition_experienced"
    }
    if (len(physical_commands)!=steps or len(transition_by_step)!=steps
        or sorted(physical_commands)!=list(range(1,steps+1))
        or sorted(transition_by_step)!=list(range(1,steps+1))):
        raise ValueError("physical commands, real transitions, and clock inconsistent")
    captures={
        (e["t_monde"],e["attempt_ref"]):e
        for e in events if e["kind"]=="perceptual_capture"
    }
    motives={
        (e["t_monde"],e["attempt_ref"]):e
        for e in events if e["kind"]=="stage12_action_motive_attested"
    }
    command_story=[]
    prior_position={"x":initial["x"],"y":initial["y"]}
    hidden_zone_entry_step=None
    hidden_zone_selected_command=None
    uc=Counter()
    accepted_uc=0
    denied_uc=0
    for ev in events:
        if ev["kind"]=="compute_charge":
            data=ev["data"]
            key=(str(data["module"]),str(data["operation"]),
                 "accepted" if data.get("accepted") else "denied")
            uc[key]+=1
            amount=data.get("requested_uc",0)
            if type(amount) is not int or amount<0:
                raise ValueError("invalid real UC charge receipt")
            if data.get("accepted") is True:
                accepted_uc+=amount
            elif data.get("accepted") is False:
                denied_uc+=amount
            else:
                raise ValueError("UC acceptance unspecified")
    for t in range(1,steps+1):
        act=physical_commands[t]
        consequence=transition_by_step[t]
        if act["attempt_ref"]!=consequence["attempt_ref"]:
            raise ValueError("experienced physical command cannot join result")
        key=(t,act["attempt_ref"])
        capture=captures.get(key)
        # Some authentic physical decisions (e.g. consecutive sleep actions)
        # have NO first-person perception event. This is epistemic absence:
        # NEVER fabricate a capture from WorldBody or future consequences.
        visible=(_visible_capture_from_event(capture)
                 if capture is not None else None)
        if visible is not None:
            if visible["position"]!=prior_position:
                raise ValueError("lived position and previous physical result differ")
            if len(visible["visible_adjacent"])!=4 or any(
                "lethal" in str(x) or "hidden" in str(x) or "oracle" in str(x)
                for x in visible["visible_adjacent"]
            ):
                raise ValueError("hidden physical cause leaked into sensation")
        c=PrimitiveCommand(act["primitive"],act.get("parameters",{}))
        if command_digest(c)!=act["command_hash"]:
            raise ValueError("physical command digest falsified")
        after=consequence["position_after"]
        if not isinstance(after,dict) or set(after)!={"x","y"}:
            raise ValueError("physical outcome position malformed")
        motor_entry=bool(
            prior_position=={"x":2,"y":1}
            and c.primitive=="se_deplacer"
            and c.parameters.get("direction")=="east"
            and after==CANDIDATE_FATAL_POSITION.as_dict()
        )
        if motor_entry:
            if hidden_zone_entry_step is not None:
                raise AssertionError("hazard candidate entered twice in one life")
            hidden_zone_entry_step=t
            hidden_zone_selected_command=c.as_dict()
        motive=motives.get(key)
        command_story.append({
            "t_monde":t,
            "attempt_ref":act["attempt_ref"],
            "primitive":act["primitive"],
            "parameters":act.get("parameters",{}),
            "command_sha256":act["command_hash"],
            "preaction_firstperson_capture":visible,
            "preaction_firstperson_sha256":(
                digest(visible) if visible is not None else None
            ),
            "preaction_firstperson_receipt_status":(
                "available" if visible is not None else
                "unavailable_in_canonical_journal"
            ),
            "preaction_position_from_physical_chain_external_only":
                prior_position,
            "motive_external_journal_receipt":(
                motive["data"] if motive is not None else None
            ),
            "verified_physical_position_after":after,
            "body_after_physical_receipt":consequence["body_after"],
            "effects_external_receipt":consequence.get("effects",{}),
            "motor_entry_into_zq_test_cell_external_only":motor_entry,
            "lab_chose_or_dispatched_this_primitive":False,
            "postdeath_subjective_comparison_generated":False,
        })
        prior_position=after
    if death:
        d=death[0]
        if d["t_monde"]!=steps:
            raise ValueError("terminal death was not at the final physical step")
        if any(e.get("t_monde",0)>steps for e in events):
            raise ValueError("postmortem cognitive or physics journal event")
        if any(e["kind"]=="perceptual_capture"
               and e["t_monde"]>steps for e in events):
            raise ValueError("postmortem first-person capture fabricated")
    if (motor=="motor_hidden_lethal"
        and hidden_zone_entry_step is not None
        and status!="dead"):
        raise AssertionError("hidden lethal cell entered but terminality lost")
    if (motor=="motor_clear" and hidden_zone_entry_step is not None
        and status=="dead" and death[0]["t_monde"]==hidden_zone_entry_step):
        raise AssertionError("clear motor control died from hidden motor treatment")
    if sum(e["t_monde"]==steps for e in death)>1:
        raise AssertionError("duplicated final physical death")
    source_external={
        "motor_hazard_mode_external_only":motor,
        "zq_lethal_zone_hidden_external_only":
            intervention["lethal_zone_external_only"],
        "first_entrance_to_test_cell_external_only":hidden_zone_entry_step,
        "first_selected_test_motor_command":hidden_zone_selected_command,
        "death_external_receipt":death[0] if death else None,
    }
    counts=Counter(x["primitive"] for x in command_story)
    east_moves=sum(
        x["primitive"]=="se_deplacer" and
        x["parameters"].get("direction")=="east"
        for x in command_story
    )
    collections_B=sum(
        x["primitive"]=="collecter" and
        x["parameters"].get("target")=="berry_b"
        for x in command_story
    )
    eats_B=sum(
        x["primitive"]=="manger" and
        x["parameters"].get("target")=="berry_b"
        for x in command_story
    )
    if collections_B!=sum(x["primitive"]=="collecter"
       for x in base["experienced_B_commands_with_motives"]):
        raise AssertionError("B experience and command audit disagree")
    if eats_B!=sum(x["primitive"]=="manger"
       for x in base["experienced_B_commands_with_motives"]):
        raise AssertionError("B ingestion and command audit disagree")
    doc={
        **base,
        "zq_schema":"a230zq-genuine-autonomous-motor-hazard-life-v1",
        "ZQ_motor_treatment_external_only":motor,
        "independent_new_ZQ_I0_birth":True,
        "identity_never_reuses_original_ZB":True,
        "birth_initial_firstperson_sha256":digest(initial),
        "initial_accessible_projection":initial,
        "motor_commands_from_original_I0_only":True,
        "physically_east_movements":east_moves,
        "physical_steps_without_same_attempt_firstperson_capture":sum(
            x["preaction_firstperson_capture"] is None
            for x in command_story
        ),
        "physically_collected_B":collections_B,
        "physically_eaten_B_commands":eats_B,
        "first_hidden_test_cell_entry_step":hidden_zone_entry_step,
        "externally_attested_terminal_mortality":status=="dead",
        "motor_zone_death_observed":bool(
            motor=="motor_hidden_lethal" and
            hidden_zone_entry_step is not None and status=="dead"
            and death[0]["t_monde"]==hidden_zone_entry_step
        ),
        "preaction_commands_with_firstperson_receipts":command_story,
        "operator_hidden_physics_external_only":source_external,
        "actual_accepted_UC_requests_total":accepted_uc,
        "actual_denied_UC_requests_total":denied_uc,
        "real_UC_receipt_counts":{
            "/".join(k):v for k,v in sorted(uc.items())
        },
        "terminal_only_in_external_causal_journal":True,
        "not_promoting_proximal_self_to_distal_death_cause":True,
        "berry_B_safety_certified":False,
        "no_world_truth_or_oracle_data_to_I0":True,
        "no_i0_cognition_modified":True,
        "directly_witnessed_last_position":prior_position,
        "journal_causal_event_kinds":dict(by_kind),
    }
    (out/"a230zq-life.json").write_text(
        json.dumps(doc,sort_keys=True,indent=2)+"\n"
    )
    return doc


def run_one(folder,profile,layout,hidden_B,motor,original):
    folder.mkdir(parents=True,exist_ok=False)
    life,identity,model_hash,intervention,root=birth(
        folder,profile,layout,hidden_B,motor,original
    )
    count=0
    observed_execution_statuses=Counter()
    for _ in range(MAX_WORLD_STEPS):
        if life.stage3.substrate.mortal_status.value!="active":
            break
        outcome=life.run_step()
        observed_execution_statuses[outcome.execution_status]+=1
        if outcome.execution_status=="safety_block":
            if life.stage3.substrate.mortal_status.value!="experiment_stopped":
                raise RuntimeError("unresolved safety block not safely stopped")
            break
        if outcome.execution_status not in ("applied","dead"):
            raise RuntimeError(
                "I0 step was not physically applied: "+outcome.execution_status
            )
        count+=1
        if outcome.execution_status=="dead":
            if life.stage3.substrate.mortal_status.value!="dead":
                raise AssertionError("mortal deadline status differs from execution")
            break
    result=verify_life_and_extract(
        folder,life,identity,model_hash,intervention,root,count,
        profile,layout,hidden_B,motor,
    )
    result["actual_execution_statuses"]=dict(observed_execution_statuses)
    (folder/"a230zq-life.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZQ_LIFE "+json.dumps({
        "birth_id":identity,"profile":profile,"layout":layout,
        "B_effect_external":hidden_B,"motor_effect_external":motor,
        "physical_steps":count,"status":result["mortal_status"],
        "first_zone_entry":result["first_hidden_test_cell_entry_step"],
        "motor_zone_death":result["motor_zone_death_observed"],
        "accepted_UC_requests":result["actual_accepted_UC_requests_total"],
        "denied_UC_requests":result["actual_denied_UC_requests_total"],
        "collect_B":result["physically_collected_B"],
        "eaten_B":result["physically_eaten_B_commands"],
    },sort_keys=True),flush=True)
    return result


def verify_pairs(lives):
    by_key={(x["profile"],x["layout"],x["hidden_B_external_only"],
             x["ZQ_motor_treatment_external_only"]):x for x in lives}
    if len(by_key)!=EXPECTED_LIVES:
        raise ValueError("births do not exhaust factorial contrast")
    pairs=[]
    for profile,layout,hidden in product(PROFILES,LAYOUTS,B_HIDDEN):
        control=by_key[(profile,layout,hidden,"motor_clear")]
        intervention=by_key[(profile,layout,hidden,"motor_hidden_lethal")]
        initial_equal=(
            control["initial_accessible_projection"]==
            intervention["initial_accessible_projection"]
            and control["equipment_sha256_A_only"]==
            intervention["equipment_sha256_A_only"]
        )
        if not initial_equal:
            raise ValueError("hidden motor treatment changed first-person birth")
        control_actions=control["preaction_commands_with_firstperson_receipts"]
        fatal_actions=intervention["preaction_commands_with_firstperson_receipts"]
        exposure=intervention["first_hidden_test_cell_entry_step"]
        common=min(len(control_actions),len(fatal_actions))
        if exposure is not None:
            common=min(common,exposure)
        parity_actions=all(
            (a["primitive"],a["parameters"])==
            (b["primitive"],b["parameters"])
            for a,b in zip(control_actions[:common],fatal_actions[:common])
        )
        parity_perceptions=all(
            a["preaction_firstperson_capture"] is not None
            and b["preaction_firstperson_capture"] is not None
            and a["preaction_firstperson_capture"]==
                b["preaction_firstperson_capture"]
            for a,b in zip(control_actions[:common],fatal_actions[:common])
        )
        matched=bool(
            exposure is not None and exposure<=len(control_actions)
            and exposure<=len(fatal_actions)
            and parity_actions and parity_perceptions
            and all(
                c["motor_entry_into_zq_test_cell_external_only"]==
                d["motor_entry_into_zq_test_cell_external_only"]
                for c,d in zip(control_actions[:common],fatal_actions[:common])
            )
        )
        true_death_contrast=bool(
            matched and intervention["motor_zone_death_observed"]
            and control["mortal_status"]!="dead"
            if len(control_actions)==exposure else
            matched and intervention["motor_zone_death_observed"] and
            (control["mortal_status"]!="dead" or
             control["world_steps"]>exposure)
        )
        # Prefer explicit checkpoint at the same physical step, not final status.
        if exposure is not None and matched:
            # The control transition at that same t has a survivor's next step
            # or, if exactly last experimental step, an external death receipt.
            # Verify nonterminal under identical action/source perception.
            ctrl_at_exposure=control_actions[exposure-1]
            control_survives_that_move=bool(
                control["mortal_status"]!="dead" or
                control["world_steps"]>exposure
            )
            true_death_contrast=bool(
                intervention["motor_zone_death_observed"]
                and control_survives_that_move
                and ctrl_at_exposure["verified_physical_position_after"]==
                    CANDIDATE_FATAL_POSITION.as_dict()
            )
        pairs.append({
            "profile":profile,"layout":layout,"hidden_B_external":hidden,
            "clear_birth_id":control["birth_id"],
            "hidden_lethal_birth_id":intervention["birth_id"],
            "initial_full_sensory_and_model_parity":initial_equal,
            "compared_preexposure_physical_steps":common,
            "commands_parity_until_exposure":parity_actions,
            "first_person_capture_parity_until_exposure":parity_perceptions,
            "treated_zone_entry_step":exposure,
            "paired_physically_same_first_motor_exposure":matched,
            "motor_death_at_intervention":intervention["motor_zone_death_observed"],
            "physical_survival_contrast_established":true_death_contrast,
            "clear_end_status":control["mortal_status"],
            "hidden_end_status":intervention["mortal_status"],
            "distinct_births_not_personally_restored_counterfactual":True,
            "not_subjectively_attributing_exogenous_death_to_self":True,
        })
    if len(pairs)!=EXPECTED_PAIRS:
        raise AssertionError("not twelve experiment-controlled birth pairs")
    return pairs


def score_study(lives,pairs):
    if len(lives)!=EXPECTED_LIVES:
        raise ValueError("not all independently preregistered births included")
    identities=[x["birth_id"] for x in lives]
    if len(set(identities))!=EXPECTED_LIVES:
        raise ValueError("duplicate mortal I0 identity")
    total=sum(x["world_steps"] for x in lives)
    if not 0<=total<=PROSPECTIVE_MAX_WORLD_STEPS:
        raise ValueError("preregistered total physical world step budget violated")
    if any(
        x["world_steps"]>MAX_WORLD_STEPS
        or x["independent_new_ZQ_I0_birth"] is not True
        or x["mortal_status"] not in ("dead","experiment_stopped")
        or x["no_forced_commands"] is not True
        or x["no_oracle_feedback"] is not True
        or x["no_world_truth_or_oracle_data_to_I0"] is not True
        or x["berry_B_safety_certified"] is not False
        or x["not_promoting_proximal_self_to_distal_death_cause"] is not True
        or x["terminal_only_in_external_causal_journal"] is not True
        or x["motor_commands_from_original_I0_only"] is not True
        or x["independent_WAL_P48_dual_agency_audits"] is not True
        or x["postterminal_revival"] is not False
        for x in lives
    ):
        raise ValueError("invalid autonomous mortal custody or scientific claim")
    if len(pairs)!=EXPECTED_PAIRS:
        raise ValueError("incomplete risk pairing")
    death_count=sum(x["mortal_status"]=="dead" for x in lives)
    zone_death_count=sum(x["motor_zone_death_observed"] for x in lives)
    if zone_death_count>death_count:
        raise ValueError("zone deaths exceed physical terminal births")
    if any(x["motor_zone_death_observed"] and
           x["ZQ_motor_treatment_external_only"]!="motor_hidden_lethal"
           for x in lives):
        raise ValueError("invented motor-zone mortality in clear control")
    return {
        "schema":"a230zq-autonomous-hidden-motor-risk-v1",
        "new_independently_born_I0":len(lives),
        "original_ZB_I0_births_used_as_readonly_initial_refs":12,
        "maximum_preregistered_autonomous_world_steps":PROSPECTIVE_MAX_WORLD_STEPS,
        "real_autonomous_world_steps":total,
        "autonomous_firstperson_motor_east_commands":sum(
            x["physically_east_movements"] for x in lives
        ),
        "autonomous_collections_berry_b":sum(
            x["physically_collected_B"] for x in lives
        ),
        "autonomous_B_eat_commands":sum(
            x["physically_eaten_B_commands"] for x in lives
        ),
        "physically_confirmed_B_ingestions":sum(
            len(x["confirmed_B_ingestions"]) for x in lives
        ),
        "terminal_individuals":death_count,
        "hidden_lethal_motor_zone_terminal_births":zone_death_count,
        "paired_mortal_exposure_comparisons":sum(
            x["paired_physically_same_first_motor_exposure"] for x in pairs
        ),
        "paired_survival_death_contrasts":sum(
            x["physical_survival_contrast_established"] for x in pairs
        ),
        "motor_hazard_HZQ1":(
            "SUPPORTED_BOUNDED" if any(
                x["physical_survival_contrast_established"] for x in pairs
            ) else "NO_CONTROLLED_MOTOR_EXPOSURE"
        ),
        "real_stage6_planner_queries":sum(
            x["stage6_searches"] for x in lives
        ),
        "actual_accepted_UC_requests_total":sum(
            x["actual_accepted_UC_requests_total"] for x in lives
        ),
        "actual_denied_UC_requests_total":sum(
            x["actual_denied_UC_requests_total"] for x in lives
        ),
        "firstperson_proximal_self_judgements":sum(
            x["proximal_self_judgements"] for x in lives
        ),
        "firstperson_proximal_unknown_judgements":sum(
            x["proximal_unknown_judgements"] for x in lives
        ),
        "dual_scope_judgements":sum(
            x["dual_judgements"] for x in lives
        ),
        "mortal_WAL_P48_dual_agency_audited":True,
        "B_food_safety_proven":False,
        "hidden_motor_safety_proven":False,
        "subjective_attribution_of_cause_of_death_proven":False,
        "new_model_transitions_or_I0_cognitive_changes":False,
        "oracle_to_I0_causality_feedback":False,
        "normative_MVP_changed":False,
        "issue110_administrative_status":"CLOSED",
        "scientific_Stage12_status":"PARTIAL",
        "A230_status":"PARTIELLE",
        "per_birth":[{
            "birth_id":x["birth_id"],"profile":x["profile"],
            "layout":x["layout"],"latent_B_external":x["hidden_B_external_only"],
            "motor_condition_external":x["ZQ_motor_treatment_external_only"],
            "steps":x["world_steps"],"end_status":x["mortal_status"],
            "motor_zone_death":x["motor_zone_death_observed"],
            "first_motor_zone_entry":x["first_hidden_test_cell_entry_step"],
            "uc_accepted":x["actual_accepted_UC_requests_total"],
            "uc_denied":x["actual_denied_UC_requests_total"],
        } for x in lives],
    }


def experiment(output,original_311,original_312):
    output.mkdir(parents=True,exist_ok=False)
    roots=original_roots(original_311,original_312)
    lives=[]
    for profile,layout,hidden_B,motor in recipes():
        folder=output/(
            f"{profile}-{layout}-{hidden_B}-{motor}"
        )
        lives.append(run_one(
            folder,profile,layout,hidden_B,motor,
            roots[(profile,layout,hidden_B)]
        ))
    pairs=verify_pairs(lives)
    summary=score_study(lives,pairs)
    summary.update({
        "original_birth_run_read_only":38767643472,
        "preregistered_protocol_commit":"cbd95fc2f0d6a5d66b682b7c97db6782605dbf1b",
        "experiment_code_head":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "original_24_new_births_digest":digest(lives),
        "paired_outcomes_digest":digest(pairs),
        "python_reruns_not_new_statistical_births":True,
    })
    (output/"a230zq-summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n"
    )
    (output/"a230zq-pairing.json").write_text(
        json.dumps(pairs,sort_keys=True,indent=2)+"\n"
    )
    print("A230ZQ_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="per_birth"
    },sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-zb-311",type=Path,required=True)
    ap.add_argument("--original-zb-312",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    v=ap.parse_args()
    experiment(v.output_dir,v.original_zb_311,v.original_zb_312)


if __name__=="__main__":
    main()
