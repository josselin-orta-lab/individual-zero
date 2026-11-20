"""Pure independent Stage8-E3C arithmetical tamper controls, zero new lives."""
import copy
import unittest
from tools import stage8e3c_first_energy_gate_timecourse as C
from tools import stage8e3c_independent_first_gate_reduction as R


def tiny():
    trace=[]
    for t in range(1,26):
        failed=t>=24
        trace.append({
            "t":t,"action":None if failed else ("dormir" if t%3==0 else "attendre"),
            "info":{"funding":"NO_PROCESSING_BUDGET" if failed else "FUNDED"},
            "funding_phases":{
                "decision":{"body_before":[.05 if failed else 25.,80.,70.,100.,90.],
                            "accounting":{"energy":{"paid":0 if failed else .2},
                                          "vigilance":{"paid":0 if failed else .3}}},
                "learning":{"accounting":{"energy":{"paid":0 if failed else .1},
                                          "vigilance":{"paid":0 if failed else .15}}}
            },
            "body":[.04 if failed else 24.,79.,69.,99.,90.],
        })
    return {"trace":trace,"steps_lived":25,"terminal":"dead"}


def synthetic_full():
    one=C.per_life(tiny())
    g=C.blank()
    for _ in range(144):
        C.combine(g,one)
    e3b={"lived_steps":g["lived_steps"],"original_lives":144}
    for r in C.REASONS:
        e3b["original_count_"+r]=g["reasons"][r]
        e3b["early20_per_observed_step_"+r] = (
            g["windows"]["t001_020"]["reasons"][r]/
            g["windows"]["t001_020"]["observed_steps"])
    e3a={
        "action_"+a+"_per_step":g["actions"][a]/g["lived_steps"] for a in C.A.ACTIONS
    }
    for action in C.A.ACTIONS:
        e3a["early20_action_"+action+"_per_step"]=(
            g["windows"]["t001_020"]["actions"][action]/
            g["windows"]["t001_020"]["observed_steps"])
    e3a["decision_energy_paid_per_step"]=sum(
        w["decision_energy_paid"] for w in g["windows"].values())/g["lived_steps"]
    e3a["learning_energy_paid_per_step"]=sum(
        w["learning_energy_paid"] for w in g["windows"].values())/g["lived_steps"]
    cell=C.population_arm(g,e3b,e3a)
    return {
        "status":"READONLY_ALL_36864_ORIGINAL_G2_FIRST_ENERGY_GATE_TIME_COURSE_COMPLETE",
        "original_g2_compressed_and_decoded_sha256_rechecked":36864,
        "original_full_trace_and_funding_chains_rechecked":36864,
        "source_stage8e3b_sha256":R.SOURCE_B,
        "source_g2_manifest_sha256":R.G2_MANIFEST,
        "stage8e2_frozen_primary":R.PRIOR,
        "posthoc_only_no_p_values":True,
        "new_native_lives":0,"populations":64,
        "arms":list(R.ARMS),
        "windows":[{"name":n,"first_t":lo,"last_t":hi} for n,lo,hi in R.WINDOWS],
        "population_rows":[{"population":i,"by_arm":{a:cell for a in R.ARMS}}
                           for i in range(64)],
    }


class IndependentFirstGateTests(unittest.TestCase):
    def test_64_population_second_pass_and_zeros(self):
        report=R.check(synthetic_full(),"a"*64)
        self.assertEqual(report["population_units"],64)
        self.assertEqual(report["original_g2_lives_checked_prior_job"],36864)
        self.assertEqual(report["new_native_lives"],0)
        self.assertEqual(report["four_arm_descriptive_interactions"]["first_failure_per_life"]["mean_contrast"],0)
        self.assertEqual(report["by_arm_original_counts"]["S_sham"]["first_failures"],9216)
        self.assertEqual(report["by_arm_original_counts"]["S_sham"]["recovery_lives"],0)

    def test_fake_late_window_population_cost_is_rejected(self):
        f=synthetic_full()
        f["population_rows"][0]["by_arm"]["S_sham"]["windows"]["t021_100"]["decision_energy_paid"]+=1.
        with self.assertRaisesRegex(ValueError,"time-window rate"):
            R.check(f,"b"*64)

    def test_first_failure_after_original_life_rejected(self):
        f=synthetic_full()
        f["population_rows"][0]["by_arm"]["S_sham"]["first_failure_lives"]=0
        with self.assertRaises(ValueError):
            R.check(f,"b"*64)

    def test_no_new_science_or_significance_in_report(self):
        f=synthetic_full()
        f["posthoc_only_no_p_values"]=False
        with self.assertRaisesRegex(ValueError,"foreign"):
            R.check(f,"b"*64)

    def test_zero_exposure_time_window_is_null_not_zero(self):
        f=synthetic_full()
        w=f["population_rows"][0]["by_arm"]["S_sham"]["windows"]["t101_200"]
        self.assertEqual(w["observed_steps"],0)
        self.assertIsNone(w["mean_predecision_energy"])
        self.assertIsNone(w["first_failure_fraction_of_lives_reached_start"])

if __name__=="__main__":
    unittest.main()
