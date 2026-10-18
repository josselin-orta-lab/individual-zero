"""Canonical I1 goal calibration: verify the actual born owners, not fixtures."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalGoalCalibrationTests(unittest.TestCase):
    def test_real_newborn_stage_configs_and_decision_contract(self):
        with TemporaryDirectory() as folder:
            build = Path(folder) / "generated"
            generate(build)
            script = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1
from i1lab.i1_natural_runtime import I1Runtime, _I1_GOAL_POLICIES
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.contracts import GoalProposal

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
sleep_config = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-vital-goal-birth-smoke-v1", window=12,
    stagnation_steps=3, stagnation_tolerance=.05, loop_repetitions=2,
    loop_max_period=2, entropy_min_samples=3,
    entropy_warning_fraction=.25, bias_min_outcomes_each=2,
    attribution_bias_threshold=.75,
)
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
    stage11_config=base._stage11_config, stage10_config=sleep_config,
    equipment=base.equipment, detector_policy=detector,
)
def substage(config):
    return config.stage9.stage8.stage7.stage6.stage4

def proposal(kind, pressure, step):
    name = {"recover_energy":"energy", "drink":"water"}[kind]
    return GoalProposal(
        id=f"g:{kind}:{step}", source="value_needs", goal_type=kind,
        target=name, base_pressure=pressure, current_pressure=pressure,
        justification_ref=f"need:{name}:{step}", t_monde=step,
        cycle=1, rule_version="test",
    )

with TemporaryDirectory() as tmp:
    default = birth_i1(
        life_id="i1:goal:normal", wal_path=str(Path(tmp)/"normal.wal"), **params)
    assert type(default) is I1Runtime
    actual = default.goal_manager._config
    assert actual.replacement_hysteresis == .04
    assert actual.critical_pressure == .35
    assert substage(default._stage11_config).goals == actual
    assert substage(default._stage10_config).goals == actual
    # Stage11 budget projection may version its runtime substrate separately.
    assert default._config.goals == actual
    assert substage(base._stage11_config).goals.replacement_hysteresis == .10
    assert substage(base._stage11_config).goals.critical_pressure == .90
    assert _I1_GOAL_POLICIES["historical-010"] == (.10,.90)
    initial_version = actual.version
    for t in range(1,5):
        default.run_step()
        assert default.goal_manager._config is actual
        assert default.goal_manager._config.version == initial_version

    # Real newborn GoalManager retains standard refractory/anti-chatter code.
    from i1.modules.goal_manager import GoalManager
    for policy, expected in (("natural-004","drink"),("historical-010","recover_energy")):
        real = I1Runtime(
            birth_life_id="i1:goal:test:" + policy,
            autonomous_mortal=True,
            wal_path=str(Path(tmp)/(policy+".wal")),
            i1_goal_policy=policy, **params)
        manager = real.goal_manager
        first = manager.arbitrate([proposal("recover_energy",.358268,1)],
                                  t_monde=1,cycle=1)
        assert first.goal_type == "recover_energy"
        second = manager.arbitrate([
            proposal("recover_energy",.358268,2),
            proposal("drink",.429922,2),
        ],t_monde=2,cycle=1)
        assert second.goal_type == expected
        if policy == "natural-004":
            for t in range(3,8):
                manager.arbitrate([
                    proposal("drink",.429922,t),
                    proposal("recover_energy",.44,t),
                ],t_monde=t,cycle=1)
                assert manager.active_goal.goal_type == "drink"
            # Two repeated failures enter refractory; critical .35 can bypass.
            manager.note_non_plannable(material_context_hash="stable",t_monde=8)
            assert manager.note_non_plannable(material_context_hash="stable",t_monde=8)
            assert manager.active_goal is None
            assert manager.arbitrate([proposal("drink",.43,9)],t_monde=9,cycle=1)
    assert default.competition is not default.goal_manager
print("CALIBRATION_BIRTH_CONTRACT_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(build) + ":" + str(ROOT / "src")},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("CALIBRATION_BIRTH_CONTRACT_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
