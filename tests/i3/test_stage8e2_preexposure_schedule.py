"""Pure Stage8-E2 allocation checks: these never execute World or birth."""
import unittest

from i3.lab.stage8e2_preexposure_schedule import (
    EXPECTED_TOTAL, check_three_roots, derive, schedule,
)

A, B, C = ("11" * 32, "22" * 32, "33" * 32)


class Stage8E2PreexposureScheduleTests(unittest.TestCase):
    def test_complete_g2_world_opportunities_and_counts(self):
        result = schedule(A)
        self.assertEqual(384, result["worlds_reserved_count"])
        self.assertEqual(EXPECTED_TOTAL, result["total_planned_lives"])
        self.assertEqual(
            {"G0": 9216, "G1": 18432, "G2": 36864},
            result["planned_lives"])
        self.assertEqual(64, len({
            x["population"] for x in result["g2_world_opportunities"]}))
        self.assertEqual(
            384, len({x["world_token"] for x in result["g2_world_opportunities"]}))
        self.assertFalse(result["scientific_claim_authorized"])
        self.assertEqual(result["new_lives"], 0)
        self.assertEqual(result["worlds_instantiated"], 0)

    def test_determinism_and_entropy_domain_isolation(self):
        self.assertEqual(schedule(A), schedule(A))
        self.assertNotEqual(schedule(A), schedule(B))
        self.assertNotEqual(
            derive(A, "world-g2", 0, "stable", 0),
            derive(A, "motor", 0, "stable", 0))
        self.assertNotEqual(
            derive(A, "motor", 0, "S_sham", 0),
            derive(A, "motor", 0, "M_sham", 0))

    def test_three_disjoint_run_roots(self):
        self.assertTrue(check_three_roots(A, B, C))
        with self.assertRaises(ValueError):
            check_three_roots(A, B, A)

    def test_reject_invalid_roots_domains_and_coordinates(self):
        for root in ("", "ff", "00" * 32, "GG" * 32, "AA" * 32):
            with self.subTest(root=root):
                with self.assertRaises(ValueError):
                    schedule(root)
        with self.assertRaises(ValueError):
            derive(A, "unregistered-domain", 0)
        with self.assertRaises(ValueError):
            derive(A, "world-g2", -1)
        with self.assertRaises(ValueError):
            derive(A, "world-g2", "path/escape")


if __name__ == "__main__":
    unittest.main()
