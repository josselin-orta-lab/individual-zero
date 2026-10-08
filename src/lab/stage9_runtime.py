"""Stage-9 Causal Model runtime integration on the frozen Stage-8 substrate.

Only the Causal Model owns learned contingency and safety statuses. Stage 3
Action Control reads them through CanonicalSafetyFacts; the runtime only wires
interfaces, phase-5 publication and journaling. No oracle or direct world reads.
The evidence producer and hypothesis lifecycle remain explicit Stage-9 work.
"""
from __future__ import annotations

from dataclasses import dataclass

from i0.equipment import EquipmentModel
from i0.modules.agency_comparator import AgencyComparator, AgencyComparatorConfig
from i0.modules.action_control import StaticSafetyFacts
from i0.modules.causal_model import (
    CanonicalSafetyFacts, CausalModel, CausalModelConfig,
)
from lab.world import WorldLayout, WorldPhysicsConfig
from lab.safety_protocol import SafetyProtocolConfig

from .stage8_runtime import Stage8Config, Stage8Runtime


@dataclass(frozen=True, slots=True)
class Stage9Config:
    version: str
    stage8: Stage8Config
    causal: CausalModelConfig
    agency: AgencyComparatorConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 9 configuration requires a version")
        self.stage8.validate()
        self.causal.validate()
        self.agency.validate()


class Stage9Runtime(Stage8Runtime):
    individual_id = "i0-stage9"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage9Config,
        equipment: EquipmentModel,
    ) -> None:
        config.validate()
        self._stage9_config = config
        self.causal_model = CausalModel(config.causal)
        self._canonical_safety = CanonicalSafetyFacts(
            innate=safety_facts, causal_model=self.causal_model,
        )
        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=self._canonical_safety,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.stage8,
            equipment=equipment,
        )
        self.stage3.control.attach_agency_comparator(AgencyComparator(config.agency))

    @property
    def causal_owners(self):
        # INV-01 / INV-33: snapshot exactly one canonical causal owner.
        return (*super().causal_owners, self.causal_model)

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle,
            capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )

        def publish_causal_statuses(_ctx):
            # DC-05, section 5.3: a cycle reads only the previously
            # published facts; the batch commits atomically in phase 5.
            updates = self.causal_model.publish()
            for change in updates:
                self._write(
                    kind="causal_safety_status_published",
                    cycle=cycle,
                    data={
                        "contingency_ref": change.contingency_ref,
                        "old_status": change.before,
                        "new_status": change.after,
                        "contingency_version": change.version,
                        "evidence_ref": change.evidence_ref,
                        "episode_ref": change.episode_ref,
                        "causal_model_version": self.causal_model.version,
                    },
                )

        hooks[5]["causal_model"] = publish_causal_statuses
        return hooks
