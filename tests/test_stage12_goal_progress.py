"""Precommitted Stage12 goal-progress evidence, never attribution calibration."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_goal_progress import (
    CONTRACT_VERSION, LivedGoalProgressIntent, Stage12GoalProgressLedger,
)
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress, _number
from lab.stage12_operator_console import Stage12OperatorConsole
from test_stage12_operator_alert_runtime import actual_stage12_runtime


def intent(t: int, *, before: float = 40.0, ref: str | None = None):
    return LivedGoalProgressIntent(
        intent_ref=ref or f"intent:{t}", goal_ref=f"goal:{t}",
        option_ref=f"option:{t}", command_hash=f"command:{t}",
        measure="water", value_before=before, sent_world_step=t,
        observe_world_step=t + 1,
    )


class Stage12GoalProgressTests(unittest.TestCase):
    def test_precommitted_goal_improvement_is_not_p47_conformity(self):
        # A goal-progress criterion does not consult predicted value,
        # prediction conformity, Oracle state or world-cause labels.
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(intent(1, before=40.0))
        gain = ledger.followup(world_step=2, body={"water": 45.0})
        self.assertIsNotNone(gain)
        self.assertEqual(gain.criterion_outcome, "success")
        self.assertEqual(gain.value_before, 40.0)
        self.assertEqual(gain.value_after, 45.0)
        self.assertEqual(gain.reason, "measured_strict_gain")
        ledger.preregister(intent(2, before=45.0))
        no_gain = ledger.followup(world_step=3, body={"water": 45.0})
        self.assertEqual(no_gain.criterion_outcome, "failure")
        self.assertEqual(no_gain.reason, "no_measured_strict_gain")
        self.assertIsNone(ledger.followup(world_step=3, body={"water": 45.0}))

    def test_missing_measure_refused_uc_or_time_gap_remains_unknown(self):
        for t, body, paid, reason in (
            (2, {}, True, "lived_measure_unavailable"),
            (2, {"water": 50.0}, False, "diagnostic_uc_not_available"),
            (3, {"water": 50.0}, True, "one_step_observation_window_missed"),
        ):
            with self.subTest(t=t, paid=paid):
                ledger = Stage12GoalProgressLedger()
                ledger.preregister(intent(1))
                followup = ledger.followup(
                    world_step=t, body=body, diagnostic_paid=paid,
                )
                self.assertEqual(followup.criterion_outcome, "unknown")
                self.assertEqual(followup.reason, reason)
                self.assertIsNone(followup.value_after)

    def test_duplicate_intent_identity_and_physical_time_fail_closed(self):
        ledger = Stage12GoalProgressLedger()
        first = intent(1)
        ledger.preregister(first)
        prior = ledger.export_causal_state()
        with self.assertRaises(ValueError):
            ledger.preregister(first)
        self.assertEqual(ledger.export_causal_state(), prior)
        ledger.followup(world_step=2, body={"water": 41.0})
        with self.assertRaises(ValueError):
            ledger.preregister(intent(1, ref="other-ref"))
        with self.assertRaises(ValueError):
            ledger.preregister(intent(2, ref=first.intent_ref))
        self.assertIsNone(ledger.pending)

    def test_criterion_requires_a_specific_lived_measure_and_next_step(self):
        ledger = Stage12GoalProgressLedger()
        for change in (
            {"measure": "hidden_world_cause"},
            {"value_before": float("nan")},
            {"observe_world_step": 4},
            {"sent_world_step": 0},
            {"goal_ref": ""},
        ):
            with self.subTest(change=change):
                values = intent(1).as_dict()
                values.update(change)
                with self.assertRaises(ValueError):
                    ledger.preregister(LivedGoalProgressIntent(**values))
        self.assertEqual(ledger.export_causal_state()["registered_intent_refs"], [])

    def test_external_auditor_decodes_only_canonical_f64_body_values(self):
        for value in (0.0, 40.5, 100.0):
            self.assertEqual(_number({"$f64": value.hex()}), value)
        for forged in (
            {"$f64": "NaN"},
            {"$f64": "0X1.0P+1"},
            {"$f64": "0x1.0p+1", "ignored": True},
            {"$f64": 4},
            True,
            {"$f64": float("inf").hex()},
        ):
            with self.subTest(forged=forged):
                self.assertIsNone(_number(forged))

    def test_real_mortal_steps_never_fabricate_lived_agency(self):
        with TemporaryDirectory() as folder:
            runtime = actual_stage12_runtime(str(Path(folder) / "real-life.wal"))
            Stage12OperatorConsole(
                substrate=runtime.stage3.substrate, mode="campaign",
                policy_version="stage12-goal-progress-physics-v1",
                maximum_world_steps=4,
            )
            for step in range(1, 5):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                self.assertEqual(runtime.scheduler.t_monde, step)
            journal = runtime.journal.canonical_bytes()
            external = audit_stage12_goal_progress(
                journal, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(
                external.preregistered,
                external.verified_strict_gains + external.verified_no_gains
                + external.unavailable + external.unresolved_at_terminal,
            )
            self.assertTrue(runtime.journal.verify())
            self.assertIsNone(runtime.detection_report.attribution_bias)
            self.assertFalse(external.as_dict()["subjective_agency_attribution_verified"])


if __name__ == "__main__":
    unittest.main()
