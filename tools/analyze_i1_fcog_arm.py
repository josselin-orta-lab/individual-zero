#!/usr/bin/env python3
"""Read-only scientific arm summary. No behavioral feedback or science GO."""
import argparse
from collections import Counter
from pathlib import Path
import json
import sys

def analyze(folder):
    report = json.loads((folder / "report.json").read_text())
    if (report.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or report.get("engine") != "I1"
            or report.get("run", {}).get("custody") != "wal"
            or not report["run"].get("git_head")
            or not report["lives"]):
        raise ValueError("invalid or incomplete prospective mortal cohort")
    weight = report["run"].get("experimental_fatigue_weight")
    if weight not in (0., .1, .2, .3):
        raise ValueError("nonregistered experimental arm")
    rows = []
    for life in report["lives"]:
        if life.get("effective_sleep_fatigue_weight") != weight:
            raise ValueError("birth weight mismatch")
        path = folder / life["custody_file"]
        if path.is_symlink() or not path.is_file():
            raise ValueError("durable individual WAL absent")
        records = [json.loads(line) for line in path.read_bytes().splitlines()]
        if (len(records) != life["durable_entries"]
                or not records or records[-1]["event_hash"] != life["journal_head"]):
            raise ValueError("WAL count or head mismatch")
        kinds = Counter(row["causal_event"].get("kind") for row in records)
        steps = life["steps"]
        if (not steps or len({r["causal_event"].get("t_monde") for r in records
               if r["causal_event"].get("kind") == "step_closed"}) != len(steps)):
            raise ValueError("world-step receipts mismatch")
        counts = Counter(step["action_primitive"] for step in steps
                         if step["execution"] in ("applied", "dead"))
        sleep_runs = []
        current_sleep = 0
        for step in steps:
            if step["execution"] in ("applied", "dead") and step["action_primitive"] == "dormir":
                current_sleep += 1
            elif current_sleep:
                sleep_runs.append(current_sleep)
                current_sleep = 0
        if current_sleep:
            sleep_runs.append(current_sleep)
        actions = sum(counts.values())
        row = {
            "life_id": life["individual_id"],
            "terminal_status": life["lifecycle"],
            "steps": len(steps),
            "actions": actions,
            "actions_per_step": actions / len(steps),
            "actions_by_primitive": dict(counts),
            "action_fractions_per_step": {a: n / len(steps) for a, n in counts.items()},
            "sleep_steps": counts["dormir"],
            "sleep_fraction": counts["dormir"] / len(steps),
            "sleep_contiguous_runs": sleep_runs,
            "stage10_committed_receipts": kinds["stage10_consolidation_committed"],
            "stage10_semantically_attributable": "NOT_ESTABLISHED",
            "learning_effect": "NOT_ESTABLISHED",
            "last_body": steps[-1]["body"],
            "final_inventory": steps[-1]["inventory"],
            "journal_head": life["journal_head"],
        }
        rows.append(row)
    return {
        "schema": "i1-fcog-prospective-arm/v1",
        "source_sha": report["run"]["git_head"],
        "world": report["source"]["preset"],
        "preset_sha256": report["source"]["sha256"],
        "seed": report["run"]["seed"],
        "weight": weight,
        "scientific_verdict": "NOT_ESTABLISHED",
        "not_evidence_of_causal_learning": True,
        "lives": rows,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = analyze(a.input)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"world": result["world"], "weight": result["weight"],
        "lives": len(result["lives"]), "steps": sum(x["steps"] for x in result["lives"])}))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as e:
        sys.exit("I1_PROSPECTIVE_AUDIT_FAILED: " + str(e))
