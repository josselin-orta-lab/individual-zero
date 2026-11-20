"""Second-source synthetic falsifiers for full E3B funding distribution."""
from copy import deepcopy
import unittest

from tools import stage8e3b_independent_funding_reduction as R


def fixture():
    names=R.CATEGORIES
    counts={names[0]:72,names[1]:24,names[2]:24,names[3]:24}
    arm={"original_lives":144,"lived_steps":144,"first20_observed_steps":144}
    for n in names:
        k=counts[n]
        arm.update({
            "original_count_"+n:k,
            "per_lived_step_"+n:k/144.,
            "early20_per_observed_step_"+n:k/144.,
            "predecision_energy_mean_"+n:20.,
            "predecision_vigilance_mean_"+n:30.,
            "predecision_energy_under10_fraction_"+n:0.,
            "predecision_vigilance_under10_fraction_"+n:0.,
        })
    rows=[{"population":p,"by_arm":{a:deepcopy(arm) for a in R.ARMS}}
          for p in range(64)]
    entries=[]
    for cat in names:
        for prefix in ("per_lived_step","early20_per_observed_step"):
            k=prefix+"_"+cat
            entries.append({
                "metric":k,"population_units":64,
                "arm_means_equal_population_weight":{
                    a:arm[k] for a in R.ARMS},
                "exploratory_did_population_mean":0.,
                "positive_negative_zero_population_counts":[0,0,64],
                "all_64_population_descriptive_did":[0.]*64,
            })
    source={"status":"READONLY_ALL_36864_ORIGINAL_FUNDING_REASONS_IDENTIFIED_POSTHOC",
            "original_stage8e3a_full_sha256":R.E3A_SHA,
            "original_stage8e3a_second_sha256":R.E3A_SECOND_SHA,
            "closed_stage8e2_primary":R.PRIMARY,
            "native_originals_rehashed":36864,
            "originals_body_and_funding_chains_verified":36864,
            "native_lives_generated":0,"exploratory_only":True,
            "four_arms":list(R.ARMS),"per_population_arm":rows,
            "funding_reason_descriptions":entries}
    old={"population_rows":[{
        "population":p,"by_arm":{a:{
            "lived_steps":144,
            "action_physical_inactivity_per_step":.5,
            "early20_action_physical_inactivity_per_step":.5,
        } for a in R.ARMS}} for p in range(64)],
        "exploratory_metric_descriptions":[{"metric":"action_physical_inactivity_per_step",
                                            "mean_exploratory_DID":0.}]}
    return source,old


class IndependentNativeFundingTests(unittest.TestCase):
    def test_all_four_categories_and_all_64_populations(self):
        source,old=fixture()
        r=R.verify(source,old,"0"*64)
        self.assertEqual(r["population_units"],64)
        self.assertEqual(r["native_lives_generated"],0)
        self.assertEqual(r["reconstructed_inactivity_did_from_three_funding_causes"],0.)
        self.assertEqual(len(r["all_eight_funding_and_early_metrics"]),8)

    def test_missing_original_lives_cannot_be_accepted(self):
        source,old=fixture()
        source["per_population_arm"][0]["by_arm"]["S_swap"]["original_lives"]=143
        with self.assertRaises(ValueError):
            R.verify(source,old,"0"*64)

    def test_unexplained_idle_action_is_rejected(self):
        source,old=fixture()
        source["per_population_arm"][0]["by_arm"]["S_swap"]["original_count_NO_FUNDED_SCORE"]=23
        with self.assertRaises(ValueError):
            R.verify(source,old,"0"*64)

    def test_old_e3a_inactivity_cannot_be_redefined(self):
        source,old=fixture()
        old["population_rows"][0]["by_arm"]["S_swap"]["action_physical_inactivity_per_step"]=.49
        with self.assertRaises(ValueError):
            R.verify(source,old,"0"*64)

    def test_single_population_repeated_is_rejected(self):
        source,old=fixture()
        source["per_population_arm"][1]["population"]=0
        with self.assertRaisesRegex(ValueError,"population"):
            R.verify(source,old,"0"*64)

    def test_historical_science_negative_closed(self):
        source,old=fixture()
        source["closed_stage8e2_primary"]="GAMMA_BLOCK_CAUSAL_POSITIVE"
        with self.assertRaises(ValueError):
            R.verify(source,old,"0"*64)

    def test_selected_metric_omission_is_rejected(self):
        source,old=fixture()
        source["funding_reason_descriptions"].pop()
        with self.assertRaisesRegex(ValueError,"metric"):
            R.verify(source,old,"0"*64)


if __name__=="__main__":
    unittest.main()
