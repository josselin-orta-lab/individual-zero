"""Stage-8 online per-source precision, INV-01/05/27/33, spec 11.2."""
from __future__ import annotations

import unittest

from i0.modules.active_precision import (
    ActivePerceptualPrecision, PrecisionConfig, PrecisionVerification
)
from i0.modules.perception import SymbolicPerception
from lab.stage8_reference_fixture import build_stage8_reference_runtime


def model():
    return ActivePerceptualPrecision(PrecisionConfig(
        version="precision-test-v1", prior_weight=2,
        initial_rmse_by_source={
            "world_symbolic": 1.0, "body_telemetry": 2.0,
        },
        variance_floor=0.01, maximum_precision=10,
    ))


def confirmation(identifier="verification-a", **changes):
    attrs = dict(
        identifier=identifier,
        source="world_symbolic",
        independent_observation_ref=f"physical:{identifier}",
        emission_step=1, observation_step=2,
        squared_error=0.0, anchor="monde",
        independent_provenance=True,
    )
    attrs.update(changes)
    return PrecisionVerification(**attrs)


class PrecisionTests(unittest.TestCase):
    def test_prior_per_source_and_later_independent_update(self):
        m = model()
        self.assertEqual(m.precision("world_symbolic"), 1.0)
        self.assertEqual(m.precision("body_telemetry"), 0.5)
        m.integrate(confirmation())
        self.assertEqual(m.precision("world_symbolic"), 1.0)
        changes = m.publish()
        self.assertEqual(len(changes), 1)
        self.assertGreater(m.precision("world_symbolic"), 1.0)
        self.assertEqual(m.precision("body_telemetry"), 0.5)

    def test_correlated_and_rollback_observations_cannot_train(self):
        m = model()
        for i, data in enumerate((
            {"independent_provenance": False},
            {"observation_step": 1},
            {"anchor": "derived"},
            {"oracle_derived": True},
            {"rollback_cancelled": True},
        )):
            m.integrate(confirmation(f"invalid-{i}", **data))
        self.assertEqual(m.publish(), ())
        self.assertEqual(m.precision("world_symbolic"), 1.0)
        m.integrate(confirmation("a", independent_observation_ref="physical:same"))
        m.integrate(confirmation("b", independent_observation_ref="physical:same"))
        self.assertEqual(len(m.publish()), 1)

    def test_snapshots_include_pending_and_deduplication_state(self):
        first = model()
        first.integrate(confirmation())
        state = first.export_causal_state()
        second = model()
        second.restore_causal_state(state)
        self.assertEqual(second.export_causal_state(), state)
        self.assertEqual(first.publish(), second.publish())
        self.assertEqual(first.export_causal_state(), second.export_causal_state())

    def test_independent_precision_verification_flows_through_stage8_runtime(self):
        runtime = build_stage8_reference_runtime()
        self.assertEqual(runtime.run_step().execution_status, "applied")
        prior = runtime.precision_active.precision("world_symbolic")
        runtime.integrate_precision_verification(confirmation(
            "physical-comparator-v1",
            emission_step=0, observation_step=1,
            independent_observation_ref="physical:step1:position",
        ))
        self.assertEqual(runtime.precision_active.precision("world_symbolic"), prior)
        self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertGreater(runtime.precision_active.precision("world_symbolic"), prior)
        self.assertIn(b"perceptual_precision_update_published", runtime.journal.canonical_bytes())

    def test_perception_only_owner_and_stage8_nonlethal_publication(self):
        legacy = SymbolicPerception()
        self.assertIsNone(legacy.active_precision)
        runtime = build_stage8_reference_runtime()
        self.assertIsNotNone(runtime.stage3.perception.active_precision)
        self.assertIs(runtime.stage3.perception.active_precision, runtime.precision_active)
        self.assertEqual(runtime.precision_active.version, 0)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        self.assertGreater(runtime.precision_active.version, 0)
        self.assertEqual(runtime.precision_active.export_causal_state()["source_sums"], [])
        self.assertIn("precision_active", runtime.stage3.perception.export_causal_state())


if __name__ == "__main__":
    unittest.main()
