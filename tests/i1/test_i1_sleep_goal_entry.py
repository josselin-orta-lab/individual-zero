"""Regression: real I1 goal-driven dormir may enter sleep, but no forged action."""
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i1.modules.sleep_session import SleepSession

class SleepGoalEntryTests(unittest.TestCase):
    def test_both_legitimate_motives_and_reject_non_admitted(self):
        for motive in ("active_goal", "sleep_pressure"):
            with self.subTest(motive=motive):
                s = SleepSession(wake_policy_version="i1-fcog-020")
                self.assertEqual(s.open_world_step(1), "awake")
                command = SimpleNamespace(primitive="dormir")
                admission = SimpleNamespace(command=command, ok=True)
                prepared = SimpleNamespace(command=command, source="decision",
                                           option_ref="option:real")
                s.record_applied_sleep_decision(
                    world_step=1, admission=admission, prepared=prepared,
                    motive_type=motive, execution_status="applied")
                self.assertEqual(s.open_world_step(2), "sleeping")
        for forbidden in ("recovery_goal", "unknown", ""):
            s = SleepSession(wake_policy_version="i1-fcog-020")
            s.open_world_step(1)
            cmd = SimpleNamespace(primitive="dormir")
            with self.assertRaises(ValueError):
                s.record_applied_sleep_decision(
                    world_step=1, admission=SimpleNamespace(command=cmd,ok=True),
                    prepared=SimpleNamespace(command=cmd,source="decision",option_ref="opt"),
                    motive_type=forbidden, execution_status="applied")
        s = SleepSession(wake_policy_version="i1-fcog-020")
        s.open_world_step(1)
        cmd = SimpleNamespace(primitive="dormir")
        with self.assertRaises(ValueError):
            s.record_applied_sleep_decision(
                world_step=1, admission=SimpleNamespace(command=cmd,ok=False),
                prepared=SimpleNamespace(command=cmd,source="decision",option_ref="opt"),
                motive_type="active_goal", execution_status="applied")

if __name__ == "__main__":
    unittest.main()
