"""A2.30-ZB: 12 real autonomous B-born mortal I0 lives with alternative foods.

Preregistered before code in docs/research/stage12-issue110-b-a230zb-
autonomous-alternative-prereg-2026-10-15.fr.md. No forced commands,
no Oracle or world-truth feedback, no learned B transitions before birth.
Stage12 B-born (dual scope, no GA06), durable mortal WAL, P48 audit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_first_planning_state as factory
from i0.equipment import FrozenTableEquipment
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_dual_scope_audit import audit_stage12_dual_scope
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

PROFILES=("restored","sustained")
LAYOUTS=("B_NONE","B_LOCAL","B_EAST")
VARIANTS=("benign","toxic_lethal")
STEPS=32
B_EAT=PrimitiveCommand("manger",{"target":"berry_b"})
B_COLLECT=PrimitiveCommand("collecter",{"target":"berry_b"})


def sha(obj):
    return sha256_hex(canonical_causal_bytes(obj))


def recipes():
    return tuple(
        (profile,layout,hidden)
        for profile in PROFILES for layout in LAYOUTS for hidden in VARIANTS
    )


def birth_effect(config, layout, target, hidden):
    if target not in LAYOUTS or hidden not in VARIANTS:
        raise ValueError("unregistered ZB physical birth condition")
    if any(name=="berry_b" for _,name,_ in layout.resources):
        raise AssertionError("historical world already has B resource")
    initial=config.initial_position
    east=initial.moved("east")
    if target=="B_EAST" and east in layout.obstacles:
        raise AssertionError("B east is not available for direct movement")
    effect=replace(config.berry_effects["berry_b"],food_gain=30.0,
                   integrity_delta=0.0 if hidden=="benign" else -100.0)
    new_config=replace(
        config,version=config.version+"-a230zb-"+hidden+"-v1",
        berry_effects={**config.berry_effects,"berry_b":effect},
    )
    resources=tuple(layout.resources)
    if target!="B_NONE":
        resources+=((
            initial if target=="B_LOCAL" else east,"berry_b",2
        ),)
    new_layout=replace(layout,resources=resources)
    new_config.validate()
    new_layout.validate(new_config)
    return new_config,new_layout


def external_authorized_projection(world):
    """Lab checks first-person projection without injecting it into I0."""
    cap=SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=1).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(capture=cap,is_night=world.is_night(1))


def birth(folder, profile, layout_name, hidden):
    if profile not in PROFILES or layout_name not in LAYOUTS or hidden not in VARIANTS:
        raise ValueError("ZB birth recipe unknown")
    identity=f"i0:stage12:b:a230zb:{profile}:{layout_name}:{hidden}"
    actual_class=factory.Stage12Runtime
    interventions=[]
    def configured_birth(**kw):
        if (kw.get("birth_life_id")!=identity
            or kw.get("subjective_goal_agency") is not True
            or kw.get("attribution_join") is not True):
            raise AssertionError("Stage12 factory was not a registered B birth")
        conf,layout=birth_effect(
            kw["world_config"],kw["layout"],layout_name,hidden
        )
        kw.update(world_config=conf,layout=layout,
                  attribution_join=False,dual_scope_agency=True,
                  dual_scope_cost_uc=1)
        interventions.append({
            "config_sha256_external":conf.digest(),
            "layout_sha256_external":sha(layout.as_dict()),
            "birth_only_intervention":True,
        })
        return actual_class(**kw)
    with patch.object(factory,"Stage12Runtime",side_effect=configured_birth):
        life,orig_config,orig_layout,equipment=factory.build_life(
            "near_food_free",70.0,"horizon_three",
            wal_path=str(folder/"life.wal"),birth_life_id=identity,
            calibration_food_profile=profile,planning_depth=3,
            progressive_planning=True,
            progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
            instrumental_geographic_value=False,
            extrinsic_gain_override=1.6,
        )
    if len(interventions)!=1:
        raise AssertionError("B world intervention did not occur exactly once")
    if (life.stage3.control.dual_scope is None
        or life._meta_custody.attribution_pairs is not None):
        raise AssertionError("not a born B dual-scope individual")
    if not isinstance(equipment,FrozenTableEquipment):
        raise AssertionError("changed Stage6 Equipment family")
    if any(kind=="berry_b" for _,kind,_ in orig_layout.resources):
        raise AssertionError("prebirth physical corpus contaminated with B")
    root=external_authorized_projection(life.stage3.world)
    visible=root.as_dict()
    east=[n for n in visible["adjacent"] if n["direction"]=="east"]
    if (len(east)!=1
        or ("berry_b" in visible["current_resources"])!=(layout_name=="B_LOCAL")
        or ("berry_b" in east[0]["resources"])!=(layout_name=="B_EAST")
        or (layout_name=="B_EAST" and not east[0]["passable"])):
        raise AssertionError("B initial accessible cue does not match layout")
    for command in (B_COLLECT,B_EAT):
        try:
            equipment.predict(state=root,command=command)
        except LookupError:
            pass
        else:
            raise AssertionError("preregistered B-unknown Equipment predicted B")
    Stage12OperatorConsole(
        substrate=life.stage3.substrate,mode="campaign",
        policy_version="stage12-b-a230zb-v1",maximum_world_steps=STEPS,
    )
    return life,identity,equipment.artifact_digest,interventions[0],visible


def _f64(value):
    if type(value) in (int,float):
        return float(value)
    if type(value) is dict and set(value)=={"$f64"}:
        return float.fromhex(value["$f64"])
    return None


def audit_finished(folder,life,identity,model_hash,intervention,first,steps,
                   profile,layout_name,hidden):
    raw=life.journal.canonical_bytes()
    (folder/"canonical.jsonl").write_bytes(raw)
    anchor={"expected_head":life.journal.head_hash,
            "expected_count":len(life.journal.entries)}
    wal=HashChainedJournal.audit_durable_wal(str(folder/"life.wal"))
    if (wal["head_hash"]!=anchor["expected_head"]
        or wal["verified_entries"]!=anchor["expected_count"]):
        raise ValueError("M11 durable WAL and live journal differ")
    journal_audit=audit_export_bytes(raw,**anchor)
    p48=audit_stage12_p48_diversity(raw,**anchor)
    proximal=audit_stage12_first_person_agency(raw,**anchor)
    dual=audit_stage12_dual_scope(raw,**anchor)
    goal=audit_stage12_goal_progress(raw,**anchor)
    if (journal_audit.world_steps_closed!=steps or p48["world_steps"]!=steps
        or not life.journal.verify()):
        raise ValueError("independent P48 physical closure/WAL mismatch")
    events=[json.loads(line)["causal_event"] for line in raw.splitlines()]
    commands={e["t_monde"]:e for e in events
              if e["kind"]=="command_experienced"}
    transitions={e["t_monde"]:e for e in events
                 if e["kind"]=="world_transition_experienced"}
    if len(commands)!=steps or len(transitions)!=steps:
        raise ValueError("wrong count of actually experienced motor commands")
    by_step=[]
    attempted_B=[]
    eaten_B=[]
    motives={(e["t_monde"],e["attempt_ref"]):e["data"]
             for e in events if e["kind"]=="stage12_action_motive_attested"}
    for t in range(1,steps+1):
        cmd=commands[t];obs=transitions[t]
        if cmd["attempt_ref"]!=obs["attempt_ref"]:
            raise ValueError("command and world transition cannot be joined")
        primitive=cmd["primitive"]
        parameters=cmd.get("parameters",{})
        target=parameters.get("target")
        by_step.append({"step":t,"primitive":primitive,
                        "parameters":parameters})
        if primitive in ("collecter","manger") and target=="berry_b":
            attempted_B.append({
                "step":t,"primitive":primitive,
                "motive":motives.get((t,cmd["attempt_ref"])),
            })
        if primitive=="manger" and target=="berry_b":
            if obs.get("effects",{}).get("ate")=="berry_b":
                eaten_B.append({
                    "step":t,
                    "food_after":_f64(obs.get("body_after",{}).get("food")),
                    "integrity_after":_f64(obs.get("body_after",{}).get("integrity")),
                })
            elif obs.get("effects",{}).get("ate") not in (None,"unavailable"):
                raise ValueError("B ingestion outcome malformed")
        if layout_name=="B_NONE" and obs.get("effects",{}).get("ate")=="berry_b":
            raise AssertionError("impossible eating of physically absent B")
    if len(eaten_B)>p48["physically_confirmed_eats"]:
        raise AssertionError("B counts exceed independent P48 food audit")
    status=life.stage3.substrate.mortal_status.value
    if steps<STEPS and status=="active":
        raise AssertionError("alive autonomous I0 stopped without its bound")
    # In particular never claim a capture after a physically terminal closure.
    if status=="dead" and any(
        e["kind"]=="perceptual_capture" and e.get("t_monde",0)>steps
        for e in events
    ):
        raise AssertionError("post-death lived capture fabricated")
    stage6=[
        e["data"]["progressive_search_diagnostic"]
        for e in events if e["kind"]=="stage6_planning_result"
        and e.get("data",{}).get("progressive_search_diagnostic") is not None
    ]
    for d in stage6:
        if d["root_available_edges"]+d["root_unavailable_edges"]>d["root_candidate_edges"]:
            raise ValueError("malformed root-edge counters")
    capture_food=[
        _f64(e.get("data",{}).get("dual_scope_visible_body",{}).get("food"))
        for e in events if e["kind"]=="perceptual_capture"
    ]
    uc=Counter(
        str(e.get("data",{}).get("operation"))
        for e in events if e["kind"]=="compute_charge"
        and e.get("data",{}).get("accepted") is False
    )
    resp=Counter(
        str(e.get("data",{}).get("subjective_responsibility"))
        for e in events if e["kind"]=="stage12_outcome_responsibility_judgement"
    )
    result={
        "birth_id":identity,"profile":profile,"layout":layout_name,
        "hidden_B_external_only":hidden,
        "world_steps":steps,"max_preregistered_steps":STEPS,
        "mortal_status":status,
        "journal_head":anchor["expected_head"],
        "journal_count":anchor["expected_count"],
        "journal_sha256":sha256(raw).hexdigest(),
        "independent_WAL_P48_dual_agency_audits":True,
        "equipment_sha256_A_only":model_hash,
        "world_birth_configuration_external":intervention,
        "initial_accessible_projection":first,
        "executed_motor_commands":by_step,
        "experienced_B_commands_with_motives":attempted_B,
        "confirmed_B_ingestions":eaten_B,
        "all_confirmed_ingestions_P48":p48["physically_confirmed_eats"],
        "physical_food_gain_steps_P48":p48["net_food_increase_steps_after_first"],
        "stage6_searches":len(stage6),
        "stage6_status_counts":dict(Counter(x["status"] for x in stage6)),
        "stage6_no_known_root_searches":sum(
            x["root_model_diagnostic"]=="no_predictable_first_step"
            for x in stage6),
        "stage6_available_root_edge_attempts":sum(
            x["root_available_edges"] for x in stage6),
        "stage6_plan_found_searches":sum(
            x["status"]=="plan_found" for x in stage6),
        "firstperson_food_first_last":{
            "first":next((x for x in capture_food if x is not None),None),
            "last":next((x for x in reversed(capture_food) if x is not None),None),
        },
        "proximal_self_judgements":proximal.judgements_self,
        "proximal_world_judgements":proximal.judgements_world,
        "proximal_unknown_judgements":proximal.judgements_unknown,
        "proximal_unavailable":proximal.unavailable,
        "dual_judgements":dual.judgements,
        "dual_unavailable":dual.unavailable,
        "dual_pending":dual.unresolved,
        "goal_precommits":goal.preregistered,
        "subjective_responsibility_receipts":dict(resp),
        "lived_UC_refusals":dict(uc),
        "no_forced_commands":True,
        "no_oracle_feedback":True,
        "postterminal_revival":False,
    }
    (folder/"a230zb-life.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    return result


def run_one(output,profile,layout_name,hidden):
    output.mkdir(parents=True,exist_ok=False)
    life,identity,equipment_hash,intervention,initial=birth(
        output,profile,layout_name,hidden
    )
    steps=0
    for _ in range(STEPS):
        if life.stage3.substrate.mortal_status.value!="active":
            break
        applied=life.run_step()
        if applied.execution_status!="applied":
            raise RuntimeError("I0 step not applied: "+applied.execution_status)
        steps+=1
    result=audit_finished(
        output,life,identity,equipment_hash,intervention,initial,steps,
        profile,layout_name,hidden,
    )
    print("A230ZB_LIFE "+json.dumps({
        key:val for key,val in result.items()
        if key not in (
            "executed_motor_commands","initial_accessible_projection",
            "world_birth_configuration_external",
            "experienced_B_commands_with_motives"
        )
    },sort_keys=True),flush=True)
    return result


def paired_comparison(rows):
    pairs=[]
    for profile in PROFILES:
        for layout in LAYOUTS:
            x=[r for r in rows if r["profile"]==profile and r["layout"]==layout]
            if len(x)!=2 or {r["hidden_B_external_only"] for r in x}!=set(VARIANTS):
                raise ValueError("missing B hidden-effect pairing")
            safe=next(r for r in x if r["hidden_B_external_only"]=="benign")
            lethal=next(r for r in x if r["hidden_B_external_only"]=="toxic_lethal")
            if safe["equipment_sha256_A_only"]!=lethal["equipment_sha256_A_only"]:
                raise ValueError("hidden effect contaminated prebirth Equipment")
            if safe["initial_accessible_projection"]!=lethal["initial_accessible_projection"]:
                raise ValueError("a hidden food effect changed root perception")
            a=safe["executed_motor_commands"]
            z=lethal["executed_motor_commands"]
            eaten=lambda cmds: next((i for i,c in enumerate(cmds)
                if c["primitive"]=="manger"
                and c["parameters"].get("target")=="berry_b"),len(cmds))
            ea=eaten(a); ez=eaten(z)
            n=min(ea,ez)
            clean=lambda cmds: [
                (c["primitive"],c["parameters"]) for c in cmds
            ]
            same=clean(a[:n])==clean(z[:n])
            pairs.append({
                "profile":profile,"layout":layout,
                "first_person_at_birth_equal":True,
                "pre_B_ingestion_command_parity":same,
                "pre_exposure_steps_compared":n,
                "first_B_ingestion_benign":ea+1 if ea<len(a) else None,
                "first_B_ingestion_toxic":ez+1 if ez<len(z) else None,
                "benign_mortal_status":safe["mortal_status"],
                "toxic_mortal_status":lethal["mortal_status"],
                "valid_limited_exposure_comparison":bool(
                    same and ea==ez and ea<len(a)
                ),
                "births_are_distinct_not_same_individual":True,
            })
    return pairs


def experiment(output_dir):
    output_dir.mkdir(parents=True,exist_ok=False)
    lives=[]
    for profile,layout,hidden in recipes():
        folder=output_dir/(profile+"-"+layout+"-"+hidden)
        lives.append(run_one(folder,profile,layout,hidden))
    if len(lives)!=12 or len({r["birth_id"] for r in lives})!=12:
        raise AssertionError("reused or missing independent birth")
    world_steps=sum(r["world_steps"] for r in lives)
    if world_steps>384:
        raise ValueError("exceeded bound 384 world steps")
    pair=paired_comparison(lives)
    result={
        "schema":"a230zb-autonomous-alternative-lived-v1",
        "git_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"],text=True
        ).strip(),
        "independent_new_I0_births":12,
        "preregistered_max_world_steps":384,
        "actual_autonomous_world_steps":world_steps,
        "mortal_statuses":dict(Counter(r["mortal_status"] for r in lives)),
        "B_collections_executed":sum(
            c["primitive"]=="collecter"
            for r in lives for c in r["experienced_B_commands_with_motives"]
        ),
        "B_eat_attempts_executed":sum(
            c["primitive"]=="manger"
            for r in lives for c in r["experienced_B_commands_with_motives"]
        ),
        "B_ingestions_physically_confirmed":sum(
            len(r["confirmed_B_ingestions"]) for r in lives
        ),
        "ingestions_all_species_physically_confirmed":sum(
            r["all_confirmed_ingestions_P48"] for r in lives
        ),
        "stage6_searches":sum(r["stage6_searches"] for r in lives),
        "stage6_no_predictable_first_step":sum(
            r["stage6_no_known_root_searches"] for r in lives
        ),
        "stage6_plan_found_searches":sum(
            r["stage6_plan_found_searches"] for r in lives
        ),
        "stage6_root_available_edge_attempts":sum(
            r["stage6_available_root_edge_attempts"] for r in lives
        ),
        "dual_scope_judgements":sum(r["dual_judgements"] for r in lives),
        "physically_verified_body_food_gain_steps":sum(
            r["physical_food_gain_steps_P48"] for r in lives
        ),
        "paired_hidden_worlds":len(pair),
        "initial_same_accessible_pairs":sum(
            p["first_person_at_birth_equal"] for p in pair
        ),
        "pre_B_exposure_motor_parity_pairs":sum(
            p["pre_B_ingestion_command_parity"] for p in pair
        ),
        "bounded_exposure_contrasts_valid":sum(
            p["valid_limited_exposure_comparison"] for p in pair
        ),
        "all_WALs_authenticated":True,
        "all_actions_autonomous":True,
        "no_Oracle_to_I0":True,
        "no_safe_B_prior_installed":True,
        "no_MVP_norm_changes":True,
        "operator_stage12_acceptance":False,
        "stage12":"PARTIAL","issue110":"OPEN",
        "pairs":pair,"lives":lives,
    }
    (output_dir/"a230zb-summary.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print("A230ZB_SUMMARY "+json.dumps({
        k:v for k,v in result.items() if k not in ("pairs","lives")
    },sort_keys=True),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    options=ap.parse_args()
    experiment(options.output_dir)


if __name__=="__main__":
    main()
