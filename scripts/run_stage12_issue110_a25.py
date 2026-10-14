"""Preregistered A2.5 contrast, read-only census atop original 16-life A/B.

All cognition is executed in the unchanged first-planning-state factory.
The same canonical WAL/agency/goal/A2 audits as the original A/B are retained.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from run_stage12_issue110_instrumental_ab import one, PROFILES, WEIGHTS, MAX_STEPS
from lab.journal import HashChainedJournal
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

PREREG = (
    "docs/research/"
    "stage12-issue110-a2-epistemic-diversity-p48-food-prereg-2026-10-14.fr.md"
)


def evaluate_cohort(lives: list[dict]) -> dict:
    by_condition = {
        (v["profile"], v["intervention"], v["instrumental"]): v
        for v in lives
    }
    if len(by_condition) != len(lives):
        raise ValueError("duplicate birth condition in P-48 contrast")
    paired = []
    for profile in PROFILES:
        for intervention in (False, True):
            control = by_condition[(profile, intervention, False)]
            instrument = by_condition[(profile, intervention, True)]
            a = control.get("physical_census") or {}
            b = instrument.get("physical_census") or {}
            a_sites = a.get("physically_distinct_sites")
            b_sites = b.get("physically_distinct_sites")
            a_move = a.get("confirmed_moves")
            b_move = b.get("confirmed_moves")
            available = all(type(n) is int and n >= 0
                            for n in (a_sites, b_sites, a_move, b_move))
            preserved = bool(available and a_sites > 0
                             and b_sites * 5 >= a_sites * 4
                             and (a_move == 0 or b_move > 0))
            paired.append({
                "profile": profile, "a2": intervention,
                "control_sites": a_sites, "instrumental_sites": b_sites,
                "control_confirmed_moves": a_move,
                "instrumental_confirmed_moves": b_move,
                "relative_site_retention": (
                    (b_sites / a_sites) if available and a_sites > 0
                    else None),
                "physical_diversity_preserved_80pct": preserved,
            })
    total = lambda key: sum(
        (v.get("physical_census") or {}).get(key, 0) for v in lives
    )
    instrumental = [v for v in lives if v["instrumental"]]
    food_witness_lives = sum(
        (v.get("physical_census") or {}).get("physically_confirmed_eats", 0) > 0
        and (v.get("physical_census") or {}).get(
            "net_food_increase_steps_after_first", 0
        ) > 0
        for v in instrumental
    )
    failures = sum(
        bool(v.get("execution_error") or v.get("audit_error")
             or v.get("independent_census_error"))
        for v in lives
    )
    return {
        "schema": "stage12-a25-cohort-comparison-v1",
        "preregistration": PREREG,
        "planned_lives": 16,
        "actual_lives": len(lives),
        "independent_physical_steps": sum(v["steps"] for v in lives),
        "errors": failures,
        "all_eight_pairs_preserve_sites": (
            len(paired) == 8 and all(
                p["physical_diversity_preserved_80pct"] for p in paired
            )),
        "matched_pairs": paired,
        "physical_meals_all_lives": total("physically_confirmed_eats"),
        "net_food_increase_steps_all_lives": total(
            "net_food_increase_steps_after_first"),
        "instrumental_lives_with_eat_and_food_gain": food_witness_lives,
        "shared_p48_source_groups": total("cross_option_shared_signal_groups"),
        "within_option_repeated_signal_ids": total(
            "within_option_repeated_signal_ids"),
        "attribution_calibration_not_inferred_from_p48": True,
        "scientific_generalization_claimed": False,
        "operator_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohort-id", required=True)
    args = parser.parse_args()
    if (not 1 <= len(args.cohort_id) <= 32
            or not all(c.isascii() and (c.isalnum() or c in "._-")
                       for c in args.cohort_id)):
        parser.error("cohort ID must be unique, ASCII and at most 32 chars")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    lives = []
    for enabled in WEIGHTS:
        for profile in PROFILES:
            for obstacle in (False, True):
                name = (
                    ("instrumental_" if enabled else "control_")
                    + profile + ("_a2" if obstacle else "_free")
                )
                try:
                    item = one(args.output_dir, profile, obstacle,
                               args.cohort_id, enabled)
                except Exception as exc:
                    # Do not conceal earlier partial journal/WAL artifacts.
                    item = {
                        "condition": name, "profile": profile,
                        "intervention": obstacle, "instrumental": enabled,
                        "steps": 0, "execution_error": (
                            type(exc).__name__ + ": " + str(exc)),
                        "audit_error": None,
                    }
                folder = args.output_dir / name
                try:
                    journal = (folder / "canonical.jsonl").read_bytes()
                    wal = HashChainedJournal.audit_durable_wal(
                        str(folder / "life.wal"))
                    item["physical_census"] = audit_stage12_p48_diversity(
                        journal, expected_head=wal["head_hash"],
                        expected_count=wal["verified_entries"])
                    item["independent_census_error"] = None
                    (folder / "a25-independent-physical-p48-census.json").write_text(
                        json.dumps(item["physical_census"], sort_keys=True,
                                   indent=2) + "\n",
                        encoding="utf-8",
                    )
                except Exception as exc:
                    item["independent_census_error"] = (
                        type(exc).__name__ + ": " + str(exc))
                print("A25_LIFE " + json.dumps({
                    "name": name, "steps": item["steps"],
                    "execution_error": item.get("execution_error"),
                    "audit_error": item.get("audit_error"),
                    "independent_census_error": item.get(
                        "independent_census_error"),
                    "physical_census": {
                        k: v for k, v in
                        (item.get("physical_census") or {}).items()
                        if k not in ("positions", "cross_option_shared_signals")
                    },
                }, sort_keys=True))
                lives.append(item)
    result = evaluate_cohort(lives)
    result["source_sha"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip()
    result["lives"] = lives
    result["cohort_id"] = args.cohort_id
    result["lives_with_calibrable_attribution"] = sum(
        bool(v.get("evaluable")) for v in lives)
    (args.output_dir / "a25-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("A25_SUMMARY " + json.dumps({
        k: v for k, v in result.items() if k != "lives"
    }, sort_keys=True))
    return 0 if (result["actual_lives"] == 16
                 and result["independent_physical_steps"] == 16 * MAX_STEPS
                 and result["errors"] == 0
                 and result["within_option_repeated_signal_ids"] == 0) else 2


if __name__ == "__main__":
    raise SystemExit(main())
