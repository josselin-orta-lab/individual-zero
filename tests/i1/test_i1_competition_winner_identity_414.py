"""Only an exact registered Competition winner can become engaged."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class CompetitionWinnerIdentity(unittest.TestCase):
 def test_generated_owner_winner_integrity(self):
  with TemporaryDirectory(prefix="i1-414-") as home:
   out=Path(home)/"generated";generate(out)
   code=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig
from i0.contracts import OptionProposal
cfg=CompetitionConfig(version="414",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,
 base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=5,substitution_evidence={})
c=Competition(cfg)
c.ensure_wait(t_monde=3,st_version="st:3")
registered=c.candidate_proposals[0]
before=c.export_causal_state()
foreign=OptionProposal(replace(registered.option,id="foreign",plan_ref=None),None)
for bad in (foreign,OptionProposal(replace(registered.option,learning_signature="changed"),registered.plan)):
 try:c.close_deliberation(bad)
 except ValueError:pass
 else:raise AssertionError("foreign/stale winner accepted")
 assert c.export_causal_state()==before
c.close_deliberation(registered)
image=c.export_causal_state()
assert image["engaged_option_id"]==registered.option.id
cold=Competition(cfg);cold.restore_causal_state(image)
assert cold.export_causal_state()==image
# A physically applied fallback is not an adjudicated winner.
cold.close_deliberation(foreign,adjudicated=False)
assert cold.export_causal_state()==image
print("I1_414_WINNER_IDENTITY_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_414_WINNER_IDENTITY_OK",p.stdout)
