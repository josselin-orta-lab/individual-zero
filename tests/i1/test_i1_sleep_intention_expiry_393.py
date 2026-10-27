"""Sleep clock expires Competition intentions without synthetic perception."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class SleepIntentionExpiry(unittest.TestCase):
 def test_generated_owner_and_sleep_wiring(self):
  with TemporaryDirectory(prefix="i1-393-") as tmp:
   generated=Path(tmp)/"built";generate(generated)
   script=r"""
import inspect
from i1.modules.competition import Competition,CompetitionConfig,AppliedMemoryIntention
from i1lab.stage10_runtime import Stage10Runtime
cfg=CompetitionConfig(version="sleep-393",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=6,substitution_evidence={})
c=Competition(cfg)
c._applied_memory_intent=AppliedMemoryIntention(
 semantic_ref="memory_place_return:old-site",
 source_option_ref="option:place-memory:place:old-site:at:4:0:from:1:0:via:2:0",
 goal_ref="goal:own",expected_position=(2,0),observed_site=(4,0),
 applied_step=1,expires_at_step=4,evidence=.5,confirmed_step=2)
before=c.export_causal_state()
assert not c.expire_memory_intention(world_step=3)
assert c.export_causal_state()==before
for bad in (False,0,1.0,"4"):
 try:c.expire_memory_intention(world_step=bad)
 except ValueError:pass
 else:raise AssertionError("invalid clock accepted")
image=c.export_causal_state()
restored=Competition(cfg);restored.restore_causal_state(image)
assert restored.export_causal_state()==image
assert restored.expire_memory_intention(world_step=4)
assert restored.applied_memory_intention is None
assert not restored.expire_memory_intention(world_step=5)
source=inspect.getsource(Stage10Runtime._sleep_step)
assert source.index("expire_memory_intention(")<source.index("open_world_step(t)")
assert '"spatial_confirmation": False' in source
assert '"motor_admission_inherited": False' in source
assert "observe_memory_intention(" not in source
print("I1_393_SLEEP_EXPIRY_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(generated),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_393_SLEEP_EXPIRY_OK",p.stdout)
