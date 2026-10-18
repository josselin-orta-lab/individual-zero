"""No motor override: only a bounded research evidence-mixing transform."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "tools" / "i1_research_lived_evidence_floor.py"
spec = importlib.util.spec_from_file_location("research_positive_floor_only", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PositiveFloorContract(unittest.TestCase):
    def test_positive_lived_signal_does_not_attenuate_prior(self):
        f = mod.effective_learned_signal
        self.assertIsNone(f(prior=.2, learned=None))
        self.assertEqual(f(prior=.2, learned=.08), .2)
        self.assertEqual(f(prior=.2, learned=.4), .4)
        self.assertEqual(f(prior=.2, learned=0.0), 0.0)
        self.assertEqual(f(prior=.2, learned=-.4), -.4)
        self.assertAlmostEqual(.25*.2+.75*f(prior=.2,learned=.08),.2)
        self.assertAlmostEqual(.25*.2+.75*(-.4),-.25)

    def test_rejects_noncanonical_evidence(self):
        for value in (float("nan"),float("inf"),2.,-2.):
            with self.assertRaises(ValueError):
                mod.effective_learned_signal(prior=.2,learned=value)
        with self.assertRaises(ValueError):
            mod.effective_learned_signal(prior=-.2,learned=.1)


if __name__ == "__main__":
    unittest.main()
