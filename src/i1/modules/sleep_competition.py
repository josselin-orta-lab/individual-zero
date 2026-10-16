"""Ordinary Stage-10 sleep candidate and DC-01 evaluation, *not* command authority.

Sleep is a normal Competition candidate. Its option is eligible only when
Metacognition and Health froze real P-39/P-40 pressure at the world-step
opening and the scheduler supplied an accepted P-43 budget charge for option
preparation. Nothing here shortcuts Action Control or advances WorldBody.
"""
from __future__ import annotations

from dataclasses import replace
from math import isfinite

from i0.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
from i0.interfaces import PrimitiveCommand
from .competition import OptionEvidenceInput
from .sleep_health import SleepHealth


def _identity(health: SleepHealth, t_monde: int) -> str:
    return f"sleep-pressure:{health.rules.config.version}:t{t_monde}"


def create_sleep_proposal(
    *, health: SleepHealth, t_monde: int, st_version: str,
    charged_preparation: object,
) -> OptionProposal:
    """Produce one primitive candidate with genuine accepted logical-UC proof.

    The actual scheduler must debit the charge in the same deliberation,
    register the proposal through Competition and journal the operation.
    The charge object alone cannot attest its originating cycle.
    """
    if (type(t_monde) is not int or t_monde < 1
            or type(st_version) is not str or not st_version
            or health.frozen_world_step != t_monde
            or health.frozen is None
            or health.frozen.intrinsic_status != "applicable"
            or health.frozen.intrinsic_value is None):
        raise ValueError("cannot propose sleep without step-frozen waking pressure")
    charge = charged_preparation
    if (getattr(charge, "accepted", None) is not True
            or getattr(charge, "module", None) != "metacognition_health"
            or getattr(charge, "operation", None) != "sleep_option_prepare"
            or type(getattr(charge, "requested_uc", None)) is not int
            or charge.requested_uc < 1
            or type(getattr(charge, "consumed_cycle_uc", None)) is not int
            or charge.consumed_cycle_uc < charge.requested_uc
            or type(getattr(charge, "consumed_module_uc", None)) is not int
            or charge.consumed_module_uc < charge.requested_uc):
        raise ValueError("P-43 sleep candidate requires real accepted budget debit")
    reference = _identity(health, t_monde)
    option_id = f"option:{reference}"
    plan_id = f"plan:{reference}"
    plan = Plan(
        id=plan_id, option_ref=option_id, version=health.rules.config.version,
        steps=(PlanStep(index=0, command=PrimitiveCommand("dormir")),),
        goal_ref=None, budget_used_uc=charge.requested_uc,
        status="valid", st_version=st_version,
    )
    option = Option(
        id=option_id, version=health.rules.config.version,
        type="primitive", learning_signature="primitive:dormir",
        preconditions=(), success_condition="next_step_sleep_entry",
        failure_condition="admitted_sleep_command_not_applied",
        invalidation_condition="sleep_pressure_world_step_expired",
        motive_ref=MotiveRef(type="sleep_pressure", id=reference),
        founding_st_version=st_version, expires_at_step=t_monde + 1,
        provenance="default", plan_ref=plan_id, state="proposed",
    )
    proposal = OptionProposal(option=option, plan=plan)
    proposal.validate()
    return proposal


def _valid_sleep_shape(
    proposal: OptionProposal, *, health: SleepHealth, t_monde: int,
) -> bool:
    o, p = proposal.option, proposal.plan
    return (
        o.type == "primitive"
        and o.motive_ref.type == "sleep_pressure"
        and o.motive_ref.id == _identity(health, t_monde)
        and o.id == f"option:{o.motive_ref.id}"
        and o.version == health.rules.config.version
        and o.learning_signature == "primitive:dormir"
        and o.preconditions == ()
        and o.success_condition == "next_step_sleep_entry"
        and o.failure_condition == "admitted_sleep_command_not_applied"
        and o.invalidation_condition == "sleep_pressure_world_step_expired"
        and o.goal_ref is None
        and o.provenance == "default"
        and o.expires_at_step == t_monde + 1
        and p is not None
        and o.plan_ref == p.id
        and p.id == f"plan:{o.motive_ref.id}"
        and p.option_ref == o.id
        and p.version == o.version
        and p.goal_ref is None
        and p.status == "valid"
        and p.st_version == o.founding_st_version
        and p.budget_used_uc > 0
        and len(p.steps) == 1
        and p.steps[0].index == 0
        and p.steps[0].command.primitive == "dormir"
        and not p.steps[0].command.parameters
        and not p.steps[0].preconditions
        and not p.steps[0].predicted_consequences
        and p.steps[0].observation_window_steps == 1
    )


def assemble_sleep_evidence(
    *, proposal: OptionProposal, base: OptionEvidenceInput,
    health: SleepHealth, t_monde: int, cycle: int, intrinsic_weight: float,
) -> OptionEvidenceInput:
    """Augment existing Stage-8 extrinsic evidence with *only* P-40 sleep m_a.

    The caller obtains base through the canonical Stage-8 evaluator; no fake
    simulator outcome or learned value is manufactured. Missing extrinsic
    evidence contributes 0 as DC-01 permits for a real intrinsic motive.
    A mismatched or forged sleep option is non_evalue (frozen accumulator).
    """
    if (type(t_monde) is not int or t_monde < 1
            or type(cycle) is not int or cycle < 1
            or type(intrinsic_weight) not in (int, float)
            or not isfinite(intrinsic_weight) or intrinsic_weight < 0):
        raise ValueError("invalid versioned P-15 sleep evaluation context")
    base.validate()
    ev = base.evaluation
    if (ev.option_ref != proposal.option.id
            or ev.option_version != proposal.option.version
            or ev.t_monde != t_monde or ev.cycle != cycle):
        raise ValueError("extrinsic evidence is not for this option/cycle")
    frozen = health.frozen
    if (health.frozen_world_step != t_monde or frozen is None
            or frozen.intrinsic_status != "applicable"
            or frozen.intrinsic_value is None
            or not _valid_sleep_shape(proposal, health=health, t_monde=t_monde)):
        invalid = replace(
            ev, status="not_evaluated",
            intrinsic_status="applicable", intrinsic_value=None,
            producers=tuple(dict.fromkeys(ev.producers + ("metacognition_health:sleep_shape_invalid",))),
        )
        result = OptionEvidenceInput(invalid, None)
        result.validate()
        return result
    signal = _identity(health, t_monde)
    if signal in ev.signal_ids:
        raise ValueError("extrinsic and intrinsic evidence cannot reuse the same signal")
    extrinsic = 0.0 if base.evidence is None else float(base.evidence)
    score = max(-1.0, min(1.0, extrinsic + intrinsic_weight * frozen.intrinsic_value))
    output = replace(
        ev, status="evaluated", intrinsic_status="applicable",
        intrinsic_value=frozen.intrinsic_value,
        signal_ids=ev.signal_ids + (signal,),
        producers=tuple(dict.fromkeys(ev.producers + ("metacognition_health:p40_sleep_pressure",))),
    )
    result = OptionEvidenceInput(output, score)
    result.validate()
    return result
