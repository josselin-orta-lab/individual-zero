"""A2.36: all four experimental models active with byte-identical M11 continuation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_i1_fork import generate


class I1A236AllActiveWaterColdRecoveryTests(unittest.TestCase):
    def test_cold_recover_with_admitted_lived_water_and_d2_reviews(self):
        with TemporaryDirectory() as folder:
            output=Path(folder)/"i1build"
            generate(output)
            code="""
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1lab.m11_transactional_mortal import M11TransactionalMortal
from i1lab.injected_scenario import ScenarioEvent
from i1lab.sqlite_life_store import SQLiteLifeLedger,RecoveryBlocked
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel,FIELDS
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from dataclasses import replace
from tempfile import TemporaryDirectory
from pathlib import Path
p=Stage12DetectionPolicy(version="i1-m11-roundtrip-v1",window=12,stagnation_steps=3,
 stagnation_tolerance=.05,loop_repetitions=2,loop_max_period=2,
 entropy_min_samples=3,entropy_warning_fraction=.25,
 bias_min_outcomes_each=2,attribution_bias_threshold=.75)
source=build_stage11_reference_runtime(enable_geography=True,autonomous_mortal=True)
s11=source._stage11_config
s9=s11.stage9;s8=s9.stage8;s7=s8.stage7;s6=s7.stage6;s4=s6.stage4
needs=replace(s4.value_needs,version="a236-m11-water95-needs-v1",
 setpoints={**s4.value_needs.setpoints,"water":95.0})
plan=replace(s6.planning,version="a236-m11-water95-plan-v1",
 setpoints={**s6.planning.setpoints,"water":95.0})
s9=replace(s9,stage8=replace(s8,stage7=replace(s7,
 stage6=replace(s6,stage4=replace(s4,value_needs=needs),planning=plan))))
s11=replace(s11,stage9=s9)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
config=replace(sleep._stage10_config,stage9=s11.stage9,
 sleep=replace(sleep._stage10_config.sleep,fatigue_gain=0.0,
 night_weight=0.0,consolidation_weight=0.0))
delta=tuple((a,tuple((k,1 if k=="x" and a=="MOVE_E" else 0)
 for k in FIELDS)) for a in ("MOVE_E","COLLECT_B"))
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 delta,(("MOVE_E",8),("COLLECT_B",8)))
identity="i1:a236:cold:recall"
physics=replace(source.world.config,version="a236-cold-episode-v1",
 initial_body=replace(source.world.config.initial_body,energy=66.0,
 food=80.0,water=1.0,integrity=100.0))
layout=replace(source.world._layout,
 resources=(),
 water_sources=frozenset({physics.initial_position.moved("north")}),danger_zones=frozenset(),
 lethal_zones=frozenset(),creatures=frozenset(),obstacles=frozenset())
def factory(cost=2,recall=True,recall_cost=1,water=True,water_uc=2,prudence=True,d2_uc=1):
 return I1WaterPrudentRuntime(
  world_config=physics,layout=layout,
  safety_config=source.stage3.substrate.safety._config,
  safety_facts=source._canonical_safety._innate,
  protected_integrity_threshold=source.stage3.control._config.protected_integrity_threshold,
  stage11_config=s11,stage10_config=config,
  equipment=source.equipment,autonomous_mortal=True,
  m11_sqlite_custody=True,wal_path=None,birth_life_id=identity,
  diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
  detector_policy=p,i1_model_enabled=True,i1_model=model,
  i1_forecast_cost_uc=cost,i1_lived_recall_enabled=recall,
  i1_recall_cost_uc=recall_cost,
  i1_water_probe_enabled=True,i1_water_learning_enabled=water,
  i1_water_consider_uc=2,i1_water_acquire_uc=water_uc,
  i1_d2_prudence=prudence,i1_d2_review_uc=d2_uc,
  scenario_id="a236-m11-water-revisit",scenario_version="a236-m11-water-v1",
  scenario_events=(ScenarioEvent(t_monde=4,sequence=0,operation="set_position",
   payload={"position":physics.initial_position.as_dict()}),))
