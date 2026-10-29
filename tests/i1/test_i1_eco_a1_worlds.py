"""A1 role reversal must remain exactly symmetric through real M11 birth."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class A1WorldRoleContracts(unittest.TestCase):
    def test_two_counterbalanced_worlds_have_identical_perception_and_m11_birth(self):
        with TemporaryDirectory(prefix="i1-eco-a1-world-contract-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            script = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1_eco_a1_matched_birth import a1_matched_temperament_birth
from i1_eco_a1_worlds import a1_world_parameters

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
detector = Stage12DetectionPolicy(
    version="i1-world-preset-diagnostic-v1",
    window=12, stagnation_steps=3, stagnation_tolerance=0.05,
    loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=0.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
)
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=(
        base.stage3.control._config.protected_integrity_threshold),
    stage11_config=base._stage11_config,
    stage10_config=replace(
        sleep._stage10_config, stage9=base._stage11_config.stage9),
    equipment=base.equipment, detector_policy=detector,
    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
)
native, native_seen = a1_world_parameters(params, role="native")
reverse, reverse_seen = a1_world_parameters(params, role="reversed")
assert native_seen == reverse_seen
assert native["layout"] == reverse["layout"]
assert native["world_config"].digest() != reverse["world_config"].digest()
assert native["world_config"].version == reverse["world_config"].version
assert native["world_config"].berry_effects["berry_a"] == (
    reverse["world_config"].berry_effects["berry_b"])
assert native["world_config"].berry_effects["berry_b"] == (
    reverse["world_config"].berry_effects["berry_a"])
assert native["stage11_config"] == reverse["stage11_config"]
assert native["stage10_config"] == reverse["stage10_config"]

with TemporaryDirectory() as d:
    traits = []
    for role, settings in (("native", native), ("reversed", reverse)):
        identity = "i1:eco:a1:contract:" + role
        path = str(Path(d) / (role + ".sqlite"))
        with a1_matched_temperament_birth(life_id=identity, seed=1):
            actor = birth_i1_m11(db_path=path, life_id=identity, **settings)
        with actor:
            initial = actor._runtime
            traits.append(initial.temperament_parameters.as_dict())
            assert initial.world.capture_local(t_monde=1).as_dict() == native_seen
            # Native physiology must NOT apply a species-specific -10 rewrite
            # only on one of the roles after the swap. Both fruit effects
            # should be bitwise identical to their preregistered configuration.
            assert (initial.world.config.berry_effects
                    == settings["world_config"].berry_effects)
            receipt = actor.run_step()
        audit = SQLiteLifeLedger.audit_read_only(
            path=path, expected_individual_id=identity)
        assert audit.generation == 1
        assert audit.journal_head == receipt.journal_head
        assert audit.status == receipt.status
    assert traits[0] == traits[1]
for bad in ("unknown", None, True):
    try:
        a1_world_parameters(params, role=bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unregistered world role accepted")
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"), str(ROOT / "tools"))))
            result = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT,
                env=env, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
