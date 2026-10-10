"""Stage-9 read-only causal test targets; no invented motivational scores.

EN MVP v1.2.1 §§8.2, 13.1-13.4, 14, P-35/P-48, INV-01/03/25/33.
The tests use controlled typed evidence to exercise the interface, not a
claim that autonomous lived intervention evidence production is complete.
"""
from __future__ import annotations

import unittest

from i0.modules.causal_lifecycle import (
    CausalObservation, CausalHypothesisReview,
)
from i0.modules.causal_model import CausalModel, CausalModelConfig


REF = "causal:hydration"


def model(*, actions=(("hydration_effect", "water", "boire"),)):
    return CausalModel(CausalModelConfig(
        version="stage9-test-target-v1", n1=2, n2=2, n_sec=2, m_sec=2,
        causal_predicates=("hydration_effect",),
        safe_test_actions=actions,
    ))


def hypothesis(m):
    for num, present, effect in (
        (1, True, True), (2, True, True),
        (3, False, False), (4, False, False),
    ):
        m.integrate_causal_observation(CausalObservation(
            identifier=f"observation:{num}", contingency_ref=REF,
            predicate="hydration_effect", subject_ref="water",
            application_context="water_source",
            observation_context="water_source", episode_ref=f"episode:{num}",
            observation_ref=f"world:{num}", observed_step=num,
            cause_present=present, effect_present=effect,
            controlled_variables=(("environment", "source"),),
        ))
    assert [c.after for c in m.publish_causal_inference()] == [
        "correlation_observee"
    ]
    m.integrate_hypothesis_review(CausalHypothesisReview(
        identifier="review:water", contingency_ref=REF,
        alternatives=("no_drink",),
        contrasting_pairs=(("observation:1", "observation:3"),),
    ))
    assert [c.after for c in m.publish_causal_inference()] == [
        "hypothese_causale"
    ]


class CausalTestTargetsTests(unittest.TestCase):
    def test_requires_published_hypothesis_and_explicit_action(self):
        m = model()
        self.assertEqual(m.proposer_test(), ())
        hypothesis(m)
        (target,) = m.proposer_test()
        self.assertEqual(target.contingency_ref, REF)
        self.assertEqual(target.primitive, "boire")
        self.assertEqual(target.subject_ref, "water")
        self.assertEqual(target.motive_ref, f"test_causal:{REF}")
        self.assertEqual(target.contingency_version, m.get(REF).version)
        self.assertEqual(m.proposer_test(), (target,))
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])

    def test_empty_protocol_proposes_nothing(self):
        m = model(actions=())
        hypothesis(m)
        self.assertEqual(m.proposer_test(), ())

    def test_unsafe_or_duplicate_registry_is_rejected(self):
        for actions in (
            (("hydration_effect", "water", "manger"),),
            (("hydration_effect", "berry_b", "boire"),),
            (("toxic_item", "water", "boire"),),
            (("hydration_effect", "water", "boire"),) * 2,
        ):
            with self.subTest(actions=actions):
                with self.assertRaises(ValueError):
                    model(actions=actions)

    def test_snapshot_cannot_reinterpret_actions_and_query_is_pure(self):
        m = model()
        hypothesis(m)
        original = m.export_causal_state()
        self.assertEqual(len(m.proposer_test()), 1)
        self.assertEqual(m.export_causal_state(), original)
        twin = model()
        twin.restore_causal_state(original)
        self.assertEqual(m.proposer_test(), twin.proposer_test())
        incompatible = model(actions=())
        before = incompatible.export_causal_state()
        with self.assertRaises(ValueError):
            incompatible.restore_causal_state(original)
        self.assertEqual(incompatible.export_causal_state(), before)


if __name__ == "__main__":
    unittest.main()
