"""Stage11 dynamic canonical known-danger transitions, unit-only.

Synthetic DC-05 evidence is deliberately invented by the test itself: it
cannot be mistaken for physical observation or a scientific verdict. The
only world steps claimed are actual public WorldBody/Perception executions.
"""
from copy import deepcopy
from unittest import TestCase

from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import Admissibility, PreparedCommand
from i0.modules.causal_model import SafetyEvidence
from i0.modules.perception import SymbolicPerception
from lab.snapshots import SnapshotType
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.world import Position


DESTINATION = (4, 2)


def synthetic_unit_record(name: str, *, step: int, harmful: bool) -> SafetyEvidence:
    return SafetyEvidence(
        identifier="stage11-synthetic-unit-" + name,
        contingency_ref="lethal-zone:4,2",
        predicate="lethal_zone", subject_ref="4,2",
        context_signature="global",
        episode_ref="unit-episode-" + name,
        observation_ref="unit-observation-" + name,
        emission_step=step, observation_step=step + 1,
        harm_observed=harmful, source="monde",
        independent_episode=True, comparable_context=True,
        alternative_cause_sufficient=False,
        exposure_motivated_independently=True,
    )


def owner_states(runtime):
    return {
        owner.owner_id: deepcopy(owner.export_causal_state())
        for owner in runtime.causal_owners
    }


def events(runtime, name, t):
    return [
        entry.causal_event for entry in runtime.journal.entries
        if entry.causal_event.get("kind") == name
        and entry.causal_event.get("t_monde") == t
    ]


def unit_policy_capture(runtime):
    # Independent test-side view of the declared public WorldBody state;
    # never published into the individual's Perception or cognition.
    return SymbolicPerception().capture(
        local_state=runtime.world.capture_local(t_monde=2).as_dict(),
        telemetry=runtime.world.telemetry(),
    )


def east_admissibility(runtime, capture):
    prepared = PreparedCommand(
        command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
        source="decision",
    )
    return runtime.stage3.control.verifier_admissibilite(
        capture=capture, prepared=prepared,
    )


def publish_record(runtime, name, step, harmful):
    runtime.causal_model.integrate(
        synthetic_unit_record(name, step=step, harmful=harmful),
    )
    return runtime.causal_model.publish()


def create_snapshot(runtime, *, step):
    snapshots = runtime.stage3.substrate.snapshots
    frozen = owner_states(runtime)
    record = snapshots.take(
        snapshot_type=SnapshotType.PERIODIC,
        individual_id=runtime.individual_id,
        t_monde=step, cycle=0, attempt_ref=None,
        owners=runtime.causal_owners,
        versions={"stage11": runtime._stage11_config.version},
    )
    if not snapshots.verify(record.id):
        raise AssertionError("periodic snapshot hash verification failed")
    return record.id, frozen


class Stage11CanonicalKnownDangerTransitionTests(TestCase):
    def test_promotion_revocation_final_veto_and_two_snapshots(self):
        runtime = build_public_route_runtime(
            layout_variant="junction_open", survey_refresh=True,
        )
        first = runtime.run_step()
        self.assertEqual(first.execution_status, "applied")
        self.assertEqual(runtime.world.position, Position(3, 2))
        capture = unit_policy_capture(runtime)
        self.assertEqual((capture.x, capture.y), (3, 2))
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "unknown",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INDETERMINATE,
        )

        self.assertEqual(publish_record(runtime, "harm-1", 1, True), ())
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "unknown",
        )
        promoted = publish_record(runtime, "harm-2", 2, True)
        self.assertEqual(len(promoted), 1)
        self.assertEqual(
            (promoted[0].before, promoted[0].after),
            ("aucun", "etabli_pour_securite"),
        )
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "known_lethal",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INADMISSIBLE,
        )

        second = runtime.run_step()
        self.assertNotEqual(runtime.world.position, Position(*DESTINATION))
        self.assertFalse(
            second.execution_status == "applied"
            and second.command_primitive == "se_deplacer"
            and runtime.world.position == Position(*DESTINATION),
        )
        excluded = [
            item for event in events(
                runtime, "stage11_geographic_admissibility_prefiltered", 2,
            )
            for item in event["data"]["excluded"]
        ]
        self.assertIn(
            {"direction": "east", "destination": [4, 2]}, excluded,
        )
        known_id, known_state = create_snapshot(runtime, step=2)
        self.assertEqual(publish_record(runtime, "safe-1", 3, False), ())
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "known_lethal",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INADMISSIBLE,
        )
        revoked = publish_record(runtime, "safe-2", 4, False)
        self.assertEqual(len(revoked), 1)
        self.assertEqual(
            (revoked[0].before, revoked[0].after),
            ("etabli_pour_securite", "aucun"),
        )
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "unknown",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INDETERMINATE,
        )

        # A real subsequent step may choose or decline movement according
        # to Competition, budget and the unchanged final Action Control.
        runtime.run_step()
        self.assertTrue(runtime.journal.verify())
        unknown_id, unknown_state = create_snapshot(runtime, step=3)
        snapshots = runtime.stage3.substrate.snapshots

        snapshots.restore(known_id, owners=runtime.causal_owners)
        self.assertEqual(owner_states(runtime), known_state)
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "known_lethal",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INADMISSIBLE,
        )

        snapshots.restore(unknown_id, owners=runtime.causal_owners)
        self.assertEqual(owner_states(runtime), unknown_state)
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=4, y=2), "unknown",
        )
        self.assertEqual(
            east_admissibility(runtime, capture),
            Admissibility.INDETERMINATE,
        )
        self.assertTrue(snapshots.verify(known_id))
        self.assertTrue(snapshots.verify(unknown_id))
        self.assertTrue(runtime.journal.verify())

    def test_independent_public_steps_match_with_identical_unit_inputs(self):
        def run():
            runtime = build_public_route_runtime(survey_refresh=True)
            runtime.run_step()
            publish_record(runtime, "harm-1", 1, True)
            publish_record(runtime, "harm-2", 2, True)
            runtime.run_step()
            publish_record(runtime, "safe-1", 3, False)
            publish_record(runtime, "safe-2", 4, False)
            runtime.run_step()
            self.assertTrue(runtime.journal.verify())
            return runtime

        left = run()
        right = run()
        self.assertEqual(
            left.journal.canonical_bytes(), right.journal.canonical_bytes(),
        )
        self.assertEqual(owner_states(left), owner_states(right))
        self.assertEqual(left.world.position, right.world.position)


if __name__ == "__main__":
    import unittest
    unittest.main()
