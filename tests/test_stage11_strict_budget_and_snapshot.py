"""Stage11 public strict-budget and canonical safety snapshot regression.

These tests are software-contract checks only. Synthetic DC-05 safety evidence
in the isolated unit test is NOT physical observation or scientific proof.
"""
from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy

from i0.modules.action_control import Admissibility
from i0.modules.causal_model import SafetyEvidence
from lab.snapshots import SnapshotType
from lab.stage11_degraded_budget_probe import (
    VARIANTS, run_public_strict_geographic_budget,
)
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime


class Stage11StrictBudgetTests(TestCase):
    def test_zero_planning_uc_reports_incomplete_and_withdraws_offers(self):
        row = run_public_strict_geographic_budget(variant="planning_0")
        self.assertEqual(row.classification, "development_only_not_heldout")
        self.assertIsNone(row.scientific_verdict)
        self.assertFalse(row.heldout)
        self.assertEqual(row.planning_envelope_uc, 0)
        self.assertGreater(row.rejected_preflight_attempts, 0)
        self.assertEqual(row.accepted_preflight_uc, 0)
        self.assertEqual(row.charged_preflight_consultations, 0)
        self.assertEqual(row.preflight_charge_order_violations, 0)
        self.assertEqual(row.applied_geographic_commands, 0)
        self.assertEqual(row.remaining_offered_targets, 0)
        self.assertGreater(row.rejected_requested_uc, 0)
        self.assertIn(
            "geographic_admissibility_preflight",
            row.budget_deferred_operations,
        )
        self.assertEqual(row.malformed_defer_events, 0)
        self.assertEqual(
            row.physically_perceived_distinct_sites,
            row.confirmed_geographic_sites,
        )
        print("stage11_public_strict_uc=" + row.to_json())

    def test_one_planning_uc_never_fabricates_a_completed_plan(self):
        row = run_public_strict_geographic_budget(variant="planning_1")
        self.assertEqual(row.planning_envelope_uc, 1)
        self.assertGreater(row.accepted_preflight_uc, 0)
        self.assertEqual(
            row.charged_preflight_consultations, row.accepted_preflight_uc,
        )
        self.assertEqual(row.preflight_charge_order_violations, 0)
        self.assertGreater(row.rejected_build_attempts, 0)
        self.assertEqual(row.accepted_build_uc, 0)
        self.assertEqual(row.applied_geographic_commands, 0)
        self.assertEqual(row.remaining_offered_targets, 0)
        self.assertIn("planning_build", row.budget_deferred_operations)
        self.assertEqual(row.malformed_defer_events, 0)
        print("stage11_public_strict_uc=" + row.to_json())

    def test_zero_exploration_uc_defers_targets_not_physical_visits(self):
        row = run_public_strict_geographic_budget(variant="exploration_0")
        self.assertEqual(row.exploration_envelope_uc, 0)
        self.assertGreater(row.rejected_exploration_attempts, 0)
        # Phase-0 consultations are now legitimately paid before an
        # independent Exploration owner later rejects its own charge.
        self.assertEqual(
            row.charged_preflight_consultations, row.accepted_preflight_uc,
        )
        self.assertEqual(row.preflight_charge_order_violations, 0)
        self.assertEqual(row.applied_geographic_commands, 0)
        self.assertEqual(row.remaining_offered_targets, 0)
        self.assertIn("exploration_observe", row.budget_deferred_operations)
        self.assertEqual(
            row.physically_perceived_distinct_sites,
            row.confirmed_geographic_sites,
        )
        self.assertEqual(row.malformed_defer_events, 0)
        print("stage11_public_strict_uc=" + row.to_json())

    def test_three_planning_uc_can_pay_preflight_and_one_build(self):
        row = run_public_strict_geographic_budget(variant="planning_3")
        self.assertEqual(row.planning_envelope_uc, 3)
        self.assertGreater(row.accepted_preflight_uc, 0)
        self.assertEqual(
            row.charged_preflight_consultations, row.accepted_preflight_uc,
        )
        self.assertEqual(row.preflight_charge_order_violations, 0)
        self.assertGreater(row.accepted_build_uc, 0)
        self.assertEqual(row.rejected_preflight_attempts, 0)
        self.assertEqual(row.rejected_build_attempts, 0)
        self.assertEqual(
            row.physically_perceived_distinct_sites,
            row.confirmed_geographic_sites,
        )
        self.assertEqual(row.malformed_defer_events, 0)
        print("stage11_public_strict_uc=" + row.to_json())

    def test_zero_uc_never_calls_early_action_control_even_before_the_charge(self):
        # This catches the previous architectural fault, which merely
        # recorded a rejected charge after an unpaid Phase-0 lookup.
        with patch.object(
            Stage11Runtime,
            "_geographic_frontier_targets",
            side_effect=AssertionError("unpaid early admissibility lookup"),
        ):
            row = run_public_strict_geographic_budget(variant="planning_0")
        self.assertGreater(row.rejected_preflight_attempts, 0)
        self.assertEqual(row.charged_preflight_consultations, 0)

    def test_early_lookup_is_observably_after_an_accepted_charge(self):
        original = Stage11Runtime._geographic_frontier_targets
        observed = []

        def track_after_charge(runtime, capture, *, raw_targets=None):
            accepted = [
                entry.causal_event for entry in runtime.journal.entries
                if entry.causal_event.get("kind") == "compute_charge"
                and entry.causal_event.get("t_monde") == capture.t_monde
                and entry.causal_event.get("cycle")
                == runtime.compute_budget.cycle
                and entry.causal_event.get("data", {}).get("module")
                == "planning"
                and entry.causal_event.get("data", {}).get("operation")
                == "geographic_admissibility_preflight"
                and entry.causal_event["data"].get("accepted") is True
            ]
            if len(accepted) != 1:
                raise AssertionError(
                    "canonical safety preflight ran before paid UC"
                )
            observed.append((capture.t_monde, runtime.compute_budget.cycle))
            return original(runtime, capture, raw_targets=raw_targets)

        with patch.object(
            Stage11Runtime, "_geographic_frontier_targets",
            track_after_charge,
        ):
            row = run_public_strict_geographic_budget(variant="planning_1")
        self.assertTrue(observed)
        self.assertEqual(len(observed), row.charged_preflight_consultations)
        self.assertEqual(row.preflight_charge_order_violations, 0)

    def test_all_strict_public_scenarios_replay_exactly_and_are_bounded(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                left = run_public_strict_geographic_budget(variant=variant)
                right = run_public_strict_geographic_budget(variant=variant)
                self.assertEqual(left, right)
                self.assertEqual(left.to_json(), right.to_json())
                self.assertEqual(left.steps, 3)
                self.assertGreaterEqual(left.confirmed_geographic_sites, 1)
                self.assertEqual(left.preflight_charge_order_violations, 0)
                self.assertLessEqual(
                    len(left.budget_deferred_operations), 3 * 5,
                    "one budget deferral per cognitive cycle at most",
                )
        for bad in (
            {"variant": "unregistered"},
            {"variant": "planning_0", "steps": 5},
            {"variant": "planning_1", "steps": True},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                run_public_strict_geographic_budget(**bad)


def _unit_only_lethal_evidence(identifier: str, step: int) -> SafetyEvidence:
    # Explicitly isolated fabricated unit fixture; NEVER a physical-world
    # witness or an assertion of scientifically established harm.
    return SafetyEvidence(
        identifier=identifier,
        contingency_ref="lethal-zone:2,1",
        predicate="lethal_zone",
        subject_ref="2,1",
        context_signature="global",
        episode_ref=f"synthetic-test-episode:{identifier}",
        observation_ref=f"synthetic-test-observation:{identifier}",
        emission_step=step,
        observation_step=step + 1,
        harm_observed=True,
        source="monde",
        independent_episode=True,
        comparable_context=True,
        alternative_cause_sufficient=False,
        exposure_motivated_independently=True,
    )


class Stage11CanonicalSnapshotTests(TestCase):
    def test_snapshot_restores_live_admissibility_and_geographic_owner(self):
        runtime = build_stage11_reference_runtime(enable_geography=True)
        physical_capture = runtime.stage3.open_step()
        geo = runtime.exploration.geographic
        self.assertIsNotNone(geo)
        runtime.exploration.observe_geographic_capture(physical_capture)
        candidates = runtime.exploration.geographic_cibles(physical_capture)
        self.assertTrue(candidates)
        self.assertEqual(candidates[0].direction, "north")
        first, excluded = runtime._geographic_frontier_targets(
            physical_capture,
        )
        self.assertEqual(first[0].direction, "north")
        self.assertEqual(excluded, ())
        initial_geo = deepcopy(runtime.exploration.export_causal_state())
        initial_model = deepcopy(runtime.causal_model.export_causal_state())
        snapshots = runtime.stage3.substrate.snapshots
        record = snapshots.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id=runtime.individual_id,
            t_monde=physical_capture.t_monde, cycle=0,
            attempt_ref=None, owners=runtime.causal_owners,
            versions={
                "cognition": runtime._stage11_config.version,
                "model": runtime.causal_model.config.version,
                "geography": geo.config.version,
            },
        )
        self.assertTrue(snapshots.verify(record.id))
        self.assertIn(runtime.exploration.owner_id, record.owner_ids)
        self.assertIn(runtime.causal_model.owner_id, record.owner_ids)

        # Unit-only fabricated DC-05 records exercise the *same* canonical
        # owner and live Action Control reader without claiming physical proof.
        runtime.causal_model.integrate(
            _unit_only_lethal_evidence("unit-harm-1", 1)
        )
        runtime.causal_model.integrate(
            _unit_only_lethal_evidence("unit-harm-2", 2)
        )
        runtime.causal_model.publish()
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=2, y=1),
            "known_lethal",
        )
        current, denied = runtime._geographic_frontier_targets(
            physical_capture,
        )
        self.assertTrue(current)
        self.assertNotEqual(current[0].direction, "north")
        self.assertIn(("north", (2, 1)), denied)
        geo.freeze_targets(candidates)
        self.assertNotEqual(
            runtime.exploration.export_causal_state(), initial_geo,
        )

        # The checkpoint restores all owner states. No private forbidden
        # map or cached decision can outlive the canonical source rollback.
        snapshots.restore(record.id, owners=runtime.causal_owners)
        self.assertEqual(
            runtime.exploration.export_causal_state(), initial_geo,
        )
        self.assertEqual(
            runtime.causal_model.export_causal_state(), initial_model,
        )
        self.assertEqual(
            runtime._canonical_safety.zone_status(x=2, y=1),
            "unknown",
        )
        restored, exclusions = runtime._geographic_frontier_targets(
            physical_capture,
        )
        self.assertEqual(exclusions, ())
        self.assertEqual(restored[0].direction, "north")
        self.assertTrue(runtime.journal.verify())
        self.assertTrue(snapshots.verify(record.id))


if __name__ == "__main__":
    import unittest
    unittest.main()
