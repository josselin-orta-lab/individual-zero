"""Issue #136: assert current I1 has no first-person water learning path.

These are diagnostics of an *existing* model, not scientific evidence of learning.
"""
from __future__ import annotations

import inspect
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class I1WaterAcquisitionReadiness(unittest.TestCase):
    def test_current_model_is_frozen_external_and_food_only(self):
        # One isolated namespace per test avoids stale sys.modules from a
        # deleted previous generated tree (the first CI run exposed this).
        with TemporaryDirectory() as directory:
            target = Path(directory) / "generated"
            generate(target)
            sys.path.insert(0, str(target))
            try:
                from i1.experimental.stage6_visible_delta_shadow import (
                    ACTIONS, SOURCE_SCOPE, ShadowVisibleDeltaModel, _action_key,
                )
                from i1.interfaces import PrimitiveCommand
                from i1.equipment import FrozenTableEquipment
                from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime

                self.assertEqual(ACTIONS, ("MOVE_E", "COLLECT_B"))
                self.assertEqual(SOURCE_SCOPE, "external_lab")
                self.assertIsNone(_action_key(PrimitiveCommand("boire")))
                self.assertIsNone(_action_key(
                    PrimitiveCommand("se_deplacer", {"direction": "north"})))
                self.assertFalse(hasattr(ShadowVisibleDeltaModel, "learn_from_life"))
                self.assertFalse(hasattr(ShadowVisibleDeltaModel, "update_from_outcome"))
                self.assertFalse(hasattr(FrozenTableEquipment, "learn_from_life"))
                source = inspect.getsource(ExperimentalI1Stage12Runtime._propose_for_cycle)
                self.assertIn('goal_for_planning.goal_type != "eat"', source)
                self.assertIn('if "berry_b" in state.current_resources:', source)
                self.assertNotIn('PrimitiveCommand("boire")', source)
                constructor = inspect.getsource(ExperimentalI1Stage12Runtime.__init__)
                self.assertIn('i1_model.source_scope != "external_lab"', constructor)
                self.assertIn("self._i1_model = i1_model", constructor)
                self.assertFalse(hasattr(ExperimentalI1Stage12Runtime,
                                         "learn_water_from_life"))
            finally:
                sys.path.remove(str(target))


if __name__ == "__main__":
    unittest.main()
