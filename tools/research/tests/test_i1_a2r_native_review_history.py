import copy
import unittest
from i1_a2r_native_review_history import verify_native_review_history, audit_native_live_review
from i1_a2r_environment_review import ENVIRONMENT

def sample():
    run={"id":42,"run_attempt":1,"event":"workflow_dispatch","head_sha":"a"*40,
         "actor":{"login":"initiator"},"repository":{"full_name":"josselin-orta-lab/individual-zero"}}
    env={"name":ENVIRONMENT,"can_admins_bypass":False,"prevent_self_review":True,
         "protection_rules":[{"type":"required_reviewers","reviewers":[
             {"type":"User","reviewer":{"login":"reviewer"}}]}]}
    history=[{"state":"approved","user":{"login":"reviewer"},
              "environments":[{"name":ENVIRONMENT}]}]
    return run,env,history

class NativeApprovalTests(unittest.TestCase):
    def test_good_snapshot_still_not_authorized(self):
        run,env,h=sample()
        r=verify_native_review_history(run=run,environment=env,history=h)
        self.assertFalse(r["launch_authorized"])
        self.assertFalse(r["external_approval_attested"])
    def test_fail_closed_on_native_mutations(self):
        for change in ("bypass","self","missing","duplicate","wrong_reviewer",
                       "wrong_env","wrong_run","not_approved","missing_rule"):
            run,env,h=copy.deepcopy(sample())
            if change=="bypass":env["can_admins_bypass"]=True
            if change=="self":env["prevent_self_review"]=False
            if change=="missing":h=[]
            if change=="duplicate":h.append(copy.deepcopy(h[0]))
            if change=="wrong_reviewer":h[0]["user"]["login"]="initiator"
            if change=="wrong_env":h[0]["environments"][0]["name"]="other"
            if change=="wrong_run":run["run_attempt"]=2
            if change=="not_approved":h[0]["state"]="rejected"
            if change=="missing_rule":env["protection_rules"]=[]
            with self.subTest(change=change),self.assertRaises(ValueError):
                verify_native_review_history(run=run,environment=env,history=h)
    def test_live_collector_uses_exact_endpoints(self):
        run,env,h=sample()
        base="/repos/josselin-orta-lab/individual-zero"
        records={base+"/actions/runs/42":run,
                 base+"/environments/"+ENVIRONMENT:env,
                 base+"/actions/runs/42/approvals":h}
        result=audit_native_live_review(run=run,api_get=lambda path,typ:records[path])
        self.assertTrue(result["snapshot_consistent"])
        bad=copy.deepcopy(run);bad["head_sha"]="b"*40
        with self.assertRaises(ValueError):
            audit_native_live_review(run=bad,api_get=lambda path,typ:records[path])

if __name__=="__main__":unittest.main()
