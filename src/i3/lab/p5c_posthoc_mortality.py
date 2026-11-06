"""P5c post-hoc ORIGINAL-ONLY active mortality diagnosis.

The original compact scientific receipts include lifetime, death causes,
inactivity, paid work and first-12-step actions. They DO NOT contain complete
resource-contact histories. Never reconstruct nonexistent observations or
rerun a mind/world to fill missing original evidence.

This audit is descriptive, post-hoc, nonconfirmatory, and opens no worlds.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
from pathlib import Path
import sys

from i3.lab import p5c_custody, p5c_schedule

SCHEMA = "i3-p5c-posthoc-active-mortality-v1"
MODES = p5c_schedule.MODES
MORTALITY_STEPS = (100, 200, 300, 400)


def _cause_label(cause):
    if isinstance(cause, str):
        return cause
    return json.dumps(cause, sort_keys=True, separators=(",", ":"))


def _action_family(action):
    if action is None:
        return "no_action"
    if action == "se_deplacer":
        return "movement"
    if action in ("dormir", "attendre"):
        return "rest_or_wait"
    if action in ("boire", "manger", "collecter"):
        return "resource"
    return "other"


def _group(rows):
    """Descriptive summaries, never claims of independent life replication."""
    deaths = Counter()
    first_actions = Counter()
    for row in rows:
        if row["terminal"] == "dead":
            # A death with multiple cited causes increments multiple bins.
            for cause in row["death_causes"]:
                deaths[_cause_label(cause)] += 1
        for item in row["early_witness"]:
            first_actions[_action_family(item["action"])] += 1
    return {
        "lives": len(rows),
        "censored": sum(x["censored"] for x in rows),
        "deaths": sum(x["terminal"] == "dead" for x in rows),
        "total_steps_lived": sum(x["steps_lived"] for x in rows),
        "total_inactive_steps": sum(x["inactive_steps"] for x in rows),
        "mean_lifetime_steps": round(sum(x["steps_lived"] for x in rows) / len(rows), 6),
        "dead_by_horizon": {
            str(t): sum(x["terminal"] == "dead" and x["steps_lived"] <= t
                        for x in rows)
            for t in MORTALITY_STEPS},
        "death_causes_multi_label": dict(sorted(deaths.items())),
        "first_12_step_action_families": dict(sorted(first_actions.items())),
        "first_12_steps_observed": sum(len(x["early_witness"]) for x in rows),
        "admitted_actions_all_lived_steps": sum(
            x["decision_status"]["action_admitted"] for x in rows),
        "no_processing_budget_all_lived_steps": sum(
            x["decision_status"]["no_processing_budget"] for x in rows),
        "paid_cognitive_energy": round(sum(x["paid"]["energy"] for x in rows), 6),
        "paid_cognitive_vigilance": round(sum(x["paid"]["vigilance"] for x in rows), 6),
    }


def analyze(original):
    checked = p5c_custody.verify(original)
    lives = original["lives"]
    if len(lives) != 1152:
        raise ValueError("missing original lives")
    by_mode = {}
    by_ecology = {}
    by_population = {}
    for mode in MODES:
        rows = [r for r in lives if r["mode"] == mode]
        if len(rows) != 288:
            raise ValueError("incorrect original mode allocation")
        by_mode[mode] = _group(rows)
        by_ecology[mode] = {}
        by_population[mode] = {}
        for family in p5c_schedule.FAMILIES:
            group = [x for x in rows if x["family"] == family]
            if len(group) != 96:
                raise ValueError("ecology denominator changed")
            by_ecology[mode][family] = _group(group)
        for p in range(p5c_schedule.POPULATIONS):
            group = [x for x in rows if x["population"] == p]
            if len(group) != 72:
                raise ValueError("genetic-population denominator changed")
            by_population[mode][str(p)] = _group(group)
    # The same 288 original genotype/world/life-seed opportunities
    # are compared without pretending they are genetic-population replicas.
    pairs = {}
    for x in lives:
        key = (x["population"], x["arm"], x["slot"], x["family"], x["repeat"])
        pairs.setdefault(key, {})[x["mode"]] = x
    if len(pairs) != 288 or any(set(x) != set(MODES) for x in pairs.values()):
        raise ValueError("paired original life identity changed")
    comparisons = {}
    for mode in MODES[1:]:
        differences = [v["normal"]["steps_lived"] - v[mode]["steps_lived"]
                       for v in pairs.values()]
        comparisons[mode] = {
            "paired_opportunities": len(differences),
            "normal_lived_longer": sum(x > 0 for x in differences),
            "equal_lifetime": sum(x == 0 for x in differences),
            "ablation_lived_longer": sum(x < 0 for x in differences),
            "population_mean_lifetime_difference": {
                str(p): round(sum(
                    v["normal"]["steps_lived"] - v[mode]["steps_lived"]
                    for k, v in pairs.items() if k[0] == p) / 72.0, 6)
                for p in range(p5c_schedule.POPULATIONS)},
        }
    return {
        "schema": SCHEMA,
        "status": "POSTHOC_DESCRIPTIVE_ONLY_NO_NEW_LIVES",
        "original_canonical_sha256": checked["raw_canonical_sha256"],
        "original_source_sha": checked["source_sha"],
        "original_lives": len(lives),
        "analysis_units": "four_P3_genetic_populations_not_1152_independent_lives",
        "scope": "original_compact_life_receipts_and_first_12_steps_only",
        "missing_data_limit": "NO_COMPLETE_POST_STEP_RESOURCE_CONTACT_OR_BODY_TRAJECTORIES",
        "death_causes": "multi_label_counts_can_exceed_number_of_deaths",
        "by_mode": by_mode,
        "by_ecology": by_ecology,
        "by_population": by_population,
        "paired_lifetime": comparisons,
    }


def load_original(path: Path):
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(raw)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5c_posthoc_mortality ORIGINAL.json.gz")
    print(json.dumps(analyze(load_original(Path(sys.argv[1]))),
                     sort_keys=True, indent=2))
