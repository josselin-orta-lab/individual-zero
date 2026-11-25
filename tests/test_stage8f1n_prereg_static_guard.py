"""F1N pre-exposure contract tests. No born individuals, no I3 engine imports."""
from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import unittest

from tools import stage8f1n_prereg_static_guard as N


class TestF1NPreregNoExposure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(N.GRID.read_bytes())

    def tampered(self):
        return deepcopy(self.original)

    def test_all_signed_prereg_source_and_grid_blobs(self):
        N.check_files()  # includes native F1J, World, Body, Mind + PH1 source pins
        self.assertEqual(len(self.original["origins"]), 48)
        self.assertEqual(self.original["design_exposure_state"]["birth_steps_performed"], 0)

    def test_scientific_exposure_cannot_be_enabled_by_a_grid_edit(self):
        g = self.tampered()
        g["design_exposure_state"]["scientific_exposure_authorized"] = True
        with self.assertRaisesRegex(ValueError, "no-scientific-exposure"):
            N.verify_grid(g)

    def test_no_seed_reuse_or_reordering(self):
        g = self.tampered()
        g["origins"][0]["seed"] = 202611239701  # M01 already consumed
        with self.assertRaisesRegex(ValueError, "identities/seeds/order"):
            N.verify_grid(g)
        g = self.tampered()
        g["origins"][0], g["origins"][1] = g["origins"][1], g["origins"][0]
        with self.assertRaisesRegex(ValueError, "identities/seeds/order"):
            N.verify_grid(g)

    def test_no_renormalization_of_48_roots_or_worlds(self):
        g = self.tampered()
        g["origins"].pop()
        with self.assertRaisesRegex(ValueError, "identities/seeds/order"):
            N.verify_grid(g)
        g = self.tampered()
        g["origins"][0]["body"][2] = 100
        with self.assertRaisesRegex(ValueError, "world/body/seed"):
            N.verify_grid(g)
        g = self.tampered()
        g["ecologies"][0]["water_stock"] = 99
        with self.assertRaisesRegex(ValueError, "ecology law"):
            N.verify_grid(g)

    def test_real_paid_memory_record_and_read_are_required(self):
        g = self.tampered()
        g["paid_self_confidence_margin"]["real_record_cost"]["memory_items"] = 0
        with self.assertRaisesRegex(ValueError, "memory formula"):
            N.verify_grid(g)
        g = self.tampered()
        g["paid_self_confidence_margin"]["real_read_cost_T6"]["memory_items"] = 0
        with self.assertRaisesRegex(ValueError, "memory formula"):
            N.verify_grid(g)
        g = self.tampered()
        g["paid_self_confidence_margin"]["record_after_actual_native_T5_motor_and_paid_learning"] = False
        with self.assertRaisesRegex(ValueError, "memory formula"):
            N.verify_grid(g)

    def test_margin_gain_and_survival_gate_cannot_change(self):
        g = self.tampered()
        g["paid_self_confidence_margin"]["intervention_gain_kappa"] = 0.8
        with self.assertRaisesRegex(ValueError, "memory formula"):
            N.verify_grid(g)
        g = self.tampered()
        g["adaptive_survival"]["success_threshold"]["max_negative_pairs"] = 1
        with self.assertRaisesRegex(ValueError, "decision threshold"):
            N.verify_grid(g)

    def test_no_discarded_failed_source_or_missing_sham(self):
        g = self.tampered()
        g["scientific_integrity"]["all_48_sources_eligible_and_paid_required"] = False
        with self.assertRaisesRegex(ValueError, "funding gates"):
            N.verify_grid(g)
        g = self.tampered()
        g["native_original_parts_per_root"].remove("masked_t6_t60_sham")
        with self.assertRaisesRegex(ValueError, "original receipts"):
            N.verify_grid(g)

    def test_validator_has_no_native_imports_or_birth_paths(self):
        src = Path(N.__file__).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or "").startswith(("i3", "src.i3")))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith(("i3", "src.i3")))
        # No native transaction or scientific dispatch, even inside a test helper.
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "step" for n in ast.walk(tree)))
        self.assertNotIn("workflow" + "_dispatch(", src.lower())


if __name__ == "__main__":
    unittest.main()
