"""G2b: held-out check of P1.1 against P1, paired by genome and life seed.

Frozen by docs/G2B_P11_HELDOUT_PREREG.md BEFORE execution. The three
held-out worlds below were written after P1.1 development stopped and were
never run before the preregistration commit. The engine version is chosen by
putting its ``src`` directory first on sys.path (P1 = commit 1068935).

Usage: python heldout_p11.py ENGINE_SRC OUTPUT.json
"""
from __future__ import annotations

import json
import sys

PROTOCOL = "i3-g2b-p11-heldout-v1"
GENOME_SEEDS = tuple(range(201, 231))
HORIZON = 400


def worlds(world_module):
    WS, Water, Food = world_module.WorldSpec, world_module.WaterSource, world_module.FoodPatch

    def h1_hidden_spring():
        return WS(name="g2b-h1-hidden-spring", width=16, height=16, spawn=(8, 8),
                  body=(75.0, 50.0, 45.0, 90.0, 100.0),
                  water={(8, 4): Water(gain=35.0)},
                  food={(10, 9): Food("amber", 3, 3, restock_every=15)},
                  token_effects={"amber": (12.0, 0.0)})

    def h2_round_trip():
        return WS(name="g2b-h2-round-trip", width=14, height=7, spawn=(1, 3),
                  body=(80.0, 35.0, 70.0, 95.0, 100.0),
                  water={(1, 3): Water(gain=35.0)},
                  food={(11, 1): Food("sage", 3, 3, restock_every=12),
                        (12, 5): Food("sage", 3, 3, restock_every=12)},
                  token_effects={"sage": (15.0, 0.0)})

    def h3_dried_spring():
        # Spring A next to birth gives 4 drinks, then is dry for good; spring
        # B is far and out of sight. Surviving needs a change of strategy.
        return WS(name="g2b-h3-dried-spring", width=12, height=12, spawn=(2, 2),
                  body=(80.0, 60.0, 60.0, 95.0, 100.0),
                  water={(3, 2): Water(gain=30.0, stock=4, max_stock=4, restock_every=0),
                         (9, 9): Water(gain=30.0)},
                  food={(2, 4): Food("rust", 3, 3, restock_every=10),
                        (8, 9): Food("rust", 3, 3, restock_every=10)},
                  token_effects={"rust": (12.0, 0.0)})

    return (h1_hidden_spring, h2_round_trip, h3_dried_spring)


def run(engine_src: str, out_path: str) -> dict:
    sys.path.insert(0, engine_src)
    from i3.modules import world as world_module
    from i3.modules.genome import digest, generation_zero
    from i3.runtime.life import run_life
    rows = []
    for make in worlds(world_module):
        for seed in GENOME_SEEDS:
            g = generation_zero(seed)
            a = run_life(g, make(), 2000 + seed, HORIZON, keep_trace=True)
            b = run_life(g, make(), 2000 + seed, HORIZON)
            trace = a.pop("trace")
            a["replay_identical"] = a["trace_head"] == b["trace_head"]
            a["genome_seed"] = seed
            a["genome"] = digest(g)
            a["drinks_at_far_spring"] = sum(
                1 for rec in trace if rec["action"] == "boire" and tuple(rec["pos"]) == (9, 9))
            rows.append(a)
    report = {"protocol": PROTOCOL, "engine_src": engine_src, "horizon": HORIZON,
              "genome_seeds": list(GENOME_SEEDS), "lives": rows}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])


MARGIN = 3  # non-inferiority margin, lives out of 30


def verdict(p1: dict, p11: dict, g2_regression: dict) -> dict:
    """Preregistered decision: adopt P1.1 only if every criterion holds."""
    out = {"by_world": {}, "criteria": {}}
    ok = True
    for name in sorted({r["world"] for r in p11["lives"]}):
        a = [r for r in p1["lives"] if r["world"] == name]
        b = [r for r in p11["lives"] if r["world"] == name]
        alive = (sum(r["terminal"] == "censored" for r in a),
                 sum(r["terminal"] == "censored" for r in b))
        late = tuple(sum(1 for r in x if r["drinks"] > 0 and "zero_water" in r["death_causes"])
                     for x in (a, b))
        far = tuple(sum(1 for r in x if r["drinks_at_far_spring"] > 0) for x in (a, b))
        non_inferior = alive[1] >= alive[0] - MARGIN
        ok &= non_inferior
        out["by_world"][name] = {"alive_p1": alive[0], "alive_p11": alive[1],
                                 "non_inferior": non_inferior,
                                 "thirst_after_drinking_p1": late[0],
                                 "thirst_after_drinking_p11": late[1],
                                 "used_far_spring_p1": far[0], "used_far_spring_p11": far[1]}
        if name == "g2b-h2-round-trip":
            out["criteria"]["defect_not_worse_h2"] = late[1] <= late[0]
            ok &= late[1] <= late[0]
    reg = g2_regression["verdict_by_world"]
    out["criteria"]["g2_regression"] = all(v["pass"] for v in reg.values())
    out["criteria"]["replay_all_p11"] = all(r["replay_identical"] for r in p11["lives"])
    mean_ms = sum(r["mean_step_ms"] for r in p11["lives"]) / len(p11["lives"])
    out["criteria"]["mean_step_ms_p11"] = round(mean_ms, 4)
    out["criteria"]["budget_ok"] = mean_ms <= 1.0
    ok &= out["criteria"]["g2_regression"] and out["criteria"]["replay_all_p11"] \
        and out["criteria"]["budget_ok"]
    out["decision"] = "ADOPT_P1_1" if ok else "REJECT_P1_1_KEEP_P1"
    return out
