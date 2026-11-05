"""Predeclared finite-water capacity contrast, no tuned risk policy."""
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, world_endpoint, DRINK, EAT
POLICIES=(("deadline",False,True),("combined",True,True))
WORLDS=("adverse","restoration")
CAPACITIES=(1,2)
HORIZON=20

def capacity_contrast():
    result={}
    with tempfile.TemporaryDirectory(prefix="i2-capacity-contrast-") as root:
        for world in WORLDS:
            result[world]={}
            for stock in CAPACITIES:
                arms={}
                for name,reflex,deadline in POLICIES:
                    life=IsolatedI2.create(Path(root)/f"{world}-{stock}-{name}.sqlite",
                        learning=True,impulses=SCENARIOS[world]+(SCENARIOS[world][-1],)*2,
                        extended_postcontact_study=True,
                        initial_energy=40,initial_uc=60,resources=8,
                        restorative_water_study=True,finite_water_capacity=stock,
                        last_resort_exploration=reflex,deadline_aware=deadline)
                    execution=life.run_world(ticks=HORIZON)
                    decision=life.decision_evidence()
                    audit=life.audit()
                    arms[name]={"actions":tuple(x["chosen"] for x in decision),
                        "energy_before":tuple(x["before_energy"] for x in decision),
                        "water_visible":tuple(DRINK in x["visible"] for x in decision),
                        "priority":tuple(bool(x["last_resort_priority_applied"]) for x in decision),
                        "endpoint":world_endpoint(execution),
                        "paid_uc":audit["actual_uc_spent"],
                        "water_remaining":audit["water_remaining"],
                        "m11_authenticated":audit["m11_authenticated"]}
                result[world][str(stock)]=arms
    return {"protocol":"i2-finite-water-capacity-contrast-v1","worlds":result,
            "capacities":CAPACITIES,"horizon":HORIZON,
            "general_survival_benefit":"NOT_ESTABLISHED"}
