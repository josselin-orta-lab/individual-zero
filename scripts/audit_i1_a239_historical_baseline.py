"""A2.39 retrospective *diagnostic* comparator. This never spawns A2.39 lives.

Consumes the independent archived A2.38 lives.jsonl; never trains I1 or
relabels previously observed cases as prospective evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

EXPECTED_SOURCE = "91c9f925b584cbd2b233619f38105b8607f666ae"

def summarize(path: Path) -> dict:
    records = [json.loads(line) for line in path.read_text().splitlines()]
    if len(records) != 160 or len({r["life_id"] for r in records}) != 160:
        raise ValueError("A2.38 historical archive is incomplete")
    if any(r["source_sha"] != EXPECTED_SOURCE for r in records):
        raise ValueError("not the original frozen A2.38 cohort")
    counts = Counter(step["command"] for record in records for step in record["steps"])
    observed = {
        "schema": "a239-historical-diagnostic-not-new-cohort-v1",
        "a238_source_sha": EXPECTED_SOURCE,
        "historical_births": len(records),
        "historical_deaths": sum(bool(r["fatal"]) for r in records),
        "historical_physical_steps": sum(r["physical_steps"] for r in records),
        "commands": dict(sorted(counts.items())),
        "lives_with_berry_collection": sum(bool(r["physical_collection"]) for r in records),
        "lives_with_food_gain": sum(bool(r["physical_food_gain"]) for r in records),
        "lives_with_water_gain": sum(bool(r["physical_water_gain"]) for r in records),
        "a239_births": 0,
        "claims": "A2.38 historical behavior motivates but cannot confirm A2.39 hypotheses"
    }
    return observed

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a238-lives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.a238_lives)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
