"""Distinct twenty-tick paid finite-water panel, no retroactive tuning."""
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, world_endpoint

POLICIES=(("observational",False,False),("reflex",True,False),
          ("deadline",False,True),("combined",True,True))
WORLDS=("adverse","restoration")
HORIZON=20
STOCK=2

def run_extended_panel():
    outcomes={}
    with tempfile.TemporaryDirectory(prefix="i2-finite-water-20-") as root:
        for world in WORLDS:
            arms={}
            for policy,reflex,deadline in POLICIES:
                life=IsolatedI2.create(
                    Path(root)/(world+"-"+policy+".sqlite"),learning=True,
                    impulses=SCENARIOS[world]+(SCENARIOS[world][-1],)*2,
                    extended_postcontact_study=True,
                    initial_energy=40,initial_uc=60,resources=8,
                    restorative_water_study=True,finite_water_capacity=STOCK,
                    last_resort_exploration=reflex,deadline_aware=deadline)
                execution=life.run_world(ticks=HORIZON)
                decisions=life.decision_evidence()
                audit=life.audit()
                arms[policy]={
                    "endpoint":world_endpoint(execution),
                    "actions":tuple(d["chosen"] for d in decisions),
                    "before_energy":tuple(d["before_energy"] for d in decisions),
                    "water_visible":tuple("affordance:drink:water" in d["visible"] for d in decisions),
                    "priority":tuple(bool(d["last_resort_priority_applied"]) for d in decisions),
                    "deadline":tuple(bool(d["deadline_infeasible_collect_suppressed"]) for d in decisions),
                    "water_remaining":audit["water_remaining"],
                    "paid_uc":audit["actual_uc_spent"],
                    "m11_authenticated":audit["m11_authenticated"],
                }
            outcomes[world]=arms
    return {"protocol":"i2-finite-water-20-tick-exploratory-v1",
            "stock":STOCK,"physical_horizon":HORIZON,"worlds":outcomes,
            "general_survival_benefit":"NOT_ESTABLISHED",
            "natural_learning":"NOT_ESTABLISHED"}
