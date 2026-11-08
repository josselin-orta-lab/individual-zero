"""Candidate-G projection-dependence diagnostic: fixtures and arms (software only)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_projection_dependence as D
from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G


class CandidateGProjectionDependenceTests(unittest.TestCase):
    def test_reference_arm_is_the_1146_mind(self):
        a, b = D.make_mind("reference"), G.make_mind()
        self.assertEqual(a.effects.stats, b.effects.stats)
        self.assertEqual((a.simulation_mode, a.projection_accounting, a.proj_chunks),
                         (b.simulation_mode, b.projection_accounting, b.proj_chunks))

    def test_arms_change_only_the_projection(self):
        f = D.make_mind("candidate_f_projection")
        s = D.make_mind("per_step")
        self.assertEqual((f.simulation_mode, f.projection_accounting),
                         ("candidate_f", "event_local_quadratic4"))
        self.assertEqual(s.proj_chunks, (1,) * 255)
        ref = D.make_mind("reference")
        for m in (f, s):
            self.assertEqual(m.effects.stats, ref.effects.stats)
            self.assertFalse(hasattr(m, "first_contact_omega"))


if __name__ == "__main__":
    unittest.main()
