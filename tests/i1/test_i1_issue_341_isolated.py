import unittest, subprocess, sys
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class LivedSite341(unittest.TestCase):
 def test_generated_i1_owner(self):
  with TemporaryDirectory() as d:
   out=Path(d)/"generated";generate(out)
   code=r"""
from i1.experimental.lived_water import I1LivedWaterOwner
from i1.experimental.witnessed_site_samples import site_samples
w=I1LivedWaterOwner(life_id="i1:test",enabled=True)
w.record_applied(sent_world_step=1,before_water=10,x=2,y=3,command_hash="command",option_ref="option",first_capture_hash="first")
p=w.observe_followup(observed_world_step=2,x=2,y=3,observed_water=15,current_water_source=True,followup_capture_hash="later",paid_uc=True)
assert p["admitted"]
s=site_samples(w,life_id="i1:test",site=(2,3),now_step=2)
assert len(s)==1 and s[0].observed_gain==5 and s[0].first_capture_hash=="first"
assert site_samples(w,life_id="i1:test",site=(1,1),now_step=2)==()
for life,now in (("i1:other",2),("i1:test",1)):
 try:site_samples(w,life_id=life,site=(2,3),now_step=now)
 except ValueError:pass
 else:raise AssertionError("unwitnessed evidence")
print("I1_341_OK")
"""
   r=subprocess.run([sys.executable,"-c",code],env={"PYTHONPATH":str(out)+":"+str(ROOT/"src")},cwd=ROOT,text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stdout+r.stderr)
