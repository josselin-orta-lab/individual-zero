from __future__ import annotations

import unittest

from i0.contracts import (
    MotiveRef,
    Option,
    OptionProposal,
    Plan,
    PlanStep,
    PredictedConsequence,
)
from i0.interfaces import PrimitiveCommand
from i0.modules import (
    ActionControl,
    ActionControlConfig,
    Admissibility,
    Competition,
    CompetitionConfig,
    StaticSafetyFacts,
)


def proposal(option_id: str, primitive: str) -> OptionProposal:
    plan = Plan(
        id=f"plan:{option_id}:{primitive}",
        option_ref=option_id,
        version=primitive,
        steps=(
            PlanStep(
                index=0,
                command=PrimitiveCommand(primitive),
            ),
        ),
        goal_ref="goal:1",
        budget_used_uc=1,
        status="valid",
        st_version="S_t:1",
    )
    option = Option(
        id=option_id,
        version="1",
        type="primitive",
        learning_signature=f"sig:{option_id}",
        preconditions=(),
        success_condition="goal_satisfied",
        failure_condition="plan_step_failed",
        invalidation_condition="goal_invalid",
        motive_ref=MotiveRef(type="active_goal", id="goal:1"),
        founding_st_version="S_t:1",
        expires_at_step=10,
        provenance="planning",
        goal_ref="goal:1",
        plan_ref=plan.id,
    )
    return OptionProposal(option=option, plan=plan)


def competition() -> Competition:
    return Competition(
        CompetitionConfig(
            version="stage6-replan-comp-v1",
            c_max=3,
            urgency_max=2.0,
            urgency_scale_cycles=2.0,
            leak=0.0,
            noise_sigma=0.0,
            gain=1.0,
            base_threshold=1.0,
            threshold_floor=0.1,
            inertia=0.2,
            residual=0.5,
            options_max=4,
            substitution_evidence={
                "boire": 0.6,
                "dormir": 0.4,
                "attendre": 0.0,
            },
        )
    )


def movement_plan_to(
    *,
    option_id: str,
    x: int,
    y: int,
) -> OptionProposal:
    base = proposal(option_id, "se_deplacer")
    step = PlanStep(
        index=0,
        command=PrimitiveCommand(
            "se_deplacer",
            {"direction": "east"},
        ),
        predicted_consequences=(
            PredictedConsequence(
                variable="position_x",
                value_or_delta=float(x),
                precision=0.0,
            ),
            PredictedConsequence(
                variable="position_y",
                value_or_delta=float(y),
                precision=0.0,
            ),
        ),
    )
    plan = Plan(
        id=f"plan:{option_id}:move:{x}:{y}",
        option_ref=option_id,
        version="move",
        steps=(step,),
        goal_ref=base.option.goal_ref,
        budget_used_uc=1,
        status="valid",
        st_version="S_t:1",
    )
    return OptionProposal(
        option=Option(
            id=base.option.id,
            version=base.option.version,
            type=base.option.type,
            learning_signature=base.option.learning_signature,
            preconditions=base.option.preconditions,
            success_condition=base.option.success_condition,
            failure_condition=base.option.failure_condition,
            invalidation_condition=base.option.invalidation_condition,
            motive_ref=base.option.motive_ref,
            founding_st_version=base.option.founding_st_version,
            expires_at_step=base.option.expires_at_step,
            provenance=base.option.provenance,
            grounding_contribution_refs=base.option.grounding_contribution_refs,
            goal_ref=base.option.goal_ref,
            plan_ref=plan.id,
            state=base.option.state,
        ),
        plan=plan,
    )


class Stage6PlanSafetyTests(unittest.TestCase):
    def control(self, facts: StaticSafetyFacts) -> ActionControl:
        return ActionControl(
            config=ActionControlConfig(
                safety_policy_version="stage6-replan-safety-v1",
                protected_integrity_threshold=20.0,
            ),
            safety_facts=facts,
            protocol_mask=lambda command: False,
        )

    def test_known_lethal_predicted_future_step_blocks_plan_adoption(self) -> None:
        control = self.control(
            StaticSafetyFacts(
                known_lethal_positions=frozenset({(5, 5)}),
            )
        )
        plan = movement_plan_to(
            option_id="option:lethal",
            x=5,
            y=5,
        )

        self.assertIs(
            control.verifier_plan_connu(plan),
            Admissibility.INADMISSIBLE,
        )

    def test_unknown_predicted_future_step_remains_indeterminate(self) -> None:
        control = self.control(StaticSafetyFacts())
        plan = movement_plan_to(
            option_id="option:unknown",
            x=5,
            y=5,
        )

        self.assertIs(
            control.verifier_plan_connu(plan),
            Admissibility.INDETERMINATE,
        )


class Stage6ReplanningCompetitionTests(unittest.TestCase):
    def test_nonengaged_material_replan_resets_accumulator(self) -> None:
        comp = competition()
        original = proposal("option:1", "boire")
        revised = proposal("option:1", "dormir")

        self.assertTrue(
            comp.register(
                original,
                active_goal_id="goal:1",
                t_monde=1,
            )
        )
        comp.open_deliberation(
            active_goal_id="goal:1",
            t_monde=1,
        )
        comp.evaluate(cycle=1, t_monde=1)
        self.assertGreater(comp.accumulator_for("option:1"), 0.0)

        self.assertTrue(
            comp.register(
                revised,
                active_goal_id="goal:1",
                t_monde=1,
            )
        )

        self.assertEqual(comp.accumulator_for("option:1"), 0.0)
        self.assertEqual(
            comp.proposal_for("option:1").plan.version,
            "dormir",
        )

    def test_engaged_material_replan_preserves_engagement(self) -> None:
        comp = competition()
        original = proposal("option:1", "boire")
        revised = proposal("option:1", "dormir")

        comp.register(
            original,
            active_goal_id="goal:1",
            t_monde=1,
        )
        comp.open_deliberation(
            active_goal_id="goal:1",
            t_monde=1,
        )
        comp.evaluate(cycle=1, t_monde=1)
        comp.evaluate(cycle=2, t_monde=1)
        comp.close_deliberation(original)
        before = comp.accumulator_for("option:1")
        self.assertTrue(comp.is_engaged("option:1"))

        comp.register(
            revised,
            active_goal_id="goal:1",
            t_monde=2,
        )

        self.assertTrue(comp.is_engaged("option:1"))
        self.assertEqual(comp.accumulator_for("option:1"), before)
        self.assertEqual(
            comp.proposal_for("option:1").option.id,
            original.option.id,
        )


if __name__ == "__main__":
    unittest.main()
