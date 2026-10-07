from __future__ import annotations

import unittest

from i0 import BootstrapI0
from i0.interfaces import Observation


class BootstrapI0Tests(unittest.TestCase):
    def test_reset_restores_bootstrap_state(self) -> None:
        individual = BootstrapI0()
        individual.reset(seed=11)
        individual.step(Observation(cycle=0, kind="tick"))

        individual.reset(seed=5)

        self.assertEqual(
            individual.snapshot(),
            {
                "seed": 5,
                "cycles_completed": 0,
                "observations_seen": 0,
                "last_observation_kind": None,
            },
        )

    def test_step_exposes_minimal_observable_state(self) -> None:
        individual = BootstrapI0()
        individual.reset(seed=3)

        result = individual.step(Observation(cycle=0, kind="example"))

        self.assertEqual(result.action.kind, "noop")
        self.assertEqual(result.state["seed"], 3)
        self.assertEqual(result.state["cycles_completed"], 1)
        self.assertEqual(result.state["last_observation_kind"], "example")


if __name__ == "__main__":
    unittest.main()
