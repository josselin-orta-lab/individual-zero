#!/usr/bin/env python3
"""Offline, read-only summarizer for I1 world-preset reports.

No simulation, import of a living engine, SQLite write, or privileged map
publication. Unknown cognitive variables are explicitly NOT_OBSERVED.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

KNOWN = {"schema", "engine", "model", "source", "run", "scientific_gate",
         "old_cohorts_used_as_oracles", "lives", "status", "environment"}
FIELDS = ("energy", "food", "water", "integrity")


def inspect(path: Path) -> dict:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 8_000_000:
        raise ValueError("expected finite, non-symlink I1 world report")
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("schema") != "individual-zero-i1-world-run/v1"
            or data.get("engine") != "I1" or data.get("scientific_gate") != "NOT_EVALUATED"
            or data.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or data.get("old_cohorts_used_as_oracles") is not False
            or not isinstance(data.get("lives"), list) or not data["lives"]):
        raise ValueError("unsupported, incomplete or scientifically misclassified report")
    source = data.get("source")
    run = data.get("run")
    if (not isinstance(source, dict) or not isinstance(source.get("preset"), str)
            or not isinstance(source.get("sha256"), str)
            or len(source["sha256"]) != 64 or not isinstance(run, dict)
            or run.get("custody") not in ("wal", "m11")
            or type(run.get("seed")) is not int):
        raise ValueError("report provenance is incomplete")
    result = []
    for life in data["lives"]:
        if (not isinstance(life, dict) or not isinstance(life.get("individual_id"), str)
                or not isinstance(life.get("steps"), list) or not life["steps"]
                or life.get("lifecycle") not in ("active", "dead")
                or not isinstance(life.get("journal_head"), str)):
            raise ValueError("invalid individual evidence")
        entries = life["steps"]
        last = entries[-1]
        if not isinstance(last, dict) or type(last.get("world_step")) is not int:
            raise ValueError("invalid physical step evidence")
        row = {
            "id": life["individual_id"],
            "lifecycle": life["lifecycle"],
            "observed_step_count": len(entries),
            "last_world_step": last["world_step"],
            "journal_head": life["journal_head"],
            "physical_state": "NOT_OBSERVED",
            "physical_delta": "NOT_OBSERVED",
        }
        if run["custody"] == "wal":
            first = entries[0]
            if all(isinstance(first.get("body"), dict) and
                   isinstance(last.get("body"), dict) and
                   all(type(first["body"].get(k)) in (int, float) and
                       type(last["body"].get(k)) in (int, float)
                       for k in FIELDS) for _ in [0]):
                row["physical_state"] = {k: last["body"][k] for k in FIELDS}
                row["physical_delta"] = {
                    k: last["body"][k] - first["body"][k] for k in FIELDS
                }
        result.append(row)
    return {
        "schema": "individual-zero-i1-observation-summary/v1",
        "source_preset": source["preset"],
        "source_sha256": source["sha256"],
        "custody": run["custody"],
        "seed": run["seed"],
        "lives": result,
        "external_world_truth": "REDACTED",
        "cognition": {
            "needs_arbitration": "NOT_OBSERVED",
            "goal_selection": "NOT_OBSERVED",
            "option_competition": "NOT_OBSERVED",
            "uc_expenditure": "NOT_OBSERVED",
            "first_person_learning": "NOT_OBSERVED",
            "stage10_nonempty_publication": "NOT_OBSERVED",
            "subjective_agency": "NOT_OBSERVED",
        },
        "scientific_gate": "NOT_EVALUATED",
        "mutates_individual": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    opts = ap.parse_args()
    try:
        result = inspect(opts.report)
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if opts.output:
            if opts.output.resolve() == opts.report.resolve():
                raise ValueError("cannot overwrite source report")
            if opts.output.exists():
                raise FileExistsError("refusing to overwrite existing summary")
            opts.output.parent.mkdir(parents=True, exist_ok=True)
            opts.output.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("I1 observation summary rejected: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
