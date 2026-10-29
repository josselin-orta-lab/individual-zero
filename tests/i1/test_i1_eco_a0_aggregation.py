"""A0 must reject absent worlds without manufacturing a scientific verdict."""
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from build_i1_fork import generate
from aggregate_i1_eco_a0 import aggregate
from run_i1_eco_a0 import PRESETS


class A0AggregationContractTests(unittest.TestCase):
    def test_missing_all_six_keeps_evidence_gap_visible(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            generated = root / "generated"
            generate(generated)
            with patch("aggregate_i1_eco_a0.subprocess.check_output",
                       return_value="a" * 40 + "\n"):
                result = aggregate(root, generated)
        self.assertEqual(result["verdict"], "MEASUREMENT_BLOCKED")
        self.assertEqual(result["audited_lives"], [])
        self.assertEqual(len(result["problems"]), len(PRESETS))
        self.assertEqual(result["adaptive_learning_go"], "NOT_ESTABLISHED")
        self.assertFalse(result["independent_cohort"])
        self.assertFalse(result["td_masked_comparator"])


if __name__ == "__main__":
    unittest.main()
