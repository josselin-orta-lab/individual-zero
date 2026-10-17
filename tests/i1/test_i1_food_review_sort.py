"""Differential ordering check for I1 food hypothesis review sorting."""
from itertools import product
from types import SimpleNamespace as NS
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "src/i1/modules/causal_model.py"


class FoodReviewSortTests(unittest.TestCase):
    def test_first_admissible_pair_order_is_unchanged(self):
        source = SOURCE.read_text()
        method = next(
            item for cls in ast.walk(ast.parse(source))
            if isinstance(cls, ast.ClassDef) and cls.name == "CausalModel"
            for item in cls.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "_lived_food_hypothesis_review"
        )
        text = ast.get_source_segment(source, method)
        self.assertIn("sorted_controls = sorted(controls, key=lambda row: row.identifier)", text)
        self.assertIn("for absent in sorted_controls:", text)
        self.assertNotIn("for absent in sorted(controls,", text)

        def accepted(present, absent):
            return (present.observation_ref != absent.observation_ref
                    and present.observed_step != absent.observed_step
                    and present.observation_context == absent.observation_context
                    and present.controlled_variables == absent.controlled_variables)

        def prior(exposed, controls):
            for present in sorted(exposed, key=lambda row: row.identifier):
                for absent in sorted(controls, key=lambda row: row.identifier):
                    if accepted(present, absent):
                        return present.identifier, absent.identifier
            return None

        def current(exposed, controls):
            sorted_controls = sorted(controls, key=lambda row: row.identifier)
            for present in sorted(exposed, key=lambda row: row.identifier):
                for absent in sorted_controls:
                    if accepted(present, absent):
                        return present.identifier, absent.identifier
            return None

        rows = tuple(
            NS(identifier=f"id:{idx}", observation_ref=f"ref:{idx%2}",
               observed_step=idx%3, observation_context=f"context:{idx%2}",
               controlled_variables=(("primitive", "manger"),))
            for idx in range(4)
        )
        for n_exposed in range(4):
            for exposures in product(rows, repeat=n_exposed):
                for n_control in range(4):
                    for controls in product(rows, repeat=n_control):
                        self.assertEqual(prior(exposures, controls),
                                         current(exposures, controls))


if __name__ == "__main__":
    unittest.main()
