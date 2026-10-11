"""Public Stage-11 geographic coverage and adversarial motive spoofing tests."""
from dataclasses import replace
import json
from unittest import TestCase

from i0.contracts import MotiveRef
from i0.interfaces import PrimitiveCommand
from i0.modules.geographic_planning import propose_geographic_frontier
from i0.modules.simulator import state_from_capture
from lab.stage11_geographic_probe import run_public_geographic_coverage
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class PublicCoverageTests(TestCase):
    def test_geographic_exploration_is_measured_not_inferred(self):
        result = run_public_geographic_coverage(steps=8)
        second = run_public_geographic_coverage(steps=8)
        self.assertEqual(result, second)
        self.assertEqual(result.classification,
                         "development_only_not_heldout")
        self.assertIsNone(result.scientific_verdict)
        self.assertFalse(result.heldout)
        self.assertEqual(result.stage9_applied_geographic_moves, 0)
        self.assertGreater(
            result.stage11_distinct_perceived_sites,
            result.stage9_distinct_perceived_sites,
        )
        self.assertEqual(
            result.stage11_confirmed_distinct_visits,
            result.stage11_distinct_perceived_sites,
        )
        self.assertGreaterEqual(result.stage11_applied_north_moves, 1)
        self.assertGreater(result.stage11_applied_geographic_moves, 0)
        self.assertGreaterEqual(result.stage11_autonomous_options_evaluated,
                                result.stage11_applied_geographic_moves)
        self.assertGreaterEqual(result.stage11_frontier_proposals,
                                result.stage11_applied_geographic_moves)
        self.assertGreaterEqual(result.stage11_model_unavailable_frontiers, 0)
        self.assertGreaterEqual(result.stage11_visit_count,
                                result.stage11_confirmed_distinct_visits)
        self.assertNotEqual(result.stage9_journal_sha256,
                            result.stage11_journal_sha256)
        print("stage11_public_geographic_coverage=" + json.dumps(
            result.as_dict(), sort_keys=True, separators=(",", ":"),
        ))

    def test_public_steps_are_bounded(self):
        for bad in (0, 2, 33, True, "8"):
            with self.subTest(steps=bad), self.assertRaises(ValueError):
                run_public_geographic_coverage(steps=bad)


class GeographicProposalIntegrityTests(TestCase):
    def test_forged_plan_cannot_borrow_frontier_interest(self):
        runtime = build_stage11_reference_runtime(enable_geography=True)
        capture = runtime.stage3.open_step()
        target = runtime.exploration.geographic_cibles(capture)[0]
        runtime.exploration.observe_geographic_capture(
            capture, frozen_targets=(target,),
        )
        state = state_from_capture(
            capture=capture, is_night=runtime.world.is_night(capture.t_monde),
        )
        original = propose_geographic_frontier(
            target=target, initial_state=state,
            simulator=runtime.simulator,
            st_version="unit:previous-st",
            t_monde=capture.t_monde, ttl_steps=4,
        )
        self.assertIsNotNone(original)
        evaluator = runtime.stage8_option_evaluator
        self.assertTrue(evaluator._safe_geographic_shape(original, target))
        self.assertIn(original.preliminary_admissibility,
                      (None, "indeterminate"))
        if not original.plan.steps[0].predicted_consequences:
            self.assertEqual(original.preliminary_admissibility, "indeterminate")
        step = original.plan.steps[0]
        forged = (
            replace(original, plan=replace(
                original.plan, steps=(replace(
                    step, command=PrimitiveCommand(
                        "se_deplacer", {"direction": "south"},
                    ),
                ),),
            )),
            replace(original, option=replace(
                original.option, goal_ref="fake:active-goal",
            )),
            replace(original, plan=replace(
                original.plan, steps=(step, step),
            )),
            replace(original, option=replace(
                original.option, provenance="injected_external_source",
            )),
            replace(original, option=replace(
                original.option, motive_ref=MotiveRef(
                    type="cible_exploration", id="frontier:forged",
                ),
            )),
            replace(original, plan=None),
        )
        for suspect in forged:
            with self.subTest(suspect=suspect):
                self.assertFalse(evaluator._safe_geographic_shape(suspect, target))
                outcome = evaluator.evaluate(
                    proposal=suspect, evaluation_state=None,
                    initial_state=None, cycle=1, t_monde=capture.t_monde,
                )
                self.assertEqual(outcome.evaluation.status, "not_evaluated")
                self.assertIsNone(outcome.evidence)
                self.assertIsNone(outcome.evaluation.intrinsic_value)

        # A target becomes obsolete when its destination is physically
        # perceived on a subsequent world step. Reusing the old option
        # must not earn interest in a later deliberation.
        destination = type("NewCapture", (), dict(
            t_monde=capture.t_monde + 1,
            x=target.destination[0],
            y=target.destination[1],
        ))()
        runtime.exploration.geographic.observe_capture(destination)
        old_option = evaluator.evaluate(
            proposal=original, evaluation_state=None,
            initial_state=None, cycle=1, t_monde=destination.t_monde,
        )
        self.assertEqual(old_option.evaluation.status, "not_evaluated")
        self.assertIsNone(old_option.evidence)


if __name__ == "__main__":
    import unittest
    unittest.main()
