"""#533: bounded action diversity preserves rare and contradictory first-person sources."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DiversePaidActionRecall533(unittest.TestCase):
    def test_generated_i1_bounded_exact_command_recall(self):
        with TemporaryDirectory() as folder:
            out = Path(folder) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            script = r"""
from i1.modules.memory import EpisodicMemory, Episode
def ep(i):
    return Episode(id=f"e{i}", start_t_monde=i, end_t_monde=i,
        event_refs=(f"c{i}", f"t{i}"), boundary_type="max_length",
        active_goal_ref=None, body_start=None, body_end=None,
        cumulative_reward=0., surprise=0., linked_previous_ref=None)
m = object.__new__(EpisodicMemory)
m._episodes = [ep(i) for i in range(1, 24)]
m._seen_event_refs = {ref for e in m._episodes for ref in e.event_refs}
body = dict(energy=30, food=60, water=50, integrity=90)
events = []
for i in range(1, 24):
    rare = i in (1, 2, 3)
    action = "collecter" if rare else "dormir"
    params = {"target": "wood"} if i in (1, 2) else (
        {"target": "stone"} if i == 3 else {})
    effects = ({"collected": {"kind": "wood", "quantity": 2}}
               if i == 1 else
               {"collected": {"kind": "wood", "quantity": 0}}
               if i == 2 else
               {"collected": {"kind": "stone", "quantity": 1}}
               if i == 3 else {"rest": "dormir"})
    events.extend((
        dict(event_id=f"c{i}", kind="command_experienced",
             t_monde=i, primitive=action, parameters=params),
        dict(event_id=f"t{i}", kind="world_transition_experienced",
             t_monde=i, position_after={"x":2,"y":3},
             body_after=body.copy(), effects=effects),
    ))
def read(**opts):
    return m.closed_applied_action_witnesses(
        autobiography=events, now=24, **opts)
assert [w["step"] for w in read()] == list(range(8, 24))
rows = read(per_command_limit=3)
assert [w["step"] for w in rows] == [1, 2, 3, 21, 22, 23]
assert rows[0]["observed_effects"]["collected"]["quantity"] == 2
assert rows[1]["observed_effects"]["collected"]["quantity"] == 0
assert rows[2]["parameters"] == {"target": "stone"}
assert len(rows) <= 16
assert [w["step"] for w in read(limit=2, per_command_limit=1)] == [3, 23]
assert [w["step"] for w in read(primitive="collecter",
      per_command_limit=2)] == [1, 2, 3]
m._episodes.pop()
assert [w["step"] for w in read(per_command_limit=3)] == [1,2,3,20,21,22]
m._episodes.append(ep(23))
events.append(events[0])
assert [w["step"] for w in read(per_command_limit=3)] == [2,3,21,22,23]
# Structured, authorized first-person scalar parameters must compare
# exactly without a hash-key crash (including canonical float wrappers).
events.pop()  # remove duplicate c1 from the earlier adversarial test
events[0]["parameters"] = {"target": {"$f64": "0x1.8000000000000p+0"}}
m._seen_event_refs.add("c1")
nested = read(per_command_limit=3)
assert [w["step"] for w in nested] == [1, 2, 3, 21, 22, 23]
assert nested[0]["parameters"] == {"target": {"$f64": "0x1.8000000000000p+0"}}
for bad in (0, -1, True, 17, 1.0):
    try:
        read(per_command_limit=bad)
    except ValueError:
        pass
    else:
        raise AssertionError(("invalid cap", bad))
print("I1_533_DIVERSE_CLOSED_ACTION_RECALL_OK")
"""
            finished = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(out)}, capture_output=True, text=True)
            self.assertEqual(finished.returncode, 0,
                             finished.stdout + finished.stderr)
            self.assertIn("I1_533_DIVERSE_CLOSED_ACTION_RECALL_OK",
                          finished.stdout)


if __name__ == "__main__":
    unittest.main()
