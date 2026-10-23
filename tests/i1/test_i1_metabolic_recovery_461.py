"""#461: newborn v4 metabolism, substrate-constrained repair and recovery."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class MetabolicCoupling461(unittest.TestCase):
    def test_born_energy_and_repair_cannot_be_created_without_substrate(self):
        with TemporaryDirectory(prefix="i1-461-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            source = r"""
from dataclasses import replace
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.i1_natural_sleep import enable_natural_sleep_birth
from i1lab.world import BodyState, WorldBody, WorldLayout
from i1.contracts import PrimitiveCommand

base = build_stage11_reference_runtime(autonomous_mortal=True).world.config
sleep = build_stage10_reference_runtime(autonomous_mortal=True)._stage10_config
born, _ = enable_natural_sleep_birth(world_config=base, stage10_config=sleep)
assert born.metabolic_recovery_cost_per_energy > 0
assert born.metabolic_repair_cost_per_integrity > 0
assert born.metabolic_minimum_water > 0
assert "v4-metabolic-coupling" in born.version
assert born.digest() != base.digest()
assert born.zero_reserve_lethal
for name, config in [
    ("legacy", base),
    ("bad_metabolic", replace(born, metabolic_repair_cost_per_integrity=0)),
    ("bad_water", replace(born, metabolic_minimum_water=-1)),
]:
    if name != "legacy":
        try:
            config.validate()
        except ValueError:
            pass
        else:
            raise AssertionError(name)
for water in (0.1, 50):
    config = replace(born, initial_body=BodyState(
        energy=25, food=0.2, water=water, integrity=40))
    w = WorldBody(config=config, layout=WorldLayout())
    actual = w.apply(PrimitiveCommand("dormir", {}), t_monde=1)
    assert actual.body_after.energy == 25
    assert actual.body_after.integrity == 40
    assert actual.lethal_reasons == (
        ("zero_food", "zero_water") if water == 0.1 else ("zero_food",)
    )
# Positive substrate + water pays for recovery and repair; no free energy.
config = replace(born, initial_body=BodyState(
    energy=25, food=50, water=50, integrity=40))
w = WorldBody(config=config, layout=WorldLayout())
s = w.apply(PrimitiveCommand("dormir", {}), t_monde=1)
assert s.body_after.energy > 25
assert s.body_after.integrity > 40
assert s.body_after.food < 50 - config.food_decay_per_step
assert s.body_after.water == 50 - config.water_decay_per_step
assert not s.lethal
# Drinking restores water without adding food/energy.
config = replace(born, initial_body=BodyState(
    energy=25, food=50, water=0.1, integrity=40))
layout = WorldLayout(water_sources=frozenset({config.initial_position}))
w = WorldBody(config=config, layout=layout)
v = w.apply(PrimitiveCommand("boire", {}), t_monde=1)
assert v.body_after.energy <= 25
assert v.body_after.food <= 50
assert v.body_after.water > 0.1
assert not v.lethal
# Frozen reference semantics remain deliberately unchanged.
reference = replace(base, initial_body=BodyState(
    energy=25, food=0.1, water=0.1, integrity=40), sleep_energy_gain=3.0)
legacy = WorldBody(config=reference, layout=WorldLayout()).apply(
    PrimitiveCommand("dormir", {}), t_monde=1)
assert legacy.body_after.energy == 28
assert not legacy.lethal
print("I1_461_METABOLIC_CONSERVATION_OK")
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", source],
                cwd=ROOT, capture_output=True, text=True,
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_461_METABOLIC_CONSERVATION_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
