"""A paid spatial prospective read can change consideration, not motor admission."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class SpatialProspectConsumption(unittest.TestCase):
 def test_generated_natural_owner_read(self):
  with TemporaryDirectory(prefix="i1-395-") as d:
   built=Path(d)/"generated";generate(built)
   source=r"""
from types import SimpleNamespace
from i1lab.i1_natural_runtime import I1Runtime
calls=[]
class Memory:
 spatial_option_prospect_count=1
 def recalled_applied_option(self,*,signature,world_step):
  calls.append(("read",signature,world_step))
  return signature=="memory_place_return:remembered"
class Actor:
 memory=Memory()
 def __init__(self,allowed):self.allowed=allowed;self.writes=[]
 def _charge(self,*,module,operation):
  calls.append(("charge",module,operation))
  return self.allowed
 def _write(self,**event):self.writes.append(event)
first=SimpleNamespace(entity_id="new")
old=SimpleNamespace(entity_id="remembered")
capture=SimpleNamespace(t_monde=3)
reader=I1Runtime._order_considered_spatial_targets
a=Actor(True)
assert reader(a,(first,old),capture=capture,cycle=1)==(old,first)
assert calls[0][0]=="charge" and all(x[0]=="read" for x in calls[1:])
assert a.writes[0]["data"]["consideration_order_changed"] is True
assert a.writes[0]["data"]["motor_admission_inherited"] is False
calls.clear()
a=Actor(False)
assert reader(a,(first,old),capture=capture,cycle=1)==(first,old)
assert [x[0] for x in calls]==["charge"] and not a.writes
calls.clear()
a=Actor(True);a.memory.spatial_option_prospect_count=0
assert reader(a,(first,old),capture=capture,cycle=1)==(first,old)
assert not calls and not a.writes
print("I1_395_SPATIAL_PROSPECT_READ_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",source],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_395_SPATIAL_PROSPECT_READ_OK",p.stdout)
