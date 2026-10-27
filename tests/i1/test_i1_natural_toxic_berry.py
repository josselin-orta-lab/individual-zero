"""Natural I1 toxic berry remains unknown but physical harm is bounded."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class ToxicBerryBirthTests(unittest.TestCase):
    def test_natural_born_physics_and_reference_isolation(self):
        with TemporaryDirectory() as temp:
            built=Path(temp)/"generated"
            generate(built)
            script=r"""
from dataclasses import replace
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.i1_natural_sleep import enable_natural_sleep_birth
from i1lab.world import BerryEffect
base=build_stage11_reference_runtime(autonomous_mortal=True)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
original=base.world.config
assert original.berry_effects["berry_b"].integrity_delta == -100.0
stage10=replace(sleep._stage10_config,stage9=base._stage11_config.stage9)
natural,_=enable_natural_sleep_birth(world_config=original,stage10_config=stage10)
assert natural.berry_effects["berry_b"] == BerryEffect(5.0,-10.0)
assert natural.berry_effects["berry_a"] == original.berry_effects["berry_a"]
assert original.berry_effects["berry_b"].integrity_delta == -100.0
assert "i1-natural-toxic-berry-integrity-minus-10-v1" in natural.version
print("NATURAL_TOXIC_BERRY_OK")
"""
            proc=subprocess.run([sys.executable,"-c",script],
                env={"PYTHONPATH":str(built)+":"+str(ROOT/"src")},
                text=True,capture_output=True,check=False)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn("NATURAL_TOXIC_BERRY_OK",proc.stdout)

if __name__=="__main__":
    unittest.main()
