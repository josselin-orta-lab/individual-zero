import unittest
from i1_a2r_environment_probe import classify_environment_snapshot, observe_live_environment
from i1_a2r_environment_review import ENVIRONMENT

def sample():
    return {"name":ENVIRONMENT,"can_admins_bypass":False,
            "deployment_branch_policy":{"protected_branches":True,
                                        "custom_branch_policies":False},
            "protection_rules":[{"type":"required_reviewers",
                                 "prevent_self_review":True,
                                 "reviewers":[{"type":"User","reviewer":{"login":"other"}}]}]}

class Tests(unittest.TestCase):
    def test_valid_policy_still_never_authorizes(self):
        result=classify_environment_snapshot(sample())
        self.assertEqual(result["observation"],"REVIEW_RULE_OBSERVED")
        self.assertFalse(result["birth_authorized"])
        self.assertFalse(result["deployment_restricted_to_main_independently_verified"])
    def test_insufficient_policy(self):
        for name in ("bypass","self","missing","empty"):
            d=sample()
            if name=="bypass":d["can_admins_bypass"]=True
            if name=="self":d["protection_rules"][0]["prevent_self_review"]=False
            if name=="missing":d["protection_rules"]=[]
            if name=="empty":d["protection_rules"][0]["reviewers"]=[]
            with self.subTest(name=name):
                self.assertEqual(classify_environment_snapshot(d)["observation"],
                                 "REVIEW_POLICY_INSUFFICIENT")
    def test_injected_get_does_not_need_token(self):
        seen=[]
        def supplied(endpoint):
            seen.append(endpoint)
            return sample()
        outcome=observe_live_environment(api_get=supplied,token="unused")
        self.assertEqual(outcome["observation"],"REVIEW_RULE_OBSERVED")
        self.assertEqual(len(seen),1)
        self.assertFalse(outcome["birth_authorized"])

    def test_inaccessible_api_is_unknown_not_absent(self):
        def denied(_):raise ValueError("API blocked")
        x=observe_live_environment(api_get=denied)
        self.assertEqual(x["observation"],"API_UNVERIFIABLE")
        self.assertFalse(x["birth_authorized"])

if __name__=="__main__":unittest.main()
