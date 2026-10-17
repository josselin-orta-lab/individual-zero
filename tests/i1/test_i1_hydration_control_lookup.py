"""Behavioral differential tests for hydration control-group lookup."""
from itertools import product
from types import SimpleNamespace as NS
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "src/i1/modules/causal_model.py"

class HydrationControlLookupTests(unittest.TestCase):
    def test_first_matched_physical_pair_equivalence(self):
        source = SOURCE.read_text()
        method = next(
            item for cls in ast.walk(ast.parse(source))
            if isinstance(cls, ast.ClassDef) and cls.name == "CausalModel"
            for item in cls.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "_lived_hydration_hypothesis_review"
        )
        snippet = ast.get_source_segment(source, method)
        self.assertIn("controls_by_context.setdefault(key, []).append(baseline)", snippet)
        self.assertIn("for baseline in controls_by_context.get(", snippet)
        rows = tuple(
            NS(identifier=f"id:{j}", observation_ref=f"physical:{j%2}",
               observed_step=j%3, observation_context=f"context:{j%2}",
               controlled_variables=(("site", f"{j%2}"),))
            for j in range(4)
        )
        def old(treated, controls):
            for effect in sorted(treated, key=lambda x: x.identifier):
                for baseline in sorted(controls, key=lambda x: x.identifier):
                    if (effect.observation_ref == baseline.observation_ref
                        or effect.observed_step == baseline.observed_step
                        or effect.controlled_variables != baseline.controlled_variables
                        or effect.observation_context != baseline.observation_context):
                        continue
                    return effect.identifier, baseline.identifier
            return None
        def new(treated, controls):
            controls = sorted(controls, key=lambda x: x.identifier)
            index = {}
            for baseline in controls:
                key = (baseline.observation_context, baseline.controlled_variables)
                index.setdefault(key, []).append(baseline)
            for effect in sorted(treated, key=lambda x: x.identifier):
                for baseline in index.get(
                    (effect.observation_context, effect.controlled_variables), ()
                ):
                    if (effect.observation_ref == baseline.observation_ref
                        or effect.observed_step == baseline.observed_step):
                        continue
                    return effect.identifier, baseline.identifier
            return None
        for t in range(4):
            for treated in product(rows, repeat=t):
                for c in range(4):
                    for controls in product(rows, repeat=c):
                        self.assertEqual(old(treated, controls), new(treated, controls))

if __name__ == "__main__":
    unittest.main()
