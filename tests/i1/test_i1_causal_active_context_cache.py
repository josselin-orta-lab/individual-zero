"""Differential query-local active intervention eligibility cache, I1 only."""
import ast
from itertools import product
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "src/i1/modules/causal_model.py"


class ActiveContextCacheTests(unittest.TestCase):
    def test_current_source_and_differential_queries(self):
        source = SOURCE.read_text()
        method = next(
            f for cls in ast.walk(ast.parse(source))
            if isinstance(cls, ast.ClassDef) and cls.name == "CausalModel"
            for f in cls.body
            if isinstance(f, ast.FunctionDef)
            and f.name == "established_prediction_corrections"
        )
        actual = ast.get_source_segment(source, method)
        self.assertIn("active_by_contingency[contingency.ref]", actual)
        self.assertIn("if contingency.ref not in active_by_contingency:", actual)
        def original(trials, revision, n2):
            active = tuple(t for t in trials if t.observed_step > revision)
            if len({t.context_signature for t in active}) < n2:
                return None
            return min(t.identifier for t in active)
        def cached(sequences, trials, revision, n2):
            lookup = {}
            outputs = []
            for contingency in sequences:
                if contingency not in lookup:
                    active = tuple(t for t in trials[contingency] if t.observed_step > revision[contingency])
                    lookup[contingency] = (
                        min(t.identifier for t in active)
                        if len({t.context_signature for t in active}) >= n2
                        else None
                    )
                outputs.append(lookup[contingency])
            return tuple(outputs)
        records = tuple(NS(identifier=f"trial:{i}", observed_step=i,
                           context_signature=f"context:{i%2}") for i in range(4))
        for n2 in (1,2,3):
            for count in range(5):
                for indices in product(range(4),repeat=count):
                    trials = tuple(records[i] for i in indices)
                    for boundary in (-1,0,2,5):
                        byref={"A":trials,"B":tuple(reversed(trials))}
                        revisions={"A":boundary,"B":boundary}
                        requests=("A","B","A","A","B")
                        former=tuple(original(byref[ref],boundary,n2) for ref in requests)
                        self.assertEqual(former,cached(requests,byref,revisions,n2))


if __name__ == "__main__":
    unittest.main()
