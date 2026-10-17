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
        self.assertIn("if canonical_controls:", snippet)
        self.assertIn("if canonical_controls else controls", snippet)
        self.assertIn("for baseline in comparable:", snippet)
        # CausalObservation.validate() accepts list- and tuple-backed
        # controls. These older/mixed representations must not crash.
        variations = (
            (("site", "0"),),
            [["site", "0"]],
            [("site", "0")],
            (["site", "0"],),
            (("site", "1"),),
            [["site", "1"]],
        )
        rows = tuple(
            NS(identifier=f"id:{j}", observation_ref=f"physical:{j%3}",
               observed_step=j%4, observation_context=f"context:{j%2}",
               controlled_variables=variations[j])
            for j in range(len(variations))
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
            treated = sorted(treated, key=lambda x: x.identifier)
            controls = sorted(controls, key=lambda x: x.identifier)
            canonical = all(
                type(row.controlled_variables) is tuple
                and all(type(pair) is tuple for pair in row.controlled_variables)
                for group in (treated, controls) for row in group
            )
            index = {}
            if canonical:
                for baseline in controls:
                    key = (baseline.observation_context, baseline.controlled_variables)
                    index.setdefault(key, []).append(baseline)
            for effect in treated:
                comparable = (
                    index.get((effect.observation_context, effect.controlled_variables), ())
                    if canonical else controls
                )
                for baseline in comparable:
                    if (effect.observation_ref == baseline.observation_ref
                        or effect.observed_step == baseline.observed_step
                        or effect.controlled_variables != baseline.controlled_variables
                        or effect.observation_context != baseline.observation_context):
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
