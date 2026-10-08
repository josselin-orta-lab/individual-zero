from __future__ import annotations

import unittest

from i0.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
from i0.interfaces import PrimitiveCommand
from i0.modules import Competition, CompetitionConfig


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
