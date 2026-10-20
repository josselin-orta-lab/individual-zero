"""Strict preregistration of new matched-temperament, unique-life Q factorial."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location(
    "q318twins",ROOT/"tools/run_i1_318_matched_temperament_q_factorial.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class Cohort(unittest.TestCase):
    def test_new_identity_controls(self):
        self.assertEqual(len(m.PRESETS)*len(m.SEEDS)*len(m.ARMS),32)
        self.assertEqual(set(m.SEEDS),{24103,24223,24359,24481})
        self.assertTrue(set(m.SEEDS).isdisjoint({
            20123,20233,20357,20477,21121,21227,21341,21467,
            22111,22229,22343,22453,23111,23239,23357,23473,
        }))
        self.assertEqual({m.factors(a)[1] for a in m.ARMS},
                         {"neutral","rank_only","evidence_only","learned"})
    def test_shared_source_distinct_mortal_identity(self):
        text=(ROOT/"tools/run_i1_318_matched_temperament_q_factorial.py").read_text()
        self.assertIn('life_id=f"i1:q-factorial-twin:{preset}:{seed}:{arm}:0"',text)
        self.assertIn('i1_research_temperament_source_id=f"i1:research-twin:{preset}:{seed}"',text)
        self.assertIn('"matched_twin_birth_temperament": True',text)
        self.assertIn('out.mkdir(parents=True, exist_ok=False)',text)
        self.assertIn('no_motor_forcing_or_new_vital_reflex',text)
if __name__=="__main__":
    unittest.main()
