"""Differential exact-overlap safety checks for natural I1 memory."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MemoryOverlapTests(unittest.TestCase):
    def test_exact_relevance_matches_all_reference_cases(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)],
                text=True, capture_output=True, check=False)
            self.assertEqual(built.returncode, 0, built.stderr)
            script = r"""
from i1.modules.memory import EpisodicMemory, Episode
import random
from types import SimpleNamespace

rng = random.Random(256)
mem = object.__new__(EpisodicMemory)
for n in (0, 1, 2, 8, 32, 256, 1024):
    for case in range(50):
        refs = tuple("ref:" + str(rng.randrange(2048)) for _ in range(n))
        visible = set("ref:" + str(rng.randrange(2048)) for _ in range(case % 20))
        episode = Episode(
            id="episode:0", start_t_monde=1, end_t_monde=2,
            event_refs=refs, boundary_type="max_length", active_goal_ref=None,
            body_start=None, body_end=None, cumulative_reward=0.0,
            surprise=0.0, linked_previous_ref=None,
        )
        st = SimpleNamespace(competitive=(), fixed={})
        expected = 1.0 if any(ref in visible for ref in refs) else 0.0
        observed = mem._relevance(episode, st, current_refs=visible,
                                  active_goal_id=None)
        assert observed == expected, (n, case, expected, observed)
        if refs:
            matched = set(visible)
            matched.add(refs[-1])
            assert mem._relevance(episode, st, current_refs=matched,
                                  active_goal_id=None) == 1.0
print("I1_MEMORY_OVERLAP_EQUIVALENCE_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(output)}, text=True,
                capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_MEMORY_OVERLAP_EQUIVALENCE_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
