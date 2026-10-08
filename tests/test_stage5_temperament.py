from __future__ import annotations

import unittest

from i0.modules import (
    Temperament,
    TemperamentMappingConfig,
    TemperamentProjector,
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
            "urg": 0.3,
            "risk": 0.6,
            "value": 0.7,
        },
        extrinsic_alpha=0.5,
        risk_alpha=0.8,
        uncertainty_linear_strength=0.4,
        protective_threshold_linear_strength=0.25,
        inertia_linear_strength=0.5,
        integrity_weight_alpha=0.6,
        exploration_linear_strength=0.75,
        beta_neutral=0.8,
        beta_min=0.5,
        beta_max=0.95,
        beta_linear_span=0.1,
    )


class TemperamentProjectionTests(unittest.TestCase):
    def test_neutral_tau_reproduces_neutral_parameters_exactly(self) -> None:
        config = mapping_config()
        projector = TemperamentProjector(
            tau=Temperament(0.0, 0.0, 0.0, 0.0, 0.0),
            config=config,
        )
        p = projector.parameters

        self.assertEqual(dict(p.gatekeeper_weights), dict(config.gatekeeper_base_weights))
        self.assertEqual(p.extrinsic_value_gain, 1.0)
        self.assertEqual(p.risk_penalty_multiplier, 1.0)
        self.assertEqual(p.uncertainty_penalty_multiplier, 1.0)
        self.assertEqual(p.protective_threshold_delta_multiplier, 1.0)
        self.assertEqual(p.inertia_multiplier, 1.0)
        self.assertEqual(
            dict(p.body_weight_multipliers),
            {"energy": 1.0, "food": 1.0, "water": 1.0, "integrity": 1.0},
        )
        self.assertEqual(p.beta_individual, config.beta_neutral)
        self.assertEqual(p.exploration_multiplier, 1.0)

    def test_threat_sensitivity_increases_authorized_threat_paths(self) -> None:
        config = mapping_config()
        low = TemperamentProjector(
            tau=Temperament(0.0, -1.0, 0.0, 0.0, 0.0),
            config=config,
        ).parameters
        high = TemperamentProjector(
            tau=Temperament(0.0, 1.0, 0.0, 0.0, 0.0),
            config=config,
        ).parameters

        self.assertGreater(high.gatekeeper_weights["risk"], low.gatekeeper_weights["risk"])
        self.assertGreater(high.gatekeeper_weights["urg"], low.gatekeeper_weights["urg"])
        self.assertGreater(high.risk_penalty_multiplier, low.risk_penalty_multiplier)
        self.assertGreater(
            high.uncertainty_penalty_multiplier,
            low.uncertainty_penalty_multiplier,
        )
        self.assertGreater(
            high.body_weight_multipliers["integrity"],
            low.body_weight_multipliers["integrity"],
        )

    def test_exploration_never_changes_common_competition_gain(self) -> None:
        config = mapping_config()
        low = TemperamentProjector(
            tau=Temperament(0.0, 0.0, -1.0, 0.0, 0.0),
            config=config,
        ).parameters
        high = TemperamentProjector(
            tau=Temperament(0.0, 0.0, 1.0, 0.0, 0.0),
            config=config,
        ).parameters

        self.assertGreater(high.gatekeeper_weights["n"], low.gatekeeper_weights["n"])
        self.assertGreater(high.exploration_multiplier, low.exploration_multiplier)

    def test_restore_rejects_tau_mutation(self) -> None:
        config = mapping_config()
        projector = TemperamentProjector(
            tau=Temperament(0.25, -0.5, 0.0, 0.75, 0.0),
            config=config,
        )
        state = projector.export_causal_state()
        state["tau"]["goal_protection"] = -0.75

        with self.assertRaisesRegex(ValueError, "INV-30"):
            projector.restore_causal_state(state)

    def test_out_of_range_tau_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TemperamentProjector(
                tau=Temperament(1.1, 0.0, 0.0, 0.0, 0.0),
                config=mapping_config(),
            )


if __name__ == "__main__":
    unittest.main()
