"""Stage-9 safe causal-test Planning and evidence barrier.

Normative EN v1.2.1 §§8.2-8.3, 13.2-13.4, 14, INV-16/25/33.
No new P-48 novelty, information-gain or learning-progress policy is
invented. Test candidates enter ordinary Competition but stay unscored
until Exploration supplies a real intrinsic evaluation in a later stage.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from i0.contracts import (
    EvaluationOption, MotiveRef, Option, OptionProposal, Plan, PlanStep,
)
from i0.equipment import SimulationState
from i0.interfaces import PrimitiveCommand

from .causal_lifecycle import CausalTestTarget
from .competition import OptionEvidenceInput
from .simulator import Simulator
from .stage6_planning import SimulatorPlanner
from .stage8_evaluator import Stage8OptionEvaluator


@dataclass(frozen=True, slots=True)
class CausalTestPlanningAttempt:
    """Read-only reason for a proposal refusal; not a learning signal."""

    proposal: OptionProposal | None
    reason: str | None
    # None means the plan contains a real Equipment prediction. A nonempty
    # reason means the plan has no invented numeric consequences, and must
    # remain unscored until ordinary evidence sources are available.
    prediction_unavailability: str | None = None


def assess_executable_causal_test(
    *,
    target: CausalTestTarget,
    initial_state: SimulationState,
    simulator: Simulator,
    st_version: str,
    t_monde: int,
    ttl_steps: int,
) -> CausalTestPlanningAttempt:
    """Try the existing safe test without inventing an Equipment prediction.

    Reasons are diagnostic only. An unavailable simulation is uncertainty,
    not evidence that an intervention is impossible or causally refuted.
    """
    target.validate()
    initial_state.validate()
    if (
        target.primitive != "boire"
        or target.subject_ref != "water"
        or target.application_context != "water_source"
    ):
        return CausalTestPlanningAttempt(None, "unsupported_test_target")
    if not initial_state.current_water_source:
        return CausalTestPlanningAttempt(None, "water_source_not_accessible")
    if float(initial_state.body["water"]) >= 100.0:
        return CausalTestPlanningAttempt(None, "water_saturated")
    if (
        not st_version
        or type(t_monde) is not int or t_monde < 1
        or type(ttl_steps) is not int or ttl_steps < 1
    ):
        return CausalTestPlanningAttempt(None, "invalid_planning_context")
    command = PrimitiveCommand("boire")
    result = simulator.rollout(
        initial_state=initial_state,
        commands=(command,),
        r_eff=1,
        h_eff=1,
    )
    prediction_unavailability = None
    if not result.complete:
        if result.reason != "equipment_input_unseen":
            # An unresolved causal correction conflict is not a mere corpus
            # coverage gap: retain an explicit refusal rather than silently
            # ignoring a potentially important competing causal prediction.
            return CausalTestPlanningAttempt(
                None, "simulation_unavailable:" + (result.reason or "unspecified"),
            )
        # §12.4: unseen Equipment input gives E_a^sim=unavailable; it does
        # not prove the physically accessible one-step test unplanifiable.
        # Never manufacture a numerical prediction or treat this as evidence.
        consequences = ()
        prediction_unavailability = result.reason
    else:
        if len(result.completed_rollouts) != 1:
            return CausalTestPlanningAttempt(None, "invalid_rollout_count")
        predictions = result.completed_rollouts[0].predictions
        if len(predictions) != 1:
            return CausalTestPlanningAttempt(None, "invalid_prediction_count")
        consequences = SimulatorPlanner._predicted_consequences(predictions[0])
        if not any(item.variable == "water" for item in consequences):
            return CausalTestPlanningAttempt(None, "water_consequence_not_predicted")

    option_id = (
        f"option:causal-test:{target.contingency_ref}:"
        f"v{target.contingency_version}"
    )
    plan = Plan(
        id=f"plan:{option_id}:v1",
        option_ref=option_id,
        version="1",
        steps=(PlanStep(
            index=0,
            command=command,
            preconditions=("water_source_present",),
            predicted_consequences=consequences,
            observation_window_steps=1,
        ),),
        goal_ref=None,
        budget_used_uc=1,
        status="valid",
        st_version=st_version,
    )
    option = Option(
        id=option_id,
        version="1",
        type="primitive",
        learning_signature=(
            "causal_test:boire:water:water_source:observation"
        ),
        preconditions=("water_source_present",),
        success_condition="agency_observation_received",
        failure_condition="observation_missing_or_nonconforming",
        invalidation_condition="causal_hypothesis_or_context_changed",
        motive_ref=MotiveRef(type="test_causal", id=target.motive_ref),
        founding_st_version=st_version,
        expires_at_step=t_monde + ttl_steps,
        provenance="test_causal",
        plan_ref=plan.id,
        state="proposed",
    )
    proposal = OptionProposal(
        option=option,
        plan=plan,
        preliminary_admissibility=(
            "indeterminate" if prediction_unavailability else None
        ),
    )
    proposal.validate()
    return CausalTestPlanningAttempt(
        proposal, None, prediction_unavailability,
    )


def propose_executable_causal_test(
    *,
    target: CausalTestTarget,
    initial_state: SimulationState,
    simulator: Simulator,
    st_version: str,
    t_monde: int,
    ttl_steps: int,
) -> OptionProposal | None:
    """Preserve the proposal API; an unknown prediction is not a veto."""
    return assess_executable_causal_test(
        target=target, initial_state=initial_state, simulator=simulator,
        st_version=st_version, t_monde=t_monde, ttl_steps=ttl_steps,
    ).proposal


class Stage9OptionEvaluator(Stage8OptionEvaluator):
    """Stage-8 evaluation for goals, but no fabricated P-48 test interest."""

    def evaluate(
        self, *, proposal, evaluation_state, initial_state, cycle, t_monde,
        remaining_plan_index=0,
    ) -> OptionEvidenceInput:
        original = super().evaluate(
            proposal=proposal,
            evaluation_state=evaluation_state,
            initial_state=initial_state,
            cycle=cycle,
            t_monde=t_monde, remaining_plan_index=remaining_plan_index,
        )
        if proposal.option.motive_ref.type != "test_causal":
            return original
        # Simulated and learned information may be known, but the required
        # informational interest is not. In particular it is NOT zero.
        # Competition may retain this candidate but cannot accumulate
        # evidence or select it until Exploration P-48 is implemented.
        assessment = replace(
            original.evaluation,
            status="not_evaluated",
            intrinsic_status="applicable",
            intrinsic_value=None,
            producers=tuple(dict.fromkeys(
                original.evaluation.producers
                + ("exploration:p48_not_available",)
            )),
        )
        assessment.validate()
        result = OptionEvidenceInput(evaluation=assessment, evidence=None)
        result.validate()
        return result
