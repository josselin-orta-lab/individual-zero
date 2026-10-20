"""Regression: paired experimental fields must track canonical mortal telemetry."""
from pathlib import Path
import ast
import unittest


class TDCounterfactualSchemaTests(unittest.TestCase):
    def test_diagnostic_observation_may_target_a_distinct_memory_signature(self):
        root = Path(__file__).resolve().parents[2]
        module = ast.parse(
            (root / "tools/run_i1_317_td_counterfactual.py").read_text())
        functions = {node.name: node for node in module.body
                     if isinstance(node, ast.FunctionDef)}
        self.assertIn("inspect_signature", [x.arg for x in
                      functions["run"].args.kwonlyargs])
        self.assertIn("--inspect-signature",
                      (root / "tools/run_i1_317_td_counterfactual.py").read_text())
        self.assertIn('else inspect_signature',
                      (root / "tools/run_i1_317_td_counterfactual.py").read_text())

    def test_trajectory_comparison_keys_exist_in_canonical_mortal_runner(self):
        root = Path(__file__).resolve().parents[2]
        runner = ast.parse((root / "tools/run_i1_world_preset.py").read_text())
        experiment = ast.parse(
            (root / "tools/run_i1_317_td_counterfactual.py").read_text())
        keys = {"world_step", "execution", "action_primitive",
                "action_source", "reflex_triggered", "fallback_used",
                "cycles_used", "body", "position", "inventory", "journal_head"}
        tuples = []
        for node in ast.walk(experiment):
            if isinstance(node, ast.Tuple):
                names = [x.value for x in node.elts
                         if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                if "action_source" in names and "fallback_used" in names:
                    tuples.append(names)
        self.assertEqual(len(tuples), 2)
        self.assertTrue(all(set(t).issubset(keys) for t in tuples))
        # The actual mortal observer emits every compared field.
        words = (root / "tools/run_i1_world_preset.py").read_text()
        for key in keys:
            self.assertIn('"' + key + '":', words)
        self.assertNotIn('"execution", "source", "fallback_used"',
                         (root / "tools/run_i1_317_td_counterfactual.py").read_text())


if __name__ == "__main__":
    unittest.main()
