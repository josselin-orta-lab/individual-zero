"""Stage6 FIFO-equivalence and scaling checks; no cognitive oracle inputs."""
import importlib.util
from collections import deque
from pathlib import Path
import json
import os
import random
import statistics
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

    def test_fifo_cost_microbenchmark_optional(self):
        """Informational CPU-only benchmark; timings cannot fail the CI."""
        if os.environ.get("I1_STAGE6_BFS_BENCH") != "1":
            return
        measurements = []
        for size in (32, 256, 1024, 4096, 8192):
            old_ns, new_ns = [], []
            expected = size * (size - 1) // 2
            for iteration in range(9):
                cases = [("list", old_ns), ("deque", new_ns)]
                if iteration % 2:
                    cases.reverse()
                for kind, samples in cases:
                    q = list(range(size)) if kind == "list" else deque(range(size))
                    total = 0
                    start = time.perf_counter_ns()
                    while q:
                        total += q.pop(0) if kind == "list" else q.popleft()
                    elapsed = time.perf_counter_ns() - start
                    self.assertEqual(total, expected)
                    samples.append(elapsed / size)
            old = statistics.median(old_ns)
            new = statistics.median(new_ns)
            measurements.append({
                "queued_states": size,
                "old_ns_per_dequeue": round(old, 2),
                "deque_ns_per_dequeue": round(new, 2),
                "ratio": round(old / new, 2) if new else None,
            })
        print("I1_STAGE6_BFS_BENCH_JSON " + json.dumps({
            "kind": "isolated_FIFO_CPU_microbenchmark_not_full_planning",
            "python": os.sys.version.split()[0],
            "repetitions": 9,
            "workloads": measurements,
        }, sort_keys=True), flush=True)

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
