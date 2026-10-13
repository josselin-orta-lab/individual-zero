"""First-person goal agency: bounded, epistemically conservative pure core.

This module does not infer physical etiology, P-47 correctness, or goal success.
Only an authorized Action Control owner may invoke it with lived cues.
"""
from dataclasses import dataclass
from typing import Literal

Agency = Literal["self", "world", "unknown"]


@dataclass(frozen=True, slots=True)
class GoalAgencyEvidence:
    """Precommitted first-person evidence, not a laboratory truth label."""

    intent_ref: str
    command_ref: str
    perceived_ref: str
    goal_ref: str
    policy_version: str
    admitted_voluntary_command: bool
    witnessed_goal_relevant_action_effect: bool
    witnessed_goal_relevant_external_constraint: bool
    ambiguous_or_confounded: bool = False


@dataclass(frozen=True, slots=True)
class GoalAgencyJudgement:
    intent_ref: str
    command_ref: str
    perceived_ref: str
    goal_ref: str
    policy_version: str
    subjective_agency: Agency
    uncertainty_reason: str | None


def judge_goal_agency(evidence: GoalAgencyEvidence) -> GoalAgencyJudgement:
    """Judge contribution, never derive it from success/failure or P-47.

    Input flags MUST be independently derived by Action Control from permitted
    perception/efference and precommitted, goal-relevant mechanism semantics.
    This pure function alone does not authenticate those claims.
    """
    if not all((evidence.intent_ref, evidence.command_ref,
                evidence.perceived_ref, evidence.goal_ref,
                evidence.policy_version)):
        raise ValueError("missing lived agency provenance")
    personal = (evidence.admitted_voluntary_command
                and evidence.witnessed_goal_relevant_action_effect)
    external = evidence.witnessed_goal_relevant_external_constraint
    if evidence.ambiguous_or_confounded or (personal and external):
        agency, reason = "unknown", "competing_or_confounded_evidence"
    elif personal:
        agency, reason = "self", None
    elif external:
        agency, reason = "world", None
    else:
        agency, reason = "unknown", "insufficient_goal_relevant_evidence"
    return GoalAgencyJudgement(
        intent_ref=evidence.intent_ref,
        command_ref=evidence.command_ref,
        perceived_ref=evidence.perceived_ref,
        goal_ref=evidence.goal_ref,
        policy_version=evidence.policy_version,
        subjective_agency=agency,
        uncertainty_reason=reason,
    )
