"""#318 holdout cohort preregistration, unique mortality and no oracle."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("ecology318",ROOT/"tools/run_i1_318_long_horizon_evidence_cohort.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class Holdout(unittest.TestCase):
 def test_design(self):
  self.assertEqual(m.PRESETS,("foraging","dry-valley","hazard-edge","empty-land"))
  self.assertEqual(m.SEEDS,(25117,25219,25339))
  self.assertEqual(m.HORIZON,900)
  self.assertEqual(m.ARMS,("local_q_neutral","local_q_evidence_only"))
  self.assertEqual([m.factors(x) for x in m.ARMS],[(True,"neutral"),(True,"evidence_only")])
  self.assertTrue(set(m.SEEDS).isdisjoint({24103,24223,24359,24481,23111,23239,23357,23473}))
 def test_independent_births(self):
  s=(ROOT/"tools/run_i1_318_long_horizon_evidence_cohort.py").read_text()
  self.assertIn('life_id=f"i1:ecology-evidence:{preset}:{seed}:{arm}:0"',s)
  self.assertIn('i1_research_temperament_source_id=f"i1:research-twin:{preset}:{seed}"',s)
  self.assertIn('i1_local_q_exposure=q_mode',s)
  self.assertIn('out.mkdir(parents=True, exist_ok=False)',s)
  self.assertIn('no_motor_forcing_or_new_vital_reflex',s)
if __name__=="__main__": unittest.main()
