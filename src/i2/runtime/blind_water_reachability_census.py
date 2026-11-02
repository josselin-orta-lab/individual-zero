"""Predeclared reachability census: unknown water, paid learning and survival.

This is a descriptive panel, not a positive survival demonstration.
"""
import tempfile
from pathlib import Path
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, EAT, world_endpoint

ENERGIES=(6,12,20,40)
CAPACITIES=(1,2)
POLICIES=(("observational",False,False),("reflex",True,False),
          ("deadline",False,True),("combined",True,True))
WORLDS=("adverse","restoration")
HORIZON=20

def census():
    rows=[]
    with tempfile.TemporaryDirectory(prefix="i2-blind-census-") as root:
        for world in WORLDS:
            schedule=SCENARIOS[world]+(SCENARIOS[world][-1],)*2
            for energy in ENERGIES:
                for stock in CAPACITIES:
                    for name,reflex,deadline in POLICIES:
                        life=IsolatedI2.create(
                            Path(root)/f"{world}-{energy}-{stock}-{name}.sqlite",
                            learning=True,impulses=schedule,
                            extended_postcontact_study=True,
                            initial_energy=energy,initial_uc=60,resources=8,
                            restorative_water_study=True,
                            water_effect_blind=True,finite_water_capacity=stock,
                            last_resort_exploration=reflex,deadline_aware=deadline)
                        execution=life.run_world(ticks=HORIZON)
                        decisions=life.decision_evidence()
                        audit=life.audit()
                        actions=tuple(d["chosen"] for d in decisions)
                        drank=[i for i,a in enumerate(actions) if a==DRINK]
                        water_used=len(drank)
                        food=[i for i,a in enumerate(actions) if a==EAT]
                        priority=[i for i,d in enumerate(decisions)
                                  if d["last_resort_priority_applied"]]
                        exhausted=water_used==stock
                        late_risky=any(i>drank[-1] for i in food) if exhausted and drank else False
                        rows.append(dict(world=world,energy=energy,stock=stock,
                          policy=name,actions=actions,
                          water_uses=water_used,exhausted=exhausted,
                          risk_after_exhaustion=late_risky,
                          first_water_seq=drank[0]+1 if drank else None,
                          emergency_recontacts=tuple(priority),
                          death_tick=world_endpoint(execution)["modeled_death_tick"],
                          censored=world_endpoint(execution)["right_censored"],
                          end_energy=audit["energy"],paid_uc=audit["actual_uc_spent"],
                          m11=audit["m11_authenticated"]))
    return {"protocol":"i2-blind-water-reachability-census-v1",
            "worlds":WORLDS,"energies":ENERGIES,"stocks":CAPACITIES,
            "policies":tuple(p[0] for p in POLICIES),
            "result":rows,"natural_learning":"NOT_ESTABLISHED",
            "general_survival":"NOT_ESTABLISHED",
            "design":"DESCRIPTIVE_PREDECLARED_NO_POSTHOC_TUNING"}
