"""Longitudinal, paid I2 survival comparison after known safe-water disclosure.

A separate 10-phase exploratory life, unchanged adverse berry physics.
The water flag is set at fresh genesis; no new rescue is injected during
the run, and researcher-only endpoints are not perceived by the subject.
"""
from __future__ import annotations
import tempfile
from pathlib import Path
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, world_endpoint

POLICIES = (
    ("observational", False, False),
    ("reflex", True, False),
    ("deadline", False, True),
    ("combined", True, True),
)
HORIZON = 20

def longitudinal_water_panel() -> dict:
    rows = {}
    with tempfile.TemporaryDirectory(prefix="i2-water-longitudinal-") as root:
        for water in (False, True):
            arms = {}
            for name, reflex, deadline in POLICIES:
                life = IsolatedI2.create(
                    Path(root) / f"{int(water)}-{name}.sqlite",
                    learning=True,
                    impulses=SCENARIOS["adverse"] + (-8, -8),
                    extended_postcontact_study=True,
                    restorative_water_study=water,
                    last_resort_exploration=reflex,
                    deadline_aware=deadline,
                    initial_energy=40, initial_uc=60, resources=8,
                )
                execution = life.run_world(ticks=HORIZON)
                decisions = life.decision_evidence()
                audit = life.audit()
                arms[name] = {
                    "endpoint": world_endpoint(execution),
                    "actions": tuple(d["chosen"] for d in decisions),
                    "decision_ticks": tuple(d["physical_ticks_before"] for d in decisions),
                    "predecision_energy": tuple(d["before_energy"] for d in decisions),
                    "emergency_raises": sum(bool(d["last_resort_priority_applied"]) for d in decisions),
                    "deadline_suppressions": sum(bool(d["deadline_infeasible_collect_suppressed"]) for d in decisions),
                    "paid_uc": audit["actual_uc_spent"],
                    "audit_terminal": audit["terminal"],
                    "m11_authenticated": audit["m11_authenticated"],
                }
            rows["restorative" if water else "inert"] = arms
    return {
        "protocol": "i2-known-water-longitudinal-exploratory-v1",
        "physical_horizon": HORIZON,
        "known_water_impulse": 6,
        "policies": tuple(x[0] for x in POLICIES),
        "environments": rows,
        "source_specific_descriptive_only": True,
        "independent_replication": False,
        "general_survival_benefit": "NOT_ESTABLISHED",
    }
