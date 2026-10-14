"""A2.25: preregistered autonomous food, action and agency evidence.

Every command is selected by the living I0. The laboratory only fixes
external world scenarios before birth and audits completed causal journals.
"""
import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_first_planning_state as factory
from lab.injected_scenario import ScenarioEvent
from lab.journal import HashChainedJournal
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_operator_console import Stage12OperatorConsole

PROFILES=("restored","sustained","episodic","marginal")
STEPS=48

def make_life(path,profile,blocked,pulse,cohort):
    name=f"{profile}-{'a2' if blocked else 'free'}-{'pulse' if pulse else 'control'}"
    ident=f"i0:a225:{cohort}:{name}"
    original=factory.Stage12Runtime
    def born(**kwargs):
        if pulse:
            events=tuple(kwargs.get("scenario_events",()))
            assert all(not (e.t_monde==4 and e.sequence==1) for e in events)
            extra=ScenarioEvent(t_monde=4,sequence=1,
                operation="set_body",payload={"food":80.0},phase="before_step")
            kwargs["scenario_events"]=events+(extra,)
            kwargs["scenario_id"]="a225-external-physical-before-step"
            kwargs["scenario_version"]="a225-frozen-pulse80-v1"
        return original(**kwargs)
    with patch.object(factory,"Stage12Runtime",side_effect=born):
        life,config,layout,equipment=factory.build_life(
            "near_food_free",70.0,"horizon_three",
            wal_path=str(path/"life.wal"),birth_life_id=ident,
            a2_external_obstacle=blocked,
            a2_obstacle_clear_step=4 if blocked else None,
            calibration_food_profile=profile,progressive_planning=True,
            progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
            instrumental_geographic_value=False,extrinsic_gain_override=1.6)
    Stage12OperatorConsole(substrate=life.stage3.substrate,mode="campaign",
        policy_version="stage12-a225-preregistered-v1",maximum_world_steps=STEPS)
    return life,config,equipment

