"""Differential I1 source-alias admission: exact extracted publication block."""
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
from types import SimpleNamespace as NS
import os
import statistics
import textwrap
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/i1/modules/causal_model.py"
SAFETY_PREDICATES = frozenset({"toxic_item"})

@dataclass(frozen=True)
class CausalObservation:
    identifier: str
    contingency_ref: str
    observation_ref: str
    observed_step: int
    predicate: str = "toxic_item"
    subject_ref: str = "berry_a"
    application_context: str = "global"
    episode_ref: str = "episode:0"
    effect_present: bool = False

@dataclass(frozen=True)
class CanonicalContingency:
    ref: str
    version: int
    predicate: str
    subject_ref: str
    context_signature: str
    causal_status: str
    safety_status: str
    evidence_refs: tuple
    harmful_episodes: tuple
    harmless_episodes: tuple

class PhysicalObservationIndexTests(unittest.TestCase):
    def test_actual_source_matches_original_admission_and_failure(self):
        raw = SOURCE.read_text()
        # Include the hoisted index initialization in the extracted block.
        # Otherwise we would compare a truncated implementation to the baseline.
        begin = raw.index("        # Most publication cycles have zero or one new observation. Build")
        end = raw.index("        byref = defaultdict(list)", begin)
        current = raw[begin:end]
        setup = "        # Most publication cycles have zero or one new observation. Build\n        # this transient index only for batches large enough to amortize it.\n        # It is not persistent evidence, memory or another causal owner.\n        index_physical_sources = len(self._pending_causal_observations) >= 3\n        first_physical: dict[tuple[str, str], CausalObservation] = {}\n        if index_physical_sources:\n            for prior in observations.values():\n                first_physical.setdefault(\n                    (prior.contingency_ref, prior.observation_ref), prior\n                )\n\n"
        scan_old = "            same_physical = (\n                v for v in observations.values()\n                if v.contingency_ref == o.contingency_ref\n                and v.observation_ref == o.observation_ref\n            )\n            for existing in same_physical:"
        scan_new = "            # A colliding identifier may replace an earlier physical\n            # source in the mapping. Keep exact old scan semantics for the\n            # rest of this batch instead of retaining a stale indexed row.\n            if index_physical_sources and o.identifier in observations:\n                index_physical_sources = False\n            if index_physical_sources:\n                first = first_physical.get((o.contingency_ref, o.observation_ref))\n                same_physical = (first,) if first is not None else ()\n            else:\n                same_physical = (\n                    v for v in observations.values()\n                    if v.contingency_ref == o.contingency_ref\n                    and v.observation_ref == o.observation_ref\n                )\n            for existing in same_physical:"
        insert_old = "                credits.add(key)\n                observations[o.identifier] = o\n                published[o.contingency_ref] = old"
        insert_new = "                credits.add(key)\n                observations[o.identifier] = o\n                if index_physical_sources:\n                    first_physical.setdefault(\n                        (o.contingency_ref, o.observation_ref), o\n                    )\n                published[o.contingency_ref] = old"
        self.assertEqual(current.count(setup), 1)
        self.assertEqual(current.count(scan_new), 1)
        self.assertEqual(current.count(insert_new), 1)
        previous = (current.replace(setup, "", 1)
                           .replace(scan_new, scan_old, 1)
                           .replace(insert_new, insert_old, 1))
        def compile_admission(block):
            namespace = globals().copy()
            body = textwrap.dedent(block)
            exec("def admit(self, observations, credits, published):\n"
                 + textwrap.indent(body + "return observations, credits, published\n", "    "),
                 namespace)
            return namespace["admit"]
        old = compile_admission(previous)
        new = compile_admission(current)
        def evaluate(fn, historical, pending, dangling=False):
            observations = {o.identifier: o for o in historical}
            credits = {(o.contingency_ref, o.observation_ref, "observation")
                       for o in historical}
            if dangling:
                credits.add(("c:1", "p:1", "observation"))
            model = NS(_pending_causal_observations=list(pending),
                       config=NS(causal_predicates=("hydration_effect",)))
            try:
                return ("accepted", fn(model, observations, credits, {}))
            except ValueError as exc:
                return ("rejected", str(exc))
        rows = (
            CausalObservation("id:a", "c:0", "p:0", 1),
            CausalObservation("id:b", "c:0", "p:0", 1),
            CausalObservation("id:c", "c:0", "p:0", 2),
            CausalObservation("id:a", "c:0", "p:1", 2),
            CausalObservation("id:d", "c:1", "p:0", 3),
            CausalObservation("id:e", "c:1", "p:1", 4),
            CausalObservation("id:f", "c:0", "p:0", 1,
                              episode_ref="episode:other"),
            CausalObservation("id:g", "c:0", "p:2", 3,
                              predicate="hydration_effect"),
        )
        # Exhaustive short batches test the <=2 fallback, indexed >=3 case,
        # conflicting physical aliases, a replaced mapping identifier,
        # duplicate published IDs and dangling physical credits.
        count = 0
        for history_size in range(3):
            for history in product(rows[:6], repeat=history_size):
                for batch_size in range(4):
                    for pending in product(rows, repeat=batch_size):
                        for dangling in (False, True):
                            a = evaluate(old, history, pending, dangling)
                            b = evaluate(new, history, pending, dangling)
                            self.assertEqual(a, b, (history, pending, dangling))
                            count += 1
        self.assertGreater(count, 10000)

        # Optional CPU-only microbenchmark. Never evidence of lived learning.
        if os.environ.get("I1_PHYSICAL_ALIAS_BENCH") == "1":
            cases = []
            for history_size, batch_size in ((0, 0), (512, 1),
                                             (512, 8), (4096, 48)):
                history = tuple(CausalObservation(
                    f"prior:{i}", "c:0", f"old:{i}", i+1
                ) for i in range(history_size))
                pending = tuple(CausalObservation(
                    f"fresh:{i}", "c:0", f"fresh:{i}", history_size+i+1
                ) for i in range(batch_size))
                times = ([], [])
                for repetition in range(7):
                    for order in ((0, 1) if repetition % 2 == 0 else (1, 0)):
                        start = time.perf_counter_ns()
                        result = evaluate((old, new)[order], history, pending)
                        times[order].append(time.perf_counter_ns()-start)
                        self.assertEqual(result[0], "accepted")
                cases.append((history_size, batch_size,
                              round(statistics.median(times[0])/1e3, 2),
                              round(statistics.median(times[1])/1e3, 2)))
            print("I1_PHYSICAL_ALIAS_INDEX_BENCH_CPU_SYNTHETIC", cases, flush=True)

if __name__ == "__main__":
    unittest.main()
