#!/usr/bin/env python3
"""External, read-only I1 pilot observations from authenticated WAL/report pairs.

Never imports an active runtime or mutates cognition. Missing evidence is NOT_OBSERVED.
The world truth in report.json is operator-only and is not included in output.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json

STEP = "step_closed"
COMMAND = "command_experienced"
TRANSITION = "world_transition_experienced"
STAGE10 = (
    "stage10_sleep_entered",
    "stage10_consolidation_batch_frozen",
    "stage10_consolidation_pass_checkpointed",
    "stage10_consolidation_work_deferred",
    "stage10_consolidation_publication_deferred",
    "stage10_consolidation_committed",
)

def life_observations(folder: Path):
    report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    if report.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT" or report.get("run", {}).get("custody") != "wal" or report.get("engine") != "I1":
        raise ValueError("incomplete or non-WAL I1 report")
    result = []
    for life in report["lives"]:
        path = folder / life["custody_file"]
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing or symlinked durable WAL")
        commands, transitions, closed = defaultdict(list), defaultdict(list), set()
        stages = Counter()
        observed_ids = set()
        head = "00" * 32
        count = 0
        for line in path.read_bytes().splitlines():
            occurrence = json.loads(line)
            if occurrence.get("index") != count or occurrence.get("previous_hash") != head:
                raise ValueError("WAL occurrence ordering/chain linkage mismatch")
            event_id = occurrence["event_id"]
            if event_id in observed_ids:
                raise ValueError("duplicated technical occurrence")
            observed_ids.add(event_id)
            head = occurrence["event_hash"]
            count += 1
            event = occurrence["causal_event"]
            kind = event.get("kind")
            key = (event.get("t_monde"), event.get("attempt_ref"))
            if kind == COMMAND:
                commands[key].append(event)
            if kind == TRANSITION:
                transitions[key].append(event)
            if kind == STEP:
                closed.add(key)
            if kind in STAGE10:
                stages[kind] += 1
        if head != life["journal_head"] or count != life["durable_entries"]:
            raise ValueError("WAL differs from authenticated runner report")
        if len(closed) != len(life["steps"]):
            raise ValueError("closed steps disagree with runner")
        verified = []
        ambiguous = 0
        for key, transitions_at_step in transitions.items():
            commands_at_step = commands.get(key, ())
            if key not in closed or len(transitions_at_step) != 1 or len(commands_at_step) != 1:
                ambiguous += 1
            else:
                verified.append((key, commands_at_step[0]["primitive"]))
        tally = Counter(primitive for _key, primitive in verified)
        total = sum(tally.values())
        denominator = len(closed)
        per_step = {
            primitive: round(len({key for key, action in verified if action == primitive}) * 100 / denominator, 3)
            for primitive in sorted(tally)
        } if denominator else {}
        result.append({
            "life_id": life["individual_id"],
            "source_preset": report["source"]["preset"],
            "preset_sha256": report["source"]["sha256"],
            "git_head": report["run"]["git_head"],
            "seed": report["run"]["seed"],
            "steps": denominator,
            "death_observed": life["lifecycle"] == "dead",
            "physically_matched_commands": total,
            "action_per_step": (round(total / denominator, 5) if denominator else None),
            "primitive_counts": dict(sorted(tally.items())),
            "primitive_share_percent": {p: round(n * 100 / total, 3) for p,n in sorted(tally.items())} if total else {},
            "steps_with_primitive_percent": per_step,
            "ambiguous_transition_count": ambiguous,
            "stage10_event_counts": dict(sorted(stages.items())),
            "stage10_nonempty_owner_publication": "NOT_OBSERVED",
            "learning_attributable_to_owned_change": "NOT_OBSERVED",
            "cognitive_uc_by_step": "NOT_OBSERVED",
            "scientific_gate": "NOT_EVALUATED",
        })
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    folders = sorted(p for p in args.root.iterdir() if p.is_dir() and (p / "report.json").is_file())
    if len(folders) != 6:
        raise ValueError("expected six registered pilot scenario directories")
    rows = [row for folder in folders for row in life_observations(folder)]
    if len(rows) != 18:
        raise ValueError("expected exactly 18 pilot newborn lives")
    output = {
        "schema": "individual-zero-i1-science-s1-pilot/v1",
        "phase": "PILOT_DESCRIPTIVE_ONLY",
        "source_commit": "f87cbc15a34f9b0f2a43749bb2b3377a45401b84",
        "lives": rows,
        "status": "OBSERVED_TECHNICAL_WAL_METRICS_ONLY",
        "scientific_gate": "NOT_EVALUATED",
        "nonempty_stage10_publication": "NOT_OBSERVED",
        "first_person_learning": "NOT_OBSERVED"
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status":output["status"], "lives":len(rows), "output":str(args.output)}))

if __name__ == "__main__":
    main()
