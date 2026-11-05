"""G2c: held-out check of P1.2 against P1.1 on RESERVED generated worlds.

Frozen by docs/G2C_P12_HELDOUT_PREREG.md before execution. Reserved seeds
(>= worldgen.RESERVED_FROM) of families 'R' (strategy revision) and 'dev'
were never run during development. Paired: same world, same shared genes,
same life seed for both engine versions.

Usage: python heldout_p12.py ENGINE_SRC OUTPUT.json
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

PROTOCOL = "i3-g2c-p12-heldout-v1"
SEEDS = tuple(range(1_000_000, 1_000_100))
H_REVISION, H_GENERAL = 400, 300
SELECTED = {"p11": 6003, "p12": 6002}  # best of 40 on dev worlds 100-129, chosen before this protocol


def run(engine_src: str, out_path: str, version: str) -> dict:
    sys.path.insert(0, engine_src)
    from i3.lab import worldgen
    from i3.lab.probes import reference_survival
    from i3.modules.genome import generation_zero
    from i3.runtime.life import run_life
    gen_src = Path(worldgen.__file__).read_bytes()
    rows = []
    for k, seed in enumerate(SEEDS):
        spec = worldgen.generate("R", seed, development=False)
        far = [q for q, s in spec.water.items() if s.stock is None][0]
        g = generation_zero(70000 + k)
        a = run_life(g, worldgen.generate("R", seed, development=False), 80000 + k,
                     H_REVISION, keep_trace=True)
        b = run_life(g, worldgen.generate("R", seed, development=False), 80000 + k, H_REVISION)
        trace = a.pop("trace")
        rows.append({"family": "R", "seed": seed, "alive": a["terminal"] == "censored",
                     "steps": a["steps_lived"], "causes": a["death_causes"],
                     "used_far_well": any(r["action"] == "boire" and tuple(r["pos"]) == far
                                          for r in trace),
                     "replay": a["trace_head"] == b["trace_head"], "ms": a["mean_step_ms"]})
        spec = worldgen.generate("dev", seed, development=False)
        a = run_life(g, spec, 80000 + k, H_GENERAL)
        b = run_life(g, worldgen.generate("dev", seed, development=False), 80000 + k, H_GENERAL)
        sel = run_life(generation_zero(SELECTED[version]),
                       worldgen.generate("dev", seed, development=False), 80000 + k, H_GENERAL)
        rows.append({"family": "dev", "seed": seed, "alive": a["terminal"] == "censored",
                     "steps": a["steps_lived"], "causes": a["death_causes"],
                     "replay": a["trace_head"] == b["trace_head"], "ms": a["mean_step_ms"],
                     "selected_alive": sel["terminal"] == "censored"})
    ref = {"R": sum(reference_survival(worldgen.generate("R", s, development=False), H_REVISION)
                    >= H_REVISION for s in SEEDS),
           "dev": sum(reference_survival(worldgen.generate("dev", s, development=False), H_GENERAL)
                      >= H_GENERAL for s in SEEDS)}
    report = {"protocol": PROTOCOL, "version": version, "engine_src": engine_src,
              "worldgen_sha256": sha256(gen_src).hexdigest(), "reference_alive": ref,
              "lives": rows}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


def sign_test(wins: int, losses: int) -> float:
    """One-sided exact sign test on discordant pairs."""
    n = wins + losses
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n


def verdict(p11: dict, p12: dict, g2_regression: dict) -> dict:
    out = {"same_worldgen": p11["worldgen_sha256"] == p12["worldgen_sha256"]}
    for fam in ("R", "dev"):
        a = [r for r in p11["lives"] if r["family"] == fam]
        b = [r for r in p12["lives"] if r["family"] == fam]
        wins = sum(1 for x, y in zip(a, b) if y["alive"] and not x["alive"])
        losses = sum(1 for x, y in zip(a, b) if x["alive"] and not y["alive"])
        out[fam] = {"alive_p11": sum(r["alive"] for r in a), "alive_p12": sum(r["alive"] for r in b),
                    "p12_only": wins, "p11_only": losses, "sign_test_p": round(sign_test(wins, losses), 6),
                    "reference_alive": p12["reference_alive"][fam]}
        if fam == "R":
            out[fam]["used_far_well_p11"] = sum(r["used_far_well"] for r in a)
            out[fam]["used_far_well_p12"] = sum(r["used_far_well"] for r in b)
        else:
            out[fam]["selected_alive_p11"] = sum(r["selected_alive"] for r in a)
            out[fam]["selected_alive_p12"] = sum(r["selected_alive"] for r in b)
    crit = {
        "A_revision_superiority": out["R"]["alive_p12"] > out["R"]["alive_p11"]
        and out["R"]["sign_test_p"] <= 0.05,
        "B_general_non_inferiority": out["dev"]["alive_p12"] >= out["dev"]["alive_p11"] - 5,
        "C_g2_regression": all(v["pass"] for v in g2_regression["verdict_by_world"].values()),
        "D_replay": all(r["replay"] for r in p12["lives"]),
        "D_budget_ms": round(sum(r["ms"] for r in p12["lives"]) / len(p12["lives"]), 4),
    }
    crit["D_budget"] = crit["D_budget_ms"] <= 1.0
    out["criteria"] = crit
    ok = (out["same_worldgen"] and crit["A_revision_superiority"] and crit["B_general_non_inferiority"]
          and crit["C_g2_regression"] and crit["D_replay"] and crit["D_budget"])
    out["decision"] = "ADOPT_P1_2" if ok else "REJECT_P1_2_KEEP_P1_1"
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
