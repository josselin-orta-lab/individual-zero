"""#318 bodily alert wake one-step sleep eligibility, no motor directives."""
import unittest
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
_GENERATED=TemporaryDirectory(prefix="i1-318-sleep-")
generate(Path(_GENERATED.name)/"generated")
sys.path.insert(0,str(Path(_GENERATED.name)/"generated"))
from i1lab.i1_natural_runtime import _critical_alert_reentry_channels

def observation(water=7,food=60,integrity=80,energy=100):
 return SimpleNamespace(t_monde=12,body=dict(water=water,food=food,integrity=integrity,energy=energy))
def pending(reason="alert",woke=True):
 return SimpleNamespace(world_step=12,reason=reason,woke=woke)
T=dict(water=15,food=10,integrity=25,energy=10)
class AlertWake318(unittest.TestCase):
 def test_only_critical_bodily_alert(self):
  f=lambda p,c: _critical_alert_reentry_channels(pending=p,sleep_mode="awake",world_step=12,capture=c,thresholds=T)
  self.assertEqual(f(pending(),observation()),("water",))
  self.assertEqual(f(pending(),observation(water=30)),())
  self.assertEqual(f(pending(),observation(energy=5)),())
  self.assertEqual(f(pending("natural_end"),observation()),())
  self.assertEqual(f(pending(woke=False),observation()),())
  self.assertEqual(f(pending(),observation(water=8,food=4,integrity=20)),("water","food","integrity"))
 def test_stale_captures_fail_closed(self):
  with self.assertRaises(RuntimeError):
   _critical_alert_reentry_channels(pending=pending(),sleep_mode="awake",world_step=12,capture=observation(),thresholds={})
  self.assertEqual(_critical_alert_reentry_channels(pending=pending(),sleep_mode="sleeping",world_step=12,capture=observation(),thresholds=T),())
if __name__=="__main__":unittest.main()
