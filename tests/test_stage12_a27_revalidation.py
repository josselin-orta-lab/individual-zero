"""A2.7: no fabricated progress and no stale partial across world steps."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_first_planning_state import build_life
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.journal import HashChainedJournal
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress


def short_life(revalidate):
    with TemporaryDirectory() as root:
        life, _, _, _ = build_life(
            "near_food_free", 70.0, "horizon_three",
            wal_path=str(Path(root) / "life.wal"),
            birth_life_id=f"i0:110:a27:test:{revalidate}",
            calibration_food_profile="sustained", progressive_planning=True,
            progressive_evaluation_prefix=True,
            instrumental_geographic_value=False,
            progressive_revalidate_on_new_capture=revalidate,
        )
        Stage12OperatorConsole(
            substrate=life.stage3.substrate, mode="campaign",
            policy_version="stage12-a27-smoke-v1", maximum_world_steps=4)
        for _ in range(4):
            result = life.run_step()
            if result.execution_status != "applied":
                raise AssertionError(result.execution_status)
        raw = life.journal.canonical_bytes()
        anchors = {"expected_head": life.journal.head_hash,
                   "expected_count": len(life.journal.entries)}
        wal = HashChainedJournal.audit_durable_wal(str(Path(root) / "life.wal"))
        if (wal["head_hash"] != anchors["expected_head"]
                or wal["verified_entries"] != anchors["expected_count"]):
            raise AssertionError("WAL mismatch")
        audit_stage12_goal_progress(raw, **anchors)
        audit_stage12_attribution_pairs(raw, **anchors)
        return [json.loads(line)["causal_event"] for line in raw.splitlines()]


class FreshCaptureTests(unittest.TestCase):
    def test_config_guard(self):
        life, _, _, _ = build_life(
            "near_food_free", 70.0, "horizon_three",
            progressive_planning=True, progressive_evaluation_prefix=True)
        cfg = life.planning._config
        with self.assertRaises(ValueError):
            replace(cfg, progressive_revalidate_on_new_capture=1).validate()
        with self.assertRaises(ValueError):
            replace(cfg, progressive_subgoals=False,
                    progressive_revalidate_on_new_capture=True).validate()

    def test_real_world_capture_revalidates_only_opt_in(self):
        control = short_life(False)
        treatment = short_life(True)
        kind = "stage6_progress_segment_revalidated"
        self.assertEqual(sum(e["kind"] == kind for e in control), 0)
        receipts = [e for e in treatment if e["kind"] == kind]
        self.assertGreaterEqual(len(receipts), 1)
        for e in receipts:
            d = e["data"]
            self.assertLess(d["authored_world_step"], d["capture_world_step"])
            self.assertFalse(d["physical_progress_claimed"])
            self.assertFalse(d["agency_claimed"])
        def plans_at(events, t):
            return [e["data"]["progressive_search_diagnostic"]["status"]
                    for e in events if e["kind"] == "stage6_planning_result"
                    and e["t_monde"] == t]
        self.assertIn("reused_cached", plans_at(control, 3))
        self.assertIn("partial_progress", plans_at(treatment, 3))
        self.assertNotIn("reused_cached", plans_at(treatment, 3))


if __name__ == "__main__":
    unittest.main()
