"""First action divergence for each factorial mechanism, without forcing actions."""
import json
import sys
import tempfile
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, world_endpoint

class FirstDivergenceFactorial(unittest.TestCase):
    def test_paid_first_divergences_remain_prechoice_matched(self):
        lives={}
        with tempfile.TemporaryDirectory(prefix="i2-first-divergence-") as root:
            for world,energy,stock,learning,deadline,reflex in product(
                ("adverse","restoration"),(6,40),(1,2),(False,True),
                (False,True),(False,True)):
                flags=(learning,deadline,reflex)
                label=f"{world}-{energy}-{stock}-{int(learning)}{int(deadline)}{int(reflex)}"
                life=IsolatedI2.create(
                    Path(root)/(label+".sqlite"),learning=learning,
                    impulses=SCENARIOS[world]+(SCENARIOS[world][-1],)*2,
                    extended_postcontact_study=True,initial_energy=energy,
                    initial_uc=60,resources=8,restorative_water_study=True,
                    water_effect_blind=True,finite_water_capacity=stock,
                    deadline_aware=deadline,last_resort_exploration=reflex)
                execution=life.run_world(ticks=20)
                audit=life.audit()
                self.assertEqual(audit["science"],"NOT_ESTABLISHED")
                self.assertFalse(audit["m11_authenticated"])
                lives[world,energy,stock,flags]=(
                    life.decision_evidence(),world_endpoint(execution))
            contrasts=[]
            for world,energy,stock,flags,axis in product(
                ("adverse","restoration"),(6,40),(1,2),
                product((False,True),repeat=3),range(3)):
                if flags[axis]:
                    continue
                switched=tuple(True if j==axis else v for j,v in enumerate(flags))
                left,le=lives[world,energy,stock,flags]
                right,re=lives[world,energy,stock,switched]
                first=None
                for i,(a,b) in enumerate(zip(left,right)):
                    if a["chosen"]==b["chosen"]:
                        continue
                    fields=("before_energy","before_inventory","before_resources",
                            "visible","physical_ticks_before","uc_before",
                            "subjective_outcomes_available")
                    for field in fields:
                        self.assertEqual(a[field],b[field],(world,energy,stock,axis,i,field))
                    self.assertEqual(tuple(x["chosen"] for x in left[:i]),
                                     tuple(x["chosen"] for x in right[:i]))
                    first={"step":i+1,"base_action":a["chosen"],
                           "enabled_action":b["chosen"],
                           "base_scores":a["candidate_scores"],
                           "enabled_scores":b["candidate_scores"],
                           "base_uc_spent":a["uc_spent"],
                           "enabled_uc_spent":b["uc_spent"],
                           "base_emergency":a["last_resort_priority_applied"],
                           "enabled_emergency":b["last_resort_priority_applied"],
                           "prior_food":any(x["chosen"]=="affordance:eat:berry_a" for x in left[:i]),
                           "prior_water":any(x["chosen"]=="affordance:drink:water" for x in left[:i])}
                    break
                contrasts.append(dict(world=world,energy=energy,stock=stock,
                    base=list(map(int,flags)),axis=("learning","deadline","reflex")[axis],
                    first=first,base_death=le["modeled_death_tick"],
                    enabled_death=re["modeled_death_tick"],
                    base_censored=le["right_censored"],
                    enabled_censored=re["right_censored"]))
            self.assertEqual(len(contrasts),96)
            print("I2_FACTORIAL_FIRST_DIVERGENCE_V1="+json.dumps({
                "contrasts":contrasts,"generalization":"NOT_ESTABLISHED",
                "causal_scope":"MATCHED_FIRST_PAID_CHOICE_ONLY"},
                sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
