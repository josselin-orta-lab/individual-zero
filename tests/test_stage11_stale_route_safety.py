"""Public Stage-11 route invalidation and synthetic canonical veto contracts.

The causal-promotion test below fabricates unit-only SafetyEvidence: it
MUST NOT be treated as physical evidence, a held-out experiment or a Golden.
"""
from unittest import TestCase

from i0.modules.causal_model import SafetyEvidence
from lab.stage11_stale_route_safety_probe import (
    VARIANTS, run_public_changed_route,
)
from lab.stage11_routed_junction_probe import build_public_route_runtime


def synthetic_unit_lethal(identifier: str, emission_step: int) -> SafetyEvidence:
    return SafetyEvidence(
        identifier=identifier,
        contingency_ref="lethal-zone:3,2",
        predicate="lethal_zone", subject_ref="3,2",
        context_signature="global",
        episode_ref=f"unit-synthetic-episode:{identifier}",
        observation_ref=f"unit-synthetic-observation:{identifier}",
        emission_step=emission_step,
        observation_step=emission_step + 1,
        harm_observed=True, source="monde",
        independent_episode=True, comparable_context=True,
        alternative_cause_sufficient=False,
        exposure_motivated_independently=True,
    )


class Stage11ChangedWorldRouteTests(TestCase):
    def test_external_changes_are_journaled_and_cannot_leak_into_past(self):
        control = run_public_changed_route(variant="unchanged_control")
        self.assertEqual(control.external_inputs_applied, 0)
        self.assertEqual(control.applied_route_steps, 2)
        self.assertTrue(control.observed_alternate_branch)
        for variant in VARIANTS[1:]:
            with self.subTest(variant=variant):
                row = run_public_changed_route(variant=variant)
                self.assertEqual(row.steps, 10)
                self.assertEqual(
                    row.initial_local_sha256, control.initial_local_sha256,
                )
                self.assertEqual(
                    row.observed_positions[:2],
                    control.observed_positions[:2],
                )
                self.assertEqual(row.actions[:2], control.actions[:2])
                self.assertEqual(row.external_inputs_applied,
                                 len(row.external_input_operations))
                self.assertEqual(set(row.confirmed_visit_sites),
                                 set(row.observed_positions))
                self.assertEqual(row.initial_safety_status, "unknown")
                self.assertEqual(row.safety_status_after_step_2, "unknown")
                self.assertFalse(row.heldout)
                self.assertIsNone(row.scientific_verdict)

    def test_persistently_occupied_next_hop_never_becomes_a_route_command(self):
        blocked = run_public_changed_route(variant="creature_blocks_return")
        self.assertEqual(blocked.external_input_operations,
                         ("place_creature",))
        self.assertEqual(blocked.external_input_steps, (3,))
        self.assertEqual(blocked.applied_route_into_active_creature, 0)
        # No forced escape success or fabricated intrinsic novelty claim.
        self.assertFalse(blocked.observed_alternate_branch)
        self.assertEqual(blocked.danger_damage_total, 0.0)

    def test_removed_obstruction_is_reobserved_before_any_reuse(self):
        restored = run_public_changed_route(variant="creature_removed")
        self.assertEqual(restored.external_input_operations,
                         ("place_creature", "remove_creature"))
        self.assertEqual(restored.external_input_steps, (3, 5))
        self.assertEqual(restored.applied_route_into_active_creature, 0)
        # Whether it actually returns is an observed endpoint, not a promise.
        self.assertTrue(all(isinstance(p, tuple)
                            for p in restored.observed_positions))

    def test_hidden_danger_is_not_injected_into_first_route_decision(self):
        clear = run_public_changed_route(variant="unchanged_control")
        danger = run_public_changed_route(variant="unknown_danger")
        self.assertEqual(danger.initial_local_sha256,
                         clear.initial_local_sha256)
        self.assertEqual(danger.actions[:3], clear.actions[:3])
        self.assertEqual(danger.external_input_operations,
                         ("set_danger_zone",))
        self.assertEqual(danger.external_input_steps, (3,))
        self.assertEqual(danger.initial_safety_status, "unknown")
        self.assertEqual(danger.safety_status_after_step_2, "unknown")
        # Damage is a Lab physical-transition score, never a forecast.
        self.assertGreater(danger.danger_damage_total, 0.0)
        self.assertLess(danger.final_integrity, clear.final_integrity)

    def test_every_public_changed_world_reexecutes_canonically(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                left = run_public_changed_route(variant=variant)
                right = run_public_changed_route(variant=variant)
                self.assertEqual(left, right)
                self.assertEqual(left.to_json(), right.to_json())
                print("stage11_public_changed_route=" + left.to_json())

    def test_only_declared_variants_and_steps_can_run(self):
        for variant, steps in (("private_oracle", 10),
                               ("unchanged_control", 9),
                               ("unchanged_control", True)):
            with self.subTest(variant=variant, steps=steps):
                with self.assertRaises(ValueError):
                    run_public_changed_route(variant=variant, steps=steps)


class Stage11SyntheticCanonicalRouteVetoTests(TestCase):
    def test_live_canonical_promotion_vetoes_return_to_previously_visited_site(self):
        owner = build_public_route_runtime()
        first_two = tuple(owner.run_step() for _ in range(2))
        self.assertTrue(all(x.execution_status == "applied" for x in first_two))
        self.assertEqual((owner.world.position.x, owner.world.position.y),
                         (4, 2))
        self.assertEqual(owner._canonical_safety.zone_status(x=3, y=2),
                         "unknown")
        # Explicitly synthetic and isolated: NO fake physical episode is
        # written to the journal and NO scientific inference is permitted.
        owner.causal_model.integrate(synthetic_unit_lethal("unit-route-harm-1", 1))
        owner.causal_model.integrate(synthetic_unit_lethal("unit-route-harm-2", 2))
        owner.causal_model.publish()
        self.assertEqual(owner._canonical_safety.zone_status(x=3, y=2),
                         "known_lethal")
        third = owner.run_step()
        recorded = tuple(e.causal_event for e in owner.journal.entries)
        self.assertTrue(owner.journal.verify())
        self.assertGreater(sum(
            e.get("kind") == "stage11_route_transit_prefiltered"
            and e["data"]["admissibility"] == "inadmissible"
            and e["data"]["destination"] == [3, 2]
            for e in recorded
        ), 0)
        self.assertFalse(
            third.execution_status == "applied"
            and "frontier_route:" in (third.option_ref or "")
        )
        self.assertFalse(owner.exploration.geographic.transit_offered)
        self.assertEqual((owner.world.position.x, owner.world.position.y),
                         (4, 2))
        self.assertEqual(owner._canonical_safety.zone_status(x=3, y=2),
                         "known_lethal")
