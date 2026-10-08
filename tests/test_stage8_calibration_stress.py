"""Physical κ calibration stress: DC-06, INV-05/26/43."""
import unittest

from lab.stage8_calibration_stress import controlled_physical_calibration


class PhysicalCalibrationStressTests(unittest.TestCase):
    def test_predeclared_real_world_comparisons_improve_brier(self):
        report = controlled_physical_calibration()
        self.assertEqual(len(report.samples), 80)
        self.assertEqual(report.credited_observations, 80)
        self.assertEqual(report.confirmations, 64)
        self.assertEqual(report.contradictions, 16)
        self.assertLess(report.late_brier, report.early_brier)
        self.assertLess(report.late_brier, report.baseline_brier)
        self.assertEqual(report, controlled_physical_calibration())

    def test_all_observations_are_physically_distinct(self):
        report = controlled_physical_calibration()
        refs = [sample.observation_ref for sample in report.samples]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertEqual(
            [sample.observed_step for sample in report.samples],
            list(range(2, 82)),
        )
        self.assertEqual(report.samples[0].confidence_before_verification, 0.5)


if __name__ == "__main__":
    unittest.main()
