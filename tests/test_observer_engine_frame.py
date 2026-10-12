"""Operator world-frame capture never changes physical state or exposes canaries."""
import tempfile
from pathlib import Path
import unittest

from lab.stage4_reference_fixture import build_stage4_reference_runtime


class OperatorWorldFrameTests(unittest.TestCase):
    def test_capture_is_read_only_and_not_cognitive_observation(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        world = individual.world
        before = world.export_causal_state()
        journal_before = individual.journal.canonical_bytes()
        frame = world.capture_operator_world_frame(t_monde=1)
        self.assertEqual(world.operator_world_geometry(), {
            "coordinate_system": "grid-xy-top-left", "width": 32, "height": 32,
        })
        self.assertEqual(frame["individual_pose"], before["position"])
        self.assertNotIn("step_boundary", frame)
        self.assertEqual(frame["t_monde"], 1)
        self.assertEqual(frame["entities"], sorted(frame["entities"], key=lambda x: x["id"]))
        self.assertEqual(len({x["id"] for x in frame["entities"]}), len(frame["entities"]))
        self.assertNotIn("oracle_canary", repr(frame))
        self.assertEqual(world.export_causal_state(), before)
        self.assertEqual(individual.journal.canonical_bytes(), journal_before)

    def test_closed_step_capture_requires_durable_wal(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        with self.assertRaisesRegex(RuntimeError, "durable journal WAL"):
            individual.stage3.substrate.capture_operator_closed_step()

    def test_wal_backed_mortal_step_publishes_exact_closed_frame(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        substrate = individual.stage3.substrate
        receipts = []
        with tempfile.TemporaryDirectory() as directory:
            individual.journal.enable_durable_wal(
                path=str(Path(directory) / "journal.wal")
            )
            substrate.install_operator_frame_sink(receipts.append)
            substrate.open_step()
            from lab.world import Command
            outcome = substrate.execute(Command("attendre"))
            self.assertEqual(outcome.status, "applied")
            self.assertEqual(len(receipts), 1)
            receipt = receipts[0]
            self.assertEqual(receipt["frame"]["t_monde"], 1)
            self.assertEqual(receipt["frame"]["step_boundary"], "committed")
            self.assertEqual(receipt["frame"]["individual_pose"],
                             individual.world.position.as_dict())
            self.assertEqual(receipt["journal_head_sha256"], individual.journal.head_hash)
            self.assertEqual(receipt["journal_closure_hash"], individual.journal.entries()[-1].event_hash)

    def test_operator_archive_persists_mortal_step(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        substrate = individual.stage3.substrate
        with tempfile.TemporaryDirectory() as directory:
            individual.journal.enable_durable_wal(
                path=str(Path(directory) / "journal.wal")
            )
            archive_path = Path(directory) / "frames.jsonl"
            with substrate.enable_operator_frame_archive(str(archive_path)):
                substrate.open_step()
                from lab.world import Command
                result = substrate.execute(Command("attendre"))
                self.assertEqual(result.status, "applied")
            import json
            receipts = [json.loads(line) for line in archive_path.read_text().splitlines()]
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["frame"]["t_monde"], 1)
            self.assertEqual(receipts[0]["journal_head_sha256"], individual.journal.head_hash)

    def test_rejects_unusable_step(self):
        world = build_stage4_reference_runtime(autonomous_mortal=True).world
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                world.capture_operator_world_frame(t_monde=value)


if __name__ == "__main__":
    unittest.main()
