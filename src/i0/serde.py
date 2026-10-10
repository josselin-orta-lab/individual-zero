"""Deterministic serialization helpers for Stage-4 cognitive state."""

from __future__ import annotations

from typing import Mapping

from i0.contracts import (
    Contribution,
    MotiveRef,
    Option,
    OptionProposal,
    Plan,
    PlanStep,
)
from i0.interfaces import PrimitiveCommand


def _encode_payload(payload: object) -> object:
    if isinstance(payload, OptionProposal):
        return {
            "__i0_type__": "OptionProposal",
            "value": encode_proposal(payload),
        }
    return payload


def _decode_payload(payload: object) -> object:
    if isinstance(payload, Mapping) and payload.get("__i0_type__") == "OptionProposal":
        raw = payload.get("value")
        if not isinstance(raw, Mapping):
            raise ValueError("invalid encoded OptionProposal payload")
        return decode_proposal(raw)
    return payload


def encode_contribution(c: Contribution) -> dict[str, object]:
    return {
        "id": c.id,
        "schema_version": c.schema_version,
        "type": c.type,
        "summary": c.summary,
        "subject_ref": c.subject_ref,
        "emitter_module": c.emitter_module,
        "signal_family": c.signal_family,
        "confidence": c.confidence,
        "urgency": c.urgency,
        "risk": c.risk,
        "value": c.value,
        "production_t": c.production_t,
        "production_cycle": c.production_cycle,
        "expires_at_step": c.expires_at_step,
        "payload": _encode_payload(c.payload),
        "goal_ref": c.goal_ref,
        "provenance_inputs": list(c.provenance_inputs),
        "signal_ids": list(c.signal_ids),
    }


def decode_contribution(raw: Mapping[str, object]) -> Contribution:
    c = Contribution(
        id=str(raw["id"]),
        schema_version=str(raw["schema_version"]),
        type=str(raw["type"]),
        summary=str(raw["summary"]),
        subject_ref=str(raw["subject_ref"]),
        emitter_module=str(raw["emitter_module"]),
        signal_family=str(raw["signal_family"]),
        confidence=float(raw["confidence"]),
        urgency=float(raw["urgency"]),
        risk=float(raw["risk"]),
        value=float(raw["value"]),
        production_t=int(raw["production_t"]),
        production_cycle=int(raw["production_cycle"]),
        expires_at_step=int(raw["expires_at_step"]),
        payload=_decode_payload(raw.get("payload")),
        goal_ref=None if raw.get("goal_ref") is None else str(raw["goal_ref"]),
        provenance_inputs=tuple(str(x) for x in raw.get("provenance_inputs", [])),
        signal_ids=tuple(str(x) for x in raw.get("signal_ids", [])),
    )
    c.validate()
    return c


def encode_proposal(p: OptionProposal) -> dict[str, object]:
    option = p.option
    plan = p.plan
    return {
        "option": {
            "id": option.id,
            "version": option.version,
            "type": option.type,
            "learning_signature": option.learning_signature,
            "preconditions": list(option.preconditions),
            "success_condition": option.success_condition,
            "failure_condition": option.failure_condition,
            "invalidation_condition": option.invalidation_condition,
            "goal_ref": option.goal_ref,
            "motive_ref": {
                "type": option.motive_ref.type,
                "id": option.motive_ref.id,
            },
            "plan_ref": option.plan_ref,
            "founding_st_version": option.founding_st_version,
            "expires_at_step": option.expires_at_step,
            "provenance": option.provenance,
            "grounding_contribution_refs": list(option.grounding_contribution_refs),
            "state": option.state,
        },
        "plan": None if plan is None else {
            "id": plan.id,
            "option_ref": plan.option_ref,
            "version": plan.version,
            "steps": [
                {
                    "index": step.index,
                    "command": step.command.as_dict(),
                    "preconditions": list(step.preconditions),
                    "predicted_consequences": [
                        {
                            "variable": consequence.variable,
                            "value_or_delta": consequence.value_or_delta,
                            "precision": consequence.precision,
                        }
                        for consequence in step.predicted_consequences
                    ],
                    "observation_window_steps": step.observation_window_steps,
                }
                for step in plan.steps
            ],
            "goal_ref": plan.goal_ref,
            "budget_used_uc": plan.budget_used_uc,
            "status": plan.status,
            "st_version": plan.st_version,
        },
        "preliminary_admissibility": p.preliminary_admissibility,
    }


