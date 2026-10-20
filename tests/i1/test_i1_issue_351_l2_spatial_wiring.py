"""Owner-level and canonical birth smoke for spatial intention continuity.

The two-hop owner contract is deterministic and negative-case-tested. The
natural birth smoke is a *software* check, not a forced behavioral cohort.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SpatialIntentionL2Tests(unittest.TestCase):
    def test_generated_wiring_and_owner_roundtrip(self):
        with TemporaryDirectory(prefix="i1-351-") as tmp:
            output = Path(tmp) / "generated"
            generate(output)
            code = '''
from dataclasses import replace
import inspect
from i0.contracts import Option, OptionProposal, Plan, PlanStep, MotiveRef
from i0.interfaces import PrimitiveCommand
from i1.modules.competition import Competition, CompetitionConfig
from i1lab.stage11_runtime import Stage11Runtime
from i1.experimental.intention_continuity import IntentEvidence, bounded_continuation
assert "record_applied_memory_intention" in inspect.getsource(Stage11Runtime._dispatch_decision)
assert "retain_bounded_intention_evidence" in inspect.getsource(Stage11Runtime._phase_hooks)
cfg = CompetitionConfig(
    version="l2-intention-test", c_max=2, urgency_max=1.0,
    urgency_scale_cycles=1.0, leak=0.0, noise_sigma=0.0, gain=1.0,
    base_threshold=0.5, threshold_floor=0.1, inertia=0.0,
    residual=0.5, options_max=6, substitution_evidence={"se_deplacer": 0.7})
def proposal(origin,via):
    entity="personally-seen-object"
    site=(2,1)
    target=(f"place:{entity}:at:{site[0]}:{site[1]}:from:"
            f"{origin[0]}:{origin[1]}:via:{via[0]}:{via[1]}")
    ident="option:place-memory:"+target
    plan=Plan(id="plan:"+ident,option_ref=ident,version="1",
              steps=(PlanStep(index=0,
                 command=PrimitiveCommand("se_deplacer",{"direction":"east" if
                   via[0]>origin[0] else "north"}),
                 preconditions=("adjacent_passable",)),),
              goal_ref="goal:test",budget_used_uc=1,status="valid",st_version="st:1")
    option=Option(id=ident,version="1",type="primitive",
              learning_signature="memory_place_return:"+entity,
              preconditions=("adjacent_passable",),
              success_condition="target_position_observed",
              failure_condition="target_position_not_observed",
              invalidation_condition="observed_entity_place_or_goal_changed",
              motive_ref=MotiveRef(type="place_memory", id=target),
              founding_st_version="st:1",expires_at_step=6,
              provenance="memory",goal_ref="goal:test",
              plan_ref=plan.id,state="proposed")
    p=OptionProposal(option=option,plan=plan)
    p.validate()
    return p
first=proposal((0,0),(1,0))
second=proposal((1,0),(2,0))
c=Competition(cfg)
assert c.register(first,active_goal_id="goal:test",t_monde=1)
assert c.evaluate(cycle=1,t_monde=1).winner.option.id==first.option.id
# No registration-only, failed admission, wrong prior step or fallback may create an intention.
assert c.record_applied_memory_intention(
    option_ref=first.option.id,verified_control_step=(first.option.id,first.plan.id,0),
    applied_step=1,expected_position=(1,0),observed_site=(2,1),
    fallback_used=False) is False
assert c.record_applied_memory_intention(
    option_ref=first.option.id,verified_control_step=(first.option.id,first.plan.id,1),
    applied_step=1,expected_position=(1,0),observed_site=(2,1),
    fallback_used=True) is False
assert c.applied_memory_intention is None
assert c.record_applied_memory_intention(
    option_ref=first.option.id,verified_control_step=(first.option.id,first.plan.id,1),
    applied_step=1,expected_position=(1,0),observed_site=(2,1),
    fallback_used=False) is True
c.close_deliberation(first,adjudicated=True)
authenticated=c.export_causal_state()
assert authenticated["applied_memory_intention"]["semantic_ref"]=="memory_place_return:personally-seen-object"
cold=Competition(cfg)
cold.restore_causal_state(authenticated)
assert cold.export_causal_state()==authenticated
cold.open_deliberation(active_goal_id="goal:test",t_monde=2)
assert cold.accumulator_for(first.option.id)==0.0, "normal motor engagement must reset"
assert cold.applied_memory_intention.evidence>=0.5, "semantic evidence must survive"
assert cold.register(second,active_goal_id="goal:test",t_monde=2)
kw=dict(option_ref=second.option.id,t_monde=2,observed_origin=(1,0),evidence=0.25)
for bad in (float("nan"),float("inf"),-0.1,True):
    try:
        cold.retain_bounded_intention_evidence(**(kw|{"evidence":bad}))
        raise AssertionError("invalid evidence was accepted")
    except ValueError:
        pass
assert not cold.retain_bounded_intention_evidence(**(kw|{"observed_origin":(0,0)}))
assert not cold.retain_bounded_intention_evidence(**(kw|{"t_monde":3}))
assert cold.retain_bounded_intention_evidence(**kw)
value=cold.accumulator_for(second.option.id)
assert 0<value<cfg.base_threshold
assert cold.engaged_option_id!=second.option.id
assert not cold.retain_bounded_intention_evidence(**kw), "cannot credit same hop twice"
assert cold.applied_memory_intention.reconsidered_step==2
persisted=cold.export_causal_state()
fresh=Competition(cfg)
fresh.restore_causal_state(persisted)
assert fresh.export_causal_state()==persisted
for corrupt in (float("nan"),"wrong"):
    bad=dict(persisted)
    bad["applied_memory_intention"]=dict(persisted["applied_memory_intention"],evidence=corrupt)
    snapshot=fresh.export_causal_state()
    try:
        fresh.restore_causal_state(bad)
        raise AssertionError("corrupted M11 owner image accepted")
    except ValueError:
        pass
    assert fresh.export_causal_state()==snapshot, "restore must be atomic"
fresh.open_deliberation(active_goal_id="goal:other",t_monde=3)
assert fresh.applied_memory_intention is not None
assert not fresh.retain_bounded_intention_evidence(**kw)
fresh.open_deliberation(active_goal_id="goal:test",t_monde=6)
assert fresh.applied_memory_intention is None, "expired cognitive proof persisted"
prior=IntentEvidence("memory_place_return:site",1,(1,0),0.4)
assert bounded_continuation(prior,intended_ref="memory_place_return:site",
    now_step=2,observed_origin=(1,0),ceiling=0.5,residual=0.5,applied=True)==0.25
print("I1_351_APPLIED_INTENTION_OWNER_OK")
'''
            env = dict(os.environ, PYTHONPATH=str(output) + os.pathsep + str(ROOT / "src"),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", code],
                                  cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_351_APPLIED_INTENTION_OWNER_OK", proc.stdout)

    def test_canonical_m11_birth_and_cold_recovery_unchanged(self):
        with TemporaryDirectory(prefix="i1-351-m11-") as tmp:
            output = Path(tmp) / "generated"
            generate(output)
            script = '''
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
base=build_stage11_reference_runtime(autonomous_mortal=True)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
stage10=replace(sleep._stage10_config,stage9=base._stage11_config.stage9)
det=Stage12DetectionPolicy(version="i1-351-m11",window=12,
    stagnation_steps=3,stagnation_tolerance=.05,loop_repetitions=2,
    loop_max_period=2,entropy_min_samples=3,entropy_warning_fraction=.25,
    bias_min_outcomes_each=2,attribution_bias_threshold=.75)
identity="i1:351:technical"
params=dict(world_config=base.world.config,layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
    stage11_config=base._stage11_config,stage10_config=stage10,
    equipment=base.equipment,detector_policy=det)
def factory():
    return I1Runtime(birth_life_id=identity,autonomous_mortal=True,
         m11_sqlite_custody=True,wal_path=None,**params)
with TemporaryDirectory() as location:
    db=str(Path(location)/"life.sqlite")
    with birth_i1_m11(db_path=db,life_id=identity,**params) as live:
        assert live._runtime.competition.applied_memory_intention is None
        before=live.run_step()
        assert before.status=="active"
        assert live._runtime.competition.applied_memory_intention is None
    with recover_i1_m11(db_path=db,life_id=identity,runtime_factory=factory) as restored:
        assert restored._runtime.competition.applied_memory_intention is None
        after=restored.run_step()
        assert after.status=="active"
        assert after.generation==before.generation+1
print("I1_351_CANONICAL_M11_OK")
'''
            env = dict(os.environ, PYTHONPATH=str(output) + os.pathsep + str(ROOT / "src"),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", script],
                                  cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_351_CANONICAL_M11_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
