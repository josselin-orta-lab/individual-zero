"""Stage-11 public physical inputs to P-23/P-24: no synthetic S_t injection."""
from unittest import TestCase

from lab.stage11_modulation_probe import run_public_local_modulation
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from i0.modules.global_modulation import GlobalModulation


class LocalThreatAndRecoveryTests(TestCase):
    def test_real_perception_alert_enters_threat_then_local_clear_exits(self):
        a = run_public_local_modulation(
            variant="trapped_local_creature", steps=8,
        )
        b = run_public_local_modulation(
            variant="trapped_local_creature", steps=8,
        )
        self.assertEqual(a, b)
        self.assertTrue(a.local_threat_alert_steps)
        self.assertTrue(a.risk_preempted_st_steps)
        self.assertTrue(a.positively_scanned_local_clear_steps)
        self.assertTrue(any(after == "threat" for _, _, after in
                            a.profile_transitions))
        self.assertTrue(any(before == "threat" and after == "normal"
                            for _, before, after in a.profile_transitions))
        self.assertEqual(a.final_profile, "normal")
        self.assertTrue(all(step < 4 for step in a.local_threat_alert_steps))
        self.assertTrue(all(step >= 4 for step in
                            a.positively_scanned_local_clear_steps))
        self.assertIsNone(a.scientific_verdict)
        self.assertFalse(a.heldout)
        print("stage11_public_local_threat=" + a.to_json())

    def test_same_physics_without_local_alert_does_not_invent_threat(self):
        ref = run_public_local_modulation(
            variant="trapped_no_local_alert", steps=8,
        )
        self.assertEqual(ref.local_threat_alert_steps, ())
        self.assertFalse(any(after == "threat"
                             for _, _, after in ref.profile_transitions))
        self.assertEqual(ref.final_profile, "normal")
        self.assertFalse(ref.heldout)
        print("stage11_public_local_threat_ablation=" + ref.to_json())

    def test_real_body_capture_enters_and_exits_recovery_in_world_steps(self):
        a = run_public_local_modulation(
            variant="externally_restored_energy", steps=9,
        )
        b = run_public_local_modulation(
            variant="externally_restored_energy", steps=9,
        )
        self.assertEqual(a, b)
        self.assertEqual(a.local_threat_alert_steps, ())
        self.assertTrue(any(after == "recovery"
                            for _, _, after in a.profile_transitions))
        self.assertTrue(any(before == "recovery" and after == "normal"
                            for _, before, after in a.profile_transitions))
        self.assertEqual(a.final_profile, "normal")
        self.assertIn((5, 80.0), a.body_energy_by_step)
        self.assertEqual(dict(a.body_energy_by_step).get(4), 20.0)
        self.assertIsNone(a.scientific_verdict)
        print("stage11_public_body_recovery=" + a.to_json())

    def test_unavailable_or_incomplete_scan_never_claims_global_clear(self):
        runtime = build_stage11_reference_runtime(
            enable_local_threats=True,
        )
        capture = runtime.stage3.open_step()
        self.assertEqual(len(capture.adjacent), 4)
        self.assertNotIn(
            "threat_clear",
            runtime._stage11_modulation_signals,
        )
        runtime.stage3._capture = None
        # Without a published S_t, no current body/cell observation may be
        # used as a shortcut to overwrite the profile.
        self.assertIsNone(
            GlobalModulation.indicators_from_st(None).threat_risk
        )

    def test_only_fixed_public_scenarios_and_bounded_steps(self):
        for bad in (-1, 0, 6, 13, True, "8"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                run_public_local_modulation(steps=bad)
        with self.assertRaises(ValueError):
            run_public_local_modulation(variant="sealed_oracle")


if __name__ == "__main__":
    import unittest
    unittest.main()
