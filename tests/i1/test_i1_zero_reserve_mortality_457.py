"""#457: physical zero-reserve lethality in independently born I1 physics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class ZeroReserveMortality457(unittest.TestCase):
    def test_born_physics_and_same_step_transition(self):
        with TemporaryDirectory(prefix="i1-457-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            script = r"""
from dataclasses import replace
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.i1_natural_sleep import enable_natural_sleep_birth
from i1lab.world import BodyState, WorldBody, WorldLayout, Position
from i1.contracts import PrimitiveCommand

reference = build_stage11_reference_runtime(autonomous_mortal=True)
base = reference.world.config
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
stage10 = build_stage10_reference_runtime(autonomous_mortal=True)._stage10_config
config, _ = enable_natural_sleep_birth(world_config=base, stage10_config=stage10)
assert config.zero_reserve_lethal is True
assert config.starvation_integrity_damage_per_step == 0.0
assert config.dehydration_integrity_damage_per_step == 0.0
assert config.digest() != base.digest()
assert not base.zero_reserve_lethal
try:
    replace(config, starvation_integrity_damage_per_step=0.5).validate()
except ValueError:
    pass
else:
    raise AssertionError("combined terminal/injury contract accepted")
position = config.initial_position
assert position not in reference.world._layout.obstacles

def act(*, food, water, primitive="attendre", inventory=None, water_here=False,
        resources=(), integrity=80.0, extra_layout=None):
    layout = WorldLayout(
        water_sources=frozenset({position}) if water_here else frozenset(),
        resources=resources,
    )
    c = replace(config, initial_body=BodyState(
        energy=70.0, food=food, water=water, integrity=integrity))
    w = WorldBody(config=c, layout=layout)
    if inventory:
        w._inventory.update(inventory)
    parameters = {"target": "berry_a"} if primitive == "manger" else {}
    res = w.apply(PrimitiveCommand(primitive=primitive, parameters=parameters),
                  t_monde=1)
    return res

food = act(food=0.1, water=50)
assert food.lethal and food.lethal_reasons == ("zero_food",)
assert food.body_after.integrity == food.body_before.integrity + config.rest_integrity_gain
water = act(food=50, water=0.1)
assert water.lethal and water.lethal_reasons == ("zero_water",)
assert water.body_after.integrity == water.body_before.integrity + config.rest_integrity_gain
both = act(food=0.1, water=0.1, primitive="dormir")
assert both.lethal and both.lethal_reasons == ("zero_food", "zero_water")
assert both.body_after.energy > both.body_before.energy
assert both.body_after.integrity > 0.0
safe = act(food=0.21, water=0.41)
assert not safe.lethal and safe.body_after.food > 0 and safe.body_after.water > 0
saved_food = act(food=0.1, water=50, primitive="manger",
                 inventory={"berry_a":1})
assert not saved_food.lethal and saved_food.body_after.food > 0
missed_food = act(food=0.1, water=50, primitive="manger")
assert missed_food.lethal and "zero_food" in missed_food.lethal_reasons
saved_water = act(food=50, water=0.1, primitive="boire", water_here=True)
assert not saved_water.lethal and saved_water.body_after.water > 0
missed_water = act(food=50, water=0.1, primitive="boire")
assert missed_water.lethal and "zero_water" in missed_water.lethal_reasons
legacy = replace(base, initial_body=BodyState(70.0, 0.1, 0.1, 80.0),
                 food_decay_per_step=0.2, water_decay_per_step=0.4)
original = WorldBody(config=legacy, layout=WorldLayout()).apply(
    PrimitiveCommand(primitive="attendre", parameters={}), t_monde=1)
assert not original.lethal and original.lethal_reasons == ()
print("I1_ZERO_RESERVE_PHYSICS_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=ROOT, capture_output=True, text=True,
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_ZERO_RESERVE_PHYSICS_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
