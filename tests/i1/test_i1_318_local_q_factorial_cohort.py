"""Preflight: only unique, never-before-born factorial source identities."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("factorial318",ROOT/"tools/run_i1_318_local_q_factorial_cohort.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class FactorialBirths(unittest.TestCase):
 def test_four_orthogonal_research_arms(self):
  self.assertEqual(m.ARMS,("local_q_neutral","local_q_rank_only","local_q_evidence_only","local_q_learned"))
  self.assertEqual([m.factors(a) for a in m.ARMS],[(True,"neutral"),(True,"rank_only"),(True,"evidence_only"),(True,"learned")])
 def test_new_birth_identity_and_no_forced_commands(self):
  self.assertEqual(len(m.PRESETS)*len(m.SEEDS)*len(m.ARMS),32)
  self.assertTrue(set(m.SEEDS).isdisjoint({21121,21227,21341,21467,22111,22229,22343,22453,20123,20233,20357,20477}))
  text=(ROOT/"tools/run_i1_318_local_q_factorial_cohort.py").read_text()
  self.assertIn('life_id=f"i1:q-factorial:{preset}:{seed}:{arm}:0"',text)
  self.assertIn('i1_local_q_exposure=q_mode',text)
  self.assertIn('i1_cross_goal_local_opportunities=True',text)
  self.assertIn('no_motor_forcing_or_new_vital_reflex',text)
  self.assertIn('out.mkdir(parents=True, exist_ok=False)',text)
if __name__=="__main__":
 unittest.main()
