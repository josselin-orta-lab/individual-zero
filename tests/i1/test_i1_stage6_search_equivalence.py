"""End-to-end Stage6 search equivalence against its precise list-FIFO variant.

Both planners receive the same accessible SimulationState and deterministic
simulated rollouts; no WorldBody, privileged map, or old scientific evidence.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Stage6SearchEquivalenceTests(unittest.TestCase):
    def test_full_search_decisions_and_diagnostics_match_prior_fifo(self):
        with TemporaryDirectory(prefix="i1-stage6-fifo-") as folder:
            output = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
import inspect
import textwrap
from dataclasses import replace
from types import SimpleNamespace
from i1.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from i0.equipment import SimulationState, SimulationNeighbor

# The exact original Stage6 queue code is reconstructed inside this isolated
# test process. The strict generated source-parity gate also rejects changes
# outside these three transformations.
src = textwrap.dedent(inspect.getsource(SimulatorPlanner.search))
for needle in ("queue = deque([", "    ])\n    visited =", "node = queue.popleft()"):
    assert src.count(needle) == 1, (needle, src)
old_src = (src.replace("queue = deque([", "queue = [", 1)
    .replace("    ])\n    visited =", "    ]\n    visited =", 1)
    .replace("node = queue.popleft()", "node = queue.pop(0)", 1))
namespace = dict(SimulatorPlanner.search.__globals__)
exec("from __future__ import annotations\n" + old_src, namespace)
old_search = namespace["search"]

deltas = {"north": (0, -1), "south": (0, 1),
          "east": (1, 0), "west": (-1, 0)}
neighbors = tuple(
    SimulationNeighbor(direction=d, x=dx, y=dy, passable=True,
                       water_source=False, resources=(), creature=False)
    for d, (dx, dy) in deltas.items()
)
initial = SimulationState(
    schema_version="stage6-simulation-state-v1", x=0, y=0,
    body={"energy": 45.0, "food": 32.0, "water": 42.0, "integrity": 80.0},
    inventory={"berry_a": 1, "berry_b": 0}, current_water_source=True,
    current_resources=("berry_a",), adjacent=neighbors,
    known_shelter_here=False, is_night=False,
)
initial.validate()

class DeterministicFixtureSimulator:
    def __init__(self, mode):
        self.mode = mode
        self.calls = []
    def rollout(self, *, initial_state, commands, r_eff, h_eff):
        assert r_eff == h_eff == 1 and len(commands) == 1
        command = commands[0]
        self.calls.append((initial_state.x, initial_state.y,
                           tuple(sorted(initial_state.inventory.items())),
                           command.primitive, tuple(sorted(command.parameters.items()))))
        if self.mode == "all_unavailable" or (
            self.mode == "mixed" and command.primitive in {"boire", "dormir"}
        ):
            return SimpleNamespace(complete=False, completed_rollouts=())
        x, y = initial_state.x, initial_state.y
        body = dict(initial_state.body)
        inventory = dict(initial_state.inventory)
        if command.primitive == "se_deplacer":
            dx, dy = deltas[command.parameters["direction"]]
            x, y = x + dx, y + dy
        elif command.primitive == "collecter":
            name = command.parameters["target"]
            inventory[name] = min(3, inventory.get(name, 0) + 1)
        elif command.primitive == "manger":
            name = command.parameters["target"]
            inventory[name] = max(0, inventory[name] - 1)
            body["food"] = min(100.0, body["food"] + 7.0)
        elif command.primitive == "boire":
            body["water"] = min(100.0, body["water"] + 8.0)
        elif command.primitive == "dormir":
            body["energy"] = min(100.0, body["energy"] + 4.0)
        next_state = replace(initial_state, x=x, y=y, body=body,
                             inventory=inventory)
        prediction = SimpleNamespace(next_state=next_state, terminal=False)
        return SimpleNamespace(
            complete=True,
            completed_rollouts=(SimpleNamespace(predictions=(prediction,)),),
        )

scenarios = (
    ("all_available", "at_goal", None),
    ("all_available", "reachable_move", None),
    ("mixed", "reachable_move", None),
    ("all_unavailable", "unreachable", "food"),
    ("mixed", "unreachable", "food"),
    ("all_available", "unreachable", "food"),
    ("all_available", "unreachable", "water"),
    ("all_available", "unreachable", None),
)
checks = 0
for depth in (1, 2, 3):
    for progressive in (False, True):
        for mode, goal, measure in scenarios:
            config = Stage6PlanningConfig(
                version="equivalence-only", option_ttl_steps=1,
                max_depth=depth, revision_delta=0.0,
                setpoints={"energy": 50, "food": 50,
                           "water": 50, "integrity": 50},
                progressive_subgoals=progressive,
                progressive_evaluation_prefix=progressive,
            )
            target = {
                "at_goal": lambda s: s.x == 0 and s.y == 0,
                "reachable_move": lambda s: s.x == 2 and s.y == 0,
                "unreachable": lambda s: s.x == 99,
            }[goal]
            previous_sim = DeterministicFixtureSimulator(mode)
            updated_sim = DeterministicFixtureSimulator(mode)
            previous = SimulatorPlanner(config=config, simulator=previous_sim)
            updated = SimulatorPlanner(config=config, simulator=updated_sim)
            expected = old_search(previous, initial_state=initial,
                                  target=target, progress_measure=measure)
            actual = updated.search(initial_state=initial, target=target,
                                    progress_measure=measure)
            assert actual == expected, (depth, progressive, mode, goal, measure)
            assert updated.last_search_diagnostic == previous.last_search_diagnostic
            assert updated_sim.calls == previous_sim.calls
            checks += 1
assert checks == 48
print("I1_STAGE6_FULL_SEARCH_FIFO_PARITY_OK", checks)
"""
            tested = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(output)},
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(tested.returncode, 0, tested.stderr)
            self.assertIn("I1_STAGE6_FULL_SEARCH_FIFO_PARITY_OK 48", tested.stdout)


if __name__ == "__main__":
    unittest.main()
