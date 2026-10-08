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

        original_memory = hooks[1]["memory"]

        def observe_then_ingest(_ctx):
            # Only Perception's accessible body telemetry, never WorldBody.
            self.causal_model.observe_followup_capture(
                t_monde=capture.t_monde,
                integrity=float(capture.body["integrity"]),
            )
            before = len(self.memory.episodes)
            original_memory(_ctx)
            newly_closed = self.memory.episodes[before:]
            if not newly_closed:
                return
            autobiography = self._autobiographical_events(cycle=cycle)
            for episode in newly_closed:
                candidates = self.causal_model.ingest_closed_autobiographical_episode(
                    episode_ref=episode.id,
                    event_refs=episode.event_refs,
                    autobiographical_events=autobiography,
                )
                for item in candidates:
                    self._write(
                        kind="causal_lived_evidence_admitted",
                        cycle=cycle,
                        data={
                            "contingency_ref": item.contingency_ref,
                            "episode_ref": item.episode_ref,
                            "observation_ref": item.observation_ref,
                            "evidence_ref": item.identifier,
                            "harm_observed": item.harm_observed,
                        },
                    )

        hooks[1]["memory"] = observe_then_ingest

        def publish_causal_statuses(_ctx):
            # DC-05, section 5.3: a cycle reads only the previously
            # published facts; the batch commits atomically in phase 5.
            inference_changes = self.causal_model.publish_causal_inference()
            for change in inference_changes:
                self._write(
                    kind="causal_inference_status_published",
                    cycle=cycle,
                    data={
                        "contingency_ref": change.contingency_ref,
                        "old_status": change.before,
                        "new_status": change.after,
                        "contingency_version": change.version,
                        "evidence_ref": change.evidence_ref,
                        "protocol": change.protocol,
                        "causal_model_version": self.causal_model.version,
                    },
                )
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

    def _dispatch_decision(
        self, *, proposal, prepared, admission, cycle: int, sent_t_monde: int,
    ):
        # Action Control first validates and executes the command. The Causal
        # Model is never allowed to count a blocked or lethal/rolled-back step.
        captured = self.stage3._capture
        execution = super()._dispatch_decision(
            proposal=proposal, prepared=prepared, admission=admission,
            cycle=cycle, sent_t_monde=sent_t_monde,
        )
        if (execution.status == "applied"
            and prepared.command.primitive == "manger"
            and captured is not None
            and proposal.option.motive_ref.type == "active_goal"):
            target = prepared.command.parameters.get("target")
            if target in {"berry_a", "berry_b"}:
                self.causal_model.record_applied_food_exposure(
                    t_monde=sent_t_monde, resource_kind=str(target),
                    option_ref=proposal.option.id,
                    motive_ref=proposal.option.motive_ref.id,
                    integrity_before=float(captured.body["integrity"]),
                )
        return execution

