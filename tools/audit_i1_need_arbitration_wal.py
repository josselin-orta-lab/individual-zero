#!/usr/bin/env python3
"""Passive WAL-only causal-choice gap audit: no changes to I1 agency."""
from collections import Counter, defaultdict
import argparse, json
from pathlib import Path

def f64(x):
    return float.fromhex(x["$f64"]) if isinstance(x, dict) else float(x)

def analyze(folder):
    report=json.loads((folder/"report.json").read_text())
    if (report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or report["run"]["custody"]!="wal" or len(report["lives"])!=1):
        raise ValueError("incomplete individual WAL run")
    life=report["lives"][0]; file=folder/life["custody_file"]
    if file.is_symlink() or not file.is_file(): raise ValueError("missing sealed WAL")
    accum=defaultdict(lambda:{"max_ratio":0,"traces":0,"crossed":0})
    seen=defaultdict(set); seen_body={}; commands={}; count=0; last=None
    for raw in file.open("rb"):
        rec=json.loads(raw); ev=rec["causal_event"]; kind=ev["kind"];t=ev["t_monde"]
        count+=1;last=rec["event_hash"]; data=ev.get("data") or {}
        if kind=="perceptual_capture":
            seen_body[t]=data
        elif kind=="command_experienced":
            commands[t]=ev["primitive"]
        elif kind=="competition_cycle":
            for tr in data.get("traces",()):
                ref=tr["option_ref"]
                key=("manger" if ":manger:" in ref else
                     "geographic" if ref.startswith("option:geographic:") else None)
                if key is None:continue
                a=accum[key];a["traces"]+=1
                ratio=f64(tr["accumulator_after"])/f64(tr["threshold"])
                a["max_ratio"]=max(a["max_ratio"],ratio)
                if tr["crossed"]:a["crossed"]+=1;seen[key].add(t)
    if count!=life["durable_entries"] or last!=life["journal_head"]:
        raise ValueError("WAL length/hash mismatch")
    critical=Counter()
    for step in life["steps"]:
        t=step["world_step"]
        capture=seen_body.get(t)
        if capture is None:continue
        body=capture["dual_scope_visible_body"]; inventory=capture["agency_visible_inventory"]
        if f64(body["food"])<=15 and inventory.get("berry_a",0)+inventory.get("berry_b",0)>0:
            critical["food_critical_with_visible_edible_inventory"]+=1
            critical[commands.get(t,"missing")]+=1
    return {"schema":"i1-need-arbitration-audit/v1",
            "sha":report["run"]["git_head"],"life_id":life["individual_id"],
            "lifecycle":life["lifecycle"],"steps":len(life["steps"]),
            "critical_food_visible":dict(critical),
            "competition_by_type":dict(accum),
            "distinct_crossed_steps":{k:len(v) for k,v in seen.items()},
            "causal_learning":"NOT_ESTABLISHED",
            "journal_head":last}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.input)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":main()
