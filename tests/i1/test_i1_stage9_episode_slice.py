"""Stage9 bounded newly closed episode access, with exact order preservation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Stage9EpisodeSliceTests(unittest.TestCase):
    def test_only_newly_closed_episodes_are_read(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"), "--output", str(output)],
                text=True, capture_output=True, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            script = r"""
from i1.modules.memory import EpisodicMemory, Episode
from types import SimpleNamespace

def ep(i):
    return Episode(
        id=f"episode:{i}", start_t_monde=i, end_t_monde=i,
        event_refs=(f"event:{i}",), boundary_type="max_length",
        active_goal_ref=None, body_start=None, body_end=None,
        cumulative_reward=0.0, surprise=0.0, linked_previous_ref=None,
    )
fake = object.__new__(EpisodicMemory)
fake._episodes = [ep(i) for i in range(2000)]
for added in (0, 1, 8, 64):
    before = fake.episode_count
    fake._episodes.extend(ep(i) for i in range(before, before + added))
    old = fake.episodes[before:]
    new = fake.read_episodes_range(before, fake.episode_count)
    assert old == new
    assert len(new) == added
for invalid in ((-1, 1), (4, 3), (0, fake.episode_count+1), (True, 2)):
    try:
        fake.read_episodes_range(*invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid range accepted: {invalid}")
print("I1_STAGE9_EPISODE_SLICE_EQUIVALENT")
"""
            proc = subprocess.run(
                [sys.executable, "-c", script], text=True, capture_output=True,
                check=False, env={"PYTHONPATH": str(output)})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_STAGE9_EPISODE_SLICE_EQUIVALENT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
