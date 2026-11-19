"""Separate Stage8-E2 parental audit tested on synthetic v4 ancestry."""
from copy import deepcopy
import unittest

from i3.lab import stage8e2_independent_parentage_audit as A
from i3.lab import stage8e2_lineage_preflight as L
from i3.modules import genome as G

ROOT = "0123456789abcdef" * 4


class Stage8E2IndependentParentageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = {
            (p, "shared", s): G.generation_zero(800_000 + p*24 + s)
            for p in range(64) for s in range(24)
        }
        cls.scores = {
            (p, "shared", s): (s % 7, 1400 + s)
            for p in range(64) for s in range(24)
        }
        cls.child, cls.draws = L.make_descendants(
            ROOT, 1, cls.parents, cls.scores, "a"*64)

    def verify(self, **overrides):
        arguments = dict(
            root=ROOT, generation=1, parents=self.parents,
            parent_scores=self.scores, descendants=self.child,
            claims=self.draws, parent_manifest_sha256="a"*64,
        )
        arguments.update(overrides)
        return A.verify_parentage(**arguments)

    def test_complete_3072_v4_offspring_and_multiplicity(self):
        r = self.verify()
        self.assertEqual(r["mutations_reconstructed"], 3072)
        self.assertTrue(r["matched_occupancy"])
        self.assertEqual(r["population_units"], 64)
        self.assertFalse(r["scientific_claim_authorized"])
        self.assertFalse(r["original_gzip_audited_here"])

    def test_swapped_parent_selected_slot_rejected(self):
        claims = deepcopy(self.draws)
        claims[0]["parent_slot"] = (claims[0]["parent_slot"] + 1) % 24
        with self.assertRaises(ValueError):
            self.verify(claims=claims)

    def test_cross_arm_control_deviation_rejected(self):
        claims = deepcopy(self.draws)
        m = next(x for x in claims if x["arm"] == "M" and x["population"] == 0)
        m["parent_slot"] = (m["parent_slot"] + 1) % 24
        with self.assertRaises(ValueError):
            self.verify(claims=claims)

    def test_missing_or_reused_offspring_rejected(self):
        with self.assertRaises(ValueError):
            self.verify(claims=self.draws[:-1])
        descendants = dict(self.child)
        descendants[(0, "S", 0)] = self.child[(0, "M", 0)]
        with self.assertRaises(ValueError):
            self.verify(descendants=descendants)

    def test_score_forgery_and_seal_mismatch_rejected(self):
        scores = dict(self.scores)
        scores[(0, "shared", 0)] = (7, 1400)
        with self.assertRaises(ValueError):
            self.verify(parent_scores=scores)
        with self.assertRaises(ValueError):
            self.verify(parent_manifest_sha256="b"*64)


if __name__ == "__main__":
    unittest.main()
