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
        command_ref=f"command:{i}",
        comparator_ref=f"agency-evidence:episode:intervention:{i}:comparison:{i}",
        context_signature=context, emitted_step=i*2,
        observed_step=i*2+1, observed_effect=effect,
        comparator_status="conforming" if effect else "nonconforming",
        attribution="self_compatible" if effect else "uncertain",
        controlled_variables=(("time","day"),), action_applied=True,
    )

def publish_matching_agency(m, row, *, publish=True):
    """Closed DC-09 comparison, with independently versioned P-47 outcomes."""
    status = "conforming" if row.observed_effect else "nonconforming"
    event_ref = "comparison:" + row.identifier.rsplit(":", 1)[-1]
    event = {
        "event_id": event_ref, "kind": "agency_comparison",
        "t_monde": row.observed_step,
        "data": {
            "option_ref": row.command_ref,
            "sent_t_monde": row.emitted_step,
            "observed_t_monde": row.observed_step,
            "status": status,
            "attribution": "self_compatible" if row.observed_effect else "uncertain",
            "effects": [{
                "variable": "integrity", "status": status,
                "predicted": 90.0,
                "observed": 90.0 if row.observed_effect else 80.0,
                "precision": 0.0, "comparator_version": "p47-causal-test-v1",
            }],
        },
    }
    (report,) = m.ingest_closed_agency_comparisons(
        episode_ref=row.episode_ref, event_refs=(event_ref,),
        autobiographical_events=(event,),
    )
    assert report.identifier == row.comparator_ref
    if publish:
        assert m.publish_causal_inference() == ()
    return report


