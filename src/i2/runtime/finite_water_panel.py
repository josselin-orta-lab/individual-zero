"""Exploratory finite-water depletion panel, no forced rescue or cherry-picking.

A bounded paid comparison of four policies, two hidden berry worlds
and the same initial finite safe water. Preserve all terminal failures.
"""
from __future__ import annotations
import tempfile
from pathlib import Path
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, world_endpoint

POLICIES=(("observational",False,False),
          ("reflex",True,False),("deadline",False,True),("combined",True,True))
WORLDS=("adverse","restoration")
WATER_CAPACITY=2
HORIZON=16

def finite_water_panel() -> dict:
    worlds={}
    with tempfile.TemporaryDirectory(prefix="i2-finite-water-panel-") as directory:
        for world in WORLDS:
            arms={}
            for label,reflex,deadline in POLICIES:
                life=IsolatedI2.create(
                    Path(directory)/(world+"-"+label+".sqlite"),
                    learning=True,impulses=SCENARIOS[world],
                    initial_energy=40,initial_uc=60,resources=8,
                    restorative_water_study=True,
                    finite_water_capacity=WATER_CAPACITY,
                    last_resort_exploration=reflex,deadline_aware=deadline)
                run=life.run_world(ticks=HORIZON)
                decisions=life.decision_evidence()
                audit=life.audit()
                arms[label]={
                    "endpoint":world_endpoint(run),
                    "actions":tuple(row["chosen"] for row in decisions),
                    "energy_before":tuple(row["before_energy"] for row in decisions),
                    "water_visible":tuple("affordance:drink:water" in row["visible"]
                                          for row in decisions),
                    "priority":tuple(bool(row["last_resort_priority_applied"])
                                     for row in decisions),
                    "deadline":tuple(bool(row["deadline_infeasible_collect_suppressed"])
                                     for row in decisions),
                    "water_remaining":audit["water_remaining"],
                    "paid_uc":audit["actual_uc_spent"],
                    "m11_authenticated":audit["m11_authenticated"],
                }
            worlds[world]=arms
    return {"protocol":"i2-finite-water-depletion-exploratory-v1",
            "finite_water_capacity":WATER_CAPACITY,
            "physical_horizon":HORIZON,"worlds":worlds,
            "general_survival_benefit":"NOT_ESTABLISHED",
            "natural_learning":"NOT_ESTABLISHED"}
