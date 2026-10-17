from __future__ import annotations

from dataclasses import replace
import unittest

from i0.modules import (
    CompetitionConfig,
    GatekeeperConfig,
    GoalManagerConfig,
    PlanningConfig,
    StaticSafetyFacts,
    ValueNeedsConfig,
)
from lab.compute_budget import ComputeBudgetConfig
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage4_runtime import Stage4Config, Stage4Runtime
from lab.world import (
    BerryEffect,
    BodyState,
    Position,
    ToolRecipe,
    WorldLayout,
    WorldPhysicsConfig,
)


def world_config(*, water: float = 20.0) -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="stage4-runtime-test-world-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0,
            food=60.0,
            water=water,
            integrity=100.0,
        ),
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={
            "se_deplacer": 0.0,
            "collecter": 0.0,
            "manger": 0.0,
            "boire": 0.0,
            "poser_une_pierre": 0.0,
            "fabriquer_outil": 0.0,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
        drink_water_gain=40.0,
        berry_effects={
            "berry_a": BerryEffect(10.0, 0.0),
            "berry_b": BerryEffect(5.0, -100.0),
        },
        creature_damage=0.0,
        danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


def stage4_config() -> Stage4Config:
    return Stage4Config(
        version="stage4-runtime-test-v1",
        perception_ttl_steps=5,
        value_needs=ValueNeedsConfig(
            version="stage4-needs-v1",
            setpoints={
                "energy": 50.0,
                "food": 60.0,
                "water": 60.0,
                "integrity": 100.0,
            },
            weights={
                "energy": 1.0,
                "food": 1.0,
                "water": 1.0,
                "integrity": 1.0,
            },
            normalization_scales={
                "energy": 100.0,
                "food": 100.0,
                "water": 100.0,
                "integrity": 100.0,
            },
            p_min=0.1,
            contribution_ttl_steps=5,
        ),
        goals=GoalManagerConfig(
            version="stage4-goals-v1",
            p_min=0.1,
            replacement_hysteresis=0.1,
            critical_pressure=0.9,
            impossible_failures_required=2,
            refractory_steps=3,
        ),
        gatekeeper=GatekeeperConfig(
            version="stage4-gate-v1",
            k_slots=4,
            recency_window_steps=5,
            replacement_hysteresis=0.1,
            safety_threshold=0.8,
            queue_capacity=10,
            emission_quota=20,
            slot_quota=2,
            quota_window_steps=3,
            weights={
                "b": 1.0,
                "n": 1.0,
                "urg": 1.0,
                "risk": 1.0,
                "value": 1.0,
            },
        ),
        planning=PlanningConfig(
            version="stage4-plan-v1",
            option_ttl_steps=20,
        ),
        competition=CompetitionConfig(
            version="stage4-comp-v1",
            c_max=5,
            urgency_max=2.0,
            urgency_scale_cycles=2.0,
            leak=0.0,
            noise_sigma=0.0,
            gain=1.0,
            base_threshold=0.5,
            threshold_floor=0.1,
            inertia=0.1,
            residual=0.5,
            options_max=8,
            substitution_evidence={
                "se_deplacer": 1.0,
                "collecter": 1.0,
                "manger": 1.0,
                "boire": 1.0,
                "dormir": 1.0,
                "attendre": 0.0,
                "poser_une_pierre": 0.5,
                "fabriquer_outil": 0.5,
            },
        ),
        compute_budget=ComputeBudgetConfig(
            version="stage4-budget-v1",
            cycle_ceiling=100,
            module_envelopes={
                "perception": 20,
                "value_needs": 10,
                "goal_manager": 10,
                "planning": 20,
                "bus": 10,
                "gatekeeper": 10,
                "competition": 30,
                "action_control": 10,
            },
            protected_modules=frozenset({
                "bus",
                "gatekeeper",
                "action_control",
            }),
            protected_capacity=20,
            operation_costs={
                "perception_publish": 1,
                "value_needs_cycle": 1,
                "goal_arbitrate": 1,
                "planning_build": 2,
                "bus_pour": 1,
                "gatekeeper_select": 1,
                "competition_register": 1,
                "competition_evaluate": 1,
                "control_admit": 1,
            },
        ),
    )


def runtime(
    *,
    water: float = 20.0,
    layout: WorldLayout | None = None,
    config: Stage4Config | None = None,
) -> Stage4Runtime:
    return Stage4Runtime(
        world_config=world_config(water=water),
        layout=layout or WorldLayout(),
        safety_config=SafetyProtocolConfig(
            version="stage4-safety-v1",
            lethal_max=2,
            mode="campaign",
        ),
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
        config=config or stage4_config(),
    )


class Stage4OwnershipTests(unittest.TestCase):
    def test_causal_state_owners_are_unique_and_include_stage4_owners(self) -> None:
        instance = runtime()
        owner_ids = [owner.owner_id for owner in instance.causal_owners]

        self.assertEqual(len(owner_ids), len(set(owner_ids)))
        for required in {
            "perception",
            "action_control",
            "value_and_needs",
            "goal_manager",
            "gatekeeper",
            "s_t",
            "planning",
            "competition",
            "metacognition_health",
            "scheduler.compute_budget",
        }:
            self.assertIn(required, owner_ids)


class Stage4IntegratedLoopTests(unittest.TestCase):
    def test_thirst_goal_appears_before_plan_and_first_move(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
            )
        )

        result = instance.run_step()

        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.source, "decision")
        self.assertEqual(result.command_primitive, "se_deplacer")
        self.assertEqual(instance.world.position, Position(3, 2))
        self.assertEqual(result.cycles_used, 3)

        events = [entry.causal_event for entry in instance.journal.entries]
        goal_changes = [
            event for event in events
            if event.get("kind") == "active_goal_changed"
        ]
        registrations = [
            event for event in events
            if event.get("kind") == "option_registration"
        ]
        self.assertEqual(goal_changes[0]["cycle"], 2)
        self.assertEqual(registrations[0]["cycle"], 3)

    def test_multi_step_drink_plan_advances_across_world_steps(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
            )
        )

        first = instance.run_step()
        second = instance.run_step()
        third = instance.run_step()

        # A genuine visible source one tile away supports a complete
        # two-command E-0 plan, then a subsequent non-goal fallback.
        self.assertEqual(first.command_primitive, "se_deplacer")
        self.assertEqual(second.command_primitive, "boire")
        self.assertEqual(third.command_primitive, "attendre")
        self.assertEqual(instance.world.position, Position(3, 2))
        self.assertEqual(instance.world.body.water, 60.0)

    def test_position_comparator_confirms_predicted_movements(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
            )
        )

        instance.run_step()
        instance.run_step()
        instance.run_step()

        comparisons = [
            entry.causal_event
            for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "agency_comparison"
        ]
        # With a legitimately *adjacent* visible water source, E-0 plans
        # one movement and then one drink. A historical two-movement target
        # was out of perception and MUST NOT be restored to satisfy this test.
        self.assertEqual(len(comparisons), 1)
        self.assertEqual(comparisons[0]["data"]["status"], "conforming")
        self.assertEqual(
            comparisons[0]["data"]["attribution"], "self_compatible",
        )
        transitions = [
            entry.causal_event for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "world_transition_experienced"
        ]
        # The physical transition event intentionally does NOT expose a
        # primitive: join it to its independently logged selected command
        # by the attempt identifier, not by an invented event field.
        commands = [
            entry.causal_event for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "command_experienced"
        ]
        self.assertGreaterEqual(len(transitions), 2)
        self.assertEqual(
            [event["primitive"] for event in commands[:2]],
            ["se_deplacer", "boire"],
        )
        self.assertEqual(
            [(e["t_monde"], e["attempt_ref"]) for e in commands[:2]],
            [(e["t_monde"], e["attempt_ref"]) for e in transitions[:2]],
        )
        self.assertEqual(instance.world.body.water, 60.0)

    def test_blocked_movement_is_nonconforming_and_invalidates_plan(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
            )
        )

        # A visible blocked neighbor must not be deliberately chosen. Here
        # the neighbor is visibly passable but the external physical scenario
        # makes the first attempted motor command fail. I0 sees only the
        # resulting nonconformance, not the hidden failure schedule.
        instance.world.apply_scenario_event(
            "set_action_failure_schedule",
            {"primitive": "se_deplacer", "schedule": [True]},
        )
        first = instance.run_step()
        self.assertEqual(first.command_primitive, "se_deplacer")
        self.assertEqual(instance.world.position, Position(2, 2))

        instance.run_step()

        comparisons = [
            entry.causal_event
            for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "agency_comparison"
        ]
        self.assertGreaterEqual(len(comparisons), 1)
        self.assertEqual(comparisons[0]["data"]["status"], "nonconforming")
        self.assertEqual(comparisons[0]["data"]["attribution"], "uncertain")

    def test_unseen_two_cell_water_does_not_create_oracle_plan(self) -> None:
        # An unobserved resource may exist physically without becoming
        # first-person knowledge or a fabricated action proposal. This
        # negative witness preserves the original two-cell world scenario.
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(4, 2)}),
            )
        )
        first = instance.run_step()
        self.assertEqual(first.execution_status, "applied")
        self.assertEqual(first.source, "fallback")
        self.assertEqual(first.command_primitive, "attendre")
        self.assertEqual(instance.world.position, Position(2, 2))
        self.assertIsNone(instance.planning.current_plan)
        kinds = [e.causal_event.get("kind") for e in instance.journal.entries]
        self.assertIn("active_goal_changed", kinds)
        self.assertNotIn("option_registration", kinds)

    def test_no_active_need_reaches_cmax_fallback_wait(self) -> None:
        instance = runtime(water=60.0)

        result = instance.run_step()

        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.source, "fallback")
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.command_primitive, "attendre")
        self.assertEqual(result.cycles_used, 5)

    def test_planning_budget_exhaustion_degrades_but_cycle_closes(self) -> None:
        config = stage4_config()
        constrained_budget = replace(
            config.compute_budget,
            module_envelopes={
                **dict(config.compute_budget.module_envelopes),
                "planning": 0,
            },
        )
        constrained = replace(
            config,
            compute_budget=constrained_budget,
        )
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(4, 2)}),
            ),
            config=constrained,
        )

        result = instance.run_step()

        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.source, "fallback")
        self.assertEqual(result.command_primitive, "attendre")
        self.assertEqual(
            instance.metacognition.state.budget_state,
            "degraded",
        )

        accepted_uc = sum(
            event["data"]["requested_uc"]
            for event in (
                entry.causal_event for entry in instance.journal.entries
            )
            if event.get("kind") == "compute_charge"
            and event["data"]["accepted"]
        )
        self.assertEqual(
            instance.metacognition.state.f_cog_uc_counter,
            accepted_uc,
        )

    def test_reflex_preempts_cognition_and_uses_zero_cycles(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                creatures=frozenset({Position(3, 2)}),
            )
        )

        result = instance.run_step()

        self.assertEqual(result.source, "reflex")
        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.cycles_used, 0)
        self.assertEqual(instance.world.position, Position(1, 2))

        cognitive_cycles = [
            entry for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "cycle_opened"
        ]
        self.assertEqual(cognitive_cycles, [])

    def test_every_cognitive_command_traces_to_option_and_st_version(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
            )
        )
        result = instance.run_step()
        self.assertEqual(result.source, "decision")

        admitted = [
            entry.causal_event
            for entry in instance.journal.entries
            if entry.causal_event.get("kind") == "command_admitted"
            and entry.causal_event["data"].get("source") == "decision"
        ]
        self.assertEqual(len(admitted), 1)
        self.assertIsNotNone(admitted[0]["data"]["option_ref"])
        founding_version = admitted[0]["data"]["st_version_ref"]
        self.assertIsNotNone(founding_version)
        grounding = admitted[0]["data"]["grounding_contribution_refs"]
        self.assertGreaterEqual(len(grounding), 1)

        founding_events = [
            event
            for event in (entry.causal_event for entry in instance.journal.entries)
            if event.get("kind") == "s_t_published"
            and event["data"]["version"] == founding_version
        ]
        self.assertEqual(len(founding_events), 1)
        retained = set(founding_events[0]["data"]["competitive_refs"])
        self.assertTrue(set(grounding).issubset(retained))

    def test_lethal_cognitive_decision_rolls_back_full_cognition_then_masks_it(self) -> None:
        instance = runtime(
            layout=WorldLayout(
                water_sources=frozenset({Position(3, 2)}),
                lethal_zones=frozenset({Position(3, 2)}),
            )
        )

        before_world = instance.world.export_causal_state()
        result = instance.run_step()

        self.assertEqual(instance.bench.metrics.lethal_transitions, 1)
        self.assertEqual(instance.bench.metrics.lethal_rollbacks, 1)
        self.assertEqual(instance.world.position, Position(2, 2))
        self.assertEqual(
            instance.world.export_causal_state()["position"],
            before_world["position"],
        )
        self.assertEqual(result.execution_status, "applied")
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.command_primitive, "attendre")

        autobiography = instance.stage3.substrate.autobiographical_view()
        self.assertEqual(len(autobiography), 2)
        self.assertEqual(autobiography[0]["primitive"], "attendre")

        technical_kinds = [
            entry.causal_event.get("kind")
            for entry in instance.journal.entries
        ]
        self.assertIn("lethal_transition_detected", technical_kinds)
        self.assertIn("lethal_rollback_completed", technical_kinds)
        self.assertIn("command_vetoed", technical_kinds)

    def test_guarded_uc_occurrence_survives_actual_cognitive_lethal_rollback(self):
        # This exercises the actual Stage-4 lethal checkpoint and new
        # Scheduler attempt, rather than a synthetic owner-only restore.
        # Stage-11 inherits this Stage-4 cognitive/physical dispatch path.
        def independent():
            prior = stage4_config()
            guarded = replace(
                prior,
                version=prior.version + "+uc-occurrence-lethal-dev-v1",
                compute_budget=replace(
                    prior.compute_budget,
                    version=prior.compute_budget.version
                    + "+uc-occurrence-lethal-dev-v1",
                    cycle_occurrence_guard=True,
                ),
            )
            instance = runtime(
                layout=WorldLayout(
                    water_sources=frozenset({Position(3, 2)}),
                    lethal_zones=frozenset({Position(3, 2)}),
                ),
                config=guarded,
            )
            result = instance.run_step()
            self.assertEqual(instance.bench.metrics.lethal_transitions, 1)
            self.assertEqual(instance.bench.metrics.lethal_rollbacks, 1)
            self.assertEqual(result.execution_status, "applied")
            self.assertTrue(result.fallback_used)
            self.assertEqual(result.command_primitive, "attendre")
            self.assertEqual(instance.world.position, Position(2, 2))

            technical = [entry.causal_event for entry in instance.journal.entries]
            kinds = [entry["kind"] for entry in technical]
            self.assertEqual(kinds.count("lethal_transition_detected"), 1)
            self.assertEqual(kinds.count("lethal_rollback_completed"), 1)
            self.assertGreaterEqual(kinds.count("snapshot_restored"), 1)
            # The first attempt may legitimately require several cycles
            # BEFORE the lethal command. Partition by the actual rollback
            # receipt, not by the first two cycle_opened records.
            rollback_at = kinds.index("lethal_rollback_completed")
            cycles_before = [
                (event["t_monde"], event["attempt_ref"], event["cycle"])
                for index, event in enumerate(technical)
                if event["kind"] == "cycle_opened" and index < rollback_at
            ]
            cycles_after = [
                (event["t_monde"], event["attempt_ref"], event["cycle"])
                for index, event in enumerate(technical)
                if event["kind"] == "cycle_opened" and index > rollback_at
            ]
            self.assertTrue(cycles_before)
            self.assertTrue(cycles_after)
            self.assertEqual(cycles_before[-1][0], 1)
            self.assertEqual(cycles_after[0][0], 1)
            self.assertNotEqual(
                cycles_before[-1][1], cycles_after[0][1],
            )
            self.assertGreater(
                cycles_after[0][2], cycles_before[-1][2],
            )
            cycles = cycles_before + cycles_after
            budget = instance.compute_budget.export_causal_state()
            self.assertEqual(
                budget["active_occurrence"],
                {
                    "t_monde": cycles[-1][0],
                    "attempt_ref": cycles[-1][1],
                    "cycle": cycles[-1][2],
                },
            )
            self.assertGreater(budget["consumed_cycle_uc"], 0)
            self.assertEqual(
                instance.stage3.substrate.autobiographical_view()[0]["primitive"],
                "attendre",
            )
            self.assertTrue(instance.journal.verify())
            return (
                result,
                budget,
                instance.journal.canonical_bytes(),
                instance.journal.head_hash,
                {
                    owner.owner_id: owner.export_causal_state()
                    for owner in instance.causal_owners
                },
            )
        self.assertEqual(independent(), independent())

    def test_same_minimal_cognitive_run_replays_identically(self) -> None:
        def execute():
            instance = runtime(
                layout=WorldLayout(
                    water_sources=frozenset({Position(4, 2)}),
                )
            )
            for _ in range(4):
                instance.run_step()
            return (
                instance.journal.canonical_bytes(),
                {
                    owner.owner_id: owner.export_causal_state()
                    for owner in instance.causal_owners
                },
            )

        journal_a, state_a = execute()
        journal_b, state_b = execute()

        self.assertEqual(journal_a, journal_b)
        self.assertEqual(state_a, state_b)


if __name__ == "__main__":
    unittest.main()
