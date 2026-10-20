"""Natural generic option intention: applied-only Memory owner and M11 fidelity."""
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class NaturalOptionIntention(unittest.TestCase):
    def test_memory_owner_contract_and_canonical_cold_recovery(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/"build"
            generate(out)
            program=r"""
from copy import deepcopy
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from run_i1_world_preset import load_preset, _birth_parameters

runtime=build_stage11_reference_runtime(autonomous_mortal=True)
owner=runtime.memory
assert owner.remember_applied_option(signature="i1:affordance:collecter:target=x",
    source_option_ref="option:i1:local:t2:collecter:target=x",
    applied_step=2,cost_uc=1)
assert owner.recalled_applied_option(signature="i1:affordance:collecter:target=x",world_step=3)
frozen=owner.export_causal_state()
restored=type(owner)(owner._config,atomic_world_step_length_boundary=True)
restored.restore_causal_state(frozen)
assert restored.export_causal_state()==frozen
assert restored.recalled_applied_option(signature="i1:affordance:collecter:target=x",world_step=3)
assert not restored.recalled_applied_option(signature="i1:affordance:collecter:target=x",world_step=100)
assert not restored.remember_applied_option(signature="i1:affordance:collecter:target=x",
    source_option_ref="option:i1:local:t2:collecter:target=x",
    applied_step=2,cost_uc=1)
assert len(restored.intentions)==1
corrupt=deepcopy(frozen)
corrupt["intentions"][0]["wake_authorized"]=True
previous=restored.export_causal_state()
try:
    restored.restore_causal_state(corrupt)
    raise AssertionError("forged option wake accepted")
except ValueError:
    pass
assert restored.export_causal_state()==previous
assert restored.check_intentions(st=None,t_monde=3,cycle=1,
    pressure_fn=lambda **kwargs: .5)==()
assert "remember_applied_option" in inspect.getsource(I1Runtime._dispatch_decision)
assert "recalled_applied_option" in inspect.getsource(I1Runtime._propose_independent_local)
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life="i1:360:contract"
def fresh():
    return I1Runtime(birth_life_id=life,wal_path=None,
        autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as temp:
    db=str(Path(temp)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=life,**params) as actor:
        first=actor.run_step()
        assert first.status=="active"
        before=actor._runtime.memory.export_causal_state()
    with recover_i1_m11(db_path=db,life_id=life,runtime_factory=fresh) as recovered:
        assert recovered._runtime.memory.export_causal_state()==before
        second=recovered.run_step()
        assert second.status=="active"
        assert second.generation==first.generation+1
print("I1_360_CONTRACT_M11_OK")
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"),str(ROOT/"tools"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_360_CONTRACT_M11_OK",p.stdout)

if __name__=="__main__":
    unittest.main()
