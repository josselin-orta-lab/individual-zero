"""Longitudinal Stage12 audit controls and short integrated smoke."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_stage12_issue110_a26_long as a26


class LongHorizonReadOnlyContracts(unittest.TestCase):
    def test_milestone_requires_all_real_physical_steps(self):
        physical = {"world_steps": 1, "positions": [
            {"step": 1, "x": 3, "y": 2, "command": "se_deplacer",
             "movement": "moved", "food_after": 24.0}
        ]}
        events = [{"kind": "perceptual_capture", "t_monde": 1,
                   "data": {"position": {"x": 2, "y": 2}}}]
        self.assertIsNone(a26._snapshot(physical, events, 100))
        result = a26._snapshot(physical, events, 1)
        self.assertEqual(result["physically_distinct_sites"], 2)
        self.assertEqual(result["food_increase_steps"], 0)
        self.assertEqual(result["attribution_pairs_consumed"], 0)

    def test_paired_missing_600_is_not_invented(self):
        lives = [
            {"profile": profile, "a2": a2, "instrumental": enabled,
             "world_steps": (600 if profile == "restored" else 48),
             "terminal_status": ("experiment_stop_at_600"
                                 if profile == "restored" else "dead"),
             "milestones": {str(n): (
                 {"physically_distinct_sites": 31,
                  "eaten": 1, "food_last": 40.0,
                  "attribution_pairs_consumed": 0}
                 if (profile == "restored" and n <= 600) else None)
                 for n in a26.MILESTONES}}
            for profile, a2 in a26.PAIRS
            for enabled in (False, True)
        ]
        pairs = a26._paired(lives)
        self.assertEqual(len(pairs), 3)
        self.assertIsNone(pairs[2]["600"])
        self.assertTrue(pairs[0]["600"]["preserved_80pct"])
        self.assertTrue(pairs[1]["300"]["preserved_80pct"])

    def test_actual_mortal_life_with_small_external_cap(self):
        with TemporaryDirectory() as root:
            with patch.object(a26, "MAX_STEPS", 6):
                report = a26.run_one(
                    Path(root), "smoke-a26", "restored", False, False)
            self.assertIsNone(report["runtime_exception"])
            self.assertIsNone(report["audit_error"], report["audit_error"])
            self.assertEqual(report["world_steps"], 6)
            self.assertEqual(report["terminal_status"], "experiment_stop_at_600")
            self.assertTrue(
                (Path(root) / "control_restored_free" / "life.wal").is_file())


if __name__ == "__main__":
    unittest.main()
