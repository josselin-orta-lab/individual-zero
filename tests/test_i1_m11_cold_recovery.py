"""I1 M11 live committed step, cold recovery and frozen model rejection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_i1_fork import generate


class I1M11RecoveryTests(unittest.TestCase):
    def test_current_generation_and_wrong_model_cost(self):
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
identity="i1:m11:isolated"
def factory(cost=2):
 return ExperimentalI1Stage12Runtime(
  world_config=source.world.config,layout=source.world._layout,
  safety_config=source.stage3.substrate.safety._config,
  safety_facts=source._canonical_safety._innate,
  protected_integrity_threshold=source.stage3.control._config.protected_integrity_threshold,
  stage11_config=source._stage11_config,stage10_config=config,
  equipment=source.equipment,autonomous_mortal=True,
  m11_sqlite_custody=True,wal_path=None,birth_life_id=identity,
  diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
  detector_policy=p,i1_model_enabled=True,i1_model=model,
  i1_forecast_cost_uc=cost)
with TemporaryDirectory() as folder:
 path=str(Path(folder)/"i1.sqlite")
 with M11TransactionalMortal.birth(db_path=path,runtime=factory(),
                                    individual_id=identity) as owner:
  receipt=owner.run_step()
  assert receipt.generation==1 and receipt.world_step==1
  assert receipt.status=="active"
  head=receipt.journal_head
 audit=SQLiteLifeLedger.audit_read_only(path=path,expected_individual_id=identity)
 assert audit.generation==1 and audit.journal_head==head
 try:
  with M11TransactionalMortal.cold_recover(
   db_path=path,individual_id=identity,runtime_factory=lambda:factory(3)): pass
 except RecoveryBlocked: pass
 else: raise AssertionError("wrong UC/model birth contract recovered")
 with M11TransactionalMortal.cold_recover(
  db_path=path,individual_id=identity,runtime_factory=factory) as restored:
  receipt=restored.run_step()
  assert receipt.generation==2 and receipt.world_step==2
 assert SQLiteLifeLedger.audit_read_only(
  path=path,expected_individual_id=identity).generation==2
print("I1_M11_COLD_RECOVERY_OK")
"""
            proc=subprocess.run(
                [sys.executable,"-c",code],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                capture_output=True,text=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("I1_M11_COLD_RECOVERY_OK",proc.stdout)


if __name__=="__main__":
    unittest.main()
