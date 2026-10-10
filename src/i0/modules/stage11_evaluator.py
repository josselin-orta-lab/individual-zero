"""Stage-11 P-48 evaluation: intrinsic evidence without Stage-9 modifications."""
from dataclasses import replace
from math import isfinite

from .causal_test_planning import Stage9OptionEvaluator
from .competition import OptionEvidenceInput
from .stage8_evaluator import Stage8OptionEvaluator


class Stage11OptionEvaluator(Stage9OptionEvaluator):
    def __init__(self, *, exploration, intrinsic_weight, **kwargs):
        super().__init__(**kwargs)
        if not isfinite(intrinsic_weight) or intrinsic_weight < 0:
            raise ValueError("P-15 intrinsic weight must be finite and nonnegative")
        self._exploration = exploration
        self._intrinsic_weight = intrinsic_weight

    @staticmethod
    def _safe_causal_test_shape(proposal):
        """Only Stage-9's physically admissible one-step water-test template.

        An arbitrary option must not acquire intrinsic interest by reusing a
        causal motive or option identifier with a different plan/command.
        Action Control and the canonical Causal Model still perform their
        separate admissibility and physical evidence checks.
        """
        option, plan = proposal.option, proposal.plan
        if (
            option.motive_ref.type != "test_causal"
            or option.type != "primitive"
            or option.provenance != "test_causal"
            or option.goal_ref is not None
            or option.learning_signature != (
                "causal_test:boire:water:water_source:observation"
            )
            or option.preconditions != ("water_source_present",)
            or option.success_condition != "agency_observation_received"
            or option.failure_condition != "observation_missing_or_nonconforming"
            or option.invalidation_condition != "causal_hypothesis_or_context_changed"
            or plan is None
            or plan.option_ref != option.id
            or plan.id != option.plan_ref
            or plan.goal_ref is not None
            or plan.status != "valid"
            or plan.st_version != option.founding_st_version
            or len(plan.steps) != 1
        ):
            return False
        step = plan.steps[0]
        return (
            step.index == 0
            and step.command.primitive == "boire"
            and not step.command.parameters
            and step.preconditions == ("water_source_present",)
            and step.observation_window_steps == 1
        )

    def evaluate(self, *, proposal, evaluation_state, initial_state, cycle, t_monde):
        if proposal.option.motive_ref.type != "test_causal":
            return super().evaluate(
                proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
            )
        if not self._safe_causal_test_shape(proposal):
            # Fail closed to the historical Stage-9 unscored behavior.
            # In particular, do not trust the motive label as evidence.
            return super().evaluate(
                proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
            )
        # Stage-8 supplies only the extrinsic term. The Stage-9 P-48 guard
        # remains unchanged on all pre-vNext runtimes.
        original = Stage8OptionEvaluator.evaluate(
            self, proposal=proposal, evaluation_state=evaluation_state,
            initial_state=initial_state, cycle=cycle, t_monde=t_monde,
        )
        intrinsic = self._exploration.motivation(proposal.option)
        ids = tuple(original.evaluation.signal_ids)
        duplicated = bool(set(ids) & set(intrinsic.signal_ids))
        if intrinsic.status != "available" or duplicated:
            reason = "shared_signal" if duplicated else intrinsic.reason
            assessment = replace(
                original.evaluation, status="not_evaluated",
                intrinsic_status="applicable", intrinsic_value=None,
                producers=tuple(dict.fromkeys(
                    original.evaluation.producers + (f"exploration:{reason}",)
                )),
            )
            result = OptionEvidenceInput(assessment, None)
            result.validate()
            return result
        # No Q and no completed simulation means extrinsic unavailable.
        # DC-01 explicitly defines the missing extrinsic component as zero,
        # without treating it as a negative learned value.
        extrinsic = 0.0 if original.evidence is None else original.evidence
        evidence = max(-1.0, min(1.0, extrinsic + self._intrinsic_weight * intrinsic.value))
        assessment = replace(
            original.evaluation, status="evaluated",
            intrinsic_status="applicable", intrinsic_value=intrinsic.value,
            signal_ids=ids + intrinsic.signal_ids,
            producers=tuple(dict.fromkeys(
                original.evaluation.producers + ("exploration:p48",)
            )),
        )
        result = OptionEvidenceInput(assessment, evidence)
        result.validate()
        return result
