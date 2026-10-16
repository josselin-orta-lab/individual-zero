"""D1: generated I1 learning and M11 cold-recovery smoke/invariant gate."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate


def _check_script(generated: Path, source: str) -> str:
    env=os.environ.copy()
    env["PYTHONPATH"]=str(generated)+os.pathsep+str(ROOT/"src")
    result=subprocess.run([sys.executable,"-c",source],env=env,
                          capture_output=True,text=True,timeout=150)
    if result.returncode:
        raise AssertionError(
            f"child code returned {result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}")
    return result.stdout


SETUP = '''
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.i1_water_runtime import I1WaterLearningRuntime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1lab.world import Position
from i1lab.injected_scenario import ScenarioEvent
s11=build_stage11_reference_runtime(enable_geography=True,autonomous_mortal=True)
s10=build_stage10_reference_runtime(autonomous_mortal=True)
c11=s11._stage11_config
c9=c11.stage9;c8=c9.stage8;c7=c8.stage7;c6=c7.stage6;c4=c6.stage4
v=replace(c4.value_needs,
    version="i136-d1-needs-v1",
    setpoints={**c4.value_needs.setpoints,"water":95.0})
p=replace(c6.planning,
    version="i136-d1-planning-v1",
    setpoints={**c6.planning.setpoints,"water":95.0})
new9=replace(c9,stage8=replace(c8,stage7=replace(c7,stage6=replace(
    c6,stage4=replace(c4,value_needs=v),planning=p))))
new11=replace(c11,stage9=new9)
sleep=replace(s10._stage10_config.sleep,fatigue_gain=0.0,
              night_weight=0.0,consolidation_weight=0.0)
new10=replace(s10._stage10_config,stage9=new9,sleep=sleep)
config=replace(s11.world.config,
               initial_body=replace(s11.world.config.initial_body,
                   energy=65.0,food=80.0,water=1.0,integrity=100.0))
origin=config.initial_position
remote=Position(12,12)
layout=replace(s11.world._layout,water_sources=frozenset(
    {origin,remote.moved("east")}),resources=(),obstacles=frozenset(),
    creatures=frozenset(),danger_zones=frozenset(),lethal_zones=frozenset())
policy=Stage12DetectionPolicy(version="i136-d1-test-v1",
    window=12,stagnation_steps=3,stagnation_tolerance=.05,
    loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
    entropy_warning_fraction=.25,bias_min_outcomes_each=2,
    attribution_bias_threshold=.75)
events=(ScenarioEvent(t_monde=3,sequence=0,operation="set_position",
    payload={"position":remote.as_dict()}),)
def make(basedir,enabled=True,m11=False):
    return I1WaterLearningRuntime(
        world_config=config,layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=new11,stage10_config=new10,
        equipment=s11.equipment,autonomous_mortal=True,
        wal_path=None if m11 else str(Path(basedir)/"life.wal"),
        m11_sqlite_custody=m11,birth_life_id="i1:d1:test:one",
        diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
        detector_policy=policy,
        i1_model_enabled=False,
        i1_water_probe_enabled=True,i1_water_learning_enabled=enabled,
        i1_water_consider_uc=2,i1_water_acquire_uc=2,
        scenario_id="d1:smoke",scenario_version="d1-test-v1",
        scenario_events=events)
'''


class I1WaterD1Tests(unittest.TestCase):
    def test_owner_has_no_oracle_or_unguarded_recovery(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            output=_check_script(generated, SETUP+'''
from i1.experimental.lived_water import I1LivedWaterOwner
from i1lab.i1_water_runtime import _I1WaterM11Owner
owner=_I1WaterM11Owner(life_id="i1:d1:test:one",enabled=True)
initial=owner.export_causal_state()
assert owner.observed_water_gain is None
owner.record_applied(sent_world_step=1,before_water=1.0,
    x=2,y=2,command_hash="a"*64,option_ref="test",
    first_capture_hash="b"*64)
assert owner.observed_water_gain is None
r=owner.observe_followup(observed_world_step=2,x=2,y=2,
    observed_water=41,current_water_source=True,
    followup_capture_hash="c"*64,paid_uc=True)
assert r["admitted"] and owner.observed_water_gain==40.0
try:
    owner.restore_causal_state(initial)
    raise AssertionError("historic rollback accepted")
except ValueError:
    pass
other=_I1WaterM11Owner(life_id="i1:d1:test:one",enabled=True)
try:
    other.install_m11_cold_state(owner.export_causal_state(),
        capability=object())
    raise AssertionError("public cold install accepted")
except ValueError:
    pass
assert other.examples==()
print("D1_OWNER_DENIAL_OK")
''')
            self.assertIn("D1_OWNER_DENIAL_OK",output)

    def test_autonomous_steps_with_logged_relocation(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            output=_check_script(generated, SETUP+'''
with TemporaryDirectory() as folder:
    life=make(folder,True)
    records=[]
    for _ in range(6):
        result=life.run_step()
        records.append((result.execution_status,result.command_primitive,
            life.world.position.as_dict(),life.world.telemetry()["water"],
            life.lived_water_model["examples"]))
        if result.execution_status!="applied":
            break
    assert life.journal.verify()
    assert life.stage3.substrate.bench is None
    assert life.equipment.artifact_digest==s11.equipment.artifact_digest
    print("D1_LIFE_SMOKE:"+repr([(r[0],r[1],r[2],r[3],len(r[4])) for r in records]))
''')
            self.assertIn("D1_LIFE_SMOKE:",output)

    def test_m11_commits_and_cold_recovers_registered_owner(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            output=_check_script(generated, SETUP+'''
from i1lab.m11_transactional_mortal import M11TransactionalMortal
with TemporaryDirectory() as folder:
    def fresh():
        return make(folder,True,m11=True)
    path=str(Path(folder)/"d1.sqlite")
    with M11TransactionalMortal.birth(
            db_path=path,runtime=fresh(),individual_id="i1:d1:test:one") as live:
        first=live.run_step()
        assert first.generation==1 and first.status=="active"
    with M11TransactionalMortal.cold_recover(
            db_path=path,individual_id="i1:d1:test:one",
            runtime_factory=fresh) as recovered:
        second=recovered.run_step()
        assert second.generation==2
        assert second.status=="active"
    print("D1_M11_COLD_OK")
''')
            self.assertIn("D1_M11_COLD_OK",output)


    def test_m11_learned_evidence_persists_and_changes_cold_decision(self):
        # Post-result software gate: an authentic D1-B north water
        # experience must survive M11 cold restart before a remote action.
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            generate(generated)
            output=_check_script(generated, SETUP+'''
from i1lab.m11_transactional_mortal import M11TransactionalMortal
layout=replace(layout,water_sources=frozenset({
    origin.moved("north"), remote.moved("east")}))
events=(ScenarioEvent(t_monde=4,sequence=0,operation="set_position",
    payload={"position":remote.as_dict()}),)
with TemporaryDirectory() as folder:
    def fresh():
        return make(folder,True,m11=True)
    path=str(Path(folder)/"learned.sqlite")
    with M11TransactionalMortal.birth(
            db_path=path,runtime=fresh(),
            individual_id="i1:d1:test:one") as live:
        for _ in range(3):
            receipt=live.run_step()
            assert receipt.status=="active",receipt
        learned=live._runtime.lived_water_model
        assert learned["enabled"]
        assert learned["examples"],learned
        assert learned["examples"][0]["sent_world_step"]==2
        assert learned["examples"][0]["observed_world_step"]==3
        before=learned["examples"]
    with M11TransactionalMortal.cold_recover(
            db_path=path,individual_id="i1:d1:test:one",
            runtime_factory=fresh) as recovered:
        assert recovered._runtime.lived_water_model["examples"]==before
        action=recovered.run_step()
        assert action.status=="active",action
        assert action.outcome=="applied",action
        assert recovered._runtime.world.position==remote.moved("east")
        drink=recovered.run_step()
        assert drink.outcome=="applied",drink
        assert recovered._runtime.world.telemetry()["water"]>80
        assert recovered._runtime.lived_water_model["examples"][:1]==before[:1]
    print("D1_M11_LEARNED_COLD_TRANSFER_OK")
''')
            self.assertIn("D1_M11_LEARNED_COLD_TRANSFER_OK",output)

if __name__=="__main__":
    unittest.main()
