"""Prospective, interruptible, nonmotor intention contract on generated I1."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ProspectiveIntentionContract(unittest.TestCase):
    def test_generated_first_person_prospect_and_cold_owner_image(self):
        with TemporaryDirectory() as d:
            built=Path(d)/"generated"
            generate(built)
            code=r"""
from copy import deepcopy
import inspect
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.i1_natural_runtime import I1Runtime
rt=build_stage11_reference_runtime(autonomous_mortal=True)
m=rt.memory
signature="i1:affordance:collecter:target=x"
ref="option:i1:local:t2:collecter:target=x"
assert m.remember_considered_option(signature=signature,
 source_option_ref=ref,considered_step=2,cost_uc=1)
assert not m.remember_considered_option(signature=signature,
 source_option_ref=ref,considered_step=2,cost_uc=1)
assert m.recalled_applied_option(signature=signature,world_step=3)
image=m.export_causal_state()
restored=type(m)(m._config,atomic_world_step_length_boundary=True)
restored.restore_causal_state(image)
assert restored.export_causal_state()==image
assert restored.reconcile_option_intentions(
 available_signatures=frozenset(),world_step=3)
assert restored.intentions[0].state=="suspended"
assert not restored.recalled_applied_option(signature=signature,world_step=3)
assert restored.reconcile_option_intentions(
 available_signatures=frozenset({signature}),world_step=4)
assert restored.intentions[0].state=="pending"
assert restored.remember_applied_option(signature=signature,
 source_option_ref="option:i1:local:t4:collecter:target=x",
 applied_step=4,cost_uc=1)
assert restored.intentions[0].state=="pending"  # applied without observed result
assert not restored.remember_applied_option(signature=signature,
 source_option_ref="option:i1:local:t4:collecter:target=x",
 applied_step=4,cost_uc=1)
state=restored.export_causal_state()
bad=deepcopy(state)
bad["intentions"][0]["wake_authorized"]=True
try: restored.restore_causal_state(bad);raise AssertionError("forged wake")
except ValueError: pass
assert restored.export_causal_state()==state
assert not restored.recalled_applied_option(signature=signature,world_step=1000)
assert restored.check_intentions(st=None,t_monde=4,cycle=1,
 pressure_fn=lambda **kwargs: .5)==()
method=inspect.getsource(I1Runtime._phase_hooks)
assert "remember_considered_option" in method
assert "original_control(ctx)" in method
assert "trace.evidence > 0.0" in method
assert "assessment.status == \"evaluated\"" in method
assert method.index("remember_considered_option") < method.index("original_control(ctx)")
assert "remember_prospect_before_motor" in method
assert "reconcile_option_intentions" in inspect.getsource(
 I1Runtime._propose_independent_local)
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from run_i1_world_preset import load_preset,_birth_parameters
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:361:technical-prospect"
def factory():
 return I1Runtime(birth_life_id=life_id,wal_path=None,
  autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as location:
 db=str(Path(location)/"life.sqlite")
 with birth_i1_m11(db_path=db,life_id=life_id,**params) as actor:
  first=actor.run_step()
  assert first.status=="active"
  image=actor._runtime.memory.export_causal_state()
 with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=factory) as cold:
  assert cold._runtime.memory.export_causal_state()==image
  second=cold.run_step()
  assert second.status=="active" and second.generation==first.generation+1
print("I1_361_PROSPECTIVE_M11_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"),str(ROOT/"tools"))),PYTHONDONTWRITEBYTECODE="1")
            result=subprocess.run([sys.executable,"-B","-c",code],
                cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_361_PROSPECTIVE_M11_OK",result.stdout)
if __name__=="__main__": unittest.main()
