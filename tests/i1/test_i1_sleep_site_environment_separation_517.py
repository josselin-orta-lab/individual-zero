"""#517: rest physiology vs environmental damage, no inferred site reward."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SleepSiteEnvironmentalSeparation517(unittest.TestCase):
    def test_native_world_rest_and_hazard_are_distinct(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                text=True, capture_output=True,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from dataclasses import replace
from i1lab.world import BodyState, Position, WorldBody, WorldLayout
from i1lab.i1_natural_sleep import enable_living_physiology_birth, SLEEP_ENERGY_GAIN
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1.contracts import PrimitiveCommand

base = build_stage11_reference_runtime(autonomous_mortal=True)
cfg = enable_living_physiology_birth(base.world.config)
cfg = replace(cfg,
    initial_body=BodyState(energy=30.,food=50.,water=50.,integrity=90.),
    danger_zone_damage=7.,creature_damage=5.,
    sleep_energy_gain=SLEEP_ENERGY_GAIN)
# Each physical world is isolated, with identical bodily starting state,
# physics, time, and command. Sites are operator fixtures, not personal
# evidence and not knowledge passed to the living individual.
def run(primitive, *, x=5, danger=False, creature=False, t=1):
    site=Position(x,5)
    layout=WorldLayout(
        danger_zones=frozenset({site}) if danger else frozenset(),
        creatures=frozenset({Position(x+1,5)}) if creature else frozenset(),
    )
    world=WorldBody(config=replace(cfg,initial_position=site),layout=layout)
    result=world.apply(PrimitiveCommand(primitive),t_monde=t)
    return result.body_before.as_dict(), result.body_after.as_dict(), result.effects
safe=run("dormir")
safe_other=run("dormir",x=6)
assert safe[0]==safe_other[0] and safe[1]==safe_other[1]
assert safe[1]["energy"] > safe[0]["energy"]
assert safe[1]["food"] < safe[0]["food"]
assert safe[1]["water"] < safe[0]["water"]
danger_sleep=run("dormir",x=6,danger=True)
safe_wait=run("attendre")
danger_wait=run("attendre",x=6,danger=True)
for name in ("energy","food","water"):
    assert safe[1][name] == danger_sleep[1][name]
    assert safe_wait[1][name] == danger_wait[1][name]
assert abs((safe[1]["integrity"]-danger_sleep[1]["integrity"])-7.)<1e-9
assert abs((safe_wait[1]["integrity"]-danger_wait[1]["integrity"])-7.)<1e-9
assert danger_sleep[2]["danger_zone_damage"]==7.
assert danger_wait[2]["danger_zone_damage"]==7.
night=cfg.night_start_step+1
night_safe=run("dormir",t=night)
night_creature=run("dormir",creature=True,t=night)
assert night_creature[2]["creature_damage"]==5.
assert abs((night_safe[1]["integrity"]-night_creature[1]["integrity"])-5.)<1e-9
assert all(night_safe[1][k]==night_creature[1][k]
           for k in ("energy","food","water"))
# Energy saturation is a general prebody constraint, not a site-specific
# benefit. No physical or cognitive owner is mutated across these worlds.
full_cfg=replace(cfg,initial_body=BodyState(
    energy=100.,food=50.,water=50.,integrity=90.))
full_world=WorldBody(config=replace(full_cfg,
    initial_position=Position(5,5)),layout=WorldLayout())
full=full_world.apply(PrimitiveCommand("dormir"),t_monde=1)
assert full.body_after.energy==100.
assert full.body_after.food<50. # Metabolic food decay still occurs.
print("I1_517_SLEEP_PHYSIOLOGY_ENVIRONMENT_SEPARATED_OK")
"""
            completed = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("I1_517_SLEEP_PHYSIOLOGY_ENVIRONMENT_SEPARATED_OK",
                          completed.stdout)


if __name__ == "__main__":
    unittest.main()
