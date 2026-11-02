"""Predeclared reproducible *varying* hidden worlds, exploratory I2 only.

Unlike order-shuffle smoke, the seed changes a world schedule before
genesis. Neither researcher seed nor future payoff is a subjective cue.
All four policies run on identical seeded physics in fresh paid owners.
"""
from __future__ import annotations
import random
import tempfile
from pathlib import Path
from i2.runtime.isolated_prototype import IsolatedI2, world_endpoint

SEEDS = (101, 211, 307, 401, 503)
POLICIES = (
    ("observational", False, False),
    ("last_resort", True, False),
    ("deadline", False, True),
    ("combined", True, True),
)
HORIZON = 16


def schedule(seed: int) -> tuple[int, ...]:
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("seed not predeclared")
    rng = random.Random(seed)
    # First observed meal is adverse in every predeclared world.
    # A later latent restoration and possible renewed reversal vary in
    # physical 2-tick epochs; no future knowledge enters the individual.
    recovery = rng.choice((3, 4, 5))
    relapse = rng.choice((6, 7, 8, 9))
    return tuple(-8 if i < recovery or i >= relapse else 6
                 for i in range(10))


def run_panel() -> dict:
    results = {}
    with tempfile.TemporaryDirectory(prefix="i2-seeded-varying-") as root:
        for seed in SEEDS:
            phases = schedule(seed)
            arms = {}
            for name, reflex, deadline in POLICIES:
                life = IsolatedI2.create(
                    Path(root) / f"{seed}-{name}.sqlite",
                    learning=True, impulses=phases,
                    extended_postcontact_study=True,
                    initial_energy=40, initial_uc=60, resources=8,
                    last_resort_exploration=reflex,
                    deadline_aware=deadline,
                )
                run = life.run_world(ticks=HORIZON)
                audit = life.audit()
                decisions = life.decision_evidence()
                arms[name] = {
                    "endpoint": world_endpoint(run),
                    "actions": tuple(d["chosen"] for d in decisions),
                    "decision_ticks": tuple(d["physical_ticks_before"] for d in decisions),
                    "last_resort_raises": sum(bool(d["last_resort_priority_applied"]) for d in decisions),
                    "deadline_suppressions": sum(bool(d["deadline_infeasible_collect_suppressed"]) for d in decisions),
                    "audit_uc": audit["actual_uc_spent"],
                    "m11_authenticated": audit["m11_authenticated"],
                }
            results[str(seed)] = {"hidden_impulses_researcher_only": phases, "arms": arms}
    return {
        "protocol": "i2-seeded-varying-hidden-world-exploratory-v1",
        "seeds": SEEDS,
        "physical_tick_horizon": HORIZON,
        "results": results,
        "statistics": "DESCRIPTIVE_ONLY_SMALL_NONINDEPENDENT_PANEL",
        "generalized_survival_benefit": "NOT_ESTABLISHED",
        "natural_learning": "NOT_ESTABLISHED",
    }
