"""Stage-9 lived causal intervention producer (EN MVP 13.2, P-35, P-47).

The verification path requires an actually applied decision, next Perception
capture, DC-09 closed physical command + transition, and a separately
published AgencyComparator report. A typed claim alone is never evidence.
"""
from __future__ import annotations

import unittest
from copy import deepcopy
from dataclasses import replace

from i0.modules.causal_lifecycle import CausalIntervention
from i0.modules.causal_model import CausalModel
from test_stage9_causal_test_targets import hypothesis, model


def physical_episode(*, step, after, position):
    return (
        {
            "event_id": f"command:{step}",
            "kind": "command_experienced",
            "t_monde": step, "primitive": "boire", "parameters": {},
        },
        {
            "event_id": f"transition:{step}",
            "kind": "world_transition_experienced",
            "t_monde": step, "effects": {"drank": True},
            "body_after": {"water": after},
            "position_after": {"x": position[0], "y": position[1]},
        },
    )


def agency_episode(*, step, option_ref, after, status="conforming"):
    return {
        "event_id": f"agency:{step}",
        "kind": "agency_comparison",
        "t_monde": step + 1,
        "data": {
            "option_ref": option_ref,
            "sent_t_monde": step,
            "observed_t_monde": step + 1,
            "status": status,
            "attribution": (
                "self_compatible" if status == "conforming" else "uncertain"
            ),
            "effects": [{
                "variable": "water", "status": status,
                "predicted": 60.0, "observed": after,
                "precision": 0.0, "comparator_version": "p47-test-v1",
            }],
        },
    }


def evidence_path(
    m: CausalModel, *, step: int, position=(2, 2),
    before=20.0, after=60.0, option_ref=None, close=True,
    comparator=True, compare_status="conforming",
):
    option_ref = option_ref or f"option:drink:{step}"
    (row,) = m.record_applied_causal_action(
        t_monde=step, option_ref=option_ref,
        motive_type="active_goal", motive_ref="goal:drink",
        primitive="boire", current_water_source=True,
        position=position, water_before=before,
    )
    m.observe_causal_action_followup(t_monde=step + 1, water=after)
    if close:
        physical = physical_episode(step=step, after=after, position=position)
        (verified,) = m.ingest_closed_causal_action_episode(
            episode_ref=f"episode:physical:{step}",
            event_refs=tuple(x["event_id"] for x in physical),
            autobiographical_events=physical,
        )
        assert verified.identifier == row.identifier
    if comparator:
        agency = agency_episode(
            step=step, option_ref=option_ref,
            after=after, status=compare_status,
        )
        m.ingest_closed_agency_comparisons(
            episode_ref=f"episode:comparison:{step}",
            event_refs=(agency["event_id"],),
            autobiographical_events=(agency,),
        )
    return row


