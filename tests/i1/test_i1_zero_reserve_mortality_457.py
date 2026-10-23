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
assert food.body_after.integrity == food.body_before.integrity
water = act(food=50, water=0.1)
assert water.lethal and water.lethal_reasons == ("zero_water",)
assert water.body_after.integrity == water.body_before.integrity + config.rest_integrity_gain
both = act(food=0.1, water=0.1, primitive="dormir")
assert both.lethal and both.lethal_reasons == ("zero_food", "zero_water")
assert both.body_after.energy == both.body_before.energy
assert both.body_after.integrity == both.body_before.integrity
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


    def test_m11_terminal_death_and_no_cold_revival(self):
        with TemporaryDirectory(prefix="i1-457-m11-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            script = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from i1lab.world import BodyState, WorldLayout
from i1.modules.stage12_detectors import Stage12DetectionPolicy

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
stage10 = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-457-m11-death-v1", window=12,
    stagnation_steps=3, stagnation_tolerance=.05,
    loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75,
)
for channel in ("food", "water"):
    body = BodyState(energy=70.0, food=0.0 if channel == "food" else 40.0,
                     water=0.0 if channel == "water" else 40.0,
                     integrity=85.0)
    params = dict(
        world_config=replace(base.world.config, initial_body=body),
        layout=WorldLayout(),
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
        stage11_config=base._stage11_config, stage10_config=stage10,
        equipment=base.equipment, detector_policy=detector,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
    )
    life_id = "i1:457:mortal:" + channel
    with TemporaryDirectory() as folder:
        db = str(Path(folder) / "terminal.sqlite")
        with birth_i1_m11(db_path=db, life_id=life_id, **params) as individual:
            assert individual._runtime.world.config.zero_reserve_lethal
            last = individual.run_step()
            assert last.status == "dead", last
            assert individual._runtime.world.body.integrity > 0.0
            try:
                individual.run_step()
            except RecoveryBlocked:
                pass
            else:
                raise AssertionError("terminal individual advanced")
        ledger = SQLiteLifeLedger.audit_read_only(
            path=db, expected_individual_id=life_id)
        assert ledger.status == "dead" and not ledger.may_recover
        try:
            with recover_i1_m11(
                db_path=db, life_id=life_id,
                runtime_factory=lambda: I1Runtime(
                    birth_life_id=life_id, autonomous_mortal=True,
                    m11_sqlite_custody=True, wal_path=None, **params)):
                pass
        except RecoveryBlocked:
            pass
        else:
            raise AssertionError("terminal M11 identity was resurrected")
print("I1_ZERO_RESERVE_M11_FINALITY_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=ROOT, capture_output=True, text=True,
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_ZERO_RESERVE_M11_FINALITY_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
