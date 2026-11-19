"""Six-life parental fitness gate, synthetic structural tests only."""
from copy import deepcopy
import unittest

from i3.lab import stage8e2_parent_fitness_gate as F


def rows(g=0):
    arms = ("shared",) if g == 0 else ("S", "M")
    return [{"population": p, "generation": g, "arm": arm,
             "slot": slot, "family": family, "repeat": repeat,
             "steps_lived": 400 if repeat else 250,
             "terminal": "censored" if repeat else "dead"}
            for p in range(64) for arm in arms for slot in range(24)
            for family in F.FAMILIES for repeat in (0, 1)]


class ParentFitnessGateTests(unittest.TestCase):
    def test_full_native_opportunity_matrix(self):
        for g in (0, 1):
            result = F.summarize_authenticated_lives(rows(g), g)
            self.assertEqual(len(result), 64*24*(1 if g == 0 else 2))
            self.assertTrue(all(v == (3, 1950) for v in result.values()))

    def test_death_at_horizon_is_not_censoring(self):
        dataset = rows()
        dataset[0]["steps_lived"] = 400
        dataset[0]["terminal"] = "dead"
        score = F.summarize_authenticated_lives(dataset, 0)[0, "shared", 0]
        self.assertEqual(score, (3, 2100))

    def test_missing_duplicate_or_invalid_identity_fails(self):
        original = rows()
        with self.assertRaises(ValueError):
            F.summarize_authenticated_lives(original[:-1], 0)
        broken = deepcopy(original)
        broken[0] = deepcopy(broken[1])
        with self.assertRaises(ValueError):
            F.summarize_authenticated_lives(broken, 0)
        broken = deepcopy(original)
        broken[0]["terminal"] = "censored"
        with self.assertRaises(ValueError):
            F.summarize_authenticated_lives(broken, 0)
        broken = deepcopy(original)
        broken[0]["steps_lived"] = True
        with self.assertRaises(ValueError):
            F.summarize_authenticated_lives(broken, 0)


if __name__ == "__main__":
    unittest.main()
