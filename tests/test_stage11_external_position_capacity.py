"""Stage11 external-world position overflow: public deterministic unit checks.

Only software fixtures. No scientific or held-out evidence.
"""
from copy import deepcopy
from dataclasses import replace
from unittest import TestCase

from lab.injected_scenario import ScenarioEvent
from lab.snapshots import SnapshotType
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import Position


def runtime():
    baseline = build_public_route_runtime(
        layout_variant="junction_open", survey_refresh=True,
    )
    original = baseline._stage11_config
    config = replace(
        original,
        version=original.version + "+external-world-overcap-test-v1",
        geographic=replace(
            original.geographic,
            version=original.geographic.version + "+physical-overcap-v1",
            max_distinct_sites=1,
        ),
    )
    return Stage11Runtime(
        world_config=baseline.world.config,
        layout=baseline.world._layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=baseline.equipment,
        scenario_id="stage11-public-external-position-overcap",
        scenario_version="unit-only-v1",
        scenario_events=(ScenarioEvent(
            t_monde=2, sequence=1, operation="set_position",
            payload={"position": {"x": 4, "y": 2}},
        ),),
    )


def events(runner, kind):
    return [
        e.causal_event for e in runner.journal.entries
        if e.causal_event.get("kind") == kind
    ]


class Stage11PhysicalOverCapacityTests(TestCase):
    def test_physical_arrival_continues_without_fake_registered_visit(self):
        runner = runtime()
        runner.run_step()
        geo = runner.exploration.geographic
        self.assertEqual(geo.distinct_sites, 1)
        self.assertEqual(runner.world.position, Position(2, 2))
        runner.run_step()
        self.assertEqual(runner.world.position, Position(4, 2))
        self.assertEqual(geo.distinct_sites, 1)
        self.assertEqual(geo.export_causal_state()["visits"], [[2, 2, 1]])
        self.assertEqual(geo.export_causal_state()["last_capture"], [1, 2, 2])
        self.assertEqual(geo.offered, ())
        self.assertEqual(geo.transit_offered, ())
        self.assertEqual(len(events(runner, "stage11_geographic_physical_capture_unregistered")), 1)
        rejected = events(runner, "stage11_geographic_physical_capture_unregistered")[0]
        self.assertEqual(rejected["data"]["physical_position"], [4, 2])
        self.assertFalse(rejected["data"]["new_registered_visit"])
        self.assertFalse(rejected["data"]["autonomous_movement_claim"])
        self.assertTrue(any(
            e["operation"] == "set_position" and e["t_monde"] == 2
            for e in events(runner, "external_input_received")
        ))
        captured = [
            e for e in events(runner, "perceptual_capture")
            if e["data"]["capture_t_monde"] == 2
        ]
        self.assertEqual([e["data"]["position"] for e in captured],
                         [{"x": 4, "y": 2}])
        self.assertFalse(any(
            e["data"].get("operation") == "geographic_route_search"
            and e["data"].get("accepted") is True
            and e["t_monde"] == 2
            for e in events(runner, "compute_charge")
        ))
        self.assertTrue(runner.journal.verify())
        runner.run_step()
        self.assertEqual(runner.world.position, Position(4, 2))
        self.assertEqual(geo.distinct_sites, 1)
        self.assertEqual(geo.visit_count, 1)
        self.assertEqual(len(events(runner, "stage11_geographic_physical_capture_unregistered")), 2)
        self.assertTrue(runner.journal.verify())

    def test_periodic_snapshot_roundtrip_with_physical_owner_divergence(self):
        runner = runtime()
        runner.run_step()
        runner.run_step()
        owners = runner.causal_owners
        before = {o.owner_id: deepcopy(o.export_causal_state()) for o in owners}
        record = runner.stage3.substrate.snapshots.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id=runner.individual_id,
            t_monde=2, cycle=0, attempt_ref=None,
            owners=owners, versions={"stage11": runner._stage11_config.version},
        )
        self.assertTrue(runner.stage3.substrate.snapshots.verify(record.id))
        runner.run_step()
        runner.stage3.substrate.snapshots.restore(record.id, owners=owners)
        after = {o.owner_id: o.export_causal_state() for o in owners}
        self.assertEqual(after, before)
        self.assertEqual(runner.world.position, Position(4, 2))
        self.assertEqual(runner.exploration.geographic.distinct_sites, 1)
        self.assertTrue(runner.journal.verify())

    def test_independent_exact_scenario_reexecution(self):
        a = runtime()
        b = runtime()
        for _ in range(3):
            self.assertEqual(a.run_step(), b.run_step())
        self.assertEqual(a.journal.canonical_bytes(), b.journal.canonical_bytes())
        self.assertEqual(
            {o.owner_id: o.export_causal_state() for o in a.causal_owners},
            {o.owner_id: o.export_causal_state() for o in b.causal_owners},
        )
        self.assertTrue(a.journal.verify())
        self.assertTrue(b.journal.verify())

    def test_bad_external_positions_rejected_without_world_mutation(self):
        runner = runtime()
        world = runner.world
        baseline = deepcopy(world.export_causal_state())
        for position in (
            {"x": 0, "y": 2},  # impassable world border
            {"x": 3, "y": 3},  # known blocked cell in public junction
            {"x": 999, "y": 999},
            None,
        ):
            with self.subTest(position=position), self.assertRaises((ValueError, TypeError, KeyError)):
                world.apply_scenario_event("set_position", {"position": position})
            self.assertEqual(world.export_causal_state(), baseline)


if __name__ == "__main__":
    import unittest
    unittest.main()
