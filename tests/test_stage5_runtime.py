from __future__ import annotations

import unittest

from i0.modules import StaticSafetyFacts
from i0.temperament import (
    LinearTemperamentCurve,
    Temperament,
    TemperamentMappingConfig,
)
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage5_copies import Stage5CopyManager
from lab.stage5_runtime import Stage5Config, Stage5Runtime
from lab.world import Position, WorldLayout

from test_stage4_runtime import runtime as stage4_runtime
from test_stage4_runtime import stage4_config, world_config


def temperament_mapping() -> TemperamentMappingConfig:
    return TemperamentMappingConfig(
        version="stage5-mapping-test-v1",
        gatekeeper_base_weights={
            "b": 1.0,
            "n": 1.0,
            "urg": 1.0,
            "risk": 1.0,
            "value": 1.0,
        },
        gatekeeper_alpha={
            "b": 0.5,
            "n": 0.5,
            "urg": 0.0,
            "risk": 0.6,
            "value": 0.5,
        },
        reward_extrinsic_alpha=0.5,
        risk_k_pi=0.5,
        risk_alpha_pi=0.6,
        uncertainty_k_chi=0.4,
        protective_threshold_delta=0.1,
        base_inertia=0.1,
        goal_protection_inertia_curve=LinearTemperamentCurve(
            at_minus_one=0.02,
            at_zero=0.1,
            at_plus_one=0.2,
        ),
        base_body_weights={
            "energy": 1.0,
            "food": 1.0,
            "water": 1.0,
            "integrity": 1.0,
        },
        integrity_weight_curve=LinearTemperamentCurve(
            at_minus_one=0.7,
            at_zero=1.0,
            at_plus_one=1.5,
        ),
        discount_beta=0.8,
    )


def stage5_runtime(
    *,
    temperament: Temperament | None = None,
    individual_id: str = "stage5-parent",
    layout: WorldLayout | None = None,
) -> Stage5Runtime:
    return Stage5Runtime(
        world_config=world_config(),
        layout=layout or WorldLayout(
            water_sources=frozenset({Position(4, 2)}),
        ),
        safety_config=SafetyProtocolConfig(
            version="stage5-safety-test-v1",
            lethal_max=2,
            mode="campaign",
        ),
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
        config=Stage5Config(
            version="stage5-test-v1",
            temperament=temperament or Temperament(0, 0, 0, 0, 0),
            mapping=temperament_mapping(),
            stage4=stage4_config(),
        ),
        individual_id=individual_id,
    )


class Stage5RuntimeTests(unittest.TestCase):
    def test_neutral_tau_reproduces_stage4_behavior(self) -> None:
        neutral = stage5_runtime()
        reference = stage4_runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(4, 2)}),
            )
        )

        neutral_results = [neutral.run_step() for _ in range(4)]
        reference_results = [reference.run_step() for _ in range(4)]

        self.assertEqual(
            [result.command_primitive for result in neutral_results],
            [result.command_primitive for result in reference_results],
        )
        self.assertEqual(
            neutral.world.export_causal_state(),
            reference.world.export_causal_state(),
        )

    def test_causal_owners_include_single_temperament_projection(self) -> None:
        runtime = stage5_runtime()
        owner_ids = [owner.owner_id for owner in runtime.causal_owners]
        self.assertEqual(len(owner_ids), len(set(owner_ids)))
        self.assertEqual(
            owner_ids.count("snapshots_and_individual_parameters"),
            1,
        )

    def test_copy_has_new_identity_and_same_causal_state_at_copy_point(self) -> None:
        parent = stage5_runtime()
        parent.run_step()
        parent_state = {
            owner.owner_id: owner.export_causal_state()
            for owner in parent.causal_owners
        }

        copy = Stage5CopyManager().create_copy(
            parent=parent,
            child_id="battery-copy-001",
            battery_copy=True,
        )
        child = copy.runtime

        self.assertEqual(child.individual_id, "battery-copy-001")
        self.assertEqual(copy.lineage.parent_id, parent.individual_id)
        self.assertTrue(copy.lineage.battery_copy)
        self.assertEqual(
            copy.lineage.parent_journal_head,
            parent.journal.head_hash,
        )

        child_state = {
            owner.owner_id: owner.export_causal_state()
            for owner in child.causal_owners
        }
        for owner_id in parent_state:
            if owner_id == "s_t":
                continue
            self.assertEqual(child_state[owner_id], parent_state[owner_id])

        self.assertEqual(
            child_state["s_t"]["current"]["version"],
            parent_state["s_t"]["current"]["version"],
        )
        self.assertEqual(
            child_state["s_t"]["current"]["individual_id"],
            "battery-copy-001",
        )

    def test_copy_execution_never_mutates_parent(self) -> None:
        parent = stage5_runtime()
        parent.run_step()
        state_before = {
            owner.owner_id: owner.export_causal_state()
            for owner in parent.causal_owners
        }
        journal_before = parent.journal.canonical_bytes()

        child = Stage5CopyManager().create_copy(
            parent=parent,
            child_id="battery-copy-002",
            battery_copy=True,
        ).runtime
        child.run_step()
        child.run_step()

        state_after = {
            owner.owner_id: owner.export_causal_state()
            for owner in parent.causal_owners
        }
        self.assertEqual(state_after, state_before)
        self.assertEqual(parent.journal.canonical_bytes(), journal_before)

    def test_copy_is_refused_mid_step(self) -> None:
        parent = stage5_runtime()
        parent.stage3.open_step()

        with self.assertRaises(RuntimeError):
            Stage5CopyManager().create_copy(
                parent=parent,
                child_id="illegal-copy",
                battery_copy=True,
            )


if __name__ == "__main__":
    unittest.main()
