"""Candidate-F shadow state custody: software only, no live policy."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from i3.modules.candidate_f_cost_control import (
    paid_candidate_f_shadow_then_reference_choice)
from i3.modules.candidate_f_shadow_state import (
    commit_actual_reference_branch, prepay_actual_reference_branch,
    synchronize_candidate_shadow)
from i3.modules.genome import midpoint
from i3.modules.genomic_omega_frontier_information_mind import (
    GenomicOmegaFrontierInformationMind)
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import STORE_WORK

BODY = (80., 80., 80., 80., 80.)


def cap(body=BODY):
    return {
        "body": tuple(body),
        "here": (False, ()),
        "neighbors": (None, None, None, None),
        "inventory": (),
    }


def pair(seed=17):
    g = midpoint()
    return Mind(g, seed), GenomicOmegaFrontierInformationMind(g, seed)


def add_private_sample(candidate, delta=(0., -.2, -.4, .2, 0.)):
    before = (60., 60., 60., 80., 60.)
    after = tuple(a + b for a, b in zip(before, delta))
    candidate.branch_memory.observe(
        ("attendre", None), before, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))
    candidate.branch_records += 1


class CandidateFShadowStateTests(unittest.TestCase):
    def test_alignment_restores_common_lived_state_and_preserves_private_memory(self):
        reference, candidate = pair()
        add_private_sample(candidate)
        memory_id = id(candidate.branch_memory)
        private_samples = tuple(candidate.branch_memory._samples)
        omega = candidate.first_contact_omega

        candidate.effects.observe(
            ("attendre",), (0., -9., -9., 0., 0.))
        candidate.map[(7, 7)] = (True, ())
        candidate.values[0][0] += 123.
        candidate.acc["fake"] = 4.
        candidate.intention = "fake"
        candidate.rng.random()
        candidate._budget_rng.random()

        receipt = synchronize_candidate_shadow(reference, candidate)

        self.assertEqual(
            receipt["status"], "COMMON_FIRST_PERSON_STATE_ALIGNED")
        self.assertEqual(id(candidate.branch_memory), memory_id)
        self.assertEqual(tuple(candidate.branch_memory._samples), private_samples)
        self.assertEqual(candidate.branch_records, 1)
        self.assertEqual(candidate.first_contact_omega, omega)

        outer = CognitiveBudget(BODY, BodyLaws())
        paid_candidate_f_shadow_then_reference_choice(
            reference, candidate, cap(), outer)
        self.assertGreater(outer.work.cycles, 0)

    def test_alignment_is_deep_not_shared_object_aliasing(self):
        reference, candidate = pair()
        reference.map[(1, 2)] = (False, ())
        reference.effects.observe(
            ("attendre",), (0., -.2, -.4, .2, 0.))
        reference.values[0][0] = 7.
        reference.buffer.append((1., BODY, BODY, False))

        synchronize_candidate_shadow(reference, candidate)

        candidate.map[(1, 2)] = (True, ())
        candidate.effects.observe(
            ("attendre",), (0., -5., -5., 0., 0.))
        candidate.values[0][0] = 99.
        candidate.buffer.clear()

        self.assertEqual(reference.map[(1, 2)], (False, ()))
        self.assertEqual(reference.values[0][0], 7.)
        self.assertEqual(len(reference.buffer), 1)
        self.assertNotEqual(candidate.effects.stats, reference.effects.stats)

    def test_alignment_keeps_reference_rng_authoritative_each_step(self):
        reference, candidate = pair()
        reference.rng.random()
        reference._budget_rng.random()
        synchronize_candidate_shadow(reference, candidate)
        self.assertEqual(reference.rng.getstate(), candidate.rng.getstate())
        self.assertEqual(
            reference._budget_rng.getstate(),
            candidate._budget_rng.getstate())

        candidate.rng.random()
        candidate._budget_rng.random()
        self.assertNotEqual(reference.rng.getstate(), candidate.rng.getstate())
        synchronize_candidate_shadow(reference, candidate)
        self.assertEqual(reference.rng.getstate(), candidate.rng.getstate())
        self.assertEqual(
            reference._budget_rng.getstate(),
            candidate._budget_rng.getstate())

    def test_actual_reference_action_not_shadow_action_is_stored(self):
        reference, candidate = pair()
        before = (70., 70., 70., 80., 70.)
        reference_work = CognitiveWork(cycles=2, memory_items=3)
        funded, _ = debit_cognition(before, BodyLaws(), reference_work)
        physical = list(funded)
        physical[2] += 10.
        physical = tuple(physical)

        reference.last = (before, ("boire",), "boire", None)
        candidate.last = (
            before, ("se_deplacer",), "se_deplacer", "N")
        learning = CognitiveBudget(physical, BodyLaws())
        learning.spend(CognitiveWork(cycles=2))

        pending = prepay_actual_reference_branch(
            reference, candidate,
            {"body": physical, "dead": ()},
            reference_work, learning,
            reference_learning_funded=True)
        self.assertIsNotNone(pending)
        self.assertEqual(pending.key, ("boire", None))
        self.assertEqual(
            learning.work,
            CognitiveWork(cycles=3, memory_items=16))

        self.assertTrue(commit_actual_reference_branch(candidate, pending))
        self.assertEqual(candidate.branch_records, 1)
        sample = candidate.branch_memory._samples[-1]
        self.assertEqual(sample.key, ("boire", None))
        for actual, expected in zip(sample.delta, (0., 0., 10., 0., 0.)):
            self.assertAlmostEqual(actual, expected)

    def test_extra_storage_never_steals_or_rewrites_reference_learning_work(self):
        reference, candidate = pair()
        before = (70., 70., 70., 80., 70.)
        reference.last = (before, ("attendre",), "attendre", None)
        physical = (.01, 70., 70., 80., .04)
        learning = CognitiveBudget(physical, BodyLaws())
        existing = CognitiveWork()
        self.assertEqual(learning.work, existing)

        pending = prepay_actual_reference_branch(
            reference, candidate,
            {"body": physical, "dead": ()},
            CognitiveWork(), learning,
            reference_learning_funded=True)
        self.assertIsNone(pending)
        self.assertEqual(learning.work, existing)
        self.assertEqual(candidate.branch_records, 0)

    def test_no_store_without_reference_learning_or_after_death(self):
        reference, candidate = pair()
        before = (70., 70., 70., 80., 70.)
        reference.last = (before, ("boire",), "boire", None)
        physical = (69., 69., 69., 80., 69.)

        for funded, dead in ((False, ()), (True, ("zero_water",))):
            with self.subTest(funded=funded, dead=dead):
                learning = CognitiveBudget(physical, BodyLaws())
                pending = prepay_actual_reference_branch(
                    reference, candidate,
                    {"body": physical, "dead": dead},
                    CognitiveWork(), learning,
                    reference_learning_funded=funded)
                self.assertIsNone(pending)
                self.assertEqual(learning.work, CognitiveWork())
        self.assertEqual(candidate.branch_records, 0)

    def test_pending_commit_is_exactly_one_prepaid_store(self):
        reference, candidate = pair()
        before = (70., 70., 70., 80., 70.)
        physical = (70., 70., 70., 80., 70.)
        reference.last = (before, ("attendre",), "attendre", None)
        learning = CognitiveBudget(physical, BodyLaws())
        pending = prepay_actual_reference_branch(
            reference, candidate,
            {"body": physical, "dead": ()},
            CognitiveWork(), learning,
            reference_learning_funded=True)
        self.assertEqual(learning.work, STORE_WORK)
        self.assertTrue(commit_actual_reference_branch(candidate, pending))
        self.assertEqual(candidate.branch_records, 1)
        self.assertFalse(commit_actual_reference_branch(candidate, None))
        self.assertEqual(candidate.branch_records, 1)

    def test_inherited_mismatch_fails_without_overwriting_private_state(self):
        reference, candidate = pair()
        add_private_sample(candidate)
        samples = tuple(candidate.branch_memory._samples)
        candidate.theta = tuple(x + 1. for x in candidate.theta)
        with self.assertRaisesRegex(ValueError, "inherited common state"):
            synchronize_candidate_shadow(reference, candidate)
        self.assertEqual(tuple(candidate.branch_memory._samples), samples)
        self.assertEqual(candidate.branch_records, 1)

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.candidate_f_shadow_state; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
