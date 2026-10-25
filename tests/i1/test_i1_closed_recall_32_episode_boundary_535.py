"""#535: distinguish M11 memory retention from short-window paid recall access."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedRecallBoundary535(unittest.TestCase):
    def test_generated_i1_long_term_retention_vs_access(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from i1.modules.memory import EpisodicMemory, Episode
from types import SimpleNamespace
def ep(i):
    return Episode(
        id=f"episode:{i}", start_t_monde=i+1, end_t_monde=i+1,
        event_refs=(f"cmd{i}", f"trans{i}"),
        boundary_type="max_length", active_goal_ref=None,
        body_start=None, body_end=None,
        cumulative_reward=0., surprise=0., linked_previous_ref=None)
m = object.__new__(EpisodicMemory)
m._episodes = [ep(i) for i in range(34)]
m._seen_event_refs = {ref for e in m._episodes for ref in e.event_refs}
body = dict(energy=35, food=60, water=55, integrity=90)
events = []
for i in range(34):
    events.extend((
        dict(event_id=f"cmd{i}", kind="command_experienced",
             t_monde=i+1, primitive="collecter" if i==0 else "dormir",
             parameters={"target":"wood"} if i==0 else {}),
        dict(event_id=f"trans{i}", kind="world_transition_experienced",
             t_monde=i+1, position_after={"x":2,"y":2},
             body_after=body.copy(),
             effects={"collected":{"kind":"wood","quantity":1}}
             if i==0 else {"rest":"dormir"}),
    ))
state_refs = {ref for e in m._episodes for ref in e.event_refs}
assert {"cmd0","trans0"} <= state_refs
eligible = m.closed_sleep_recall_source_refs()
assert "cmd0" not in eligible and "trans0" not in eligible
assert {"cmd2","trans2","cmd33","trans33"} <= eligible
# The owner still remembers its old closed episode; selection simply
# cannot authenticate it in the 32-episode paid witness window.
assert m._episodes[0].event_refs == ("cmd0","trans0")
rows = m.closed_applied_action_witnesses(
    autobiography=events, now=35, per_command_limit=3)
assert [w["step"] for w in rows] == [32,33,34]
assert all(w["primitive"]=="dormir" for w in rows)
# A direct projection injection cannot overcome owner-side closed custody.
assert m.closed_applied_action_witnesses(
    autobiography=events[:2], now=35)==()
# An open or later episode cannot become testimony.
m._episodes.append(ep(34))
assert "cmd34" not in m.closed_sleep_recall_source_refs()
print("I1_535_SHORT_WINDOW_RETAINED_OLD_SOURCE_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_535_SHORT_WINDOW_RETAINED_OLD_SOURCE_OK",
                          result.stdout)


if __name__ == "__main__":
    unittest.main()
