import unittest, subprocess, sys
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class LocalDedup340(unittest.TestCase):
 def test_generated_i1(self):
  with TemporaryDirectory() as d:
   out=Path(d)/"generated";generate(out)
   code=r"""
from i1.experimental.local_command_dedup import distinct_local_commands
from i1.interfaces import PrimitiveCommand
from types import SimpleNamespace
a=PrimitiveCommand("collecter",{"nested":{"x":1,"y":[2]}})
b=PrimitiveCommand("boire",{})
c=PrimitiveCommand("collecter",{"nested":{"y":[2],"x":1}})
def p(command,expiry):
 return SimpleNamespace(option=SimpleNamespace(expires_at_step=expiry),plan=SimpleNamespace(steps=(SimpleNamespace(command=command),)))
assert distinct_local_commands((a,b,c),(p(a,5),),now_step=4)==(b,)
assert distinct_local_commands((a,b,c),(p(a,4),),now_step=4)==(a,b)
for bad in (float("nan"),object()):
 try:distinct_local_commands((PrimitiveCommand("x",{"a":bad}),),(),now_step=4)
 except ValueError:pass
 else:raise AssertionError("nonserializable value accepted")
print("I1_340_OK")
"""
   r=subprocess.run([sys.executable,"-c",code],env={"PYTHONPATH":str(out)+":"+str(ROOT/"src")},cwd=ROOT,text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
