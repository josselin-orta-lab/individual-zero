"""Gate under selection (ADR-0015): judge an architecture by its selected genomes.

One run per architecture ("arm"). The engine (mind, genome, body, world,
runtime) comes from ENGINE_SRC; the laboratory files (world generator, probes)
always come from this file's own tree, so every arm meets the same worlds.

    python selection_gate.py ENGINE_SRC ARM OUTPUT.json

Selection: K candidates generation_zero(s) on development worlds; keep the m
best by persistence. Evaluation: those m genomes on reserved worlds never run
before; per world, the number of selected genomes that survive (0..m).
"""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import sys
import time

LAB = Path(__file__).resolve().parent
CANDIDATES = tuple(range(6000, 6040))   # K = 40
KEEP = 5                                 # m = 5
HORIZON = {"dev": 300, "R": 400}
SELECTION = {"dev": tuple(range(100, 130)), "R": tuple(range(100, 130))}
EVALUATION = {"dev": tuple(range(1_000_100, 1_000_200)), "R": tuple(range(1_000_100, 1_000_200))}


def _lab_module(name):
    spec = importlib.util.spec_from_file_location(f"i3_gate_{name}", LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(engine_src: str, arm: str, out_path: str) -> dict:
    sys.path.insert(0, engine_src)
    from i3.modules.genome import digest, generation_zero
    from i3.runtime.life import run_life
    import i3.modules.body as body_mod
    import i3.modules.world as world_mod
    worldgen = _lab_module("worldgen")
    started = time.time()

    def world(fam, seed):
        return worldgen.generate(fam, seed, development=seed < worldgen.RESERVED_FROM)

    ranking = []
    for c in CANDIDATES:
        g = generation_zero(c)
        alive = steps = 0
        for fam, seeds in SELECTION.items():
            for i, s in enumerate(seeds):
                r = run_life(g, world(fam, s), 9000 + i, HORIZON[fam])
                alive += r["terminal"] == "censored"
                steps += r["steps_lived"]
        ranking.append((-alive, -steps, c))
    ranking.sort()
    selected = [c for _, _, c in ranking[:KEEP]]
    evaluation = {}
    ms, replay_ok = [], True
    for fam, seeds in EVALUATION.items():
        per_world = []
        for k, s in enumerate(seeds):
            survivors = 0
            for rank, c in enumerate(selected):
                r = run_life(generation_zero(c), world(fam, s), 80000 + k, HORIZON[fam])
                survivors += r["terminal"] == "censored"
                ms.append(r["mean_step_ms"])
                if rank == 0:
                    again = run_life(generation_zero(c), world(fam, s), 80000 + k, HORIZON[fam])
                    replay_ok &= again["trace_head"] == r["trace_head"]
            rnd = run_life(generation_zero(70000 + k), world(fam, s), 80000 + k, HORIZON[fam])
            per_world.append({"seed": s, "selected_alive": survivors,
                              "random_alive": rnd["terminal"] == "censored"})
        evaluation[fam] = per_world
    report = {
        "protocol": "i3-gate-under-selection-v1", "arm": arm, "engine_src": engine_src,
        "hashes": {n: sha256(Path(m.__file__).read_bytes()).hexdigest()
                   for n, m in (("body", body_mod), ("world", world_mod))}
        | {"worldgen": sha256((LAB / "worldgen.py").read_bytes()).hexdigest()},
        "candidates": list(CANDIDATES), "keep": KEEP,
        "ranking": [{"seed": c, "selection_alive": -a, "selection_steps": -st} for a, st, c in ranking],
        "selected": selected,
        "selected_genomes": {c: digest(generation_zero(c)) for c in selected},
        "evaluation": evaluation, "replay_identical": replay_ok,
        "mean_step_ms": round(sum(ms) / len(ms), 4), "wall_seconds": round(time.time() - started, 1),
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


def reference(out_path: str) -> dict:
    """Systematic reference searcher on the evaluation worlds (descriptive)."""
    sys.path.insert(0, str(LAB.parents[1]))
    worldgen, probes = _lab_module("worldgen"), _lab_module("probes")
    out = {fam: sum(probes.reference_survival(worldgen.generate(fam, s, development=False),
                                              HORIZON[fam]) >= HORIZON[fam] for s in seeds)
           for fam, seeds in EVALUATION.items()}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1)
    return out


def sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n


def compare(base: dict, cand: dict) -> dict:
    """Paired per-world comparison of selected-genome survival (candidate vs base)."""
    out = {}
    wins = losses = 0
    for fam in EVALUATION:
        a = [w["selected_alive"] for w in base["evaluation"][fam]]
        b = [w["selected_alive"] for w in cand["evaluation"][fam]]
        fw = sum(1 for x, y in zip(a, b) if y > x)
        fl = sum(1 for x, y in zip(a, b) if y < x)
        wins, losses = wins + fw, losses + fl
        out[fam] = {"base": sum(a), "cand": sum(b), "worlds_better": fw, "worlds_worse": fl}
    out["pooled"] = {"base": sum(out[f]["base"] for f in EVALUATION),
                     "cand": sum(out[f]["cand"] for f in EVALUATION),
                     "worlds_better": wins, "worlds_worse": losses,
                     "sign_test_p": round(sign_test(wins, losses), 6)}
    return out


FAMILY_MARGIN = 15   # non-inferiority per family, out of 500 selected lives
SIMPLER_MARGIN = 10  # if two candidates qualify within this pooled gap, prefer fewer genes


def decide(base: dict, candidates: dict, g2: dict, genes: dict) -> dict:
    """G2d rule, frozen before execution (see G2D_SELECTION_GATE_PREREG.md)."""
    out = {"comparisons": {}, "qualified": []}
    for name, cand in candidates.items():
        cmp = compare(base, cand)
        floors = {
            "g2_regression": all(v["pass"] for v in g2[name]["verdict_by_world"].values()),
            "replay": cand["replay_identical"],
            "budget": cand["mean_step_ms"] <= 1.0,
            "same_worlds": cand["hashes"] == base["hashes"],
        }
        qualifies = (cmp["pooled"]["cand"] > cmp["pooled"]["base"]
                     and cmp["pooled"]["sign_test_p"] <= 0.05
                     and all(cmp[f]["cand"] >= cmp[f]["base"] - FAMILY_MARGIN for f in EVALUATION)
                     and all(floors.values()))
        out["comparisons"][name] = {"vs_base": cmp, "floors": floors, "qualifies": qualifies,
                                    "mean_step_ms": cand["mean_step_ms"]}
        if qualifies:
            out["qualified"].append(name)
    q = sorted(out["qualified"], key=lambda n: -compare(base, candidates[n])["pooled"]["cand"])
    if not q:
        out["decision"] = "KEEP_BASE"
    elif len(q) == 1:
        out["decision"] = f"ADOPT_{q[0]}"
    else:
        top, second = q[0], q[1]
        gap = (compare(base, candidates[top])["pooled"]["cand"]
               - compare(base, candidates[second])["pooled"]["cand"])
        if gap <= SIMPLER_MARGIN and genes[second] < genes[top]:
            top = second
        out["decision"] = f"ADOPT_{top}"
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--reference":
        print(json.dumps(reference(sys.argv[2])))
    else:
        run(sys.argv[1], sys.argv[2], sys.argv[3])
