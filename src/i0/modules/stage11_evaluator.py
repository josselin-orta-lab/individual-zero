"""Stage-11 P-48 evaluation: intrinsic evidence without Stage-9 modifications."""
from dataclasses import replace
from math import isfinite

from .causal_test_planning import Stage9OptionEvaluator
from .competition import OptionEvidenceInput
from i0.contracts import EvaluationOption
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

    @staticmethod
    def _safe_geographic_shape(proposal, target):
        option, plan = proposal.option, proposal.plan
        if (
            option.motive_ref.type != "cible_exploration"
            or option.motive_ref.id != target.ref
            or option.id != (
                f"option:geographic:{target.ref}:t{target.source_t_monde}"
            )
            or option.provenance != "exploration"
            or option.type != "primitive"
            or option.goal_ref is not None
            or option.preconditions != ("adjacent_passable",)
            or option.success_condition != "target_position_observed"
            or option.failure_condition != "target_position_not_observed"
            or option.invalidation_condition != "target_visited_or_context_changed"
            or option.learning_signature != (
                f"geographic_frontier:{target.destination[0]}:{target.destination[1]}"
            )
            or plan is None or option.plan_ref != plan.id
            or plan.option_ref != option.id
            or plan.goal_ref is not None
            or plan.status != "valid"
            or plan.st_version != option.founding_st_version
            or len(plan.steps) != 1
        ):
            return False
        step = plan.steps[0]
        observed = {
            effect.variable: effect.value_or_delta
            for effect in step.predicted_consequences
        }
        return (
            step.index == 0
            and step.command.primitive == "se_deplacer"
            and step.command.parameters == {"direction": target.direction}
            and step.preconditions == ("adjacent_passable",)
            and step.observation_window_steps == 1
            and observed.get("position_x") == target.destination[0]
            and observed.get("position_y") == target.destination[1]
        )

    @staticmethod
    def _unscored_geographic(proposal, *, cycle, t_monde):
        evaluation = EvaluationOption(
            option_ref=proposal.option.id,
            option_version=proposal.option.version,
            cycle=cycle, t_monde=t_monde,
            status="not_evaluated",
            learned_value_status="unlearned", learned_value=None,
            simulated_value_status="unavailable", simulated_value=None,
            intrinsic_status="applicable", intrinsic_value=None,
            risk_status="unknown", risk=None,
            safety_uncertainty=0.0, protection=False,
            signal_ids=(), producers=("exploration:unverified_frontier",),
        )
        evaluation.validate()
        return OptionEvidenceInput(evaluation=evaluation, evidence=None)

    def evaluate(self, *, proposal, evaluation_state, initial_state, cycle, t_monde):
        if proposal.option.motive_ref.type == "cible_exploration":
            geographic = self._exploration.geographic
            target = (
                None if geographic is None
                else geographic.target_for(proposal.option)
            )
            if (
                target is None
                or target.source_t_monde != t_monde
                or not self._safe_geographic_shape(proposal, target)
            ):
                return self._unscored_geographic(
                    proposal, cycle=cycle, t_monde=t_monde,
                )
            original = Stage8OptionEvaluator.evaluate(
                self, proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
            )
            intrinsic = self._exploration.geographic_motivation(proposal.option)
            signals = tuple(original.evaluation.signal_ids)
            if (
                intrinsic.status != "available"
                or set(signals) & set(intrinsic.signal_ids)
            ):
                assessment = replace(
                    original.evaluation, status="not_evaluated",
                    intrinsic_status="applicable", intrinsic_value=None,
                    producers=tuple(dict.fromkeys(
                        original.evaluation.producers + (
                            "exploration:geographic_interest_unavailable",
                        )
                    )),
                )
                result = OptionEvidenceInput(assessment, None)
                result.validate()
                return result
            ext = 0.0 if original.evidence is None else original.evidence
            score = max(-1.0, min(1.0, ext + (
                self._intrinsic_weight * intrinsic.value
            )))
            assessment = replace(
                original.evaluation, status="evaluated",
                intrinsic_status="applicable",
                intrinsic_value=intrinsic.value,
                signal_ids=signals + intrinsic.signal_ids,
                producers=tuple(dict.fromkeys(
                    original.evaluation.producers + (
                        "exploration:p48_geographic",
                    )
                )),
            )
            result = OptionEvidenceInput(assessment, score)
            result.validate()
            return result

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
