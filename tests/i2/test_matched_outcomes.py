"""Observed matched episodes are descriptive, not interventions or causal proof."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, MatchedLivedEpisode, compare_matched_outcomes,
)
class Source:
    def verify_lived(self, *, event): return True
    def verify_complete_episode(self, *, episode): return True
class Reject(Source):
    def verify_complete_episode(self, *, episode): return False
def event(t, name, val):
    return ClaimedLivedStep("life:one",t,f"capture:{t}","goal:one",
                           name,f"admit:{t}",f"evidence:{t}",
                           None if val is None else f"outcome:{t}",val)
def pair():
    return (
        MatchedLivedEpisode("episode:prepared",("context:observed",),
                           (event(1,"prepare",-2),event(2,"finish",8))),
        MatchedLivedEpisode("episode:control",("context:observed",),
                           (event(5,"alternative",-2),event(6,"finish",1))),
    )
def compare(a,b,source=None):
    return compare_matched_outcomes(
        prepared=a,control=b,preparatory_action_ref="prepare",
        completion_action_ref="finish",source=source or Source())
class MatchedOutcomeTests(unittest.TestCase):
    def test_descriptive_contrast_without_motor_authority(self):
        x=compare(*pair())
        self.assertEqual(x.observed_outcome_difference,7)
        self.assertEqual(x.observed_net_difference,7)
        self.assertEqual(x.alternative_action_ref,"alternative")
        self.assertEqual(x.interpretation,"MATCHED_OBSERVATION_NOT_CAUSAL_IDENTIFICATION")
        self.assertEqual(x.motor_authority,"NONE")
        self.assertFalse(x.m11_authenticated)
    def test_neutral_adverse_and_reversed_effects(self):
        a,b=pair()
        for delta,difference in [(1,0),(-8,-9),(12,11)]:
            changed=replace(a,events=(a.events[0],replace(a.events[-1],lived_delta=delta)))
            self.assertEqual(compare(changed,b).observed_outcome_difference,difference)
    def test_no_credit_when_preparation_not_unique_or_not_observed(self):
        a,b=pair()
        variants=[
            replace(a,events=(replace(a.events[0],action_semantic_ref="alternative"),a.events[1])),
            replace(a,events=(a.events[0],replace(a.events[1],lived_delta=None,outcome_ref=None))),
            replace(a,context_signature=("context:other",)),
            replace(a,events=(a.events[0],replace(a.events[1],action_semantic_ref="other"))),
            replace(a,events=(a.events[0],replace(a.events[1],physical_step=4))),
        ]
        for bad in variants:
            with self.subTest(bad=bad),self.assertRaises(ValueError): compare(bad,b)
    def test_no_replayed_or_overlapping_episodes(self):
        a,b=pair()
        for bad in (
            replace(b,events=(replace(b.events[0],capture_ref=a.events[0].capture_ref),b.events[1])),
            replace(b,events=(replace(b.events[0],physical_step=1),replace(b.events[1],physical_step=2))),
            replace(b,episode_ref=a.episode_ref),
            replace(b,events=(replace(b.events[0],admission_ref=a.events[0].admission_ref),b.events[1])),
        ):
            with self.subTest(bad=bad),self.assertRaises(ValueError): compare(a,bad)
    def test_first_person_claims_are_required(self):
        a,b=pair()
        with self.assertRaises(ValueError): compare(a,b,Reject())
        with self.assertRaises(ValueError):
            compare_matched_outcomes(prepared=a,control=b,
                preparatory_action_ref="prepare",completion_action_ref="finish",source=None)
    def test_incidental_action_does_not_become_causal_identification(self):
        a,b=pair()
        a=replace(a,events=(event(1,"prepare",0),event(2,"incidental",0),event(3,"finish",8)))
        b=replace(b,events=(event(5,"alternative",0),event(6,"incidental",0),event(7,"finish",8)))
        result=compare(a,b)
        self.assertEqual(result.observed_outcome_difference,0)
        self.assertEqual(result.shared_intervening_actions,("incidental",))
        self.assertFalse(result.scheduler_uc_authenticated)
if __name__=="__main__": unittest.main()
