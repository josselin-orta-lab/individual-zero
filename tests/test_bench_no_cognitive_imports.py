"""The scientific Bench must not import I0, Oracle or technical journal modules."""
from __future__ import annotations

import subprocess
import sys
import unittest


class BenchNoCognitiveImportTests(unittest.TestCase):
    def test_bench_constructs_and_measures_with_all_i0_modules_blocked(self):
        sample = r'''
import importlib.abc
import sys

class BlockCognitiveAndOracle(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "i0" or fullname in {
            "lab.journal", "lab.journal_views", "lab.world",
            "lab.stage2_runtime", "lab.oracle", "lab.independent_journal_audit",
        }:
            raise ImportError("illegal Bench import: " + fullname)
        return None

sys.meta_path.insert(0, BlockCognitiveAndOracle())
from lab.bench import EvaluationBench
from lab.evaluation_trace import EvaluationTrace
trace = EvaluationTrace()
bench = EvaluationBench(trace=trace)
bench.count_safety_block(data={"allowed_observation": True})
bench.count_lethal_transition(data={"t_monde": 1})
assert bench.metrics.safety_blocks == 1
assert bench.metrics.lethal_transitions == 1
assert [entry.kind for entry in trace.records] == ["safety_block", "lethal_transition"]
for forbidden in ("i0", "lab.journal", "lab.journal_views",
                  "lab.world", "lab.oracle", "lab.independent_journal_audit"):
    assert forbidden not in sys.modules, forbidden
print("scientific_bench_without_i0_oracle_or_journal:OK")
'''
        proc = subprocess.run(
            [sys.executable, "-c", sample],
            text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("scientific_bench_without_i0_oracle_or_journal:OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
