"""Public Stage-11 total-UC comparison; results may be favorable or negative.

Never infer scientific evidence from these fixed public software fixtures.
"""
from dataclasses import replace
from unittest import TestCase

from lab.stage11_geographic_robustness_probe import VARIANTS
from lab.stage11_geographic_uc_probe import run_public_geographic_total_uc
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class GeographicTotalUCAblationTests(TestCase):
    def test_same_public_known_lethal_map_no_plan_retries_with_safe_prefilter(self):
        row = run_public_geographic_total_uc(
            variant="known_lethal_north", steps=6,
        )
        old, new = row.legacy_compatible, row.preflight
        self.assertEqual(row.classification, "development_only_not_heldout")
        self.assertFalse(row.heldout)
        self.assertIsNone(row.scientific_verdict)
        self.assertFalse(old.preflight_enabled)
        self.assertTrue(new.preflight_enabled)
        self.assertNotEqual(old.config_version, new.config_version)
        self.assertGreater(old.planning_unavailable, 0)
        self.assertEqual(new.planning_unavailable, 0)
        self.assertGreater(new.prefiltered_inadmissible, 0)
        self.assertEqual(old.prefiltered_inadmissible, 0)
        self.assertEqual(old.accepted_preflight_uc, 0)
        self.assertGreater(new.accepted_preflight_uc, 0)
        self.assertEqual(old.known_lethal_visits, 0)
        self.assertEqual(new.known_lethal_visits, 0)
        self.assertEqual(old.creature_occupied_visits, 0)
        self.assertEqual(new.creature_occupied_visits, 0)
        self.assertEqual(
            row.accepted_uc_delta_preflight_minus_legacy,
            new.accepted_uc_total - old.accepted_uc_total,
        )
        self.assertEqual(
            row.requested_rejected_uc_delta_preflight_minus_legacy,
            new.rejected_requested_uc - old.rejected_requested_uc,
        )
        self.assertEqual(
            new.accepted_planning_uc,
            sum(value for name, value in new.accepted_uc_by_planning_operation),
        )
        self.assertEqual(
            new.accepted_uc_total,
            sum(value for _, value in new.accepted_uc_by_module),
        )
        self.assertEqual(
            old.accepted_uc_total,
            sum(value for _, value in old.accepted_uc_by_module),
        )
        print("stage11_public_total_uc_ablation=" + row.to_json())

    def test_all_four_public_controls_have_bounded_accounted_software_uc(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                row = run_public_geographic_total_uc(
                    variant=variant, steps=6,
                )
                for result in (row.legacy_compatible, row.preflight):
                    self.assertGreater(result.accepted_uc_total, 0)
                    self.assertGreaterEqual(result.cognitive_cycles, 0)
                    self.assertEqual(result.known_lethal_visits, 0)
                    self.assertEqual(result.creature_occupied_visits, 0)
                    self.assertGreaterEqual(result.rejected_requested_uc, 0)
                    self.assertGreaterEqual(
                        result.distinct_physically_perceived_sites, 1,
                    )
                self.assertEqual(row.legacy_compatible.accepted_preflight_uc, 0)
                self.assertGreater(row.preflight.accepted_preflight_uc, 0)
                print("stage11_public_total_uc_control=" + row.to_json())

    def test_current_code_ablation_exact_reexecution(self):
        first = run_public_geographic_total_uc(
            variant="known_lethal_north", steps=6,
        )
        second = run_public_geographic_total_uc(
            variant="known_lethal_north", steps=6,
        )
        self.assertEqual(first, second)
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertNotEqual(
            first.legacy_compatible.journal_sha256,
            first.preflight.journal_sha256,
        )

    def test_opt_in_flag_is_versioned_and_geometry_off_does_not_pay(self):
        enabled = build_stage11_reference_runtime(enable_geography=True)
        disabled = build_stage11_reference_runtime(enable_geography=False)
        self.assertTrue(enabled._stage11_config.geographic_preflight)
        self.assertNotIn(
            "geographic_admissibility_preflight",
            disabled._config.compute_budget.operation_costs,
        )
        self.assertEqual(
            enabled._config.compute_budget.operation_costs[
                "geographic_admissibility_preflight"
            ], 1,
        )
        cfg = replace(enabled._stage11_config, geographic_preflight=False)
        self.assertNotIn(
            "geographic_admissibility_preflight",
            cfg.with_budget().stage8.stage7.stage6.stage4.compute_budget.operation_costs,
        )
        with self.assertRaises(ValueError):
            replace(cfg, geographic_preflight="no").validate()

    def test_rejects_unregistered_public_worlds_and_windows(self):
        for kwargs in (
            {"variant": "sealed_hidden"},
            {"steps": 7},
            {"steps": True},
            {"steps": 3},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_public_geographic_total_uc(**kwargs)


if __name__ == "__main__":
    import unittest
    unittest.main()
