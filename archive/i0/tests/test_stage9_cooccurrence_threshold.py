"""Stage-9 P-35: n1 is a count of true co-occurrences, not exposures.

INV-03/25: no correlation can be promoted by a single effect plus repeated
harmless exposures, especially when available controls are non-comparable.
"""
import unittest

from i0.modules.causal_model import CausalModel, CausalModelConfig
from i0.modules.causal_lifecycle import CausalObservation


def model():
    return CausalModel(CausalModelConfig(
        version="stage9-n1-cooccurrence-v1",
        n1=2, n2=2, n_sec=2, m_sec=2,
        causal_predicates=("food_energy_effect",),
    ))


def observed(n, *, cause=True, effect=True, location="site-a"):
    return CausalObservation(
        identifier=f"obs:{n}", contingency_ref="food:energy",
        predicate="food_energy_effect", subject_ref="food",
        application_context="food-context", observation_context=location,
        episode_ref=f"episode:{n}", observation_ref=f"physical:{n}",
        observed_step=n, cause_present=cause, effect_present=effect,
        controlled_variables=(("site", location),),
    )


class CooccurrenceGateTests(unittest.TestCase):
    def test_n1_really_counts_exposed_effect_cooccurrences(self):
        m = model()
        for row in (observed(1), observed(2,effect=False),
                    observed(3,cause=False,effect=False)):
            m.integrate_causal_observation(row)
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get("food:energy").causal_status, "aucun")
        m.integrate_causal_observation(observed(4))
        self.assertEqual(
            [x.after for x in m.publish_causal_inference()],
            ["correlation_observee"],
        )

    def test_unmatched_cooccurrences_cannot_meet_threshold(self):
        m = model()
        for row in (observed(1,location="site-a"),
                    observed(2,location="site-b"),
                    observed(3,cause=False,effect=False,location="site-a")):
            m.integrate_causal_observation(row)
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get("food:energy").causal_status, "aucun")

    def test_pending_observation_replay_is_deterministic(self):
        left = model()
        for row in (observed(1),observed(2,effect=False),
                    observed(3,cause=False,effect=False)):
            left.integrate_causal_observation(row)
        snap = left.export_causal_state()
        right = model()
        right.restore_causal_state(snap)
        self.assertEqual(snap,right.export_causal_state())
        self.assertEqual(left.publish_causal_inference(),right.publish_causal_inference())
        self.assertEqual(left.export_causal_state(),right.export_causal_state())


if __name__ == "__main__":
    unittest.main()
