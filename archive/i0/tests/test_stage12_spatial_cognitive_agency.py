"""Action Control GA-SPATIAL-01 owner-local cognitive tests.

Fixtures only. These do not establish autonomous world attribution.
"""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.stage12_goal_agency import (
    GoalAgencyService, GOAL_AGENCY_SPATIAL_VERSION,
)
from test_stage12_spatial_cue_policy import capture


def preregister(blocked: bool = True):
    svc = GoalAgencyService()
    pre = capture(passable=not blocked)
    claim = svc.preregister(
        assessment_ref="assessment:one", intent_ref="goal-intent:one",
        life_id="life:first", goal_ref="goal:water",
        option_ref="opt:move", command_hash="cmd:east",
        world_step=1, measure="spatial_distance",
        command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        capture=pre, spatial_target=(3, 2, "water"),
    )
    return svc, claim


class SpatialCognitiveAgencyTests(unittest.TestCase):
    def test_world_is_authored_from_blocked_first_person_cue(self):
        svc, commitment = preregister(True)
        self.assertEqual(commitment.policy_version, GOAL_AGENCY_SPATIAL_VERSION)
        image = svc.export_causal_state()
        self.assertEqual(image["pending_commitment"]["spatial_prepassable"], False)
        judgement = svc.evaluate(capture=capture(t=2), world_step=2,
                                 cue_ref="sensory:two", paid=True)
        self.assertEqual(judgement.subjective_agency, "world")
        self.assertEqual(judgement.reason,
                         "witnessed_goal_relevant_blocked_direction")

    def test_self_requires_perceived_displacement(self):
        svc, _ = preregister(False)
        judgement = svc.evaluate(
            capture=capture(t=2, x=3, y=2), world_step=2,
            cue_ref="sensory:two", paid=True,
        )
        self.assertEqual(judgement.subjective_agency, "self")

    def test_confounded_or_missing_movement_is_unknown(self):
        svc, _ = preregister(False)
        # The old static fixture's default is a *new blocked cue*, which
        # now legitimately represents A2. Keep this an unchanged-free-world
        # negative control: no movement by itself never proves world agency.
        judgement = svc.evaluate(
            capture=capture(t=2, passable=True), world_step=2,
            cue_ref="sensory:two", paid=True,
        )
        self.assertEqual(judgement.subjective_agency, "unknown")

    def test_refused_uc_is_unavailable_not_world(self):
        svc, _ = preregister(True)
        judgement = svc.evaluate(
            capture=capture(t=2), world_step=2,
            cue_ref=None, paid=False,
        )
        self.assertEqual(judgement.subjective_agency, "unavailable")

    def test_cold_restore_is_not_historical_rewind(self):
        svc, _ = preregister(True)
        state = svc.export_causal_state()
        cold = GoalAgencyService()
        cold.restore_causal_state(state)
        self.assertEqual(cold.pending, svc.pending)
        with self.assertRaises(ValueError):
            cold.restore_causal_state(state)

    def test_wrong_visible_target_never_forms_commitment(self):
        svc = GoalAgencyService()
        with self.assertRaises(ValueError):
            svc.preregister(
                assessment_ref="assessment:one", intent_ref="goal-intent:one",
                life_id="life:first", goal_ref="goal:water",
                option_ref="opt:move", command_hash="cmd:east",
                world_step=1, measure="spatial_distance",
                command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
                capture=capture(water=False),
                spatial_target=(3, 2, "water"),
            )
        self.assertIsNone(svc.pending)

    def test_body_gain_cannot_flip_spatial_agency(self):
        first, _ = preregister(True)
        second, _ = preregister(True)
        base = capture(t=2)
        a = first.evaluate(capture=base, world_step=2,
                           cue_ref="cue:one", paid=True)
        b = second.evaluate(
            capture=replace(base, body={**base.body, "water": 99.0}),
            world_step=2, cue_ref="cue:two", paid=True,
        )
        self.assertEqual(a.subjective_agency, b.subjective_agency)


if __name__ == "__main__":
    unittest.main()