def decode_proposal(raw: Mapping[str, object]) -> OptionProposal:
    from i0.contracts import PredictedConsequence

    option_raw = raw["option"]
    if not isinstance(option_raw, Mapping):
        raise ValueError("invalid option state")
    motive_raw = option_raw["motive_ref"]
    if not isinstance(motive_raw, Mapping):
        raise ValueError("invalid motive state")

    option = Option(
        id=str(option_raw["id"]),
        version=str(option_raw["version"]),
        type=str(option_raw["type"]),
        learning_signature=str(option_raw["learning_signature"]),
        preconditions=tuple(str(x) for x in option_raw.get("preconditions", [])),
        success_condition=str(option_raw["success_condition"]),
        failure_condition=str(option_raw["failure_condition"]),
        invalidation_condition=str(option_raw["invalidation_condition"]),
        goal_ref=None if option_raw.get("goal_ref") is None else str(option_raw["goal_ref"]),
        motive_ref=MotiveRef(
            type=str(motive_raw["type"]),
            id=str(motive_raw["id"]),
        ),
        plan_ref=None if option_raw.get("plan_ref") is None else str(option_raw["plan_ref"]),
        founding_st_version=str(option_raw["founding_st_version"]),
        expires_at_step=int(option_raw["expires_at_step"]),
        provenance=str(option_raw["provenance"]),
        grounding_contribution_refs=tuple(
            str(x) for x in option_raw.get("grounding_contribution_refs", [])
        ),
        state=str(option_raw["state"]),
    )

    plan_raw = raw.get("plan")
    plan = None
    if plan_raw is not None:
        if not isinstance(plan_raw, Mapping):
            raise ValueError("invalid plan state")
        steps = []
        for step_raw in plan_raw.get("steps", []):
            if not isinstance(step_raw, Mapping):
                raise ValueError("invalid plan step state")
            cmd_raw = step_raw["command"]
            if not isinstance(cmd_raw, Mapping):
                raise ValueError("invalid command state")
            steps.append(
                PlanStep(
                    index=int(step_raw["index"]),
                    command=PrimitiveCommand(
                        primitive=str(cmd_raw["primitive"]),
                        parameters=dict(cmd_raw.get("parameters", {})),
                    ),
                    preconditions=tuple(str(x) for x in step_raw.get("preconditions", [])),
                    predicted_consequences=tuple(
                        PredictedConsequence(
                            variable=str(c["variable"]),
                            value_or_delta=float(c["value_or_delta"]),
                            precision=float(c["precision"]),
                        )
                        for c in step_raw.get("predicted_consequences", [])
                    ),
                    observation_window_steps=int(step_raw["observation_window_steps"]),
                )
            )
        plan = Plan(
            id=str(plan_raw["id"]),
            option_ref=str(plan_raw["option_ref"]),
            version=str(plan_raw["version"]),
            steps=tuple(steps),
            goal_ref=None if plan_raw.get("goal_ref") is None else str(plan_raw["goal_ref"]),
            budget_used_uc=int(plan_raw["budget_used_uc"]),
            status=str(plan_raw["status"]),
            st_version=str(plan_raw["st_version"]),
        )

    proposal = OptionProposal(
        option=option,
        plan=plan,
        preliminary_admissibility=(
            None
            if raw.get("preliminary_admissibility") is None
            else str(raw["preliminary_admissibility"])
        ),
    )
    proposal.validate()
    return proposal
