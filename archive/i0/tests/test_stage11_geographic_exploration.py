"""Stage-11 autonomous frontier: public, observable, deterministic tests.

These are software integration tests, never scientific EXP or held-out data.
"""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from i0.modules.action_control import Admissibility, StaticSafetyFacts

from i0.modules.exploration import Exploration, ExplorationConfig
from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import BodyState, Position


def config(*, sites=15, weight=0.7):
    return GeographicExplorationConfig(
        version="p48-geographic-software-test-v1",
        novelty_weight=weight,
        max_distinct_sites=sites, max_targets_per_cycle=1,
    )


def cell(direction, x, y, *, passable=True, creature=False):
    return SimpleNamespace(
        direction=direction, x=x, y=y,
        passable=passable, creature=creature,
        water_source=False, resources=(),
    )


def capture(step=1, x=2, y=2, *, blocked_north=False, creature_east=False):
    return SimpleNamespace(
        t_monde=step, x=x, y=y,
        adjacent=(
            cell("south", x, y + 1),
            cell("east", x + 1, y, creature=creature_east),
            cell("north", x, y - 1, passable=not blocked_north),
            cell("west", x - 1, y),
        ),
    )


def exploration(geographic=True):
    return Exploration(
        ExplorationConfig("p48-geographic-unit-v1", 0.5, 0.3, 2, 2),
        coefficient=0.0,
        geographic_config=config() if geographic else None,
    )


