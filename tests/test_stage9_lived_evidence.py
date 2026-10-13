"""Stage9 lived DC-05 provenance tests: no fabricated independence."""
import unittest
from i0.modules.causal_model import CausalModel, CausalModelConfig


def model():
    return CausalModel(CausalModelConfig("lived-test-v1",2,2,2,2))


def pair(m, *, t=1, integrity=90.0, ate="berry_b", alternative=False,
         verified_control=True, position=(2, 2)):
    # One independently performed, closed and physically matched wait precedes
    # the food event. Keep historical event IDs keyed by fixture case 't'.
    # For control-negative tests, omit the actual waiting evidence entirely.
    food_step = 2 * t
    if verified_control:
        m.record_applied_ambient_integrity_control(
            t_monde=food_step-1, option_ref=f"wait-option:{t}",
            position=position, integrity_before=100.0,
        )
        m.observe_followup_capture(t_monde=food_step, integrity=100.0)
        wait = (
            {"event_id":f"wait-c:{t}", "kind":"command_experienced",
             "t_monde":food_step-1, "primitive":"attendre", "parameters":{}},
            {"event_id":f"wait-w:{t}", "kind":"world_transition_experienced",
             "t_monde":food_step-1,
             "position_after":{"x":position[0],"y":position[1]},
             "body_after":{"integrity":100.0},
             "effects":{"rest":"attendre"}},
        )
        assert m.ingest_closed_autobiographical_episode(
            episode_ref=f"episode:wait:{t}",
            event_refs=(f"wait-c:{t}",f"wait-w:{t}"),
            autobiographical_events=wait,
        ) == ()
    m.record_applied_food_exposure(
        t_monde=food_step, resource_kind="berry_b", option_ref=f"option:{t}",
        motive_ref="goal:food", integrity_before=100.0,
        position_before=position, body_before={
            "energy":50.0,"food":60.0,"water":50.0,"integrity":100.0,
        },
    )
    m.observe_followup_capture(t_monde=food_step+1,integrity=integrity)
    return (
        {"event_id":f"c:{t}","kind":"command_experienced",
         "t_monde":food_step,"primitive":"manger",
         "parameters":{"target":"berry_b"}},
        {"event_id":f"w:{t}","kind":"world_transition_experienced",
         "t_monde":food_step,"body_after":{"integrity":integrity},
         "position_after":{"x":position[0],"y":position[1]},
         "effects":{"ate":ate,**({"creature_damage":10} if alternative else {})}},
    )


