"""Obsolete goal candidates are pruned even when refresh UC is denied."""
import os,sys,subprocess,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class GoalPruningBoundary(unittest.TestCase):
 def test_generated_stage4_wiring_and_owner(self):
  with TemporaryDirectory(prefix="i1-406-") as tmp:
   out=Path(tmp)/"generated";generate(out)
   script=r"""
from dataclasses import replace
import inspect
from i1lab.stage4_runtime import Stage4Runtime
from i1.modules.competition import Competition,CompetitionConfig
from i0.contracts import OptionProposal, MotiveRef
src=inspect.getsource(Stage4Runtime._phase_hooks)
reg=src[src.index("def competition_registration_hook"):src.index("def competition_decision_hook")]
assert reg.index("self.competition.prune_invalid(")<reg.index('operation="competition_register"')
cfg=CompetitionConfig(version="406",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,
 leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,
 inertia=0.,residual=.5,options_max=5,substitution_evidence={})
c=Competition(cfg)
c.ensure_wait(t_monde=4,st_version="st:4")
wait=c.candidate_proposals[0]
opt=replace(wait.option,id="candidate:goal:old",goal_ref="goal:old",
 motive_ref=MotiveRef(type="active_goal",id="goal:old"),
 plan_ref="plan:goal:old")
plan=replace(wait.plan,id="plan:goal:old",option_ref=opt.id,goal_ref="goal:old")
proposal=OptionProposal(option=opt,plan=plan)
assert c.register(proposal,active_goal_id="goal:old",t_monde=4)
assert c.proposal_for(opt.id) is not None
c.prune_invalid(active_goal_id="goal:new",t_monde=4)
assert c.proposal_for(opt.id) is None
assert c.proposal_for("permanent:attendre") is not None
image=c.export_causal_state()
restored=Competition(cfg);restored.restore_causal_state(image)
assert restored.export_causal_state()==image
print("I1_406_GOAL_PRUNE_BEFORE_UC_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_406_GOAL_PRUNE_BEFORE_UC_OK",p.stdout)
