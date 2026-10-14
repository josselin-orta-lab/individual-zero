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

PROFILES = ("restored", "sustained", "replenished", "urgent")
WEIGHTS = (False, True)
MAX_STEPS = 42


def motive_trace(raw: bytes) -> list[dict]:
    """Read-only summary of actual goal choices, not feedback to cognition."""
    steps: dict[int, dict] = {}
    for line in raw.splitlines():
        event = json.loads(line)["causal_event"]
        t = event.get("t_monde")
        if type(t) is not int:
            continue
        kind = event.get("kind")
        data = event.get("data", {})
        row = steps.setdefault(t, {
            "step": t, "goals": [], "selected": [], "candidates": [],
            "registrations": [], "refused_uc": [],
        })
        if kind == "active_goal_changed" and isinstance(data, dict):
            def project(goal):
                return ({k: goal.get(k) for k in
                         ("goal_type", "target", "current_pressure")}
                        if isinstance(goal, dict) else None)
            row["goals"].append({
                "before": project(data.get("before")),
                "after": project(data.get("after"))})
        elif kind == "stage12_action_motive_attested" and isinstance(data, dict):
            row["selected"].append({
                "motive": data.get("motive_type"),
                "goal_ref": data.get("goal_ref"),
                "active_goal_ref": data.get("active_goal_ref"),
                "option": data.get("option_ref")})
        elif kind == "stage8_option_evaluation" and isinstance(data, dict):
            row["candidates"].append({
                "signature": data.get("learning_signature"),
                "status": data.get("status")})
        elif kind in ("option_registration",
                      "stage11_geographic_option_registration") and isinstance(data, dict):
            row["registrations"].append({
                "kind": kind, "registered": data.get("registered"),
                "option": data.get("option_ref")})
        elif kind == "compute_charge" and isinstance(data, dict) and data.get("accepted") is False:
            row["refused_uc"].append({
                "module": data.get("module"),
                "operation": data.get("operation"),
                "reason": data.get("reason")})
    return [steps[t] for t in sorted(steps)]


