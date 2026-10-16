"""I1-only M11 source isolation: birth policy, model and identity are fixed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_i1_fork import generate


class I1A235M11RecallContractTests(unittest.TestCase):
    def test_recall_custody_digest_changes_with_activation_and_uc_cost(self):
        with TemporaryDirectory() as folder:
            output=Path(folder)/"isolated"
            generate(output)
            code="""
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1lab.m11_transactional_mortal import _runtime_contract
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel,FIELDS
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
p=Stage12DetectionPolicy(version="i1-m11-test-v1",window=12,stagnation_steps=3,
 stagnation_tolerance=.05,loop_repetitions=2,loop_max_period=2,
 entropy_min_samples=3,entropy_warning_fraction=.25,
 bias_min_outcomes_each=2,attribution_bias_threshold=.75)
st11=build_stage11_reference_runtime(autonomous_mortal=True)
st10=build_stage10_reference_runtime(autonomous_mortal=True)
cfg=replace(st10._stage10_config,stage9=st11._stage11_config.stage9,
 sleep=replace(st10._stage10_config.sleep,fatigue_gain=0.0,
 night_weight=0.0,consolidation_weight=0.0))
delta=tuple((a,tuple((k,1 if k=="x" and a=="MOVE_E" else 0)
 for k in FIELDS)) for a in ("MOVE_E","COLLECT_B"))
def born(cost=2, enabled=True, recall=False, recall_cost=1):
 model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
  delta,(("MOVE_E",8),("COLLECT_B",8))) if enabled else None
 return ExperimentalI1Stage12Runtime(
  world_config=st11.world.config,layout=st11.world._layout,
  safety_config=st11.stage3.substrate.safety._config,
  safety_facts=st11._canonical_safety._innate,
  protected_integrity_threshold=st11.stage3.control._config.protected_integrity_threshold,
  stage11_config=st11._stage11_config,stage10_config=cfg,
  equipment=st11.equipment,autonomous_mortal=True,
  m11_sqlite_custody=True,wal_path=None,birth_life_id="i1:m11:model",
  diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
  detector_policy=p,i1_model_enabled=enabled,
  i1_model=model,i1_forecast_cost_uc=cost,
  i1_lived_recall_enabled=recall,i1_recall_cost_uc=recall_cost)
a,b,c,d=born(recall=True),born(recall=False),born(recall=True,recall_cost=2),born(enabled=False)
assert len({_runtime_contract(a),_runtime_contract(b),_runtime_contract(c),_runtime_contract(d)})==4
assert not a.journal.durable_wal_enabled
assert "i1_partial_model_forecast" in a._config.compute_budget.operation_costs
assert "i1_partial_model_forecast" not in d._config.compute_budget.operation_costs
assert "i1_lived_recall_review" in a._config.compute_budget.operation_costs
assert "i1_lived_recall_review" not in b._config.compute_budget.operation_costs
assert a._config.compute_budget.operation_costs["i1_lived_recall_review"]==1
assert c._config.compute_budget.operation_costs["i1_lived_recall_review"]==2
print("I1_A235_M11_RECALL_CONTRACT_OK")
"""
            proc=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("I1_A235_M11_RECALL_CONTRACT_OK",proc.stdout)


if __name__ == "__main__":
    unittest.main()
