"""Negative and positive *software* semantics for GA-SPATIAL-01.

These fixtures DO NOT show any autonomously executed blocked-world command or
a validated attribution-bias detector. The integrated canonical auditor must
later verify actual physical admission, intent, cues, receipts and UC.
"""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import PerceivedCell, PerceptualCapture
from i0.modules.stage12_spatial_cue_policy import evaluate_spatial_goal_cue


def capture(*, t=1, x=2, y=2, passable=False,
            direction="east", water=True, berries=()):
    cell = PerceivedCell(
        direction=direction,
        x=x + (1 if direction == "east" else -1 if direction == "west" else 0),
        y=y + (1 if direction == "south" else -1 if direction == "north" else 0),
        passable=passable, water_source=water,
        resources=tuple(berries), creature=False,
    )
    return PerceptualCapture(
        t_monde=t, x=x, y=y,
        body={"food": 50.0, "water": 40.0, "energy": 55.0,
              "integrity": 100.0},
        current_water_source=False, current_resources=(),
        adjacent=(cell,),
    )


def judge(before=None, after=None, *, direction="east",
          target=(3, 2), kind="water", executed=True):
    return evaluate_spatial_goal_cue(
        pre=capture() if before is None else before,
        post=capture(t=2) if after is None else after,
        command=PrimitiveCommand("se_deplacer", {"direction": direction}),
        target_x=target[0], target_y=target[1],
        target_kind=kind, admitted_and_executed=executed,
    )


class SpatialCueContractTests(unittest.TestCase):
    def test_world_requires_witnessed_blocked_target_direction(self):
        result = judge()
        self.assertEqual(result.agency, "world")
        self.assertEqual(result.reason,
                         "witnessed_goal_relevant_blocked_direction")

    def test_self_requires_witnessed_efferent_displacement(self):
        result = judge(before=capture(passable=True),
                       after=capture(t=2, x=3, y=2))
        self.assertEqual(result.agency, "self")

    def test_no_command_admission_never_world(self):
        self.assertEqual(judge(executed=False).agency, "unknown")

    def test_unrelated_target_does_not_blame_world(self):
        self.assertEqual(judge(target=(3, 3)).agency, "unknown")

    def test_opposite_direction_does_not_blame_world(self):
        self.assertEqual(judge(direction="west").agency, "unknown")

    def test_unseen_resource_not_a_goal_target(self):
        self.assertEqual(judge(before=capture(water=False)).agency, "unknown")

    def test_blocked_other_direction_is_irrelevant(self):
        self.assertEqual(judge(
            before=capture(direction="north"),
        ).agency, "unknown")

    def test_no_displacement_is_not_world_when_passable(self):
        self.assertEqual(judge(before=capture(passable=True)).agency, "unknown")

    def test_late_observation_is_not_world(self):
        self.assertEqual(judge(after=capture(t=3)).agency, "unknown")

    def test_wrong_type_is_rejected(self):
        with self.assertRaises(ValueError):
            judge(target=(True, 2))

    def test_body_success_cannot_change_spatial_agency(self):
        before = capture()
        result = judge(after=replace(capture(t=2), body={
            "food": 90.0, "water": 80.0, "energy": 90.0, "integrity": 100.0,
        }))
        self.assertEqual(result.agency, judge(before=before).agency)


if __name__ == "__main__":
    unittest.main()