def one(root, profile, obstacle, cohort, enabled):
    name = ("instrumental_" if enabled else "control_") + profile + ("_a2" if obstacle else "_free")
    folder = root / name
    folder.mkdir()
    life_id = f"i0:110:multi:{cohort}:{name}"
    life, config, layout, equipment = build_life(
        "near_food_free",70.0,"horizon_three",
        birth_life_id=life_id, wal_path=str(folder/"life.wal"),
        a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=(4 if obstacle else None),
        calibration_food_profile=profile, progressive_planning=True,
        progressive_evaluation_prefix=True,
        instrumental_geographic_value=enabled)
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-stage6-reachability-prereg-v1",
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
    motivations=motive_trace(raw)
    (folder/"motive-trace.json").write_text(json.dumps(motivations,indent=2,sort_keys=True)+"\n")
    (folder/"step-trace.json").write_text(json.dumps(trace,indent=2,sort_keys=True)+"\n")
    counts=coverage_census(trace)
    plan_trace=[]
    for rawline in raw.splitlines():
        ev=json.loads(rawline)["causal_event"]
        if ev.get("kind")=="stage6_planning_result":
            data=ev.get("data", {})
            diag=data.get("progressive_search_diagnostic")
            if diag is not None:
                plan_trace.append({
                    "t_monde":ev.get("t_monde"),
                    "goal_ref":data.get("goal_ref"),
                    "proposal_ref":data.get("proposal_ref"),
                    "segment_proposed":data.get("progressive_segment_proposed"),
                    "search":diag,
                })
    # Join separately authored plan proposals, competition valuations, and
    # actual motor selections by world step and original option reference.
    # Never equate "proposed" with "executed".
    events=[json.loads(line)["causal_event"] for line in raw.splitlines()]
    for planned in plan_trace:
        opt=planned["proposal_ref"]
        t=planned["t_monde"]
        evaluation=[e.get("data",{}) for e in events
            if e.get("t_monde")==t
            and e.get("kind")=="stage6_option_evaluation"
            and e.get("data",{}).get("option_ref")==opt]
        selection=[e.get("data",{}) for e in events
            if e.get("t_monde")==t
            and e.get("kind")=="stage12_action_motive_attested"
            and e.get("data",{}).get("option_ref")==opt]
        planned["evaluations"]=[{
            "status": e.get("status"),
            "simulated_value_status":e.get("simulated_value_status"),
            "simulated_value":e.get("simulated_value"),
            "evidence":e.get("evidence"),
        } for e in evaluation]
        planned["selection_count"]=len(selection)
        registration=[e.get("data",{}) for e in events
            if e.get("t_monde")==t
            and e.get("kind")=="option_registration"
            and e.get("data",{}).get("option_ref")==opt]
        competition=[trace for e in events
            if e.get("t_monde")==t and e.get("kind")=="competition_cycle"
            for trace in e.get("data",{}).get("traces",[])
            if trace.get("option_ref")==opt]
        planned["registrations"]=registration
        planned["competition_traces"]=competition
    for entry in plan_trace:
        if not entry["segment_proposed"]:
            continue
        opt=entry["proposal_ref"]
        t=entry["t_monde"]
        entry["admission_receipts"]=[
            {"kind":e.get("kind"),"data":e.get("data",{})}
            for e in events if e.get("t_monde")==t
            and e.get("kind") in ("command_admitted","command_vetoed")
            and e.get("data",{}).get("option_ref")==opt
        ]
        entry["stage8_evaluation"]=[
            {"status":e.get("data",{}).get("status"),
             "simulated_value":e.get("data",{}).get("simulated_value"),
             "evidence":e.get("data",{}).get("evidence")}
            for e in events if e.get("t_monde")==t
            and e.get("kind")=="stage8_option_evaluation"
            and e.get("data",{}).get("option_ref")==opt
        ]
    # Independently reconstruct crossed candidates per exact cycle from
    # persisted Competition traces; never choose or rank options inside I0.
    decisions=[]
    for e in events:
        if e.get("kind")!="competition_cycle":
            continue
        crossed=[]
        for item in e.get("data",{}).get("traces",[]):
            if item.get("crossed"):
                before=item.get("accumulator_after")
                threshold=item.get("threshold")
                def numeric(x):
                    return float.fromhex(x["$f64"]) if isinstance(x,dict) and "$f64" in x else float(x)
                score=(numeric(before)-numeric(threshold))/numeric(threshold)
                crossed.append({"option_ref":item["option_ref"],"margin":score})
        crossed.sort(key=lambda r:-r["margin"])
        if crossed:
            t=e.get("t_monde")
            cy=e.get("cycle")
            admissions=[{"kind":v.get("kind"),"option_ref":v.get("data",{}).get("option_ref"),"reason":v.get("data",{}).get("reason")}
                for v in events if v.get("t_monde")==t and v.get("cycle")==cy
                and v.get("kind") in ("command_admitted","command_vetoed")]
            decisions.append({"t_monde":t,"cycle":cy,"crossed":crossed,
                              "admissions":admissions})
    (folder/"crossed-ranked-audit.json").write_text(
        json.dumps(decisions,indent=2,sort_keys=True)+"\\n")
    if True:
        for decision in decisions:
            if any(":progress:prefix" in row["option_ref"] for row in decision["crossed"]):
                print("CROSSED_RANKED " + json.dumps(
                    {"condition":name,**decision},sort_keys=True))
    (folder/"progressive-search-trace.json").write_text(
        json.dumps(plan_trace,indent=2,sort_keys=True)+"\n")
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
    report=dict(condition=name,profile=profile,intervention=obstacle,instrumental=enabled,life_id=life_id,
                config_sha256=config.digest(),equipment_sha256=equipment.artifact_digest,
                journal_sha256=sha256(raw).hexdigest(),steps=sum(actions.values()),
                commands=dict(actions),coverage=counts,execution_error=execution_error,
                audit_error=audit_error,
                progressive_search_census={
                    "events":len(plan_trace),
                    "statuses":dict(Counter(
                        entry["search"].get("status") for entry in plan_trace
                        if isinstance(entry["search"],dict))),
                    "unavailable_edges":sum(
                        int(entry["search"].get("unavailable_edges",0))
                        for entry in plan_trace if isinstance(entry["search"],dict)),
                    "expanded_states":sum(
                        int(entry["search"].get("expanded_states",0))
                        for entry in plan_trace if isinstance(entry["search"],dict)),
                    "segments_proposed":sum(bool(entry["segment_proposed"])
                                            for entry in plan_trace),
                    "segments_selected":sum(
                        entry["selection_count"] for entry in plan_trace
                        if entry["segment_proposed"]),
                    "segment_evaluations":sum(
                        len(entry["evaluations"]) for entry in plan_trace
                        if entry["segment_proposed"]),
                    "segment_registration_attempts":sum(
                        len(entry["registrations"]) for entry in plan_trace
                        if entry["segment_proposed"]),
                    "segment_registered_true":sum(
                        e.get("registered") is True
                        for entry in plan_trace if entry["segment_proposed"]
                        for e in entry["registrations"]),
                    "segment_competition_traces":sum(
                        len(entry["competition_traces"]) for entry in plan_trace
                        if entry["segment_proposed"]),
                    "segment_evaluations_unavailable":sum(
                        e["status"] == "not_evaluated"
                        for entry in plan_trace if entry["segment_proposed"]
                        for e in entry["evaluations"]),
                    "segment_evaluations_nonpositive":sum(
                        e["status"] == "evaluated"
                        and isinstance(e["evidence"], (int, float))
                        and e["evidence"] <= 0
                        for entry in plan_trace if entry["segment_proposed"]
                        for e in entry["evaluations"]),
                },
                motive_census={
                    "goal_changes":sum(len(r["goals"]) for r in motivations),
                    "goal_motives":sum(m["motive"]=="active_goal" for r in motivations for m in r["selected"]),
                    "other_motives":sum(m["motive"]!="active_goal" for r in motivations for m in r["selected"]),
                    "option_evaluations":sum(len(r["candidates"]) for r in motivations),
                    "registrations":sum(len(r["registrations"]) for r in motivations),
                    "refused_uc":sum(len(r["refused_uc"]) for r in motivations),
                },**results)
    (folder/"result.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))
    if True:
        for entry in plan_trace:
            if entry["segment_proposed"]:
                print("PROGRESSIVE_FUNNEL " + json.dumps({
                    "condition":name, **entry,
                },sort_keys=True))
    for row in motivations:
        if row["goals"] or row["selected"] or row["refused_uc"]:
            print("MOTIVE_STEP "+json.dumps({
                "condition":name, "step":row["step"],
                "goals":row["goals"], "selected":row["selected"],
                "candidates":row["candidates"][:8],
                "registrations":row["registrations"][:8],
                "refused_uc":row["refused_uc"][:6],
            },sort_keys=True))
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--cohort-id",required=True)
    args=ap.parse_args()
    if not 1<=len(args.cohort_id)<=32 or not all(c.isascii() and (c.isalnum() or c in "._-") for c in args.cohort_id):
        raise ValueError("invalid independent birth cohort")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    lives=[one(args.output_dir,p,intervention,args.cohort_id,enabled) for enabled in WEIGHTS for p in PROFILES for intervention in (False,True)]
    summary=dict(schema="issue110-instrumental-geographic-ab-v1",
                 source_sha=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                 preregistration="docs/research/stage12-issue110-instrumental-geographic-prereg-2026-10-14.fr.md",
                 lives=lives,planned_lives=16,actual_lives=len(lives),
                 physical_steps=sum(l["steps"] for l in lives),
                 evaluable_lives=sum(l.get("evaluable",False) for l in lives),
                 failures=sum(bool(l["execution_error"] or l["audit_error"]) for l in lives),
                 operator_accepted=False,scientific_status="exploratory")
    (args.output_dir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("CAMPAIGN_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="lives"},sort_keys=True))
    return 2 if summary["failures"] else 0


if __name__=="__main__":
    raise SystemExit(main())
