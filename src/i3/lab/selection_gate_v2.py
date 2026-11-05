"""Gate under selection on the funded v2 substrate (ADR-0015; G2e).

One run per architecture ("arm"). The engine (mind, genome, body, world,
runtime) comes from ENGINE_SRC; the laboratory files (world generator, probes)
always come from THIS file's tree, so every arm meets the same worlds.

    python selection_gate_v2.py ENGINE_SRC ARM OUTPUT.json
    python selection_gate_v2.py --reference OUTPUT.json   (descriptive only)

Selection: K candidates generation_zero(s) on development worlds; keep the m
best by persistence. Evaluation: those m genomes on FRESH reserved worlds;
per world, the number of selected genomes that survive (0..m). In family R,
revision latency is counted from the first personally available evidence that
the near well is dry (the drink that empties it) to the first drink at the far
well. Probes are descriptive only (not validated, not cost-matched; P2).
"""
from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import sys
import time

PROTOCOL = "i3-g2e-selection-v2"
LAB = Path(__file__).resolve().parent
CANDIDATES = tuple(range(6000, 6040))   # K = 40
KEEP = 5                                 # m = 5
HORIZON = {"dev": 300, "R": 400}
SELECTION = {"dev": tuple(range(100, 130)), "R": tuple(range(100, 130))}
EVALUATION = {"dev": tuple(range(1_000_200, 1_000_300)), "R": tuple(range(1_000_200, 1_000_300))}
FAMILY_MARGIN = 15     # non-inferiority per family, out of 500 selected lives
SIMPLER_MARGIN = 10    # (two candidates only) prefer fewer genes within this gap
STEP_CEILING_MS = 2.0  # engineering sanity ceiling on this host, not a science claim
G2_MARGIN = 1          # candidate drinkers per G2 world >= base - 1


def _lab_module(name):
    spec = importlib.util.spec_from_file_location(f"i3_gate_{name}", LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def revision_latency(spec, trace):
    """(depleted, latency) for a family-R life; latency None if never revised."""
    near = [q for q, s in spec.water.items() if s.stock is not None and not s.restock_every]
    far = [q for q, s in spec.water.items() if s.stock is None]
    if len(near) != 1 or len(far) != 1:
        raise ValueError("family R world must have one finite near well and one far well")
    near, far = near[0], far[0]
    stock = spec.water[near].stock
    drinks_near, t_evidence = 0, None
    for rec in trace:
        if rec.get("action") != "boire":
            continue
        pos = tuple(rec["pos"])
        if pos == near and t_evidence is None:
            drinks_near += 1
            if drinks_near == stock:
                t_evidence = rec["t"]
        elif pos == far and t_evidence is not None:
            return True, rec["t"] - t_evidence
    return t_evidence is not None, None


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
                r = run_life(g, world(fam, s), 9000 + i, HORIZON[fam], protocol=PROTOCOL)
                alive += r["terminal"] == "censored"
                steps += r["steps_lived"]
        ranking.append((-alive, -steps, c))
    ranking.sort()
    selected = [c for _, _, c in ranking[:KEEP]]
    evaluation, ms, replay_ok, shortfall = {}, [], True, 0
    inactive = lived = 0
    for fam, seeds in EVALUATION.items():
        per_world = []
        for k, s in enumerate(seeds):
            survivors, latencies, depleted = 0, [], 0
            for rank, c in enumerate(selected):
                r = run_life(generation_zero(c), world(fam, s), 80000 + k, HORIZON[fam],
                             keep_trace=(fam == "R"), protocol=PROTOCOL)
                survivors += r["terminal"] == "censored"
                ms.append(r["mean_step_ms"])
                shortfall += r["cognitive_accounting"].get("shortfall_steps", 0) or 0
                inactive += r["cognitive_accounting"].get("inactive_steps", 0) or 0
                lived += r["steps_lived"]
                if fam == "R":
                    dep, lat = revision_latency(world(fam, s), r["trace"])
                    depleted += dep
                    latencies.append(lat)
                if rank == 0:
                    again = run_life(generation_zero(c), world(fam, s), 80000 + k, HORIZON[fam],
                                     protocol=PROTOCOL)
                    replay_ok &= again["trace_head"] == r["trace_head"]
            rnd = run_life(generation_zero(70000 + k), world(fam, s), 80000 + k, HORIZON[fam],
                           protocol=PROTOCOL)
            row = {"seed": s, "selected_alive": survivors, "random_alive": rnd["terminal"] == "censored"}
            if fam == "R":
                row["depleted"] = depleted
                row["latencies"] = latencies
            per_world.append(row)
        evaluation[fam] = per_world
    report = {
        "protocol": PROTOCOL, "arm": arm, "engine_src": engine_src,
        "hashes": {n: sha256(Path(m.__file__).read_bytes()).hexdigest()
                   for n, m in (("body", body_mod), ("world", world_mod))}
        | {"worldgen": sha256((LAB / "worldgen.py").read_bytes()).hexdigest()},
        "candidates": list(CANDIDATES), "keep": KEEP,
        "ranking": [{"seed": c, "selection_alive": -a, "selection_steps": -st} for a, st, c in ranking],
        "selected": selected,
        "selected_genomes": {c: digest(generation_zero(c)) for c in selected},
        "evaluation": evaluation, "replay_identical": replay_ok,
        "shortfall_steps_total": shortfall,
        "inactive_fraction_selected": round(inactive / max(1, lived), 4),
        "mean_step_ms": round(sum(ms) / len(ms), 4), "wall_seconds": round(time.time() - started, 1),
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


def reference(out_path: str) -> dict:
    """Probes on evaluation and selection worlds (descriptive; not cost-matched)."""
    sys.path.insert(0, str(LAB.parents[1]))
    worldgen, probes = _lab_module("worldgen"), _lab_module("probes")
    out = {}
    for name, sets in (("evaluation", EVALUATION), ("selection", SELECTION)):
        out[name] = {fam: sum(probes.reference_survival(
            worldgen.generate(fam, s, development=s < worldgen.RESERVED_FROM), HORIZON[fam])
            >= HORIZON[fam] for s in seeds) for fam, seeds in sets.items()}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1)
    return out


def sign_test(wins: int, losses: int) -> float:
    n = wins + losses
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n


def compare(base: dict, cand: dict) -> dict:
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
                     "sign_test_p": sign_test(wins, losses)}
    return out