class LivedEvidenceTests(unittest.TestCase):
    def test_only_closed_episode_with_next_capture_is_withheld_as_ambiguous(self):
        m=model()
        events=pair(m)
        self.assertEqual(m.export_causal_state()["pending"],[])
        evidence=m.ingest_closed_autobiographical_episode(
            episode_ref="episode:1",event_refs=("c:1","w:1"),
            autobiographical_events=events,
        )
        self.assertEqual(len(evidence),1)
        self.assertTrue(evidence[0].harm_observed)
        self.assertEqual(evidence[0].source,"monde")
        self.assertEqual(
            evidence[0].epistemic_status, "ambiguous_food_association",
        )
        self.assertEqual(m.pending_causal_observations(), ())
        self.assertEqual(m.export_causal_state()["pending_numeric_witnesses"], [])
        self.assertEqual(m.publish(),())
        self.assertIsNone(m.get("toxic:berry_b"))

    def test_harm_without_lived_clean_control_never_credits_safety(self):
        m = model()
        events = pair(m, verified_control=False)
        before = m.export_causal_state()
        self.assertEqual(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:confounded",
            event_refs=("c:1","w:1"),
            autobiographical_events=events,
        ), ())
        self.assertEqual(m.pending_causal_observations(), ())
        self.assertEqual(m.export_causal_state()["pending_numeric_witnesses"], [])
        self.assertEqual(m.publish(), ())
        self.assertIsNone(m.get("toxic:berry_b"))
        self.assertNotEqual(before, m.export_causal_state())

    def test_harmful_wait_does_not_become_a_clean_control(self):
        m = model()
        m.record_applied_ambient_integrity_control(
            t_monde=1, option_ref="wait:1", position=(2,2),
            integrity_before=100.0,
        )
        m.observe_followup_capture(t_monde=2, integrity=90.0)
        wait = (
            {"event_id":"wait-c:1","kind":"command_experienced",
             "t_monde":1,"primitive":"attendre","parameters":{}},
            {"event_id":"wait-w:1","kind":"world_transition_experienced",
             "t_monde":1,"position_after":{"x":2,"y":2},
             "body_after":{"integrity":90.0},"effects":{"rest":"attendre"}},
        )
        self.assertEqual(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:wait:1",event_refs=("wait-c:1","wait-w:1"),
            autobiographical_events=wait,
        ), ())
        m.record_applied_food_exposure(
            t_monde=2, resource_kind="berry_a", option_ref="food:2",
            motive_ref="goal:food", integrity_before=90.0,
            position_before=(2,2),
            body_before={"energy":50.0,"food":60.0,
                         "water":50.0,"integrity":90.0},
        )
        m.observe_followup_capture(t_monde=3, integrity=80.0)
        food = (
            {"event_id":"food-c:2","kind":"command_experienced",
             "t_monde":2,"primitive":"manger","parameters":{"target":"berry_a"}},
            {"event_id":"food-w:2","kind":"world_transition_experienced",
             "t_monde":2,"body_after":{"integrity":80.0},
             "position_after":{"x":2,"y":2},
             "effects":{"ate":"berry_a"}},
        )
        self.assertEqual(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:food:2",event_refs=("food-c:2","food-w:2"),
            autobiographical_events=food,
        ), ())
        self.assertEqual(m.publish(), ())
        self.assertIsNone(m.get("toxic:berry_a"))
        self.assertEqual(m.export_causal_state()["pending_numeric_witnesses"], [])

    def test_invalid_combined_episode_does_not_partially_verify_control(self):
        from i0.modules.causal_model import SafetyEvidence
        m = model()

        # Use a no-harm meal because harmful food outcomes are deliberately
        # ambiguous under issue #89 and never enter the DC-05 credit ledger.
        # A colliding admissible no-harm row still exercises the same late
        # atomic preflight without weakening the epistemic boundary.
        m.record_applied_ambient_integrity_control(
            t_monde=3, option_ref="option:wait", position=(2,2),
            integrity_before=100.0,
        )
        m.observe_followup_capture(t_monde=4, integrity=100.0)
        m.record_applied_food_exposure(
            t_monde=4, resource_kind="berry_b", option_ref="option:food",
            motive_ref="goal:food", integrity_before=100.0,
            position_before=(2,2),
            body_before={"energy":50.0,"food":60.0,
                         "water":50.0,"integrity":100.0},
        )
        m.observe_followup_capture(t_monde=5, integrity=100.0)
        m.integrate(SafetyEvidence(
            identifier="dc05:episode:combined:food-w",
            contingency_ref="toxic:berry_b", predicate="toxic_item",
            subject_ref="berry_b", context_signature="global",
            episode_ref="episode:combined", observation_ref="food-w",
            emission_step=4, observation_step=5, harm_observed=False,
            source="monde", independent_episode=True,
            comparable_context=True, alternative_cause_sufficient=False,
            exposure_motivated_independently=True,
        ))
        events = (
            {"event_id":"wait-c","kind":"command_experienced",
             "t_monde":3,"primitive":"attendre","parameters":{}},
            {"event_id":"wait-w","kind":"world_transition_experienced",
             "t_monde":3,"position_after":{"x":2,"y":2},
             "body_after":{"integrity":100.0},"effects":{"rest":"attendre"}},
            {"event_id":"food-c","kind":"command_experienced",
             "t_monde":4,"primitive":"manger",
             "parameters":{"target":"berry_b"}},
            {"event_id":"food-w","kind":"world_transition_experienced",
             "t_monde":4,"position_after":{"x":2,"y":2},
             "body_after":{"integrity":100.0},"effects":{"ate":"berry_b"}},
        )
        snapshot = m.export_causal_state()
        with self.assertRaisesRegex(ValueError, "duplicate closed Memory safety evidence"):
            m.ingest_closed_autobiographical_episode(
                episode_ref="episode:combined",
                event_refs=tuple(row["event_id"] for row in events),
                autobiographical_events=events,
            )
        self.assertEqual(m.export_causal_state(), snapshot)
        controls = m.export_causal_state()["lived_ambient_integrity_controls"]
        target = next(row for row in controls if row["t_monde"] == 3)
        self.assertIsNone(target["episode_ref"])

    def test_control_snapshot_roundtrip_and_forged_control_rejected(self):
        m = model()
        pair(m)
        raw = m.export_causal_state()
        twin = model()
        twin.restore_causal_state(raw)
        self.assertEqual(twin.export_causal_state(), raw)
        from copy import deepcopy
        forged = deepcopy(raw)
        forged["lived_ambient_integrity_controls"][0]["integrity_observed"] = 88.0
        with self.assertRaisesRegex(ValueError,"ambient control lacks"):
            twin.restore_causal_state(forged)
        self.assertEqual(twin.export_causal_state(), raw)

    def test_without_matching_effect_or_transition_no_knowledge(self):
        for ate,alt in [("unavailable",False),("berry_b",True)]:
            m=model()
            events=pair(m,ate=ate,alternative=alt)
            self.assertEqual(m.ingest_closed_autobiographical_episode(
                episode_ref="episode:x",event_refs=("c:1","w:1"),
                autobiographical_events=events,
            ),())
            self.assertEqual(m.publish(),())
            self.assertIsNone(m.get("toxic:berry_b"))

    def test_duplicate_autobiographical_projection_id_is_not_last_write_wins(self):
        # A closed episode's event_refs are unique, but a corrupted source
        # view can still supply two payloads under the same referenced ID.
        # Neither arrival order may rescue an otherwise ambiguous attempt.
        for repeated_kind in ("command", "transition"):
            for reverse in (False, True):
                with self.subTest(kind=repeated_kind, reverse=reverse):
                    m = model()
                    command, transition = pair(m)
                    original = command if repeated_kind == "command" else transition
                    altered = dict(original)
                    if repeated_kind == "command":
                        altered["parameters"] = {"target": "berry_a"}
                    else:
                        altered["body_after"] = {"integrity": 75.0}
                    extra = (altered, original) if reverse else (original, altered)
                    source = (
                        (transition, *extra) if repeated_kind == "command"
                        else (command, *extra)
                    )
                    before = m.export_causal_state()
                    with self.assertRaisesRegex(
                        ValueError,
                        "duplicate closed Memory autobiographical event projection",
                    ):
                        m.ingest_closed_autobiographical_episode(
                            episode_ref="episode:ambiguous-projection",
                            event_refs=("c:1", "w:1"),
                            autobiographical_events=source,
                        )
                    self.assertEqual(m.export_causal_state(), before)
                    self.assertEqual(m.pending_causal_observations(), ())
                    self.assertIsNone(m.get("toxic:berry_b"))

        # A different event not named by this episode is not an alternate
        # physical witness and must not poison an otherwise valid ingestion.
        m = model()
        events = pair(m)
        unrelated = {
            **events[0], "event_id": "command:outside-closed-episode",
        }
        self.assertEqual(len(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:valid",
            event_refs=("c:1", "w:1"),
            autobiographical_events=(*events, unrelated),
        )), 1)

    def test_duplicate_closed_event_reference_is_rejected_atomically(self):
        m = model()
        events = pair(m)
        before = m.export_causal_state()
        with self.assertRaisesRegex(
            ValueError, "closed Memory episode reference ledger",
        ):
            m.ingest_closed_autobiographical_episode(
                episode_ref="episode:dup",
                event_refs=("c:1", "c:1", "w:1"),
                autobiographical_events=events,
            )
        self.assertEqual(m.export_causal_state(), before)
        # A valid later projection of the same genuinely closed attempt
        # remains creditable after the invalid input was rejected.
        self.assertEqual(len(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:valid",
            event_refs=("c:1", "w:1"),
            autobiographical_events=events,
        )), 1)

    def test_three_conflicting_events_cannot_resurrect_one_physical_step(self):
        for kind in ("command_experienced", "world_transition_experienced"):
            with self.subTest(kind=kind):
                m = model()
                command, transition = pair(m)
                primary = command if kind == "command_experienced" else transition
                alternatives = tuple(
                    {**primary, "event_id": f"duplicate:{kind}:{index}"}
                    for index in (1, 2)
                )
                events = (command, transition, *alternatives)
                refs = tuple(event["event_id"] for event in events)
                self.assertEqual(
                    m.ingest_closed_autobiographical_episode(
                        episode_ref="episode:ambiguous",
                        event_refs=refs,
                        autobiographical_events=events,
                    ), (),
                )
                snapshot = m.export_causal_state()
                self.assertEqual(snapshot["pending"], [])
                self.assertEqual(snapshot["pending_causal_observations"], [])
                self.assertEqual(snapshot["pending_numeric_witnesses"], [])
                self.assertEqual(snapshot["lived_food_exposures"], [])
                self.assertEqual(m.publish(), ())
                self.assertEqual(m.publish_causal_inference(), ())
                self.assertIsNone(m.get("toxic:berry_b"))
                # The rejected closed attempt cannot be reopened with a
                # different autobiographical label and then promoted.
                self.assertEqual(m.ingest_closed_autobiographical_episode(
                    episode_ref="episode:alias",
                    event_refs=("c:1", "w:1"),
                    autobiographical_events=(command, transition),
                ), ())
                self.assertEqual(m.pending_causal_observations(), ())

    def test_distinct_positions_do_not_manufacture_harmful_food_credit(self):
        m=model()
        statuses=[]
        publications=[]
        for t, position in ((1,(2,2)),(3,(3,2)),(5,(4,2))):
            ev=pair(m,t=t,position=position)
            rows=m.ingest_closed_autobiographical_episode(
                episode_ref=f"episode:{t}",
                event_refs=(f"c:{t}",f"w:{t}"),
                autobiographical_events=ev,
            )
            self.assertEqual(len(rows),1)
            statuses.append(rows[0].epistemic_status)
            publications.append(len(m.publish()))
        self.assertEqual(statuses,[
            "ambiguous_food_association",
            "ambiguous_food_association",
            "ambiguous_food_association",
        ])
        self.assertEqual(publications,[0,0,0])
        self.assertIsNone(m.get("toxic:berry_b"))

    def test_ambiguous_lived_harm_generates_no_causal_observation_or_intervention(self):
        m=model()
        events=pair(m)
        admitted=m.ingest_closed_autobiographical_episode(
            episode_ref="episode:1",event_refs=("c:1","w:1"),
            autobiographical_events=events,
        )
        self.assertEqual(len(admitted),1)
        self.assertEqual(
            admitted[0].epistemic_status, "ambiguous_food_association",
        )
        self.assertEqual(m.pending_causal_observations(), ())
        self.assertEqual(m.publish_causal_inference(),())
        self.assertIsNone(m.get("toxic:berry_b"))
        self.assertEqual(m.export_causal_state()["causal_interventions"],[])

    def test_confounder_rejects_safety_and_causal_observation_together(self):
        m=model()
        events=pair(m,alternative=True)
        self.assertEqual(m.ingest_closed_autobiographical_episode(
            episode_ref="episode:1",event_refs=("c:1","w:1"),
            autobiographical_events=events,
        ),())
        self.assertEqual(m.pending_causal_observations(),())

    def test_preregistered_control_is_other_actually_consumed_food(self):
        cfg=CausalModelConfig("lived-comparison-v1",2,2,2,2,
                              food_control_pairs=(("berry_b","berry_a"),))
        m=CausalModel(cfg)
        m.record_applied_food_exposure(
            t_monde=1,resource_kind="berry_a",
            option_ref="option:1",motive_ref="goal:food",integrity_before=100.0,
        )
        m.observe_followup_capture(t_monde=2,integrity=100.0)
        source=(
            {"event_id":"command:1","kind":"command_experienced",
             "t_monde":1,"primitive":"manger","parameters":{"target":"berry_a"}},
            {"event_id":"transition:1","kind":"world_transition_experienced",
             "t_monde":1,"body_after":{"integrity":100.0},
             "effects":{"ate":"berry_a"}},
        )
        m.ingest_closed_autobiographical_episode(
            episode_ref="episode:real-1",
            event_refs=("command:1","transition:1"),
            autobiographical_events=source,
        )
        observed=m.pending_causal_observations()
        self.assertEqual(len(observed),2)
        control=next(o for o in observed if not o.cause_present)
        self.assertEqual(control.contingency_ref,"toxic:berry_b")
        self.assertEqual(control.episode_ref,"episode:real-1")
        self.assertEqual(control.observation_ref,"transition:1")
        self.assertFalse(control.effect_present)
        self.assertEqual(m.publish_causal_inference(),())
        published=m.export_causal_state()["causal_observations"]
        self.assertEqual(len(published),2)
        self.assertEqual(len({v["episode_ref"] for v in published}),1)
        self.assertEqual(m.get("toxic:berry_b").causal_status,"aucun")

    def test_control_requires_explicit_registry(self):
        with self.assertRaises(ValueError):
            CausalModelConfig("bad-v1",2,2,2,2,
                food_control_pairs=(("berry_b","berry_b"),)).validate()
        self.assertEqual(model().config.food_control_pairs,())

    def test_ambiguous_food_association_adds_no_snapshot_credit_state(self):
        m=model()
        events=pair(m,position=(2,2))
        row=m.ingest_closed_autobiographical_episode(
            episode_ref="episode:ambiguous",
            event_refs=("c:1","w:1"),
            autobiographical_events=events,
        )[0]
        self.assertEqual(row.epistemic_status,"ambiguous_food_association")
        raw=m.export_causal_state()
        self.assertNotIn("ambiguous_food_harm_contexts",raw)
        self.assertEqual(raw["pending"],[])
        self.assertEqual(raw["admitted_safety_evidence"],[])
        clone=model()
        clone.restore_causal_state(raw)
        self.assertEqual(clone.export_causal_state(),raw)
        self.assertIsNone(clone.get("toxic:berry_b"))

    def test_snapshot_restores_unfinished_exposure(self):
        m=model()
        m.record_applied_food_exposure(t_monde=1,resource_kind="berry_a",
            option_ref="o",motive_ref="g",integrity_before=100)
        raw=m.export_causal_state()
        clone=model()
        clone.restore_causal_state(raw)
        self.assertEqual(raw,clone.export_causal_state())


if __name__=="__main__":
    unittest.main()
