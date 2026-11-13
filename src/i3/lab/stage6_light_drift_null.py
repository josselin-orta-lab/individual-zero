"""Genome-only neutral drift model for sizing a Stage-6-light protocol.

Numbers only: no World, Mind, run_life, runner or life is created or read.
The model, grid, consistency checks and recommendation rule were frozen
before this code in
``docs/studies/stage6-light-preparation/STAGE6_LIGHT_DRIFT_NULL_PREFLIGHT_2026-11-13.md``.

It says which shift between a persistence-selected arm and a random-parent
arm would be visible for a quantity WITHOUT effect on persistence. It never
says whether selection produces a shift, and it is not a retrospective test
of P3. Never a scientific verdict.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import accumulate
import json
from math import comb, fsum, isfinite, sqrt
import random
from statistics import NormalDist

SCHEMA = "i3-stage6-light-drift-null/v1"
PREFLIGHT_COMMIT = "d1437b301793858170cfc5a3e989ca44e5c79d33"
SEED_LABEL = "i3-stage6-light-drift-null/v1"

ARMS = ("selected", "random_parent")
REGIMES = ("fresh", "heritable")
GRID_N = (6, 12, 24, 48)
GRID_G = (3, 4, 6, 8)  # generations, generation zero included
REPLICATES = 4000
MUTATION_SCALE = 0.1  # genome.mutate: sigma = scale x gene range, then clamp
QUANTITIES = ("z", "beta_u_eff")

POPULATION_OPTIONS = (8, 12, 16)
ALPHA = 0.05
POWER = 0.80
LIVES_PER_GENOME = 6  # three F0 families x two repeats, as in P3
HORIZON = 400
# Exact SD of b * (1 + 0.5 e), b ~ U[0, 2], e ~ U[-1, 1], independent.
SD_G0_BETA_U_EFF = sqrt((4.0 / 3.0) * (1.0 + 0.25 / 3.0) - 1.0)
THRESHOLD_FRACTIONS = (0.5, 0.25)
S1_BRACKET = (0.10, 0.45)
DIGITS = 9


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def _r(value: float) -> float:
    if not isfinite(value):
        raise ValueError("nonfinite drift-null value")
    return round(value, DIGITS)


def _mutate(rng: random.Random, value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value + rng.gauss(0.0, MUTATION_SCALE * (hi - lo))))


def simulate_population(rng: random.Random, n: int, generations: int,
                        regime: str) -> dict:
    """One paired population: same founders, two parent rules, no fitness effect."""
    if not (type(n) is int and n >= 1 and type(generations) is int
            and generations >= 1 and regime in REGIMES):
        raise ValueError("invalid drift-null configuration")
    z = [rng.uniform(0.0, 1.0) for _ in range(n)]
    b = [rng.uniform(0.0, 2.0) for _ in range(n)]
    e = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    latent = [rng.random() for _ in range(n)]
    slots = range(n)
    cum_weights = list(accumulate(range(n, 0, -1)))  # P3 rank weights N..1
    state = {arm: (list(z), list(b), list(e), list(slots), list(latent))
             for arm in ARMS}
    for _ in range(generations - 1):
        for arm in ARMS:
            zs, bs, es, founders, lat = state[arm]
            if arm == "selected":
                if regime == "fresh":
                    order = list(slots)
                    rng.shuffle(order)
                else:
                    order = sorted(slots, key=lambda s: (-lat[s], s))
                parents = [order[i] for i in
                           rng.choices(slots, cum_weights=cum_weights, k=n)]
            else:
                parents = rng.choices(slots, k=n)
            state[arm] = (
                [_mutate(rng, zs[p], 0.0, 1.0) for p in parents],
                [_mutate(rng, bs[p], 0.0, 2.0) for p in parents],
                [_mutate(rng, es[p], -1.0, 1.0) for p in parents],
                [founders[p] for p in parents],
                [lat[p] for p in parents],
            )
    out = {}
    for arm in ARMS:
        zs, bs, es, founders, _ = state[arm]
        out[arm] = {
            "z": fsum(zs) / n,
            "beta_u_eff": fsum(bv * (1.0 + 0.5 * ev)
                               for bv, ev in zip(bs, es)) / n,
            "founders": len(set(founders)),
            "z_at_bound": sum(1 for v in zs if v in (0.0, 1.0)) / n,
        }
    return out


def run_configuration(n: int, generations: int, regime: str,
                      replicates: int = REPLICATES) -> dict:
    if type(replicates) is not int or replicates < 2:
        raise ValueError("at least two replicate populations required")
    contrasts = {q: [] for q in QUANTITIES}
    founders = {arm: 0 for arm in ARMS}
    at_bound = {arm: 0.0 for arm in ARMS}
    for replicate in range(replicates):
        rng = random.Random(
            f"{SEED_LABEL}:{n}:{generations}:{regime}:{replicate}")
        population = simulate_population(rng, n, generations, regime)
        for q in QUANTITIES:
            contrasts[q].append(population["selected"][q]
                                - population["random_parent"][q])
        for arm in ARMS:
            founders[arm] += population[arm]["founders"]
            at_bound[arm] += population[arm]["z_at_bound"]
    stats = {}
    for q in QUANTITIES:
        values = contrasts[q]
        mean = fsum(values) / replicates
        sd = sqrt(fsum((v - mean) ** 2 for v in values) / (replicates - 1))
        stats[q] = {
            "mean": _r(mean), "sd": _r(sd),
            "mean_standard_error": _r(sd / sqrt(replicates)),
            "positive_share": _r(sum(1 for v in values if v > 0.0) / replicates),
        }
    return {
        "n": n, "generations": generations, "regime": regime,
        "replicates": replicates, "contrast": stats,
        "mean_founders_left": {arm: _r(founders[arm] / replicates) for arm in ARMS},
        "mean_z_at_bound": {arm: _r(at_bound[arm] / replicates) for arm in ARMS},
    }


def sign_threshold(populations: int, alpha: float = ALPHA):
    """Smallest concordant-sign count with exact two-sided probability <= alpha."""
    for k in range(populations // 2 + 1, populations + 1):
        tail = 2.0 * sum(comb(populations, j)
                         for j in range(k, populations + 1)) / 2 ** populations
        if tail <= alpha:
            return k, tail
    return None, None


def detectable_ratio(populations: int, k: int, power: float = POWER):
    """Per-population favourable-sign probability reaching ``power`` and the
    matching shift in units of the per-population contrast SD (normal model)."""
    def reach(pi: float) -> float:
        return fsum(comb(populations, j) * pi ** j * (1.0 - pi) ** (populations - j)
                    for j in range(populations + 1)
                    if j >= k or j <= populations - k)
    lo, hi = 0.5, 1.0 - 1e-12
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if reach(mid) >= power:
            hi = mid
        else:
            lo = mid
    return hi, NormalDist().inv_cdf(hi)


def _symmetric(config: dict, quantity: str) -> bool:
    stat = config["contrast"][quantity]
    share_se = sqrt(0.25 / config["replicates"])
    return (abs(stat["mean"]) <= 4.0 * stat["mean_standard_error"]
            and abs(stat["positive_share"] - 0.5) <= 4.0 * share_se)


def _cheapest(table: list, limit: float):
    eligible = [row for row in table if row["regime"] == "heritable"
                and row["detectable_shift"]["beta_u_eff"] <= limit]
    if not eligible:
        return "NONE_IN_GRID"
    return min(eligible, key=lambda row: (
        row["lives"], row["generations"], row["n"], row["populations"]))


def audit(grid_n=GRID_N, grid_g=GRID_G, regimes=REGIMES,
          replicates: int = REPLICATES) -> dict:
    """Run the frozen grid (or a reduced test grid) and apply the frozen rules."""
    configs = [run_configuration(n, g, regime, replicates)
               for regime in regimes for n in grid_n for g in grid_g]
    criteria = []
    for populations in POPULATION_OPTIONS:
        k, tail = sign_threshold(populations)
        pi, ratio = detectable_ratio(populations, k)
        criteria.append({
            "populations": populations, "threshold": k,
            "two_sided_probability": _r(tail),
            "per_population_probability_for_power": _r(pi),
            "detectable_ratio": _r(ratio),
        })
    table = []
    for config in configs:
        for criterion in criteria:
            lives = (criterion["populations"] * config["generations"] * config["n"]
                     * LIVES_PER_GENOME * len(ARMS))
            table.append({
                "regime": config["regime"], "n": config["n"],
                "generations": config["generations"],
                "populations": criterion["populations"],
                "threshold": criterion["threshold"],
                "lives": lives, "max_steps": lives * HORIZON,
                "detectable_shift": {
                    q: _r(criterion["detectable_ratio"] * config["contrast"][q]["sd"])
                    for q in QUANTITIES},
            })
    s1_configs = [c for c in configs if (c["n"], c["generations"]) == (6, 3)]
    s1_evaluated = len(s1_configs) == len(REGIMES)
    s1 = all(S1_BRACKET[0] <= c["contrast"]["z"]["sd"] <= S1_BRACKET[1]
             for c in s1_configs)
    s2 = all(_symmetric(c, "z") for c in configs)
    composite = all(_symmetric(c, "beta_u_eff") for c in configs)
    adequate = s1 and s2
    report = {
        "schema": SCHEMA,
        "status": ("DRIFT_NULL_SIZING_COMPLETE" if adequate
                   else "DRIFT_NULL_MODEL_INADEQUATE"),
        "scientific_verdict": "NOT_ISSUED",
        "preflight_commit": PREFLIGHT_COMMIT,
        "worlds_opened": 0, "lives_created": 0,
        "parameters": {
            "grid_n": list(grid_n), "grid_g": list(grid_g),
            "regimes": list(regimes), "replicates": replicates,
            "seed_label": SEED_LABEL, "mutation_scale": MUTATION_SCALE,
            "population_options": list(POPULATION_OPTIONS),
            "alpha": ALPHA, "power": POWER,
            "lives_per_genome": LIVES_PER_GENOME, "horizon": HORIZON,
            "sd_g0_beta_u_eff": _r(SD_G0_BETA_U_EFF),
            "threshold_fractions": list(THRESHOLD_FRACTIONS),
        },
        "checks": {
            "s1_order_of_magnitude_evaluated": s1_evaluated,
            "s1_order_of_magnitude": s1,
            "s2_symmetry_z": s2,
            "composite_symmetry_beta_u_eff": composite,
        },
        "flags": [] if composite else ["COMPOSITE_NULL_ASYMMETRY"],
        "criteria": criteria,
        "configurations": configs,
        "sizing_table": table,
        "recommendation": ({
            str(fraction): _cheapest(table, fraction * SD_G0_BETA_U_EFF)
            for fraction in THRESHOLD_FRACTIONS} if adequate else None),
    }
    report["digest_sha256"] = sha256(_canonical(report).encode("utf-8")).hexdigest()
    return report


def main() -> int:
    print(_canonical(audit()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
