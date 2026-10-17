"""Stage-10 sleep option must truly enter ordinary Competition and stay budgeted."""
import unittest
from dataclasses import replace

from i0.contracts import EvaluationOption, OptionProposal, PlanStep
from i0.interfaces import PrimitiveCommand
from i0.modules.sleep_pressure import SleepPressureConfig
from i0.modules.sleep_health import SleepHealth
from i0.modules.sleep_competition import create_sleep_proposal, assemble_sleep_evidence
from i0.modules.competition import Competition, CompetitionConfig, OptionEvidenceInput
from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget


def health(t=5):
    cfg = SleepPressureConfig(
        version="P-40:test", fatigue_gain=0.1, sleep_fatigue_recovery=0.1,
        waking_recovery_profile_relief=0.0, fatigue_weight=0.5,
        consolidation_weight=0.5, night_weight=0.0,
        unconsolidated_episode_reference=2.0, memory_saturation_reference=1.0,
        natural_wake_threshold=0.1, alert_wake_threshold=0.6,
        max_consecutive_sleep_steps=4,
    )
    owner = SleepHealth(cfg)
    owner.begin_waking_step(world_step=t, unconsolidated_episodes=2,
                            memory_occupancy=0.0, is_night=False)
    return owner


def charged():
    budget = CycleComputeBudget(config=ComputeBudgetConfig(
        version="P-43:test", cycle_ceiling=4, protected_capacity=0,
        protected_modules=frozenset(),
        module_envelopes={"metacognition_health":4},
        operation_costs={"sleep_option_prepare":1},
    ))
    budget.open_cycle(1)
    return budget.charge(module="metacognition_health", operation="sleep_option_prepare")


def original(proposal, status="not_evaluated", value=None, cycle=1, t=5):
    assessment = EvaluationOption(
        option_ref=proposal.option.id, option_version=proposal.option.version,
        cycle=cycle, t_monde=t, status=status,
        learned_value_status="unlearned", learned_value=None,
        simulated_value_status="unavailable", simulated_value=None,
        intrinsic_status="not_applicable", intrinsic_value=None,
        risk_status="unknown", risk=None, safety_uncertainty=0.0,
        protection=False, signal_ids=(), producers=("value_needs.q_active",),
    )
    result = OptionEvidenceInput(assessment, value)
    result.validate()
    return result


def competition():
    return Competition(CompetitionConfig(
        version="stage10-test", c_max=3, urgency_max=1.0, urgency_scale_cycles=1.0,
        leak=0.0, noise_sigma=0.0, gain=1.0, base_threshold=0.3,
        threshold_floor=0.1, inertia=0.0, residual=0.5, options_max=5,
        substitution_evidence={},
    ))


