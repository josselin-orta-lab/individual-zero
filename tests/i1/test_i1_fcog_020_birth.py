"""I1-only canonical cognitive fatigue weight is effective at real birth."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class I1FCogCanonicalBirth(unittest.TestCase):
    def test_generated_real_birth_and_sleep_assessment(self):
        with TemporaryDirectory(prefix="i1-fcog-birth-") as temp:
            build = Path(temp) / "build"
            generate(build)
            probe = r"""
from dataclasses import replace
from tempfile import TemporaryDirectory
from pathlib import Path
from i1lab.i1_birth import birth_i1
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.i1_natural_sleep import FATIGUE_WEIGHT
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.modules.sleep_pressure import SleepPressureRules

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
stage10 = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-fcog-020-birth-validation", window=12,
    stagnation_steps=3, stagnation_tolerance=.05,
    loop_repetitions=2, loop_max_period=2, entropy_min_samples=3,
    entropy_warning_fraction=.25, bias_min_outcomes_each=2,
    attribution_bias_threshold=.75)
with TemporaryDirectory(prefix="i1-fcog-wal-") as temp:
    life = birth_i1(
        life_id="i1:fcog:020:birth", wal_path=str(Path(temp)/"life.wal"),
        world_config=base.world.config, layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
        stage11_config=base._stage11_config, stage10_config=stage10,
        equipment=base.equipment, detector_policy=detector)
    effective = life._stage10_config.sleep
    assert FATIGUE_WEIGHT == effective.fatigue_weight == .2
    assert effective.fatigue_gain == .7
    assert effective.sleep_fatigue_recovery == .3
    assert effective.consolidation_weight == .25
    assert effective.night_weight == .20
    rules = SleepPressureRules(effective)
    for f in (0.0, 0.25, 0.8, 1.0):
        assessed = rules.assess_step(
            f_cog=f, unconsolidated_episodes=0,
            memory_occupancy=0.0, is_night=False, awake=True)
        assert abs(assessed.sleep_pressure - .2*f) < 1e-12
    assert rules.waking_cycle_fatigue(
        f_cog=0., consumed_uc=5, c_max=1, b_cycle_uc=10) == .35
    assert rules.sleep_step_fatigue(f_cog=.8) == .5
    receipt = life.run_step()
    assert receipt.execution_status in ("applied", "dead", "safety_block")
    assert life.journal.verify()
"""
            done = subprocess.run(
                [sys.executable, "-c", probe],
                cwd=ROOT, env=__import__("os").environ.copy() |
                {"PYTHONPATH": str(build) + __import__("os").pathsep + str(ROOT / "src")},
                capture_output=True, text=True, timeout=180)
            self.assertEqual(done.returncode, 0, done.stdout + "\n" + done.stderr)


if __name__ == "__main__":
    unittest.main()
