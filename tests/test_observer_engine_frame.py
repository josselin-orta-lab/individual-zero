"""Operator world-frame capture never changes physical state or exposes canaries."""
import unittest

from lab.stage4_reference_fixture import build_stage4_reference_runtime


class OperatorWorldFrameTests(unittest.TestCase):
    def test_capture_is_read_only_and_not_cognitive_observation(self):
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        world = individual.world
        before = world.export_causal_state()
        journal_before = individual.journal.canonical_bytes()
        frame = world.capture_operator_world_frame(t_monde=1)
        self.assertEqual(frame["individual_pose"], before["position"])
        self.assertEqual(frame["step_boundary"], "committed")
        self.assertEqual(frame["t_monde"], 1)
        self.assertEqual(frame["entities"], sorted(frame["entities"], key=lambda x: x["id"]))
        self.assertEqual(len({x["id"] for x in frame["entities"]}), len(frame["entities"]))
        self.assertNotIn("oracle_canary", repr(frame))
        self.assertEqual(world.export_causal_state(), before)
        self.assertEqual(individual.journal.canonical_bytes(), journal_before)

    def test_rejects_unusable_step(self):
        world = build_stage4_reference_runtime(autonomous_mortal=True).world
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                world.capture_operator_world_frame(t_monde=value)


if __name__ == "__main__":
    unittest.main()
