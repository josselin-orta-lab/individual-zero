import copy
import unittest
from i1_a2r_environment_review import verify_protected_review, ENVIRONMENT

def fixture():
    run={"id":42,"run_attempt":1,"actor":{"login":"initiator"},
         "event":"workflow_dispatch","repository":{"full_name":"josselin-orta-lab/individual-zero"}}
    environment={"name":ENVIRONMENT,"protection_rules":[{"type":"required_reviewers",
        "prevent_self_review":True,"reviewers":[{"type":"User","reviewer":{"login":"independent"}}]}]}
    approvals={"reviewers":[{"state":"approved","run_id":42,"run_attempt":1,
                              "environment":ENVIRONMENT,"reviewer":"independent"}]}
    jobs={"jobs":[{"run_id":42,"run_attempt":1,"environment":ENVIRONMENT}]}
    return dict(run=run,environment=environment,approvals=approvals,jobs=jobs)

class Tests(unittest.TestCase):
    def test_valid_snapshot_not_launch_authorization(self):
        got=verify_protected_review(**fixture())
        self.assertTrue(got["snapshot_independent_approval_verified"])
        self.assertFalse(got["launch_authorized"])
        self.assertFalse(got["external_immutable_approval_attested"])
    def test_forgery_and_self_approval(self):
        for target,key,value in (
            ("run","run_attempt",2),("run","event","pull_request"),
            ("environment","name","other"),
            ("approvals","reviewers",[]),
            ("jobs","jobs",[]),
        ):
            x=fixture();x[target][key]=value
            with self.subTest(target=target,key=key),self.assertRaises(ValueError):
                verify_protected_review(**x)
        x=fixture()
        x["environment"]["protection_rules"][0]["prevent_self_review"]=False
        with self.assertRaises(ValueError):verify_protected_review(**x)
        x=fixture();x["approvals"]["reviewers"][0]["reviewer"]="initiator"
        with self.assertRaises(ValueError):verify_protected_review(**x)
        x=fixture();x["approvals"]["reviewers"][0]["run_id"]=99
        with self.assertRaises(ValueError):verify_protected_review(**x)

if __name__=="__main__":unittest.main()
