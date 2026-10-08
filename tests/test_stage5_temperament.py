from __future__ import annotations

import unittest

from i0.temperament import (
    LinearTemperamentCurve,
    Temperament,
    TemperamentMappingConfig,
    TemperamentProjection,
)


def mapping_config() -> TemperamentMappingConfig:
    return TemperamentMappingConfig(
        version="stage5-temperament-test-v1",
        gatekeeper_base_weights={
            "b": 1.1,
            "n": 0.9,
            "urg": 1.2,
            "risk": 1.3,
            "value": 0.8,
        },
        gatekeeper_alpha={
            "b": 0.4,
            "n": 0.5,
            "urg": 99.0,  # forbidden path: urgency has no temperament dimension
            "risk": 0.6,
            "value": 0.7,
        },
        reward_extrinsic_alpha=0.5,
        risk_k_pi=0.7,
        risk_alpha_pi=0.8,
        uncertainty_k_chi=0.4,
        protective_threshold_delta=0.2,
        base_inertia=0.15,
        goal_protection_inertia_curve=LinearTemperamentCurve(
            at_minus_one=0.05,
            at_zero=0.15,
            at_plus_one=0.25,
        ),
        base_body_weights={
            "energy": 1.0,
            "food": 1.1,
            "water": 1.2,
            "integrity": 1.3,
        },
        integrity_weight_curve=LinearTemperamentCurve(
            at_minus_one=0.8,
            at_zero=1.3,
            at_plus_one=1.8,
        ),
        discount_beta=0.8,
    )


class TemperamentProjectionTests(unittest.TestCase):
    def test_neutral_tau_reproduces_neutral_stage4_values(self) -> None:
        config = mapping_config()
        projection = TemperamentProjection(
            temperament=Temperament(0.0, 0.0, 0.0, 0.0, 0.0),
            mapping=config,
        )
        p = projection.parameters

        self.assertEqual(
            dict(p.gatekeeper_weights),
            dict(config.gatekeeper_base_weights),
        )
        self.assertEqual(p.extrinsic_value_gain, 1.0)
        self.assertEqual(p.risk_penalty_scale, config.risk_k_pi)
        self.assertEqual(
            p.uncertainty_penalty_scale,
            config.uncertainty_k_chi / 2.0,
        )
        self.assertEqual(
            p.protective_threshold_reduction,
            config.protective_threshold_delta / 2.0,
        )
        self.assertEqual(p.inertia, config.base_inertia)
        self.assertEqual(dict(p.body_weights), dict(config.base_body_weights))
        self.assertEqual(p.discount_beta, config.discount_beta)

    def test_threat_sensitivity_changes_only_authorized_stage5_paths(self) -> None:
        config = mapping_config()
        low = TemperamentProjection(
            temperament=Temperament(0.0, -1.0, 0.0, 0.0, 0.0),
            mapping=config,
        ).parameters
        high = TemperamentProjection(
            temperament=Temperament(0.0, 1.0, 0.0, 0.0, 0.0),
            mapping=config,
        ).parameters

        self.assertGreater(
            high.gatekeeper_weights["risk"],
            low.gatekeeper_weights["risk"],
        )
        self.assertEqual(
            high.gatekeeper_weights["urg"],
            low.gatekeeper_weights["urg"],
        )
        self.assertGreater(high.risk_penalty_scale, low.risk_penalty_scale)
        self.assertGreater(
            high.uncertainty_penalty_scale,
            low.uncertainty_penalty_scale,
        )
        self.assertGreater(
            high.protective_threshold_reduction,
            low.protective_threshold_reduction,
        )
        self.assertGreater(
            high.body_weights["integrity"],
            low.body_weights["integrity"],
        )

    def test_exploration_does_not_modify_competition_gain(self) -> None:
        config = mapping_config()
        low = TemperamentProjection(
            temperament=Temperament(0.0, 0.0, -1.0, 0.0, 0.0),
            mapping=config,
        ).parameters
        high = TemperamentProjection(
            temperament=Temperament(0.0, 0.0, 1.0, 0.0, 0.0),
            mapping=config,
        ).parameters

        self.assertGreater(
            high.gatekeeper_weights["n"],
            low.gatekeeper_weights["n"],
        )
        self.assertEqual(low.risk_penalty_scale, high.risk_penalty_scale)
        self.assertEqual(low.inertia, high.inertia)

    def test_goal_protection_changes_inertia_and_gatekeeper_relevance_only(self) -> None:
        config = mapping_config()
        low = TemperamentProjection(
            temperament=Temperament(0.0, 0.0, 0.0, -1.0, 0.0),
            mapping=config,
        ).parameters
        high = TemperamentProjection(
            temperament=Temperament(0.0, 0.0, 0.0, 1.0, 0.0),
            mapping=config,
        ).parameters

        self.assertGreater(high.inertia, low.inertia)
        self.assertGreater(
            high.gatekeeper_weights["b"],
            low.gatekeeper_weights["b"],
        )
        self.assertEqual(
            high.gatekeeper_weights["risk"],
            low.gatekeeper_weights["risk"],
        )

    def test_restore_rejects_tau_mutation(self) -> None:
        projection = TemperamentProjection(
            temperament=Temperament(0.25, -0.5, 0.0, 0.75, 0.0),
            mapping=mapping_config(),
        )
        state = projection.export_causal_state()
        state["tau"]["goal_protection"] = -0.75

        with self.assertRaisesRegex(ValueError, "INV-30"):
            projection.restore_causal_state(state)

    def test_out_of_range_tau_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TemperamentProjection(
                temperament=Temperament(1.1, 0.0, 0.0, 0.0, 0.0),
                mapping=mapping_config(),
            )


if __name__ == "__main__":
    unittest.main()
