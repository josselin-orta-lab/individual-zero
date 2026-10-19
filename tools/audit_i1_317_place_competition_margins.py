#!/usr/bin/env python3
"""#317 causally bounded analysis of prior 24 *sealed* first-person place WAL.

First independently reauthenticate each physical life via the existing
24-life certifier. Compare only equal (world, seed, worldstep, cycle,
option_ref) after an admitted positive personal boire follow-up at the
candidate's exact source coordinates. Estimate real Competition evidence
and threshold effects, not unjournaled researcher invocation counters.

Never relaunch any individual, import a living actor or infer benefit from
resource type, a copied path, or a numerical score alone.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from math import isfinite, isclose
from pathlib import Path

from audit_i1_317_lived_place_cohort import (
    ARMS, PRESETS, SEEDS, EXACT_SOURCE_SHA,
    certify as certify_original_lives,
)

SCHEMA = "i1-317-place-evidence-margin-sealed/v1"
KEY = ("canonical", "value_only", "recall_only", "recall_and_value")


def require(ok, why):
    if not ok:
        raise ValueError(why)


def number(x):
    if type(x) in (int, float):
        val = float(x)
    elif type(x) is dict and set(x) == {"$f64"} and type(x["$f64"]) is str:
        val = float.fromhex(x["$f64"])
    else:
        raise ValueError("not a canonical WAL float")
    require(isfinite(val), "non-finite causal number")
    return val


def _place_coordinate(value):
    return (type(value) is list and len(value) == 2
            and all(type(x) is int for x in value))


def read_effects(wal):
    """Audited before invocation; now inspect trace-aligned observed effects.

    The same memory candidate may persist across multiple cycles. Only
    proposals actually re-offered in the same cognitive cycle are considered,
    to avoid claiming an unobserved motivational basis for a carryover.
    """
    learned_places = set()
    offered = defaultdict(dict)
    traces = {}
    actions = {}
    wake = Counter()
    learned_count = 0
    with wal.open(encoding="utf-8") as stream:
        for raw in stream:
            e = json.loads(raw)["causal_event"]
            t, cycle = e.get("t_monde"), e.get("cycle")
            kind, data = e.get("kind"), e.get("data", {})
            if kind == "i1_water_lived_outcome_admitted":
                require(data.get("admitted") is True
                        and _place_coordinate(data.get("source_position"))
                        and number(data.get("delta_water")) > 0,
                        "positive site is not first-person experienced")
                learned_places.add(tuple(data["source_position"]))
                learned_count += 1
            if kind == "i1_place_memory_option_proposed":
                target = data.get("target")
                opt = data.get("option_ref")
                if (data.get("entity_type") == "water_source"
                        and _place_coordinate(target)
                        and tuple(target) in learned_places
                        and type(opt) is str
                        and opt.startswith("option:place-memory:")
                        and type(data.get("active_goal")) is str
                        and data["active_goal"].startswith("goal:drink:")):
                    offered[(t, cycle)][opt] = tuple(target)
            if kind == "competition_cycle":
                for trace in data.get("traces", ()):
                    ref = trace.get("option_ref")
                    if ref not in offered.get((t, cycle), {}):
                        continue
                    threshold = number(trace.get("threshold"))
                    acc = number(trace.get("accumulator_after"))
                    ev = (None if trace.get("evidence") is None
                          else number(trace["evidence"]))
                    require(threshold > 0 and acc >= 0
                            and (ev is None or -1 <= ev <= 1)
                            and type(trace.get("crossed")) is bool,
                            "invalid score for personally learned place")
                    key = (t, cycle, ref)
                    require(key not in traces, "duplicate Competition cycle")
                    traces[key] = {
                        "evidence": ev, "accumulator": acc,
                        "threshold": threshold,
                        "threshold_fraction": acc / threshold,
                        "crossed": trace["crossed"],
                        "position": offered[(t, cycle)][ref],
                    }
            if kind == "command_experienced":
                require(t not in actions, "duplicate physically experienced command")
                actions[t] = (e.get("primitive"), e.get("parameters"))
            if kind == "stage10_sleep_woke":
                wake[data.get("reason")] += 1
    require(actions and learned_count >= 0, "not a lived physical journal")
    return {
        "learned_positive_followups": learned_count,
        "learned_site_candidates_scored": traces,
        "physical_action_by_step": actions,
        "wake_reason_count": dict(wake),
    }


def compare_scores(reference, candidate):
    """Exact paired-candidate numerical contrasts; not a new motor policy."""
    r, c = (reference["learned_site_candidates_scored"],
            candidate["learned_site_candidates_scored"])
    shared = r.keys() & c.keys()
    changed = []
    for key in sorted(shared):
        old, new = r[key], c[key]
        require(old["position"] == new["position"],
                "different place compared as one option")
        if (not isclose(old["evidence"] or 0, new["evidence"] or 0,
                        rel_tol=0.0, abs_tol=1e-12)
            or old["crossed"] != new["crossed"]):
            changed.append({
                "step": key[0], "cycle": key[1],
                "option_ref": key[2],
                "source_position": list(old["position"]),
                "reference_evidence": old["evidence"],
                "candidate_evidence": new["evidence"],
                "reference_threshold_fraction": old["threshold_fraction"],
                "candidate_threshold_fraction": new["threshold_fraction"],
                "reference_crossed": old["crossed"],
                "candidate_crossed": new["crossed"],
            })
    return {
        "paired_first_person_site_candidate_evaluations": len(shared),
        "reference_only_opportunities": len(r.keys() - c.keys()),
        "candidate_only_opportunities": len(c.keys() - r.keys()),
        "number_with_changed_evidence_or_crossing": len(changed),
        "changed_crossing_outcomes": sum(x["reference_crossed"]
                                         != x["candidate_crossed"]
                                         for x in changed),
        "changed_scores": changed,
    }


def compare_motors(reference, candidate):
    a, b = reference["physical_action_by_step"], candidate["physical_action_by_step"]
    require(a.keys() == b.keys(), "mortally lived step sets differed")
    changed = [(step, a[step], b[step]) for step in sorted(a) if a[step] != b[step]]
    return {
        "physical_step_motor_divergences": len(changed),
        "first_changed_physical_step": (
            None if not changed else {
                "world_step": changed[0][0],
                "baseline": changed[0][1],
                "variant": changed[0][2],
            }),
    }


def run(root):
    certificate = certify_original_lives(root)
    require(certificate["scientific_verdict"] == "NO-GO"
            and certificate["certified_original_wal_paths"] == 24
            and certificate["exact_birth_source_sha"] == EXACT_SOURCE_SHA,
            "cannot interpret an uncertified physical cohort")
    paired = []
    totals = {arm: Counter() for arm in ARMS if arm != "canonical"}
    effects = Counter()
    for world in PRESETS:
        for seed in SEEDS:
            site = root/world/str(seed)
            result = {arm: read_effects(site/arm/"life-01.wal") for arm in KEY}
            comparisons = {}
            for arm in KEY[1:]:
                delta = compare_scores(result["canonical"], result[arm])
                motor = compare_motors(result["canonical"], result[arm])
                comparisons[arm] = {**delta, **motor}
                totals[arm].update({
                    key: delta[key] for key in (
                        "paired_first_person_site_candidate_evaluations",
                        "reference_only_opportunities",
                        "candidate_only_opportunities",
                        "number_with_changed_evidence_or_crossing",
                        "changed_crossing_outcomes",
                    )
                })
                totals[arm]["physical_step_motor_divergences"] += (
                    motor["physical_step_motor_divergences"])
            paired.append({
                "world": world, "seed": seed,
                "learned_positive_followups": result["canonical"]["learned_positive_followups"],
                "canonical_site_evaluations": len(
                    result["canonical"]["learned_site_candidates_scored"]),
                "comparisons": comparisons,
            })
    summary = {arm: dict(totals[arm]) for arm in totals}
    return {
        "schema": SCHEMA,
        "status": "ATTESTED_SCORE_MARGIN_DIAGNOSTIC_NO_GO",
        "source_run": 39308197811,
        "exact_source_sha": EXACT_SOURCE_SHA,
        "certified_original_wal_paths": 24,
        "original_independent_certificate_schema": certificate["schema"],
        "physically_mortal_and_hash_verified": True,
        "research_adapter_invocation_count_is_WAL_proven": False,
        "no_type_only_resource_utility_asserted": True,
        "no_automatic_motor_promotion": True,
        "scientific_verdict": "NO-GO",
        "totals_by_treatment": summary,
        "matched_first_person_pair_comparisons": paired,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    r = run(a.root)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": r["status"], "scientific_verdict": r["scientific_verdict"],
        "totals_by_treatment": r["totals_by_treatment"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
