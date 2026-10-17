"""Stage-8 normative acceptance measurements, Lab-only and reproducible."""
import unittest

from lab.stage8_learning_benchmark import (
    world_learning_curve, brier_score, CalibrationSample,
    Stage8PhysicalCalibrationRecorder,
)
from lab.stage8_reference_fixture import build_stage8_reference_runtime


class Stage8LearningBenchmarkTests(unittest.TestCase):
    def test_lived_world_td_curve_improves_from_birth(self):
        curve = world_learning_curve(pairs=80, interval=20)
        self.assertEqual(curve.sample_count, 160)
        self.assertGreater(curve.points[0].rmse_against_observed_return, 0.0)
        self.assertLess(
            curve.points[-1].rmse_against_observed_return,
            curve.points[0].rmse_against_observed_return,
        )
        self.assertEqual(curve, world_learning_curve(pairs=80, interval=20))

    def test_brier_score_uses_preverification_predictions_not_posteriors(self):
        points = (
            CalibrationSample("a", 1, 0.5, True),
            CalibrationSample("b", 2, 0.75, True),
        )
        self.assertEqual(brier_score(points), (0.25 + 0.0625) / 2)
        self.assertIsNone(brier_score(()))

    def test_physical_calibration_recorder_never_writes_individual(self):
        runtime = build_stage8_reference_runtime()
        recorder = Stage8PhysicalCalibrationRecorder()
        before = runtime.kappa_active.export_causal_state()
        recorder.after_step(runtime, recorder.before_step(runtime))
        self.assertEqual(before, runtime.kappa_active.export_causal_state())
        self.assertEqual(recorder.curve().samples, ())


if __name__ == "__main__":
    unittest.main()
