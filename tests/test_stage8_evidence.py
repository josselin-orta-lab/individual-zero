"""Stage-8 normative evidence and decision tests (8.5, 11, DC-01, INV-07/16).

Controlled rewards are lived-transition fixtures, never oracle targets.
"""
from __future__ import annotations

import unittest
from dataclasses import replace
from math import tanh

from i0.modules.competition import Competition, CompetitionConfig
from i0.modules.stage8_evaluator import Stage8EvaluationConfig, Stage8OptionEvaluator
from i0.modules.td_values import LinearTDValues, TDLearningConfig, ValueFeatureConfig

from test_stage4_modules import proposal
from test_stage6_equipment import state as simulated_state
from test_stage6_evaluator import evaluator_with_drink_transition
from test_stage8_td_values import state as evaluation_state


def live_input():
    return replace(
        simulated_state(),
        body={"energy": 50.0, "food": 60.0, "water": 20.0, "integrity": 100.0},
        current_water_source=True,
    )


def q_model():
    return LinearTDValues(
        TDLearningConfig(
            version="stage8-evidence-td-v1",
            eta=0.5, lambda_e=0.0, beta=0.8, evidence_scale=10.0,
            features=ValueFeatureConfig(
                version="stage8-evidence-phi-v1",
                feature_names=("bias", "water", "goal_drink"),
                position_scale_x=31.0, position_scale_y=31.0,
            ),
        )
    )


def evaluator(q):
    return Stage8OptionEvaluator(
        config=Stage8EvaluationConfig(
            version="stage8-evidence-test-v1",
            n0=3.0, evidence_scale=10.0, extrinsic_gain=1.0,
        ),
        stage6=evaluator_with_drink_transition(include_wait=True),
        q_values=q,
    )


def competition():
    return Competition(CompetitionConfig(
        version="stage8-behavioral-v1",
        c_max=3, urgency_max=2.0, urgency_scale_cycles=2.0,
        leak=0.0, noise_sigma=0.0, gain=1.0,
        base_threshold=0.2, threshold_floor=0.1,
        inertia=0.0, residual=0.0, options_max=4,
        substitution_evidence={"boire": 0.7, "attendre": 0.3},
    ))


class Stage8EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.drink = proposal("drink", "boire")
        self.wait = proposal("wait", "attendre")
        self.eval_state = evaluation_state(20.0)
        self.sim_state = live_input()

    def _evaluate(self, model, proposed):
        return evaluator(model).evaluate(
            proposal=proposed,
            evaluation_state=self.eval_state,
            initial_state=self.sim_state,
            cycle=1, t_monde=1,
        )

    def test_missing_q_keeps_simulation_and_no_implicit_q_state(self):
        model = q_model()
        input_ = self._evaluate(model, self.drink)
        self.assertEqual(input_.evaluation.learned_value_status, "unlearned")
        self.assertIsNone(input_.evaluation.learned_value)
        self.assertEqual(input_.evaluation.simulated_value_status, "computed")
        self.assertGreater(input_.evidence, 0)
        self.assertEqual(model.export_causal_state()["weights"], {})

    def test_no_sim_and_no_q_is_not_evaluated_not_zero(self):
        model = q_model()
        result = self._evaluate(model, proposal("move", "se_deplacer"))
        self.assertEqual(result.evaluation.status, "not_evaluated")
        self.assertIsNone(result.evidence)
        self.assertIsNone(result.evaluation.learned_value)

    def test_evidence_weight_is_exact_n_over_n_plus_n0(self):
        model = q_model()
        model.update_segment(
            previous_state=self.eval_state, previous_signature="sig:drink",
            rewards=(20.0,), next_state=self.eval_state, next_signature="sig:wait",
        )
        result = self._evaluate(model, self.drink)
        learned = model.learned_value(self.eval_state, "sig:drink")
        self.assertEqual(learned.update_count, 1)
        expected = tanh(
            ((learned.value / 4) + (3 * result.evaluation.simulated_value / 4))
            / 10.0
        )
        self.assertAlmostEqual(result.evidence, expected, places=12)

    def test_experienced_consequence_changes_future_option_winner(self):
        # INV-07/16: same options and accessible context, before/after only
        # online lived experience; Competition, not the learner, decides.
        model = q_model()

        def winner():
            comp = competition()
            offered = (self.drink, self.wait)
            for opt in offered:
                self.assertTrue(comp.register(opt, active_goal_id=None, t_monde=1))
            comp.open_deliberation(active_goal_id=None, t_monde=1)
            evidence = {
                opt.option.id: self._evaluate(model, opt)
                for opt in offered
            }
            return comp.evaluate(
                cycle=1, t_monde=1, evidence_inputs=evidence
            ).winner.option.id

        self.assertEqual(winner(), "drink")
        model.update_segment(
            previous_state=self.eval_state, previous_signature="sig:drink",
            rewards=(-400.0,), next_state=self.eval_state,
            next_signature="sig:wait",
        )
        model.update_segment(
            previous_state=self.eval_state, previous_signature="sig:wait",
            rewards=(40.0,), next_state=self.eval_state,
            next_signature="sig:drink",
        )
        self.assertEqual(winner(), "wait")


if __name__ == "__main__":
    unittest.main()
