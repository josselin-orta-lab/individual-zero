"""Source-predeclared 32-life blind-water learning-toggle ablation.

No forced actions, hidden phase sensing, altered physics or threshold changes.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, world_endpoint

class BlindWaterLearningAblation(unittest.TestCase):
    def test_paired_learning_switch_at_same_prechoice_state(self):
        outcomes=[]
        contrasts=[]
        with tempfile.TemporaryDirectory() as root:
            for world in ("adverse", "restoration"):
                impulses=SCENARIOS[world]+(SCENARIOS[world][-1],)*2
                for initial_energy in (6,40):
                    for stock in (1,2):
                        for name,reflex in (("deadline",False),("combined",True)):
                            pair={}
                            for learning in (False,True):
                                life=IsolatedI2.create(
                                    Path(root)/f"{world}-{initial_energy}-{stock}-{name}-{int(learning)}.sqlite",
                                    learning=learning,impulses=impulses,
                                    extended_postcontact_study=True,
                                    initial_energy=initial_energy,initial_uc=60,resources=8,
                                    restorative_water_study=True,water_effect_blind=True,
                                    finite_water_capacity=stock,
                                    last_resort_exploration=reflex,deadline_aware=True)
                                execution=life.run_world(ticks=20)
                                decisions=life.decision_evidence()
                                audit=life.audit()
                                used=sum(d["chosen"]==DRINK for d in decisions)
                                self.assertLessEqual(used,stock)
                                self.assertEqual(audit["water_remaining"],stock-used)
                                self.assertEqual(audit["actual_uc_spent"],
                                                 world_endpoint(execution)["actual_uc_spent"])
                                self.assertFalse(audit["m11_authenticated"])
                                self.assertEqual(audit["science"],"NOT_ESTABLISHED")
                                if used==stock:
                                    last=max(i for i,d in enumerate(decisions) if d["chosen"]==DRINK)
                                    self.assertTrue(all(DRINK not in d["visible"]
                                            for d in decisions[last+1:]))
                                pair[learning]=decisions
                                outcomes.append(dict(world=world,initial_energy=initial_energy,
                                    stock=stock,policy=name,learning=learning,
                                    actions=[d["chosen"] for d in decisions],
                                    paid_uc=audit["actual_uc_spent"],
                                    water_used=used,remaining=audit["water_remaining"],
                                    death_tick=world_endpoint(execution)["modeled_death_tick"],
                                    censored=world_endpoint(execution)["right_censored"]))
                            fixed,learned=pair[False],pair[True]
                            first=None
                            for i,(a,c) in enumerate(zip(fixed,learned)):
                                if a["chosen"]!=c["chosen"]:
                                    same_state=all(a[k]==c[k] for k in (
                                        "before_energy","before_inventory","before_resources",
                                        "visible","uc_before","physical_ticks_before"))
                                    self.assertTrue(same_state)
                                    self.assertEqual([d["chosen"] for d in fixed[:i]],
                                                     [d["chosen"] for d in learned[:i]])
                                    prior=learned[:i]
                                    first=dict(index=i+1,fixed=a["chosen"],learned=c["chosen"],
                                       prior_water_gain=any(d["chosen"]==DRINK and
                                           d["energy_after"]>d["before_energy"] for d in prior),
                                       prior_food=any(d["chosen"]=="affordance:eat:berry_a"
                                           for d in prior),
                                       fixed_scores=a["candidate_scores"],
                                       learned_scores=c["candidate_scores"])
                                    break
                            contrasts.append(dict(world=world,initial_energy=initial_energy,
                                stock=stock,policy=name,first_divergence=first))
        self.assertEqual(len(outcomes),32)
        self.assertEqual(len(contrasts),16)
        print("I2_BLIND_WATER_LEARNING_ABLATION_V1="+json.dumps(
            dict(outcomes=outcomes,contrasts=contrasts,
                 generalized_survival="NOT_ESTABLISHED",
                 water_learning_necessity="NOT_ESTABLISHED",
                 design="DETERMINISTIC_MATCHED_ABLATION"),sort_keys=True),flush=True)

if __name__=="__main__":
    unittest.main()
