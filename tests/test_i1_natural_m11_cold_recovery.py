"""Current I1 M11: canonical birth, authenticated cold recovery, physical parity.

Functional validation of the current natural runtime only. No archived
experimental cohort is used as a scientific baseline.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalI1M11Tests(unittest.TestCase):
    def test_current_birth_cold_roundtrip_and_changed_contract_rejection(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "i1build"
            generate(output)
            script = """
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
stage10 = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-natural-m11-v1", window=12, stagnation_steps=3,
    stagnation_tolerance=.05, loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75)
life_id = "i1:natural:m11:smoke"
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
    stage11_config=base._stage11_config, stage10_config=stage10,
    equipment=base.equipment, detector_policy=detector,
    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
def factory(policy=detector):
    return I1Runtime(
        birth_life_id=life_id, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None,
        **{**params, "detector_policy": policy})
with TemporaryDirectory() as temp:
    continuous = str(Path(temp) / "continuous.sqlite")
    cold = str(Path(temp) / "cold.sqlite")
    with birth_i1_m11(db_path=continuous, life_id=life_id, **params) as life:
        before = life.run_step()
        after = life.run_step()
        assert before.status == after.status == "active"
    with birth_i1_m11(db_path=cold, life_id=life_id, **params) as life:
        first = life.run_step()
        assert first.journal_head == before.journal_head
        assert first.generation == 1 and first.world_step == 1
        assert not life._runtime.journal.durable_wal_enabled
    audit = SQLiteLifeLedger.audit_read_only(
        path=cold, expected_individual_id=life_id)
    assert audit.generation == 1 and audit.journal_head == before.journal_head
    try:
        with recover_i1_m11(
            db_path=cold, life_id=life_id,
            runtime_factory=lambda: factory(replace(detector, window=13))):
            pass
    except RecoveryBlocked:
        pass
    else:
        raise AssertionError("changed detector birth contract accepted")
    with recover_i1_m11(
        db_path=cold, life_id=life_id, runtime_factory=factory) as resumed:
        second = resumed.run_step()
        assert second.generation == 2 and second.world_step == 2
        assert second.status == "active"
        assert second.journal_head == after.journal_head
    assert SQLiteLifeLedger.audit_read_only(
        path=cold, expected_individual_id=life_id).generation == 2
print("I1_NATURAL_M11_ROUNDTRIP_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(output) + ":" + str(ROOT / "src")},
                capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_NATURAL_M11_ROUNDTRIP_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
