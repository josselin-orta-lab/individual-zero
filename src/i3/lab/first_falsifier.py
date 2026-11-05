"""G2 first falsifier: can the I3 core reach water where I1 and I2 died of thirst?

Frozen by docs/G2_FIRST_FALSIFIER_PREREG.md BEFORE any execution. The three
worlds reproduce, in I3's grid, the situations of the 5 November diagnosis:
I1 'foraging' (water 2 cells away, out of sight) and the two I2 native
corridors (camp - passage - source). Generation-0 genomes, no evolution,
no special rule. One execution; results are kept whatever they are.

Usage: python -m i3.lab.first_falsifier OUTPUT.json   (with src/ on sys.path)
"""
from __future__ import annotations

import json
import sys
import time

from i3.modules.genome import digest, generation_zero, midpoint
from i3.modules.world import FoodPatch, WaterSource, WorldSpec
from i3.runtime.life import run_life

PROTOCOL = "i3-g2-first-falsifier-v1"
GENOME_SEEDS = tuple(range(1, 11))
HORIZON = 300
REQUIRED = 8          # lives out of 10 that must drink, in EACH world
STEP_BUDGET_MS = 1.0  # mean over all primary lives


def i1_foraging_like() -> WorldSpec:
    """I1 preset 'foraging' (32x32 with walls -> 30x30 interior, shifted by -1)."""
    return WorldSpec(
        name="g2-i1-foraging-like", width=30, height=30, spawn=(7, 7),
        body=(70.0, 45.0, 42.0, 85.0, 100.0),
        water={(9, 7): WaterSource(gain=40.0), (10, 9): WaterSource(gain=40.0)},
        food={(8, 7): FoodPatch("berry_a", 4, 4), (7, 9): FoodPatch("berry_a", 3, 3),
              (11, 8): FoodPatch("berry_b", 3, 3)},
        token_effects={"berry_a": (10.0, 0.0), "berry_b": (5.0, -10.0)},
    )


def i2_native_a_like() -> WorldSpec:
    """I2 native world A of the diagnosis: water at camp, food at passage."""
    return WorldSpec(
        name="g2-i2-native-A-like", width=3, height=1, spawn=(0, 0),
        body=(78.0, 46.0, 44.0, 94.0, 100.0),
        water={(0, 0): WaterSource(gain=35.0, stock=2, max_stock=2, restock_every=10)},
        food={(1, 0): FoodPatch("food", 1, 1, restock_every=8)},
        token_effects={"food": (20.0, 0.0)},
    )


def i2_native_b_like() -> WorldSpec:
    """I2 native world B of the diagnosis: water and food at source only."""
    return WorldSpec(
        name="g2-i2-native-B-like", width=3, height=1, spawn=(0, 0),
        body=(78.0, 46.0, 44.0, 94.0, 100.0),
        water={(2, 0): WaterSource(gain=35.0, stock=2, max_stock=2, restock_every=8)},
        food={(2, 0): FoodPatch("food", 2, 2, restock_every=8)},
        token_effects={"food": (20.0, 0.0)},
    )


WORLDS = (i1_foraging_like, i2_native_a_like, i2_native_b_like)


def run(out_path: str) -> dict:
    started = time.time()
    rows, replay_ok, step_ms = [], True, []
    for make in WORLDS:
        for seed in GENOME_SEEDS:
            g = generation_zero(seed)
            a = run_life(g, make(), 1000 + seed, HORIZON)
            b = run_life(g, make(), 1000 + seed, HORIZON)
            same = a["trace_head"] == b["trace_head"]
            replay_ok &= same
            step_ms.append(a["mean_step_ms"])
            a["genome_seed"] = seed
            a["replay_identical"] = same
            rows.append(a)
    reference = [run_life(midpoint(), make(), 999, HORIZON) for make in WORLDS]
    verdict = {}
    for make in WORLDS:
        name = make().name
        lives = [r for r in rows if r["world"] == name]
        drank = sum(1 for r in lives if r["drinks"] > 0)
        verdict[name] = {
            "drank": drank, "of": len(lives), "required": REQUIRED,
            "pass": drank >= REQUIRED,
            "survived_to_horizon": sum(1 for r in lives if r["terminal"] == "censored"),
            "deaths_by_cause": {c: sum(1 for r in lives if c in r["death_causes"])
                                for c in ("zero_water", "zero_food", "zero_integrity")},
        }
    mean_ms = sum(step_ms) / len(step_ms)
    behavioural = all(v["pass"] for v in verdict.values())
    technical = replay_ok and mean_ms <= STEP_BUDGET_MS
    report = {
        "protocol": PROTOCOL, "horizon": HORIZON, "genome_seeds": list(GENOME_SEEDS),
        "genomes": {s: digest(generation_zero(s)) for s in GENOME_SEEDS},
        "verdict_by_world": verdict,
        "technical": {"replay_identical_all": replay_ok, "mean_step_ms": round(mean_ms, 4),
                      "budget_ms": STEP_BUDGET_MS, "pass": technical},
        "g2_verdict": ("INVALID_EXPERIMENT" if not replay_ok else
                       "G2_PASS_BEHAVIOURAL_AND_TECHNICAL" if behavioural and technical else
                       "G2_FAIL"),
        "scientific_claim": "NONE (software gate and one fixed behavioural falsifier)",
        "lives": rows, "reference_midpoint": reference,
        "wall_seconds": round(time.time() - started, 1),
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print(json.dumps({k: rep[k] for k in ("g2_verdict", "verdict_by_world", "technical")},
                     indent=1))
