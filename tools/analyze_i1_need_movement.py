#!/usr/bin/env python3
"""External WAL diagnostic, not an individual's cognitive sensor."""
import argparse
from collections import Counter
import json
from pathlib import Path

def inspect(folder):
    report=json.loads((folder/"report.json").read_text())
    if report.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT" or len(report["lives"])!=1:
        raise ValueError("technical failure or invalid cohort size")
    run=report["run"]
    life=report["lives"][0]
    novelty=run["geographic_novelty_weight"]
    if life["effective_geographic_novelty_weight"]!=novelty:
        raise ValueError("newborn did not receive declared novelty weight")
    p=folder/life["custody_file"]
    if p.is_symlink() or not p.is_file():
        raise ValueError("missing durable WAL")
    counts=Counter()
    commands=Counter()
    visible_water=0
    water_cue_steps=set()
    proposed_steps=set()
    crossed_steps=set()
    chosen_move_steps=set()
    admission_refusals=0
    max_geo_accumulator_ratio=0.0
    last=None
    n=0
    with p.open("rb") as f:
        for raw in f:
            row=json.loads(raw)
            n+=1
            ev=row["causal_event"]
            kind=ev["kind"]
            counts[kind]+=1
            last=row["event_hash"]
            t=ev.get("t_monde")
            d=ev.get("data") or {}
            if kind=="perceptual_capture":
                near=d.get("agency_visible_adjacent") or []
                if any(x.get("water_source") and x.get("passable") for x in near):
                    water_cue_steps.add(t)
            elif kind=="stage11_geographic_option_proposed":
                proposed_steps.add(t)
            elif kind=="competition_cycle":
                for tr in d.get("traces",()):
                    if tr.get("option_ref","").startswith("option:geographic:"):
                        def num(v):
                            return float.fromhex(v["$f64"]) if isinstance(v,dict) else float(v)
                        threshold=num(tr["threshold"])
                        after=num(tr["accumulator_after"])
                        max_geo_accumulator_ratio=max(max_geo_accumulator_ratio,after/threshold)
                        if tr["crossed"]:
                            crossed_steps.add(t)
            elif kind=="command_experienced":
                commands[ev["primitive"]]+=1
                if ev["primitive"]=="se_deplacer":
                    chosen_move_steps.add(t)
            elif kind=="command_admission_refused":
                admission_refusals+=1
    if n!=life["durable_entries"] or last!=life["journal_head"]:
        raise ValueError("tampered/incomplete WAL head or length")
    if len(life["steps"])!=counts["step_closed"]:
        raise ValueError("physical steps not committed exactly once")
    return {
        "schema":"i1-need-movement-audit-v1",
        "source_sha":run["git_head"],
        "world":report["source"]["preset"],
        "layout_sha":report["source"]["sha256"],
        "seed":run["seed"],
        "world_variant":run["world_variant"],
        "weight":run["experimental_fatigue_weight"],
        "geographic_novelty_weight":novelty,
        "life":life["individual_id"],
        "lifecycle":life["lifecycle"],
        "physical_steps":len(life["steps"]),
        "physically_executed":dict(commands),
        "steps_visible_adjacent_water":len(water_cue_steps),
        "steps_with_geographic_proposals":len(proposed_steps),
        "steps_geographic_threshold_crossed":len(crossed_steps),
        "steps_actual_movement":len(chosen_move_steps),
        "admission_refusals":admission_refusals,
        "maximum_geographic_accumulator_ratio":max_geo_accumulator_ratio,
        "stage10_consolidation_receipts":counts["stage10_consolidation_committed"],
        "causal_learning":"NOT_ESTABLISHED",
        "WAL_head":last,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=inspect(a.input)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:result[key] for key in ("world","weight","geographic_novelty_weight","physical_steps","steps_actual_movement","lifecycle")}))
if __name__=="__main__":
    main()
