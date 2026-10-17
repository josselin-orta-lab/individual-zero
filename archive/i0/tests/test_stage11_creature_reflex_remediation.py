"""Normative §9.2 movement-away reflex regression, separately versioned.

Triggered by the observed pre-fix physical counterexample, archived in
stage11-stale-route-safety-first-results-2026-10-11.fr.md.
These tests do not create new avoidance capabilities or scientific evidence.
"""
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.action_control import (
    ActionControl, ActionControlConfig, StaticSafetyFacts,
)
from lab.stage11_stale_route_safety_probe import run_public_changed_route


def candidate(direction, x, y):
    return SimpleNamespace(direction=direction, x=x, y=y)


def raw_capture(*, x=4, y=2, creatures=(), moves=()):
    return SimpleNamespace(
        x=x, y=y,
        adjacent_creatures=tuple(
            SimpleNamespace(x=cx, y=cy) for cx, cy in creatures
        ),
        passable_moves=tuple(
            candidate(direction, xx, yy)
            for direction, xx, yy in moves
        ),
    )


def action_control():
    return ActionControl(
        config=ActionControlConfig(
            safety_policy_version="mvp-v1.2.1",
            protected_integrity_threshold=25.0,
        ),
        safety_facts=StaticSafetyFacts(),
        protocol_mask=lambda _command: False,
    )


class NormativeCreatureReflexDistanceTests(TestCase):
    def test_only_passable_neighbor_is_occupied_by_creature(self):
        control = action_control()
        observed = raw_capture(
            creatures=((3, 2),), moves=(("west", 3, 2),),
        )
        self.assertIsNone(control.reflex(observed))

    def test_reflex_prefers_genuinely_more_distant_move(self):
        result = action_control().reflex(raw_capture(
            creatures=((3, 2),),
            moves=(("west", 3, 2), ("east", 5, 2), ("north", 4, 1)),
        ))
        self.assertIsNotNone(result)
        self.assertEqual(result.prepared.source, "reflex")
        self.assertEqual(result.prepared.command.parameters, {"direction": "east"})

    def test_tie_keeps_existing_canonical_direction_precedence(self):
        result = action_control().reflex(raw_capture(
            creatures=((3, 2),),
            moves=(("south", 4, 3), ("north", 4, 1), ("west", 3, 2)),
        ))
        self.assertIsNotNone(result)
        self.assertEqual(result.prepared.command.parameters, {"direction": "north"})

    def test_multiple_threats_require_increasing_nearest_threat_distance(self):
        result = action_control().reflex(raw_capture(
            creatures=((3, 2), (5, 2)),
            moves=(("west", 3, 2), ("east", 5, 2),
                   ("south", 4, 3), ("north", 4, 1)),
        ))
        self.assertIsNotNone(result)
        self.assertEqual(result.prepared.command.parameters, {"direction": "north"})

    def test_no_creature_or_no_passable_move_never_generates_reflex(self):
        control = action_control()
        self.assertIsNone(control.reflex(raw_capture(
            creatures=(), moves=(("west", 3, 2),),
        )))
        self.assertIsNone(control.reflex(raw_capture(
            creatures=((3, 2),), moves=(),
        )))


class PublicChangedRouteReflexRemediationTests(TestCase):
    def test_occupied_return_neighbor_cannot_trigger_reflex_toward_creature(self):
        row = run_public_changed_route(variant="creature_blocks_return")
        self.assertEqual(row.external_input_steps, (3,))
        self.assertEqual(row.actions[:2], (
            ("applied", "se_deplacer", "option:geographic:frontier:3:2:from:2:2:t1"),
            ("applied", "se_deplacer", "option:geographic:frontier:4:2:from:3:2:t2"),
        ))
        self.assertNotEqual(row.action_sources[2], "reflex")
        self.assertEqual(row.applied_reflex_moves_into_active_creature, 0)
        self.assertEqual(row.applied_route_into_active_creature, 0)
        self.assertEqual(row.observed_positions[2], (4, 2))
        self.assertEqual(row.observed_positions[3], (4, 2))
        self.assertFalse(row.heldout)
        self.assertIsNone(row.scientific_verdict)

    def test_temporary_obstacle_not_confused_with_novelty_or_oracle(self):
        row = run_public_changed_route(variant="creature_removed")
        self.assertEqual(row.external_input_steps, (3, 5))
        self.assertEqual(row.applied_reflex_moves_into_active_creature, 0)
        self.assertEqual(row.applied_route_into_active_creature, 0)
        self.assertNotEqual(row.action_sources[2], "reflex")

    def test_hidden_hazard_does_not_invent_avoidable_creature(self):
        control = run_public_changed_route(variant="unchanged_control")
        hazard = run_public_changed_route(variant="unknown_danger")
        self.assertEqual(hazard.actions[:3], control.actions[:3])
        self.assertEqual(hazard.applied_reflex_steps, ())
        self.assertGreater(hazard.danger_damage_total, 0.0)
        self.assertEqual(hazard.initial_safety_status, "unknown")
