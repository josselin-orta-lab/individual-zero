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

    def test_visible_single_creature_justifies_only_integrity_loss(self):
        from dataclasses import replace
        base = capture_with_creature(creature_direction="east")
        capture = replace(
            base, t_monde=2,
            body={**base.body, "integrity": 88.0},
        )
        comparison = comparator().compare(
            option_ref="night:wait", sent_t_monde=1,
            deadline_t_monde=2,
            predictions=(PredictedConsequence("integrity", 100.0, 0.0),),
            capture=capture,
            command=PrimitiveCommand("attendre"),
        )
        self.assertEqual(comparison.status, "nonconforming")
        self.assertEqual(comparison.attribution, "world_justified")
        gain = comparator().compare(
            option_ref="gain", sent_t_monde=1,
            deadline_t_monde=2,
            predictions=(PredictedConsequence("integrity", 70.0, 0.0),),
            capture=capture, command=PrimitiveCommand("attendre"),
        )
        self.assertEqual(gain.attribution, "uncertain")
        no_creature = replace(
            capture, adjacent=tuple(
                replace(cell, creature=False) for cell in capture.adjacent
            ),
        )
        hidden = comparator().compare(
            option_ref="hidden", sent_t_monde=1,
            deadline_t_monde=2,
            predictions=(PredictedConsequence("integrity", 100.0, 0.0),),
            capture=no_creature, command=PrimitiveCommand("attendre"),
        )
        self.assertEqual(hidden.attribution, "uncertain")

    def test_world_obstacle_attribution_requires_matching_displacement(self):
        from dataclasses import replace

        base = capture_with_creature(creature_direction=None)
        blocked = replace(
            base,
            t_monde=2,
            adjacent=tuple(
                replace(cell, passable=False) if cell.direction == "east" else cell
                for cell in base.adjacent
            ),
        )

        def compare(*predictions):
            return comparator().compare(
                option_ref="move:east",
                sent_t_monde=1,
                deadline_t_monde=2,
                predictions=predictions,
                capture=blocked,
                command=PrimitiveCommand(
                    "se_deplacer", {"direction": "east"},
                ),
            )

        # The expected eastward displacement was blocked by an accessible
        # impassable eastern cell, so a world contribution is defensible.
        blocked_forward = compare(PredictedConsequence("position_x", 3.0, 0.0))
        self.assertEqual(blocked_forward.status, "nonconforming")
        self.assertEqual(blocked_forward.attribution, "world_justified")

        # That same obstacle cannot explain a sideways displacement,
        # an opposite predicted direction, an excessive missed distance,
        # or multiple deviations.
        for predictions in (
            (PredictedConsequence("position_y", 3.0, 0.0),),
            (PredictedConsequence("position_x", 1.0, 0.0),),
            (PredictedConsequence("position_x", 4.0, 0.0),),
            (
                PredictedConsequence("position_x", 3.0, 0.0),
                PredictedConsequence("position_y", 3.0, 0.0),
            ),
        ):
            with self.subTest(predictions=predictions):
                result = compare(*predictions)
                self.assertEqual(result.status, "nonconforming")
                self.assertEqual(result.attribution, "uncertain")

        # Moving a cell in the opposite direction cannot be explained by
        # the eastward obstacle, even if the *predicted* east destination is
        # still farther east than the observed west-shifted coordinate.
        opposite_capture = replace(blocked, x=blocked.x - 1)
        opposite = comparator().compare(
            option_ref="move:east:opposite",
            sent_t_monde=1, deadline_t_monde=2,
            predictions=(PredictedConsequence("position_x", 3.0, 0.0),),
            capture=opposite_capture,
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        self.assertEqual(opposite.status, "nonconforming")
        self.assertEqual(opposite.attribution, "uncertain")

        accessible = replace(
            blocked,
            adjacent=tuple(
                replace(cell, passable=True) for cell in blocked.adjacent
            ),
        )
        unblocked = comparator().compare(
            option_ref="move:east",
            sent_t_monde=1,
            deadline_t_monde=2,
            predictions=(PredictedConsequence("position_x", 3.0, 0.0),),
            capture=accessible,
            command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        )
        self.assertEqual(unblocked.attribution, "uncertain")

    def test_northward_blockage_explains_only_northward_difference(self):
        from dataclasses import replace

        base = capture_with_creature(creature_direction=None)
        blocked = replace(
            base,
            t_monde=2,
            adjacent=tuple(
                replace(cell, passable=False) if cell.direction == "north" else cell
                for cell in base.adjacent
            ),
        )
        result = comparator().compare(
            option_ref="move:north", sent_t_monde=1, deadline_t_monde=2,
            predictions=(PredictedConsequence("position_y", 1.0, 0.0),),
            capture=blocked,
            command=PrimitiveCommand("se_deplacer", {"direction": "north"}),
        )
        self.assertEqual(result.attribution, "world_justified")

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
