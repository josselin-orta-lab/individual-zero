"""Lab probes under body laws v2: executable and never on credit.

Development worlds only; no reserved or held-out seed is used. These are
software checks, not a revalidation of the probes as scientific comparators (P2).
"""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.modules.body import ACTION_COSTS, CognitiveWork, E, V, cognitive_cost
from i3.modules.world import World
from i3.lab import worldgen
from i3.lab.dev_worlds import dev_far_home, dev_open_field
from i3.lab.probes import PROBE_WORK, _funded_step, oracle_survival, reference_survival

BILL_E, BILL_V = cognitive_cost(dev_open_field().laws, PROBE_WORK)

# Development cases on which the probes raised under v2 with the source of
# 2b3371dd: an unpayable probe bill (CognitiveFundingError) or a motor command
# left unfunded after the bill (ValueError).
REGRESSION_CASES = (
    (oracle_survival, "dev-far-home", dev_far_home),                  # unpayable bill
    (oracle_survival, "dev-4", lambda: worldgen.generate("dev", 4)),  # unfunded motor
    (reference_survival, "dev-far-home", dev_far_home),               # unpayable bill
    (reference_survival, "dev-open-field", dev_open_field),           # unfunded motor
    (reference_survival, "R-10", lambda: worldgen.generate("R", 10)), # unpayable bill
)


def _recording_step():
    """Spy on every command a probe sends to the world, with the body it saw."""
    calls = []
    original = World.step

    def spy(world, action, param, work):
        calls.append((world.body, action, work))
        return original(world, action, param, work)
    return calls, patch.object(World, "step", spy)


class ProbeFundingTests(unittest.TestCase):
    def test_probes_complete_where_unfunded_commands_used_to_raise(self):
        for probe, name, make in REGRESSION_CASES:
            with self.subTest(probe=probe.__name__, world=name):
                calls, spy = _recording_step()
                with spy:
                    steps = probe(make(), 400)
                self.assertTrue(1 <= steps <= 400)
                self.assertEqual(len(calls), steps)
                for body, action, work in calls:
                    # Paid before acting from actual reserves; no passive trap here.
                    self.assertIsNotNone(action)
                    self.assertEqual(work, PROBE_WORK)
                    self.assertLessEqual(BILL_E, body[E])
                    self.assertLessEqual(BILL_V, body[V])
                    if action != "dormir":
                        # The command and the next bill both remain funded.
                        self.assertGreaterEqual(body[E] - BILL_E - ACTION_COSTS[action], BILL_E)
                        self.assertGreaterEqual(body[V] - BILL_V, BILL_V)

    def test_unpayable_probe_bill_means_passive_inactivity_not_free_sleep(self):
        spec = replace(dev_open_field(), body=(0.05, 60.0, 60.0, 90.0, 50.0))
        self.assertLess(spec.body[E], BILL_E)
        passive = World(spec)
        while not passive.dead:
            passive.step(None, None, CognitiveWork())
        for probe in (oracle_survival, reference_survival):
            with self.subTest(probe=probe.__name__):
                calls, spy = _recording_step()
                with spy:
                    steps = probe(spec, 400)
                self.assertEqual(steps, passive.t)
                self.assertTrue(all(action is None and work == CognitiveWork()
                                    for _, action, work in calls))

    def test_command_that_would_leave_the_next_bill_unpaid_falls_back_to_sleep(self):
        # 2.1 energy pays this bill and a move (2.07) but not the next bill as well.
        world = World(replace(dev_open_field(), body=(2.1, 60.0, 60.0, 90.0, 100.0)))
        result, done = _funded_step(world, "se_deplacer", "E")
        self.assertEqual(done, "dormir")
        self.assertFalse(result["moved"])
        self.assertEqual(world.pos, (3, 3))
        self.assertGreater(world.body[E], 2.1 - BILL_E)  # sleep restored energy
        # Vigilance that would not cover the next bill also leads to sleep.
        world = World(replace(dev_open_field(), body=(80.0, 60.0, 60.0, 90.0, 0.2)))
        _, done = _funded_step(world, "attendre", None)
        self.assertEqual(done, "dormir")

    def test_command_with_a_funded_reserve_executes_unchanged(self):
        world = World(replace(dev_open_field(), body=(2.3, 60.0, 60.0, 90.0, 100.0)))
        result, done = _funded_step(world, "se_deplacer", "E")
        self.assertEqual(done, "se_deplacer")
        self.assertTrue(result["moved"])
        self.assertEqual(world.pos, (4, 3))
        self.assertEqual(result["cognitive_accounting"]["energy"]["paid"], BILL_E)


if __name__ == "__main__":
    unittest.main()
