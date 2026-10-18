#!/usr/bin/env python3
"""Fail-closed descriptive observer for I1 minimal-choice proof; no GO by counts."""
import argparse, csv, json
from pathlib import Path
from collections import Counter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--sha",required=True)
    a=p.parse_args()
    rows=[]
    for role in ("a","b"):
        for mode in ("active","masked"):
            for seed in range(246,251):
                folder=a.input/role/mode/("seed-"+str(seed))
                file=folder/"report.json"
                if not file.is_file():raise ValueError("missing arm "+str(file))
                report=json.loads(file.read_text())
                run=report["run"]
                if (report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
                    or run.get("git_head")!=a.sha
                    or run.get("food_role")!=role
                    or run.get("learning_read_ablation")!=(mode=="masked")
                    or run.get("seed")!=seed or len(report["lives"])!=1):
                    raise ValueError("unpaired/mixed source study")
                life=report["lives"][0]
                steps=life["steps"]
                if (not steps or len(steps)>200
                    or life["lifecycle"] not in ("active","dead")
                    or (life["lifecycle"]=="active" and len(steps)!=200)):
                    raise ValueError("invalid censor/death receipt")
                actions=Counter(x["action_primitive"] for x in steps)
                path=folder/life["custody_file"]
                if path.is_symlink() or not path.is_file():
                    raise ValueError("absent durable WAL")
                n=0;head=None;berry=Counter();events=Counter()
                with path.open("rb") as wal:
                    for line in wal:
                        item=json.loads(line);n+=1
                        if head is not None and item["previous_hash"]!=head:
                            raise ValueError("broken WAL link")
                        head=item["event_hash"]
                        ev=item["causal_event"];events[ev["kind"]]+=1
                        if ev["kind"]=="command_experienced" and ev["primitive"]=="manger":
                            berry[(ev.get("parameters") or {}).get("target")]+=1
                if n!=life["durable_entries"] or head!=life["journal_head"]:
                    raise ValueError("WAL mismatch")
                rows.append({
                    "source_sha":a.sha,"food_role":role,"learning_read":mode,
                    "seed":seed,"status":life["lifecycle"],"steps":len(steps),
                    "actions":sum(actions.values()),"move":actions["se_deplacer"],
                    "drink":actions["boire"],"collect":actions["collecter"],
                    "eat_a":berry["berry_a"],"eat_b":berry["berry_b"],
                    "helpful_eat":berry["berry_"+role],
                    "unhelpful_eat":berry["berry_"+("b" if role=="a" else "a")],
                    "sleep":actions["dormir"],
                    "td_updates":events["td_update_published"],
                    "final_food":steps[-1]["body"]["food"],
                    "final_water":steps[-1]["body"]["water"],
                    "final_integrity":steps[-1]["body"]["integrity"],
                })
    a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/"individuals.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    (a.output/"report.json").write_text(json.dumps({
        "schema":"i1-simple-learning-read-ablation/v1","source_sha":a.sha,
        "births":len(rows),"deaths":sum(x["status"]=="dead" for x in rows),
        "observed_steps":sum(x["steps"] for x in rows),
        "verdict":"NOT_ESTABLISHED_PENDING_CAUSAL_POSTEXPOSURE_REVIEW",
        "per_arm":{role+"-"+mode:[x for x in rows if x["food_role"]==role
            and x["learning_read"]==mode]
            for role in ("a","b") for mode in ("active","masked")},
    },indent=2)+"\n")
    print(json.dumps({"lives":len(rows),"observed_steps":sum(x["steps"] for x in rows),
                      "verdict":"NOT_ESTABLISHED_PENDING_CAUSAL_POSTEXPOSURE_REVIEW"}))
if __name__=="__main__":main()
