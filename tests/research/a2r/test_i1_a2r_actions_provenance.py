"""Adversarial independent GitHub run metadata gate, no live run/offspring."""
import copy
import unittest
from i1_a2r_actions_provenance import verify_actions_run
from i1_a2r_archive_guard import origin_lock

C="a"*40
T="b"*40
P="c"*64
ID=12345
WF=9876
LOCK=origin_lock(source_commit=C,source_tree=T,preset_sha256=P,run_id=ID)
PATH=".github/workflows/i1-a2r-confirmatory-one-shot.yml"
REPO="josselin-orta-lab/individual-zero"


def records():
    run={"id":ID,"workflow_id":WF,"event":"workflow_dispatch",
        "path":PATH,"head_sha":C,"head_branch":"main",
        "run_attempt":1,"run_number":1,"status":"completed",
        "conclusion":"success","repository":{"full_name":REPO},
        "head_repository":{"full_name":REPO},"head_commit":{"id":C}}
    workflow={"id":WF,"path":PATH,"state":"active"}
    commit={"sha":C,"tree":{"sha":T}}
    listing={"total_count":1,"workflow_runs":[{
        "id":ID,"workflow_id":WF,"event":"workflow_dispatch",
        "head_sha":C,"run_attempt":1}]}
    return dict(lock=copy.deepcopy(LOCK),commit=C,tree=T,preset=P,
                run_id=ID,run=run,workflow=workflow,git_commit=commit,
                dispatch_listing=listing)


class ProvenanceTests(unittest.TestCase):
    def test_exact_live_metadata_is_not_scientific_authorization(self):
        result=verify_actions_run(**records())
        self.assertTrue(result["live_api_metadata_matches_external_lock"])
        self.assertFalse(result["immutable_once_only_guaranteed"])
        self.assertFalse(result["runtime_executed_source_independently_proven"])
        self.assertFalse(result["study_admissible"])

    def test_pending_prebirth(self):
        x=records()
        x["run"]["status"]="in_progress"
        x["run"]["conclusion"]=None
        self.assertEqual(verify_actions_run(**x,phase="before_birth")["phase"],
                         "before_birth")
        with self.assertRaises(ValueError):
            verify_actions_run(**x)

    def test_failures_are_retained_not_hidden(self):
        x=records()
        x["run"]["conclusion"]="failure"
        self.assertEqual(verify_actions_run(**x)["actions_conclusion"],"failure")

    def test_anti_relaunch_and_other_dispatches(self):
        for field,value in (("run_attempt",2),("id",ID+1),
                            ("event","pull_request"),("head_sha","f"*40),
                            ("head_branch","other"),("path","bad")):
            x=records()
            x["run"][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify_actions_run(**x)
        x=records()
        x["dispatch_listing"]["total_count"]=2
        with self.assertRaises(ValueError):
            verify_actions_run(**x)

    def test_forged_git_tree_or_workflow(self):
        for k in ("git_commit","workflow"):
            x=records()
            if k=="git_commit":
                x[k]["tree"]["sha"]="f"*40
            else:
                x[k]["state"]="disabled_manually"
            with self.subTest(k=k),self.assertRaises(ValueError):
                verify_actions_run(**x)

    def test_forked_run_and_false_source_lock(self):
        x=records()
        x["run"]["head_repository"]["full_name"]="other/repo"
        with self.assertRaises(ValueError):
            verify_actions_run(**x)
        x=records()
        x["lock"]["source_tree"]="f"*40
        with self.assertRaises(ValueError):
            verify_actions_run(**x)

    def test_no_boolean_or_partial_record_acceptance(self):
        x=records()
        x["run"]["run_attempt"]=True
        with self.assertRaises(ValueError):
            verify_actions_run(**x)
        x=records()
        x["dispatch_listing"]["workflow_runs"]=[]
        with self.assertRaises(ValueError):
            verify_actions_run(**x)

if __name__=="__main__":
    unittest.main()
