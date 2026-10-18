#!/usr/bin/env python3
"""Fail-closed external-only longitudinal evidence; no memory-learning oracle."""
from collections import Counter
from pathlib import Path
import argparse
import json

MEMORY_TYPES = ("stage10_consolidation_committed",
                "i1_private_procedure_recall_considered",
                "memory_recall_proposed")

def analyze(folder):
    report = json.loads((folder / "report.json").read_text())
    run = report["run"]
    if report.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT" or (
        run["custody"] != "wal" or not run.get("git_head") or not report["lives"]
    ):
        raise ValueError("no completed authenticated WAL study")
    if run.get("world_variant") != report["source"].get("world_variant"):
        raise ValueError("world variation mismatch")
    result = {"schema":"i1-longlife-v1", "source_sha":run["git_head"],
              "world":report["source"]["preset"],
              "layout_hash":report["source"]["sha256"],
              "variant":run["world_variant"], "seed":run["seed"],
              "weight":run["experimental_fatigue_weight"],
              "scientific_verdict":"NOT_ESTABLISHED", "lives":[]}
    for life in report["lives"]:
        if life["effective_sleep_fatigue_weight"] != result["weight"]:
            raise ValueError("actual birth fatigue mismatch")
        p = folder / life["custody_file"]
        if p.is_symlink() or not p.is_file():
            raise ValueError("missing mortal WAL")
        rows = [json.loads(x) for x in p.read_bytes().splitlines()]
        if (len(rows) != life["durable_entries"] or not rows or
            rows[-1]["event_hash"] != life["journal_head"]):
            raise ValueError("WAL audit count/head differs")
        steps = life["steps"]
        if not steps or len({row["causal_event"]["t_monde"]
              for row in rows if row["causal_event"]["kind"]=="step_closed"}) != len(steps):
            raise ValueError("physical closed-step mismatch")
        kinds = Counter(x["causal_event"]["kind"] for x in rows)
        bins=[]
        for i in range(0,len(steps),50):
            chunk=steps[i:i+50]
            counts=Counter(x["action_primitive"] for x in chunk
                           if x["execution"] in ("applied","dead"))
            bins.append({"from":i+1,"to":i+len(chunk),"steps":len(chunk),
                 "actions":sum(counts.values()),"actions_by_type":dict(counts),
                 "sleep_fraction":counts["dormir"]/len(chunk),
                 "effective_action_fraction":sum(v for k,v in counts.items()
                    if k not in ("dormir","attendre"))/len(chunk),
                 "water_min":min(x["body"]["water"] for x in chunk),
                 "food_min":min(x["body"]["food"] for x in chunk),
                 "water_zero_steps":sum(x["body"]["water"]<=0 for x in chunk)})
        events=[]
        for item in rows:
            ev=item["causal_event"]
            if ev["kind"] in MEMORY_TYPES:
                events.append({"kind":ev["kind"],"event_ref":item["event_id"],
                               "t_monde":ev["t_monde"]})
        result["lives"].append({"id":life["individual_id"],"status":life["lifecycle"],
             "steps":len(steps),"right_censored":life["lifecycle"]=="active",
             "effective_weight":life["effective_sleep_fatigue_weight"],
             "memory_events":events,"bins":bins,"journal_head":life["journal_head"],
             "attributable_learning":"NOT_ESTABLISHED",
             "semantic_retention":"NOT_ESTABLISHED"})
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=analyze(a.input)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"sha":result["source_sha"],"world":result["world"],
        "variant":result["variant"],"weight":result["weight"],
        "births":len(result["lives"]),
        "steps":sum(x["steps"] for x in result["lives"]),
        "status":"ANALYZED_NO_LEARNING_VERDICT"}))
if __name__=="__main__":
    main()
