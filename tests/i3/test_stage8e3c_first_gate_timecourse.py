"""Pure falsifiers: no native life, World or source-replay in Stage8-E3C tests."""
import unittest
from tools import stage8e3c_first_energy_gate_timecourse as C


def synthetic(steps=25, first=24, terminal="dead", recovery=False):
    rows=[]
    for t in range(1,steps+1):
        reason="NO_PROCESSING_BUDGET" if first is not None and t >= first else "FUNDED"
        if recovery and first is not None and t == first+1:
            reason="FUNDED"
        act=("dormir" if t % 3==0 else "attendre") if reason=="FUNDED" else None
        rows.append({
            "t":t,"action":act,"info":{"funding":reason},
            "body":[60.,40.,30.,90.,95.],
            "funding_phases":{
                "decision":{"body_before":[0.05 if reason!="FUNDED" else 10.,40.,30.,90.,95.],
                            "accounting":{"energy":{"paid":.1 if reason=="FUNDED" else 0},
                                          "vigilance":{"paid":.2 if reason=="FUNDED" else 0}}},
                "learning":{"accounting":{"energy":{"paid":.03 if reason=="FUNDED" else 0},
                                          "vigilance":{"paid":.04 if reason=="FUNDED" else 0}}}
            }
        })
    return {"trace":rows,"steps_lived":steps,"terminal":terminal}


class FirstGateOriginalWindowTests(unittest.TestCase):
    def test_fixed_temporal_windows_and_first_event(self):
        got=C.per_life(synthetic())
        self.assertEqual(got["first_failure_lives"],1)
        self.assertEqual(got["first_failure_t_min"],24)
        self.assertEqual(got["windows"]["t001_020"]["observed_steps"],20)
        self.assertEqual(got["windows"]["t001_020"]["first_failures"],0)
        self.assertEqual(got["windows"]["t021_100"]["first_failures"],1)
        self.assertEqual(got["pre10_observed_steps"],10)
        self.assertEqual(got["post_first_failure_funded_action_count"] if "post_first_failure_funded_action_count" in got else got["funded_actions_after_first_failure"],0)
        self.assertEqual(got["windows"]["t101_200"]["observed_steps"],0)

    def test_post_gate_recovery_is_observed_not_assumed(self):
        got=C.per_life(synthetic(first=24,recovery=True))
        self.assertEqual(got["recovery_lives"],1)
        self.assertEqual(got["funded_actions_after_first_failure"],1)

    def test_no_first_failure_is_not_imputed_as_negative_biology(self):
        got=C.per_life(synthetic(steps=14,first=None))
        self.assertEqual(got["never_failure_lives"],1)
        self.assertIsNone(got["first_failure_t_min"])
        self.assertEqual(got["windows"]["t001_020"]["observed_steps"],14)
        self.assertEqual(got["windows"]["t021_100"]["observed_steps"],0)
        w=C._win_values(got["windows"]["t021_100"])
        self.assertIsNone(w["no_processing_per_observed_step"])
        self.assertIsNone(w["first_failure_fraction_of_lives_reached_start"])

    def test_first_gate_on_window_boundary_is_counted_once(self):
        for t,expected in [(20,"t001_020"),(21,"t021_100"),
                           (100,"t021_100"),(101,"t101_200"),
                           (200,"t101_200"),(201,"t201_400"),(400,"t201_400")]:
            with self.subTest(t=t):
                got=C.per_life(synthetic(steps=400,first=t))
                self.assertEqual(sum(w["first_failures"] for w in got["windows"].values()),1)
                self.assertEqual(got["windows"][expected]["first_failures"],1)

    def test_original_life_exposure_stops_at_death(self):
        with self.assertRaisesRegex(ValueError,"time"):
            life=synthetic()
            life["trace"][23]["t"]=26
            C.per_life(life)

    def test_missing_or_foreign_funding_rejected(self):
        life=synthetic()
        life["trace"][1]["info"]["funding"]="IMPOSSIBLE"
        with self.assertRaisesRegex(ValueError,"unknown original"):
            C.per_life(life)

    def test_null_motor_on_funded_step_rejected(self):
        life=synthetic()
        life["trace"][0]["action"]=None
        with self.assertRaisesRegex(ValueError,"motor"):
            C.per_life(life)

    def test_failed_predecisions_do_not_become_a_paid_action(self):
        life=synthetic()
        life["trace"][23]["funding_phases"]["decision"]["body_before"]=[0.02,40,30,90,90]
        o=C.per_life(life)
        self.assertEqual(o["first_failure_energy_sum"],.02)
        self.assertEqual(o["first_failure_t_sum"],24)

    def test_second_population_merge_keeps_first_failure_counts(self):
        group=C.blank()
        C.combine(group,C.per_life(synthetic(first=24)))
        C.combine(group,C.per_life(synthetic(first=None)))
        self.assertEqual(group["lives"],2)
        self.assertEqual(group["first_failure_lives"],1)
        self.assertEqual(group["never_failure_lives"],1)
        self.assertEqual(group["lived_steps"],50)
        self.assertEqual(group["windows"]["t001_020"]["observed_steps"],40)

    def test_early_window_funded_only_fixture(self):
        got=C.per_life(synthetic())
        w=C._win_values(got["windows"]["t001_020"])
        self.assertEqual(w["reasons"]["FUNDED"],20)
        self.assertEqual(w["no_processing_per_observed_step"],0)
        self.assertEqual(w["lives_at_risk_at_start"],1)


if __name__=="__main__":
    unittest.main()
