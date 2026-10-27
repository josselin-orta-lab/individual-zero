"""Issue 365: two contradicting first-person witnesses persist in one owner."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class ContradictoryOptionEvidence(unittest.TestCase):
 def test_generated_owner_m11(self):
  with TemporaryDirectory() as d:
   build=Path(d)/"build";generate(build)
   code=r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.i1_natural_runtime import I1Runtime
import inspect
m=build_stage11_reference_runtime(autonomous_mortal=True).memory
sig="i1:affordance:collecter:target=x"
body=dict(energy=60.,food=60.,water=60.,integrity=60.)
def act(step):
 return m.remember_applied_option(signature=sig,source_option_ref=f"option:i1:local:t{step}:collecter:target=x",applied_step=step,cost_uc=1,body_before=body)
assert act(2)
plus=dict(body,water=70.)
assert len(m.observe_applied_option_followups(world_step=3,body_after=plus))==1
assert act(4)
minus=dict(body,water=50.)
assert len(m.observe_applied_option_followups(world_step=5,body_after=minus))==1
w=m.observed_option_witnesses(signature=sig,world_step=6)
assert len(w)==2 and w[0]["body_delta"]["water"]==10. and w[1]["body_delta"]["water"]==-10.
assert w[0]["observed_step"]==3 and w[1]["observed_step"]==5
assert not m.observe_applied_option_followups(world_step=5,body_after=minus)
image=m.export_causal_state()
other=type(m)(m._config,atomic_world_step_length_boundary=True)
other.restore_causal_state(image)
assert other.export_causal_state()==image
bad=deepcopy(image);bad["intentions"][0]["trigger_value"]["observations"][0]["observed_step"]=7
previous=other.export_causal_state()
try:other.restore_causal_state(bad);raise AssertionError("forged witness")
except ValueError:pass
assert other.export_causal_state()==previous
w[0]["body_delta"]["water"]=999.
assert other.observed_option_witnesses(signature=sig,world_step=6)[0]["body_delta"]["water"]==10.
assert not other.observed_option_witnesses(signature=sig,world_step=1000)
assert "observed_option_witnesses" in inspect.getsource(I1Runtime._propose_independent_local)
assert "learned.evidence" in inspect.getsource(I1Runtime._propose_independent_local)
print("I1_365_CONTRADICTION_M11_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(build),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   out=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,capture_output=True,text=True)
   self.assertEqual(out.returncode,0,out.stdout+out.stderr)
   self.assertIn("I1_365_CONTRADICTION_M11_OK",out.stdout)
if __name__=="__main__":unittest.main()
