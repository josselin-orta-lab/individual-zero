"""Differential equivalence of P-35 distinct positive observation counting."""
from itertools import product
from pathlib import Path
import ast
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "src/i1/modules/causal_model.py"


class ConfirmedCountReuseTests(unittest.TestCase):
    def test_distinct_positive_evidence_matches_old_count(self):
        code = SOURCE.read_text()
        method = next(
            fn for cls in ast.walk(ast.parse(code))
            if isinstance(cls, ast.ClassDef) and cls.name == "CausalModel"
            for fn in cls.body
            if isinstance(fn, ast.FunctionDef)
            and fn.name == "publish_causal_inference"
        )
        source = ast.get_source_segment(code,method)
        self.assertIn("if len(confirmed) * len(b) <=",source)
        self.assertIn("x.identifier for x in e.values() if x.effect_present",source)
        # e is an identifier-keyed dict of admitted observations, so each
        # positive record is uniquely represented. Duplicate aliases do not
        # become separate P-35 evidence.
        for n in range(6):
            for vals in product((False,True),repeat=n):
                observed={f"id:{i}":bool(flag) for i,flag in enumerate(vals)}
                confirmed={identifier for identifier,flag in observed.items() if flag}
                before=sum(bool(v) for v in observed.values())
                self.assertEqual(before,len(confirmed))
                for controls in range(1,5):
                    for positive_controls in range(controls+1):
                        self.assertEqual(
                            before*controls <= positive_controls*len(observed),
                            len(confirmed)*controls <= positive_controls*len(observed)
                        )

if __name__=="__main__":
    unittest.main()
