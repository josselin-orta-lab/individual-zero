"""Spatial residual Competition evidence requires witnessed arrival."""
import os, subprocess, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class ConfirmationGate(unittest.TestCase):
 def test_generated_owner_contract(self):
  with TemporaryDirectory() as d:
   out=Path(d)/"generated";generate(out)
   code=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig,AppliedMemoryIntention
from i0.contracts import Option,OptionProposal,Plan,PlanStep,MotiveRef
from i0.interfaces import PrimitiveCommand
from copy import deepcopy
cfg=CompetitionConfig(version="confirmed-owner-v1",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,options_max=6,substitution_evidence={})
def proposal():
 ref="place:object:at:3:0:from:1:0:via:2:0";oid="option:place-memory:"+ref
 plan=Plan(id="plan:"+oid,option_ref=oid,version="1",steps=(PlanStep(index=0,command=PrimitiveCommand("se_deplacer",{"direction":"east"}),preconditions=("adjacent_passable",)),),goal_ref="goal:test",budget_used_uc=1,status="valid",st_version="st:2")
 option=Option(id=oid,version="1",type="primitive",learning_signature="memory_place_return:object",preconditions=("adjacent_passable",),success_condition="target_position_observed",failure_condition="target_position_not_observed",invalidation_condition="observed_entity_place_or_goal_changed",motive_ref=MotiveRef(type="place_memory",id=ref),founding_st_version="st:2",expires_at_step=8,provenance="memory",goal_ref="goal:test",plan_ref=plan.id)
 return OptionProposal(option=option,plan=plan)
def owner():
 c=Competition(cfg);c.open_deliberation(active_goal_id="goal:test",t_monde=2)
 p=proposal();assert c.register(p,active_goal_id="goal:test",t_monde=2)
 intent=AppliedMemoryIntention(semantic_ref="memory_place_return:object",source_option_ref="option:place-memory:place:object:at:3:0:from:0:0:via:1:0",goal_ref="goal:test",expected_position=(1,0),observed_site=(3,0),applied_step=1,expires_at_step=8,evidence=.7)
 intent.validate();c._applied_memory_intent=intent
 return c,p,intent
c,p,intent=owner()
assert not c.retain_bounded_intention_evidence(option_ref=p.option.id,t_monde=2,observed_origin=(1,0),evidence=.2)
assert c.accumulator_for(p.option.id)==0
for changed in (replace(intent,reconsidered_step=2),replace(intent,reconsidered_step=3)):
 try:changed.validate()
 except ValueError:pass
 else:raise AssertionError("unconfirmed reentry accepted")
assert c.observe_memory_intention(world_step=2,observed_position=(1,0))=="reconsider"
assert c.applied_memory_intention.confirmed_step==2
image=c.export_causal_state();other=Competition(cfg);other.restore_causal_state(image)
assert other.export_causal_state()==image
assert other.retain_bounded_intention_evidence(option_ref=p.option.id,t_monde=2,observed_origin=(1,0),evidence=.2)
assert 0<other.accumulator_for(p.option.id)<cfg.base_threshold
for forged in (replace(intent,reconsidered_step=2),replace(intent,reconsidered_step=3)):
 state=deepcopy(image);state["applied_memory_intention"]["confirmed_step"]=None;state["applied_memory_intention"]["reconsidered_step"]=forged.reconsidered_step
 before=other.export_causal_state()
 try:other.restore_causal_state(state)
 except ValueError:pass
 else:raise AssertionError("forged confirmed M11 intent")
 assert other.export_causal_state()==before
contradicted,q,_=owner()
assert contradicted.observe_memory_intention(world_step=2,observed_position=(0,0))=="contradicted"
assert not contradicted.retain_bounded_intention_evidence(option_ref=q.option.id,t_monde=2,observed_origin=(1,0),evidence=.2)
print("I1_372_CONFIRMED_SPATIAL_EVIDENCE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",code],cwd=ROOT,env=env,capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_372_CONFIRMED_SPATIAL_EVIDENCE_OK",p.stdout)
if __name__=="__main__":unittest.main()
