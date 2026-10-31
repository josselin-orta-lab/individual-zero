"""Prospective H2 tests: held-out outcomes may never shape the prior forecast."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep,MatchedLivedEpisode,ForecastOpportunity,
    project_matched_outcome,score_heldout_forecast,
)
def step(t,action,delta):
    return ClaimedLivedStep("life:one",t,f"capture:{t}","goal:one",action,
                           f"admit:{t}",f"evidence:{t}",f"outcome:{t}",delta)
def episode(name,t,first,last):
    return MatchedLivedEpisode(name,("context:seen",),
                              (step(t,first,-2),step(t+1,"finish",last)))
class Source:
    def verify_lived(self,*,event):return True
    def verify_complete_episode(self,*,episode):return True
    def verify_forecast_capture(self,*,opportunity):return True
    def verify_issued_forecast(self,*,forecast):return True
class BadIssue(Source):
    def verify_issued_forecast(self,*,forecast):return False
def training():
    return episode("train:prepared",1,"prepare",8),episode("train:control",5,"alternative",1)
def holdout(prepared=7,control=2):
    return episode("test:prepared",12,"prepare",prepared),episode("test:control",16,"alternative",control)
def opportunity():
    return ForecastOpportunity("life:one","goal:one","capture:10",10,
                               ("context:seen",),"prepare","alternative","finish")
class ProspectiveTests(unittest.TestCase):
    def test_genuine_temporal_split_and_nonmotor_score(self):
        f=project_matched_outcome(prepared=training()[0],control=training()[1],
                                  opportunity=opportunity(),source=Source())
        s=score_heldout_forecast(forecast=f,prepared=holdout()[0],
                                 control=holdout()[1],source=Source())
        self.assertEqual((f.predicted_outcome_difference,s.observed_outcome_difference),(7,5))
        self.assertEqual(s.absolute_error,2)
        self.assertTrue(s.direction_agreement)
        self.assertEqual(s.motor_authority,"NONE")
        self.assertFalse(s.m11_authenticated)
    def test_outcome_inversion_does_not_rewrite_issued_forecast(self):
        f=project_matched_outcome(prepared=training()[0],control=training()[1],
                                  opportunity=opportunity(),source=Source())
        negative=score_heldout_forecast(forecast=f,prepared=holdout(-8,4)[0],
                                        control=holdout(-8,4)[1],source=Source())
        self.assertEqual(f.predicted_outcome_difference,7)
        self.assertEqual(negative.observed_outcome_difference,-12)
        self.assertFalse(negative.direction_agreement)
    def test_prediction_requires_only_past_and_claimed_first_person(self):
        a,b=training()
        for bad in (replace(opportunity(),physical_step=6),
                    replace(opportunity(),life_ref="life:foreign"),
                    replace(opportunity(),context_signature=("context:alien",)),
                    replace(opportunity(),capture_ref=a.events[0].capture_ref)):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                project_matched_outcome(prepared=a,control=b,opportunity=bad,source=Source())
    def test_no_reused_or_early_heldout_episodes(self):
        a,b=training()
        f=project_matched_outcome(prepared=a,control=b,
                                  opportunity=opportunity(),source=Source())
        for p,c in ((a,b),(episode("test:prepared",9,"prepare",8),holdout()[1]),
                    (replace(holdout()[0],episode_ref=a.episode_ref),holdout()[1])):
            with self.subTest(p=p),self.assertRaises(ValueError):
                score_heldout_forecast(forecast=f,prepared=p,control=c,source=Source())
    def test_forecast_authentication_and_tampering_fail_closed(self):
        a,b=training()
        f=project_matched_outcome(prepared=a,control=b,
                                  opportunity=opportunity(),source=Source())
        for bad in (replace(f,motor_authority="ADMITTED"),
                    replace(f,m11_authenticated=True),
                    replace(f,last_training_step=10),
                    replace(f,training_episode_refs=("same","same"))):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                score_heldout_forecast(forecast=bad,prepared=holdout()[0],
                                       control=holdout()[1],source=Source())
        with self.assertRaises(ValueError):
            score_heldout_forecast(forecast=f,prepared=holdout()[0],
                                   control=holdout()[1],source=BadIssue())
if __name__=="__main__": unittest.main()
