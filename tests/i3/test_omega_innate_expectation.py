"""omega: inherited expectation toward the unknown (software contract only)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from i3.archive.stage1.lab import stage1_omega_falsifier as F
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.recent_rms_effect_prior import paid_recent_rms_zero_mean_effect_prior
from i3.modules.rms_three_leaf_target_prior import paid_rms_three_leaf_target_prior
from i3.modules.water_future_opportunity import paid_water_one_future_opportunity_value
import test_water_future_opportunity as W

BODY = (80., 80., 30., 80., 80.)
SRC = Path(__file__).resolve().parents[2] / "src" / "i3" / "modules"


def rms(omega=0.0, memory=None):
    return paid_recent_rms_zero_mean_effect_prior(
        memory or W.realistic_memory(), CognitiveBudget(BODY, BodyLaws()), omega=omega)


class OmegaPriorTests(unittest.TestCase):
    def test_default_is_the_zero_mean_prior(self):
        a = paid_recent_rms_zero_mean_effect_prior(
            W.realistic_memory(), CognitiveBudget(BODY, BodyLaws()))
        b = rms(0.0)
        for key in ("outcomes", "expected_external_delta", "branch_second_moment",
                    "rms_scale", "work", "status"):
            self.assertEqual(a[key], b[key])
        self.assertEqual(b["expected_external_delta"], (0.0,) * 5)

    def test_shift_moves_mean_keeps_spread(self):
        for omega in (-1.0, -0.5, 0.25, 1.0):
            r = rms(omega)
            s = r["rms_scale"]
            plus, minus = r["outcomes"]
            for c in range(5):
                self.assertAlmostEqual(r["expected_external_delta"][c], omega * s[c], places=12)
                self.assertAlmostEqual(plus.probe_delta[c] - minus.probe_delta[c], 2 * s[c], places=12)
                self.assertAlmostEqual(
                    r["branch_second_moment"][c],
                    (1 + omega * omega) * r["recent_raw_second_moment"][c], places=9)
            self.assertEqual(r["innate_mean_shift_omega"], omega)

    def test_extremes_remove_one_side(self):
        hope, dread = rms(1.0), rms(-1.0)
        self.assertEqual(hope["outcomes"][1].probe_delta, (0.0,) * 5)
        self.assertEqual(dread["outcomes"][0].probe_delta, (0.0,) * 5)

    def test_invalid_omega_rejected(self):
        for bad in (1.5, -1.01, float("nan"), float("inf"), True, "0.5", None):
            with self.assertRaises(ValueError):
                rms(bad)

    def test_omega_changes_beliefs_not_computation(self):
        works = {omega: rms(omega)["work"] for omega in F.OMEGAS}
        self.assertEqual(len({tuple(sorted(w.items())) for w in works.values()}), 1)

    def test_insufficient_support_stays_without_branches(self):
        from i3.modules.reference_branches import ReferenceBranchMemory
        r = rms(0.75, memory=ReferenceBranchMemory())
        self.assertEqual(r["status"], "INSUFFICIENT_GENERIC_SUPPORT")
        self.assertEqual(r["outcomes"], ())


class OmegaCompositionTests(unittest.TestCase):
    def test_three_leaf_mean_is_target_probability_times_shift(self):
        for omega in (-0.5, 0.0, 0.5):
            r = paid_rms_three_leaf_target_prior(
                {}, W.realistic_memory(), "water", CognitiveBudget(BODY, BodyLaws()),
                omega=omega)
            self.assertEqual(r["leaf_count"], 3)
            for c in range(5):
                self.assertAlmostEqual(
                    r["expected_external_delta"][c],
                    r["target_probability"] * omega * r["rms_scale"][c], places=12)

    def test_water_kernel_work_identical_across_omega(self):
        def work(omega):
            return paid_water_one_future_opportunity_value(
                W.make_mind(), W.realistic_memory(), W.EXPLORE, F.STOP_AFTER_PREFIX,
                6, CognitiveBudget(BODY, BodyLaws()), omega=omega)["work"]
        reference = work(0.0)
        for omega in F.OMEGAS:
            self.assertEqual(work(omega), reference)


class OmegaBoundaryTests(unittest.TestCase):
    def test_personal_support_paths_never_read_omega(self):
        for name in ("carried_food_information.py", "mind.py", "personal_outcomes.py",
                     "reference_branches.py", "observed_effect_view.py"):
            self.assertNotIn("omega", (SRC / name).read_text(), name)

    def test_genome_wiring_remains_separate_from_mind(self):
        self.assertIn("omega", (SRC / "genome.py").read_text())
        self.assertNotIn("omega", (SRC / "mind.py").read_text())

    def test_falsifier_fixtures_match_the_1101_tests(self):
        self.assertEqual(F.EXPLORE, W.EXPLORE)
        self.assertEqual(F.BASE, W.BASE)
        a, b = F.realistic_memory(), W.realistic_memory()
        self.assertEqual([(x.key, x.delta) for x in a._samples],
                         [(x.key, x.delta) for x in b._samples])
        self.assertEqual(F.make_mind().effects.stats, W.make_mind().effects.stats)


if __name__ == "__main__":
    unittest.main()