class SleepCompetitionTests(unittest.TestCase):
    def test_real_budget_charge_and_normative_proposal(self):
        owner = health()
        proposal = create_sleep_proposal(
            health=owner, t_monde=5, st_version="s:5", charged_preparation=charged())
        self.assertEqual(proposal.option.motive_ref.type, "sleep_pressure")
        self.assertEqual(proposal.plan.steps[0].command.primitive, "dormir")
        self.assertEqual(proposal.plan.budget_used_uc, 1)
        self.assertIsNone(proposal.option.goal_ref)
        self.assertEqual(proposal.option.expires_at_step, 6)
        proposal.validate()

    def test_no_sleep_proposal_from_zero_or_unaccepted_budget(self):
        owner = health()
        x = charged()
        with self.assertRaises(ValueError):
            create_sleep_proposal(health=owner, t_monde=5, st_version="s:5",
                                  charged_preparation=replace(x, accepted=False))
        with self.assertRaises(ValueError):
            create_sleep_proposal(health=owner, t_monde=5, st_version="s:5",
                                  charged_preparation=replace(x, requested_uc=0))
        with self.assertRaises(ValueError):
            create_sleep_proposal(health=owner, t_monde=6, st_version="s:6",
                                  charged_preparation=x)

    def test_frozen_pressure_is_ordinary_competition_evidence(self):
        owner = health()
        proposal = create_sleep_proposal(health=owner, t_monde=5,
                                         st_version="s:5", charged_preparation=charged())
        sleep = assemble_sleep_evidence(
            proposal=proposal, base=original(proposal), health=owner,
            t_monde=5, cycle=1, intrinsic_weight=1.0)
        self.assertEqual(sleep.evaluation.intrinsic_status, "applicable")
        self.assertEqual(sleep.evaluation.learned_value_status, "unlearned")
        self.assertEqual(sleep.evaluation.simulated_value_status, "unavailable")
        c = competition()
        self.assertTrue(c.register(proposal, active_goal_id=None, t_monde=5))
        result = c.evaluate(cycle=1, t_monde=5,
                            evidence_inputs={proposal.option.id:sleep})
        self.assertEqual(result.winner.option.id, proposal.option.id)
        self.assertGreater(c.accumulator_for(proposal.option.id), 0.3)

    def test_unverified_sleep_shape_must_freeze_accumulator(self):
        owner = health()
        proposal = create_sleep_proposal(health=owner, t_monde=5,
                                         st_version="s:5", charged_preparation=charged())
        altered = replace(proposal, plan=replace(
            proposal.plan, steps=(PlanStep(index=0, command=PrimitiveCommand("attendre")),)))
        assessment = assemble_sleep_evidence(
            proposal=altered, base=original(altered), health=owner,
            t_monde=5, cycle=1, intrinsic_weight=1.0)
        self.assertEqual(assessment.evaluation.status, "not_evaluated")
        c = competition()
        c.register(altered, active_goal_id=None, t_monde=5)
        c.evaluate(cycle=1, t_monde=5,
                   evidence_inputs={altered.option.id:assessment})
        self.assertEqual(c.accumulator_for(altered.option.id), 0.0)

    def test_score_sums_real_external_and_intrinsic_and_clips(self):
        owner = health()
        proposal = create_sleep_proposal(health=owner, t_monde=5,
                                         st_version="s:5", charged_preparation=charged())
        result = assemble_sleep_evidence(
            proposal=proposal, base=original(proposal, status="evaluated", value=0.8),
            health=owner, t_monde=5, cycle=1, intrinsic_weight=1.0)
        self.assertEqual(result.evidence, 1.0)
        self.assertEqual(result.evaluation.producers,
                         ("value_needs.q_active", "metacognition_health:p40_sleep_pressure"))

    def test_wrong_or_missing_frozen_world_step_cannot_make_evidence(self):
        owner = health()
        proposal = create_sleep_proposal(health=owner, t_monde=5,
                                         st_version="s:5", charged_preparation=charged())
        result = assemble_sleep_evidence(
            proposal=proposal, base=original(proposal, t=6), health=owner,
            t_monde=6, cycle=1, intrinsic_weight=1.0)
        self.assertEqual(result.evaluation.status, "not_evaluated")

    def test_evidence_reusing_intrinsic_signal_is_rejected(self):
        owner = health()
        proposal = create_sleep_proposal(health=owner, t_monde=5,
                                         st_version="s:5", charged_preparation=charged())
        base = original(proposal)
        shared = replace(base, evaluation=replace(
            base.evaluation, signal_ids=(proposal.option.motive_ref.id,)))
        with self.assertRaises(ValueError):
            assemble_sleep_evidence(proposal=proposal, base=shared, health=owner,
                                    t_monde=5, cycle=1, intrinsic_weight=1.0)

    def test_same_world_step_pressure_cannot_change_mid_cycle(self):
        owner = health()
        before = owner.frozen
        again = owner.begin_waking_step(world_step=5, unconsolidated_episodes=0,
                                         memory_occupancy=0.0, is_night=True)
        self.assertEqual(again, before)


if __name__ == "__main__":
    unittest.main()