with TemporaryDirectory() as folder:
 path=str(Path(folder)/"i1.sqlite")
 baseline_path=str(Path(folder)/"i1-uninterrupted.sqlite")
 with M11TransactionalMortal.birth(
  db_path=baseline_path,runtime=factory(),individual_id=identity) as baseline:
  for i in range(6):
   stable=baseline.run_step()
   assert stable.status=="active" and stable.generation==i+1
   if i==4: baseline_head_at_five=stable.journal_head
  baseline_head_at_six=stable.journal_head
 candidate=factory()
 from i1lab.stage12_runtime import Stage12Runtime
 assert isinstance(candidate,Stage12Runtime),str(type(candidate).__mro__)
 assert candidate._m11_sqlite_custody is True
 with M11TransactionalMortal.birth(db_path=path,runtime=candidate,
                                    individual_id=identity) as owner:
  for index in range(5):
   receipt=owner.run_step()
   assert receipt.generation==index+1 and receipt.world_step==index+1
   assert receipt.status=="active"
  assert owner._runtime.memory.episodes,"no first-person closed episode"
  assert owner._runtime._i1_enabled
  assert owner._runtime._i1_lived_recall_enabled
  assert owner._runtime._i1_water_learning_enabled
  assert owner._runtime._d2_prudence
  assert any(e.causal_event.get("kind")=="i1_water_lived_outcome_admitted"
   for e in owner._runtime.journal.entries),"missing water learning"
  assert any(e.causal_event.get("kind")=="i1_d2_movement_commitment_review"
   for e in owner._runtime.journal.entries),"missing D2 review"
  assert owner._runtime.lived_water_model["examples"],"empty water owner"
  head=receipt.journal_head
  assert head==baseline_head_at_five,"divergence before cold restart"
 audit=SQLiteLifeLedger.audit_read_only(path=path,expected_individual_id=identity)
 assert audit.generation==5 and audit.journal_head==head
 try:
  with M11TransactionalMortal.cold_recover(
   db_path=path,individual_id=identity,runtime_factory=lambda:factory(recall=False)): pass
 except RecoveryBlocked: pass
 else: raise AssertionError("wrong UC/model birth contract recovered")
 try:
  with M11TransactionalMortal.cold_recover(
   db_path=path,individual_id=identity,runtime_factory=lambda:factory(recall_cost=2)): pass
 except RecoveryBlocked: pass
 else: raise AssertionError("wrong recall cost recovered")
 for wrong in (
   lambda:factory(water=False,prudence=False),
   lambda:factory(water_uc=3),
   lambda:factory(prudence=False),
   lambda:factory(d2_uc=2),
   lambda:factory(cost=3)):
  try:
   with M11TransactionalMortal.cold_recover(
    db_path=path,individual_id=identity,runtime_factory=wrong): pass
  except RecoveryBlocked: pass
  else: raise AssertionError("mismatched I1 water/D2/forecast contract recovered")
 with M11TransactionalMortal.cold_recover(
  db_path=path,individual_id=identity,runtime_factory=factory) as restored:
  assert restored._runtime.memory.episodes,"cold recovery lost the episode"
  assert restored._runtime._i1_enabled
  assert restored._runtime._i1_water_learning_enabled
  assert restored._runtime._i1_lived_recall_enabled
  assert restored._runtime._d2_prudence
  receipt=restored.run_step()
  assert receipt.generation==6 and receipt.world_step==6
  assert receipt.journal_head==baseline_head_at_six,"cold restart is not byte-identical"
 assert SQLiteLifeLedger.audit_read_only(
  path=path,expected_individual_id=identity).generation==6
print("I1_A236_M11_COLD_WATER_D2_OK")
"""
            proc=subprocess.run(
                [sys.executable,"-c",code],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                capture_output=True,text=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("I1_A236_M11_COLD_WATER_D2_OK",proc.stdout)


if __name__=="__main__":
    unittest.main()
