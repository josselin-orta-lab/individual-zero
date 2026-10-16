"""I1 opt-in regression: no I0 imports and no hidden knowledge injection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_i1_fork import generate


class I1ModelOptinTests(unittest.TestCase):
    def test_independent_i1_activation_and_denial_contracts(self):
        with TemporaryDirectory() as folder:
            output=Path(folder)/"i1build"
            generate(output)
            code = """
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime, I1_POLICY
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel, FIELDS
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.stage12_runtime import Stage12Runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
p=Stage12DetectionPolicy(version="i1-sample-v1",window=12,stagnation_steps=3,
 stagnation_tolerance=.05,loop_repetitions=2,loop_max_period=2,
 entropy_min_samples=3,entropy_warning_fraction=.25,
 bias_min_outcomes_each=2,attribution_bias_threshold=.75)
deltas=tuple((action,tuple((key,1 if key=="x" and action=="MOVE_E" else 0)
 for key in FIELDS)) for action in ("MOVE_E","COLLECT_B"))
model=ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1","a"*64,
 deltas,(("MOVE_E",8),("COLLECT_B",8)))
st11=build_stage11_reference_runtime(autonomous_mortal=True)
st10=build_stage10_reference_runtime(autonomous_mortal=True)
sleep=replace(st10._stage10_config.sleep,fatigue_gain=0.0,
 night_weight=0.0,consolidation_weight=0.0)
cfg=replace(st10._stage10_config,stage9=st11._stage11_config.stage9,sleep=sleep)
with TemporaryDirectory() as folder:
 def born(enabled):
  return ExperimentalI1Stage12Runtime(
   world_config=st11.world.config,layout=st11.world._layout,
   safety_config=st11.stage3.substrate.safety._config,
   safety_facts=st11._canonical_safety._innate,
   protected_integrity_threshold=st11.stage3.control._config.protected_integrity_threshold,
   stage11_config=st11._stage11_config,stage10_config=cfg,
   equipment=st11.equipment,autonomous_mortal=True,
   wal_path=str(Path(folder)/("on" if enabled else "off")),
   birth_life_id="i1:test:" + str(enabled).lower(),
   diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
   detector_policy=p,i1_model_enabled=enabled,
   i1_model=model if enabled else None)
 on=born(True)
 off=born(False)
 assert on.individual_id=="i1:test:true"
 assert on._i1_model_contract[0]==I1_POLICY
 assert "i1_partial_model_forecast" in on._config.compute_budget.operation_costs
 assert "i1_partial_model_forecast" not in off._config.compute_budget.operation_costs
 assert on.stage3.substrate.bench is None
 assert on._i1_pending == {}
 assert off._i1_pending == {}
 assert on.stage8_option_evaluator.__class__.__name__!="I1PartialEvidenceAdapter"
 assert on.run_step().execution_status in ("applied","dead","safety_block")
 assert on.journal.verify()
 assert on._i1_pending == {}
print("I1_ACTIVE_BIRTH_OK")
"""
            run=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(output)+":"+str(
                    Path(__file__).resolve().parents[1]/"src")},
                capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIn("I1_ACTIVE_BIRTH_OK",run.stdout)


if __name__ == "__main__":
    unittest.main()
