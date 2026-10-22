"""An engaged motor plan cannot be replaced while retaining prior evidence."""
import os,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class EngagedPlanIdentity(unittest.TestCase):
 def test_generated_owner_m11(self):
  with TemporaryDirectory(prefix="i1-416-") as home:
   out=Path(home)/"generated";generate(out)
   script=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig
from i0.contracts import OptionProposal,PlanStep
from i0.interfaces import PrimitiveCommand
cfg=CompetitionConfig(version="416",c_max=3,urgency_max=1.,urgency_scale_cycles=1.,
 leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,
 inertia=0.,residual=.5,options_max=5,substitution_evidence={"attendre":.7})
c=Competition(cfg);c.ensure_wait(t_monde=3,st_version="st:3")
wait=c.candidate_proposals[0]
option=replace(wait.option,id="candidate:stable",plan_ref="plan:stable",learning_signature="memory:stable")
plan=replace(wait.plan,id="plan:stable",option_ref=option.id)
initial=OptionProposal(option,plan)
assert c.register(initial,active_goal_id=None,t_monde=3)
result=c.evaluate(cycle=1,t_monde=3)
assert any(p.option.id==option.id for p in result.crossed_ranked)
c.close_deliberation(initial)
engaged=c.export_causal_state()
changed=OptionProposal(option,replace(plan,steps=(replace(plan.steps[0],command=PrimitiveCommand("se_deplacer",{"direction":"north"})),)))
assert c.material_plan_change(initial,changed)
assert c.register(changed,active_goal_id=None,t_monde=4) is False
assert c.export_causal_state()==engaged
assert c.register(initial,active_goal_id=None,t_monde=4) is True
cold=Competition(cfg);image=c.export_causal_state();cold.restore_causal_state(image)
assert cold.export_causal_state()==image
other=Competition(cfg);other.ensure_wait(t_monde=3,st_version="st:3")
assert other.register(initial,active_goal_id=None,t_monde=3)
other.evaluate(cycle=1,t_monde=3)
assert other.accumulator_for(option.id)>0
assert other.register(changed,active_goal_id=None,t_monde=4)
assert other.accumulator_for(option.id)==0
print("I1_416_ENGAGED_PLAN_IDENTITY_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   result=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   self.assertIn("I1_416_ENGAGED_PLAN_IDENTITY_OK",result.stdout)
