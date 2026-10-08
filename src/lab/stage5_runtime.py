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
    ) -> None:
        config.validate()
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
    def causal_owners(self):
        owners = list(super().causal_owners)
        if all(
            owner.owner_id != self.temperament_projection.owner_id
            for owner in owners
        ):
            owners.append(self.temperament_projection)
        return tuple(owners)
