"""Applied spatial intent provenance cannot diverge across M11 owners.

Software and short real-step custody checks only, not spontaneous route proof.
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


class SpatialIntentionProvenance(unittest.TestCase):
    def run_generated(self, program):
        with TemporaryDirectory(prefix="i1-375-build-") as tmp:
            built = Path(tmp) / "generated"
            generate(built)
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join(
                           (str(built), str(ROOT / "src"), str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
            return result.stdout

    def test_competition_applied_option_and_atomic_cold_restore(self):
        self.assertIn("I1_375_CAUSAL_OPTION_IDENTITY_OK",
                      self.run_generated(r"""
from copy import deepcopy
from dataclasses import replace
from i0.contracts import Option, OptionProposal, Plan, PlanStep, MotiveRef
from i0.interfaces import PrimitiveCommand
from i1.modules.competition import Competition, CompetitionConfig

cfg=CompetitionConfig(
    version="i1-375", c_max=2, urgency_max=1.0, urgency_scale_cycles=1.0,
    leak=0.0, noise_sigma=0.0, gain=1.0,
    base_threshold=0.5, threshold_floor=0.1, inertia=0.0,
    residual=0.5, options_max=6, substitution_evidence={"se_deplacer":0.7})
entity="sighting:berry_a:2:1"
target=f"place:{entity}:at:2:1:from:0:0:via:1:0"
oid="option:place-memory:"+target
plan=Plan(id="plan:"+oid,option_ref=oid,version="1",
    steps=(PlanStep(index=0,command=PrimitiveCommand("se_deplacer",
    {"direction":"east"}),preconditions=("adjacent_passable",)),),
    goal_ref="goal:food",budget_used_uc=1,status="valid",st_version="st:1")
option=Option(
    id=oid,version="1",type="primitive",
    learning_signature="memory_place_return:"+entity,
    preconditions=("adjacent_passable",),
    success_condition="target_position_observed",
    failure_condition="target_position_not_observed",
    invalidation_condition="observed_entity_place_or_goal_changed",
    motive_ref=MotiveRef(type="place_memory",id=target),
    founding_st_version="st:1",expires_at_step=9,
    provenance="memory",goal_ref="goal:food",plan_ref=plan.id,state="proposed")
proposal=OptionProposal(option=option,plan=plan)
proposal.validate()
c=Competition(cfg)
assert c.register(proposal,active_goal_id="goal:food",t_monde=1)
assert c.evaluate(cycle=1,t_monde=1).winner.option.id==oid
source=(oid,plan.id,1)
for expected,site in (((0,1),(2,1)),((1,0),(5,5))):
    before=c.export_causal_state()
    assert not c.record_applied_memory_intention(
        option_ref=oid,verified_control_step=source,
        applied_step=1,expected_position=expected,
        observed_site=site,fallback_used=False)
    assert c.export_causal_state()==before
assert c.record_applied_memory_intention(
    option_ref=oid,verified_control_step=source,
    applied_step=1,expected_position=(1,0),
    observed_site=(2,1),fallback_used=False)
intent=c.applied_memory_intention
intent.validate()
assert intent.semantic_ref=="memory_place_return:"+entity
assert intent.expected_position==(1,0) and intent.observed_site==(2,1)
image=c.export_causal_state()
cold=Competition(cfg)
cold.restore_causal_state(image)
assert cold.export_causal_state()==image
# Historical semantic identity, observed site and intended first hop cannot be
# edited independently in an authenticated owner snapshot.
bad_refs=(
    "option:place-memory:place:sighting:other:2:1:at:2:1:from:0:0:via:1:0",
    "option:place-memory:place:sighting:berry_a:2:1:at:7:7:from:0:0:via:1:0",
    "option:place-memory:place:sighting:berry_a:2:1:at:2:1:from:0:0:via:0:1",
    "option:place-memory:place:sighting:berry_a:2:1:at:2:1:from:0:0:via:2:0",
    "option:place-memory:place:sighting:berry_a:2:1:at:2:1:from:0:0:via:01:0",
)
variants=[("source_option_ref",v) for v in bad_refs]+[
    ("semantic_ref","memory_place_return:sighting:other:2:1"),
    ("expected_position",[0,1]),("observed_site",[3,1]),
]
for key,value in variants:
    bad=deepcopy(image)
    bad["applied_memory_intention"][key]=value
    baseline=cold.export_causal_state()
    try: cold.restore_causal_state(bad)
    except ValueError: pass
    else: raise AssertionError("forged spatial witness accepted: "+key)
    assert cold.export_causal_state()==baseline
assert cold.observe_memory_intention(world_step=2,observed_position=(1,0))=="reconsider"
assert cold.applied_memory_intention.confirmed_step==2
confirmed=cold.export_causal_state()
again=Competition(cfg)
again.restore_causal_state(confirmed)
assert again.export_causal_state()==confirmed
assert again.applied_memory_intention.semantic_ref=="memory_place_return:"+entity
print("I1_375_CAUSAL_OPTION_IDENTITY_OK")
"""))

    def test_canonical_m11_two_steps_no_forged_spatial_provenance(self):
        self.assertIn("I1_375_CANONICAL_M11_CUSTODY_OK",
                      self.run_generated(r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset,_birth_parameters
preset,_=load_preset("oasis")
params,_=_birth_parameters(preset)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:375:source-consistency"
def new_runtime():
    return I1Runtime(
        birth_life_id=life_id,wal_path=None,
        autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory(prefix="i1-375-life-") as tmp:
    path=str(Path(tmp)/"life.sqlite")
    with birth_i1_m11(db_path=path,life_id=life_id,**params) as born:
        receipt=born.run_step()
        assert receipt.status=="active"
        before=born._runtime.competition.export_causal_state()
        if born._runtime.competition.applied_memory_intention is not None:
            born._runtime.competition.applied_memory_intention.validate()
    audit=SQLiteLifeLedger.audit_read_only(
        path=path,expected_individual_id=life_id)
    assert audit.may_recover and audit.generation==1 and not audit.pending_intent
    with recover_i1_m11(
        db_path=path,life_id=life_id,runtime_factory=new_runtime) as cold:
        assert cold._runtime.competition.export_causal_state()==before
        if cold._runtime.competition.applied_memory_intention is not None:
            cold._runtime.competition.applied_memory_intention.validate()
        second=cold.run_step()
        assert second.status=="active" and second.generation==2
        if cold._runtime.competition.applied_memory_intention is not None:
            cold._runtime.competition.applied_memory_intention.validate()
    final=SQLiteLifeLedger.audit_read_only(
        path=path,expected_individual_id=life_id)
    assert final.may_recover and final.generation==2 and not final.pending_intent
print("I1_375_CANONICAL_M11_CUSTODY_OK")
"""))


if __name__ == "__main__":
    unittest.main()
