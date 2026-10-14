"""Explore preregistered independent lives, never alter cognitive policy."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from run_stage12_issue110_first_planning_state import build_life
from run_stage12_issue110_calibration_feasibility import source_step_trace, coverage_census
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_a2_causal_audit import audit_stage12_a2_causal_link
from lab.stage12_operator_console import Stage12OperatorConsole

PROFILES = ("sustained", "episodic", "marginal")
MAX_STEPS = 36


def one(root, profile, obstacle, cohort):
    name = profile + ("_a2" if obstacle else "_free")
    folder = root / name
    folder.mkdir()
    life_id = f"i0:110:multi:{cohort}:{name}"
    life, config, layout, equipment = build_life(
        "near_food_free",70.0,"horizon_three",
        birth_life_id=life_id, wal_path=str(folder/"life.wal"),
        a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=(4 if obstacle else None),
        calibration_food_profile=profile)
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-multi-engagement-prereg-v1",
        maximum_world_steps=MAX_STEPS)
    actions=Counter()
    execution_error=None
    for _ in range(MAX_STEPS):
        try:
            step=life.run_step()
            if step.execution_status!="applied":
                execution_error="nonapplied:"+step.execution_status
                break
            actions[step.command_primitive]+=1
        except Exception as exc:
            execution_error=type(exc).__name__+": "+str(exc)
            break
    raw=life.journal.canonical_bytes()
    (folder/"canonical.jsonl").write_bytes(raw)
    trace=source_step_trace(raw)
    (folder/"step-trace.json").write_text(json.dumps(trace,indent=2,sort_keys=True)+"\n")
    counts=coverage_census(trace)
    anchors=dict(expected_head=life.journal.head_hash,expected_count=len(life.journal.entries))
    audit_error=None
    results={}
    try:
        durable=HashChainedJournal.audit_durable_wal(str(folder/"life.wal"))
        if durable["head_hash"]!=anchors["expected_head"] or durable["verified_entries"]!=anchors["expected_count"]:
            raise ValueError("durability custody differs from journal")
        base=audit_export_bytes(raw,**anchors)
        goal=audit_stage12_goal_progress(raw,**anchors)
        agency=audit_stage12_first_person_agency(raw,**anchors)
        pairs=audit_stage12_attribution_pairs(raw,**anchors)
        if base.world_steps_closed != sum(actions.values()):
            raise ValueError("physical steps mismatch")
        if obstacle:
            causal=audit_stage12_a2_causal_link(raw,expected_interventions=((2,3,1),),**anchors)
            results["a2_verified_judgements"]=causal.verified_a2_subjective_world_judgements
        labels=[{"step":step,"label":label} for step,label in pairs.diagnostic_labels if label is not None]
        if counts["admitted_pairs"]!=pairs.admitted_pairs or counts["applied_pairs"]!=pairs.applied_pairs:
            raise ValueError("census disagrees with independent audit")
        results.update(
            engagements=goal.preregistered,
            agency_self=agency.judgements_self,agency_world=agency.judgements_world,
            agency_unknown=agency.judgements_unknown,applied_successes=pairs.applied_successes,
            applied_failures=pairs.applied_failures,bias_labels=labels,
            evaluable=bool(labels),pairs_admitted=pairs.admitted_pairs,
            pairs_applied=pairs.applied_pairs)
    except Exception as exc:
        audit_error=type(exc).__name__+": "+str(exc)
    report=dict(condition=name,profile=profile,intervention=obstacle,life_id=life_id,
                config_sha256=config.digest(),equipment_sha256=equipment.artifact_digest,
                journal_sha256=sha256(raw).hexdigest(),steps=sum(actions.values()),
                commands=dict(actions),coverage=counts,execution_error=execution_error,
                audit_error=audit_error,**results)
    (folder/"result.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--cohort-id",required=True)
    args=ap.parse_args()
    if not 1<=len(args.cohort_id)<=32 or not all(c.isascii() and (c.isalnum() or c in "._-") for c in args.cohort_id):
        raise ValueError("invalid independent birth cohort")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    lives=[one(args.output_dir,p,intervention,args.cohort_id) for p in PROFILES for intervention in (False,True)]
    summary=dict(schema="issue110-multi-engagement-exploration-v1",
                 source_sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                 preregistration="docs/research/stage12-issue110-multi-engagement-prereg-2026-10-14.fr.md",
                 lives=lives,planned_lives=6,actual_lives=len(lives),
                 physical_steps=sum(l["steps"] for l in lives),
                 evaluable_lives=sum(l.get("evaluable",False) for l in lives),
                 failures=sum(bool(l["execution_error"] or l["audit_error"]) for l in lives),
                 operator_accepted=False,scientific_status="exploratory")
    (args.output_dir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("CAMPAIGN_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="lives"},sort_keys=True))
    return 2 if summary["failures"] else 0


if __name__=="__main__":
    raise SystemExit(main())
