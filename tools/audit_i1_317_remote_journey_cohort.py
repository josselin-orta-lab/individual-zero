"""#317: independently authenticate and pair physical remote-return journeys.

The sealed WAL is read as evidence and never changed. This is a read-only
scientific analysis, not an actor, a reward function, or a movement oracle.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from audit_i1_spatial_navigation_314 import audit as audit_wal

KEYS = (1141, 1142, 2027, 2028)


def cohort(root: Path, *, sha: str) -> dict[int, dict]:
    rows = {}
    for path in sorted(root.rglob("report.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        life = report["lives"]
        if (report["engine"] != "I1"
            or report["run"]["git_head"] != sha
            or report["source"]["preset"] != "memory-corridor"
            or report["run"]["requested_steps"] != 300
            or report["run"]["requested_lives"] != 1
            or report["run"]["custody"] != "wal"
            or report["old_cohorts_used_as_oracles"] is not False
            or len(life) != 1):
            raise ValueError("mismatched or unsealed experimental report")
        seed = report["run"]["seed"]
        if type(seed) is not int or seed not in KEYS or seed in rows:
            raise ValueError("missing/duplicate/alien experimental seed")
        one = life[0]
        if (one["individual_id"] != f"i1:preset:memory-corridor:{seed}:0"
            or one["custody_file"] != "life-01.wal"
            or one["lifecycle"] not in ("active", "dead")
            or not (1 <= len(one["steps"]) <= 300)
            or (one["lifecycle"] == "active" and len(one["steps"]) != 300)
            or one["steps"][-1]["journal_head"] != one["journal_head"]):
            raise ValueError("life report does not match a mortal step history")
        wal = path.parent / one["custody_file"]
        verified = audit_wal(wal)
        if (verified["independent_hash_chain_verified"] is not True
            or verified["journal_head"] != one["journal_head"]
            or verified["journal_entries"] != one["durable_entries"]):
            raise ValueError("WAL authentication or journal head mismatch")
        causal = verified["memory_causality_317"]
        if causal["schema"] != "i1-memory-causality-317/v2":
            raise ValueError("wrong physical journey auditor")
        completed = causal["completed_remote_multihop_returns"]
        sleep = causal["completed_remote_returns_after_sleep"]
        if (type(completed) is not int or type(sleep) is not int
            or not 0 <= sleep <= completed
            or completed * 2 > verified["stages"]["physically_applied"]):
            raise ValueError("unbounded journey count")
        rows[seed] = {
            "sha": sha, "seed": seed,
            "life_id": one["individual_id"], "state": one["lifecycle"],
            "steps": len(one["steps"]), "journal_head": one["journal_head"],
            "durable_entries": one["durable_entries"],
            "preset_digest": report["source"]["sha256"],
            "physics_digest": report["environment"]["world_physics_digest"],
            "spawn": report["environment"]["spawn"],
            "initial_body": report["environment"]["initial_body"],
            "memory_actions": verified["stages"]["physically_applied"],
            "remote_first_hops": causal[
                "physically_applied_unseen_multihop_first_hops"],
            "completed_remote_multihop_returns": completed,
            "returns_after_sleep": sleep,
            "td_used_memory_actions": causal[
                "physically_applied_memory_actions_using_prior_td"],
            "examples": causal["completed_remote_return_examples"],
        }
    if set(rows) != set(KEYS):
        raise ValueError(f"incomplete authenticated cohort: {sorted(rows)}")
    return rows


def compare(old: dict[int,dict], new: dict[int,dict]) -> dict:
    pairs = []
    for seed in KEYS:
        p, q = old[seed], new[seed]
        for field in ("life_id", "preset_digest", "physics_digest",
                      "spawn", "initial_body"):
            if p[field] != q[field]:
                raise ValueError(f"not paired {seed}: {field}")
        pairs.append({"seed": seed, "baseline": p, "interruption_aware": q})
    summary = {}
    for name, arm in (("baseline", old), ("interruption_aware", new)):
        group = list(arm.values())
        summary[name] = {
            "lives":len(group),
            "deaths":sum(x["state"]=="dead" for x in group),
            "mean_observed_steps":mean(x["steps"] for x in group),
            "physically_applied_memory_actions":sum(x["memory_actions"] for x in group),
            "remote_first_hops":sum(x["remote_first_hops"] for x in group),
            "completed_remote_multihop_returns":sum(
                x["completed_remote_multihop_returns"] for x in group),
            "completed_returns_after_sleep":sum(x["returns_after_sleep"] for x in group),
            "td_used_memory_actions":sum(x["td_used_memory_actions"] for x in group),
        }
    return {
        "schema":"individual-zero-i1-317-remote-journey-pairs/v1",
        "status":"WAL_AUTHENTICATED_ALL_LIVES",
        "baseline_engine_sha":old[KEYS[0]]["sha"],
        "interruption_engine_sha":new[KEYS[0]]["sha"],
        "summary":summary,"pairs":pairs,
        "scientific_verdict":"NO-GO",
        "limitations":[
            "A few events in a diagnostic corridor do not establish robustness.",
            "Sleep interruption and remote completion must not bypass motor admission.",
            "Reaching wood or stone does not prove its physiological utility.",
            "The diagnostic seeds were used to discover this mechanism, not held out.",
        ]
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline",type=Path,required=True)
    ap.add_argument("--interruption-aware",type=Path,required=True)
    ap.add_argument("--baseline-sha",required=True)
    ap.add_argument("--interruption-sha",required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    p=cohort(args.baseline,sha=args.baseline_sha)
    q=cohort(args.interruption_aware,sha=args.interruption_sha)
    result=compare(p,q)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError("scientific evidence must not overwrite prior report")
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ISSUE317_EXACT_SHA_AUTHENTICATED_REMOTE_RETURNS")
    print(json.dumps(result["summary"],indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
