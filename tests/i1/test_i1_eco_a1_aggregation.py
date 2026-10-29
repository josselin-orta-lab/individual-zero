"""A1 aggregation is fail closed before authentic independent M11 births."""
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from build_i1_fork import generate
from aggregate_i1_eco_a1 import aggregate
from run_i1_eco_a1 import MATRIX


class A1AggregationContract(unittest.TestCase):
    def test_missing_eight_never_yields_measurement_or_causal_go(self):
        with TemporaryDirectory() as root:
            d = Path(root)
            generated = d / "generated"
            generate(generated)
            with patch("aggregate_i1_eco_a1.subprocess.check_output",
                       return_value="a" * 40 + "\n"):
                report = aggregate(d / "empty", generated)
            self.assertEqual(report["verdict"], "MEASUREMENT_BLOCKED")
            self.assertEqual(report["adaptive_learning_go"], "NOT_ESTABLISHED")
            self.assertEqual(report["causal_attribution"], "NOT_ESTABLISHED")
            self.assertEqual(report["audited_lives"], 0)
            self.assertEqual(len(report["problems"]), len(MATRIX))
            self.assertEqual(report["pairs"], [])


if __name__ == "__main__":
    unittest.main()
