"""Issue 318: never grant a benefit or motor from cross-goal local curiosity."""
import unittest
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
BUILD=TemporaryDirectory(prefix="i1-318-unknown-local-")
generate(Path(BUILD.name)/"generated")
sys.path.insert(0,str(Path(BUILD.name)/"generated"))
from i1lab.i1_active_runtime import _local_interaction_choices

class LocalCuriosity318(unittest.TestCase):
 def test_perceived_executable_commands_only(self):
  def command(name):
   return SimpleNamespace(primitive=name,parameters={})
  offered=[command(p) for p in ("attendre","boire","manger","collecter","se_deplacer","dormir")]
  self.assertEqual(tuple(c.primitive for c in _local_interaction_choices(offered,enabled=True)),
                   ("boire","manger","collecter"))
  self.assertEqual(_local_interaction_choices(offered,enabled=False),())
  # A visible resource is NOT authority to propose an unavailable command.
  self.assertEqual(_local_interaction_choices([command("attendre")],enabled=True),())
 def test_bad_flags_fail(self):
  with self.assertRaises(ValueError):
   _local_interaction_choices((),enabled=1)
if __name__=="__main__":unittest.main()
