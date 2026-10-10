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

from .determinism import deterministic_id
from .injected_scenario import ScenarioEvent
from .safety_protocol import SafetyProtocolConfig
from .snapshots import SnapshotRecord, SnapshotType
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

        if dict(self.mapping.gatekeeper_base_weights) != dict(
            self.stage4.gatekeeper.weights
        ):
            raise ValueError(
                "temperament gatekeeper neutral weights must equal Stage-4 weights"
            )
        if dict(self.mapping.base_body_weights) != dict(
            self.stage4.value_needs.weights
        ):
            raise ValueError(
                "temperament neutral body weights must equal Stage-4 need weights"
            )
        if self.mapping.base_inertia != self.stage4.competition.inertia:
            raise ValueError(
                "temperament neutral inertia must equal Stage-4 inertia"
            )


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
        lineage_id: str | None = None,
        lineage_parent_id: str | None = None,
        lineage_copy_point: str | None = None,
        battery_copy: bool = False,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: tuple[ScenarioEvent, ...] = (),
    ) -> None:
        config.validate()
        if not individual_id:
            raise ValueError("Stage-5 individual_id must not be empty")
        self.individual_id = individual_id
        self.lineage_parent_id = lineage_parent_id
        self.lineage_copy_point = lineage_copy_point
        self._battery_copy_requested = bool(battery_copy)

        self._birth_world_config = world_config
        self._birth_layout = layout
        self._birth_safety_config = safety_config
        self._birth_safety_facts = safety_facts
        self._birth_protected_integrity_threshold = protected_integrity_threshold

        self.temperament_projection = TemperamentProjection(
            temperament=config.temperament,
            mapping=config.mapping,
            individual_id=individual_id,
            lineage_id=lineage_id,
            parent_id=lineage_parent_id,
            copy_snapshot_id=lineage_copy_point,
            battery_copy=battery_copy,
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
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=scenario_events,
        )

    @property
    def temperament_parameters(self) -> ParametresTemperament:
        return self.temperament_projection.parameters

    @property
    def stage5_config(self) -> Stage5Config:
        return self._stage5_config

    @property
    def battery_copy(self) -> bool:
        return self.temperament_projection.battery_copy

    def create_copy(
        self,
        *,
        copy_ref: str,
        battery_copy: bool = False,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: tuple[ScenarioEvent, ...] = (),
    ) -> tuple["Stage5Runtime", SnapshotRecord]:
        """Create an isolated individual from a complete coherent copy snapshot."""
        if not copy_ref:
            raise ValueError("copy_ref must not be empty")
        if self.scheduler.active_attempt is not None:
            raise RuntimeError("copies may be created only at a coherent step boundary")

        snapshots = self.stage3.substrate.snapshots
        record = snapshots.take(
            snapshot_type=SnapshotType.COPY,
            individual_id=self.individual_id,
            t_monde=self.scheduler.t_monde,
            cycle=0,
            attempt_ref=None,
            owners=self.causal_owners,
            versions={
                "stage5": self._stage5_config.version,
                "temperament_mapping": (
                    self.temperament_projection.mapping_version
                ),
                "world_physics": self.world.config.version,
            },
            context={
                "copy_ref": copy_ref,
                "battery_copy": battery_copy,
                "fresh_scenario_id": scenario_id,
                "fresh_scenario_version": scenario_version,
            },
        )
        child_id = deterministic_id(
            "individual-copy-v1",
            self.individual_id,
            record.id,
            copy_ref,
        )
        child = Stage5Runtime(
            world_config=self._birth_world_config,
            layout=self._birth_layout,
            safety_config=self._birth_safety_config,
            safety_facts=self._birth_safety_facts,
            protected_integrity_threshold=(
                self._birth_protected_integrity_threshold
            ),
            config=self._stage5_config,
            individual_id=child_id,
            lineage_id=self.temperament_projection.lineage_id,
            lineage_parent_id=self.individual_id,
            lineage_copy_point=record.id,
            battery_copy=battery_copy,
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=scenario_events,
        )

        payload = snapshots.export_payload(record.id)
        owner_states = payload.get("owner_states")
        if not isinstance(owner_states, dict):
            raise ValueError("copy snapshot owner state is malformed")
        child_owners = {
            owner.owner_id: owner
            for owner in child.causal_owners
        }
        inherited_owner_ids = set(owner_states)
        child_owner_ids = set(child_owners)
        fresh_external_scenario = scenario_id is not None
        if fresh_external_scenario:
            # The new scenario belongs to the external branch environment, not
            # to copied individual identity. It starts from its own initial state.
            child_owner_ids_without_scenario = child_owner_ids - {"scenario"}
            inherited_without_scenario = inherited_owner_ids - {"scenario"}
            if child_owner_ids_without_scenario != inherited_without_scenario:
                raise ValueError("copy owner set does not match parent snapshot")
        elif inherited_owner_ids != child_owner_ids:
            raise ValueError("copy owner set does not match parent snapshot")

        for owner_id in sorted(owner_states):
            if fresh_external_scenario and owner_id == "scenario":
                continue
            state = owner_states[owner_id]
            if owner_id == "s_t":
                child.s_t.restore_copy_causal_state(state)
            elif owner_id == "snapshots_and_individual_parameters":
                child.temperament_projection.restore_copy_causal_state(state)
            else:
                child_owners[owner_id].restore_causal_state(state)

        parent_event = {
            "emitter": "stage5.copy",
            "kind": "copy_created",
            "t_monde": self.scheduler.t_monde,
            "parent_individual": self.individual_id,
            "child_individual": child_id,
            "copy_ref": copy_ref,
            "copy_snapshot_id": record.id,
            "battery_copy": battery_copy,
        }
        self.journal.append(
            event_id=deterministic_id(
                "journal-event-v1",
                "stage5.copy",
                "parent",
                self.individual_id,
                child_id,
                record.id,
                copy_ref,
            ),
            causal_event=parent_event,
        )
        child.journal.append(
            event_id=deterministic_id(
                "journal-event-v1",
                "stage5.copy",
                "child",
                self.individual_id,
                child_id,
                record.id,
                copy_ref,
            ),
            causal_event={
                "emitter": "stage5.copy",
                "kind": "copy_branch_started",
                "t_monde": child.scheduler.t_monde,
                "individual": child_id,
                "parent_individual": self.individual_id,
                "copy_ref": copy_ref,
                "shared_prefix_snapshot_id": record.id,
                "battery_copy": battery_copy,
            },
        )
        return child, record

    @property
    def causal_owners(self):
        owners = list(super().causal_owners)
        if all(
            owner.owner_id != self.temperament_projection.owner_id
            for owner in owners
        ):
            owners.append(self.temperament_projection)
        return tuple(owners)
