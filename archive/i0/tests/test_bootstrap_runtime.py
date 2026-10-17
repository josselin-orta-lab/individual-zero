from __future__ import annotations

import unittest

from i0 import BootstrapI0
from lab.runtime import RunConfig, run_individual
from lab.scenarios import SmokeScenario
from lab.sinks import MemorySink


class BootstrapRuntimeTests(unittest.TestCase):
    def run_once(self) -> tuple[dict[str, object], list[dict[str, object]]]:
        sink = MemorySink()
        summary = run_individual(
            individual=BootstrapI0(),
            scenario=SmokeScenario(),
            config=RunConfig(run_id="test-run", seed=7, cycles=3),
            sink=sink,
        )
        return summary.as_dict(), [event.as_dict() for event in sink.events]

    def test_run_is_deterministic_for_same_inputs(self) -> None:
        summary_a, events_a = self.run_once()
        summary_b, events_b = self.run_once()

        self.assertEqual(summary_a, summary_b)
        self.assertEqual(events_a, events_b)

    def test_bootstrap_emits_only_noop_actions(self) -> None:
        summary, _ = self.run_once()
        self.assertEqual(summary["action_kinds"], ["noop", "noop", "noop"])

    def test_event_sequence_is_complete(self) -> None:
        _, events = self.run_once()
        self.assertEqual(
            [event["kind"] for event in events],
            [
                "run_started",
                "observation",
                "step_completed",
                "observation",
                "step_completed",
                "observation",
                "step_completed",
                "run_completed",
            ],
        )

    def test_zero_cycles_is_valid(self) -> None:
        sink = MemorySink()
        summary = run_individual(
            individual=BootstrapI0(),
            scenario=SmokeScenario(),
            config=RunConfig(run_id="zero", seed=0, cycles=0),
            sink=sink,
        )

        self.assertEqual(summary.cycles_completed, 0)
        self.assertEqual([event.kind for event in sink.events], ["run_started", "run_completed"])


if __name__ == "__main__":
    unittest.main()
