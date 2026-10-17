"""Stage-11 Action Control handoff contract, with TEST-ONLY prior witnesses.

No simulator or world truth is injected into production. The external
dispatch is mocked: these assertions check that a prospective prediction is
sealed *before* any send and that the original plan remains unchanged.
"""
from unittest import TestCase
from unittest.mock import Mock, patch

from i0.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import PreparedCommand
from lab.stage2_runtime import CommandExecution
from lab.stage9_runtime import Stage9Runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime

from test_stage11_lived_prediction import row


def safe_causal_proposal():
    option_id = "option:causal-test:causal:hydration:v1"
    plan_id = f"plan:{option_id}:v1"
    plan = Plan(
        id=plan_id, option_ref=option_id, version="1",
        steps=(PlanStep(
            index=0, command=PrimitiveCommand("boire"),
            preconditions=("water_source_present",),
            predicted_consequences=(), observation_window_steps=1,
        ),),
        goal_ref=None, budget_used_uc=1, status="valid",
        st_version="S_t:previous",
    )
    option = Option(
        id=option_id, version="1", type="primitive",
        learning_signature="causal_test:boire:water:water_source:observation",
        preconditions=("water_source_present",),
        success_condition="agency_observation_received",
        failure_condition="observation_missing_or_nonconforming",
        invalidation_condition="causal_hypothesis_or_context_changed",
        motive_ref=MotiveRef(
            type="test_causal", id="test_causal:causal:hydration",
        ),
        founding_st_version="S_t:previous",
        expires_at_step=10, provenance="test_causal",
        plan_ref=plan_id,
    )
    proposal = OptionProposal(option=option, plan=plan)
    proposal.validate()
    return proposal


class ProspectiveDispatchTests(TestCase):
    def test_prior_closed_witness_is_frozen_before_dispatch(self):
        runtime = build_stage11_reference_runtime(
            enable_lived_prediction=True,
        )
        proposal = safe_causal_proposal()
        self.assertTrue(runtime.stage8_option_evaluator._safe_causal_test_shape(proposal))
        prepared = runtime.stage3.control.prepare_option_step(proposal)
        self.assertEqual(prepared.predicted_consequences, ())
        runtime._stage11_prospective_state = {
            "lived_causal_actions": [row(
                step=1, before=40, after=52,
                position=(2,2),
            )],
            "causal_action_witnesses": [],
        }
        runtime._stage11_prospective_capture = (4, (2,2), 50.0)
        logged = []
        forwarded = []

        def dispatch(_instance, **kwargs):
            forwarded.append(kwargs["prepared"])
            # Simulated rollback: even if the actual send fails, this
            # prospective observation is never counted as a visit.
            return CommandExecution(
                status="rolled_back", transition=None, lethal_handling=None,
            )

        with patch.object(runtime, "_write", side_effect=lambda **k: logged.append(k)), patch.object(
            Stage9Runtime, "_dispatch_decision", autospec=True,
            side_effect=dispatch,
        ):
            result = runtime._dispatch_decision(
                proposal=proposal, prepared=prepared, admission=None,
                cycle=1, sent_t_monde=4,
            )
        self.assertEqual(result.status, "rolled_back")
        self.assertEqual(len(forwarded), 1)
        prediction = forwarded[0].predicted_consequences
        self.assertEqual(len(prediction), 1)
        self.assertEqual(prediction[0].variable, "water")
        self.assertEqual(prediction[0].value_or_delta, 62.0)
        self.assertEqual(prediction[0].precision, 0.0)
        self.assertEqual(proposal.plan.steps[0].predicted_consequences, ())
        self.assertEqual(prepared.predicted_consequences, ())
        self.assertEqual(len(logged), 1)
        self.assertEqual(logged[0]["kind"], "stage11_prospective_prediction_frozen")
        self.assertEqual(
            logged[0]["data"]["source_transition_refs"],
            ["physical:transition:1"],
        )
        self.assertFalse(logged[0]["data"]["causal_validation"])

    def test_unavailable_sample_leaves_unpredicted_command_untouched(self):
        runtime = build_stage11_reference_runtime(
            enable_lived_prediction=True,
        )
        proposal = safe_causal_proposal()
        prepared = runtime.stage3.control.prepare_option_step(proposal)
        witness = row(step=3)
        witness["physical_episode_ref"] = None  # No Memory closure.
        runtime._stage11_prospective_state = {
            "lived_causal_actions": [witness],
            "causal_action_witnesses": [],
        }
        runtime._stage11_prospective_capture = (5, (2,2), 50.0)
        forwarded = []
        with patch.object(runtime, "_write", side_effect=AssertionError(
            "missing physical witness must not produce a numeric claim"
        )), patch.object(
            Stage9Runtime, "_dispatch_decision", autospec=True,
            side_effect=lambda _instance, **kwargs: (
                forwarded.append(kwargs["prepared"]),
                CommandExecution("rolled_back", None, None),
            )[1],
        ):
            runtime._dispatch_decision(
                proposal=proposal, prepared=prepared, admission=None,
                cycle=1, sent_t_monde=5,
            )
        self.assertEqual(forwarded[0].predicted_consequences, ())
