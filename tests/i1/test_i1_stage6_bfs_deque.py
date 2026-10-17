"""Stage6 FIFO-equivalence and scaling checks; no cognitive oracle inputs."""
import importlib.util
from collections import deque
from pathlib import Path
import random
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Stage6BFSDequeTests(unittest.TestCase):
    def test_fifo_replacement_preserves_breadth_first_order(self):
        rng = random.Random(256)
        for size in (0, 1, 3, 16, 128, 1024):
            for trial in range(12):
                roots = [("root", i, 0) for i in range(size)]
                old = list(roots)
                new = deque(roots)
                old_visit, new_visit = [], []
                # Simulated bounded expansions, with heterogeneous branching
                # and repeated-state suppression, as in Stage6's BFS.
                max_depth = 3
                for source, visited in ((old, old_visit), (new, new_visit)):
                    seen = set()
                    while source:
                        node = source.pop(0) if isinstance(source, list) else source.popleft()
                        visited.append(node)
                        _, value, depth = node
                        if depth >= max_depth:
                            continue
                        for delta in range(random.Random(value + 100 * depth + trial).randrange(4)):
                            child = ("child", value * 3 + delta, depth + 1)
                            if child in seen:
                                continue
                            seen.add(child)
                            source.append(child)
                self.assertEqual(old_visit, new_visit)

    def test_exact_parity_helper_rejects_unrelated_drift(self):
        spec = importlib.util.spec_from_file_location(
            "i1_parity", ROOT / "scripts/test_i1_artifact_parity.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        content = (ROOT / "src/i1/modules/stage6_planning.py").read_bytes()
        self.assertFalse(module._approved_stage6_bfs_deque(content, content))
        self.assertFalse(module._approved_stage6_bfs_deque(content, content + b"\n# drift"))


if __name__ == "__main__":
    unittest.main()
