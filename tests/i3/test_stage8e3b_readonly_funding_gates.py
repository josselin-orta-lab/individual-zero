"""Pure synthetic attempts to falsify native Stage8-E3B funding classification.
No World, native individual or original experimental life is instantiated.
"""
import unittest

from tools import stage8e3b_readonly_funding_gates as G


def test_step(category, action, *, option=None, processing_cycles=3, e=50., v=60.):
    return {
        "action":action,"option":option,
        "info":{"funding":category,"option":option},
        "funding_phases":{"decision":{
            "body_before":[e,60.,60.,100.,v],
            "work":{"cycles":processing_cycles,"simulated_steps":0,"memory_items":0,"replays":0}
        }},
    }


def fixture():
    return {
        "trace":[
            test_step("FUNDED","attendre",option="stay"),
            test_step("NO_PROCESSING_BUDGET",None,processing_cycles=0,e=0.),
            test_step("NO_FUNDED_SCORE",None,e=5.),
            test_step("NO_FUNDED_MOTOR",None,e=40.),
        ],
        "actions":{"attendre":1,"physical_inactivity":3}
    }


class FundingGateFalsifiers(unittest.TestCase):
    def test_complete_native_causes_and_no_action_rewrite(self):
        x=G.classify_one(fixture())
        self.assertEqual(x["lives"],1)
        self.assertEqual(x["steps"],4)
        self.assertEqual(x["early_steps"],4)
        self.assertEqual(sum(x["funding"].values()),4)
        for reason in G.CATEGORIES:
            self.assertEqual(x["funding"][reason],1)
        self.assertEqual(x["under10_energy_by_funding"]["NO_PROCESSING_BUDGET"],1)
        self.assertEqual(x["under10_energy_by_funding"]["NO_FUNDED_SCORE"],1)

    def test_physical_none_is_not_chosen_wait(self):
        life=fixture()
        life["trace"][1]["action"]="attendre"
        with self.assertRaisesRegex(ValueError,"null action"):
            G.classify_one(life)

    def test_funded_label_does_not_authorize_empty_motor(self):
        life=fixture()
        life["trace"][0]["action"]=None
        with self.assertRaisesRegex(ValueError,"null action"):
            G.classify_one(life)

    def test_unregistered_native_cause_rejected(self):
        life=fixture()
        life["trace"][1]["info"]["funding"]="DECISION_TIMEOUT"
        with self.assertRaisesRegex(ValueError,"unknown native"):
            G.classify_one(life)

    def test_no_processing_must_not_claim_paid_decision_work(self):
        life=fixture()
        life["trace"][1]["funding_phases"]["decision"]["work"]["cycles"]=1
        with self.assertRaisesRegex(ValueError,"unfunded processing"):
            G.classify_one(life)

    def test_option_tampering_rejected(self):
        life=fixture()
        life["trace"][0]["info"]["option"]="other"
        with self.assertRaisesRegex(ValueError,"decision option"):
            G.classify_one(life)

    def test_per_life_action_counters_are_exact(self):
        life=fixture()
        life["actions"]={"attendre":2,"physical_inactivity":2}
        with self.assertRaisesRegex(ValueError,"conservation"):
            G.classify_one(life)

    def test_population_group_must_match_published_e3a_original(self):
        one=G.classify_one(fixture())
        whole=G._make()
        for _ in range(144):
            G.add(whole,one)
        old={"lived_steps":576,"action_physical_inactivity_per_step":.75,
             "early20_action_physical_inactivity_per_step":.75}
        out=G.summarize_group(whole,old)
        self.assertEqual(out["original_lives"],144)
        self.assertEqual(out["original_count_FUNDED"],144)
        self.assertEqual(out["original_count_NO_FUNDED_MOTOR"],144)
        self.assertAlmostEqual(out["per_lived_step_NO_PROCESSING_BUDGET"],.25)
        old["action_physical_inactivity_per_step"]=.60
        with self.assertRaisesRegex(ValueError,"published Stage8-E3A"):
            G.summarize_group(whole,old)

    def test_first_twenty_observed_steps_not_future_imputed(self):
        life=fixture()
        life["trace"]=life["trace"][:2]
        life["actions"]={"attendre":1,"physical_inactivity":1}
        out=G.classify_one(life)
        self.assertEqual(out["early_steps"],2)
        self.assertEqual(out["early_funding"]["NO_PROCESSING_BUDGET"],1)

if __name__=="__main__":
    unittest.main()
