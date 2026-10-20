"""Applied cognitive intention is not achieved without observed outcome."""
import os, subprocess, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ObservedOutcomeContracts(unittest.TestCase):
    def test_generated_owner_and_natural_m11(self):
        with TemporaryDirectory() as tmp:
            output=Path(tmp)/"fork"
            generate(output)
            script=r"""
from copy import deepcopy
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from run_i1_world_preset import load_preset,_birth_parameters
m=build_stage11_reference_runtime(autonomous_mortal=True).memory
sig="i1:affordance:collecter:target=x"
option="option:i1:local:t2:collecter:target=x"
body=dict(energy=60.,food=40.,water=50.,integrity=95.)
assert m.remember_considered_option(signature=sig,source_option_ref=option,considered_step=2,cost_uc=1)
assert m.remember_applied_option(signature=sig,source_option_ref=option,applied_step=2,cost_uc=1,body_before=body)
assert m.intentions[0].state=="awaiting_observation"
image=m.export_causal_state()
cold=type(m)(m._config,atomic_world_step_length_boundary=True)
cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert cold.observe_applied_option_followups(world_step=2,body_after=body)==()
assert cold.intentions[0].state=="awaiting_observation"
negative=deepcopy(image)
negative["intentions"][0]["trigger_value"]["body_before"]["water"]=float("nan")
original=cold.export_causal_state()
try: cold.restore_causal_state(negative);raise AssertionError("forged NaN")
except ValueError: pass
assert cold.export_causal_state()==original
after=dict(body,water=58.,integrity=87.)
observed=cold.observe_applied_option_followups(world_step=3,body_after=after)
assert len(observed)==1 and observed[0][1]=="observed_not_causal"
assert observed[0][2]["water"]==8. and observed[0][2]["integrity"]==-8.
assert cold.intentions[0].state=="pending"
assert "observed_step" in cold.intentions[0].trigger_value
assert cold.observe_applied_option_followups(world_step=3,body_after=after)==()
st=cold.export_causal_state()
third=type(m)(m._config,atomic_world_step_length_boundary=True)
third.restore_causal_state(st)
assert third.export_causal_state()==st
missed=type(m)(m._config,atomic_world_step_length_boundary=True)
missed.restore_causal_state(image)
assert missed.observe_applied_option_followups(world_step=4,body_after=after)[0][1]=="not_observed_in_next_step"
assert missed.intentions[0].state=="suspended"
assert "observed_step" not in missed.intentions[0].trigger_value
assert "observe_applied_option_followups" in inspect.getsource(I1Runtime._on_open_step_capture)
assert "body_before=" in inspect.getsource(I1Runtime._dispatch_decision)
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:364:natural"
def fresh():
 return I1Runtime(birth_life_id=life_id,wal_path=None,
  autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as d:
 db=str(Path(d)/"life.sqlite")
 with birth_i1_m11(db_path=db,life_id=life_id,**params) as actor:
  first=actor.run_step()
  assert first.status=="active"
  snapshot=actor._runtime.memory.export_causal_state()
 with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as actor:
  assert actor._runtime.memory.export_causal_state()==snapshot
  second=actor.run_step()
  assert second.status=="active" and second.generation==2
print("I1_364_OBSERVED_OUTCOME_M11_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(output),str(ROOT/"src"),str(ROOT/"tools"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_364_OBSERVED_OUTCOME_M11_OK",p.stdout)
if __name__=="__main__": unittest.main()
