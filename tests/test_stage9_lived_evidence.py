"""Stage9 lived DC-05 provenance tests: no fabricated independence."""
import unittest
from i0.modules.causal_model import CausalModel, CausalModelConfig


def model():
    return CausalModel(CausalModelConfig("lived-test-v1",2,2,2,2))


def pair(m, *, t=1, integrity=90.0, ate="berry_b", alternative=False):
    m.record_applied_food_exposure(
        t_monde=t,resource_kind="berry_b",option_ref=f"option:{t}",
        motive_ref="goal:food",integrity_before=100.0,
    )
    m.observe_followup_capture(t_monde=t+1,integrity=integrity)
    return (
        {"event_id":f"c:{t}","kind":"command_experienced",
         "t_monde":t,"primitive":"manger","parameters":{"target":"berry_b"}},
        {"event_id":f"w:{t}","kind":"world_transition_experienced",
         "t_monde":t,"body_after":{"integrity":integrity},
         "effects":{"ate":ate,**({"creature_damage":10} if alternative else {})}},
    )


class LivedEvidenceTests(unittest.TestCase):
    def test_only_closed_episode_with_next_capture_is_credited(self):
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
        self.assertEqual(m.publish(),())
        self.assertEqual(m.get("toxic:berry_b").safety_status,"aucun")

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

    def test_distinct_closed_episodes_required(self):
        m=model()
        for t in (1,3):
            ev=pair(m,t=t)
            self.assertEqual(len(m.ingest_closed_autobiographical_episode(
                episode_ref=f"episode:{t}",
                event_refs=(f"c:{t}",f"w:{t}"),
                autobiographical_events=ev,
            )),1)
            self.assertEqual(m.publish().__len__(),int(t==3))
        self.assertEqual(m.get("toxic:berry_b").safety_status,"etabli_pour_securite")

    def test_lived_episode_generates_observation_not_intervention(self):
        m=model()
        events=pair(m)
        admitted=m.ingest_closed_autobiographical_episode(
            episode_ref="episode:1",event_refs=("c:1","w:1"),
            autobiographical_events=events,
        )
        self.assertEqual(len(admitted),1)
        observed=m.pending_causal_observations()
        self.assertEqual(len(observed),1)
        self.assertTrue(observed[0].cause_present)
        self.assertTrue(observed[0].effect_present)
        self.assertEqual(observed[0].episode_ref,"episode:1")
        self.assertEqual(m.publish_causal_inference(),())
        self.assertEqual(m.get("toxic:berry_b").causal_status,"aucun")
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