class LivedCausalInterventionProducerTests(unittest.TestCase):
    def test_full_lived_path_requires_previous_comparator_publication(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        self.assertEqual(m.publish_causal_inference(), ())
        (trial,) = m.promote_lived_causal_interventions()
        self.assertEqual(trial.contingency_ref, "causal:hydration")
        self.assertEqual(trial.observation_ref, "transition:10")
        self.assertEqual(trial.episode_ref, "episode:comparison:10")
        self.assertEqual(trial.comparator_status, "conforming")
        self.assertEqual(trial.context_signature, "water_source:2,2")
        self.assertTrue(trial.observed_effect)
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["testee_par_intervention"],
        )
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 1)

    def test_second_physical_context_needed_for_n2(self):
        m = model()
        hypothesis(m)
        for step, position in ((10, (2, 2)), (20, (2, 2))):
            evidence_path(m, step=step, position=position)
            m.publish_causal_inference()
            m.promote_lived_causal_interventions()
            m.publish_causal_inference()
        self.assertEqual(
            m.get("causal:hydration").causal_status,
            "testee_par_intervention",
        )
        evidence_path(m, step=30, position=(4, 4))
        m.publish_causal_inference()
        m.promote_lived_causal_interventions()
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["etablie"],
        )
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 3)

    def test_no_credit_from_comparator_only_or_open_action(self):
        m = model()
        hypothesis(m)
        comparison = agency_episode(
            step=10, option_ref="option:drink:10", after=60.0,
        )
        m.ingest_closed_agency_comparisons(
            episode_ref="episode:comparison:10",
            event_refs=(comparison["event_id"],),
            autobiographical_events=(comparison,),
        )
        m.publish_causal_inference()
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(m.get("causal:hydration").causal_status, "hypothese_causale")
        # Even an actually recorded decision cannot count without a closed
        # matching physical transition.
        m.record_applied_causal_action(
            t_monde=10, option_ref="option:drink:10",
            motive_type="active_goal", motive_ref="goal:drink",
            primitive="boire", current_water_source=True,
            position=(2, 2), water_before=20.0,
        )
        m.observe_causal_action_followup(t_monde=11, water=60.0)
        self.assertEqual(m.promote_lived_causal_interventions(), ())

    def test_inconsistent_physical_telemetry_prevents_intervention(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10, close=False)
        # A forged body result in a closed event is not the captured value.
        events = physical_episode(step=10, after=45.0, position=(2, 2))
        self.assertEqual(m.ingest_closed_causal_action_episode(
            episode_ref="episode:physical:10",
            event_refs=tuple(v["event_id"] for v in events),
            autobiographical_events=events,
        ), ())
        m.publish_causal_inference()
        self.assertEqual(m.promote_lived_causal_interventions(), ())

    def test_snapshot_preserves_pending_physical_and_comparator_provenance(self):
        left = model()
        hypothesis(left)
        evidence_path(left, step=10)
        original = left.export_causal_state()
        twin = model()
        twin.restore_causal_state(original)
        self.assertEqual(original, twin.export_causal_state())
        self.assertEqual(left.publish_causal_inference(), twin.publish_causal_inference())
        self.assertEqual(
            left.promote_lived_causal_interventions(),
            twin.promote_lived_causal_interventions(),
        )
        self.assertEqual(left.export_causal_state(), twin.export_causal_state())
        self.assertEqual(left.publish_causal_inference(), twin.publish_causal_inference())
        self.assertEqual(left.export_causal_state(), twin.export_causal_state())


    def test_typed_intervention_cannot_borrow_comparator_without_lived_action(self):
        m = model()
        hypothesis(m)
        comparison = agency_episode(
            step=10, option_ref="option:drink:10", after=60.0,
        )
        (report,) = m.ingest_closed_agency_comparisons(
            episode_ref="episode:comparison:10",
            event_refs=(comparison["event_id"],),
            autobiographical_events=(comparison,),
        )
        m.publish_causal_inference()
        m.integrate_causal_intervention(CausalIntervention(
            identifier="intervention:unverified",
            contingency_ref="causal:hydration",
            episode_ref=report.episode_ref,
            observation_ref="transition:unverified",
            command_ref=report.option_ref,
            comparator_ref=report.identifier,
            context_signature="water_source:2,2",
            emitted_step=10, observed_step=11,
            observed_effect=True,
            comparator_status="conforming",
            attribution="self_compatible",
            controlled_variables=(
                ("primitive", "boire"),
                ("water_source", "present"),
                ("site", "2,2"),
            ),
            action_applied=True,
        ))
        snapshot = m.export_causal_state()
        with self.assertRaisesRegex(ValueError, "closed physical action evidence"):
            m.publish_causal_inference()
        self.assertEqual(m.export_causal_state(), snapshot)
        self.assertEqual(
            m.get("causal:hydration").causal_status,
            "hypothese_causale",
        )

    def test_canonical_admission_rejects_tampered_physical_lineage(self):
        mismatches = (
            {"identifier": "intervention:forged"},
            {"observation_ref": "transition:unrelated"},
            {"context_signature": "water_source:99,99"},
            {"controlled_variables": (
                ("primitive", "boire"),
                ("water_source", "present"),
                ("site", "99,99"),
            )},
        )
        for fields in mismatches:
            with self.subTest(fields=fields):
                m = model()
                hypothesis(m)
                evidence_path(m, step=10)
                m.publish_causal_inference()
                (trial,) = m.promote_lived_causal_interventions()
                snapshot = m.export_causal_state()
                self.assertEqual(len(snapshot["causal_action_witnesses"]), 1)
                altered = deepcopy(snapshot)
                altered["pending_causal_interventions"][0].update(fields)
                twin = model()
                twin.restore_causal_state(altered)
                before = twin.export_causal_state()
                with self.assertRaisesRegex(
                    ValueError, "closed physical action evidence",
                ):
                    twin.publish_causal_inference()
                self.assertEqual(twin.export_causal_state(), before)
                self.assertEqual(
                    twin.get("causal:hydration").causal_status,
                    "hypothese_causale",
                )

    def test_closed_physical_witness_replay_and_duplicate_prevention(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        m.publish_causal_inference()
        m.promote_lived_causal_interventions()
        snapshot = m.export_causal_state()
        self.assertEqual(len(snapshot["causal_action_witnesses"]), 1)
        self.assertEqual(snapshot["lived_causal_actions"], [])
        twin = model()
        twin.restore_causal_state(snapshot)
        self.assertEqual(twin.export_causal_state(), snapshot)
        self.assertEqual(m.publish_causal_inference(),
                         twin.publish_causal_inference())
        self.assertEqual(m.export_causal_state(),
                         twin.export_causal_state())
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(twin.promote_lived_causal_interventions(), ())
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(twin.publish_causal_inference(), ())
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 1)

        corrupt = deepcopy(snapshot)
        corrupt["causal_action_witnesses"][0]["transition_event_ref"] = None
        with self.assertRaises(ValueError):
            model().restore_causal_state(corrupt)


    def test_failed_snapshot_restore_is_atomic_even_at_late_validation(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        m.publish_causal_inference()
        m.promote_lived_causal_interventions()
        m.publish_causal_inference()
        baseline = m.export_causal_state()
        self.assertEqual(len(baseline["causal_action_witnesses"]), 1)
        self.assertEqual(len(baseline["agency_evidence"]), 1)
        original_owner = m

        corrupt_witness = deepcopy(baseline)
        # This early, well-typed change would be applied before the late
        # invalid physical witness if restore mutated the live owner.
        corrupt_witness["published"][0]["causal_status"] = "correlation_observee"
        corrupt_witness["causal_action_witnesses"][0][
            "transition_event_ref"
        ] = None

        duplicate_comparison = deepcopy(baseline)
        duplicate_comparison["published"][0][
            "causal_status"
        ] = "correlation_observee"
        duplicate_comparison["pending_agency_evidence"] = deepcopy(
            duplicate_comparison["agency_evidence"]
        )

        config_mismatch = deepcopy(baseline)
        config_mismatch["config_contract"]["n2"] = 99
        for invalid in (
            corrupt_witness, duplicate_comparison, config_mismatch,
        ):
            with self.subTest(fault=list(invalid.keys())):
                with self.assertRaises(ValueError):
                    m.restore_causal_state(invalid)
                self.assertIs(m, original_owner)
                self.assertEqual(m.export_causal_state(), baseline)
                self.assertEqual(
                    m.get("causal:hydration").causal_status,
                    "testee_par_intervention",
                )

        # The original owner is still usable after rejected restore calls.
        m.restore_causal_state(baseline)
        self.assertIs(m, original_owner)
        self.assertEqual(m.export_causal_state(), baseline)

    def test_promoted_applied_action_cannot_be_recorded_a_second_time(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        m.publish_causal_inference()
        m.promote_lived_causal_interventions()
        m.publish_causal_inference()
        baseline = m.export_causal_state()
        self.assertEqual(len(baseline["causal_action_witnesses"]), 1)
        with self.assertRaisesRegex(
            ValueError, "duplicate applied causal action",
        ):
            m.record_applied_causal_action(
                t_monde=10, option_ref="option:drink:10",
                motive_type="active_goal", motive_ref="goal:drink",
                primitive="boire", current_water_source=True,
                position=(2, 2), water_before=20.0,
            )
        self.assertEqual(m.export_causal_state(), baseline)
        self.assertEqual(m.promote_lived_causal_interventions(), ())

    def test_valid_and_reused_interventions_fail_as_one_atomic_batch(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        m.publish_causal_inference()
        (genuine,) = m.promote_lived_causal_interventions()
        m.integrate_causal_intervention(replace(
            genuine,
            identifier="intervention:zz-reused-physical-transition",
            context_signature="water_source:4,4",
        ))
        before = m.export_causal_state()
        with self.assertRaisesRegex(
            ValueError, "closed physical action evidence",
        ):
            m.publish_causal_inference()
        self.assertEqual(m.export_causal_state(), before)
        self.assertEqual(
            m.get("causal:hydration").causal_status, "hypothese_causale",
        )
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])

    def test_unconfigured_model_does_not_record_normal_drinking(self):
        from i0.modules.causal_model import CausalModel, CausalModelConfig
        m = CausalModel(CausalModelConfig("no-preregistered-test-v1", 2, 2, 2, 2))
        self.assertEqual(m.record_applied_causal_action(
            t_monde=10, option_ref="option:drink:10",
            motive_type="active_goal", motive_ref="goal:drink",
            primitive="boire", current_water_source=True,
            position=(2, 2), water_before=20.0,
        ), ())
        self.assertEqual(m.export_causal_state()["lived_causal_actions"], [])

    def test_refutation_uses_real_missing_water_effect(self):
        m = model()
        hypothesis(m)
        for step, position in ((10, (2, 2)), (20, (4, 4))):
            evidence_path(m, step=step, position=position)
            m.publish_causal_inference()
            m.promote_lived_causal_interventions()
            m.publish_causal_inference()
        self.assertEqual(m.get("causal:hydration").causal_status, "etablie")
        evidence_path(
            m, step=30, position=(6, 6), before=20.0,
            after=20.0, compare_status="nonconforming",
        )
        m.publish_causal_inference()
        (missing,) = m.promote_lived_causal_interventions()
        self.assertFalse(missing.observed_effect)
        self.assertEqual(
            [c.after for c in m.publish_causal_inference()],
            ["hypothese_causale"],
        )



class RuntimeLivedInterventionTests(unittest.TestCase):
    def test_real_applied_action_memory_p47_and_causal_publication(self):
        from test_stage9_causal_test_pipeline import configured_runtime

        runtime = configured_runtime()
        hypothesis(runtime.causal_model)
        initial_state = runtime.causal_model.export_causal_state()
        self.assertEqual(
            runtime.causal_model.get("causal:hydration").causal_status,
            "hypothese_causale",
        )
        self.assertEqual(initial_state["lived_causal_actions"], [])

        first = runtime.run_step()
        self.assertEqual(first.execution_status, "applied")
        self.assertEqual(first.command_primitive, "boire")
        # A selected goal action is not yet an intervention. Its evidence is
        # physical and autobiographical, never the predicted effect alone.
        self.assertEqual(
            runtime.causal_model.get("causal:hydration").causal_status,
            "hypothese_causale",
        )
        self.assertEqual(
            runtime.causal_model.export_causal_state()["causal_interventions"],
            [],
        )
        self.assertEqual(
            len(runtime.causal_model.export_causal_state()["lived_causal_actions"]),
            1,
        )

        for _ in range(10):
            runtime.run_step()

        reports = runtime.causal_model.published_agency_evidence()
        interventions = runtime.causal_model.export_causal_state()[
            "causal_interventions"
        ]
        self.assertGreater(len(reports), 0)
        self.assertEqual(len(interventions), 1)
        (trial,) = interventions
        self.assertEqual(trial["contingency_ref"], "causal:hydration")
        self.assertEqual(trial["observed_step"], trial["emitted_step"] + 1)
        self.assertTrue(trial["observed_effect"])
        self.assertIn(trial["comparator_ref"], {
            record.identifier for record in reports
        })
        self.assertIn(trial["observation_ref"], {
            ref for episode in runtime.memory.episodes
            for ref in episode.event_refs
        })
        self.assertEqual(
            runtime.causal_model.get("causal:hydration").causal_status,
            "testee_par_intervention",
        )
        events = [entry.causal_event for entry in runtime.journal.entries]
        self.assertTrue(any(
            event.get("kind") == "causal_applied_action_memory_verified"
            for event in events
        ))
        self.assertTrue(any(
            event.get("kind") == "causal_lived_intervention_staged"
            for event in events
        ))
        self.assertTrue(runtime.journal.verify())

if __name__ == "__main__":
    unittest.main()
