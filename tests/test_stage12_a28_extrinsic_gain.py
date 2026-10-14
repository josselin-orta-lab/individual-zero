"""A2.8: prebirth prospective-value sensitivity only; no policy bypass."""
from pathlib import Path
from dataclasses import replace
from tempfile import TemporaryDirectory
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_first_planning_state import build_life

class ProspectiveGainContractTests(unittest.TestCase):
    @staticmethod
    def birth(gain):
        with TemporaryDirectory() as root:
            life, config, layout, equipment = build_life(
                "near_food_free", 70.0, "horizon_three",
                birth_life_id="i0:110:a28:config:"+str(gain),
                wal_path=str(Path(root)/"life.wal"),
                calibration_food_profile="sustained",
                progressive_planning=True,
                progressive_evaluation_prefix=True,
                progressive_revalidate_on_new_capture=True,
                extrinsic_gain_override=gain,
            )
            return (life._stage11_config.stage9.stage8.evaluation.extrinsic_gain,
                    life._stage11_config.intrinsic_weight,
                    life._stage11_config.stage9.stage8.stage7.stage6.evaluation.h_eff)
    def test_only_extrinsic_gain_changes(self):
        self.assertEqual(self.birth(None),self.birth(1.0))
        for v in (1.0,1.6,2.0):
            actual=self.birth(v)
            self.assertEqual(actual[0],v)
            self.assertEqual(actual[1:],(0.75,3))
    def test_unregistered_gain_rejected_before_birth(self):
        with TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError,"preregistered extrinsic"):
                build_life("near_food_free",70.0,"horizon_three",
                           birth_life_id="i0:110:a28:invalid",
                           wal_path=str(Path(root)/"invalid.wal"),
                           extrinsic_gain_override=100.0)
if __name__=="__main__":unittest.main()
