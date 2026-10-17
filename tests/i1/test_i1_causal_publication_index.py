"""Differential phase-5 agency publication duplicate checks, not scientific evidence."""
from pathlib import Path
from tempfile import TemporaryDirectory
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
import inspect, textwrap
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
]
for prior, pending in cases:
    inp = NS(_agency_evidence={r.identifier:r for r in prior},
             _pending_agency_evidence=list(pending))
    def attempt(fn):
        try: return "ok", fn(inp)
        except ValueError as e: return "error", str(e)
    assert attempt(old) == attempt(new), (prior, pending)
print("I1_CAUSAL_PUBLICATION_DUPLICATES_EQUIVALENT")
"""
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH":str(output)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_CAUSAL_PUBLICATION_DUPLICATES_EQUIVALENT", result.stdout)


if __name__ == "__main__":
    unittest.main()
