"""I1 M11 live committed step, cold recovery and frozen model rejection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_i1_fork import generate


class I1A235M11RecallTests(unittest.TestCase):
    def test_cold_recovery_preserves_recall_birth_contract(self):
        with TemporaryDirectory() as folder:
            output=Path(folder)/"i1build"
            generate(output)
            code="""
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1lab.m11_transactional_mortal import M11TransactionalMortal
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
source=build_stage11_reference_runtime(autonomous_mortal=True)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
config=replace(sleep._stage10_config,stage9=source._stage11_config.stage9,
 sleep=replace(sleep._stage10_config.sleep,fatigue_gain=0.0,
 night_weight=0.0,consolidation_weight=0.0))
delta=tuple((a,tuple((k,1 if k=="x" and a=="MOVE_E" else 0)
 for k in FIELDS)) for a in ("MOVE_E","COLLECT_B"))
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 delta,(("MOVE_E",8),("COLLECT_B",8)))
identity="i1:a235:cold:recall"
physics=replace(source.world.config,version="a235-cold-episode-v1",
 initial_body=replace(source.world.config.initial_body,energy=66.0,
 food=10.0,water=90.0,integrity=100.0))
layout=replace(source.world._layout,
 resources=((physics.initial_position,"berry_b",18),),
 water_sources=frozenset(),danger_zones=frozenset(),
 lethal_zones=frozenset(),creatures=frozenset(),obstacles=frozenset())
def factory(cost=2,recall=True,recall_cost=1):
 return ExperimentalI1Stage12Runtime(
  world_config=physics,layout=layout,
  safety_config=source.stage3.substrate.safety._config,
  safety_facts=source._canonical_safety._innate,
  protected_integrity_threshold=source.stage3.control._config.protected_integrity_threshold,
  stage11_config=source._stage11_config,stage10_config=config,
  equipment=source.equipment,autonomous_mortal=True,
  m11_sqlite_custody=True,wal_path=None,birth_life_id=identity,
  diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
  detector_policy=p,i1_model_enabled=True,i1_model=model,
  i1_forecast_cost_uc=cost,i1_lived_recall_enabled=recall,
  i1_recall_cost_uc=recall_cost)
with TemporaryDirectory() as folder:
 path=str(Path(folder)/"i1.sqlite")
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
  assert owner.runtime.memory.episodes,"no first-person closed episode"
  assert any(e.causal_event.get("kind")=="i1_lived_recall_review" and
   e.causal_event.get("data",{}).get("source_event_refs")
   for e in owner.runtime.journal.entries),"no recalled positive source"
  head=receipt.journal_head
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
 with M11TransactionalMortal.cold_recover(
  db_path=path,individual_id=identity,runtime_factory=factory) as restored:
  assert restored.runtime.memory.episodes,"cold recovery lost the episode"
  receipt=restored.run_step()
  assert receipt.generation==6 and receipt.world_step==6
 assert SQLiteLifeLedger.audit_read_only(
  path=path,expected_individual_id=identity).generation==6
print("I1_A235_M11_COLD_RECALL_OK")
"""
            proc=subprocess.run(
                [sys.executable,"-c",code],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                capture_output=True,text=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("I1_A235_M11_COLD_RECALL_OK",proc.stdout)


if __name__=="__main__":
    unittest.main()
