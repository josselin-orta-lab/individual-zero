#!/usr/bin/env python3
"""External WAL audit of real berry_b ingestion and subsequent learned choices.

Counts observed experiences, not imagined rewards or inferred avoidance.
Never imports the motor runtime, changes a life, or restarts a dead individual.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json


def numeric(value):
    if type(value) in (int, float):
        return float(value)
    if isinstance(value, dict) and set(value) == {"$f64"}:
        return float.fromhex(value["$f64"])
    raise ValueError("unrecognized causal float")


def _berry_target(event):
    if event.get("primitive") != "manger":
        return None
    return (event.get("parameters") or {}).get("target")


def audit(folder):
    report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    if (report.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or report.get("engine") != "I1"
            or report.get("run", {}).get("custody") != "wal"
            or len(report.get("lives", [])) != 1):
        raise ValueError("incomplete or non-I1 WAL cohort")
    run, life = report["run"], report["lives"][0]
    weight = run.get("experimental_berry_b_damage")
    if weight not in (-100.0, -10.0, 0.0):
        raise ValueError("unregistered toxicity arm")
    if life["effective_berry_b_damage"] != weight:
        raise ValueError("actual birth toxicity differs from declared arm")
    relative = Path(life["custody_file"])
    if relative.is_absolute() or relative.name != str(relative):
        raise ValueError("unsafe WAL path")
    file = folder / relative
    if file.is_symlink() or not file.is_file():
        raise ValueError("durable identity WAL absent")
    observed = {}
    commands = {}
    aftermath = {}
    proposals = defaultdict(list)
    value_updates = defaultdict(list)
    closed = set()
    kind_counts = Counter()
    n = 0
    previous = None
    last = None
    with file.open("rb") as stream:
        for line in stream:
            entry = json.loads(line)
            event = entry["causal_event"]
            n += 1
            if previous is not None and entry["previous_hash"] != previous:
                raise ValueError("WAL hash links not contiguous")
            previous = entry["event_hash"]
            last = previous
            kind = event["kind"]
            t = event.get("t_monde")
            kind_counts[kind] += 1
            if kind == "perceptual_capture":
                observed[t] = event["data"]
            elif kind == "command_experienced":
                if t in commands:
                    raise ValueError("multiple physical commands in one world step")
                commands[t] = event
            elif kind == "world_transition_experienced":
                aftermath[t] = event
            elif kind == "i1_unknown_affordance_proposed":
                data = event.get("data") or {}
                command = data.get("command") or {}
                if command.get("primitive") == "manger" and (
                    (command.get("parameters") or {}).get("target") == "berry_b"
                ):
                    proposals[t].append({
                        "goal_ref": data.get("goal_ref"),
                        "option_ref": data.get("option_ref"),
                        "learned_status": data.get("learned_value_status"),
                        "learned_value": data.get("learned_value"),
                        "prior_evidence": data.get("prior_evidence"),
                    })
            elif kind == "td_update_published":
                data = event.get("data") or {}
                if any("manger:target=berry_b" in x
                       for x in data.get("updated_signatures", [])):
                    value_updates[t].append(entry["event_id"])
            elif kind == "step_closed":
                if t in closed:
                    raise ValueError("duplicate closed world step")
                closed.add(t)
    if (n != life["durable_entries"] or last != life["journal_head"]
            or len(closed) != len(life["steps"])):
        raise ValueError("mortal WAL count/ending/step receipt mismatch")

    berry = []
    for t in sorted(commands):
        e = commands[t]
        if _berry_target(e) != "berry_b":
            continue
        if t not in aftermath:
            raise ValueError("ingestion has no physical world consequence")
        after = aftermath[t]
        pre = observed.get(t, {}).get("dual_scope_visible_body") or {}
        before_integrity = numeric(pre["integrity"]) if "integrity" in pre else None
        after_integrity = numeric(after["body_after"]["integrity"])
        berry.append({
            "t_monde": t,
            "integrity_before_observed": before_integrity,
            "integrity_after": after_integrity,
            "observed_integrity_delta": (
                after_integrity - before_integrity
                if before_integrity is not None else None
            ),
            "transition_effects": after.get("effects", {}),
            "alive_after_step": not any(
                x["world_step"] == t and x["execution"] == "dead"
                for x in life["steps"]
            ),
        })
    first = berry[0]["t_monde"] if berry else None
    conditional = {
        "perceived_inventory_at_subsequent_steps": 0,
        "separate_steps_with_eat_berry_b_proposal": 0,
        "later_eat_berry_b_actions": 0,
        "later_td_updates_referencing_berry_b": 0,
    }
    if first is not None:
        conditional["perceived_inventory_at_subsequent_steps"] = sum(
            t > first and (x.get("agency_visible_inventory") or {}).get("berry_b", 0) > 0
            for t, x in observed.items()
        )
        conditional["separate_steps_with_eat_berry_b_proposal"] = sum(
            t > first and bool(rows) for t, rows in proposals.items()
        )
        conditional["later_eat_berry_b_actions"] = sum(
            t > first and _berry_target(x) == "berry_b"
            for t, x in commands.items()
        )
        conditional["later_td_updates_referencing_berry_b"] = sum(
            len(rows) for t, rows in value_updates.items() if t > first
        )
    return {
        "schema": "i1-berry-toxic-experience-v1",
        "source_sha": run["git_head"],
        "world": report["source"]["preset"],
        "layout_sha256": report["source"]["sha256"],
        "variant": run["world_variant"],
        "seed": run["seed"],
        "life_id": life["individual_id"],
        "terminal_status": life["lifecycle"],
        "observed_steps": len(life["steps"]),
        "declared_and_effective_integrity_damage": weight,
        "first_ingestion": berry[0] if berry else None,
        "all_ingestions": berry,
        "subsequent_observable_opportunities": conditional,
        "eat_berry_b_option_proposal_steps": len(proposals),
        "total_eat_berry_b_proposals": sum(map(len, proposals.values())),
        "td_updates_referencing_berry_b": sum(map(len, value_updates.values())),
        "consolidation_committed_receipts": kind_counts["stage10_consolidation_committed"],
        "causal_avoidance_from_lived_negative_experience": "NOT_ESTABLISHED",
        "why_no_verdict": (
            "NO_FIRST_INGESTION" if first is None
            else "NO_COMPARABLE_COUNTERFACTUAL_ATTRIBUTION"
        ),
        "durable_wal_head": last,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.input)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "world": result["world"],
        "variant": result["variant"],
        "damage": result["declared_and_effective_integrity_damage"],
        "steps": result["observed_steps"],
        "ingestions": len(result["all_ingestions"]),
        "opportunities_after_ingestion": result["subsequent_observable_opportunities"],
        "status": result["why_no_verdict"],
    }))


if __name__ == "__main__":
    main()
