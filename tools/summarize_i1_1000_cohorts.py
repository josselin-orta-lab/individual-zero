#!/usr/bin/env python3
"""Postmortem-only, fail-closed paired analysis of independent 1000-step I1 lives."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

WORLDS = ("oasis", "foraging", "dry-valley", "blocked-route", "longlife-garden")
WEIGHTS = (0.0, 0.1, 0.2, 0.65)
HORIZON = 1000


def aggregate(directory, *, variants=2, variant_start=1, expected_sha=None):
    if variants < 1 or variant_start < 1:
        raise ValueError("invalid declared environment range")
    expected = {(world, w, v) for world in WORLDS for w in WEIGHTS
                for v in range(variant_start, variant_start + variants)}
    paths = sorted(directory.rglob("science-summary.json"))
    if len(paths) != len(expected):
        raise ValueError("incomplete factorial: expected %d, observed %d" %
                         (len(expected), len(paths)))
    known = {}
    pairing = defaultdict(set)
    seed_pair = defaultdict(set)
    commit_shas = set()
    individuals = []
    bins = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != "i1-longlife-v1":
            raise ValueError("unexpected observer schema")
        world, weight, variant = (data["world"], float(data["weight"]), data["variant"])
        key = (world, weight, variant)
        if key not in expected or key in known or len(data["lives"]) != 1:
            raise ValueError("duplicate/unregistered arm or birth")
        known[key] = True
        commit_shas.add(data["source_sha"])
        pairing[(world, variant)].add(data["layout_hash"])
        seed_pair[(world, variant)].add(data["seed"])
        life = data["lives"][0]
        if life.get("attributable_learning") != "NOT_ESTABLISHED" or (
            life.get("semantic_retention") != "NOT_ESTABLISHED"
            or data.get("scientific_verdict") != "NOT_ESTABLISHED"
        ):
            raise ValueError("observer cannot claim causal memory success")
        steps = life["steps"]
        if not 1 <= steps <= HORIZON or life["effective_weight"] != weight:
            raise ValueError("invalid horizon/effective sleep pressure")
        status = life["status"]
        if status not in ("dead", "active"):
            raise ValueError("invalid terminal life state")
        if bool(life["right_censored"]) != (status == "active") or (
            status == "active" and steps != HORIZON
        ):
            raise ValueError("active individual must be right censored at 1000")
        if not life.get("journal_head"):
            raise ValueError("missing validated chained WAL head")
        partitions = life["bins"]
        if not partitions or sum(item["steps"] for item in partitions) != steps:
            raise ValueError("missing physical longitudinal steps")
        acts = Counter()
        sleep = 0
        for index, chunk in enumerate(partitions, start=1):
            counter = Counter(chunk["actions_by_type"])
            if counter.total() != chunk["actions"]:
                raise ValueError("bin action totals inconsistent")
            acts.update(counter)
            sleep += counter["dormir"]
            bins.append({
                "world":world,"weight":weight,"variant":variant,"bin":index,
                "end_step":chunk["to"],"exposed_steps":chunk["steps"],
                "sleep_steps":counter["dormir"],
                "other_action_steps":sum(n for k,n in counter.items()
                                        if k not in ("dormir", "attendre")),
                "water_zero_steps":chunk["water_zero_steps"],
            })
        mem = Counter(e["kind"] for e in life["memory_events"])
        individuals.append({
            "world":world,"weight":weight,"variant":variant,
            "seed":data["seed"],"life_id":life["id"],
            "layout_sha256":data["layout_hash"],
            "terminal_status":status,"right_censored":status=="active",
            "steps":steps,"applied_actions":acts.total(),
            "actions_per_step":acts.total()/steps,
            "sleep_steps":sleep,"sleep_fraction_observed":sleep/steps,
            "wait_steps":acts["attendre"],"drink_steps":acts["boire"],
            "eat_steps":acts["manger"],"collect_steps":acts["collecter"],
            "move_steps":acts["se_deplacer"],
            "stage10_technical_commits":mem["stage10_consolidation_committed"],
            "private_recall_considered":mem["i1_private_procedure_recall_considered"],
            "memory_proposed":mem["memory_recall_proposed"],
            "critical_zero_water_steps":sum(i["water_zero_steps"] for i in partitions),
            "last_wal_hash":life["journal_head"],
        })
    if set(known) != expected or len(commit_shas) != 1:
        raise ValueError("non-paired arms or mixed engine commits")
    if any(len(x)!=1 for x in pairing.values()) or (
        any(len(x)!=1 for x in seed_pair.values())
    ):
        raise ValueError("paired world layout and temperament seed changed")
    sha = commit_shas.pop()
    if expected_sha is not None and sha != expected_sha:
        raise ValueError("source SHA disagrees with physical GitHub run")
    strata = []
    for world in WORLDS:
        for weight in WEIGHTS:
            group = [x for x in individuals
                     if x["world"] == world and x["weight"] == weight]
            observed_steps = sum(x["steps"] for x in group)
            strata.append({
                "world":world,"weight":weight,"births":len(group),
                "deaths":sum(x["terminal_status"]=="dead" for x in group),
                "censored_at_1000":sum(x["right_censored"] for x in group),
                "observed_steps":observed_steps,
                "pooled_sleep_fraction_observed":(
                    sum(x["sleep_steps"] for x in group)/observed_steps),
                "nonrest_actions_per_step":sum(
                    x["applied_actions"]-x["sleep_steps"]-x["wait_steps"]
                    for x in group)/observed_steps,
                "technical_consolidation_receipts":sum(
                    x["stage10_technical_commits"] for x in group),
                "recall_considered":sum(x["private_recall_considered"] for x in group),
                "attributable_learning":"NOT_ESTABLISHED",
            })
    trajectories = []
    for world in WORLDS:
        for weight in WEIGHTS:
            for i in range(1, 21):
                rows = [x for x in bins if x["world"]==world and
                        x["weight"]==weight and x["bin"]==i]
                if not rows:
                    continue
                exposure = sum(x["exposed_steps"] for x in rows)
                trajectories.append({
                    "world":world,"weight":weight,"end_step":min(50*i,1000),
                    "initial_births":variants,"exposed_lives":len(rows),
                    "observed_steps":exposure,
                    "sleep_fraction_observed":sum(x["sleep_steps"]
                                                   for x in rows)/exposure,
                    "nonrest_action_fraction_observed":sum(
                        x["other_action_steps"] for x in rows)/exposure,
                    "water_zero_fraction_observed":sum(
                        x["water_zero_steps"] for x in rows)/exposure,
                })
    return {"schema":"i1-longlife-1000-report/v1",
            "source_sha":sha,"horizon":1000,"variants":variants,
            "variant_start":variant_start,"births":len(individuals),
            "simulated_steps":sum(x["steps"] for x in individuals),
            "deaths":sum(x["terminal_status"]=="dead" for x in individuals),
            "censored":sum(x["right_censored"] for x in individuals),
            "scientific_verdict":"INCONCLUSIVE_PENDING_CAUSAL_LEARNING_AND_POWER",
            "individuals":individuals,"strata":strata,"trajectories":trajectories}


def write_csv(path, rows):
    if not rows:
        raise ValueError("empty science table")
    with path.open("w",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def save(result, folder):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"report.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(folder/"individuals.csv",result["individuals"])
    write_csv(folder/"strata.csv",result["strata"])
    write_csv(folder/"longitudinal_50steps.csv",result["trajectories"])
    lines=["# Campagne I1 : 1 000 pas par vie (maximum)","",
           "SHA physique : "+result["source_sha"],"",
           "%d vies, %d pas effectifs, %d morts, %d vies censurées à 1 000."%(
           result["births"],result["simulated_steps"],
           result["deaths"],result["censored"]),"",
           "| Monde | w_F | Naissances | Morts | Censurés à 1 000 | Sommeil (pas observés) | Stage10 commits |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for row in result["strata"]:
        lines.append("| %s | %.2f | %d | %d | %d | %.1f%% | %d |"%(
            row["world"],row["weight"],row["births"],row["deaths"],
            row["censored_at_1000"],
            100*row["pooled_sleep_fraction_observed"],
            row["technical_consolidation_receipts"]))
    lines.extend(["","**Verdict : INCONCLUSIVE.** Les commits Stage10 et les",
        "changements de fréquence d'actions ne prouvent pas un apprentissage.",
        "Ce petit échantillon ne valide ni une non-infériorité de survie ni",
        "un choix optimal du coefficient. Les morts restent dans la population initiale.",
        ""])
    (folder/"report.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--variants",type=int,default=2)
    p.add_argument("--variant-start",type=int,default=1)
    p.add_argument("--sha",required=True)
    a=p.parse_args()
    result=aggregate(a.input,variants=a.variants,variant_start=a.variant_start,
                     expected_sha=a.sha)
    save(result,a.output)
    print(json.dumps({"births":result["births"],"steps":result["simulated_steps"],
                      "deaths":result["deaths"],"status":result["scientific_verdict"]}))


if __name__=="__main__":
    main()
