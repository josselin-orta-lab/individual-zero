"""Unit checks of paired 2x2 arithmetic, not physical efficacy proof."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("paired318",ROOT/"tools/audit_i1_318_matched_q_paired_effects.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class Contrasts(unittest.TestCase):
 def test_only_evidence_effect(self):
  x=m.paired_axes({"neutral":100,"rank_only":100,"evidence_only":5,"learned":5})
  self.assertEqual(x["rank_effect_times_2"],0)
  self.assertEqual(x["evidence_effect_times_2"],-190)
  self.assertEqual(x["interaction"],0)
 def test_interaction_detected(self):
  x=m.paired_axes({"neutral":8,"rank_only":12,"evidence_only":4,"learned":20})
  self.assertEqual(x["interaction"],12)
 def test_missing_arm_rejected(self):
  with self.assertRaises(ValueError):
   m.paired_axes({"neutral":1})
if __name__=="__main__": unittest.main()
