"""Candidate-F shadow cost control: software only, no live policy."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.candidate_f_cost_control import (
    SCHEMA, paid_candidate_f_shadow_then_reference_choice)
from i3.modules.genome import midpoint
from i3.modules.genomic_omega_frontier_information_mind import (
    GenomicOmegaFrontierInformationMind)
from i3.modules.mind import Mind

BODY = (80., 80., 80., 80., 80.)


def capture(body=BODY):
    return {
        "body": tuple(body),
        "here": (False, ()),
        "neighbors": (None, None, None, None),
        "inventory": (),
    }


def pair(seed=17):
    genome = midpoint()
    return (
        Mind(genome, seed, observer_decision_diagnostics=True),
        GenomicOmegaFrontierInformationMind(
            genome, seed, observer_decision_diagnostics=True),
    )


def add(a, b):
    return CognitiveWork(
        cycles=a.cycles + b.cycles,
        simulated_steps=a.simulated_steps + b.simulated_steps,
        memory_items=a.memory_items + b.memory_items,
        replays=a.replays + b.replays,
    )


class CandidateFCostControlTests(unittest.TestCase):
    def test_result_is_exact_reference_choice_from_post_shadow_body(self):
        expected_ref, expected_candidate = pair()
        cb = CognitiveBudget(BODY, BodyLaws())
        _ca, _cp, candidate_work, _ci = expected_candidate.decide(
            capture(), cb)
        self.assertEqual(candidate_work, cb.work)
        post_shadow = tuple(cb.remaining)

        rb = CognitiveBudget(post_shadow, BodyLaws())
        post_capture = capture(post_shadow)
        expected = expected_ref.decide(post_capture, rb)

        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())
        actual = paid_candidate_f_shadow_then_reference_choice(
            reference, candidate, capture(), outer)

        self.assertEqual(actual[:2], expected[:2])
        self.assertEqual(actual[3]["option"], expected[3]["option"])
        self.assertEqual(actual[2], add(candidate_work, expected[2]))
        self.assertEqual(actual[2], outer.work)
        for actual_body, sequential_body in zip(outer.remaining, rb.remaining):
            self.assertAlmostEqual(actual_body, sequential_body, places=12)
        self.assertLessEqual(
            actual[3]["cost_control"]["sequential_settlement_max_abs_gap"],
            1e-12)

    def test_shadow_action_has_no_motor_authority(self):
        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())

        def fake_candidate(_cap, budget):
            budget.spend(CognitiveWork(cycles=1, memory_items=1))
            return (
                "boire", None, budget.work,
                {"option": "shadow-forced-water", "funding": "FUNDED"})

        with patch.object(candidate, "decide", side_effect=fake_candidate):
            action, _param, work, info = (
                paid_candidate_f_shadow_then_reference_choice(
                    reference, candidate, capture(), outer))

        self.assertNotEqual(action, "boire")
        self.assertEqual(
            info["cost_control"]["candidate_shadow_action"], "boire")
        self.assertFalse(
            info["cost_control"]["candidate_motor_authority"])
        self.assertEqual(
            info["cost_control"]["motor_authority"],
            "P1.3_REFERENCE_ONLY")
        self.assertEqual(work, outer.work)

    def test_shadow_work_is_physically_settled_before_reference_choice(self):
        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())
        _action, _param, _work, info = (
            paid_candidate_f_shadow_then_reference_choice(
                reference, candidate, capture(), outer))
        c = info["cost_control"]
        self.assertEqual(c["body_before"], BODY)
        self.assertLess(
            c["body_after_candidate_shadow"][0], BODY[0])
        self.assertLess(
            c["body_after_candidate_shadow"][4], BODY[4])
        self.assertEqual(
            c["body_after_reference_choice"], tuple(outer.remaining))
        self.assertEqual(
            c["settlement_authority"], "CUMULATIVE_V2_PHASE_START_BODY")
        self.assertLessEqual(
            c["sequential_settlement_max_abs_gap"], 1e-12)
        self.assertEqual(
            c["cost_matching_claim"], "UPPER_COST_NOT_EXACT_MATCH")

    def test_total_work_is_exact_sum_of_executed_subcomputations(self):
        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())
        _a, _p, total, info = paid_candidate_f_shadow_then_reference_choice(
            reference, candidate, capture(), outer)
        cc = info["cost_control"]
        cw = CognitiveWork(**cc["candidate_shadow_work"])
        rw = CognitiveWork(**cc["reference_choice_work"])
        self.assertEqual(total, add(cw, rw))
        self.assertEqual(CognitiveWork(**cc["total_work"]), total)

    def test_common_state_mismatch_fails_before_any_work(self):
        reference, candidate = pair()
        candidate.effects.observe(
            ("attendre",), (0., -1., -1., 0., 0.))
        outer = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "first-person state mismatch"):
            paid_candidate_f_shadow_then_reference_choice(
                reference, candidate, capture(), outer)
        self.assertEqual(outer.work, CognitiveWork())

    def test_rng_mismatch_fails_before_any_work(self):
        reference, candidate = pair()
        candidate.rng.random()
        outer = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "perception RNG"):
            paid_candidate_f_shadow_then_reference_choice(
                reference, candidate, capture(), outer)
        self.assertEqual(outer.work, CognitiveWork())

    def test_capture_or_dead_body_failure_is_precomputation(self):
        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaises(ValueError):
            paid_candidate_f_shadow_then_reference_choice(
                reference, candidate, capture((79., 80., 80., 80., 80.)),
                outer)
        self.assertEqual(outer.work, CognitiveWork())

        dead_body = (80., 0., 80., 80., 80.)
        reference, candidate = pair()
        dead = CognitiveBudget(dead_body, BodyLaws())
        with self.assertRaises(ValueError):
            paid_candidate_f_shadow_then_reference_choice(
                reference, candidate, capture(dead_body), dead)
        self.assertEqual(dead.work, CognitiveWork())

    def test_plain_reference_type_is_required(self):
        _reference, candidate = pair()
        wrong_reference = GenomicOmegaFrontierInformationMind(
            midpoint(), 17)
        outer = CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(ValueError, "plain P1.3"):
            paid_candidate_f_shadow_then_reference_choice(
                wrong_reference, candidate, capture(), outer)
        self.assertEqual(outer.work, CognitiveWork())

    def test_control_is_explicitly_not_exact_cost_matching(self):
        reference, candidate = pair()
        outer = CognitiveBudget(BODY, BodyLaws())
        _a, _p, _work, info = paid_candidate_f_shadow_then_reference_choice(
            reference, candidate, capture(), outer)
        self.assertEqual(info["experimental_policy"], SCHEMA)
        self.assertEqual(
            info["cost_control"]["scope"],
            "SOFTWARE_ONE_DECISION_UPPER_COST_NOT_RUNTIME")
        self.assertFalse(info["cost_control"]["world_access"])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.candidate_f_cost_control; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
