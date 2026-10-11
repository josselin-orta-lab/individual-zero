"""Stage12 operator control is external, monotonic and physically mortal."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.world import Command
from test_stage12_mortal_runtime import stage12_runtime


class Stage12ExternalConsoleTests(unittest.TestCase):
    def test_step_cap_permanently_stops_without_death_or_ghost_step(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.jsonl")
            runtime = stage12_runtime(path)
            substrate = runtime.stage3.substrate
            console = Stage12OperatorConsole(
                substrate=substrate, mode="campaign",
                policy_version="stage12-console-dev-v1",
                maximum_world_steps=2,
            )
            self.assertEqual(
                [o.owner_id for o in runtime.causal_owners].count("operator_console"),
                1,
            )
            with self.assertRaises(ValueError):
                console.plafonner(3)
            for _ in range(2):
                self.assertEqual(runtime.run_step().execution_status, "applied")
            before = deepcopy(runtime.world.export_causal_state())
            count = runtime.detection_report.evidence_samples
            with self.assertRaisesRegex(RuntimeError, "cap"):
                runtime.run_step()
            self.assertEqual(substrate.mortal_status, MortalStatus.EXPERIMENT_STOPPED)
            self.assertIsNone(substrate._mortal_boundary.terminal_death)
            self.assertEqual(runtime.scheduler.t_monde, 2)
            self.assertEqual(runtime.world.export_causal_state(), before)
            self.assertEqual(runtime.detection_report.evidence_samples, count)
            self.assertTrue(runtime.journal.verify())
            self.assertEqual(
                runtime.journal.entries[-1].causal_event["kind"],
                "experiment_stopped",
            )
            with self.assertRaises(RuntimeError):
                runtime.journal.append(event_id="illegal", causal_event={"kind": "learn"})
            with self.assertRaises(RuntimeError):
                runtime.world.apply(Command("attendre"), t_monde=3)
            with self.assertRaises(RuntimeError):
                runtime.run_step()
            with self.assertRaises(RuntimeError):
                console.arreter(reason="repeat")
            self.assertEqual(
                HashChainedJournal.audit_durable_wal(path)["head_hash"],
                runtime.journal.head_hash,
            )
            result = audit_export_bytes(runtime.journal.canonical_bytes())
            self.assertEqual(result.terminal_deaths, 0)
            self.assertEqual(result.world_steps_closed, 2)

    def test_diagnostic_block_can_resume_only_with_closed_zero_advance_proof(self):
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "diagnostic.jsonl"))
            sub = runtime.stage3.substrate
            console = Stage12OperatorConsole(
                substrate=sub, mode="diagnostic",
                policy_version="stage12-console-dev-v1",
            )
            sub.open_step()
            sub.safety.enter_safety_block(reason="diagnostic_injected_block")
            sub.scheduler.close_step(
                outcome="blocked", applied_command_count=0,
                world_advance_count=0,
            )
            self.assertTrue(sub.safety.blocked)
            self.assertEqual(sub._mortal_boundary.last_world_step, 0)
            with self.assertRaises(RuntimeError):
                runtime.run_step()
            console.resoudre_blocage(
                decision="resume", decision_ref="operator:accept-resume:1",
            )
            self.assertFalse(sub.safety.blocked)
            self.assertEqual(sub._mortal_boundary.last_world_step, 1)
            self.assertEqual(sub.mortal_status, MortalStatus.ACTIVE)
            result = runtime.run_step()
            self.assertEqual(result.execution_status, "applied")
            self.assertEqual(runtime.scheduler.t_monde, 2)
            audited = audit_export_bytes(runtime.journal.canonical_bytes())
            self.assertEqual(audited.world_steps_closed, 2)
            self.assertEqual(audited.autobiographical_commits, 1)
            self.assertTrue(runtime.journal.verify())

    def test_campaign_block_auto_stops_and_cannot_release_it(self):
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "campaign.jsonl"))
            sub = runtime.stage3.substrate
            console = Stage12OperatorConsole(
                substrate=sub, mode="campaign",
                policy_version="stage12-console-dev-v1",
            )
            sub.open_step()
            sub.safety.enter_safety_block(reason="test_campaign_block")
            sub.scheduler.close_step(
                outcome="blocked", applied_command_count=0, world_advance_count=0,
            )
            with self.assertRaises(RuntimeError):
                console.resoudre_blocage(decision="resume", decision_ref="forbidden")
            with self.assertRaisesRegex(RuntimeError, "safety block"):
                runtime.run_step()
            self.assertEqual(sub.mortal_status, MortalStatus.EXPERIMENT_STOPPED)
            self.assertTrue(sub.safety.blocked)
            self.assertEqual(
                runtime.journal.entries[-1].causal_event["kind"],
                "experiment_stopped",
            )
            self.assertEqual(audit_export_bytes(
                runtime.journal.canonical_bytes()
            ).terminal_deaths, 0)

    def test_offline_audit_rejects_rehashed_poststop_cognition(self):
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "stop.jsonl"))
            console = Stage12OperatorConsole(
                substrate=runtime.stage3.substrate,
                mode="diagnostic", policy_version="stage12-console-dev-v1",
            )
            runtime.run_step()
            console.arreter(reason="operator_finished")
            rows = [
                json.loads(raw)
                for raw in runtime.journal.canonical_bytes().split(b"\n")
            ]
            extra = {
                "index": len(rows),
                "event_id": "forged:poststop",
                "previous_hash": rows[-1]["event_hash"],
                "causal_event": {
                    "emitter": "stage4-runtime", "kind": "episode_closed",
                    "t_monde": runtime.scheduler.t_monde,
                },
            }
            extra["event_hash"] = sha256(
                bytes.fromhex(extra["previous_hash"]) + canonical_causal_bytes({
                    "event_id": extra["event_id"],
                    "causal_event": extra["causal_event"],
                })
            ).hexdigest()
            forged = b"\n".join(
                canonical_causal_bytes(row) for row in rows + [extra]
            )
            with self.assertRaisesRegex(ValueError, "after experiment stop"):
                audit_export_bytes(forged)
            self.assertTrue(runtime.journal.verify())


if __name__ == "__main__":
    unittest.main()
