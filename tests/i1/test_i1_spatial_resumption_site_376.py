"""Interrupted spatial intention remains site-specific and motor-neutral."""
import os, subprocess, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ResumptionSite(unittest.TestCase):
 def test_generated_competition_cold_and_goal_switch(self):
  with TemporaryDirectory() as tmp:
   output=Path(tmp)/"generated";generate(output)
   script=r"""
from i1.modules.competition import Competition,CompetitionConfig,AppliedMemoryIntention
from i0.contracts import Option,OptionProposal,Plan,PlanStep,MotiveRef
from i0.interfaces import PrimitiveCommand
cfg=CompetitionConfig(version="376",c_max=2,urgency_max=1.,urgency_scale_cycles=1.,
 leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,
 inertia=0.,residual=.5,options_max=5,substitution_evidence={})
entity="sighting:berry_a:3:0"
def proposal(site,step):
 ref=f"place:{entity}:at:{site[0]}:{site[1]}:from:1:0:via:2:0"
 oid="option:place-memory:"+ref
 plan=Plan(id="plan:"+oid,option_ref=oid,version="1",steps=(
  PlanStep(index=0,command=PrimitiveCommand("se_deplacer",{"direction":"east"}),
   preconditions=("adjacent_passable",)),),goal_ref="goal:food",
  budget_used_uc=1,status="valid",st_version="st:6")
 option=Option(id=oid,version="1",type="primitive",
  learning_signature="memory_place_return:"+entity,
  preconditions=("adjacent_passable",),success_condition="target_position_observed",
  failure_condition="target_position_not_observed",
  invalidation_condition="observed_entity_place_or_goal_changed",
  motive_ref=MotiveRef(type="place_memory",id=ref),founding_st_version="st:6",
  expires_at_step=12,provenance="memory",goal_ref="goal:food",plan_ref=plan.id)
 p=OptionProposal(option=option,plan=plan);p.validate()
 return p
owner=Competition(cfg)
intent=AppliedMemoryIntention(semantic_ref="memory_place_return:"+entity,
 source_option_ref="option:place-memory:place:"+entity+":at:3:0:from:0:0:via:1:0",
 goal_ref="goal:food",expected_position=(1,0),observed_site=(3,0),
 applied_step=2,expires_at_step=11,evidence=.7,confirmed_step=3)
intent.validate();owner._applied_memory_intent=intent
image=owner.export_causal_state()
cold=Competition(cfg);cold.restore_causal_state(image)
assert cold.export_causal_state()==image
cold.open_deliberation(active_goal_id="goal:water",t_monde=4)
assert cold.applied_memory_intention is not None
assert cold.observe_memory_intention(world_step=5,observed_position=(8,8))=="suspended"
cold.open_deliberation(active_goal_id="goal:food",t_monde=6)
wrong=proposal((9,0),6)
assert cold.register(wrong,active_goal_id="goal:food",t_monde=6)
before=cold.export_causal_state()
assert not cold.reconsider_confirmed_intention(option_ref=wrong.option.id,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:food")
assert cold.export_causal_state()==before
assert cold.accumulator_for(wrong.option.id)==0
correct=proposal((3,0),6)
assert cold.register(correct,active_goal_id="goal:food",t_monde=6)
assert cold.reconsider_confirmed_intention(option_ref=correct.option.id,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:food")
assert cold.accumulator_for(correct.option.id)==0
assert not cold.reconsider_confirmed_intention(option_ref=correct.option.id,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:food")
restored=Competition(cfg);state=cold.export_causal_state()
restored.restore_causal_state(state)
assert restored.export_causal_state()==state
restored.open_deliberation(active_goal_id="goal:food",t_monde=11)
assert restored.applied_memory_intention is None
print("I1_376_SPATIAL_RESUMPTION_SITE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(output),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   result=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   self.assertIn("I1_376_SPATIAL_RESUMPTION_SITE_OK",result.stdout)
if __name__=="__main__":unittest.main()
