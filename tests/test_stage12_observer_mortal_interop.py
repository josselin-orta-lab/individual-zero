"""Observer frame custody must not alter a genuine Stage12 mortal life.

This bridges the independently developed Observer Phase2 and Stage12 hooks.
It is a technical deterministic integration check, not physical truth or M-11.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.mortal_execution import MortalStatus
from lab.stage12_operator_console import Stage12OperatorConsole
from test_stage12_operator_alert_runtime import actual_stage12_runtime


class Stage12ObserverMortalInteropTests(unittest.TestCase):
    def _run_life(self, *, with_observer: bool):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            runtime = actual_stage12_runtime(str(root / "life.wal"))
            substrate = runtime.stage3.substrate
            self.assertIsNone(substrate.bench)
            self.assertIsNone(substrate.evaluation_trace)
            self.assertTrue(runtime.journal.durable_wal_enabled)
            Stage12OperatorConsole(
                substrate=substrate, mode="campaign",
                policy_version="stage12-observer-mortal-interop-v1",
                maximum_world_steps=4,
            )
            if with_observer:
                archive_path = root / "frames.jsonl"
                with substrate.enable_operator_frame_archive(str(archive_path)):
                    for step in range(1, 5):
                        self.assertEqual(runtime.run_step().execution_status, "applied")
                        self.assertEqual(runtime.scheduler.t_monde, step)
                frames = [
                    json.loads(line)
                    for line in archive_path.read_text(encoding="utf-8").splitlines()
                ]
            else:
                frames = []
                for step in range(1, 5):
                    self.assertEqual(runtime.run_step().execution_status, "applied")
                    self.assertEqual(runtime.scheduler.t_monde, step)
            self.assertIs(substrate.mortal_status, MortalStatus.EXPERIMENT_STOPPED)
            with self.assertRaises(RuntimeError):
                runtime.run_step()
            self.assertTrue(runtime.journal.verify())
            raw = runtime.journal.canonical_bytes()
            report = audit_export_bytes(
                raw, expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(report.world_steps_closed, 4)
            return raw, frames

    def test_frame_receipts_are_closed_and_causally_inert(self):
        baseline, _ = self._run_life(with_observer=False)
        observed, frames = self._run_life(with_observer=True)
        # External frame publication is neither a cognitive event nor a
        # backchannel: matched Stage12 lives retain identical causal bytes.
        self.assertEqual(observed, baseline)
        self.assertEqual(len(frames), 4)
        events = [json.loads(line) for line in observed.split(b"\n")]
        closed = {
            (row["causal_event"]["t_monde"], row["causal_event"]["attempt_ref"]):
            (index + 1, row["event_hash"])
            for index, row in enumerate(events)
            if row["causal_event"]["kind"] == "step_closed"
        }
        physical = {
            row["causal_event"]["t_monde"]: row["causal_event"]["position_after"]
            for row in events
            if row["causal_event"]["kind"] == "world_transition_experienced"
        }
        self.assertEqual(len(closed), 4)
        self.assertEqual(len(physical), 4)
        for expected_step, receipt in enumerate(frames, start=1):
            frame = receipt["frame"]
            self.assertEqual(frame["t_monde"], expected_step)
            self.assertEqual(frame["step_boundary"], "committed")
            anchor = closed[(expected_step, receipt["attempt_ref"])]
            self.assertEqual(receipt["journal_event_count"], anchor[0])
            self.assertEqual(receipt["journal_closure_hash"], anchor[1])
            self.assertEqual(receipt["journal_head_sha256"], anchor[1])
            self.assertEqual(frame["individual_pose"], physical[expected_step])


if __name__ == "__main__":
    unittest.main()
