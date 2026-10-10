"""Stage-11 public developmental hydration funnel, NEVER held-out acceptance."""
import unittest
import json

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_hydration_probe import run_public_hydration_funnel


class Stage11HydrationProbeTests(unittest.TestCase):
    def test_public_run_is_reproducible_and_does_not_forge_science(self):
        first = run_public_hydration_funnel(seed=41, world="small_water_gain", steps=18)
        second = run_public_hydration_funnel(seed=41, world="small_water_gain", steps=18)
        self.assertEqual(first, second)
        self.assertEqual(first.classification, "development_only_not_heldout")
        self.assertIsNone(first.scientific_verdict)
        self.assertFalse(first.golden_stage9_frozen)
        self.assertEqual(first.schedule_sha256, second.schedule_sha256)
        self.assertGreaterEqual(first.stage11_test_proposals, 0)
        self.assertGreaterEqual(first.stage11_unscored_evaluations, 0)
        self.assertGreaterEqual(first.stage11_scored_intrinsic_evaluations, 0)
        self.assertLessEqual(first.stage11_scored_distinct_options,
                             first.stage11_scored_intrinsic_evaluations)
        self.assertLessEqual(first.stage11_verified_interventions,
                             first.stage11_executed_test_commands)
        data = first.as_dict()
        digest = data.pop("evidence_sha256")
        self.assertEqual(digest, sha256_hex(canonical_causal_bytes(data)))
        # Preserve the diagnostic readout in the small software CI log.
        # This is NOT an independent protocol registration or scientific GO.
        print("stage11_public_hydration_diagnostic=" + json.dumps(
            first.as_dict(), sort_keys=True, separators=(",", ":")
        ))

    def test_rejects_nonpublic_variants_and_invalid_seeds(self):
        for args in (
            {"seed": -1}, {"seed": True}, {"steps": 0},
            {"world": "sealed_hidden"}, {"world": "null_water_reference"},
        ):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    run_public_hydration_funnel(**args)


if __name__ == "__main__":
    unittest.main()
