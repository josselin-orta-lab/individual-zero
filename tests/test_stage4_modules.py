from __future__ import annotations

import unittest

from i0.contracts import (
    Contribution,
    Goal,
    GoalProposal,
    MotiveRef,
    Option,
    OptionProposal,
    Plan,
    PlanStep,
)
from i0.interfaces import PrimitiveCommand
from i0.modules import (
    CognitiveSpace,
    Competition,
    CompetitionConfig,
    Gatekeeper,
    GatekeeperConfig,
    GoalManager,
    GoalManagerConfig,
    GreedyPlannerE0,
    PlanningConfig,
    ValueAndNeeds,
    ValueNeedsConfig,
)
from i0.modules.perception import PerceivedEntity


def need_config() -> ValueNeedsConfig:
    return ValueNeedsConfig(
        version="stage4-needs-test-v1",
        setpoints={"energy": 50, "food": 60, "water": 60, "integrity": 100},
        weights={"energy": 1, "food": 1, "water": 1, "integrity": 1},
        normalization_scales={
            "energy": 100,
            "food": 100,
            "water": 100,
            "integrity": 100,
        },
        p_min=0.1,
        contribution_ttl_steps=5,
    )


class ValueNeedsTests(unittest.TestCase):
    def test_deficit_is_zero_above_setpoint(self) -> None:
        module = ValueAndNeeds(need_config())
        state = module.assess(
            {"energy": 70, "food": 80, "water": 90, "integrity": 100}
        )
        self.assertEqual(state.deficits, {
            "energy": 0.0,
            "food": 0.0,
            "water": 0.0,
            "integrity": 0.0,
        })

    def test_thirst_produces_alert_and_goal_proposal(self) -> None:
        module = ValueAndNeeds(need_config())
        state = module.assess(
            {"energy": 50, "food": 60, "water": 20, "integrity": 100}
        )
        alerts, proposals = module.produce(state=state, t_monde=1, cycle=1)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0].goal_type, "drink")
        self.assertEqual(alerts[0].signal_family, "value_needs")

    def test_reward_is_reduction_of_weighted_deviation(self) -> None:
        module = ValueAndNeeds(need_config())
        first = module.assess(
            {"energy": 50, "food": 60, "water": 20, "integrity": 100}
        )
        self.assertEqual(module.reward_for(first), 0.0)
        second = module.assess(
            {"energy": 50, "food": 60, "water": 40, "integrity": 100}
        )
        self.assertGreater(module.reward_for(second), 0.0)


class GoalManagerTests(unittest.TestCase):
    def manager(self) -> GoalManager:
        return GoalManager(
            GoalManagerConfig(
                version="stage4-goals-test-v1",
                p_min=0.1,
                replacement_hysteresis=0.2,
                critical_pressure=0.9,
                impossible_failures_required=2,
                refractory_steps=3,
            )
        )

    @staticmethod
    def proposal(goal_type: str, pressure: float, ident: str) -> GoalProposal:
        return GoalProposal(
            id=ident,
            source="value_needs",
            goal_type=goal_type,
            target=goal_type,
            base_pressure=pressure,
            current_pressure=pressure,
            justification_ref="alert",
            t_monde=1,
            cycle=1,
            rule_version="v1",
        )

    def test_highest_pressure_activates(self) -> None:
        manager = self.manager()
        goal = manager.arbitrate(
            [
                self.proposal("eat", 0.3, "a"),
                self.proposal("drink", 0.6, "b"),
            ],
            t_monde=1,
            cycle=1,
        )
        self.assertIsNotNone(goal)
        self.assertEqual(goal.goal_type, "drink")

    def test_hysteresis_prevents_small_replacement(self) -> None:
        manager = self.manager()
        manager.arbitrate(
            [self.proposal("drink", 0.6, "a")],
            t_monde=1,
            cycle=1,
        )
        goal = manager.arbitrate(
            [
                self.proposal("drink", 0.6, "a2"),
                self.proposal("eat", 0.7, "b"),
            ],
            t_monde=1,
            cycle=2,
        )
        self.assertEqual(goal.goal_type, "drink")

    def test_abandonment_requires_configured_failures(self) -> None:
        manager = self.manager()
        manager.arbitrate(
            [self.proposal("drink", 0.6, "a")],
            t_monde=1,
            cycle=1,
        )
        self.assertFalse(
            manager.note_non_plannable(material_context_hash="ctx", t_monde=1)
        )
        self.assertTrue(
            manager.note_non_plannable(material_context_hash="ctx", t_monde=2)
        )
        self.assertIsNone(manager.active_goal)


def contribution(
    ident: str,
    *,
    subject: str,
    module: str = "perception",
    risk: float = 0.0,
    urgency: float = 0.0,
    value: float = 0.0,
    t: int = 1,
) -> Contribution:
    return Contribution(
        id=ident,
        schema_version="mvp-v1.2.1",
        type="observation",
        summary=ident,
        subject_ref=subject,
        emitter_module=module,
        signal_family="world_symbolic",
        confidence=1.0,
        urgency=urgency,
        risk=risk,
        value=value,
        production_t=t,
        production_cycle=1,
        expires_at_step=t + 10,
        payload={},
    )