class GeographicOwnerTests(TestCase):
    def test_geographic_targets_are_ordered_north_and_no_hidden_map(self):
        geo = GeographicExploration(config())
        source = capture()
        self.assertEqual(geo.distinct_sites, 0)
        targets = geo.cibles(source)
        self.assertEqual(len(targets), 1)
        target = targets[0]
        self.assertEqual(target.direction, "north")
        self.assertEqual(target.origin, (2,2))
        self.assertEqual(target.destination, (2,1))
        self.assertTrue(geo.observe_capture(source))
        geo.freeze_targets(targets)
        self.assertEqual(geo.distinct_sites, 1)
        self.assertEqual(geo.visit_count, 1)
        # Deliberation cycles do not create imaginary physical visits.
        self.assertFalse(geo.observe_capture(source))
        self.assertEqual(geo.visit_count, 1)
        self.assertEqual(geo.cibles(source, degraded=True), ())

    def test_inadmissible_north_does_not_starve_single_target_capacity(self):
        geo = GeographicExploration(config())
        source = capture()
        self.assertEqual(geo.cibles(source)[0].direction, "north")
        filtered = geo.cibles(
            source, inadmissible_directions=frozenset({"north"}),
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].direction, "east")
        self.assertEqual(filtered[0].destination, (3,2))
        # An unknown status is NOT prohibited and must remain eligible.
        self.assertEqual(geo.cibles(source)[0].direction, "north")
        for malformed in (
            {"north"}, frozenset({"north", "invisible"}),
            frozenset({False}), None,
        ):
            with self.subTest(value=malformed), self.assertRaises(ValueError):
                geo.cibles(source, inadmissible_directions=malformed)

    def test_real_new_capture_retires_the_old_frontier(self):
        geo = GeographicExploration(config())
        source = capture()
        candidates = geo.cibles(source)
        geo.observe_capture(source)
        geo.freeze_targets(candidates)
        visited = capture(step=2, x=2, y=1)
        self.assertTrue(geo.observe_capture(visited))
        self.assertEqual(geo.distinct_sites, 2)
        self.assertFalse(geo.cibles(visited)[0].destination in {(2,2),(2,1)})
        self.assertEqual(geo.cibles(visited)[0].direction, "north")
        geo.freeze_targets(geo.cibles(visited))
        self.assertEqual(geo.visit_count, 2)
        with self.assertRaises(ValueError):
            geo.observe_capture(capture(step=2, x=8, y=8))

    def test_veto_surfaces_and_degraded_mode_cannot_invent_targets(self):
        geo = GeographicExploration(config())
        blocked = capture(blocked_north=True, creature_east=True)
        self.assertEqual(geo.cibles(blocked)[0].direction, "south")
        self.assertEqual(geo.cibles(blocked, degraded=True), ())
        zero = GeographicExploration(config(weight=0))
        self.assertEqual(zero.cibles(capture()), ())

    def test_visit_ledger_caps_capacity_without_revisiting_as_novel(self):
        geo = GeographicExploration(config(sites=1))
        geo.observe_capture(capture())
        self.assertEqual(geo.cibles(capture()), ())
        with self.assertRaises(ValueError):
            geo.observe_capture(capture(step=2, x=2, y=1))
        self.assertEqual(geo.distinct_sites, 1)
        self.assertEqual(geo.visit_count, 1)

    def test_snapshot_is_exact_atomic_and_versioned(self):
        owner = exploration()
        source = capture()
        target = owner.geographic_cibles(source)
        owner.observe_geographic_capture(source, frozen_targets=target)
        snapshot = owner.export_causal_state()
        self.assertEqual(snapshot["state_schema"],
                         "exploration-activity-v3-geographic")
        restored = exploration()
        restored.restore_causal_state(snapshot)
        self.assertEqual(restored.export_causal_state(), snapshot)
        for key, value in (
            ("schema", "corrupt"),
            ("offered", [
                {**snapshot["geography"]["offered"][0],
                 "direction": "west"},
            ]),
            ("visits", [[2,2,1],[2,2,2]]),
        ):
            mutated = deepcopy(snapshot)
            mutated["geography"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                restored.restore_causal_state(mutated)
            self.assertEqual(restored.export_causal_state(), snapshot)
        with self.assertRaises(ValueError):
            exploration(False).restore_causal_state(snapshot)

    def test_frontier_motivation_requires_current_physically_offered_target(self):
        owner = exploration()
        source = capture()
        target = owner.geographic_cibles(source)[0]
        owner.observe_geographic_capture(source, frozen_targets=(target,))
        option = SimpleNamespace(
            motive_ref=SimpleNamespace(
                type="cible_exploration", id=target.ref,
            ), provenance="exploration", goal_ref=None,
            id=f"option:geographic:{target.ref}:t{target.source_t_monde}",
        )
        result = owner.geographic_motivation(option)
        self.assertEqual(result.status, "available")
        self.assertGreater(result.value, 0)
        owner.observe_geographic_capture(capture(step=2, x=2, y=1))
        self.assertEqual(owner.geographic_motivation(option).status, "unavailable")


class GeographicRuntimeTests(TestCase):
    def test_preflight_requeries_action_control_no_unsafe_private_cache(self):
        runtime = build_stage11_reference_runtime(enable_geography=True)
        capture = runtime.stage3.open_step()
        statuses = {"north": Admissibility.INADMISSIBLE}
        consulted = []

        def decide(*, capture, prepared):
            direction = prepared.command.parameters["direction"]
            consulted.append(direction)
            return statuses.get(direction, Admissibility.INDETERMINATE)

        with patch.object(
            runtime.stage3.control, "verifier_admissibilite",
            side_effect=decide,
        ):
            one, excluded = runtime._geographic_frontier_targets(capture)
            self.assertEqual(one[0].direction, "east")
            self.assertIn(("north", (2,1)), excluded)
            # The canonical service reclassifies this cell: no permanent
            # Exploration-local 'forbidden map' may hide it on re-query.
            statuses["north"] = Admissibility.INDETERMINATE
            two, new_excluded = runtime._geographic_frontier_targets(capture)
            self.assertEqual(new_excluded, ())
            self.assertEqual(two[0].direction, "north")
            self.assertGreaterEqual(consulted.count("north"), 2)
        runtime.stage3._capture = None

    def test_phase1_cap_one_filters_known_lethal_before_offering_east(self):
        base = build_stage11_reference_runtime(enable_geography=True)
        geography = replace(
            base._stage11_config.geographic,
            version="p48-public-cap-one-phase1-v1",
            max_targets_per_cycle=1,
        )
        cfg = replace(
            base._stage11_config,
            version="stage11-phase1-cap-one-test-v1",
            geographic=geography,
        )
        owner = Stage11Runtime(
            world_config=replace(
                base.world.config,
                initial_body=BodyState(
                    energy=50, food=60, water=60, integrity=100,
                ),
            ),
            layout=replace(
                base.world._layout,
                lethal_zones=frozenset({Position(2, 1)}),
            ),
            safety_config=base.stage3.substrate.safety._config,
            safety_facts=StaticSafetyFacts(
                known_lethal_positions=frozenset({(2, 1)}),
            ),
            protected_integrity_threshold=(
                base.stage3.control._config.protected_integrity_threshold
            ),
            config=cfg, equipment=base.equipment,
        )
        for _ in range(4):
            owner.run_step()
        proposed = [
            entry.causal_event["data"]
            for entry in owner.journal.entries
            if entry.causal_event.get("kind")
            == "stage11_geographic_option_proposed"
        ]
        self.assertTrue(proposed)
        self.assertEqual(proposed[0]["direction"], "east")
        # A later northward step from a different position can be safe.
        # Forbid the known lethal PHYSICAL CELL, not a global direction.
        self.assertFalse(any(
            tuple(row["destination"]) == (2, 1)
            for row in proposed
        ))
        visits = owner.exploration.geographic.export_causal_state()["visits"]
        self.assertNotIn((2, 1), {tuple(row[:2]) for row in visits})
        self.assertTrue(owner.journal.verify())

    def test_disabled_by_default_preserves_stage9_and_stage11_schema(self):
        baseline = build_stage9_reference_runtime()
        stage11 = build_stage11_reference_runtime()
        self.assertIsNone(stage11.exploration.geographic)
        self.assertEqual(stage11.exploration.export_causal_state()["state_schema"],
                         "exploration-activity-v2")
        for runtime in (baseline, stage11):
            self.assertEqual(runtime.run_step().execution_status, "applied")
            self.assertTrue(runtime.journal.verify())
        self.assertFalse(any(
            row.causal_event.get("kind", "").startswith("stage11_geographic")
            for row in stage11.journal.entries
        ))

    def test_opt_in_frontier_produced_from_real_perception(self):
        runtime = build_stage11_reference_runtime(enable_geography=True)
        for _ in range(3):
            self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertGreater(runtime.exploration.geographic.distinct_sites, 0)
        events = [entry.causal_event for entry in runtime.journal.entries]
        proposed = [
            row["data"] for row in events
            if row.get("kind") == "stage11_geographic_option_proposed"
        ]
        self.assertTrue(proposed)
        self.assertTrue(all(
            row["source"] == "single_perceptual_capture"
            and row["goal_ref"] is None
            and row["simulation_status"] in ("complete", "unavailable")
            and row["simulated"] == (row["simulation_status"] == "complete")
            and (
                row["simulation_reason"] == "equipment_input_unseen"
                if not row["simulated"]
                else row["simulation_reason"] is None
            )
            for row in proposed
        ))
        intrinsic = [
            row["data"] for row in events
            if row.get("kind") == "stage11_intrinsic_evaluation"
            and row["data"]["option_ref"].startswith("option:geographic:")
        ]
        self.assertTrue(intrinsic)
        self.assertTrue(any(
            row["status"] == "evaluated"
            and row["intrinsic_value"] is not None
            and row["intrinsic_value"] > 0
            for row in intrinsic
        ))
        self.assertTrue(runtime.journal.verify())

    def test_satisfied_needs_can_explore_north_and_reexecute_identically(self):
        base = build_stage11_reference_runtime(enable_geography=True)
        initial = BodyState(
            energy=50, food=60, water=60, integrity=100,
        )
        def make_runtime():
            return Stage11Runtime(
                world_config=replace(base.world.config, initial_body=initial),
                layout=base.world._layout,
                safety_config=base.stage3.substrate.safety._config,
                safety_facts=base._canonical_safety._innate,
                protected_integrity_threshold=(
                    base.stage3.control._config.protected_integrity_threshold
                ),
                config=base._stage11_config, equipment=base.equipment,
            )
        a, b = make_runtime(), make_runtime()
        results = []
        for owner in (a, b):
            outputs = [owner.run_step() for _ in range(5)]
            self.assertTrue(owner.journal.verify())
            results.append([
                (result.command_primitive, result.option_ref)
                for result in outputs
            ])
        self.assertEqual(results[0], results[1])
        self.assertEqual(a.journal.canonical_bytes(), b.journal.canonical_bytes())
        self.assertEqual(a.exploration.export_causal_state(),
                         b.exploration.export_causal_state())
        self.assertTrue(any(
            cmd == "se_deplacer" and option is not None
            and option.startswith("option:geographic:")
            for cmd, option in results[0]
        ))
        self.assertGreaterEqual(a.exploration.geographic.distinct_sites, 2)


if __name__ == "__main__":
    import unittest
    unittest.main()
