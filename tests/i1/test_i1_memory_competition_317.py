"""Issue #317: a remembered intention competes without synthetic evidence."""
from dataclasses import replace
from math import exp
from pathlib import Path
import unittest

from i1.modules.competition import Competition, CompetitionConfig

ROOT = Path(__file__).resolve().parents[2]


def native_competition():
    return Competition(CompetitionConfig(
        version="i1-317-test", c_max=5, urgency_max=2.0,
        urgency_scale_cycles=2.0, leak=0.0, noise_sigma=0.0,
        gain=1.0, base_threshold=0.5, threshold_floor=0.1,
        inertia=0.1, residual=0.5, options_max=8,
        substitution_evidence={},
    ))


class MemoryCompetition317Tests(unittest.TestCase):
    def test_five_cycle_evidence_ceiling(self):
        c = native_competition()
        accumulated = sum(
            c.urgency(cycle) * 0.0378 for cycle in range(1, 6)
        )
        self.assertLess(accumulated, 0.5)
        self.assertGreater(accumulated, 0.20)

    def test_fallback_never_decays_unselected_candidates(self):
        c = native_competition()
        from i0.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
        from i0.interfaces import PrimitiveCommand
        option = Option(
            id="memory:neutral:entity:origin:hop", version="1",
            type="primitive", learning_signature="memory_place_return:entity",
            preconditions=("adjacent_passable",),
            success_condition="target_position_observed",
            failure_condition="target_position_not_observed",
            invalidation_condition="observed_entity_place_or_goal_changed",
            motive_ref=MotiveRef(type="place_memory", id="entity"),
            founding_st_version="test", expires_at_step=50,
            provenance="memory", goal_ref="goal-1", plan_ref="plan-1",
            state="candidate",
        )
        plan = Plan(
            id="plan-1", option_ref=option.id, version="1",
            steps=(PlanStep(
                index=0, command=PrimitiveCommand(
                    "se_deplacer", {"direction": "west"}),
                preconditions=("adjacent_passable",),
                observation_window_steps=1,
            ),),
            goal_ref="goal-1", budget_used_uc=1,
            status="valid", st_version="test",
        )
        first = OptionProposal(option=option, plan=plan)
        first.validate()
        self.assertTrue(c.register(first, active_goal_id="goal-1", t_monde=10))
        from i0.contracts import EvaluationOption
        from i1.modules.competition import OptionEvidenceInput
        for cycle in range(1, 6):
            evaluation = EvaluationOption(
                option_ref=option.id, option_version=option.version,
                cycle=cycle, t_monde=10, status="evaluated",
                learned_value_status="unlearned", learned_value=None,
                simulated_value_status="unavailable", simulated_value=None,
                intrinsic_status="applicable", intrinsic_value=0.0311,
                risk_status="unknown", risk=None,
                safety_uncertainty=0.0, protection=False,
                signal_ids=(), producers=("test",),
            )
            result = c.evaluate(
                cycle=cycle, t_monde=10,
                evidence_inputs={option.id: OptionEvidenceInput(
                    evaluation=evaluation, evidence=0.0311)},
            )
            self.assertIsNone(result.winner)
        prior = c.accumulator_for(option.id)
        self.assertGreater(prior, 0)
        c.close_deliberation(None, adjudicated=False)
        c.open_deliberation(active_goal_id="goal-1", t_monde=11)
        again = OptionProposal(
            option=replace(option, expires_at_step=51), plan=plan)
        self.assertTrue(c.register(again, active_goal_id="goal-1", t_monde=11))
        self.assertAlmostEqual(c.accumulator_for(option.id), prior)
        c.open_deliberation(active_goal_id="different-goal", t_monde=12)
        self.assertIsNone(c.accumulator_for(option.id))

    def test_real_adjudication_keeps_original_residual(self):
        c = native_competition()
        c.ensure_wait(t_monde=1, st_version="test")
        # Await is zero-evidence in this fixture, so only fallback semantics differ.
        c.close_deliberation(None, adjudicated=True)
        self.assertEqual(c.accumulator_for("permanent:attendre"), 0)

    def test_memory_option_identifiers_are_not_world_step_keyed(self):
        planner = (ROOT / "src/i1/modules/geographic_planning.py").read_text()
        self.assertIn('option_id = f"option:place-memory:{target.ref}"', planner)
        for name in ("geographic_exploration.py",):
            source = (ROOT / "src/i1/modules" / name).read_text()
            self.assertNotIn('place-memory:{target.ref}:t{target.source_t_monde}', source)
        runtime = (ROOT / "src/i1/runtime/stage11_runtime.py").read_text()
        self.assertNotIn('place-memory:{target.ref}:t{target.source_t_monde}', runtime)


if __name__ == "__main__":
    unittest.main()
