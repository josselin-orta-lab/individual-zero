"""A2.29: independently classify already lived B choices from canonical receipts."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import json,subprocess
import run_stage12_issue110_b_a228_funnel as a228

PROFILES=a228.PROFILES
CATEGORIES=("reduced_sleep","no_attested_active_goal","no_planner_proposal",
 "goal_proposed_not_registered","registered_but_not_evaluated",
 "evaluated_but_not_crossed","crossed_not_selected",
 "goal_selected_no_B","goal_selected_B","evidence_insufficient")

def classify_step(entries):
    kinds=defaultdict(list)
    for e in entries:kinds[e["kind"]].append(e)
    executed=kinds["command_experienced"]
    assert len(executed)==1
    motive=kinds["stage12_action_motive_attested"]
    if not motive:
        if len(kinds["stage10_reduced_capture"])!=1 or executed[0].get("primitive")!="dormir":
            raise ValueError("unauthorized absence of waking motive")
        return "reduced_sleep",{}
    if len(motive)!=1:raise ValueError("ambiguous motor motive")
    attested=motive[0]["data"]
    goal=attested.get("active_goal_ref")
    if goal is None:return "no_attested_active_goal",{}
    if attested["motive_type"]=="active_goal":
        return ("goal_selected_B" if len(kinds["stage12_outcome_responsibility_precommitted"])==1
                else "goal_selected_no_B"),{}
    planning=[e for e in kinds["stage6_planning_result"] if e.get("data",{}).get("goal_ref")==goal]
    if not planning:return "evidence_insufficient",{"reason":"no_recorded_planning_call"}
    options={e["data"].get("proposal_ref") for e in planning if e["data"].get("proposal_ref")}
    status=Counter(str(e["data"].get("progressive_search_diagnostic",{}).get("status","missing")) for e in planning)
    if not options:return "no_planner_proposal",{"search_status":dict(status)}
    registered={e["data"].get("option_ref") for e in kinds["option_registration"] if e["data"].get("registered") is True}
    if not options & registered:
        return "goal_proposed_not_registered",{"search_status":dict(status)}
    candidates=options & registered
    evaluated={e["data"].get("option_ref") for e in kinds["stage8_option_evaluation"]}
    if not candidates & evaluated:return "registered_but_not_evaluated",{"search_status":dict(status)}
    traces=[t for e in kinds["competition_cycle"] for t in e.get("data",{}).get("traces",[])]
    if not traces:return "evidence_insufficient",{"reason":"missing_competition_traces"}
    crossed={t.get("option_ref") for t in traces if t.get("crossed") is True}
    if not crossed & candidates:return "evaluated_but_not_crossed",{"search_status":dict(status)}
    return "crossed_not_selected",{"search_status":dict(status)}

def controls():
    def ev(k,**kwargs):return {"kind":k,"t_monde":1,"attempt_ref":"x",**kwargs}
    assert classify_step([ev("command_experienced",primitive="dormir"),ev("stage10_reduced_capture")])[0]=="reduced_sleep"
    assert classify_step([ev("command_experienced",primitive="attendre"),
        ev("stage12_action_motive_attested",data={"active_goal_ref":"food","motive_type":"cible_exploration"}),
        ev("stage6_planning_result",data={"goal_ref":"food","proposal_ref":None})])[0]=="no_planner_proposal"
    assert classify_step([ev("command_experienced",primitive="manger"),
        ev("stage12_action_motive_attested",data={"active_goal_ref":"food","motive_type":"active_goal"}),
        ev("stage12_outcome_responsibility_precommitted")])[0]=="goal_selected_B"
    return 3

def run(folder,profile,blocked):
    old=a228.STEPS
    a228.STEPS=48
    try:row=a228.run_one(folder,profile,blocked,birth_cohort='a229')
    finally:a228.STEPS=old
    assert row["birth_id"].startswith("i0:stage12:b:a229:"), "cohort birth identity collision"
    events=[json.loads(x)["causal_event"] for x in (folder/"canonical.jsonl").read_bytes().splitlines()]
    bystep=defaultdict(list)
    for e in events:
        if e.get("t_monde") is not None:bystep[e["t_monde"]].append(e)
    counts=Counter();statuses=Counter();examples={}
    for t in range(1,row["world_steps"]+1):
        kind,detail=classify_step(bystep[t])
        counts[kind]+=1
        statuses.update(detail.get("search_status",{}))
        examples.setdefault(kind,t)
    assert sum(counts.values())==row["world_steps"]
    result={"profile":profile,"blocked":blocked,"steps":row["world_steps"],
        "categories":dict(counts),"planner_statuses":dict(statuses),
        "first_examples":examples,"dual_judgements":row["dual_judgements"],
        "journal_head":row["journal_head"]}
    (folder/"arbitration.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("A229_LIFE "+json.dumps(result,sort_keys=True),flush=True)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=False)
    checks=controls();rows=[];errors=[]
    for profile in PROFILES:
        for blocked in (False,True):
            label=profile+("-a2" if blocked else "-free")
            try:rows.append(run(a.output_dir/label,profile,blocked))
            except Exception as e:
                errors.append({"life":label,"error":type(e).__name__+": "+str(e)})
                (a.output_dir/(label+"-error.json")).write_text(json.dumps(errors[-1])+"\n")
    result={"schema":"stage12-a229-choice-v1","head_sha":subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True).strip(),
        "lives":len(rows),"errors":errors,"physical_steps":sum(r["steps"] for r in rows),
        "dual_judgements":sum(r["dual_judgements"] for r in rows),
        "categories":dict(sum((Counter(r["categories"]) for r in rows),Counter())),
        "negative_controls":checks,"norm_changed":False,"stage12":"PARTIAL"}
    (a.output_dir/"summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("A229_SUMMARY "+json.dumps(result,sort_keys=True),flush=True)
    if errors or len(rows)!=8 or result["physical_steps"]!=384:raise SystemExit(2)
if __name__=="__main__":main()
