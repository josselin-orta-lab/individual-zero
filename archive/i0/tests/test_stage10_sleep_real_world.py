"""Stage-10 physical contract checks with real WorldBody, Competition and Action Control.

These are short software integration tests, not a complete Stage-10 runtime.
No physical command bypasses the Action Control admission/dispatch boundary.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from i0.modules.action_control import (
    ActionControl, ActionControlConfig, StaticSafetyFacts,
)
from i0.modules.perception import PerceptualCapture, PerceivedCell
from i0.modules.competition import Competition, CompetitionConfig
from i0.modules.sleep_health import SleepHealth
from i0.modules.sleep_pressure import SleepPressureConfig, WakeSignals
from i0.modules.sleep_session import SleepSession
from i0.modules.sleep_competition import (
    create_sleep_proposal, assemble_sleep_evidence,
)
from i0.contracts import EvaluationOption
from i0.modules.competition import OptionEvidenceInput
from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget
from lab.world import WorldBody, WorldLayout, Position
from test_world_physics import physics


def health():
    policy = SleepPressureConfig(
        version="sleep:physical-test-v1", fatigue_gain=0.2,
        sleep_fatigue_recovery=0.1,
        waking_recovery_profile_relief=0.0, fatigue_weight=0.5,
        consolidation_weight=0.8, night_weight=0.0,
        unconsolidated_episode_reference=1.0,
        memory_saturation_reference=1.0,
        natural_wake_threshold=0.1, alert_wake_threshold=0.5,
        max_consecutive_sleep_steps=3,
    )
    owner = SleepHealth(policy)
    owner.begin_waking_step(world_step=1, unconsolidated_episodes=1,
                            memory_occupancy=0.0, is_night=False)
    return owner


def charge():
    budget = CycleComputeBudget(config=ComputeBudgetConfig(
        version="compute:sleep:test", cycle_ceiling=4,
        module_envelopes={"metacognition_health":4},
        protected_modules=frozenset(), protected_capacity=0,
        operation_costs={"sleep_option_prepare":1},
    ))
    budget.open_cycle(1)
    return budget.charge(module="metacognition_health",
                         operation="sleep_option_prepare")


def capture(world, step):
    local = world.capture_local(t_monde=step)
    return PerceptualCapture(
        t_monde=step, x=local.position.x, y=local.position.y,
        body=dict(world.telemetry()),
        current_water_source=local.current_water_source,
        current_resources=tuple(local.current_resources),
        adjacent=tuple(
            PerceivedCell(
                direction=cell.direction, x=cell.position.x, y=cell.position.y,
                passable=cell.passable, creature=cell.creature,
                water_source=cell.water_source, resources=tuple(cell.resources),
            ) for cell in local.adjacent
        ),
    )


def competition():
    return Competition(CompetitionConfig(
        version="competition:sleep:test", c_max=2, urgency_max=1.0,
        urgency_scale_cycles=1.0, leak=0.0, noise_sigma=0.0,
        gain=1.0, base_threshold=0.3, threshold_floor=0.1,
        inertia=0.0, residual=0.5, options_max=4,
        substitution_evidence={},
    ))


def admitted_world_sleep(*, world, protocol_mask=lambda _: False):
    owner = health()
    proposal = create_sleep_proposal(
        health=owner, t_monde=1, st_version="s:physical:1",
        charged_preparation=charge(),
    )
    orig = OptionEvidenceInput(
        EvaluationOption(
            option_ref=proposal.option.id, option_version=proposal.option.version,
            cycle=1, t_monde=1, status="not_evaluated",
            learned_value_status="unlearned", learned_value=None,
            simulated_value_status="unavailable", simulated_value=None,
            intrinsic_status="not_applicable", intrinsic_value=None,
            risk_status="unknown", risk=None, safety_uncertainty=0.0,
            protection=False, signal_ids=(), producers=(),
        ), None,
    )
    evidence = assemble_sleep_evidence(
        proposal=proposal, base=orig, health=owner,
        t_monde=1, cycle=1, intrinsic_weight=1.0,
    )
    comp = competition()
    assert comp.register(proposal, active_goal_id=None, t_monde=1)
    decision = comp.evaluate(
        cycle=1, t_monde=1,
        evidence_inputs={proposal.option.id: evidence},
    )
    if decision.winner is None:
        raise AssertionError("sleep should cross in this test configuration")
    control = ActionControl(
        config=ActionControlConfig(
            safety_policy_version="physical-safety-test-v1",
            protected_integrity_threshold=10.0,
        ),
        safety_facts=StaticSafetyFacts(),
        protocol_mask=protocol_mask,
    )
    prepared = control.prepare_option_step(decision.winner)
    sent = []
    admission, result = control.dispatch_if_admitted(
        capture=capture(world, 1), prepared=prepared,
        sender=lambda command: (sent.append(command), world.apply(command, t_monde=1))[1],
    )
    session = SleepSession(wake_policy_version=owner.rules.config.version)
    session.open_world_step(1)
    if admission.ok and result is not None and not result.lethal:
        session.record_applied_sleep_decision(
            world_step=1, admission=admission, prepared=prepared,
            motive_type=proposal.option.motive_ref.type,
            execution_status="applied",
        )
    return session, owner, control, prepared, admission, result, sent


class SleepPhysicalIntegrationTests(unittest.TestCase):
    def test_competition_control_real_dormir_enters_sleep_next_step(self):
        world = WorldBody(config=physics(), layout=WorldLayout())
        before = world.telemetry()["energy"]
        session, _, _, _, admission, transition, sent = admitted_world_sleep(world=world)
        self.assertTrue(admission.ok)
        self.assertEqual(len(sent), 1)
        self.assertEqual(transition.command.primitive, "dormir")
        self.assertEqual(transition.effects["rest"], "dormir")
        self.assertGreater(transition.body_after.energy, before)
        self.assertEqual(session.mode, "awake")
        self.assertEqual(session.open_world_step(2), "sleeping")
        self.assertEqual(session.sleep_duration, 1)

    def test_protocol_veto_prevents_world_transition_and_sleep(self):
        world = WorldBody(config=physics(), layout=WorldLayout())
        before = deepcopy(world.export_causal_state())
        session, _, _, _, admission, transition, sent = admitted_world_sleep(
            world=world, protocol_mask=lambda command: command.primitive == "dormir")
        self.assertFalse(admission.ok)
        self.assertEqual(admission.reason, "protocol_mask")
        self.assertIsNone(transition)
        self.assertEqual(sent, [])
        self.assertEqual(world.export_causal_state(), before)
        self.assertEqual(session.open_world_step(2), "awake")

    def test_sleeping_reflex_is_admitted_by_control_and_advances_real_world(self):
        world = WorldBody(
            config=physics(),
            layout=WorldLayout(creatures=frozenset({Position(2, 3)})),
        )
        session, owner, control, _, _, _, _ = admitted_world_sleep(world=world)
        self.assertEqual(session.open_world_step(2), "sleeping")
        perception = capture(world, 2)
        reflex = control.reflex(perception)
        self.assertIsNotNone(reflex)
        self.assertEqual(reflex.prepared.command.primitive, "se_deplacer")
        admission, physical = control.dispatch_if_admitted(
            capture=perception, prepared=reflex.prepared,
            sender=lambda command: world.apply(command, t_monde=2),
        )
        self.assertTrue(admission.ok)
        self.assertFalse(physical.lethal)
        signals = WakeSignals(
            admitted_reflex=True, reduced_perception_alert=None,
            authorized_dated_intention_due=False,
            consecutive_sleep_steps=session.sleep_duration,
            consolidation_active=False,
        )
        outcome = session.evaluate_sleep_step(
            signals=signals, frozen_sleep_pressure=owner.frozen.sleep_pressure,
            wake_rule=owner.rules,
        )
        self.assertEqual(outcome.reason, "reflex")
        self.assertFalse(outcome.resume_cognition)
        session.finish_sleep_step(
            decision=outcome, admission=admission, prepared=reflex.prepared,
            command_sent=True, world_advanced=True,
            consolidation_interrupted=False,
        )
        self.assertEqual(session.mode, "awake")
        self.assertEqual(world.position, physical.position_after)

    def test_sleep_cannot_be_armed_by_unapplied_or_refused_command(self):
        world = WorldBody(config=physics(), layout=WorldLayout())
        session, owner, _, prepared, admission, _, _ = admitted_world_sleep(
            world=world, protocol_mask=lambda command: True,
        )
        with self.assertRaises(ValueError):
            session.record_applied_sleep_decision(
                world_step=1, admission=admission, prepared=prepared,
                motive_type="sleep_pressure", execution_status="applied",
            )
        self.assertEqual(session.mode, "awake")


if __name__ == "__main__":
    unittest.main()
