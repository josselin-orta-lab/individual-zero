"""Stage-5 temperament-enabled individual.

This layer reuses the completed Stage-4 cognitive loop and replaces only the
declared neutral temperament stubs with immutable projected parameters.

Spec: 7.3, 20.3 Stage 5, INV-30, INV-40.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from i0.modules import StaticSafetyFacts
from i0.temperament import (
    ParametresTemperament,
    Temperament,
    TemperamentMappingConfig,
    TemperamentProjection,
)

from .safety_protocol import SafetyProtocolConfig
from .stage4_runtime import Stage4Config, Stage4Runtime
from .world import WorldLayout, WorldPhysicsConfig


@dataclass(frozen=True, slots=True)
class Stage5Config:
    version: str
    temperament: Temperament
    mapping: TemperamentMappingConfig
    stage4: Stage4Config

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 5 config version must not be empty")
        self.temperament.validate()
        self.mapping.validate()
        self.stage4.validate()


class Stage5Runtime(Stage4Runtime):
    """Stage 4 loop plus birth-time temperament projection."""

    individual_id = "i0-stage5"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage5Config,
        individual_id: str = "i0-stage5",
        lineage_parent_id: str | None = None,
        lineage_copy_point: str | None = None,
        battery_copy: bool = False,
    ) -> None:
        config.validate()
        if not individual_id:
            raise ValueError("Stage-5 individual_id must not be empty")
        self.individual_id = individual_id
        self.lineage_parent_id = lineage_parent_id
        self.lineage_copy_point = lineage_copy_point
        self.battery_copy = battery_copy

        self._birth_world_config = world_config
        self._birth_layout = layout
        self._birth_safety_config = safety_config
        self._birth_safety_facts = safety_facts
        self._birth_protected_integrity_threshold = protected_integrity_threshold

        self.temperament_projection = TemperamentProjection(
            temperament=config.temperament,
            mapping=config.mapping,
        )
        params = self.temperament_projection.parameters

        stage4 = replace(
            config.stage4,
            version=f"{config.stage4.version}+temperament:{config.mapping.version}",
            gatekeeper=replace(
                config.stage4.gatekeeper,
                weights=dict(params.gatekeeper_weights),
            ),
            value_needs=replace(
                config.stage4.value_needs,
                weights=dict(params.body_weights),
            ),
            competition=replace(
                config.stage4.competition,
                inertia=params.inertia,
            ),
        )

        self._stage5_config = config
        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=stage4,
        )

    @property
    def temperament_parameters(self) -> ParametresTemperament:
        return self.temperament_projection.parameters

    @property
    def stage5_config(self) -> Stage5Config:
        return self._stage5_config

    def copy_constructor_kwargs(self) -> dict[str, object]:
        return {
            "world_config": self._birth_world_config,
            "layout": self._birth_layout,
            "safety_config": self._birth_safety_config,
            "safety_facts": self._birth_safety_facts,
            "protected_integrity_threshold": (
                self._birth_protected_integrity_threshold
            ),
            "config": self._stage5_config,
        }

    @property
    def causal_owners(self):
        owners = list(super().causal_owners)
        if all(
            owner.owner_id != self.temperament_projection.owner_id
            for owner in owners
        ):
            owners.append(self.temperament_projection)
        return tuple(owners)
