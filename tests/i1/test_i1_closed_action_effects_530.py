"""#530: preserve only already lived, whitelisted transition effects."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedActionEffects530(unittest.TestCase):
    def test_generated_i1_effects_custody_and_absence(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)],
                capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            script = r"""
from i1.modules.memory import EpisodicMemory, Episode

def ep(i):
    return Episode(
        id=f"episode:{i}", start_t_monde=i, end_t_monde=i,
        event_refs=(f"c{i}", f"t{i}"), boundary_type="max_length",
        active_goal_ref=None, body_start=None, body_end=None,
        cumulative_reward=0., surprise=0., linked_previous_ref=None)
m = object.__new__(EpisodicMemory)
m._episodes = [ep(i) for i in range(1, 7)]
m._seen_event_refs = {ref for e in m._episodes for ref in e.event_refs}
body = dict(energy=30, food=60, water=50, integrity=90)
effects = [
    {"collected": {"kind": "wood", "quantity": 2}},
    {"collected": {"kind": "wood", "quantity": 0}},
    {"movement": "blocked"},
    {"tool_crafted": False},
    {"drank": False},
    {},
]
actions = ["collecter", "collecter", "se_deplacer",
           "fabriquer_outil", "boire", "attendre"]
events = []
for i, (action, effect) in enumerate(zip(actions, effects), 1):
    events.extend([
        {"event_id": f"c{i}", "kind": "command_experienced",
         "t_monde": i, "primitive": action, "parameters": {}},
        {"event_id": f"t{i}", "kind": "world_transition_experienced",
         "t_monde": i, "position_after": {"x": 1, "y": 2},
         "body_after": body.copy(), "effects": effect},
    ])
def read(rows=events, memory=m):
    return memory.closed_applied_action_witnesses(
        autobiography=rows, now=7)
rows = read()
assert len(rows) == 6
assert [x["observed_effects"] for x in rows] == effects
assert all(x["causal_attribution"] is False and
           x["decision_evidence"] is False for x in rows)
assert rows[0]["same_step_body_delta"] is None
rows[0]["observed_effects"]["collected"]["quantity"] = 900
assert read()[0]["observed_effects"]["collected"]["quantity"] == 2
# No source may become a successful collection from its command alone.
for effect in (
    {"collected": {"kind":"wood", "quantity": True}},
    {"collected": {"kind":"wood", "quantity": -1}},
    {"collected": {"kind":"wood", "quantity": 1, "secret": "oracle"}},
    {"drank": 1}, {"tool_crafted": "yes"}, {"unknown_oracle": True},
    {"movement": {"hidden": "ground_truth"}},
):
    modified = [dict(e) for e in events]
    modified[1] = dict(modified[1], effects=effect)
    assert [x["step"] for x in read(modified)] == [2,3,4,5,6]
m._episodes.pop()
assert [x["step"] for x in read()] == [1,2,3,4,5]
print("I1_530_CLOSED_ACTION_EFFECTS_OK")
"""
            run = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(output)},
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_530_CLOSED_ACTION_EFFECTS_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
