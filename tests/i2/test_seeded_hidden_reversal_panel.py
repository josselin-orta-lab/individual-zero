"""Reproducible panel of hidden future food schedules, no learned oracle.

Seed affects ONLY researcher-defined world schedules, not the organism's
capture. Never interpret repeated deterministic schedules as independent
natural-world replication.
"""
import random
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT

SEEDS=(11,23,37,51,79)
SCHEDULES=((6,6),(6,-8),(-8,-8))

def run_panel(seed):
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("unregistered panel seed")
    order=list(SCHEDULES)
    random.Random(seed).shuffle(order)
    result=[]
    with tempfile.TemporaryDirectory() as root:
        for i,tail in enumerate(order):
            life=IsolatedI2.create(
                Path(root)/f"{i}.sqlite",learning=True,
                impulses=SCENARIOS["restoration"]+tail,
                initial_energy=40,initial_uc=60,resources=8,
                last_resort_exploration=True,
                extended_postcontact_study=True)
            life.run_world(ticks=18)
            decisions=life.decision_evidence()
            audit=life.audit()
            result.append((tail,tuple((
                row["chosen"],row["before_energy"],row["before_inventory"],
                row["before_resources"],row["physical_ticks_before"],
                row["uc_before"],row["uc_spent"],
                tuple(sorted(row["candidate_scores"].items())),
                tuple((x["action"],x["observed_net"])
                      for x in row["subjective_outcomes_available"])
            ) for row in decisions), audit["terminal"],audit["energy"],
                           audit["actual_uc_spent"]))
    return tuple(sorted(result,key=lambda x:x[0]))

class SeededHiddenReversalPanel(unittest.TestCase):
    def test_predeclared_seeds_preserve_no_oracle_prechoice_invariance(self):
        reference=run_panel(SEEDS[0])
        for seed in SEEDS:
            with self.subTest(seed=seed):
                result=run_panel(seed)
                self.assertEqual(result,reference)
                self.assertEqual(len(result),3)
                self.assertEqual(len({entry[1] for entry in result}),1)
                self.assertEqual({e[2] for e in result},{True,False})
                self.assertEqual(len({e[4] for e in result}),1)
                self.assertTrue(all(e[1][8][0]==EAT for e in result))

    def test_refuses_unregistered_schedule_seeds(self):
        for bad in (True,0,1,80,"11"):
            with self.subTest(seed=bad),self.assertRaises(ValueError):
                run_panel(bad)

if __name__=="__main__":
    unittest.main()
