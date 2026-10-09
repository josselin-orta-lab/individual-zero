"""Stage-9 §13.2 P-35 causal progression, INV-03/25/27/33."""
from __future__ import annotations
import unittest
from dataclasses import replace
from copy import deepcopy
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

    def test_one_step_may_have_distinct_observational_arms(self):
        # Closed physical exposure and its matched no-treatment control
        # can share a time without being equivalent observations.
        m = model()
        treated = obs(1, cause=True, effect=True)
        control = replace(
            obs(3, cause=False, effect=False),
            observed_step=treated.observed_step,
        )
        m.integrate_causal_observation(treated)
        m.integrate_causal_observation(control)
        self.assertEqual(m.publish_causal_inference(), ())
        observations = m.export_causal_state()["causal_observations"]
        self.assertEqual(len(observations), 2)
        self.assertNotEqual(
            observations[0]["cause_present"],
            observations[1]["cause_present"],
        )

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

    def test_same_observation_step_cannot_supply_two_independent_contexts(self):
        # Two different sent commands and comparator IDs using one accessible
        # Perception capture are NOT two independently observed experiments.
        # P-35 n2 must count distinct physical follow-ups, not aliases.
        first = trial(10, context="zone1")
        alias = replace(
            trial(11, context="zone2"),
            emitted_step=first.emitted_step - 1,
            observed_step=first.observed_step,
        )
        self.assertNotEqual(first.emitted_step, alias.emitted_step)
        self.assertNotEqual(first.observation_ref, alias.observation_ref)
        self.assertNotEqual(first.comparator_ref, alias.comparator_ref)

        for separate_publications in (False, True):
            with self.subTest(separate_publications=separate_publications):
                m = model()
                hypothesized(m)
                publish_matching_agency(m, first)
                publish_matching_agency(m, alias)
                m.integrate_causal_intervention(first)
                if separate_publications:
                    self.assertEqual(
                        [v.after for v in m.publish_causal_inference()],
                        ["testee_par_intervention"],
                    )
                m.integrate_causal_intervention(alias)
                before = m.export_causal_state()
                replay = model()
                replay.restore_causal_state(before)
                changes = m.publish_causal_inference()
                self.assertEqual(changes, replay.publish_causal_inference())
                self.assertEqual(
                    [v.after for v in changes],
                    [] if separate_publications else ["testee_par_intervention"],
                )
                self.assertEqual(m.export_causal_state(), replay.export_causal_state())
                state = m.export_causal_state()
                self.assertEqual(len(state["causal_interventions"]), 1)
                self.assertEqual(
                    len([item for item in state["causal_credits"]
                         if item[2] == "intervention"]),
                    1,
                )
                self.assertEqual(m.get(REF).causal_status, "testee_par_intervention")
                self.assertEqual(m.publish_causal_inference(), ())

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

    def test_late_negative_in_same_batch_revokes_newly_established_claim(self):
        # Phase 5 receives observations in world-time order, while holding
        # its publication atomic. An already tested hypothesis must not
        # remain established after a later contradictory lived intervention.
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        self.assertEqual(m.get(REF).causal_status, "testee_par_intervention")

        positive = trial(11, context="zone2")
        negative = trial(12, context="zone3", effect=False)
        # P-47 comparisons must be independently published before the
        # interventions arrive. The interventions themselves stay pending
        # together until the single phase-5 publication being tested.
        for row in (positive, negative):
            publish_matching_agency(m, row)
        for row in (positive, negative):
            m.integrate_causal_intervention(row)
        self.assertEqual(
            len(m.export_causal_state()["pending_causal_interventions"]), 2,
        )

        frozen = m.export_causal_state()
        replay = model()
        replay.restore_causal_state(frozen)
        changes = m.publish_causal_inference()
        self.assertEqual(changes, replay.publish_causal_inference())
        self.assertEqual(changes[-1].after, "hypothese_causale")
        self.assertEqual(m.get(REF).causal_status, "hypothese_causale")
        self.assertEqual(m.export_causal_state(), replay.export_causal_state())
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 3)
        self.assertEqual(m.publish_causal_inference(), ())
        # The last negative invalidates pre-refutation positive contexts.
        publish_trial(m, trial(13, context="zone1"))
        self.assertEqual(m.get(REF).causal_status, "testee_par_intervention")
        publish_trial(m, trial(14, context="zone2"))
        self.assertEqual(m.get(REF).causal_status, "etablie")

    def test_negative_before_positive_in_batch_does_not_reuse_stale_contexts(self):
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        self.assertEqual(m.get(REF).causal_status, "testee_par_intervention")
        earlier_negative = trial(11, context="zone2", effect=False)
        later_positive = trial(12, context="zone3")
        for row in (earlier_negative, later_positive):
            publish_matching_agency(m, row)
        for row in (earlier_negative, later_positive):
            m.integrate_causal_intervention(row)
        self.assertEqual(
            len(m.export_causal_state()["pending_causal_interventions"]), 2,
        )
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get(REF).causal_status, "testee_par_intervention")
        self.assertEqual(m.publish_causal_inference(), ())
        # The old zone1 positive is stale; the later zone3 observation alone
        # cannot satisfy n2, despite being processed in the same batch.
        publish_trial(m, trial(13, context="zone4"))
        self.assertEqual(m.get(REF).causal_status, "etablie")

    def test_snapshot_duplicate_causal_rows_are_rejected_atomically(self):
        # DC-08 / INV-33: restore may not quietly discard two rows carrying
        # one identity, in either a published or pending evidence collection.
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        m.integrate_causal_observation(obs(6, cause=True, effect=True))
        baseline = m.export_causal_state()
        self.assertTrue(baseline["causal_observations"])
        self.assertTrue(baseline["causal_interventions"])
        self.assertTrue(baseline["causal_reviews"])
        self.assertTrue(baseline["causal_credits"])

        corruptions = (
            ("causal_observations", "causal_observations",
             "duplicate causal observation identity"),
            ("causal_interventions", "causal_interventions",
             "duplicate causal intervention identity"),
            ("causal_reviews", "causal_reviews",
             "duplicate causal review identity"),
            ("causal_credits", "causal_credits",
             "duplicate causal evidence credit"),
            ("pending_causal_observations", "causal_observations",
             "duplicate causal observation identity"),
            ("pending_causal_interventions", "causal_interventions",
             "duplicate causal intervention identity"),
        )
        for destination, source, message in corruptions:
            with self.subTest(destination=destination, source=source):
                modified = deepcopy(baseline)
                modified[destination].append(deepcopy(modified[source][0]))
                with self.assertRaisesRegex(ValueError, message):
                    m.restore_causal_state(modified)
                self.assertEqual(m.export_causal_state(), baseline)


    def test_snapshot_credits_match_published_evidence_not_pending_rows(self):
        # §13.2 / DC-08 / INV-33: an independent episode is not a
        # free-standing credit that can be forged or erased by replay.
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        m.integrate_causal_observation(obs(6, cause=True, effect=True))
        m.integrate_causal_intervention(trial(11, context="zone2"))
        baseline = m.export_causal_state()
        self.assertTrue(baseline["pending_causal_observations"])
        self.assertTrue(baseline["pending_causal_interventions"])

        # Pending evidence does not appear in published credits until phase 5.
        credits = {tuple(row) for row in baseline["causal_credits"]}
        self.assertNotIn((REF, "episode:6", "observation"), credits)
        self.assertNotIn(
            (REF, "world:intervention:11", "intervention"), credits,
        )
        twin = model()
        twin.restore_causal_state(baseline)
        self.assertEqual(twin.export_causal_state(), baseline)

        for kind in ("observation", "intervention"):
            for mutation in ("missing", "invented"):
                with self.subTest(kind=kind, mutation=mutation):
                    damaged = deepcopy(baseline)
                    if mutation == "missing":
                        damaged["causal_credits"] = [
                            row for row in damaged["causal_credits"]
                            if row[2] != kind
                        ]
                    else:
                        damaged["causal_credits"].append(
                            [REF, "unwitnessed:synthetic", kind]
                        )
                    with self.assertRaisesRegex(
                        ValueError, "credits mismatch published evidence",
                    ):
                        m.restore_causal_state(damaged)
                    self.assertEqual(m.export_causal_state(), baseline)

        for source, key in (
            ("causal_observations", "episode_ref"),
            ("causal_interventions", "observation_ref"),
        ):
            with self.subTest(source=source):
                damaged = deepcopy(baseline)
                damaged[source][0][key] = "unwitnessed:synthetic"
                with self.assertRaisesRegex(
                    ValueError, "credits mismatch published evidence",
                ):
                    m.restore_causal_state(damaged)
                self.assertEqual(m.export_causal_state(), baseline)

    def test_valid_snapshot_with_pending_and_published_evidence_roundtrips(self):
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        m.integrate_causal_observation(obs(6, cause=True, effect=True))
        m.integrate_causal_intervention(trial(11, context="zone2"))
        checkpoint = m.export_causal_state()
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(twin.export_causal_state(), checkpoint)


    def test_snapshot_revision_boundary_requires_latest_published_failure(self):
        # An erased, stale or fabricated revision would allow pre-failure
        # positives to be counted again after snapshot restoration.
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        publish_trial(m, trial(11, context="zone2"))
        self.assertEqual(m.get(REF).causal_status, "etablie")
        publish_trial(m, trial(12, context="zone3", effect=False))
        publish_trial(m, trial(13, context="zone4", effect=False))
        self.assertEqual(m.get(REF).causal_status, "hypothese_causale")

        pending = trial(14, context="zone5", effect=False)
        publish_matching_agency(m, pending)
        m.integrate_causal_intervention(pending)
        checkpoint = m.export_causal_state()
        self.assertEqual(
            checkpoint["causal_revision_boundaries"],
            [[REF, trial(13, context="zone4").observed_step, "intervention:13"]],
        )
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(twin.export_causal_state(), checkpoint)

        forged = (
            ("missing", []),
            ("stale_valid_failure", [[REF, 25, "intervention:12"]]),
            ("same_failure_wrong_step", [[REF, 99, "intervention:13"]]),
            ("nonexistent_failure", [[REF, 27, "intervention:forged"]]),
            ("positive_as_failure", [[REF, 21, "intervention:10"]]),
            ("wrong_contingency", [["causal:unknown", 27, "intervention:13"]]),
        )
        for label, replacement in forged:
            with self.subTest(label=label):
                damaged = deepcopy(checkpoint)
                damaged["causal_revision_boundaries"] = replacement
                with self.assertRaisesRegex(
                    ValueError, "revision boundary mismatches published counterexample",
                ):
                    m.restore_causal_state(damaged)
                self.assertEqual(m.export_causal_state(), checkpoint)

        # The next pending counterexample can move the boundary only after
        # its own phase-5 publication, and replay must agree exactly.
        self.assertEqual(
            m.publish_causal_inference(), twin.publish_causal_inference(),
        )
        self.assertEqual(
            m.export_causal_state()["causal_revision_boundaries"],
            [[REF, pending.observed_step, pending.identifier]],
        )
        self.assertEqual(m.export_causal_state(), twin.export_causal_state())

    def test_snapshot_cannot_invent_revision_without_negative_intervention(self):
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        checkpoint = m.export_causal_state()
        self.assertEqual(checkpoint["causal_revision_boundaries"], [])
        damaged = deepcopy(checkpoint)
        damaged["causal_revision_boundaries"] = [
            [REF, 21, "intervention:10"],
        ]
        with self.assertRaisesRegex(
            ValueError, "revision boundary mismatches published counterexample",
        ):
            m.restore_causal_state(damaged)
        self.assertEqual(m.export_causal_state(), checkpoint)

    def test_snapshot_published_interventions_keep_agency_lineage(self):
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        m.integrate_causal_intervention(trial(11, context="zone2"))
        checkpoint = m.export_causal_state()
        self.assertEqual(len(checkpoint["causal_interventions"]), 1)
        self.assertGreaterEqual(len(checkpoint["agency_evidence"]), 1)
        self.assertEqual(len(checkpoint["pending_causal_interventions"]), 1)
        replay = model()
        replay.restore_causal_state(checkpoint)
        self.assertEqual(replay.export_causal_state(), checkpoint)

        for kind in (
            "missing_agency", "missing_comparator", "wrong_option",
            "wrong_step", "wrong_episode", "unknown_contingency",
        ):
            with self.subTest(kind=kind):
                damaged = deepcopy(checkpoint)
                published = damaged["causal_interventions"][0]
                if kind == "missing_agency":
                    damaged["agency_evidence"] = []
                elif kind == "missing_comparator":
                    published["comparator_ref"] = "agency-evidence:missing"
                elif kind == "wrong_option":
                    damaged["agency_evidence"][0]["option_ref"] = "command:unrelated"
                elif kind == "wrong_step":
                    damaged["agency_evidence"][0]["observed_t_monde"] += 1
                elif kind == "wrong_episode":
                    published["episode_ref"] = "episode:unrelated"
                elif kind == "unknown_contingency":
                    published["contingency_ref"] = "causal:unknown"
                    damaged["causal_credits"] = [
                        ["causal:unknown", row[1], row[2]]
                        if row[2] == "intervention" else row
                        for row in damaged["causal_credits"]
                    ]
                expected = (
                    "lacks canonical contingency"
                    if kind == "unknown_contingency"
                    else "lacks matching published agency comparison"
                )
                with self.assertRaisesRegex(ValueError, expected):
                    m.restore_causal_state(damaged)
                self.assertEqual(m.export_causal_state(), checkpoint)

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
