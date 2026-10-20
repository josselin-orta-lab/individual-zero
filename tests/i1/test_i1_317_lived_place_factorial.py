"""Adversarial guards for first-person place relevance, no type oracle."""
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("lived_places317",ROOT/"tools/run_i1_317_lived_place_factorial.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LivedPlace317Tests(unittest.TestCase):
    def test_preregistered_factorial_and_unrecognized_arm(self):
        self.assertEqual({m.factors(a) for a in m.ARMS},
                         {(False,False),(True,False),(False,True),(True,True)})
        with self.assertRaises(ValueError):m.factors("force-water")
        self.assertEqual(len(m.ARMS)*len(m.PRESETS)*len(m.SEEDS),24)
    def test_lived_positive_only_ranks_personal_target(self):
        targets=[SimpleNamespace(observed_position=(8,9)),
                 SimpleNamespace(observed_position=(9,8)),
                 SimpleNamespace(observed_position=(8,8)),
                 SimpleNamespace(observed_position=(10,8))]
        self.assertEqual(m.rank_by_lived_sites(targets,{},3),tuple(targets[:3]))
        self.assertEqual(m.rank_by_lived_sites(targets,{(10,8):40.0},3),
                         (targets[3],targets[0],targets[1]))
        self.assertEqual(m.rank_by_lived_sites(targets,{(8,8):40.0},2),
                         (targets[2],targets[0]))
        for bad in ({(10,8):0},{(10,8):-1},{(10,8):float("nan")},{(10,8):float("inf")}):
            with self.assertRaises(ValueError):m.rank_by_lived_sites(targets,bad,3)
    def test_positive_site_requires_lived_owner_receipt(self):
        owner=SimpleNamespace(enabled=True,examples=(
            {"source_position":[8,8],"delta_water":39.6},
            {"source_position":[8,8],"delta_water":18.0},))
        actor=SimpleNamespace(_water_learner=owner)
        self.assertEqual(m.positive_sites_from_lived_owner(actor),{(8,8):39.6})
        owner.examples=({"source_position":[8,8],"delta_water":0},)
        with self.assertRaises(RuntimeError):m.positive_sites_from_lived_owner(actor)
        owner.enabled=False
        self.assertEqual(m.positive_sites_from_lived_owner(actor),{})
if __name__=="__main__":unittest.main()
