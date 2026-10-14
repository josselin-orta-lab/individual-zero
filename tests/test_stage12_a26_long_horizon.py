"""Longitudinal Stage12 audit controls and short integrated smoke."""
from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_stage12_issue110_a26_long as a26
from test_stage12_spatial_integrated_rehash import rechain
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs


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
            self.assertEqual(report["terminal_status"], "experiment_stopped_at_cap")
            journal = Path(root) / "control_restored_free" / "canonical.jsonl"
            self.assertTrue(journal.is_file())
            self.assertTrue(
                (Path(root) / "control_restored_free" / "life.wal").is_file())
            original = journal.read_bytes()
            self.assertGreaterEqual(
                audit_stage12_attribution_pairs(original).admitted_pairs, 1,
            )
            rows = [json.loads(line) for line in original.splitlines()]
            pair_t = min(
                r["causal_event"]["t_monde"] for r in rows
                if r["causal_event"].get("kind")
                == "stage12_attribution_pair_admitted"
            )
            # Mutation preserves the cryptographic chain and world steps,
            # but removes evidence that the final unpaired step was asleep.
            missing = next(
                (r for r in rows
                 if r["causal_event"].get("kind") == "stage10_reduced_capture"
                 and r["causal_event"].get("t_monde") > pair_t),
                None,
            )
            self.assertIsNotNone(missing)
            missing["causal_event"]["kind"] = "forged_non_sleep_receipt"
            altered = rechain(rows)
            self.assertEqual(audit_export_bytes(altered).world_steps_closed, 6)
            with self.assertRaisesRegex(
                ValueError, "missing next-step diagnostic"
            ):
                audit_stage12_attribution_pairs(altered)


if __name__ == "__main__":
    unittest.main()
