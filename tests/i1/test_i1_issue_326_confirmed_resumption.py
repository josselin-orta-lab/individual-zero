"""L2 #326: confirmed semantic intent survives intervening steps but not authority."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate
class ConfirmedIntentTests(unittest.TestCase):
    def test_generated_owner_and_canonical_wiring(self):
        with TemporaryDirectory() as d:
            out=Path(d)/"generated"
            generate(out)
            script="""
from i1.modules.competition import Competition,CompetitionConfig
from i1lab.stage11_runtime import Stage11Runtime
import inspect
from tests.i1.test_i1_issue_351_l2_spatial_wiring import SpatialIntentionL2Tests
assert 'reconsider_confirmed_intention' in inspect.getsource(Stage11Runtime._evaluate_competition_cycle)
assert 'reconsider_confirmed_intention' not in inspect.getsource(Stage11Runtime._phase_hooks)
assert 'motor_admission_inherited' in inspect.getsource(Stage11Runtime._evaluate_competition_cycle)
cfg=CompetitionConfig(version='326',c_max=2,urgency_max=1.,urgency_scale_cycles=1.,
 leak=0.,noise_sigma=0.,gain=1.,base_threshold=.5,threshold_floor=.1,
 inertia=0.,residual=.5,options_max=4,substitution_evidence={})
from i1.modules.competition import AppliedMemoryIntention
intent=AppliedMemoryIntention(semantic_ref='memory_place_return:stone',
 source_option_ref='option:place-memory:place:stone:at:3:0:from:0:0:via:1:0',
 goal_ref='goal:test',expected_position=(1,0),observed_site=(3,0),
 applied_step=2,expires_at_step=15,evidence=.75)
intent.validate()
c=Competition(cfg)
c._applied_memory_intent=intent
assert c.observe_memory_intention(world_step=3,observed_position=(1,0))=='reconsider'
assert c.applied_memory_intention.confirmed_step==3
img=c.export_causal_state()
cold=Competition(cfg)
cold.restore_causal_state(img)
assert cold.export_causal_state()==img
assert cold.observe_memory_intention(world_step=6,observed_position=(9,0))=='suspended'
assert cold.applied_memory_intention.confirmed_step==3
assert not cold.reconsider_confirmed_intention(option_ref='absent',t_monde=6,
 observed_site=(3,0),active_goal_id='goal:test')
assert cold.accumulator_for('absent') is None
# Fresh funded candidate, same personally known site; never inherit old motor evidence.
from i0.contracts import Option, OptionProposal, Plan, PlanStep, MotiveRef
from i0.interfaces import PrimitiveCommand
ref="place:stone:at:3:0:from:1:0:via:2:0"
oid="option:place-memory:"+ref
plan=Plan(id="plan:"+oid,option_ref=oid,version="1",
 steps=(PlanStep(index=0,command=PrimitiveCommand("se_deplacer",{"direction":"east"}),
  preconditions=("adjacent_passable",)),),
 goal_ref="goal:test",budget_used_uc=1,status="valid",st_version="st:2")
option=Option(id=oid,version="1",type="primitive",
 learning_signature="memory_place_return:stone",
 preconditions=("adjacent_passable",),
 success_condition="target_position_observed",
 failure_condition="target_position_not_observed",
 invalidation_condition="observed_entity_place_or_goal_changed",
 motive_ref=MotiveRef(type="place_memory",id=ref),
 founding_st_version="st:2",expires_at_step=12,
 provenance="memory",goal_ref="goal:test",plan_ref=plan.id,state="proposed")
proposal=OptionProposal(option=option,plan=plan)
proposal.validate()
cold.open_deliberation(active_goal_id="goal:test",t_monde=6)
assert cold.register(proposal,active_goal_id="goal:test",t_monde=6)
before=cold.accumulator_for(oid)
assert before==0
assert not cold.reconsider_confirmed_intention(option_ref=oid,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:other")
assert cold.reconsider_confirmed_intention(option_ref=oid,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:test")
assert cold.accumulator_for(oid)==before, "resumption must not create motor credit"
assert not cold.reconsider_confirmed_intention(option_ref=oid,t_monde=6,
 observed_site=(3,0),active_goal_id="goal:test"),"one consideration per step"
persisted=cold.export_causal_state()
rewarmed=Competition(cfg)
rewarmed.restore_causal_state(persisted)
assert rewarmed.export_causal_state()==persisted
contradicted=Competition(cfg)
contradicted._applied_memory_intent=intent
assert contradicted.observe_memory_intention(world_step=3,observed_position=(0,0))=='contradicted'
assert contradicted.applied_memory_intention is None
for bad in (True, 0.2, -1):
 try:
  cold.observe_memory_intention(world_step=bad,observed_position=(1,0))
  raise AssertionError('bad world step accepted')
 except ValueError: pass
print('I1_326_CONFIRMED_INTENT_M11_OK')
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"),str(ROOT))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_326_CONFIRMED_INTENT_M11_OK",p.stdout)
if __name__=="__main__": unittest.main()
