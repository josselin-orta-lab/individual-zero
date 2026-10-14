"""A2.27 research-only dual-scope read-only external classification."""
import argparse
import json
from pathlib import Path
from collections import Counter
import subprocess

from run_stage12_issue110_a226 import run_one
from lab.stage12_goal_progress_audit import _number
from lab.determinism import canonical_causal_bytes

PROFILES=("restored","sustained","episodic","marginal")
def classify(primitive,effects,food_before,food_after,external):
    ate=effects.get("ate") in ("berry_a","berry_b")
    collected=effects.get("collected")
    gathered=isinstance(collected,dict) and type(collected.get("quantity")) is int and collected["quantity"]>0
    assert not ate or primitive=="manger"
    assert not gathered or primitive=="collecter"
    return {"proximal":("ingestion_effect" if ate else "collection_effect" if gathered
            else "no_direct_effect_witness"),
        "distal":("mixed" if external and ate else "external_influenced" if external
            else "ingestion_observed" if ate else "other"),
        "food_increase":food_after>food_before,"distal_responsibility":"not_established"}
def verify_controls():
    a=classify("collecter",{"collected":{"quantity":1}},30,30,False)
    b=classify("attendre",{},30,75,True)
    c=classify("manger",{"ate":"berry_a"},30,75,True)
    assert a["proximal"]=="collection_effect" and not a["food_increase"]
    assert b["distal"]=="external_influenced" and b["distal_responsibility"]=="not_established"
    assert c["distal"]=="mixed"
    return 3
def review(folder,row):
    events=[json.loads(s)["causal_event"] for s in (folder/"canonical.jsonl").read_bytes().splitlines()]
    witness=json.loads((folder/"physical-witness.json").read_text())
    effects=json.loads((folder/"effects-external-audit.json").read_text())
    assert len(witness)==len(effects)==row["physical_steps"]
    commands={};transitions={};closed=set();pulses=set()
    for e in events:
        t=e.get("t_monde"); k=e.get("kind")
        if k=="command_experienced":
            assert t not in commands
            commands[t]=e
        if k=="world_transition_experienced":
            assert t not in transitions
            transitions[t]=e
        if k=="step_closed":
            assert t not in closed
            closed.add(t)
        if k=="external_input_received" and e.get("operation")=="set_body":
            assert t not in pulses
            pulses.add(t)
    assert len(commands)==len(transitions)==len(closed)==len(witness)
    categories=Counter()
    for w,x in zip(witness,effects):
        t=w["step"];cmd=commands[t];tr=transitions[t]
        assert cmd["attempt_ref"]==tr["attempt_ref"]
        assert cmd["primitive"]==w["primitive"]==x["primitive"]
        assert tr["position_after"]==w["after"]["position"]
        assert _number(tr["body_after"]["food"])==w["after"]["body"]["food"]
        assert x["pulse_received"]==(t in pulses)
        got=classify(cmd["primitive"],tr["effects"],w["before"]["body"]["food"],
                     w["after"]["body"]["food"],t in pulses)
        assert got["distal_responsibility"]=="not_established"
        if got["proximal"]=="collection_effect":
            quant=tr["effects"]["collected"]["quantity"]
            target=cmd["parameters"]["target"]
            assert w["after"]["inventory"].get(target,0)-w["before"]["inventory"].get(target,0)==quant
        categories[got["proximal"]]+=1
        categories[got["distal"]]+=1
    assert len(pulses)==int(row["pulse_step"] is not None)
    return dict(categories)
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=False)
    controls=verify_controls();rows=[];aggregate=Counter()
    for profile in PROFILES:
        for blocked in (False,True):
            for pulse in (None,6):
                d=a.output_dir/f"{profile}-{'a2' if blocked else 'free'}-pulse{pulse if pulse is not None else 'none'}"
                row=run_one(d,profile,blocked,pulse,"a227-dual-scope-newborn-v1")
                assert row["failure"] is None,row
                counts=review(d,row)
                aggregate.update(counts)
                rows.append({"profile":profile,"blocked":blocked,"pulse_step":pulse,
                             "steps":row["physical_steps"],"goal_audit":row["goal_progress_audit_status"],
                             "agency_self":row["agency_self"],"agency_world":row["agency_world"],
                             "agency_unknown":row["agency_unknown"],"pairs_applied":row["pairs_applied"],
                             "bias_evaluable":row["bias_evaluable"],"effects":counts})
    summary={"schema":"a227-dual-scope-lab-v1","head_sha":subprocess.check_output(
        ["git","rev-parse","HEAD"],text=True).strip(),"life_count":len(rows),
        "physical_steps":sum(r["steps"] for r in rows),"external_pulses":8,
        "negative_controls":controls,
        "fully_audited_lives":sum(r["goal_audit"]=="verified" for r in rows),
        "confounded_lives":sum(r["goal_audit"]=="fail_closed_exogenous_confounded" for r in rows),
        "ga06_evaluable_lives":sum(bool(r["bias_evaluable"]) for r in rows),
        "effect_categories":dict(aggregate),"responsibility_distal_proven":0,
        "cognitive_policy_changed":False,"operator_reception":False,"stage12":"PARTIAL"}
    assert summary["life_count"]==16 and summary["physical_steps"]==512
    assert sum(r["pulse_step"] is not None for r in rows)==8
    (a.output_dir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("A227_SUMMARY "+json.dumps(summary,sort_keys=True),flush=True)
if __name__=="__main__":main()
