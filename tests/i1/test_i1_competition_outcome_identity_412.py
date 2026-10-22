"""Version and outcome meaning must not inherit previously accumulated Competition proof."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class OutcomeContractIdentity(unittest.TestCase):
 def test_generated_I1_owner_outcome_identity(self):
  with TemporaryDirectory(prefix="i1-412-") as home:
   out=Path(home)/"generated";generate(out)
   code=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig
from i0.contracts import OptionProposal
cfg=CompetitionConfig(version="412",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,
 base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=5,substitution_evidence={"attendre":.2})
c=Competition(cfg);c.ensure_wait(t_monde=3,st_version="st:3")
wait=c.candidate_proposals[0]
option=replace(wait.option,id="candidate:contract",plan_ref="plan:contract",learning_signature="candidate:contract")
plan=replace(wait.plan,id="plan:contract",option_ref=option.id)
initial=OptionProposal(option,plan)
assert c.register(initial,active_goal_id=None,t_monde=3)
c.evaluate(cycle=1,t_monde=3)
assert c.accumulator_for(option.id)>0
cases=(
 {"version":"2"},
 {"type":"composite"},
 {"preconditions":("changed",)},
 {"success_condition":"different"},
 {"failure_condition":"different"},
 {"invalidation_condition":"different"},
)
for changes in cases:
 changed=OptionProposal(replace(option,**changes),plan)
 assert c.register(changed,active_goal_id=None,t_monde=3)
 assert c.accumulator_for(option.id)==0, changes
 assert c.register(initial,active_goal_id=None,t_monde=3)
 c.evaluate(cycle=2,t_monde=3)
 assert c.accumulator_for(option.id)>0
cold=Competition(cfg)
image=c.export_causal_state();cold.restore_causal_state(image)
assert cold.export_causal_state()==image
print("I1_412_OUTCOME_IDENTITY_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_412_OUTCOME_IDENTITY_OK",p.stdout)
