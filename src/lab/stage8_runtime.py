"""Integrated Stage-8 online value learning over Stage 7.

The update schedule follows DC-15 exactly: a learned update is computed only
after the later cognitive decision step finishes without lethal rollback, and
can therefore influence evidence only from the next world step.

Spec: 8.5, 11.1, 20.3 Stage 8, DC-01, DC-15, INV-07, INV-16.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.equipment import EquipmentModel
from i0.modules.active_kappa import KappaConfig, KappaVerification
from i0.modules.active_precision import PrecisionConfig, PrecisionVerification
from i0.modules import (
    EvaluationState,
    LinearTDValues,
    StaticSafetyFacts,
    TDLearningConfig,
)
from i0.modules.simulator import state_from_capture
from i0.modules.stage8_evaluator import (
    Stage8EvaluationConfig,
    Stage8OptionEvaluator,
)

from .determinism import deterministic_id
from .safety_protocol import SafetyProtocolConfig
from .stage2_runtime import CommandExecution
from .stage7_runtime import Stage7Config, Stage7Runtime
from .world import WorldLayout, WorldPhysicsConfig


@dataclass(frozen=True, slots=True)
class Stage8Config:
    version: str
    stage7: Stage7Config
    td: TDLearningConfig
    evaluation: Stage8EvaluationConfig
    kappa: KappaConfig
    precision: PrecisionConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 8 config version must not be empty")
        self.stage7.validate()
        self.td.validate()
        self.evaluation.validate()
        self.kappa.validate()
        self.precision.validate()
        beta_sim = self.stage7.stage6.evaluation.beta
        if self.td.beta != beta_sim:
            raise ValueError("P-30 beta must be common to Q and simulation")
        if self.evaluation.evidence_scale != self.stage7.stage6.evaluation.evidence_scale:
            raise ValueError("Stage 8 must reuse the DC-01 evidence scale")


class Stage8Runtime(Stage7Runtime):
    """Stage 7 plus Q_active and learned/simulated evidence."""

    individual_id = "i0-stage8"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage8Config,
        equipment: EquipmentModel,
    ) -> None:
        config.validate()
        self._stage8_config = config
        self.q_active = LinearTDValues(config.td)
        self._applied_decision_context: tuple[
            EvaluationState, str, int, int, str
        ] | None = None

        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.stage7,
            equipment=equipment,
        )

        self.value_needs.attach_td_values(self.q_active)
        self.metacognition.attach_active_kappa(config.kappa)
        self.stage3.perception.attach_active_precision(config.precision)
        self.gatekeeper.attach_reliability(self._contribution_reliability)
        self.stage8_option_evaluator = Stage8OptionEvaluator(
            config=config.evaluation,
            stage6=self.option_evaluator,
            q_values=self.q_active,
        )

    @property
    def precision_active(self):
        return self.stage3.perception.active_precision

    def integrate_precision_verification(self, verification: PrecisionVerification) -> None:
        """Perception alone learns per-source active precision; no oracle labels."""
        self.precision_active.integrate(verification)

    @property
    def kappa_active(self):
        return self.metacognition.active_kappa

    def _contribution_reliability(self, contribution) -> float:
        kappa = self.kappa_active
        if kappa is None:
            raise RuntimeError("Stage 8 active kappa is missing")
        version = (
            self.equipment.version
            if contribution.signal_family == "equipment_predictor"
            else self._config.version
        )
        return kappa.reliability(
            version=version,
            module=contribution.emitter_module,
            contribution_type=contribution.type,
            family=contribution.signal_family,
            confidence=contribution.confidence,
        )

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        original_closure = hooks[5]["metacognition_health"]

        def close_kappa(ctx):
            original_closure(ctx)
            kappa = self.kappa_active
            updates = kappa.publish()
            for verification, before, after in updates:
                self._write(
                    kind="kappa_update_published", cycle=cycle,
                    data={
                        "verification_ref": verification.identifier,
                        "calibration_key": list(verification.key),
                        "confidence": verification.declared_confidence,
                        "outcome": verification.outcome,
                        "reliability_before": before,
                        "reliability_after": after,
                        "kappa_version": kappa.version,
                    },
                )
        hooks[5]["metacognition_health"] = close_kappa
        return hooks

    def integrate_kappa_verification(self, verification: KappaVerification) -> None:
        """Accept an externally produced causal verification, not an oracle verdict.

        Evidence provenance must be supplied by the owning verifier.
        Only Metacognition can mutate counters, and only at phase 5.
        """
        self.kappa_active.integrate(verification)

    def _evaluation_state(self, capture) -> EvaluationState:
        goal = self.goal_manager.active_goal
        return EvaluationState(
            body=dict(capture.body),
            x=capture.x,
            y=capture.y,
            active_goal_type=None if goal is None else goal.goal_type,
            temporal_context=(
                "night"
                if self.world.is_night(capture.t_monde)
                else "day"
            ),
        )

    def _evaluate_competition_cycle(
        self,
        *,
        capture,
        cycle: int,
    ):
        initial_state = state_from_capture(
            capture=capture,
            is_night=self.world.is_night(capture.t_monde),
        )
        evaluation_state = self._evaluation_state(capture)

        evidence_inputs = {}
        for proposal in self.competition.candidate_proposals:
            supplied = self.stage8_option_evaluator.evaluate(
                proposal=proposal,
                evaluation_state=evaluation_state,
                initial_state=initial_state,
                cycle=cycle,
                t_monde=capture.t_monde,
            )
            evidence_inputs[proposal.option.id] = supplied
            evaluation = supplied.evaluation
            self._write(
                kind="stage8_option_evaluation",
                cycle=cycle,
                data={
                    "option_ref": proposal.option.id,
                    "learning_signature": (
                        proposal.option.learning_signature
                    ),
                    "status": evaluation.status,
                    "learned_value_status": (
                        evaluation.learned_value_status
                    ),
                    "learned_value": evaluation.learned_value,
                    "simulated_value_status": (
                        evaluation.simulated_value_status
                    ),
                    "simulated_value": evaluation.simulated_value,
                    "evidence": supplied.evidence,
                    "equipment_version": self.equipment.version,
                    "q_version": self._stage8_config.td.version,
                },
            )

        return self.competition.evaluate(
            cycle=cycle,
            t_monde=capture.t_monde,
            evidence_inputs=evidence_inputs,
        )

    def _handle_agency_comparison(self, *, capture, comparison) -> None:
        super()._handle_agency_comparison(capture=capture, comparison=comparison)
        # DC-06: the simulator's declared outcome is compared with a fresh
        # physical capture. Predictions do not verify themselves. Unknown
        # comparisons and unobserved consequences never enter the posterior.
        for index, effect in enumerate(comparison.effects):
            status = effect.get("status")
            if status not in {"conforming", "nonconforming"}:
                continue
            if effect.get("observed") is None or effect.get("predicted") is None:
                continue
            self.kappa_active.integrate(KappaVerification(
                identifier=deterministic_id(
                    "kappa-verification-v1",
                    self.equipment.version,
                    comparison.option_ref,
                    comparison.sent_t_monde,
                    comparison.observed_t_monde,
                    index,
                ),
                equipment_or_module_version=self.equipment.version,
                module="simulator",
                contribution_type="prediction",
                signal_family="equipment_predictor",
                declared_confidence=1.0,
                emission_step=comparison.sent_t_monde,
                observation_step=comparison.observed_t_monde,
                outcome=(
                    "confirmee" if status == "conforming"
                    else "contredite"
                ),
                observation_anchor="monde",
                observation_ref=(
                    f"physical-capture:{comparison.observed_t_monde}:"
                    f"{str(effect.get('variable'))}"
                ),
                independent_family="world_symbolic"
                if str(effect.get("variable")) in {"position_x", "position_y"}
                else "body_telemetry",
                physical_consequence=True,
                provenance_independent=True,
            ))

    def _dispatch_decision(
        self,
        *,
        proposal,
        prepared,
        admission,
        cycle: int,
        sent_t_monde: int,
    ) -> CommandExecution:
        capture = self.stage3._capture
        if capture is None:
            raise RuntimeError("Stage 8 decision requires the frozen step capture")
        evaluation_state = self._evaluation_state(capture)
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("Stage 8 decision requires an active attempt")
        attempt_ref = attempt.attempt_ref

        execution = super()._dispatch_decision(
            proposal=proposal,
            prepared=prepared,
            admission=admission,
            cycle=cycle,
            sent_t_monde=sent_t_monde,
        )
        if execution.status == "applied":
            self._applied_decision_context = (
                evaluation_state,
                proposal.option.learning_signature,
                sent_t_monde,
                cycle,
                attempt_ref,
            )
        return execution

    def _write_td_update(
        self,
        *,
        update,
        t_monde: int,
        cycle: int,
        attempt_ref: str,
    ) -> None:
        event_id = deterministic_id(
            "journal-event-v1",
            "stage8.td",
            t_monde,
            cycle,
            attempt_ref,
            update.previous_signature,
            update.next_signature,
            update.segment_length,
        )
        self.journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "value_needs",
                "kind": "td_update_published",
                "t_monde": t_monde,
                "cycle": cycle,
                "attempt_ref": attempt_ref,
                "data": {
                    "previous_signature": update.previous_signature,
                    "next_signature": update.next_signature,
                    "segment_length": update.segment_length,
                    "return_g": update.return_g,
                    "q_previous": update.q_previous,
                    "q_next": update.q_next,
                    "delta": update.delta,
                    "updated_signatures": list(
                        update.updated_signatures
                    ),
                    "td_version": self._stage8_config.td.version,
                },
            },
        )

    def run_step(self):
        before_body = dict(self.world.body.as_dict())
        self._applied_decision_context = None

        result = super().run_step()

        if result.execution_status != "applied":
            return result

        after_body = dict(self.world.body.as_dict())
        reward = self.value_needs.reward_between(
            before_body,
            after_body,
        )

        if self._applied_decision_context is not None:
            (
                evaluation_state,
                signature,
                decision_t,
                cycle,
                attempt_ref,
            ) = self._applied_decision_context
            update = self.q_active.arrive_decision(
                state=evaluation_state,
                signature=signature,
                t_monde=decision_t,
            )
            if update is not None:
                self._write_td_update(
                    update=update,
                    t_monde=decision_t,
                    cycle=cycle,
                    attempt_ref=attempt_ref,
                )

        # The reward caused by the command just experienced belongs to the
        # segment opened by the current decision. Reflex steps reach this path
        # with no new decision and therefore extend the existing segment.
        self.q_active.append_experienced_reward(reward)
        # Perception-only active precision; publish after the lived nonlethal
        # transition, never during the decision's evidence snapshot.
        for source, old, new, observation_ref in self.precision_active.publish():
            self.journal.append(
                event_id=deterministic_id(
                    "journal-event-v1", "stage8.precision",
                    self.scheduler.t_monde, source, observation_ref,
                    self.precision_active.version,
                ),
                causal_event={
                    "emitter": "perception",
                    "kind": "perceptual_precision_update_published",
                    "t_monde": self.scheduler.t_monde,
                    "source": source,
                    "verification_ref": observation_ref,
                    "before": old, "after": new,
                    "precision_version": self.precision_active.version,
                },
            )
        return result
