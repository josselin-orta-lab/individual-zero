"""Stage-9 causal configuration is part of replay identity (INV-01/33).

Changing the declared treatment/control mapping or P-35/P-36 thresholds while
reusing a human-readable configuration version must never silently reinterpret
a restored causal history. Stage 8 is unaffected by this Stage-9-only test.
"""
from __future__ import annotations

import unittest

from i0.modules.causal_model import CausalModel, CausalModelConfig


def make_model(*, pairs=(), n1=2, n2=2):
    return CausalModel(CausalModelConfig(
        version="stage9-causal-contract-v1",
        n1=n1, n2=n2, n_sec=2, m_sec=2,
        causal_predicates=("food_energy_effect",),
        food_control_pairs=pairs,
    ))


class Stage9CausalConfigContractTests(unittest.TestCase):
    def test_identical_config_restores_exactly(self):
        original = make_model(pairs=(("berry_b", "berry_a"),))
        original.record_applied_food_exposure(
            t_monde=1, resource_kind="berry_a", option_ref="option:1",
            motive_ref="goal:food", integrity_before=95.0,
        )
        snapshot = original.export_causal_state()
        twin = make_model(pairs=(("berry_b", "berry_a"),))
        twin.restore_causal_state(snapshot)
        self.assertEqual(twin.export_causal_state(), snapshot)

    def test_same_version_but_changed_controls_is_not_the_same_causal_state(self):
        original = make_model(pairs=(("berry_b", "berry_a"),))
        snapshot = original.export_causal_state()
        receiving = make_model(pairs=())
        before = receiving.export_causal_state()
        with self.assertRaises(ValueError):
            receiving.restore_causal_state(snapshot)
        self.assertEqual(receiving.export_causal_state(), before)

    def test_same_version_but_changed_thresholds_cannot_restore(self):
        original = make_model(n1=2, n2=2)
        snapshot = original.export_causal_state()
        receiving = make_model(n1=3, n2=2)
        before = receiving.export_causal_state()
        with self.assertRaises(ValueError):
            receiving.restore_causal_state(snapshot)
        self.assertEqual(receiving.export_causal_state(), before)


if __name__ == "__main__":
    unittest.main()
