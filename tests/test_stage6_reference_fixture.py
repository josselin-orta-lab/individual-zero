from __future__ import annotations

import unittest

from lab.stage6_reference_fixture import build_stage6_reference_runtime


class Stage6ReferenceFixtureTests(unittest.TestCase):
    def test_reference_path_drinks_then_stabilizes(self) -> None:
        runtime = build_stage6_reference_runtime()

        first = runtime.run_step()
        later = [runtime.run_step() for _ in range(9)]

        self.assertEqual(first.execution_status, "applied")
        self.assertEqual(first.command_primitive, "boire")
        self.assertTrue(
            all(result.execution_status == "applied" for result in later)
        )
        self.assertEqual(runtime.world.body.water, 60.0)
        self.assertEqual((runtime.world.position.x, runtime.world.position.y), (2, 2))
        self.assertTrue(
            any(
                entry.causal_event.get("kind") == "stage6_option_evaluation"
                and entry.causal_event.get("data", {}).get(
                    "simulated_value_status"
                ) == "computed"
                for entry in runtime.journal.entries
            )
        )
        self.assertFalse(
            any(
                entry.causal_event.get("kind") == "stage6_option_evaluation"
                and entry.causal_event.get("data", {}).get("equipment_version")
                != "E-v1-stage6-reference"
                for entry in runtime.journal.entries
            )
        )

    def test_reference_execution_is_byte_identical(self) -> None:
        def execute() -> bytes:
            runtime = build_stage6_reference_runtime()
            for _ in range(10):
                runtime.run_step()
            self.assertTrue(runtime.journal.verify())
            return runtime.journal.canonical_bytes()

        self.assertEqual(execute(), execute())


if __name__ == "__main__":
    unittest.main()
