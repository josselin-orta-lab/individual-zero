"""Stage-9 Causal Model runtime integration on the frozen Stage-8 substrate.

Only the Causal Model owns learned contingency and safety statuses. Stage 3
Action Control reads them through CanonicalSafetyFacts; the runtime only wires
interfaces, phase-5 publication and journaling. No oracle or direct world reads.
The evidence producer and hypothesis lifecycle remain explicit Stage-9 work.
"""
from __future__ import annotations

from dataclasses import dataclass

from i0.contracts import Contribution
from i0.modules.action_control import Admissibility
from i0.modules.causal_test_planning import (
    Stage9OptionEvaluator, propose_executable_causal_test,
)
from i0.equipment import EquipmentModel
from i0.modules.simulator import state_from_capture
from .determinism import canonical_causal_bytes, sha256_hex
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
        # The Simulator only receives a read-only pointer to the canonical
        # Causal Model; no cached or consolidated correction state exists.
        self.simulator.attach_established_correction_source(self.causal_model)
        # Only the Stage-9 instance receives this test-specific guard. Goal
        # options and every Stage-7/8 reference evaluator remain unchanged.
        self.stage8_option_evaluator = Stage9OptionEvaluator(
            config=config.stage8.evaluation,
            stage6=self.option_evaluator,
            q_values=self.q_active,
        )
        self._causal_test_proposals_this_cycle = ()

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
                # Stage 9 §9.6: only Memory-closed DC-09 comparator reports
                # reach Causal Model; no comparator output becomes an
                # intervention or independent confirmation by itself.
                agency_reports = self.causal_model.ingest_closed_agency_comparisons(
                    episode_ref=episode.id,
                    event_refs=episode.event_refs,
                    autobiographical_events=autobiography,
                )
                for report in agency_reports:
                    self._write(
                        kind="causal_agency_evidence_admitted",
                        cycle=cycle,
                        data={
                            "evidence_ref": report.identifier,
                            "episode_ref": report.episode_ref,
                            "source_event_ref": report.event_ref,
                            "option_ref": report.option_ref,
                            "status": report.status,
                            "attribution": report.attribution,
                            "observed_t_monde": report.observed_t_monde,
                            "causal_status_changed": False,
                        },
                    )

        hooks[1]["memory"] = observe_then_ingest

        def publish_causal_statuses(_ctx):
            # INV-01/25/33: causal and safety statuses inhabit ONE canonical
            # owner. Prepare both publications before any journal write;
            # rollback its entire causal state if either rejects a batch.
            old = self.causal_model.export_causal_state()
            corrections_before = self.causal_model.established_prediction_corrections()
            try:
                inference_changes = self.causal_model.publish_causal_inference()
                safety_changes = self.causal_model.publish()
            except Exception:
                self.causal_model.restore_causal_state(old)
                raise
            corrections_after = self.causal_model.established_prediction_corrections()
            if corrections_after != corrections_before:
                self._write(
                    kind="causal_prediction_corrections_published",
                    cycle=cycle,
                    data={
                        "causal_model_version": self.causal_model.version,
                        "before": [
                            [rule.contingency_ref, rule.intervention_ref,
                             rule.agency_evidence_ref]
                            for rule in corrections_before
                        ],
                        "after": [
                            [rule.contingency_ref, rule.intervention_ref,
                             rule.agency_evidence_ref]
                            for rule in corrections_after
                        ],
                        "versioned_source": "causal_model",
                    },
                )
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
            for change in safety_changes:
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

        # §8.3 / §13.4: the Causal Model designates tests during production,
        # but Planning alone turns a target into a locally feasible option.
        # The Exploration P-48 evaluation is NOT implemented at Stage 9:
        # Stage9OptionEvaluator leaves these candidates unscored and unable
        # to cross a competition threshold.
        previous_causal_producer = hooks[1]["causal_model"]
        previous_planning_producer = hooks[1]["planning"]
        previous_registration = hooks[3]["competition"]

        def designate_causal_tests(ctx):
            self._causal_test_proposals_this_cycle = ()
            previous_causal_producer(ctx)
            self._causal_test_targets_this_cycle = (
                self.causal_model.proposer_test()
                if not self._cycle_degraded else ()
            )

        def plan_causal_tests(ctx):
            previous_planning_producer(ctx)
            if (
                st_before_cycle is None or self._cycle_degraded
                or not self._causal_test_targets_this_cycle
            ):
                return
            initial_state = state_from_capture(
                capture=capture,
                is_night=self.world.is_night(capture.t_monde),
            )
            proposals = []
            for target in self._causal_test_targets_this_cycle:
                if not self._charge(
                    module="planning", operation="planning_build",
                ):
                    break
                proposal = propose_executable_causal_test(
                    target=target,
                    initial_state=initial_state,
                    simulator=self.simulator,
                    st_version=st_before_cycle.version,
                    t_monde=capture.t_monde,
                    ttl_steps=self._stage6_config.planning.option_ttl_steps,
                )
                if proposal is None:
                    continue
                if (
                    self.stage3.control.verifier_plan_connu(proposal)
                    is Admissibility.INADMISSIBLE
                ):
                    continue
                self._publish_contribution(Contribution(
                    id=(
                        f"action-proposal:{proposal.option.id}:"
                        f"{capture.t_monde}:{cycle}"
                    ),
                    schema_version="mvp-v1.2.1",
                    type="proposed_action",
                    summary=(
                        f"causal test proposal for {target.contingency_ref}"
                    ),
                    subject_ref=f"option:{proposal.option.id}",
                    emitter_module="causal_model",
                    signal_family="causal_model",
                    confidence=1.0,
                    urgency=0.0,
                    risk=0.0,
                    value=0.0,
                    production_t=capture.t_monde,
                    production_cycle=cycle,
                    expires_at_step=proposal.option.expires_at_step,
                    payload=proposal,
                    provenance_inputs=(target.contingency_ref,),
                ))
                proposals.append(proposal)
                self._write(
                    kind="causal_test_option_proposed", cycle=cycle,
                    data={
                        "contingency_ref": target.contingency_ref,
                        "contingency_version": target.contingency_version,
                        "option_ref": proposal.option.id,
                        "primitive": target.primitive,
                        "motif_ref": target.motive_ref,
                        "intrinsic_evidence": "unavailable",
                    },
                )
            self._causal_test_proposals_this_cycle = tuple(proposals)

        def register_causal_tests(ctx):
            previous_registration(ctx)
            # Stale hypotheses, unsuitable current context, missing equipment
            # or degraded processing must never leave old tests executable.
            current_ids = {
                proposal.option.id
                for proposal in self._causal_test_proposals_this_cycle
            }
            for old in self.competition.candidate_proposals:
                if (
                    old.option.motive_ref.type == "test_causal"
                    and old.option.id not in current_ids
                ):
                    self.competition.invalidate_candidate(old.option.id)
            if self._cycle_degraded:
                return
            for proposal in self._causal_test_proposals_this_cycle:
                if not self._charge(
                    module="competition",
                    operation="competition_register",
                ):
                    break
                accepted = self._register_option_proposal(
                    proposal=proposal,
                    active_goal_id=(
                        None if self.goal_manager.active_goal is None
                        else self.goal_manager.active_goal.id
                    ),
                    t_monde=capture.t_monde,
                    cycle=cycle,
                )
                self._write(
                    kind="causal_test_option_registration", cycle=cycle,
                    data={
                        "option_ref": proposal.option.id,
                        "registered": accepted,
                        "intrinsic_evidence": "unavailable",
                    },
                )

        hooks[1]["causal_model"] = designate_causal_tests
        hooks[1]["planning"] = plan_causal_tests
        hooks[3]["competition"] = register_causal_tests
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
                    body_before=dict(captured.body),
                    position_before=(captured.x, captured.y),
                    state_before_digest=sha256_hex(canonical_causal_bytes(
                        state_from_capture(
                            capture=captured,
                            is_night=self.world.is_night(captured.t_monde),
                        ).as_dict()
                    )),
                )
        return execution

