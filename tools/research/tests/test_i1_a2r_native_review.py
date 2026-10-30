import copy
import unittest
from i1_a2r_native_review import verify_native_review, audit_live_native_review
from i1_a2r_environment_review import ENVIRONMENT

def data():
    run={"id":42,"run_attempt":1,"event":"workflow_dispatch","actor":{"login":"initiator"},
         "repository":{"full_name":"josselin-orta-lab/individual-zero"}}
    env={"name":ENVIRONMENT,"can_admins_bypass":False,"protection_rules":[
        {"type":"required_reviewers","prevent_self_review":True,"reviewers":[
            {"type":"User","reviewer":{"login":"reviewer"}}]}]}
    history=[{"state":"approved","user":{"login":"reviewer"},"environments":[{"name":ENVIRONMENT}]}]
    return run,env,history

class Tests(unittest.TestCase):
    def test_native_snapshot_still_not_authority(self):
        r,e,h=data();v=verify_native_review(run=r,environment=e,history=h)
        self.assertFalse(v["launch_authorized"])
    def test_missing_policy_or_forged_history(self):
        for case in range(7):
            r,e,h=copy.deepcopy(data())
            if case==0:del e["protection_rules"][0]["prevent_self_review"]
            if case==1:e["can_admins_bypass"]=True
            if case==2:h[0]["user"]["login"]="initiator"
            if case==3:h[0]["environments"]=[]
            if case==4:h.append(copy.deepcopy(h[0]))
            if case==5:r["run_attempt"]=2
            if case==6:e["protection_rules"]=[]
            with self.subTest(case=case),self.assertRaises(ValueError):
                verify_native_review(run=r,environment=e,history=h)
    def test_endpoint_shapes(self):
        r,e,h=data();requests=[]
        def fetch(path,expected_type=dict):
            requests.append((path,expected_type))
            if path.endswith("/approvals"):return h
            if "/environments/" in path:return e
            return r
        v=audit_live_native_review(run_id=42,api_get=fetch)
        self.assertFalse(v["durable_external_approval_proven"])
        self.assertEqual(requests[-1][1],list)

if __name__=="__main__":unittest.main()
