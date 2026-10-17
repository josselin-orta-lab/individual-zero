"""Differential I1 phase-5 numeric witness publication tests, not scientific evidence."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NumericPublicationIndexTests(unittest.TestCase):
    def test_exact_block_equivalence(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "generated"
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"), "--output", str(target)],
                capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            program = r'''
import inspect
from itertools import product
from types import SimpleNamespace as NS
import textwrap
from i1.modules.causal_model import CausalModel

source = inspect.getsource(CausalModel)
start = source.index("        numeric = dict(self._numeric_witnesses)")
end = source.index("        self._published = published", start)
new_block = source[start:end]
old_block = """        numeric = dict(self._numeric_witnesses)
        for witness in sorted(
            self._pending_numeric_witnesses, key=lambda row: row.identifier,
        ):
            witness.validate()
            if (
                witness.identifier in numeric
                or any(
                    prior.transition_event_ref == witness.transition_event_ref
                    for prior in numeric.values()
                )
            ):
                raise ValueError("duplicate published physical numeric witness")
            numeric[witness.identifier] = witness
"""
assert "numeric_transition_refs.add(witness.transition_event_ref)" in new_block
def compile_block(block):
    ns = {}
    exec("def evaluate(self):\n" +
         textwrap.indent(textwrap.dedent(block) + "return numeric\n", "    "), ns)
    return ns["evaluate"]
old = compile_block(old_block)
new = compile_block(new_block)
class Witness:
    def __init__(self, identifier, ref, invalid=False):
        self.identifier = identifier
        self.transition_event_ref = ref
        self.invalid = invalid
    def validate(self):
        if self.invalid:
            raise ValueError("invalid physical witness")
    def __eq__(self, other):
        return (isinstance(other, Witness)
                and (self.identifier, self.transition_event_ref, self.invalid)
                  == (other.identifier, other.transition_event_ref, other.invalid))
    def __repr__(self):
        return f"Witness({self.identifier!r},{self.transition_event_ref!r},{self.invalid!r})"

def attempt(fn, prior, pending):
    state = NS(_numeric_witnesses={row.identifier: row for row in prior},
               _pending_numeric_witnesses=list(pending))
    try:
        return ("ok", fn(state))
    except ValueError as exc:
        return ("error", str(exc))

rows = tuple(Witness(identifier, ref, invalid)
             for identifier in ("id:0", "id:1")
             for ref in ("physical:0", "physical:1")
             for invalid in (False, True))
for prior_len in range(3):
    for prior_rows in product(rows, repeat=prior_len):
        for pending_len in range(4):
            for pending_rows in product(rows, repeat=pending_len):
                assert attempt(old, prior_rows, pending_rows) == attempt(new, prior_rows, pending_rows), (prior_rows, pending_rows)
print("I1_NUMERIC_PUBLICATION_INDEX_EQUIVALENT")
'''
            outcome = subprocess.run(
                [sys.executable, "-c", program],
                env={**os.environ, "PYTHONPATH": str(target)},
                capture_output=True, text=True,
            )
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            self.assertIn("I1_NUMERIC_PUBLICATION_INDEX_EQUIVALENT", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
