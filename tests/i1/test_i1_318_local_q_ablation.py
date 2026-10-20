"""Issue #318: inspect Q exposure without modifying learning or action control."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class LocalQ318(unittest.TestCase):
 def test_only_local_exposure_changes(self):
  with TemporaryDirectory() as d:
   generate(Path(d)/"generated")
   s=(Path(d)/"generated"/"i1lab"/"i1_active_runtime.py").read_text()
   self.assertIn('q_exposure = getattr(self, "_i1_local_q_exposure", "learned")',s)
   self.assertIn('selected_evidence = learned if q_exposure == "learned" else None',s)
   self.assertIn('"q_exposure": q_exposure',s)
   self.assertNotIn('self.q_active._weights.clear()',s)
  m=(ROOT/"src/i1/runtime/m11_transactional_mortal.py").read_text()
  self.assertIn('getattr(runtime, "_i1_local_q_exposure", "learned")',m)
 def test_config_requires_optin(self):
  n=(ROOT/"src/i1/runtime/i1_natural_runtime.py").read_text()
  self.assertIn('and not self._i1_cross_goal_local_opportunities',n)

if __name__=="__main__":unittest.main()
