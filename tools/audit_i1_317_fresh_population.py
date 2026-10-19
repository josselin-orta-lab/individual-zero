#!/usr/bin/env python3
"""#317 pre-registered fresh population: independent physical WAL analysis.

Observer-only. No interventions on the individual and no inferred food/water
affordance. The engine and world facts are independently pinned by exact
Git SHA, preset SHA-256, physics digest, immutable WAL and 1:1 birth IDs.
This is a diagnostic replication of real-world behaviours, not an automatic
scientific GO or a replacement for randomized entity-causality trials.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

from audit_i1_317_architecture_cohort import cohort, summary
from audit_i1_317_contact_causality import audit as audit_contact

SCHEMA = "i1-317-fresh-current-model-population/v1"
# Locked *before* running. Neither the historical demonstration 1141 nor the
# former "held-out" seeds 3011..3137 are present. Do not tune on this cohort.
FRESH_SEEDS = (8411, 8431, 8467, 8497)
PRESETS = (
    "oasis", "foraging", "dry-valley", "blocked-route", "memory-corridor"
)


def design(worlds, seeds):
    """Reject cherry-picked, duplicated, dropped or renamed experimental arms."""
    if (not isinstance(worlds, (tuple, list))
        or not isinstance(seeds, (tuple, list))
        or len(worlds) != len(PRESETS)
        or len(seeds) != len(FRESH_SEEDS)
        or len(set(worlds)) != len(worlds)
        or len(set(seeds)) != len(seeds)
        or set(worlds) != set(PRESETS)
        or any(type(s) is not int for s in seeds)
        or set(seeds) != set(FRESH_SEEDS)):
        raise ValueError("not the pre-registered 20-life physical cohort")
    return tuple(sorted((world, seed)
                        for world in PRESETS for seed in FRESH_SEEDS))


def _safe_keys(d):
    return {str(k) if k is not None else "<no applied primitive>": v
            for k, v in d.items()}


def summarize_world(rows):
    s = summary(rows)
    s["actions"] = _safe_keys(s["actions"])
    steps = sum(row["steps"] for row in rows.values())
    if not 1 <= steps <= len(rows) * 300:
        raise ValueError("impossible physically lived step count")
    if sum(s["actions"].values()) != steps:
        raise ValueError("lost or double-counted lived actions")
    s["total_lived_steps"] = steps
    s["action_percentages"] = {
        k: round(100 * value / steps, 4)
        for k, value in sorted(s["actions"].items())
    }
    s["mean_actions_per_lived_step"] = round(
        sum(value for k, value in s["actions"].items()
            if k != "<no applied primitive>") / steps, 6)
    return s


def analyse(root: Path, *, expected_sha: str, worlds=PRESETS, seeds=FRESH_SEEDS):
    plan = design(tuple(worlds), tuple(seeds))
    if (type(expected_sha) is not str or len(expected_sha) != 40
        or any(char not in "0123456789abcdef" for char in expected_sha)):
        raise ValueError("unpinned experiment git SHA")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("missing fresh population evidence directory")
    # The preexisting #317 cohort verifier enforces each of the exact twenty
    # report identity, world preset, initial body, physical configuration,
    # mortal status, journal head and fully verified WAL hash chain.
    rows = cohort(root, expected_sha, worlds, seeds)
    if set(rows) != set(plan):
        raise ValueError("missing or alien birth in sealed population")
    individuals = []
    unverified_contacts = 0
    contact_totals = Counter()
    td_reuses = 0
    td_credits = 0
    for world, seed in plan:
        key = (world, seed)
        row = rows[key]
        wal = root / world / str(seed) / "life-01.wal"
        if wal.is_symlink():
            raise ValueError("symlink WAL is not a sealed life")
        observation = audit_contact(wal)
        if (observation["independent_hash_chain_verified"] is not True
            or observation["journal_head"] != row["journal_head"]
            or observation["journal_entries"] != row["verified_journal_entries"]):
            raise ValueError("mismatched physical WAL and contact analysis")
        counters = observation["counters"]
        raw_contacts = sum(
            row["actions"].get(x, 0)
            for x in ("boire", "manger", "collecter"))
        if (counters["possible_contact_commands"] > raw_contacts
            or counters["physically_certified_contacts"]
               + counters["unverifiable_contacts"]
               != counters["possible_contact_commands"]):
            raise ValueError("unbounded/misattributed lived contacts")
        for name, count in counters.items():
            if type(count) is not int or count < 0:
                raise ValueError("invalid contact counter")
            contact_totals[name] += count
        unverified_contacts += counters["unverifiable_contacts"]
        bridge = observation["td_decision_bridge"]
        if (bridge["entity_causality_proven"] is not False
            or bridge["heldout_population_go"] is not False
            or type(bridge["physically_certified_reuses"]) is not int
            or type(bridge["physically_certified_eligible_action_credits"]) is not int):
            raise ValueError("contact was misrepresented as entity causality")
        td_reuses += bridge["physically_certified_reuses"]
        td_credits += bridge["physically_certified_eligible_action_credits"]
        individuals.append({
            "world": world, "seed": seed, "life_id": row["life_id"],
            "engine_sha": row["sha"],
            "preset_sha256": row["preset_digest"],
            "world_physics_digest": row["physics_digest"],
            "initial_body": row["initial_body"],
            "spawn": row["spawn"],
            "lifecycle": row["lifecycle"],
            "physically_lived_steps": row["steps"],
            "actions": _safe_keys(row["actions"]),
            "movement_reversals": row["immediate_movement_reversals"],
            "accepted_uc": row["accepted_uc"],
            "sleep_consolidation_commits": row["consolidation_commits"],
            "final_body": row["final_body"],
            "final_position": row["final_position"],
            "journal_head": row["journal_head"],
            "verified_journal_entries": row["verified_journal_entries"],
            "source_wal_sha256": observation["source_sha256"],
            "contact_counters": counters,
            "physically_certified_td_to_memory_decision_bridges":
                bridge["physically_certified_reuses"],
            "physically_certified_eligible_td_action_credits":
                bridge["physically_certified_eligible_action_credits"],
            "remote_unseen_first_hops":
                row["memory_causality"][
                    "physically_applied_unseen_multihop_first_hops"],
            "completed_remote_returns":
                row["memory_causality"].get(
                    "completed_remote_multihop_returns", 0),
        })
    worlds_summary = {
        world: summarize_world({
            key: rows[key] for key in plan if key[0] == world
        }) for world in PRESETS
    }
    totals = summarize_world(rows)
    # A fresh observational population provides no intervention contrast.
    return {
        "schema": SCHEMA,
        "status": "SEALED_OBSERVATIONAL_POPULATION_NO_SCIENTIFIC_GO",
        "preregistered_design": {
            "preset_ids": list(PRESETS),
            "fresh_seeds": list(FRESH_SEEDS),
            "exact_required_lives": len(plan),
            "steps_requested_per_birth": 300,
            "engine_sha": expected_sha,
            "no_seed_selected_post_outcome": True,
            "previous_diagnostic_or_heldout_seeds_reused": False,
            "evidence_from_ordinary_mortal_births": True,
            "no_scripted_actions_or_ablations": True,
        },
        "summary": totals,
        "by_world": worlds_summary,
        "physically_certified_contacts": dict(sorted(contact_totals.items())),
        "unverifiable_contacts": unverified_contacts,
        "physically_certified_eligible_td_action_credits": td_credits,
        "physically_certified_td_to_memory_decision_bridges": td_reuses,
        "individuals": individuals,
        "entity_specific_causality_proven": False,
        "remote_navigation_generality_proven": False,
        "survival_advantage_proven": False,
        "scientific_verdict": "NO-GO",
        "caveats": [
            "A positive TD return can result from prior *action* eligibility.",
            "Consumption from inventory is not causal credit for a co-located entity.",
            "Co-location with a resource is not a learned affordance.",
            "Lived body changes include baseline metabolism and are not intervention controls.",
            "No absence of a strict bridge proves learning is impossible.",
            "The published 1141 intervention is an in-sample diagnostic, not a population control.",
            "A positive survival rate over a mortal 300-step horizon is not long-term safety.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("never overwrite a prior scientific report")
    result = analyse(args.root, expected_sha=args.expected_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    print("I1_317_FRESH_POPULATION_SEALED_20_LIVES")
    print(json.dumps({
        "engine_sha": args.expected_sha,
        "lives": result["preregistered_design"]["exact_required_lives"],
        "summary": result["summary"],
        "contacts": result["physically_certified_contacts"],
        "strict_td_bridges": result[
            "physically_certified_td_to_memory_decision_bridges"],
        "scientific_verdict": result["scientific_verdict"],
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
