"""Evidence for an old meaning cannot attach to a same-ID new meaning."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class SemanticCandidateEvidence(unittest.TestCase):
 def test_generated_owner_semantic_refresh(self):
  with TemporaryDirectory(prefix="i1-410-") as home:
   out=Path(home)/"generated";generate(out)
   code=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig
from i0.contracts import OptionProposal,MotiveRef
cfg=CompetitionConfig(version="410",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,
 gain=1.,base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=5,substitution_evidence={"attendre":.2})
c=Competition(cfg);c.ensure_wait(t_monde=3,st_version="st:3")
wait=c.candidate_proposals[0]
opt=replace(wait.option,id="candidate:memory",plan_ref="plan:memory",learning_signature="memory:A")
plan=replace(wait.plan,id="plan:memory",option_ref=opt.id)
a=OptionProposal(opt,plan)
assert c.register(a,active_goal_id=None,t_monde=3)
c.evaluate(cycle=1,t_monde=3)
assert c.accumulator_for(opt.id)>0
b=OptionProposal(replace(opt,learning_signature="memory:B"),plan)
assert c.register(b,active_goal_id=None,t_monde=3)
assert c.accumulator_for(opt.id)==0
assert c.proposal_for(opt.id)==b
c.evaluate(cycle=2,t_monde=3)
assert c.accumulator_for(opt.id)>0
before=c.export_causal_state()
assert c.register(b,active_goal_id=None,t_monde=2) is False
assert c.export_causal_state()==before
c.close_deliberation(b)
engaged=c.export_causal_state()
rejected=OptionProposal(replace(b.option,motive_ref=MotiveRef(type="other",id="other")),plan)
assert c.register(rejected,active_goal_id=None,t_monde=4) is False
assert c.export_causal_state()==engaged
cold=Competition(cfg);cold.restore_causal_state(engaged)
assert cold.export_causal_state()==engaged
print("I1_410_SEMANTIC_EVIDENCE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_410_SEMANTIC_EVIDENCE_OK",p.stdout)