class GatekeeperTests(unittest.TestCase):
    def gatekeeper(self, *, k: int = 2, queue: int = 2) -> Gatekeeper:
        return Gatekeeper(
            GatekeeperConfig(
                version="stage4-gate-test-v1",
                k_slots=k,
                recency_window_steps=4,
                replacement_hysteresis=0.1,
                safety_threshold=0.8,
                queue_capacity=queue,
                emission_quota=20,
                slot_quota=1,
                quota_window_steps=3,
                weights={"b": 1, "n": 1, "urg": 1, "risk": 1, "value": 1},
            )
        )

    def test_safety_preemption_takes_first_slot(self) -> None:
        result = self.gatekeeper().select(
            [
                contribution("normal", subject="a", value=1.0),
                contribution("danger", subject="b", risk=0.9),
            ],
            active_goal=None,
            t_monde=1,
        )
        self.assertEqual(result.elements[0].contribution_ref, "danger")
        self.assertTrue(result.elements[0].preempted)

    def test_queue_is_bounded(self) -> None:
        result = self.gatekeeper(k=1, queue=1).select(
            [
                contribution("a", subject="a"),
                contribution("b", subject="b"),
                contribution("c", subject="c"),
            ],
            active_goal=None,
            t_monde=1,
        )
        statuses = {f.contribution_ref: f.status for f in result.feedback}
        self.assertEqual(sum(v == "queued" for v in statuses.values()), 1)
        self.assertEqual(sum(v == "evicted" for v in statuses.values()), 1)


class CognitiveSpaceTests(unittest.TestCase):
    def test_published_version_is_immutable(self) -> None:
        store = CognitiveSpace(individual_id="i0")
        version = store.publish(
            cycle=1,
            t_monde=1,
            fixed={"body": {"water": 30}},
            competitive=(),
        )
        with self.assertRaises(TypeError):
            version.fixed["body"] = {}  # type: ignore[index]
        with self.assertRaises(TypeError):
            version.fixed["body"]["water"] = 50  # type: ignore[index]


class PlannerTests(unittest.TestCase):
    def test_e0_builds_route_to_water_then_drinks(self) -> None:
        planner = GreedyPlannerE0(
            PlanningConfig(version="stage4-plan-test-v1", option_ttl_steps=5)
        )
        goal = Goal(
            id="goal-water",
            goal_type="drink",
            target="water",
            satisfaction_condition="water_at_setpoint",
            principal_measure="water",
            current_pressure=0.5,
            state="active",
            activation_t=1,
            activation_cycle=1,
        )
        proposal = planner.propose(
            goal=goal,
            st_version="S_t:1",
            position=(2, 2),
            known_entities={
                "water_source:0": PerceivedEntity(
                    entity_id="water_source:0",
                    entity_type="water_source",
                    x=4,
                    y=2,
                    properties={},
                )
            },
            t_monde=1,
            cycle=2,
        )
        self.assertIsNotNone(proposal)
        primitives = [s.command.primitive for s in proposal.plan.steps]
        self.assertEqual(primitives, ["se_deplacer", "se_deplacer", "boire"])


def proposal(option_id: str, primitive: str, *, expires: int = 10) -> OptionProposal:
    plan = Plan(
        id=f"plan:{option_id}",
        option_ref=option_id,
        version="1",
        steps=(PlanStep(index=0, command=PrimitiveCommand(primitive)),),
        goal_ref=None,
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
        success_condition="done",
        failure_condition="failed",
        invalidation_condition="invalid",
        motive_ref=MotiveRef(type="default", id="default"),
        founding_st_version="S_t:1",
        expires_at_step=expires,
        provenance="default",
        plan_ref=plan.id,
    )
    return OptionProposal(option=option, plan=plan)


class CompetitionTests(unittest.TestCase):
    def competition(self, *, max_options: int = 2) -> Competition:
        return Competition(
            CompetitionConfig(
                version="stage4-comp-test-v1",
                c_max=3,
                urgency_max=2,
                urgency_scale_cycles=2,
                leak=0.0,
                noise_sigma=0.0,
                gain=1.0,
                base_threshold=1.0,
                threshold_floor=0.1,
                inertia=0.2,
                residual=0.5,
                options_max=max_options,
                substitution_evidence={"attendre": 0.2, "boire": 0.6, "dormir": 0.4},
            )
        )

    def test_candidate_registry_is_bounded_excluding_wait(self) -> None:
        comp = self.competition(max_options=2)
        comp.ensure_wait(t_monde=1, st_version="S_t:1")
        for ident in ("a", "b", "c"):
            comp.register(proposal(ident, "boire"), active_goal_id=None, t_monde=1)
        self.assertLessEqual(comp.registry_size, 3)

    def test_threshold_crossing_selects_largest_relative_margin(self) -> None:
        comp = self.competition()
        comp.register(proposal("drink", "boire"), active_goal_id=None, t_monde=1)
        comp.register(proposal("sleep", "dormir"), active_goal_id=None, t_monde=1)
        comp.open_deliberation(active_goal_id=None, t_monde=1)
        first = comp.evaluate(cycle=1, t_monde=1)
        self.assertIsNone(first.winner)
        second = comp.evaluate(cycle=2, t_monde=1)
        self.assertIsNotNone(second.winner)
        self.assertEqual(second.winner.option.id, "drink")

    def test_engaged_option_restarts_from_zero_on_opening(self) -> None:
        comp = self.competition()
        p = proposal("drink", "boire")
        comp.register(p, active_goal_id=None, t_monde=1)
        comp.open_deliberation(active_goal_id=None, t_monde=1)
        comp.evaluate(cycle=1, t_monde=1)
        comp.evaluate(cycle=2, t_monde=1)
        comp.close_deliberation(p)
        comp.open_deliberation(active_goal_id=None, t_monde=2)
        result = comp.evaluate(cycle=1, t_monde=2)
        trace = next(t for t in result.traces if t.option_ref == "drink")
        self.assertEqual(trace.accumulator_before, 0.0)


if __name__ == "__main__":
    unittest.main()
