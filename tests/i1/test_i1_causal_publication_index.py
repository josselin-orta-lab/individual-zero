"""Differential phase-5 agency publication duplicate checks, not scientific evidence."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CausalPublicationIndexTests(unittest.TestCase):
    def test_agency_duplicate_admission_equivalence(self):
        with TemporaryDirectory() as d:
            output = Path(d) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT/"scripts/build_i1_fork.py"), "--output", str(output)],
                capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
import inspect, textwrap, json, os, statistics, sys, time
from types import SimpleNamespace as NS
from i1.modules.causal_model import CausalModel

source = inspect.getsource(CausalModel)
start = source.index("        agency = dict(self._agency_evidence)")
end = source.index("        numeric = dict(self._numeric_witnesses)", start)
new_block = source[start:end]
old_block = '''        agency = dict(self._agency_evidence)
        for report in sorted(
            self._pending_agency_evidence,
            key=lambda value: (value.observed_t_monde, value.event_ref),
        ):
            if report.event_ref in {v.event_ref for v in agency.values()}:
                raise ValueError("duplicate published physical agency observation")
            agency[report.identifier] = report
'''
assert "agency_event_refs.add(report.event_ref)" in new_block

def compile_block(block):
    body = textwrap.dedent(block)
    namespace = {}
    exec("def evaluate(self):\n" +
         textwrap.indent(body + "return agency\n", "    "), namespace)
    return namespace["evaluate"]

old, new = compile_block(old_block), compile_block(new_block)
def report(identifier, ref, t):
    return NS(identifier=identifier, event_ref=ref, observed_t_monde=t)
cases = [
    ((), ()),
    ((report("prior", "event:1", 1),), ()),
    ((report("prior", "event:1", 1),), (report("new", "event:2", 2),)),
    ((report("prior", "event:1", 1),), (report("new", "event:1", 2),)),
    ((), (report("new:1", "event:1", 2), report("new:2", "event:1", 3))),
    ((), (report("new:1", "event:1", 2), report("new:2", "event:2", 3))),
    ((), (report("new:2", "event:2", 3), report("new:1", "event:1", 2))),
    # Replacing an existing identifier removes only that mapping's old ref.
    ((report("prior", "event:1", 1),),
     (report("prior", "event:2", 2), report("new", "event:1", 3))),
    ((), (report("same", "event:1", 1), report("same", "event:2", 2),
          report("new", "event:1", 3))),
    # If another published identifier still holds the old ref, it stays blocked.
    ((report("prior", "event:1", 1), report("other", "event:1", 1)),
     (report("prior", "event:2", 2), report("new", "event:1", 3))),
]
def attempt(fn, inp):
    try: return "ok", fn(inp)
    except ValueError as e: return "error", str(e)
for prior, pending in cases:
    inp = NS(_agency_evidence={r.identifier:r for r in prior},
             _pending_agency_evidence=list(pending))
    assert attempt(old, inp) == attempt(new, inp), (prior, pending)
# Exhaustively compare short accepted/rejected sequences, including repeated
# mapping identifiers and physical references. No clock or randomness involved.
from itertools import product
possible = tuple((identifier, physical) for identifier in ("id:0", "id:1", "id:2")
                 for physical in ("event:1", "event:2", "event:3"))
for prior_count in range(3):
    for initial_refs in product(("event:1", "event:2"), repeat=prior_count):
        prior = tuple(report(f"id:{i}", ref, i) for i, ref in enumerate(initial_refs))
        for pending_count in range(4):
            for rows in product(possible, repeat=pending_count):
                pending = tuple(report(identifier, ref, i+1)
                                for i, (identifier, ref) in enumerate(rows))
                inp = NS(_agency_evidence={r.identifier:r for r in prior},
                         _pending_agency_evidence=list(pending))
                assert attempt(old, inp) == attempt(new, inp), (prior, pending)
if os.environ.get("I1_AGENCY_PUBLICATION_BENCH") == "1":
    results = []
    for existing, incoming in ((0, 0), (32, 1), (512, 8), (2048, 32), (8192, 64)):
        prior = {f"old:{i:05d}": report(f"old:{i:05d}", f"ref:old:{i}", i)
                 for i in range(existing)}
        pending = [report(f"new:{i:05d}", f"ref:new:{i}", existing + i)
                   for i in range(incoming)]
        old_samples, new_samples = [], []
        for repetition in range(7):
            candidates = [(old, old_samples), (new, new_samples)]
            if repetition % 2:
                candidates.reverse()
            for operation, samples in candidates:
                item = NS(_agency_evidence=prior, _pending_agency_evidence=pending)
                start_ns = time.perf_counter_ns()
                observed = operation(item)
                samples.append(time.perf_counter_ns() - start_ns)
                assert len(observed) == existing + incoming
        former_ns = statistics.median(old_samples)
        current_ns = statistics.median(new_samples)
        results.append({
            "existing_reports": existing, "new_reports": incoming,
            "old_median_us": round(former_ns/1000, 2),
            "new_median_us": round(current_ns/1000, 2),
            "speedup": round(former_ns/current_ns, 2) if current_ns else None,
        })
    print("I1_AGENCY_PUBLICATION_BENCH_JSON " + json.dumps({
        "kind": "synthetic_publication_duplicate_check_only",
        "repetitions": 7, "python": sys.version.split()[0],
        "workloads": results,
    }, sort_keys=True))
print("I1_CAUSAL_PUBLICATION_DUPLICATES_EQUIVALENT")
"""
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH":str(output),
                     "I1_AGENCY_PUBLICATION_BENCH": os.environ.get("I1_AGENCY_PUBLICATION_BENCH", "0")},
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_CAUSAL_PUBLICATION_DUPLICATES_EQUIVALENT", result.stdout)
            if os.environ.get("I1_AGENCY_PUBLICATION_BENCH") == "1":
                self.assertIn("I1_AGENCY_PUBLICATION_BENCH_JSON ", result.stdout)
                print(result.stdout.split("I1_AGENCY_PUBLICATION_BENCH_JSON ", 1)[1].splitlines()[0], flush=True)


if __name__ == "__main__":
    unittest.main()
