"""P-47 / §9.6: finite tolerances, window, non-oracle attribution."""
import unittest
from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand
from i0.modules.agency_comparator import AgencyComparator, AgencyComparatorConfig
from test_action_control import capture_with_creature


def comparator():
    return AgencyComparator(AgencyComparatorConfig(
        version="p47-test-v1",
        tolerances={name: 0.0 for name in (
            "position_x", "position_y", "energy", "food", "water", "integrity"
        )},
        max_observation_window_steps=2,
    ))


class AgencyComparatorStage9Tests(unittest.TestCase):
    def test_earlier_capture_does_not_verify(self):
        c = comparator()
        p = PredictedConsequence("position_x", 3.0, 0.0)
        self.assertIsNone(c.compare(
            option_ref="a", sent_t_monde=1, deadline_t_monde=3,
            predictions=(p,), capture=capture_with_creature(creature_direction=None),
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        ))

    def test_conforming_prediction_is_compatible_not_causal_proof(self):
        from dataclasses import replace
        c = comparator()
        capture = replace(capture_with_creature(creature_direction=None), t_monde=2)
        result = c.compare(
            option_ref="a", sent_t_monde=1, deadline_t_monde=2,
            predictions=(PredictedConsequence("position_x", 2.0, 0.0),),
            capture=capture, command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        self.assertEqual(result.status, "conforming")
        self.assertEqual(result.attribution, "self_compatible")
        self.assertEqual(c.compatible_candidates((result,)), ("a",))

    def test_nonconforming_ambiguous_attribution(self):
        from dataclasses import replace
        c = comparator()
        capture = replace(capture_with_creature(creature_direction=None), t_monde=2)
        result = c.compare(
            option_ref="a", sent_t_monde=1, deadline_t_monde=2,
            predictions=(PredictedConsequence("integrity", 90.0, 0.0),),
            capture=capture, command=PrimitiveCommand("attendre"),
        )
        self.assertEqual(result.status, "nonconforming")
        self.assertEqual(result.attribution, "uncertain")

    def test_window_closure_is_not_retroactive(self):
        from dataclasses import replace
        c = comparator()
        capture = replace(capture_with_creature(creature_direction=None), t_monde=4)
        result = c.compare(
            option_ref="a", sent_t_monde=1, deadline_t_monde=3,
            predictions=(PredictedConsequence("position_x", 2.0, 0.0),),
            capture=capture, command=PrimitiveCommand("attendre"),
        )
        self.assertEqual(result.status, "indeterminable")
        self.assertEqual(result.effects[0]["status"], "expected_effect_missing")


if __name__ == "__main__":
    unittest.main()
