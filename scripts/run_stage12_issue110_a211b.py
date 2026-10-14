"""A2.11b preregistered 16-life obstacle timing causal contrast; real physical witnesses."""
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
TIMINGS={"none":None,"original":4}
MAX_STEPS=42


def run_one(root, cohort, profile, timing, extended):
    gain=1.6
    obstacle = timing != 'none'
    clear_step = TIMINGS[timing]
    instrumental = False
    name="_".join((profile,timing,"corpus_extended" if extended else "corpus_original"))
    folder=root/name
    folder.mkdir()
    life,config,layout,equipment=build_life(
        "near_food_free",70.0,"horizon_three",
        birth_life_id=f"i0:110:a211b:{cohort}:{name}",
        wal_path=str(folder/"life.wal"),
        a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=clear_step,
        calibration_food_profile=profile,
        progressive_planning=True,progressive_evaluation_prefix=True,
        instrumental_geographic_value=False,
        progressive_revalidate_on_new_capture=True,
        extrinsic_gain_override=gain,
        extended_prebirth_equipment=extended)
    Stage12OperatorConsole(substrate=life.stage3.substrate,
        mode="campaign",policy_version="stage12-issue110-a211b-prereg-v1",
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
    row={"name":name,"profile":profile,"a2":obstacle,"timing":timing,
         "instrumental":instrumental,"gain":gain,"extended":extended,
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
            collected=sum(e["kind"]=="world_transition_experienced" and isinstance(e.get("effects",{}).get("collected"),dict) for e in events),
            body_food_final=physical["positions"][-1]["food_after"],
            goal_decision_steps=[e["t_monde"] for e in events if e["kind"]=="stage12_action_motive_attested" and e.get("data",{}).get("motive_type")=="active_goal"],
            blocked_moves=physical["blocked_moves"],
            planning_unavailable=sum(e["kind"]=="stage6_planning_result" and e.get("data",{}).get("progressive_search_diagnostic",{}).get("status")=="incomplete_model" for e in events),
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
    print("A211B_LIFE "+json.dumps(row,sort_keys=True),flush=True)
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
        for timing in TIMINGS:
            for extended in (False,True):
                try:
                    lives.append(run_one(args.output_dir,args.cohort_id,profile,timing,extended))
                except Exception as exc:
                    lives.append({"profile":profile,"timing":timing,"a2":timing!="none",
                                  "instrumental":False,"gain":1.6,"extended":extended,"world_steps":0,
                                  "failure":type(exc).__name__+": "+str(exc),"audit_error":"incomplete"})
    pairs=[]
    for profile in PROFILES:
        for timing in TIMINGS:
            samples=[next(v for v in lives if
                (v["profile"],v["timing"],v["extended"])==(profile,timing,mode))
                for mode in (False,True)]
            pairs.append({"profile":profile,"timing":timing,
                "baseline":{"ingestion":samples[0].get("ingestion"),
                            "sites":samples[0].get("site_count"),
                            "food_gains":samples[0].get("food_net_gains"),
                            "incomplete":samples[0].get("planning_unavailable")},
                "extended":{"ingestion":samples[1].get("ingestion"),
                            "sites":samples[1].get("site_count"),
                            "food_gains":samples[1].get("food_net_gains"),
                            "incomplete":samples[1].get("planning_unavailable")},
                "sha_distinct":samples[0].get("equipment_sha256")!=samples[1].get("equipment_sha256")})
    summary={"schema":"stage12-a211b-physical-corpus-ablation-v1",
             "code_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
             "cohort":args.cohort_id,"lives":lives,"paired":pairs,
             "planned_lives":8,"actual_lives":len(lives),
             "real_physical_steps":sum(x.get("world_steps",0) for x in lives),
             "technical_errors":sum(bool(x.get("failure") or x.get("audit_error")) for x in lives),
             "bias_evaluable_lives":sum(bool(x.get("bias_evaluable")) for x in lives),
             "operator_accepted":False,"scientific_generalization_proven":False}
    (args.output_dir/"a211b-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A211B_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="lives"},sort_keys=True),flush=True)
    return 0 if summary["actual_lives"]==8 and summary["technical_errors"]==0 and summary["real_physical_steps"]==336 else 2

if __name__=="__main__":
    raise SystemExit(main())