def run_one(path,profile,blocked,pulse,cohort):
    path.mkdir()
    life,config,equipment=make_life(path,profile,blocked,pulse,cohort)
    witness=[]
    error=None
    for t in range(1,STEPS+1):
        if life.stage3.substrate.mortal_status.value!="active":
            break
        world=life.stage3.world
        before={"position":world.position.as_dict(),
                "body":world.body.as_dict(),"inventory":dict(world.inventory())}
        try:
            step=life.run_step()
            after={"position":world.position.as_dict(),
                   "body":world.body.as_dict(),"inventory":dict(world.inventory())}
            witness.append({"step":t,"execution_status":step.execution_status,
                "primitive":step.command_primitive,"before":before,"after":after})
            if step.execution_status!="applied":
                error="nonapplied:"+step.execution_status
                break
        except Exception as exc:
            error=type(exc).__name__+":"+str(exc)
            break
    raw=life.journal.canonical_bytes()
    (path/"canonical.jsonl").write_bytes(raw)
    (path/"physical-witness.json").write_text(json.dumps(witness,sort_keys=True,indent=2)+"\n")
    anchor=dict(expected_head=life.journal.head_hash,expected_count=len(life.journal.entries))
    audited={}
    try:
        wal=HashChainedJournal.audit_durable_wal(str(path/"life.wal"))
        assert wal["head_hash"]==anchor["expected_head"]
        assert wal["verified_entries"]==anchor["expected_count"]
        base=audit_export_bytes(raw,**anchor)
        # A2.25b: preserve the original independent fail-closed auditors.
        # Their rejection is NOT counted as a verified positive goal result.
        goal=agency=pairs=None
        audit_rejection=None
        try:
            goal=audit_stage12_goal_progress(raw,**anchor)
            agency=audit_stage12_first_person_agency(raw,**anchor)
            pairs=audit_stage12_attribution_pairs(raw,**anchor)
        except ValueError as exc:
            if str(exc)!="goal followup diverges from committed lived state":
                raise
            audit_rejection=str(exc)
        assert base.world_steps_closed==len(witness)
        events=[json.loads(x)["causal_event"] for x in raw.splitlines()]
        physics={e["t_monde"]:e for e in events if e.get("kind")=="world_transition_experienced"}
        assert len(physics)==len(witness)
        pulses=[e for e in events if e.get("kind")=="external_input_applied"
                and e.get("operation")=="set_body"]
        # Applied scenario receipts may omit operation, so cross-link to the
        # preceding external_input_received by step and sequence instead.
        arrivals=[e for e in events if e.get("kind")=="external_input_received"
                  and e.get("operation")=="set_body"
                  and isinstance(e.get("payload",{}).get("food"),dict)
                  and e["payload"]["food"].get("$f64")==float(80).hex()]
        # A received pulse must have an applied receipt with identical causal
        # scenario coordinates and must precede this step's sensory capture.
        applied=[(i,e) for i,e in enumerate(events) if e.get("kind")=="external_input_applied"]
        for received in arrivals:
            coords=tuple(received.get(k) for k in ("scenario_id","scenario_version","t_monde","sequence"))
            match=[i for i,e in applied if tuple(e.get(k) for k in ("scenario_id","scenario_version","t_monde","sequence"))==coords]
            assert len(match)==1,("pulse has no unique applied receipt",coords)
            perception=[i for i,e in enumerate(events) if e.get("kind")=="perceptual_capture" and e.get("t_monde")==received["t_monde"]]
            assert perception and match[0]<min(perception),("pulse not before perception",coords)
        if audit_rejection:
            assert pulse and len(arrivals)==1, "unauthorized goal audit rejection"
            t=arrivals[0]["t_monde"]
            intents=[(i,e) for i,e in enumerate(events) if e.get("kind")=="stage12_goal_progress_preregistered" and e.get("data",{}).get("measure")=="food" and e.get("data",{}).get("observe_world_step")==t]
            follow=[e for e in events if e.get("kind")=="stage12_goal_progress_followup" and e.get("t_monde")==t and e.get("data",{}).get("measure")=="food" and e.get("data",{}).get("criterion_outcome")=="success"]
            assert len(intents)==len(follow)==1 and intents[0][1]["t_monde"]==t-1, "unexpected rejected goal topology"
            from lab.stage12_goal_progress_audit import _number
            assert _number(follow[0]["data"]["value_after"])==80.0
            assert _number(physics[t-1]["body_after"]["food"])!=80.0
            assert physics[t-1].get("effects",{}).get("ate") not in ("berry_a","berry_b")
            assert physics[t].get("effects",{}).get("ate") not in ("berry_a","berry_b")
            assert not any(e.get("kind")=="stage12_attribution_pair_admitted" and e.get("t_monde")==t for e in events)
        admitted=[e for e in events if e.get("kind")=="stage12_attribution_pair_admitted"]
        self_world=[e for e in events if e.get("kind")=="stage12_goal_agency_judgement"]
        confirmed=[]
        for item in witness:
            t=item["step"]
            effect=physics[t].get("effects",{})
            assert item["primitive"]==physics[t].get("command",{}).get("primitive",item["primitive"]) or item["primitive"]==next(
                (e.get("primitive") for e in events if e.get("kind")=="command_experienced" and e.get("t_monde")==t),item["primitive"])
            ate=effect.get("ate")
            collected=effect.get("collected")
            ate_proven=ate in ("berry_a","berry_b")
            collected_proven=isinstance(collected,dict) and collected.get("quantity",0)>0
            exogenous=any(e.get("t_monde")==t for e in arrivals)
            food_before=item["before"]["body"]["food"]
            food_after=item["after"]["body"]["food"]
            food_up=food_after>food_before
            category=("mixed_ate_and_pulse" if exogenous and ate_proven
                       else "ate_without_pulse" if ate_proven
                       else "pulse_without_ate" if exogenous
                       else "other")
            # No observationally unsupported assignment of external food gain
            # to an intention or to an inventory-only collection.
            confirmed.append({"step":t,"primitive":item["primitive"],"ate":ate,
                "collected":collected,"food_before":food_before,
                "food_after":food_after,"food_net_gain":food_up,
                "pulse_received":exogenous,"episode_category":category,
                "proximal_collect":collected_proven})
        assert len(arrivals)==(int(pulse) if len(witness)>=4 else 0),len(arrivals)
        assert not pulses or len(pulses)==len(arrivals)
        successful=sum(x["food_net_gain"] for x in confirmed)
        categorized=Counter(x["episode_category"] for x in confirmed if x["food_net_gain"])
        audited={
            "world_steps":base.world_steps_closed,
            "goal_progress_audit_status":("fail_closed_exogenous_confounded" if audit_rejection else "verified"),
            "goal_audit_rejection":audit_rejection,
            "goal_preregistered":goal.preregistered if goal else None,
            "goal_success":goal.verified_strict_gains if goal else None,
            "goal_failure":goal.verified_no_gains if goal else None,
            "goal_unavailable":goal.unavailable if goal else None,
            "agency_self":agency.judgements_self if agency else None,
            "agency_world":agency.judgements_world if agency else None,
            "agency_unknown":agency.judgements_unknown if agency else None,
            "pairs_admitted":pairs.admitted_pairs if pairs else None,
            "pairs_applied":pairs.applied_pairs if pairs else None,
            "pairs_success":pairs.applied_successes if pairs else None,
            "pairs_failure":pairs.applied_failures if pairs else None,
            "bias_evaluable":(any(label is not None for _,label in pairs.diagnostic_labels) if pairs else False),
            "actual_eats":sum(x["ate"] in ("berry_a","berry_b") for x in confirmed),
            "real_collections":sum(x["proximal_collect"] for x in confirmed),
            "food_gains":successful,"pulse_events":len(arrivals),
            "food_gains_by_category":dict(categorized),
            "journal_head":anchor["expected_head"],
            "journal_count":anchor["expected_count"],
        }
        (path/"effects-external-audit.json").write_text(json.dumps(confirmed,sort_keys=True,indent=2)+"\n")
    except Exception as exc:
        error=(error+"; " if error else "")+"AUDIT:"+type(exc).__name__+":"+str(exc)
    row={"profile":profile,"blocked":blocked,"pulse":pulse,
         "physical_steps":len(witness),"failure":error,
         "equipment_sha256":equipment.artifact_digest,
         "world_config_sha256":config.digest(),**audited}
    (path/"result.json").write_text(json.dumps(row,sort_keys=True,indent=2)+"\n")
    print("A225_LIFE "+json.dumps(row,sort_keys=True),flush=True)
    return row

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--cohort-id",default="autonomous-a225-v1")
    args=p.parse_args()
    if not args.cohort_id or len(args.cohort_id)>40 or not all(
            x.isascii() and (x.isalnum() or x in "-._") for x in args.cohort_id):
        p.error("invalid cohort")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    rows=[]
    for profile in PROFILES:
        for blocked in (False,True):
            for pulse in (False,True):
                label=f"{profile}-{'a2' if blocked else 'free'}-{'pulse' if pulse else 'control'}"
                rows.append(run_one(args.output_dir/label,profile,blocked,pulse,args.cohort_id))
    summary={"schema":"stage12-a225-autonomous-lived-outcomes-v1",
        "head_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "lives":rows,"life_count":len(rows),
        "physical_steps":sum(r["physical_steps"] for r in rows),
        "errors":sum(bool(r["failure"]) for r in rows),
        "pulse_events":sum(r.get("pulse_events",0) for r in rows),
        "goal_successes":sum(r.get("goal_success") or 0 for r in rows),
        "goal_failures":sum(r.get("goal_failure") or 0 for r in rows),
        "agency_unknown":sum(r.get("agency_unknown") or 0 for r in rows),
        "actual_eats":sum(r.get("actual_eats",0) for r in rows),
        "pairs_applied":sum(r.get("pairs_applied") or 0 for r in rows),
        "evaluable_lives":sum(bool(r.get("bias_evaluable")) for r in rows),
        "exogenous_confounded_audits":sum(r.get("goal_progress_audit_status")=="fail_closed_exogenous_confounded" for r in rows),
        "original_goal_verification_criterion_passed":False,
        "stage12":"PARTIAL","operator_reception":False,"norm_changed":False}
    (args.output_dir/"a225-summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("A225_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="lives"},sort_keys=True),flush=True)
    assert len(rows)==16
    return 0 if summary["errors"]==0 and summary["physical_steps"]==16*STEPS and summary["pulse_events"]==8 else 2

if __name__=="__main__":raise SystemExit(main())
