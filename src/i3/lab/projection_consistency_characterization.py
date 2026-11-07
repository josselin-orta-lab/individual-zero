"""Frozen software characterization of P1.3 projection bootstrap consistency.

Protocol: docs/STAGE1_PROJECTION_CONSISTENCY.md. No World, no life, no study
index. Schemes: reference "chunk_end", candidate "trapezoid", and the per-step
diagnostic truth (255 unit chunks, chunk_end accounting).

    python -m i3.lab.projection_consistency_characterization OUTPUT.json
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget
from ..modules.genome import generation_zero, midpoint
from ..modules.mind import Mind

SCHEMA = "i3-projection-consistency-characterization/v1"
HORIZON = 6
PER_STEP = (1,) * 255
BIAS_LIMIT = 1e-3
PLANS = {
    "prefix": (("se_deplacer",),),
    "plus_1_wait": (("se_deplacer",), ("attendre",)),
    "plus_3_waits": (("se_deplacer",), ("attendre",), ("attendre",), ("attendre",)),
}


def genomes():
    yield "midpoint", midpoint()
    for seed in range(6000, 6005):
        yield f"g0-{seed}", generation_zero(seed)


def bodies():
    for channel in range(5):
        for level in (10., 20., 30., 40., 50.):
            body = [80.] * 5
            body[channel] = level
            yield tuple(body)
    yield (80.,) * 5
    yield (80., 30., 30., 80., 80.)


def make_mind(genome, sleep_learned=True, projection_equivalent=False):
    mind = Mind(genome, 97)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    if projection_equivalent:
        # Wait moves exactly as the projection drifts (energy, vigilance held).
        mind.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    else:
        mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    if sleep_learned:
        mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def configure(mind, scheme):
    if scheme == "per_step":
        mind.proj_chunks = PER_STEP
        mind.projection_accounting = "chunk_end"
    else:
        mind.projection_accounting = scheme
    return mind


def values(genome, body, scheme, **fixture):
    out = {}
    for name, plan in PLANS.items():
        mind = configure(make_mind(genome, **fixture), scheme)
        out[name] = mind.simulate(body, plan, HORIZON, CognitiveBudget(body, BodyLaws()))[0]
    return out


def paid_units(scheme):
    mind = configure(make_mind(midpoint()), scheme)
    budget = CognitiveBudget((80.,) * 5, BodyLaws())
    mind.project((80., 30., 30., 80., 80.), mind._drift, budget)
    return budget.work.simulated_steps


def run(out_path):
    schemes = ("chunk_end", "trapezoid", "per_step")
    fixtures = {"sleep_learned": {"sleep_learned": True},
                "sleep_unlearned": {"sleep_learned": False},
                "projection_equivalent": {"sleep_learned": False,
                                          "projection_equivalent": True}}
    stats = {s: {"max_abs_gap_plus_1": 0.0, "max_abs_gap_plus_3": 0.0,
                 "max_abs_prefix_error_vs_per_step": 0.0,
                 "max_decision_bias_vs_per_step": 0.0} for s in schemes}
    invariant = {s: 0.0 for s in schemes}
    cases = 0
    for fname, fixture in fixtures.items():
        for _, genome in genomes():
            for body in bodies():
                cases += 1
                truth = values(genome, body, "per_step", **fixture)
                for scheme in schemes:
                    v = truth if scheme == "per_step" else values(genome, body, scheme, **fixture)
                    g1 = v["plus_1_wait"] - v["prefix"]
                    g3 = v["plus_3_waits"] - v["prefix"]
                    st = stats[scheme]
                    st["max_abs_gap_plus_1"] = max(st["max_abs_gap_plus_1"], abs(g1))
                    st["max_abs_gap_plus_3"] = max(st["max_abs_gap_plus_3"], abs(g3))
                    st["max_abs_prefix_error_vs_per_step"] = max(
                        st["max_abs_prefix_error_vs_per_step"], abs(v["prefix"] - truth["prefix"]))
                    bias = max(abs(g1 - (truth["plus_1_wait"] - truth["prefix"])),
                               abs(g3 - (truth["plus_3_waits"] - truth["prefix"])))
                    st["max_decision_bias_vs_per_step"] = max(st["max_decision_bias_vs_per_step"], bias)
                    if fname == "projection_equivalent":
                        invariant[scheme] = max(invariant[scheme], abs(g1), abs(g3))
    units = {s: paid_units(s) for s in schemes}
    promoted = (stats["trapezoid"]["max_decision_bias_vs_per_step"] <= BIAS_LIMIT
                and units["trapezoid"] == units["chunk_end"])
    report = {"schema": SCHEMA, "protocol": "STAGE1_PROJECTION_CONSISTENCY.md",
              "world_access": False, "lives": 0, "cases_per_scheme": cases,
              "stats": stats, "projection_equivalent_invariant_max_gap": invariant,
              "paid_simulated_units_per_projection": units,
              "selection": {"bias_limit": BIAS_LIMIT,
                            "trapezoid_bias": stats["trapezoid"]["max_decision_bias_vs_per_step"],
                            "equal_paid_units": units["trapezoid"] == units["chunk_end"],
                            "verdict": "TRAPEZOID_PROMOTED_AS_OPT_IN_CANDIDATE" if promoted
                            else "NO_CANDIDATE_PROMOTED"}}
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print(json.dumps({k: rep[k] for k in ("stats", "projection_equivalent_invariant_max_gap",
                                           "paid_simulated_units_per_projection", "selection")}, indent=1))
