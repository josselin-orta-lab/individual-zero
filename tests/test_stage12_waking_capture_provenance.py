"""Stage10 wake must preserve the same sensory provenance as Stage3.

No Oracle or laboratory world truth is emitted into the individual's state.
"""
import unittest
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from i0.modules.perception import SymbolicPerception
from lab.stage3_runtime import Stage3Runtime


class Stage12WakingCaptureProvenanceTests(unittest.TestCase):
    def test_same_full_receipt_for_preopened_wake_and_regular_open(self):
        # The one canonical serializer is called by both runtime paths.
        reference = build_stage11_reference_runtime()
        stage3 = reference.stage3
        stage3.control.enable_goal_agency()
        local = reference.world.capture_local(t_monde=1)
        capture = SymbolicPerception().capture(
            local_state=local.as_dict(), telemetry=reference.world.telemetry())
        normal = stage3._perceptual_capture_receipt(capture)
        waking = stage3._perceptual_capture_receipt(capture)
        self.assertEqual(normal, waking)
        self.assertEqual(normal["agency_capture_schema"], "stage12-first-person-cue-v1")
        self.assertEqual(len(normal["agency_visible_adjacent"]), 4)
        self.assertEqual(normal["capture_t_monde"], capture.t_monde)
        self.assertNotIn("oracle_canary", str(normal))
        self.assertNotIn("external_input_applied", str(normal))

    def test_legacy_receipt_unchanged_when_agency_not_enabled(self):
        reference = build_stage11_reference_runtime()
        stage3 = reference.stage3
        local = reference.world.capture_local(t_monde=1)
        capture = SymbolicPerception().capture(
            local_state=local.as_dict(), telemetry=reference.world.telemetry())
        self.assertEqual(stage3._perceptual_capture_receipt(capture), {
            "capture_t_monde": capture.t_monde,
            "position": {"x": capture.x, "y": capture.y},
            "adjacent_creature_count": len(capture.adjacent_creatures),
        })


if __name__ == "__main__":
    unittest.main()
