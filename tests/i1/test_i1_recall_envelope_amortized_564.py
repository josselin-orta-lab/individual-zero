"""#564: informative work and amortization benchmark of the L1-only envelope.

No cognitive code is changed. No timing threshold gates CI. This measures
the cost of building and updating a derived selector as well as using it.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

PROGRAM = r'''
import json
import runpy
from statistics import median
from time import perf_counter_ns
from i1.modules.memory import EpisodicMemory

# The benchmark uses the EXACT L1 candidate algorithm already approved by
# #569, without duplicating a subtly different design.
program = runpy.run_path(
    "tests/i1/test_i1_recall_envelope_feasibility_564.py")["PROGRAM"]
marker = "\nmetrics = []\n"
assert program.count(marker) == 1, "candidate reference changed"
namespace = {"__name__": "i1_recall_envelope_564_reference"}
exec(program.split(marker, 1)[0], namespace)
Envelope = namespace["ConservativeEnvelope"]
build = namespace["build"]
config = namespace["config"]
context = namespace["context"]
subset = namespace["subset"]

results = []
for kind in ("canonical", "low-relevance", "all-eligible"):
    cfg = config(kind)
    for n in (32, 512, 2048):
        source = build(n, cfg)
        timed = []
        for _ in range(5):
            start = perf_counter_ns()
            index = Envelope(cfg, source._episodes)
            elapsed = perf_counter_ns() - start
            assert index.trusted
            timed.append(elapsed)
        build_ns = int(median(timed))
        t = n + 200
        for label, st in (
            ("none", context()),
            ("ancient-goal", context(goal="goal:ancient")),
            ("ancient-source", context(refs=("src:0",))),
            ("shared-source", context(refs=("common:3",))),
        ):
            original = source.recall(st=st, t_monde=t)
            full_times = []
            selected_times = []
            candidate_counts = []
            for _ in range(9):
                start = perf_counter_ns()
                full = source.recall(st=st, t_monde=t)
                full_times.append(perf_counter_ns() - start)
                start = perf_counter_ns()
                candidates = index.select(st=st, t_monde=t)
                reduced = subset(source, candidates).recall(
                    st=st, t_monde=t)
                selected_times.append(perf_counter_ns() - start)
                candidate_counts.append(len(candidates))
                assert full == reduced == original
            full_median = int(median(full_times))
            indexed_median = int(median(selected_times))
            saving = full_median - indexed_median
            results.append({
                "configuration": kind,
                "episodes": n,
                "context": label,
                "candidates": candidate_counts[-1],
                "build_ns": build_ns,
                "exhaustive_median_ns": full_median,
                "indexed_median_ns": indexed_median,
                "break_even_queries_if_positive": (
                    (build_ns + saving - 1) // saving if saving > 0 else None),
            })

        # True incremental append measurement; no rebuilding the whole index.
        fresh = Envelope(cfg)
        times = []
        for episode in source._episodes:
            start = perf_counter_ns()
            fresh.append(episode)
            times.append(perf_counter_ns() - start)
        assert fresh.trusted
        assert fresh.select(st=context(), t_monde=t) == index.select(
            st=context(), t_monde=t)
        # A newly closed episode can become relevant even after a cold import.
        cold = EpisodicMemory(cfg, atomic_world_step_length_boundary=True)
        cold.restore_causal_state(source.export_causal_state())
        rebuilt = Envelope(cfg, cold._episodes)
        assert rebuilt.trusted
        for st in (
            None, context(goal="goal:ancient"),
            context(refs=("src:0",)),
        ):
            candidates = rebuilt.select(st=st, t_monde=t)
            assert subset(cold, candidates).recall(
                st=st, t_monde=t) == cold.recall(st=st, t_monde=t)
        results.append({
            "configuration": kind, "episodes": n,
            "context": "incremental-maintenance",
            "candidates": len(fresh.records),
            "build_ns": build_ns,
            "append_median_ns": int(median(times)),
            "append_total_ns": sum(times),
            "cold_rederivation_exact": True,
        })
print("I1_RECALL_AMORTIZED_L1_564=" + json.dumps({
    "evidence": "synthetic-L1-only",
    "timing_informational": True,
    "engine_modified": False,
    "index_is_noncausal": True,
    "rows": results,
}, sort_keys=True))
'''


class RecallEnvelopeAmortized564(unittest.TestCase):
    def test_generated_i1_profile_and_exact_output(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], cwd=ROOT,
                capture_output=True, text=True, timeout=180)
            self.assertEqual(built.returncode, 0,
                             built.stdout + built.stderr)
            env = dict(os.environ, PYTHONPATH=str(generated))
            result = subprocess.run(
                [sys.executable, "-c", PROGRAM], cwd=ROOT,
                env=env, capture_output=True, text=True, timeout=240)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
            rows = [s for s in result.stdout.splitlines()
                    if s.startswith("I1_RECALL_AMORTIZED_L1_564=")]
            self.assertEqual(len(rows), 1, result.stdout)
            data = json.loads(rows[0].split("=", 1)[1])
            self.assertEqual(data["evidence"], "synthetic-L1-only")
            self.assertTrue(data["timing_informational"])
            self.assertFalse(data["engine_modified"])
            self.assertTrue(data["index_is_noncausal"])
            self.assertEqual(len(data["rows"]), 3 * 3 * 5)
            for row in data["rows"]:
                self.assertGreaterEqual(row["build_ns"], 0)
                self.assertGreaterEqual(row["candidates"], 0)
                self.assertLessEqual(row["candidates"], row["episodes"])
                if row["context"] == "incremental-maintenance":
                    self.assertTrue(row["cold_rederivation_exact"])
                    self.assertGreaterEqual(row["append_total_ns"], 0)
                else:
                    self.assertGreaterEqual(row["exhaustive_median_ns"], 0)
                    self.assertGreaterEqual(row["indexed_median_ns"], 0)
            print(rows[0])


if __name__ == "__main__":
    unittest.main()