def publish_trial(m, row):
    publish_matching_agency(m, row)
    m.integrate_causal_intervention(row)
    return m.publish_causal_inference()


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
        self.assertEqual(
            [v.after for v in publish_trial(m, trial(10,context="zone1"))],
            ["testee_par_intervention"],
        )
        self.assertEqual(
            [v.after for v in publish_trial(m, trial(11,context="zone2"))],
            ["etablie"],
        )
        self.assertEqual(m.get(REF).safety_status,"aucun")

    def test_multiple_valid_reviews_in_one_publication_promote_only_once(self):
        m = model()
        correlated(m)
        before = m.get(REF)
        self.assertEqual(before.causal_status, "correlation_observee")
        second = CausalHypothesisReview(
            identifier="review:2",
            contingency_ref=REF,
            alternatives=("observed_hunger_control",),
            contrasting_pairs=(("observation:2", "observation:4"),),
        )
        m.integrate_hypothesis_review(review())
        m.integrate_hypothesis_review(second)
        frozen = m.export_causal_state()

        twin = model()
        twin.restore_causal_state(frozen)
        change = m.publish_causal_inference()
        self.assertEqual(change, twin.publish_causal_inference())
        self.assertEqual(len(change), 1)
        self.assertEqual(change[0].before, "correlation_observee")
        self.assertEqual(change[0].after, "hypothese_causale")
        self.assertEqual(change[0].version, before.version + 1)
        self.assertEqual(m.get(REF).version, before.version + 1)
        self.assertEqual(
            m.export_causal_state()["causal_reviews"],
            ["review:1", "review:2"],
        )
        self.assertEqual(m.export_causal_state(), twin.export_causal_state())
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get(REF).version, before.version + 1)

    def test_invalid_second_review_rolls_back_entire_publication(self):
        m = model()
        correlated(m)
        m.integrate_hypothesis_review(review())
        m.integrate_hypothesis_review(CausalHypothesisReview(
            identifier="review:2",
            contingency_ref=REF,
            alternatives=("unobserved_control",),
            contrasting_pairs=(("observation:2", "observation:missing"),),
        ))
        before = m.export_causal_state()
        with self.assertRaisesRegex(ValueError, "matched controls"):
            m.publish_causal_inference()
        self.assertEqual(m.export_causal_state(), before)

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
            publish_trial(m, trial(i,context="zone1"))
        self.assertEqual(m.get(REF).causal_status,"testee_par_intervention")

    def test_revision_does_not_keep_stale_successes(self):
        m=model()
        hypothesized(m)
        for i,c in ((10,"zone1"),(11,"zone2")):
            publish_trial(m, trial(i,context=c))
        self.assertEqual(m.get(REF).causal_status,"etablie")
        self.assertEqual(
            [x.after for x in publish_trial(m, trial(12,context="zone3",effect=False))],
            ["hypothese_causale"],
        )
        publish_trial(m, trial(13,context="zone1"))
        self.assertEqual(m.get(REF).causal_status,"testee_par_intervention")
        publish_trial(m, trial(14,context="zone2"))
        self.assertEqual(m.get(REF).causal_status,"etablie")

    def test_unlinked_typed_intervention_cannot_advance_canonical_status(self):
        m = model()
        hypothesized(m)
        m.integrate_causal_intervention(trial(10, context="zone1"))
        before = m.export_causal_state()
        with self.assertRaisesRegex(ValueError, "published DC-09 agency comparison"):
            m.publish_causal_inference()
        self.assertEqual(m.export_causal_state(), before)
        self.assertEqual(m.get(REF).causal_status, "hypothese_causale")
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])

    def test_same_batch_pending_comparison_is_not_yet_published(self):
        m = model()
        hypothesized(m)
        row = trial(10, context="zone1")
        publish_matching_agency(m, row, publish=False)
        m.integrate_causal_intervention(row)
        before = m.export_causal_state()
        with self.assertRaisesRegex(ValueError, "published DC-09 agency comparison"):
            m.publish_causal_inference()
        self.assertEqual(m.export_causal_state(), before)

    def test_published_comparison_must_match_all_trial_lineage(self):
        mismatches = (
            {"comparator_ref": "agency-evidence:missing"},
            {"episode_ref": "episode:unrelated"},
            {"command_ref": "command:unrelated"},
            {"emitted_step": 19},
            {"observed_step": 22},
            {"observed_effect": False, "comparator_status": "nonconforming",
             "attribution": "uncertain"},
        )
        for fields in mismatches:
            with self.subTest(fields=fields):
                m = model()
                hypothesized(m)
                row = trial(10, context="zone1")
                publish_matching_agency(m, row)
                m.integrate_causal_intervention(replace(row, **fields))
                before = m.export_causal_state()
                with self.assertRaisesRegex(ValueError, "published DC-09 agency comparison"):
                    m.publish_causal_inference()
                self.assertEqual(m.export_causal_state(), before)
                self.assertEqual(m.get(REF).causal_status, "hypothese_causale")
        # A negative observation cannot claim another comparator attribution.
        m = model()
        hypothesized(m)
        negative = trial(10, context="zone1", effect=False)
        publish_matching_agency(m, negative)
        m.integrate_causal_intervention(replace(negative, attribution="self_compatible"))
        with self.assertRaisesRegex(ValueError, "published DC-09 agency comparison"):
            m.publish_causal_inference()

    def test_distinct_physical_interventions_in_one_memory_episode_meet_n2_later(self):
        m = model()
        hypothesized(m)
        first = trial(10, context="zone1")
        # Several DC-09 comparisons may be placed in one closed Memory
        # episode, without the same physical transition being reused.
        second = replace(
            trial(11, context="zone2"),
            episode_ref=first.episode_ref,
            comparator_ref=f"agency-evidence:{first.episode_ref}:comparison:11",
        )
        publish_matching_agency(m, first)
        publish_matching_agency(m, second)
        m.integrate_causal_intervention(first)
        m.integrate_causal_intervention(second)
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["testee_par_intervention"],
        )
        snapshot = m.export_causal_state()
        self.assertEqual(len(snapshot["causal_interventions"]), 2)
        self.assertEqual(
            len([v for v in snapshot["causal_credits"] if v[2] == "intervention"]),
            2,
        )
        twin = model()
        twin.restore_causal_state(snapshot)
        self.assertEqual(snapshot, twin.export_causal_state())
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["etablie"],
        )
        self.assertEqual(
            [v.after for v in twin.publish_causal_inference()],
            ["etablie"],
        )
        self.assertEqual(m.export_causal_state(), twin.export_causal_state())
        self.assertEqual(m.publish_causal_inference(), ())

    def test_reused_comparison_or_world_step_is_not_a_second_context(self):
        for mode in ("same_comparator", "same_step"):
            with self.subTest(mode=mode):
                m = model()
                hypothesized(m)
                first = trial(10, context="zone1")
                publish_matching_agency(m, first)
                if mode == "same_comparator":
                    # Different alias and invented transition/context cannot
                    # turn one agency comparison into two experiments.
                    second = replace(
                        first, identifier="intervention:reused",
                        observation_ref="world:invented",
                        context_signature="zone2",
                    )
                else:
                    second = replace(
                        trial(11, context="zone2"),
                        emitted_step=first.emitted_step,
                        observed_step=first.observed_step,
                    )
                    publish_matching_agency(m, second)
                m.integrate_causal_intervention(first)
                m.integrate_causal_intervention(second)
                self.assertEqual(
                    [v.after for v in m.publish_causal_inference()],
                    ["testee_par_intervention"],
                )
                state = m.export_causal_state()
                self.assertEqual(len(state["causal_interventions"]), 1)
                self.assertEqual(m.publish_causal_inference(), ())
                self.assertEqual(
                    m.get(REF).causal_status, "testee_par_intervention",
                )

    def test_failed_intervention_blocks_stale_n2_establishment(self):
        m = model()
        hypothesized(m)
        rows = (
            trial(10, context="zone1"), trial(11, context="zone2"),
        )
        failed = trial(12, context="zone3", effect=False)
        # Publish all comparator reports BEFORE the staged interventions:
        # preparation cannot accidentally finalize n2 at the next phase 5.
        for row in (*rows, failed):
            publish_matching_agency(m, row)
        for row in rows:
            m.integrate_causal_intervention(row)
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["testee_par_intervention"],
        )
        m.integrate_causal_intervention(failed)
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(
            m.get(REF).causal_status, "testee_par_intervention",
        )
        # Fresh independent contexts after the negative observation may
        # establish the claim; pre-refutation positives cannot do so.
        publish_trial(m, trial(13, context="zone1"))
        self.assertEqual(
            m.get(REF).causal_status, "testee_par_intervention",
        )
        self.assertEqual(
            [v.after for v in publish_trial(m, trial(14, context="zone2"))],
            ["etablie"],
        )

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
