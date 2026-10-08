"""Stage-9 §13.2 P-35 causal progression, INV-03/25/27/33."""
from __future__ import annotations
import unittest
from dataclasses import replace
from i0.modules.causal_model import CausalModel, CausalModelConfig
from i0.modules.causal_lifecycle import (
    CausalObservation, CausalHypothesisReview, CausalIntervention,
)

REF = "causal:food-energy"
def model():
    return CausalModel(CausalModelConfig(
        version="stage9-inference-tests-v1", n1=2, n2=2, n_sec=2,
        m_sec=2, causal_predicates=("food_energy_effect",),
    ))

def obs(i, *, cause, effect, context="zone1", controls=(("time","day"),)):
    return CausalObservation(
        identifier=f"observation:{i}", contingency_ref=REF,
        predicate="food_energy_effect", subject_ref="food",
        application_context="all_food", observation_context=context,
        episode_ref=f"episode:{i}", observation_ref=f"world:{i}",
        observed_step=i, cause_present=cause, effect_present=effect,
        controlled_variables=controls,
    )

def review():
    return CausalHypothesisReview(
        identifier="review:1", contingency_ref=REF,
        alternatives=("hunger",),
        contrasting_pairs=(("observation:1","observation:3"),),
    )

def trial(i, *, context, effect=True):
    return CausalIntervention(
        identifier=f"intervention:{i}", contingency_ref=REF,
        episode_ref=f"episode:intervention:{i}",
        observation_ref=f"world:intervention:{i}",
        command_ref=f"command:{i}", comparator_ref=f"comparison:{i}",
        context_signature=context, emitted_step=i*2,
        observed_step=i*2+1, observed_effect=effect,
        comparator_status="conforming" if effect else "nonconforming",
        attribution="self_compatible" if effect else "uncertain",
        controlled_variables=(("time","day"),), action_applied=True,
    )

def correlated(m):
    for event in (obs(1,cause=True,effect=True),obs(2,cause=True,effect=True),
                  obs(3,cause=False,effect=False),obs(4,cause=False,effect=False)):
        m.integrate_causal_observation(event)
    changes=m.publish_causal_inference()
    assert [c.after for c in changes]==["correlation_observee"]

def hypothesized(m):
    correlated(m)
    m.integrate_hypothesis_review(review())
    assert [c.after for c in m.publish_causal_inference()]==["hypothese_causale"]

class CausalLifecycleTests(unittest.TestCase):
    def test_four_levels_require_separate_publications(self):
        m=model()
        for o in (obs(1,cause=True,effect=True),obs(2,cause=True,effect=True),
                  obs(3,cause=False,effect=False)):
            m.integrate_causal_observation(o)
        m.integrate_hypothesis_review(review())
        before=m.export_causal_state()
        with self.assertRaises(ValueError):
            m.publish_causal_inference()
        self.assertEqual(before,m.export_causal_state())
        # No partial batch mutation on invalid next-level evidence.
        m= model()
        hypothesized(m)
        m.integrate_causal_intervention(trial(10,context="zone1"))
        self.assertEqual([v.after for v in m.publish_causal_inference()],["testee_par_intervention"])
        m.integrate_causal_intervention(trial(11,context="zone2"))
        self.assertEqual([v.after for v in m.publish_causal_inference()],["etablie"])
        self.assertEqual(m.get(REF).safety_status,"aucun")

    def test_equal_base_rate_or_unmatched_context_never_correlates(self):
        m=model()
        for x in (obs(1,cause=True,effect=True),
                  obs(2,cause=True,effect=False),
                  obs(3,cause=False,effect=True),
                  obs(4,cause=False,effect=False)):
            m.integrate_causal_observation(x)
        self.assertEqual(m.publish_causal_inference(),())
        self.assertEqual(m.get(REF).causal_status,"aucun")
        n=model()
        for x in (obs(1,cause=True,effect=True,context="here"),
                  obs(2,cause=True,effect=True,context="here"),
                  obs(3,cause=False,effect=False,context="elsewhere")):
            n.integrate_causal_observation(x)
        self.assertEqual(n.publish_causal_inference(),())

    def test_same_context_interventions_never_meet_n2(self):
        m=model()
        hypothesized(m)
        for i in (10,11,12):
            m.integrate_causal_intervention(trial(i,context="zone1"))
            m.publish_causal_inference()
        self.assertEqual(m.get(REF).causal_status,"testee_par_intervention")

    def test_revision_does_not_keep_stale_successes(self):
        m=model()
        hypothesized(m)
        for i,c in ((10,"zone1"),(11,"zone2")):
            m.integrate_causal_intervention(trial(i,context=c))
            m.publish_causal_inference()
        self.assertEqual(m.get(REF).causal_status,"etablie")
        m.integrate_causal_intervention(trial(12,context="zone3",effect=False))
        self.assertEqual([x.after for x in m.publish_causal_inference()],["hypothese_causale"])
        m.integrate_causal_intervention(trial(13,context="zone1"))
        m.publish_causal_inference()
        self.assertEqual(m.get(REF).causal_status,"testee_par_intervention")
        m.integrate_causal_intervention(trial(14,context="zone2"))
        m.publish_causal_inference()
        self.assertEqual(m.get(REF).causal_status,"etablie")

    def test_snapshot_replay_pending_and_no_oracle(self):
        m=model()
        correlated(m)
        m.integrate_hypothesis_review(review())
        checkpoint=m.export_causal_state()
        twin=model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(checkpoint,twin.export_causal_state())
        self.assertEqual(m.publish_causal_inference(),twin.publish_causal_inference())
        self.assertEqual(m.export_causal_state(),twin.export_causal_state())
        for invalid in ({"oracle_derived":True},{"rollback_cancelled":True},
                        {"counterfactual":True}):
            old=m.export_causal_state()
            with self.assertRaises(ValueError):
                m.integrate_causal_intervention(replace(trial(10,context="zone1"),**invalid))
            self.assertEqual(old,m.export_causal_state())

if __name__=="__main__":
    unittest.main()
