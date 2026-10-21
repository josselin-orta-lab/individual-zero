"""Confirmed spatial intentions lose only contradicted premises, not memory."""
import os, subprocess, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class SpatialIntentPremiseTest(unittest.TestCase):
 def test_generated_owner_and_natural_paid_wiring(self):
  with TemporaryDirectory(prefix="i1-374-") as tmp:
   output=Path(tmp)/"generated";generate(output)
   script=r"""
from i1.modules.competition import Competition, CompetitionConfig, AppliedMemoryIntention
from i1lab.stage11_runtime import Stage11Runtime
import inspect
cfg=CompetitionConfig(version="premise-374",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=6,substitution_evidence={})
def owner():
 c=Competition(cfg)
 c._applied_memory_intent=AppliedMemoryIntention(
  semantic_ref="memory_place_return:sighting:berry_a:3:0",
  source_option_ref="option:place-memory:place:sighting:berry_a:3:0:at:3:0:from:0:0:via:1:0",
  goal_ref="goal:food",expected_position=(1,0),observed_site=(3,0),
  applied_step=2,expires_at_step=15,evidence=.5,confirmed_step=3)
 c._applied_memory_intent.validate()
 return c
c=owner();image=c.export_causal_state()
assert not c.invalidate_contradicted_place_intention(semantic_ref="memory_place_return:sighting:berry_a:4:0",observed_site=(3,0),contradiction_step=4)
assert not c.invalidate_contradicted_place_intention(semantic_ref="memory_place_return:sighting:berry_a:3:0",observed_site=(4,0),contradiction_step=4)
assert not c.invalidate_contradicted_place_intention(semantic_ref="memory_place_return:sighting:berry_a:3:0",observed_site=(3,0),contradiction_step=2)
assert c.export_causal_state()==image
cold=Competition(cfg);cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert cold.invalidate_contradicted_place_intention(semantic_ref="memory_place_return:sighting:berry_a:3:0",observed_site=(3,0),contradiction_step=4)
assert cold.applied_memory_intention is None
assert cold.export_causal_state()["applied_memory_intention"] is None
for bad in (False,1.0,-1):
 try:c.invalidate_contradicted_place_intention(semantic_ref="memory_place_return:sighting:berry_a:3:0",observed_site=(3,0),contradiction_step=bad)
 except ValueError:pass
 else:raise AssertionError("invalid step accepted")
code=inspect.getsource(Stage11Runtime._phase_hooks)
assert code.index('operation="exploration_observe"')<code.index("invalidate_contradicted_place_intention(")
assert 'memory.contradiction_step == capture.t_monde' in code
assert 'memory.last_seen_step < capture.t_monde' in code
assert 'motor_admission_inherited": False' in code
assert "geo.observe_entities(" in code
assert 'operation="competition_register"' in code
print("I1_374_SPATIAL_INTENT_PREMISE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(output),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_374_SPATIAL_INTENT_PREMISE_OK",p.stdout)
if __name__=="__main__":unittest.main()
