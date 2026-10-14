"""A2.7 preregistered 16-life real physical A/B: never synthetic outcomes."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from run_stage12_issue110_first_planning_state import build_life
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.journal import HashChainedJournal
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_a2_causal_audit import audit_stage12_a2_causal_link
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

PROFILES=("restored","sustained")
MAX_STEPS=42


def run_one(root, cohort, profile, obstacle, instrumental, revalidate):
    name=("_".join((profile,"a2" if obstacle else "free",
                    "instrumental" if instrumental else "control",
                    "revalidate" if revalidate else "baseline")))
    folder=root/name
    folder.mkdir()
    life,config,layout,equipment=build_life(
        "near_food_free",70.0,"horizon_three",
        birth_life_id=f"i0:110:a27:{cohort}:{name}",
        wal_path=str(folder/"life.wal"),
        a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=4 if obstacle else None,
        calibration_food_profile=profile,
        progressive_planning=True,progressive_evaluation_prefix=True,
        instrumental_geographic_value=instrumental,
        progressive_revalidate_on_new_capture=revalidate)
    Stage12OperatorConsole(substrate=life.stage3.substrate,
        mode="campaign",policy_version="stage12-issue110-a27-prereg-v1",
        maximum_world_steps=MAX_STEPS)
    commands=Counter()
    failure=None
    for _ in range(MAX_STEPS):
        if life.stage3.substrate.mortal_status.value!="active":
            break
        try:
            result=life.run_step()
            if result.execution_status!="applied":
                failure="nonapplied:"+result.execution_status
                break
            commands[result.command_primitive]+=1
        except Exception as exc:
            failure=type(exc).__name__+": "+str(exc)
            break
    raw=life.journal.canonical_bytes()
    (folder/"canonical.jsonl").write_bytes(raw)
    row={"name":name,"profile":profile,"a2":obstacle,
         "instrumental":instrumental,"revalidate":revalidate,
         "world_steps":sum(commands.values()),"commands":dict(commands),
         "failure":failure,"audit_error":None,
         "config_sha256":config.digest(),
         "equipment_sha256":equipment.artifact_digest,
         "journal_sha256":sha256(raw).hexdigest()}
    try:
        anchor={"expected_head":life.journal.head_hash,
                "expected_count":len(life.journal.entries)}
        wal=HashChainedJournal.audit_durable_wal(str(folder/"life.wal"))
        if wal["head_hash"]!=anchor["expected_head"] or wal["verified_entries"]!=anchor["expected_count"]:
            raise ValueError("WAL mismatch")
        base=audit_export_bytes(raw,**anchor)
        goal=audit_stage12_goal_progress(raw,**anchor)
        agency=audit_stage12_first_person_agency(raw,**anchor)
        pairs=audit_stage12_attribution_pairs(raw,**anchor)
        physical=audit_stage12_p48_diversity(raw,**anchor)
        if obstacle:
            audit_stage12_a2_causal_link(raw,expected_interventions=((2,3,1),),**anchor)
        if base.world_steps_closed!=row["world_steps"]:
            raise ValueError("physical step mismatch")
        events=[json.loads(line)["causal_event"] for line in raw.splitlines()]
        changes=[e for e in events if e["kind"]=="stage6_progress_segment_revalidated"]
        if not revalidate and changes:
            raise ValueError("off variant emitted revalidation")
        for e in changes:
            d=e["data"]
            if (e.get("emitter")!="stage4-runtime"
                or d["authored_world_step"]>=e["t_monde"]
                or d["capture_world_step"]!=e["t_monde"]
                or d["physical_progress_claimed"] is not False
                or d["agency_claimed"] is not False):
                raise ValueError("unjustified revalidation receipt")
        row.update(
            site_count=physical["physically_distinct_sites"],
            moved=physical["confirmed_moves"],
            ingestion=physical["physically_confirmed_eats"],
            food_net_gains=physical["net_food_increase_steps_after_first"],
            first_post_move_search=[
                e.get("data",{}).get("progressive_search_diagnostic",{}).get("status")
                for e in events if e["kind"]=="stage6_planning_result"
                and e["t_monde"]==3],
            revalidations=len(changes),
            agency_self=agency.judgements_self,
            agency_world=agency.judgements_world,
            agency_unknown=agency.judgements_unknown,
            applied_pairs=pairs.applied_pairs,
            bias_evaluable=any(label is not None for _,label in pairs.diagnostic_labels))
        (folder/"physical-census.json").write_text(
            json.dumps(physical,indent=2,sort_keys=True)+"\n")
    except Exception as exc:
        row["audit_error"]=type(exc).__name__+": "+str(exc)
    (folder/"result.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n")
    print("A27_LIFE "+json.dumps(row,sort_keys=True),flush=True)
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--cohort-id",required=True)
    args=parser.parse_args()
    if not (1<=len(args.cohort_id)<=32 and
            all(c.isascii() and (c.isalnum() or c in "._-") for c in args.cohort_id)):
        parser.error("invalid preregistered cohort ID")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    lives=[]
    for profile in PROFILES:
        for obstacle in (False,True):
            for instrumental in (False,True):
                for revalidate in (False,True):
                    try:
                        lives.append(run_one(args.output_dir,args.cohort_id,profile,obstacle,instrumental,revalidate))
                    except Exception as exc:
                        lives.append({"profile":profile,"a2":obstacle,"instrumental":instrumental,
                            "revalidate":revalidate,"world_steps":0,
                            "failure":type(exc).__name__+": "+str(exc),"audit_error":"incomplete"})
    pairs=[]
    for profile in PROFILES:
        for a2 in (False,True):
            for instrumental in (False,True):
                off=next(v for v in lives if (v["profile"],v["a2"],v["instrumental"],v["revalidate"])==(profile,a2,instrumental,False))
                on=next(v for v in lives if (v["profile"],v["a2"],v["instrumental"],v["revalidate"])==(profile,a2,instrumental,True))
                pairs.append({"profile":profile,"a2":a2,"instrumental":instrumental,
                              "sites_off":off.get("site_count"),"sites_on":on.get("site_count"),
                              "ingestion_off":off.get("ingestion"),"ingestion_on":on.get("ingestion"),
                              "food_gains_off":off.get("food_net_gains"),"food_gains_on":on.get("food_net_gains"),
                              "revalidation_on":on.get("revalidations"),
                              "revalidation_off":off.get("revalidations")})
    summary={"schema":"stage12-a27-real-physical-contrast-v1",
             "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "cohort":args.cohort_id,"lives":lives,"paired":pairs,
             "planned_lives":16,"actual_lives":len(lives),
             "real_physical_steps":sum(x.get("world_steps",0) for x in lives),
             "technical_errors":sum(bool(x.get("failure") or x.get("audit_error")) for x in lives),
             "bias_evaluable_lives":sum(bool(x.get("bias_evaluable")) for x in lives),
             "operator_accepted":False,"scientific_generalization_proven":False}
    (args.output_dir/"a27-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A27_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="lives"},sort_keys=True),flush=True)
    return 0 if summary["technical_errors"]==0 and summary["real_physical_steps"]==672 else 2

if __name__=="__main__":
    raise SystemExit(main())
