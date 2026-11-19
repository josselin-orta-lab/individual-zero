"""Native Stage8-E2 WorldSpec and identity preflight (no lives)."""
from copy import deepcopy
import unittest

from i3.lab import stage8e2_native_preflight as N

ROOT = "0123456789abcdef" * 4


class NativePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = N.verify_native_preflight(ROOT)

    def test_physical_f0_world_specs_and_all_g2_opportunities(self):
        p = self.report
        self.assertEqual(p["all_worldspec_count"], 1152)
        self.assertEqual(p["physical_worlds_by_generation"],
                         {"G0": 384, "G1": 384, "G2": 384})
        self.assertEqual(len(p["g2_worldspecs"]), 384)
        self.assertEqual(384, len({(w["population"], w["family"], w["repeat"])
                                  for w in p["g2_worldspecs"]}))
        self.assertEqual(384, len({w["world_sha256"]
                                  for w in p["g2_worldspecs"]}))
        self.assertEqual(p["unique_birth_identifiers"], 64512)
        self.assertEqual(p["native_lives_created"], 0)
        self.assertFalse(p["science_admitted"])

    def test_recomputed_manifest_same_and_tamper_fails(self):
        self.assertEqual(N.verify_native_preflight(ROOT, expected=self.report),
                         self.report)
        altered = deepcopy(self.report)
        altered["g2_worldspecs"][0]["world_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            N.verify_native_preflight(ROOT, expected=altered)

    def test_g2_four_branches_share_physics_not_rng_identity(self):
        key = (0, 2, 0, "stable", 0)
        assert N._world_row(ROOT, *key)["world_sha256"] == (
            N._world_row(ROOT, *key)["world_sha256"])
        ids = [(seed, motor) for identity, seed, motor in N._identities(ROOT)
               if (identity[0], identity[1], identity[3],
                   identity[4], identity[5]) == key]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(seed for seed, _ in ids)), 4)
        self.assertEqual(len(set(motor for _, motor in ids)), 4)


if __name__ == "__main__":
    unittest.main()
