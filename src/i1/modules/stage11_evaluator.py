"""Stage-11 P-48 evaluation: intrinsic evidence without Stage-9 modifications."""
from dataclasses import replace
from math import isfinite

from .causal_test_planning import Stage9OptionEvaluator
from .competition import OptionEvidenceInput
from i0.contracts import EvaluationOption
from .stage8_evaluator import Stage8OptionEvaluator


class Stage11OptionEvaluator(Stage9OptionEvaluator):
    def __init__(self, *, exploration, intrinsic_weight, instrumental_planning=None, **kwargs):
        super().__init__(**kwargs)
        if not isfinite(intrinsic_weight) or intrinsic_weight < 0:
            raise ValueError("P-15 intrinsic weight must be finite and nonnegative")
        self._exploration = exploration
        self._intrinsic_weight = intrinsic_weight
        self._instrumental_planning = instrumental_planning

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
        expected = {
            "position_x": target.destination[0],
            "position_y": target.destination[1],
        }
        required_axis = (
            "position_y" if target.direction in ("north", "south")
            else "position_x"
        )
        return (
            len(observed) == len(step.predicted_consequences)
            and step.index == 0
            and step.command.primitive == "se_deplacer"
            and step.command.parameters == {"direction": target.direction}
            and step.preconditions == ("adjacent_passable",)
            and step.observation_window_steps == 1
            and (
                # No Equipment numeric prediction means explicit uncertainty
                # as at Stage 9, not a fabricated zero-movement forecast.
                (
                    not step.predicted_consequences
                    and proposal.preliminary_admissibility == "indeterminate"
                )
                or (
                    proposal.preliminary_admissibility is None
                    and observed.get(required_axis) == expected[required_axis]
                    and all(
                        observed.get(name, value) == value
                        for name, value in expected.items()
                    )
                )
            )
        )

    @staticmethod
    def _safe_transit_shape(proposal, target):
        """No route label can authorize an arbitrary movement or inflated m_a."""
        option, plan = proposal.option, proposal.plan
        if (
            option.motive_ref.type != "cible_exploration"
            or option.motive_ref.id != target.ref
            or option.id != f"option:geographic:{target.ref}:t{target.source_t_monde}"
            or option.provenance != "exploration"
            or option.type != "primitive"
            or option.goal_ref is not None
            or option.preconditions != ("adjacent_passable",)
            or option.success_condition != "target_position_observed"
            or option.failure_condition != "target_position_not_observed"
            or option.invalidation_condition != "route_objective_visited_or_context_changed"
            or option.learning_signature != (
                f"geographic_transit:{target.observed_frontier[0]}:"
                f"{target.observed_frontier[1]}:via:"
                f"{target.destination[0]}:{target.destination[1]}"
            )
            or plan is None or plan.id != option.plan_ref
            or plan.option_ref != option.id
            or plan.goal_ref is not None
            or plan.status != "valid"
            or plan.st_version != option.founding_st_version
            or len(plan.steps) != 1
        ):
            return False
        step = plan.steps[0]
        forecast = {v.variable: v.value_or_delta for v in step.predicted_consequences}
        expected = {"position_x": target.destination[0],
                    "position_y": target.destination[1]}
        changed = "position_y" if target.direction in ("north", "south") else "position_x"
        return (
            step.index == 0
            and step.command.primitive == "se_deplacer"
            and step.command.parameters == {"direction": target.direction}
            and step.preconditions == ("adjacent_passable",)
            and step.observation_window_steps == 1
            and len(forecast) == len(step.predicted_consequences)
            and (
                (not step.predicted_consequences
                 and proposal.preliminary_admissibility == "indeterminate")
                or (proposal.preliminary_admissibility is None
                    and forecast.get(changed) == expected[changed]
                    and all(forecast.get(k, v) == v for k, v in expected.items()))
            )
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

    def evaluate(self, *, proposal, evaluation_state, initial_state, cycle, t_monde,
                 remaining_plan_index=0):
        if proposal.option.motive_ref.type == "place_memory":
            geo = self._exploration.geographic
            target = None if geo is None else geo.place_for(proposal.option)
            valid = (target is not None and target.source_t_monde == t_monde
                     and proposal.option.goal_ref is not None
                     and proposal.option.provenance == "memory"
                     and proposal.option.plan_ref == proposal.plan.id
                     and proposal.option.learning_signature == (
                         f"memory_place_return:{target.entity_id}"
                     ) and proposal.plan is not None
                     and proposal.plan.goal_ref == proposal.option.goal_ref
                     and proposal.plan.st_version ==
                         proposal.option.founding_st_version
                     and len(proposal.plan.steps) == 1
                     and proposal.plan.steps[0].command.primitive == "se_deplacer"
                     and proposal.plan.steps[0].command.parameters ==
                         {"direction": target.direction}
                     and proposal.plan.steps[0].preconditions ==
                         ("adjacent_passable",))
            if not valid:
                return self._unscored_geographic(
                    proposal, cycle=cycle, t_monde=t_monde)
            original = Stage8OptionEvaluator.evaluate(
                self, proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
                remaining_plan_index=remaining_plan_index,
            )
            # This is confidence in a remembered destination, NOT a claim
            # about physiology or an artificially learned Q value.
            # Existing goal pressure is supplied by Stage4's real need owner.
            # No built-in entity-usefulness relation: even a remembered berry
            # has no prelearned nutritional value. Stage8 TD stays authoritative.
            value = min(0.12, self._intrinsic_weight * 0.12 * target.confidence)
            ext = 0.0 if original.evidence is None else original.evidence
            assessment = replace(
                original.evaluation, status="evaluated",
                intrinsic_status="applicable", intrinsic_value=value,
                signal_ids=tuple(original.evaluation.signal_ids) + (
                    f"place-memory:{target.entity_id}:seen-t{target.observed_step}",
                ),
                producers=tuple(dict.fromkeys(
                    original.evaluation.producers + ("exploration:entity_place_recall",)
                )),
            )
            scored = OptionEvidenceInput(assessment, max(-1.0, min(1.0, ext + value)))
            scored.validate()
            return scored
        if proposal.option.motive_ref.type == "cible_exploration":
            geographic = self._exploration.geographic
            target = (
                None if geographic is None
                else geographic.target_for(proposal.option)
            )
            transit = (
                None if geographic is None
                else geographic.transit_for(proposal.option)
            )
            if (
                (target is None and transit is None)
                or (target is not None and transit is not None)
                or (target is not None and (
                    target.source_t_monde != t_monde
                    or not self._safe_geographic_shape(proposal, target)
                ))
                or (transit is not None and (
                    transit.source_t_monde != t_monde
                    or not self._safe_transit_shape(proposal, transit)
                ))
            ):
                return self._unscored_geographic(
                    proposal, cycle=cycle, t_monde=t_monde,
                )
            original = Stage8OptionEvaluator.evaluate(
                self, proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
                remaining_plan_index=remaining_plan_index,
            )
            intrinsic = (
                self._exploration.geographic_motivation(proposal.option)
                if target is not None
                else self._exploration.geographic_transit_motivation(
                    proposal.option
                )
            )
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

        # Optional goal-linked interest: only a genuine current Stage6
        # progressive prefix can share a currently offered frontier signal.
        # Never rewrite the option's own original motive or goal reference.
        owner = self._instrumental_planning
        if (
            owner is not None
            and proposal.option.motive_ref.type == "active_goal"
            and proposal.option.goal_ref == proposal.option.motive_ref.id
            and proposal.option.success_condition == "step_completed"
            and proposal.plan is not None
            and len(proposal.plan.steps) > 1
            and owner.current_proposal == proposal
            and proposal.plan.steps[0].command.primitive == "se_deplacer"
        ):
            geo = self._exploration.geographic
            direction = proposal.plan.steps[0].command.parameters.get("direction")
            candidates = () if geo is None else tuple(
                target for target in geo.offered
                if target.source_t_monde == t_monde
                and target.direction == direction
                and target.origin == (initial_state.x, initial_state.y)
            )
            if len(candidates) == 1:
                original = Stage8OptionEvaluator.evaluate(
                    self, proposal=proposal,
                    evaluation_state=evaluation_state,
                    initial_state=initial_state,
                    cycle=cycle, t_monde=t_monde,
                    remaining_plan_index=remaining_plan_index,
                )
                evaluation = original.evaluation
                if (
                    evaluation.status == "evaluated"
                    and evaluation.simulated_value_status == "computed"
                    and evaluation.simulated_value is not None
                    and evaluation.simulated_value > 0
                ):
                    interest = self._exploration.geographic_interest_for_target(
                        candidates[0]
                    )
                    if (
                        interest.status == "available"
                        and not set(evaluation.signal_ids) & set(interest.signal_ids)
                    ):
                        evidence = max(-1.0, min(1.0,
                            original.evidence + self._intrinsic_weight * interest.value
                        ))
                        augmented = replace(
                            evaluation, intrinsic_status="applicable",
                            intrinsic_value=interest.value,
                            signal_ids=tuple(evaluation.signal_ids) + interest.signal_ids,
                            producers=tuple(dict.fromkeys(
                                evaluation.producers + ("exploration:p48_instrumental",)
                            )),
                        )
                        result = OptionEvidenceInput(augmented, evidence)
                        result.validate()
                        return result
        if proposal.option.motive_ref.type != "test_causal":
            return super().evaluate(
                proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
                remaining_plan_index=remaining_plan_index,
            )
        if not self._safe_causal_test_shape(proposal):
            # Fail closed to the historical Stage-9 unscored behavior.
            # In particular, do not trust the motive label as evidence.
            return super().evaluate(
                proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
                remaining_plan_index=remaining_plan_index,
            )
        # Stage-8 supplies only the extrinsic term. The Stage-9 P-48 guard
        # remains unchanged on all pre-vNext runtimes.
        original = Stage8OptionEvaluator.evaluate(
            self, proposal=proposal, evaluation_state=evaluation_state,
            initial_state=initial_state, cycle=cycle, t_monde=t_monde,
                remaining_plan_index=remaining_plan_index,
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
