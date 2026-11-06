"""P5b POST-HOC paid-score algebra, original evidence only.

No run_life, no world instantiation, no prospective claim. Contrasts are
hypothesis-generating decomposition of actually prepaid option scores.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
from pathlib import Path
import sys

from i3.lab import p5b_custody, p5b_schedule

SCHEMA = "i3-p5b-posthoc-score-terms-v1"
EPS = 1e-9
MODES = p5b_schedule.READOUTS


def pair_terms(full: dict, treatment: dict) -> dict:
    """Only common paid options at identical body before first action change.

    Flags for base and bonus differences are NON-EXCLUSIVE at pair level.
    They are arithmetic observations, not causal attributions.
    """
    counts = Counter()
    flags = set()
    first_changed_action = None
    base_steps = full["early_witness"]
    intervention_steps = treatment["early_witness"]
    for i in range(min(len(base_steps), len(intervention_steps))):
        a, b = base_steps[i], intervention_steps[i]
        if a["pre_body"] == b["pre_body"]:
            left = {v["option"]: v for v in a["scores"]}
            right = {v["option"]: v for v in b["scores"]}
            for oid in sorted(left.keys() & right.keys()):
                l, r = left[oid], right[oid]
                base = abs(l["base_return"] - r["base_return"]) > EPS
                bonus = abs(l["bonus"] - r["bonus"]) > EPS
                score = abs(l["score"] - r["score"]) > EPS
                counts["matched_funded_candidate_observations"] += 1
                if base:
                    flags.add("any_base_delta")
                if bonus:
                    flags.add("any_bonus_delta")
                if score:
                    flags.add("any_score_delta")
                    if base and bonus:
                        counts["option_score_delta_both_terms"] += 1
                        flags.add("score_delta_both_terms")
                    elif base:
                        counts["option_score_delta_base_only"] += 1
                        flags.add("score_delta_base_only")
                    elif bonus:
                        counts["option_score_delta_bonus_only"] += 1
                        flags.add("score_delta_bonus_only")
                    else:
                        raise ValueError("score changed despite unchanged components")
                elif base or bonus:
                    counts["option_components_changed_but_score_cancelled"] += 1
                    flags.add("cancelled_component_deltas")
        if (a["action"], a["param"]) != (b["action"], b["param"]):
            first_changed_action = i + 1
            break
    return {
        "matched_funded_candidate_observations": counts["matched_funded_candidate_observations"],
        "first_action_difference_within_window": first_changed_action,
        "option_score_delta_base_only": counts["option_score_delta_base_only"],
        "option_score_delta_bonus_only": counts["option_score_delta_bonus_only"],
        "option_score_delta_both_terms": counts["option_score_delta_both_terms"],
        "option_components_changed_but_score_cancelled": counts[
            "option_components_changed_but_score_cancelled"],
        "pair_flags": sorted(flags),
    }


def analyze(original: dict) -> dict:
    verified = p5b_custody.verify(original)
    matches = {}
    for row in original["lives"]:
        key = (row["population"], row["arm"], row["slot"],
               row["family"], row["repeat"])
        matches.setdefault(key, {})[row["mode"]] = row
    if len(matches) != 288:
        raise RuntimeError("P5b original pair count changed")
    result = {}
    for mode in MODES[1:]:
        counts = Counter()
        populations = {p: Counter() for p in range(p5b_schedule.POPULATIONS)}
        for key, pair in matches.items():
            witness = pair_terms(pair["full"], pair[mode])
            p = key[0]
            counts["pairs"] += 1
            populations[p]["pairs"] += 1
            counts["matched_funded_candidate_observations"] += witness[
                "matched_funded_candidate_observations"]
            populations[p]["matched_funded_candidate_observations"] += witness[
                "matched_funded_candidate_observations"]
            for metric in (
                "option_score_delta_base_only",
                "option_score_delta_bonus_only",
                "option_score_delta_both_terms",
                "option_components_changed_but_score_cancelled"):
                counts[metric] += witness[metric]
                populations[p][metric] += witness[metric]
            for flag in witness["pair_flags"]:
                counts["pairs_"+flag] += 1
                populations[p]["pairs_"+flag] += 1
        if counts["pairs"] != 288 or any(x["pairs"] != 72 for x in populations.values()):
            raise RuntimeError("non-independent or missing genetic population pairs")
        result[mode] = {
            "total": dict(sorted(counts.items())),
            "by_genetic_population": {
                str(p): dict(sorted(populations[p].items()))
                for p in range(p5b_schedule.POPULATIONS)},
        }
    return {
        "schema": SCHEMA,
        "status": "POST_HOC_DESCRIPTIVE_NOT_PREREGISTERED_NOT_CONFIRMATORY",
        "original_canonical_sha256": verified["raw_canonical_sha256"],
        "original_source_sha": verified["source_sha"],
        "new_study_lives": 0,
        "matching": "same_pre_body_same_funded_option_pre_first_action_difference",
        "scope": "score_equals_base_return_plus_curiosity_risk_bonus",
        "pair_flag_categories": "NON_EXCLUSIVE",
        "modes": result,
    }


def load_original(path: Path) -> dict:
    data = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5b_posthoc_terms ORIGINAL.json.gz")
    print(json.dumps(analyze(load_original(Path(sys.argv[1]))),
                     sort_keys=True, indent=2))
