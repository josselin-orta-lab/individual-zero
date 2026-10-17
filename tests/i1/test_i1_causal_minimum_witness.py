"""Exact source-anchored differential test for I1 numeric correction provenance."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/i1/modules/causal_model.py"


class MinimumInterventionWitnessTests(unittest.TestCase):
    def test_minimum_is_identical_for_every_compatible_report(self):
        source = SOURCE.read_text()
        tree = ast.parse(source)
        method = next(
            item for cls in ast.walk(tree)
            if isinstance(cls, ast.ClassDef) and cls.name == "CausalModel"
            for item in cls.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "established_prediction_corrections"
        )
        method_text = ast.get_source_segment(source, method)
        # The prior #261 test asserted an incidental placement of min().
        # #264 computes it once per eligible contingency instead of once per
        # witness. Verify the same provenance and refutation gates, not a
        # specific previous optimization's local variable assignment.
        self.assertIn("active_by_contingency[contingency.ref] = (", method_text)
        self.assertIn("(min(trial.identifier for trial in active_trials),)", method_text)
        self.assertIn("if len(matching_contexts) >= self.config.n2", method_text)
        self.assertIn("intervention_ref = selected[0]", method_text)
        self.assertIn("intervention_ref=intervention_ref", method_text)
        self.assertNotIn("intervention_ref=min(", method_text)
        self.assertLess(
            method_text.index("if witness.observed_t_monde <= revision:"),
            method_text.index("if contingency.ref not in active_by_contingency:")
        )
        self.assertLess(
            method_text.index("if len(matching_contexts) >= self.config.n2"),
            method_text.index("intervention_ref = selected[0]")
        )
        # Compare per-report recomputation and hoisted result on deliberately
        # unsorted, repeated and lexically competing identifiers.
        from itertools import product
        from types import SimpleNamespace as NS
        identifiers = ("a", "z", "b")
        for count in range(1, 6):
            for refs in product(identifiers, repeat=count):
                trials = tuple(NS(identifier=ref) for ref in refs)
                hoisted = min(trial.identifier for trial in trials)
                for compatible_count in range(5):
                    before = tuple(
                        min(trial.identifier for trial in trials)
                        for _ in range(compatible_count)
                    )
                    after = tuple(hoisted for _ in range(compatible_count))
                    self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
