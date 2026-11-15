"""No-World regression: prospective Stage6 ecology uses reserved high seeds only.

Do not instantiate World or run_life. The WorldSpec data factory runs with
patched ecological validation to avoid any live-world creation during CI.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from i3.lab import p2_ecologies, worldgen

HIGH = 2 << 60


class Stage6ProspectiveEcologyGateTests(unittest.TestCase):
    def test_high_reserve_requires_exact_stage6_flag_and_namespace(self):
        with patch.object(p2_ecologies, "validate_ecology"):
            for family in p2_ecologies.FAMILIES:
                with self.subTest(family=family):
                    with self.assertRaises(ValueError):
                        p2_ecologies._generate_ecology(family, HIGH + 102)
                    with self.assertRaises(PermissionError):
                        p2_ecologies._generate_ecology(
                            family, HIGH-1, prospective_stage6=True)
                    with self.assertRaises(PermissionError):
                        p2_ecologies._generate_ecology(
                            family, 3 << 60, prospective_stage6=True)
                    with self.assertRaises(TypeError):
                        p2_ecologies._generate_ecology(
                            family, HIGH+102, prospective_stage6=1)

    def test_exact_p2_f0_mechanisms_with_explicit_reserved_override(self):
        with patch.object(p2_ecologies, "validate_ecology"), \
             patch.object(p2_ecologies, "generate", wraps=worldgen.generate) as gen:
            for i, family in enumerate(p2_ecologies.FAMILIES):
                with self.subTest(family=family):
                    seed = HIGH + 123 + i
                    first = p2_ecologies._generate_ecology(
                        family, seed, prospective_stage6=True)
                    self.assertEqual(gen.call_args.kwargs,
                                     {"development": False})
                    again = p2_ecologies._generate_ecology(
                        family, seed, prospective_stage6=True)
                    self.assertEqual(
                        p2_ecologies.fingerprint(first),
                        p2_ecologies.fingerprint(again))
                    other = p2_ecologies._generate_ecology(
                        family, seed+100, prospective_stage6=True)
                    self.assertNotEqual(
                        p2_ecologies.fingerprint(first),
                        p2_ecologies.fingerprint(other))

    def test_historical_low_seed_p2_behavior_not_modified(self):
        with patch.object(p2_ecologies, "validate_ecology"), \
             patch.object(p2_ecologies, "generate", wraps=worldgen.generate) as gen:
            a = p2_ecologies._generate_ecology("stable", 2034)
            self.assertEqual(gen.call_args.kwargs, {"development": True})
            b = p2_ecologies._generate_ecology(
                "stable", 2034, prospective_stage6=False)
            self.assertEqual(
                p2_ecologies.fingerprint(a),
                p2_ecologies.fingerprint(b))


if __name__ == "__main__":
    unittest.main()
