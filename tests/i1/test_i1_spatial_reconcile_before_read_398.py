"""A suspended remembered route can be reconsidered in its first available cycle."""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SpatialReconcileBeforeRecall(unittest.TestCase):
    def test_generated_natural_memory_owner_and_uc(self):
        with TemporaryDirectory(prefix="i1-398-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            script = r"""
from types import SimpleNamespace
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1.modules.memory import EpisodicMemory

def owner():
 m=build_stage11_reference_runtime(autonomous_mortal=True).memory
 sig="memory_place_return:old"
 assert m.remember_considered_option(
    signature=sig,
    source_option_ref="option:place-memory:place:old:at:3:0:from:1:0:via:2:0",
    considered_step=2,cost_uc=1)
 assert m.reconcile_option_intentions(
    available_signatures=frozenset(),world_step=3,
    namespace="memory_place_return:")
 assert next(i for i in m.intentions if i.target==sig).state=="suspended"
 return m
class Actor:
 def __init__(self, decisions):
  self.memory=owner()
  self.decisions=iter(decisions)
  self.charges=[]
  self.writes=[]
 def _charge(self,*,module,operation):
  self.charges.append((module,operation))
  return next(self.decisions)
 def _write(self,**event):self.writes.append(event)

targets=(SimpleNamespace(entity_id="new"),SimpleNamespace(entity_id="old"))
capture=SimpleNamespace(t_monde=4)
reader=I1Runtime._order_considered_spatial_targets
a=Actor([True,True])
result=reader(a,targets,capture=capture,cycle=1)
assert result==(targets[1],targets[0])
assert next(i for i in a.memory.intentions if i.target=="memory_place_return:old").state=="pending"
assert len(a.charges)==2
assert a._i1_spatial_reconciled_cycle==(4,1)
assert a.writes[0]["data"]["motor_admission_inherited"] is False

# Declining the *first* UC prevents both reconciliation and reading.
b=Actor([False])
assert reader(b,targets,capture=capture,cycle=1)==targets
assert len(b.charges)==1 and not b.writes
assert next(i for i in b.memory.intentions if i.target=="memory_place_return:old").state=="suspended"

# Paid reconciliation without a second paid read cannot influence order.
c=Actor([True,False])
assert reader(c,targets,capture=capture,cycle=1)==targets
assert len(c.charges)==2 and not c.writes
assert next(i for i in c.memory.intentions if i.target=="memory_place_return:old").state=="pending"

# Expired intentions never recover from a fresh advertised route.
d=Actor([True,True])
assert d.memory.expire_option_intentions(world_step=100)
assert reader(d,targets,capture=SimpleNamespace(t_monde=100),cycle=1)==targets
assert not d.writes
state=d.memory.export_causal_state()
cold=EpisodicMemory(d.memory._config,atomic_world_step_length_boundary=True)
cold.restore_causal_state(state)
assert cold.export_causal_state()==state
print("I1_398_SAME_CYCLE_RECONCILIATION_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable,"-B","-c",script],
                                    cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_398_SAME_CYCLE_RECONCILIATION_OK",result.stdout)
