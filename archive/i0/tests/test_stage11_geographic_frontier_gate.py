"""Public Stage11 v4 demand-guarded preflight tests, with negative controls.

All references are fixed, publicly described worlds; no hidden experimentation.
"""
from dataclasses import replace
from unittest import TestCase
from unittest.mock import patch

from lab.stage11_geographic_frontier_gate_probe import (
    VARIANTS, _extra_public_inputs, run_public_demand_preflight,
)
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime


class PublicDemandDrivenPreflightTests(TestCase):
    def test_all_obstacles_eliminates_unnecessary_preflights(self):
        row = run_public_demand_preflight(
            variant="all_adjacent_obstacles", steps=6,
        )
        off, eager, demand = (
            row.without_preflight, row.eager_preflight, row.demand_preflight,
        )
        self.assertEqual(row.classification, "development_only_not_heldout")
        self.assertIsNone(row.scientific_verdict)
        self.assertFalse(row.heldout)
        self.assertEqual(off.accepted_preflight_uc, 0)
        self.assertGreater(eager.accepted_preflight_uc, 0)
        self.assertEqual(demand.accepted_preflight_uc, 0)
        self.assertEqual(
            row.demand_empty_frontier_skips,
            eager.accepted_preflight_uc,
        )
        self.assertEqual(
            row.demand_minus_eager_total_accepted_uc,
            -eager.accepted_preflight_uc,
        )
        self.assertEqual(
            demand.accepted_uc_total, off.accepted_uc_total,
        )
        self.assertEqual(
            tuple(x.applied_geographic_commands
                  for x in (off, eager, demand)),
            (0, 0, 0),
        )
        self.assertEqual(
            tuple(x.distinct_physically_perceived_sites
                  for x in (off, eager, demand)),
            (1, 1, 1),
        )
        self.assertEqual(
            tuple(x.rejected_requested_uc
                  for x in (off, eager, demand)),
            (0, 0, 0),
        )
        print("stage11_public_demand_preflight=" + row.to_json())

    def test_only_known_lethal_frontier_still_requires_security_consultation(self):
        row = run_public_demand_preflight(
            variant="sole_north_known_lethal", steps=6,
        )
        off, eager, demand = (
            row.without_preflight, row.eager_preflight, row.demand_preflight,
        )
        self.assertGreater(off.planning_unavailable, 0)
        self.assertEqual(eager.planning_unavailable, 0)
        self.assertEqual(demand.planning_unavailable, 0)
        self.assertEqual(row.demand_empty_frontier_skips, 0)
        self.assertGreater(demand.prefiltered_inadmissible, 0)
        self.assertGreater(eager.accepted_preflight_uc, 0)
        self.assertEqual(
            eager.accepted_preflight_uc,
            demand.accepted_preflight_uc,
        )
        self.assertEqual(
            eager.accepted_uc_total, demand.accepted_uc_total,
        )
        self.assertEqual(row.demand_minus_eager_total_accepted_uc, 0)
        for condition in (off, eager, demand):
            self.assertEqual(condition.known_lethal_visits, 0)
            self.assertEqual(condition.creature_occupied_visits, 0)
            self.assertEqual(condition.applied_geographic_commands, 0)
            self.assertEqual(condition.distinct_physically_perceived_sites, 1)
        print("stage11_public_demand_preflight=" + row.to_json())

    def test_four_existing_public_maps_keep_physical_safety(self):
        for variant in VARIANTS[:4]:
            with self.subTest(variant=variant):
                row = run_public_demand_preflight(
                    variant=variant, steps=6,
                )
                for condition in (
                    row.without_preflight, row.eager_preflight,
                    row.demand_preflight,
                ):
                    self.assertEqual(condition.known_lethal_visits, 0)
                    self.assertEqual(condition.creature_occupied_visits, 0)
                    self.assertEqual(
                        condition.accepted_uc_total,
                        sum(v for _, v in condition.accepted_uc_by_module),
                    )
                    self.assertGreaterEqual(
                        condition.distinct_physically_perceived_sites, 1,
                    )
                self.assertEqual(
                    row.eager_preflight.applied_geographic_commands,
                    row.demand_preflight.applied_geographic_commands,
                )
                self.assertEqual(
                    row.eager_preflight.distinct_physically_perceived_sites,
                    row.demand_preflight.distinct_physically_perceived_sites,
                )
                self.assertEqual(
                    row.eager_preflight.planning_unavailable,
                    row.demand_preflight.planning_unavailable,
                )
                print("stage11_public_demand_preflight=" + row.to_json())

    def test_reexecution_recovers_same_exact_public_provenance(self):
        a = run_public_demand_preflight(
            variant="all_adjacent_obstacles",
        )
        b = run_public_demand_preflight(
            variant="all_adjacent_obstacles",
        )
        self.assertEqual(a, b)
        self.assertEqual(a.to_json(), b.to_json())
        self.assertNotEqual(
            a.eager_preflight.journal_sha256,
            a.demand_preflight.journal_sha256,
        )

    def test_zero_raw_frontier_does_not_query_canonical_admissibility(self):
        ref = build_stage11_reference_runtime(enable_geography=True)
        world, layout, safety_facts = _extra_public_inputs(
            ref, "all_adjacent_obstacles",
        )
        runtime = Stage11Runtime(
            world_config=world, layout=layout,
            safety_config=ref.stage3.substrate.safety._config,
            safety_facts=safety_facts,
            protected_integrity_threshold=(
                ref.stage3.control._config.protected_integrity_threshold
            ),
            config=ref._stage11_config, equipment=ref.equipment,
        )
        capture = runtime.stage3.open_step()
        self.assertEqual(runtime.exploration.geographic_cibles(capture), ())
        with patch.object(
            runtime.stage3.control, "verifier_admissibilite",
            side_effect=AssertionError("zero raw frontier must not query safety"),
        ):
            targets, excluded = runtime._geographic_frontier_targets(capture)
        self.assertEqual(targets, ())
        self.assertEqual(excluded, ())
        runtime.stage3._capture = None

    def test_boolean_version_gate_and_unregistered_inputs_rejected(self):
        ref = build_stage11_reference_runtime(enable_geography=True)
        self.assertTrue(
            ref._stage11_config.geographic_preflight_requires_frontier
        )
        self.assertIn(
            "+geographic-demand-preflight-v1",
            ref._config.compute_budget.version,
        )
        with self.assertRaises(ValueError):
            replace(
                ref._stage11_config,
                geographic_preflight_requires_frontier="false",
            ).validate()
        for kwargs in (
            {"variant": "unknown_hidden"},
            {"steps": 7},
            {"steps": True},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_public_demand_preflight(**kwargs)


if __name__ == "__main__":
    import unittest
    unittest.main()
