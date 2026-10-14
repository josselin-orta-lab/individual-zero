"""A2.11b: deterministic prebirth physical coverage, strict unseen-input refusal."""
from dataclasses import replace
from tempfile import TemporaryDirectory
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_first_planning_state import build_life, build_prebirth_equipment
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from i0.interfaces import PrimitiveCommand
from i0.modules.simulator import state_from_capture
from i0.modules.perception import SymbolicPerception


class PhysicalCorpusTests(unittest.TestCase):
    def test_prebirth_more_physical_observations_without_inventing_unknowns(self):
        with TemporaryDirectory() as root:
            original,cfg,layout,base=build_life(
                "near_food_free",70.0,"horizon_three",
                wal_path=str(Path(root)/"off.wal"),
                birth_life_id="i0:a211b:off",
                calibration_food_profile="sustained",
                progressive_planning=True,progressive_evaluation_prefix=True,
                progressive_revalidate_on_new_capture=True,
                extrinsic_gain_override=1.6)
            extended,_,_,augmented=build_life(
                "near_food_free",70.0,"horizon_three",
                wal_path=str(Path(root)/"on.wal"),
                birth_life_id="i0:a211b:on",
                calibration_food_profile="sustained",
                progressive_planning=True,progressive_evaluation_prefix=True,
                progressive_revalidate_on_new_capture=True,
                extrinsic_gain_override=1.6,
                extended_prebirth_equipment=True)
            self.assertEqual(len(base._records),4)
            self.assertGreaterEqual(len(augmented._records),8)
            self.assertNotEqual(base.artifact_digest,augmented.artifact_digest)
            self.assertTrue(set(base._records).issubset(augmented._records))
            perception=SymbolicPerception().capture(
                local_state=original.world.capture_local(t_monde=1).as_dict(),
                telemetry=original.world.telemetry())
            state=state_from_capture(capture=perception,
                is_night=original.world.is_night(1))
            with self.assertRaises(LookupError):
                augmented.predict(state=state,
                    command=PrimitiveCommand("fabriquer_outil"))
            for digest in base._records:
                self.assertEqual(base._records[digest],augmented._records[digest])

    def test_flag_strict(self):
        with TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError,"must be boolean"):
                build_life("near_food_free",70.0,"horizon_three",
                    wal_path=str(Path(root)/"bad.wal"),
                    extended_prebirth_equipment=1)

if __name__=="__main__":
    unittest.main()
