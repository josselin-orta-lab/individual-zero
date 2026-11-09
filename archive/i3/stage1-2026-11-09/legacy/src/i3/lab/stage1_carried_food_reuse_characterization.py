"""Frozen software characterization: carried-food information vs represented future uses.

Protocol: docs/STAGE1_CARRIED_FOOD_REUSE_CHARACTERIZATION.md (+ Amendment 1).
No World, no life, no study index. Fixtures are byte-for-byte the #1103 test
fixtures (tests/i3/test_stage1_carried_food_rank_audit.py), copied here so the
laboratory never imports test code.

    python -m i3.lab.stage1_carried_food_reuse_characterization OUTPUT.json
"""
from __future__ import annotations

import json
from statistics import median
import sys

from .stage1_carried_food_rank_audit import audit_carried_food_raw_rank
from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from ..modules.genome import midpoint
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind

SCHEMA = "i3-stage1-carried-food-reuse-characterization/v1"
BASE = (50., 50., 50., 50., 50.)
SAFE = (0., 30., 0., 0., 0.)
TOXIC = (0., 30., 0., -35., 0.)
CARRIED = (2, 3, 5, 9)          # max_future_repeats = n - 1 = 1, 2, 4, 8
GRID = tuple((energy, food, 80., integrity, 80.)
             for energy in (35., 60., 85.)
             for food in (5., 20., 40.)
             for integrity in (20., 50., 80.))


def _remember(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(key, BASE, CognitiveWork(), CognitiveBudget(after, BodyLaws()))


def _mind(rows, seed=127):
    mind = ReferenceBranchMemoryMind(midpoint(), seed)
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    for key, delta in rows:
        mind.effects.observe(key, delta)
        _remember(mind.branch_memory, key, delta)
    return mind


MIXED = ((("manger", "known-safe"), SAFE), (("manger", "known-toxic"), TOXIC))
HARMFUL = ((("manger", "known-a"), (0., 5., 0., -20., 0.)),
           (("manger", "known-b"), (0., 10., 0., -30., 0.)))


def _cap(body, count, token="mystery"):
    return {"body": tuple(body), "inventory": ((token, count),),
            "here": (False, ()), "neighbors": (None, None, None, None)}


def _summary(rows):
    done = [r for r in rows if r["status"] == "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT"]
    info = [r["candidate"]["information_value"] for r in done]
    work = [r["candidate"]["work"] for r in done]
    return {
        "evaluated": len(rows), "complete": len(done),
        "positive_information": sum(v > 1e-12 for v in info),
        "median_information": median(info) if info else None,
        "max_information": max(info) if info else None,
        "candidate_raw_top_base": sum(
            r["placement_vs_reference_base"]["candidate_raw_top"] for r in done),
        "candidate_raw_top_total": sum(
            r["placement_vs_reference_total"]["candidate_raw_top"] for r in done),
        "base_rank_improved": sum(
            r["placement_vs_reference_base"]["candidate_improves_reference_meal_rank"]
            for r in done),
        "total_rank_improved": sum(
            r["placement_vs_reference_total"]["candidate_improves_reference_meal_rank"]
            for r in done),
        "candidate_above_reference_meal_base": sum(
            r["placement_vs_reference_base"]["candidate_minus_reference_meal"] > 1e-12
            for r in done),
        "reference_chose_meal": sum(
            r["reference"]["chosen_option"] == r["meal_option"] for r in done),
        "mean_kernel_work": {
            key: sum(w[key] for w in work) / len(work) for key in work[0]} if work else None,
    }


def run(out_path: str) -> dict:
    report = {"schema": SCHEMA, "protocol": "STAGE1_CARRIED_FOOD_REUSE_CHARACTERIZATION.md",
              "label": "DESCRIPTIVE_NOT_COST_MATCHED", "world_access": False,
              "lives": 0, "mixed": {}, "harmful": {}, "one_unit": {}}
    for name, rows in (("mixed", MIXED), ("harmful", HARMFUL)):
        for n in CARRIED:
            report[name][str(n)] = _summary([
                audit_carried_food_raw_rank(
                    _mind(rows), _cap(body, n), BodyLaws(), "mystery",
                    max_future_repeats=n - 1)
                for body in GRID])
    report["one_unit"] = _summary([
        audit_carried_food_raw_rank(_mind(MIXED), _cap(body, 1), BodyLaws(),
                                    "mystery", max_future_repeats=8)
        for body in GRID])
    base = report["mixed"]["2"]["mean_kernel_work"]
    for n in CARRIED:
        w = report["mixed"][str(n)]["mean_kernel_work"]
        report["mixed"][str(n)]["work_ratio_to_n2"] = {
            k: (w[k] / base[k] if base[k] else None) for k in w}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    out = run(sys.argv[1])
    for name in ("mixed", "harmful"):
        for n, s in out[name].items():
            print(name, n, {k: s[k] for k in (
                "positive_information", "max_information", "candidate_raw_top_base",
                "base_rank_improved", "total_rank_improved", "reference_chose_meal")})
    print("one_unit", {k: out["one_unit"][k] for k in ("positive_information", "max_information")})
