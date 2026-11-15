"""Stage6 reserved seed adapter parity with untouched historical P2 F0.

Constructs only WorldSpec data under mocked ecological World validation.
No actual World, Mind or native life is opened by these software tests.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from i3.lab import p2_ecologies as P2
from i3.lab import stage6_light_prospective_ecologies as E
from i3.lab import worldgen

HIGH = 2 << 60


class Stage6ProspectiveEcologyTests(unittest.TestCase):
    def test_original_p2_rejects_all_high_seed_worlds(self):
        with patch.object(P2, "validate_ecology"):
            for family in P2.FAMILIES:
                with self.subTest(family=family):
                    with self.assertRaises(ValueError):
                        P2._generate_ecology(family, HIGH + 102)
                    with self.assertRaises(PermissionError):
                        E.world_for_stage6(family, HIGH - 1)
                    with self.assertRaises(PermissionError):
                        E.world_for_stage6(family, 3 << 60)
                    with self.assertRaises(PermissionError):
                        E.world_for_stage6(family, True)
                    with self.assertRaises(ValueError):
                        E.world_for_stage6("foreign", HIGH + 1)

    def test_prospective_seed_materialization_explicit_reserved_override(self):
        with patch.object(P2, "validate_ecology"), \
             patch.object(E, "generate_world", wraps=worldgen.generate) as gen:
            for i, family in enumerate(P2.FAMILIES):
                with self.subTest(family=family):
                    seed = HIGH + 123 + i
                    first = E.world_for_stage6(family, seed)
                    self.assertEqual(gen.call_args.kwargs,
                                     {"development": False})
                    second = E.world_for_stage6(family, seed)
                    self.assertEqual(P2.fingerprint(first),
                                     P2.fingerprint(second))
                    third = E.world_for_stage6(family, seed+100)
                    self.assertNotEqual(P2.fingerprint(first),
                                        P2.fingerprint(third))

    def test_stage6_adapter_matches_exact_historical_f0_for_low_seed_fixtures(self):
        # Low-seed parity check through a PRIVATE pure adapter helper only.
        # Public world_for_stage6() itself MUST reject every low seed.
        with patch.object(P2, "validate_ecology"):
            for i, family in enumerate(P2.FAMILIES):
                with self.subTest(family=family):
                    seed = 2034 + i
                    historical = P2._generate_ecology(family, seed)
                    adapter = E._build_family(family, seed)
                    self.assertEqual(
                        P2.fingerprint(historical),
                        P2.fingerprint(adapter))
                    with self.assertRaises(PermissionError):
                        E.world_for_stage6(family, seed)


if __name__ == "__main__":
    unittest.main()
