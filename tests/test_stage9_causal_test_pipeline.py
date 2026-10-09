"""Stage 9 proposal to Competition plumbing without premature P-48 motivation."""
from __future__ import annotations

from dataclasses import replace
import unittest

from i0.modules.causal_test_planning import (
    Stage9OptionEvaluator, assess_executable_causal_test,
    propose_executable_causal_test,
)
from i0.modules.causal_model import CausalModelConfig
from i0.modules.simulator import state_from_capture
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage9_runtime import Stage9Runtime
from test_stage9_causal_test_targets import hypothesis


def configured_runtime():
    reference = build_stage9_reference_runtime()
    cfg = replace(
        reference._stage9_config,
        causal=CausalModelConfig(
            version="p35-p36-safe-test-stage9-v1",
            n1=2, n2=2, n_sec=2, m_sec=2,
            causal_predicates=("hydration_effect",),
            safe_test_actions=(("hydration_effect", "water", "boire"),),
        ),
    )
    return Stage9Runtime(
        world_config=reference.world.config,
        layout=reference.world._layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=reference._canonical_safety._innate,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=cfg,
        equipment=reference.equipment,
    )


class CausalTestPipelineTests(unittest.TestCase):
    def test_planning_only_grounded_accessible_water_and_equipment(self):
        runtime = configured_runtime()
        hypothesis(runtime.causal_model)
        (target,) = runtime.causal_model.proposer_test()
        capture = runtime.stage3.perception.capture(
            local_state=runtime.world.capture_local(t_monde=1).as_dict(),
            telemetry=runtime.world.telemetry(),
        )
        initial = state_from_capture(capture=capture, is_night=False)
        proposal = propose_executable_causal_test(
            target=target, initial_state=initial,
            simulator=runtime.simulator,
            st_version="st:test", t_monde=1, ttl_steps=5,
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.option.motive_ref.type, "test_causal")
        self.assertIsNone(proposal.option.goal_ref)
        self.assertEqual(proposal.plan.steps[0].command.primitive, "boire")
        self.assertEqual(proposal.option.learning_signature,
                         "causal_test:boire:water:water_source:observation")
        self.assertEqual(
            propose_executable_causal_test(
                target=target,
                initial_state=replace(initial, current_water_source=False),
                simulator=runtime.simulator, st_version="st:test",
                t_monde=1, ttl_steps=5,
            ), None,
        )
        self.assertEqual(
            propose_executable_causal_test(
                target=target,
                initial_state=replace(initial, body={**initial.body, "water":100.0}),
                simulator=runtime.simulator, st_version="st:test",
                t_monde=1, ttl_steps=5,
            ), None,
        )

    def test_prediction_gap_is_diagnostic_not_a_fabricated_test(self):
        runtime = configured_runtime()
        hypothesis(runtime.causal_model)
        (target,) = runtime.causal_model.proposer_test()
        capture = runtime.stage3.perception.capture(
            local_state=runtime.world.capture_local(t_monde=1).as_dict(),
            telemetry=runtime.world.telemetry(),
        )
        initial = state_from_capture(capture=capture, is_night=False)
        common = dict(
            target=target, simulator=runtime.simulator,
            st_version="st:test", t_monde=1, ttl_steps=5,
        )
        known = assess_executable_causal_test(initial_state=initial, **common)
        self.assertIsNotNone(known.proposal)
        self.assertIsNone(known.reason)
        no_source = assess_executable_causal_test(
            initial_state=replace(initial, current_water_source=False),
            **common,
        )
        self.assertIsNone(no_source.proposal)
        self.assertEqual(no_source.reason, "water_source_not_accessible")
        saturated = assess_executable_causal_test(
            initial_state=replace(initial, body={**initial.body, "water": 100.0}),
            **common,
        )
        self.assertEqual(saturated.reason, "water_saturated")
        unseen = assess_executable_causal_test(
            initial_state=replace(initial, body={**initial.body, "water": 37.25}),
            **common,
        )
        self.assertIsNone(unseen.proposal)
        self.assertEqual(
            unseen.reason, "simulation_unavailable:equipment_input_unseen",
        )
        self.assertIsNone(propose_executable_causal_test(
            initial_state=replace(initial, body={**initial.body, "water": 37.25}),
            **common,
        ))

    def test_causal_option_is_registered_but_intrinsically_unevaluated(self):
        runtime = configured_runtime()
        hypothesis(runtime.causal_model)
        # Phase-1 uses an already published hypothesis, not typed pending rows.
        original = runtime.causal_model.export_causal_state()
        runtime.run_step()
        proposed = [
            entry for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "causal_test_option_proposed"
        ]
        self.assertTrue(proposed)
        registrations = [
            entry for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "causal_test_option_registration"
        ]
        self.assertTrue(any(e.causal_event["data"]["registered"]
                            for e in registrations))
        candidates = [
            row for row in runtime.competition.candidate_proposals
            if row.option.motive_ref.type == "test_causal"
        ]
        self.assertTrue(candidates)
        self.assertTrue(all(row.option.goal_ref is None for row in candidates))
        self.assertTrue(all(
            runtime.competition.accumulator_for(row.option.id) == 0.0
            for row in candidates
        ))
        evaluation = [
            e for e in runtime.journal.entries
            if e.causal_event.get("kind") == "stage8_option_evaluation"
            and e.causal_event["data"]["option_ref"] in {
                row.option.id for row in candidates
            }
        ]
        self.assertTrue(evaluation)
        self.assertTrue(all(
            e.causal_event["data"]["status"] == "not_evaluated"
            and e.causal_event["data"]["evidence"] is None
            for e in evaluation
        ))
        self.assertEqual(runtime.causal_model.export_causal_state()["causal_interventions"], [])
        self.assertEqual(
            runtime.causal_model.export_causal_state()["causal_reviews"],
            original["causal_reviews"],
        )
        self.assertTrue(runtime.journal.verify())

    def test_test_candidates_do_not_change_stage9_unconfigured_reference(self):
        reference = build_stage9_reference_runtime()
        self.assertEqual(reference.causal_model.proposer_test(), ())
        for _ in range(3):
            self.assertEqual(reference.run_step().execution_status, "applied")
        self.assertFalse(any(
            entry.causal_event.get("kind") == "causal_test_option_proposed"
            for entry in reference.journal.entries
        ))


if __name__ == "__main__":
    unittest.main()
