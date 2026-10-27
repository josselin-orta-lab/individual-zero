"""Reject corrupt Competition M11 candidate images atomically in generated I1."""
import os, sys, subprocess, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class CompetitionM11Image(unittest.TestCase):
 def test_generated_rejections(self):
  with TemporaryDirectory(prefix="i1-392-") as temp:
   out=Path(temp)/"build";generate(out)
   script=r"""
from copy import deepcopy
from i1.modules.competition import Competition,CompetitionConfig
cfg=CompetitionConfig(version="392",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=3,substitution_evidence={})
owner=Competition(cfg)
owner.ensure_wait(t_monde=1,st_version="st:1")
good=owner.export_causal_state()
def reject(edit):
 bad=deepcopy(good);edit(bad)
 before=owner.export_causal_state()
 try: owner.restore_causal_state(bad)
 except (ValueError,TypeError,KeyError,OverflowError): pass
 else: raise AssertionError("corrupt image accepted: "+repr(bad))
 assert owner.export_causal_state()==before
reject(lambda x:x["registry"][0].update(accumulator=float("nan")))
reject(lambda x:x["registry"][0].update(accumulator=float("inf")))
reject(lambda x:x["registry"][0].update(accumulator=-1.))
reject(lambda x:x["registry"][0].update(accumulator="1"))
reject(lambda x:x["registry"][0].update(last_threshold=float("nan")))
reject(lambda x:x["registry"][0].update(last_threshold=0.0))
reject(lambda x:x["registry"][0].update(last_threshold=True))
reject(lambda x:x["registry"][0].update(last_proposal_t=True))
reject(lambda x:x["registry"][0].update(last_proposal_t=-1))
reject(lambda x:x["registry"].append(deepcopy(x["registry"][0])))
reject(lambda x:x.update(engaged_option_id="nonexistent"))
reject(lambda x:x.update(cycle=True))
reject(lambda x:x.update(unrecognized="hidden"))
cold=Competition(cfg)
cold.restore_causal_state(good)
assert cold.export_causal_state()==good
print("I1_392_COMPETITION_M11_IMAGE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_392_COMPETITION_M11_IMAGE_OK",p.stdout)
