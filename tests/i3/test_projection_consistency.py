"""P1.3 projection accounting: opt-in discounted trapezoid (software contract)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import projection_consistency_characterization as P
from i3.modules import genome as G
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.mind import Mind, PROJECTION_ACCOUNTING


def linear_regime_mind():
    # Only water is below its threshold all along the 255-step projection,
    # with p = 1 and a constant drift: distress is linear in steps.
    g = G.midpoint()
    for ch in ("energy", "food", "integrity", "vigilance"):
        g["genes"][f"theta.{ch}"] = 30.0
    g["genes"]["theta.water"] = 90.0
    g["genes"]["p.water"] = 1.0
    mind = Mind(G.validate(g), 3)
    mind.effects.observe(("attendre",), (0., 0., -.1, 0., 0.))
    mind._drift = mind.drift()
    return mind


class ProjectionAccountingTests(unittest.TestCase):
    def test_default_is_reference_and_unknown_mode_rejected(self):
        mind = P.make_mind(G.midpoint())
        self.assertEqual(mind.projection_accounting, "chunk_end")
        self.assertEqual(PROJECTION_ACCOUNTING, ("chunk_end", "trapezoid"))
        mind.projection_accounting = "midpoint"
        with self.assertRaises(ValueError):
            mind.project((80.,) * 5, mind._drift)

    def test_unit_chunks_make_both_modes_identical(self):
        a, b = P.make_mind(G.midpoint()), P.make_mind(G.midpoint())
        a.proj_chunks = b.proj_chunks = (1,) * 40
        b.projection_accounting = "trapezoid"
        body = (80., 30., 30., 80., 80.)
        self.assertEqual(a.project(body, a._drift), b.project(body, b._drift))

    def test_trapezoid_is_exact_when_distress_is_linear(self):
        body = (100., 100., 80., 100., 100.)
        step, trap = linear_regime_mind(), linear_regime_mind()
        step.proj_chunks = P.PER_STEP
        trap.projection_accounting = "trapezoid"
        exact = step.project(body, step._drift)[0]
        approx = trap.project(body, trap._drift)[0]
        for e, t in zip(exact, approx):
            self.assertAlmostEqual(e, t, delta=1e-9 * max(1.0, abs(e)))

    def test_paid_units_are_identical(self):
        self.assertEqual(P.paid_units("trapezoid"), P.paid_units("chunk_end"))
        self.assertEqual(P.paid_units("chunk_end"), 8)

    def test_trapezoid_reduces_projection_equivalent_gap(self):
        body = (80., 20., 80., 80., 80.)
        gaps = {}
        for scheme in ("chunk_end", "trapezoid", "per_step"):
            v = P.values(G.midpoint(), body, scheme,
                         sleep_learned=False, projection_equivalent=True)
            gaps[scheme] = abs(v["plus_1_wait"] - v["prefix"])
        self.assertLess(gaps["per_step"], 1e-9)
        self.assertLess(gaps["trapezoid"], gaps["chunk_end"])


if __name__ == "__main__":
    unittest.main()
