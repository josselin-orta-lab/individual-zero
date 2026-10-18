#!/usr/bin/env python3
"""Read-only operator analysis of immutable WAL and passive lived-step receipts."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import argparse

SUBJECT = "0972b58040285a0ae3931f3fd6fae03d94830c10"
PRESETS = ("oasis","foraging","dry-valley","empty-land","hazard-edge","blocked-route")
CATEGORIES = {
    "se_deplacer":"movement","collecter":"collection",
    "manger":"eating","boire":"drinking",
    "dormir":"sleep","attendre":"waiting",
    "poser_une_pierre":"construction","fabriquer_outil":"toolmaking",
}
def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def observe(folder):
    report=json.loads((folder/"report.json").read_text(encoding="utf-8"))
    if (report.get("engine")!="I1" or report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or report.get("run",{}).get("git_head")!=SUBJECT
            or report.get("run",{}).get("custody")!="wal"):
        raise ValueError("unexpected scientific subject or incomplete WAL evidence: "+str(folder))
    if len(report["lives"])!=3 or report["source"]["preset"]!=folder.name:
        raise ValueError("unexpected preset or life count: "+str(folder))
    actions, physio, stage10, summaries=[],[],[],[]
    for life in report["lives"]:
        wal=folder/life["custody_file"]
        if not wal.is_file() or wal.is_symlink():raise ValueError("invalid WAL path")
        records=[json.loads(line) for line in wal.read_bytes().splitlines()]
        if len(records)!=life["durable_entries"] or not records or records[-1]["event_hash"]!=life["journal_head"]:
            raise ValueError("unauthenticated WAL count/head")
        for i, rec in enumerate(records):
            if rec["index"]!=i or rec["previous_hash"]!=("00"*32 if i==0 else records[i-1]["event_hash"]):
                raise ValueError("broken event chain linkage")
        kinds=Counter(row["causal_event"].get("kind") for row in records)
        closed={row["causal_event"].get("t_monde") for row in records
                if row["causal_event"].get("kind")=="step_closed"}
        if len(closed)!=len(life["steps"]):
            raise ValueError("closed-world steps disagree with operator receipts")
        commands=defaultdict(list)
        for row in records:
            ev=row["causal_event"]
            if ev.get("kind")=="command_experienced":
                commands[ev.get("t_monde")].append(ev.get("primitive"))
            if str(ev.get("kind","")).startswith("stage10_"):
                stage10.append({"preset":folder.name,"life_id":life["individual_id"],
                                "world_step":ev.get("t_monde"),"event_kind":ev["kind"],"event_id":row["event_id"]})
        counters=Counter()
        with_action=set()
        steps=life["steps"]
        seen_steps=set()
        for step in steps:
            time=step["world_step"]
            if time in seen_steps: raise ValueError("duplicate step receipt")
            seen_steps.add(time)
            primitive=step.get("action_primitive")
            executed=step["execution"] in ("applied","dead")
            if executed and (not isinstance(primitive,str) or primitive not in commands.get(time,())):
                raise ValueError("operator action is not supported by WAL command")
            if executed:
                counters[primitive]+=1
                with_action.add(time)
            actions.append({"preset":folder.name,"life_id":life["individual_id"],"step":time,
                            "primitive":primitive,"category":CATEGORIES.get(primitive, "other") if primitive else "none",
                            "source":step.get("action_source"),"execution":step["execution"],
                            "applied":int(executed),"reflex_triggered":int(step.get("reflex_triggered",False)),
                            "fallback_used":int(step.get("fallback_used",False)),"cycles_used":step.get("cycles_used")})
            physio.append({"preset":folder.name,"life_id":life["individual_id"],"step":time,
                           "body_json":json.dumps(step["body"],sort_keys=True),
                           "position_json":json.dumps(step["position"],sort_keys=True),
                           "inventory_json":json.dumps(step["inventory"],sort_keys=True)})
        n=len(steps);num=sum(counters.values())
        summaries.append({
            "preset":folder.name,"life_id":life["individual_id"],"steps":n,
            "life_status":life["lifecycle"],"applied_actions":num,
            "applied_actions_per_step":(round(num/n,5) if n else None),
            "steps_without_applied_action":n-len(with_action),
            "primitive_counts":dict(sorted(counters.items())),
            "primitive_percentage_of_actions":{k:round(100*v/num,3) for k,v in sorted(counters.items())} if num else {},
            "primitive_frequency_per_100_steps":{k:round(100*v/n,3) for k,v in sorted(counters.items())} if n else {},
            "stage10_events":{k:v for k,v in kinds.items() if str(k).startswith("stage10_")},
            "semantic_owner_delta":"NOT_OBSERVED",
            "first_person_learning":"NOT_OBSERVED",
        })
    return actions,physio,stage10,summaries

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    aa,pp,ss,ll=[],[],[],[]
    for preset in PRESETS:
        a,p,s,l=observe(args.root/preset)
        aa+=a;pp+=p;ss+=s;ll+=l
    if len(ll)!=18:raise ValueError("incomplete pilot")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    write_csv(args.output_dir/"actions_by_step.csv",
              ["preset","life_id","step","primitive","category","source","execution","applied",
               "reflex_triggered","fallback_used","cycles_used"],aa)
    write_csv(args.output_dir/"physiology_by_step.csv",
              ["preset","life_id","step","body_json","position_json","inventory_json"],pp)
    write_csv(args.output_dir/"stage10_events.csv",
              ["preset","life_id","world_step","event_kind","event_id"],ss)
    aggregate={}
    for preset in PRESETS:
        rows=[r for r in ll if r["preset"]==preset]
        n=sum(r["steps"] for r in rows)
        counts=Counter()
        for r in rows:counts.update(r["primitive_counts"])
        aggregate[preset]={
            "lives":len(rows),"observed_steps":n,
            "applied_actions":sum(counts.values()),
            "pooled_actions_per_step":round(sum(counts.values())/n,5) if n else None,
            "mean_of_per_life_ratios":round(sum(r["applied_actions_per_step"] for r in rows if r["applied_actions_per_step"] is not None)/len(rows),5) if rows and all(r["applied_actions_per_step"] is not None for r in rows) else None,
            "primitive_distribution_pct":{k:round(100*v/sum(counts.values()),3) for k,v in sorted(counts.items())} if counts else {},
        }
    obj={"schema":"individual-zero-i1-s1-corrected-pilot-v2",
         "subject_sha":SUBJECT,"status":"DESCRIPTIVE_ONLY",
         "lives":ll,"aggregate_by_preset":aggregate,
         "semantic_consolidation":"NOT_OBSERVED","learning":"NOT_OBSERVED",
         "scientific_gate":"NOT_EVALUATED"}
    (args.output_dir/"summary.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":obj["status"],"lives":len(ll),"steps":len(aa),"subject_sha":SUBJECT}))

if __name__=="__main__":
    main()
