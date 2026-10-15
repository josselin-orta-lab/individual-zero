"""A2.30 preregistered first-pass read-only planning completeness census.

Investigates observed unavailable search edges, does not claim their cause.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import subprocess

import run_stage12_issue110_b_a228_funnel as cohort

PROFILES=("restored","sustained","episodic","marginal")
STEPS=48

def inspect(folder,profile,blocked):
    old=cohort.STEPS
    cohort.STEPS=STEPS
    try:
        row=cohort.run_one(folder,profile,blocked,birth_cohort="a230")
    finally:
        cohort.STEPS=old
    if not row["birth_id"].startswith("i0:stage12:b:a230:"):
        raise ValueError("wrong scientific birth namespace")
    events=[json.loads(x)["causal_event"] for x in
            (folder/"canonical.jsonl").read_bytes().splitlines()]
    statuses=Counter();searches=[];no_proposals=0;incomplete=0
    for event in events:
        if event.get("kind")!="stage6_planning_result":
            continue
        d=event.get("data",{})
        diag=d.get("progressive_search_diagnostic")
        if not isinstance(diag,dict):
            raise ValueError("missing search diagnostic")
        status=str(diag.get("status","missing"))
        statuses[status]+=1
        no_proposals+=d.get("proposal_ref") is None
        incomplete+=status=="incomplete_model"
        # This diagnostic is *not* a root-cause label.
        searches.append({"world_step":event["t_monde"],
            "attempt_ref":event.get("attempt_ref"),
            "goal_ref":d.get("goal_ref"),
            "proposal_ref":d.get("proposal_ref"),
            "status":status,
            "expanded_states":diag.get("expanded_states"),
            "unavailable_edges":diag.get("unavailable_edges"),
            "diagnostic_fields":sorted(diag)})
    unsupported=Counter()
    for e in events:
        if e.get("kind")!="compute_charge":continue
        d=e.get("data",{})
        if not d.get("accepted",True):
            unsupported[str(d.get("operation"))]+=1
    audit={"profile":profile,"obstacle":"A2" if blocked else "free",
        "birth_id":row["birth_id"],"world_steps":row["world_steps"],
        "journal_head":row["journal_head"],"goal_activations":row["goal_activations"],
        "active_goal_motive":row["motive_counts"].get("active_goal",0),
        "dual_judgements":row["dual_judgements"],
        "statuses":dict(statuses),"no_proposals":no_proposals,
        "incomplete_diagnostics":incomplete,"uc_refusals":dict(unsupported),
        "causal_root_cause":"unresolved_without_per_edge_receipts"}
    (folder/"planning-searches.json").write_text(json.dumps(searches,indent=2,sort_keys=True)+"\n")
    (folder/"a230-result.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print("A230_LIFE "+json.dumps(audit,sort_keys=True),flush=True)
    return audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=False)
    results=[];failures=[]
    for profile in PROFILES:
        for blocked in (False,True):
            name=profile+("-a2" if blocked else "-free")
            try:results.append(inspect(a.output_dir/name,profile,blocked))
            except Exception as exc:
                item={"life":name,"error":type(exc).__name__+": "+str(exc)}
                failures.append(item)
                (a.output_dir/(name+"-error.json")).write_text(json.dumps(item)+"\n")
    report={"schema":"stage12-a230-model-completeness-v1",
        "sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "lives":len(results),"physical_steps":sum(x["world_steps"] for x in results),
        "status_counts":dict(sum((Counter(x["statuses"]) for x in results),Counter())),
        "incomplete_diagnostics":sum(x["incomplete_diagnostics"] for x in results),
        "dual_judgements":sum(x["dual_judgements"] for x in results),
        "failures":failures,"model_root_cause":"not_established",
        "norm_changed":False,"stage12":"PARTIAL"}
    (a.output_dir/"summary.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("A230_SUMMARY "+json.dumps(report,sort_keys=True),flush=True)
    if failures or len(results)!=8 or report["physical_steps"]!=384:
        raise SystemExit(2)

if __name__=="__main__":main()