def decide(base: dict, candidates: dict, g2_base: dict, g2: dict, genes: dict) -> dict:
    """G2e rule, frozen before execution (see G2E_P13_V2_PREREG.md)."""
    out = {"comparisons": {}, "qualified": []}
    base_drink = {k: v["drank"] for k, v in g2_base["verdict_by_world"].items()}
    for name, cand in candidates.items():
        cmp = compare(base, cand)
        floors = {
            "g2_not_worse": all(v["drank"] >= base_drink[k] - G2_MARGIN
                                for k, v in g2[name]["verdict_by_world"].items()),
            "replay": cand["replay_identical"],
            "step_ceiling": cand["mean_step_ms"] <= STEP_CEILING_MS,
            "same_worlds": cand["hashes"] == base["hashes"],
            "no_shortfall": cand["shortfall_steps_total"] == 0,
        }
        qualifies = (cmp["pooled"]["cand"] > cmp["pooled"]["base"]
                     and cmp["pooled"]["sign_test_p"] <= 0.05
                     and all(cmp[f]["cand"] >= cmp[f]["base"] - FAMILY_MARGIN for f in EVALUATION)
                     and all(floors.values()))
        out["comparisons"][name] = {"vs_base": cmp, "floors": floors, "qualifies": qualifies}
        if qualifies:
            out["qualified"].append(name)
    q = sorted(out["qualified"], key=lambda n: -compare(base, candidates[n])["pooled"]["cand"])
    if not q:
        out["decision"] = "KEEP_BASE"
    else:
        top = q[0]
        if len(q) > 1:
            gap = (compare(base, candidates[q[0]])["pooled"]["cand"]
                   - compare(base, candidates[q[1]])["pooled"]["cand"])
            if gap <= SIMPLER_MARGIN and genes[q[1]] < genes[q[0]]:
                top = q[1]
        out["decision"] = f"ADOPT_{top}"
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--reference":
        print(json.dumps(reference(sys.argv[2])))
    else:
        run(sys.argv[1], sys.argv[2], sys.argv[3])
