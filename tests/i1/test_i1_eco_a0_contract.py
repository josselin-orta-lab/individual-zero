"""ECO-v1 A0 fail-closed manifest and pilot-bound tests, no births."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from build_i1_fork import generate
from run_i1_eco_a0 import PRESETS, LABEL


class EcoA0ContractTests(unittest.TestCase):
    def test_fixed_six_distinct_preset_horizons(self):
        self.assertEqual(
            PRESETS,
            (("oasis", 24), ("foraging", 32), ("blocked-route", 36),
             ("dry-valley", 36), ("hazard-edge", 30), ("empty-land", 38)))
        self.assertEqual(LABEL, "i1-eco-v1-a0-measurement-only")

    def test_six_missing_or_malformed_worlds_fail_closed(self):
        from aggregate_i1_eco_a0 import aggregate
        with TemporaryDirectory(prefix="i1-eco-a0-contract-") as home:
            root = Path(home)
            generate(root / "generated")
            archive = root / "artifacts"
            archive.mkdir()
            result = aggregate(archive, root / "generated")
            self.assertEqual(result["verdict"], "MEASUREMENT_BLOCKED")
            self.assertEqual(len(result["problems"]), 6)
            self.assertFalse(result["audited_lives"])
            self.assertFalse(result["independent_cohort"])
            self.assertFalse(result["td_masked_comparator"])
            self.assertEqual(result["adaptive_learning_go"], "NOT_ESTABLISHED")
            # A fragment with a plausible name but no authenticated M11 still
            # fails; never synthesize a successful ecological trajectory.
            bad = archive / "i1-eco-a0-oasis-fake"
            bad.mkdir()
            (bad / "report.json").write_text("{}", encoding="utf-8")
            result = aggregate(archive, root / "generated")
            self.assertEqual(result["verdict"], "MEASUREMENT_BLOCKED")
            self.assertEqual(len(result["problems"]), 6)
            self.assertEqual(result["problems"][0]["preset"], "oasis")
            self.assertEqual(result["problems"][0]["problem"],
                             "TECHNICAL_AUDIT_FAILURE")


if __name__ == "__main__":
    unittest.main()
