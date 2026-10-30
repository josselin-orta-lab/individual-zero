"""Read-only native GitHub Actions review-history inspection. No launch permission.

Fetches GET /actions/runs/{id}/approvals (native list) and GET /environments/
{name} (native object). GitHub nests prevent_self_review in the
required_reviewers protection rule, not at the environment root.
Run metadata still needs the separate frozen source/run lock audit.
A snapshot is not immutable external human attestation.
"""
from __future__ import annotations

from i1_a2r_actions_provenance import REPOSITORY, _fetch_github_json
from i1_a2r_environment_review import ENVIRONMENT

def verify_native_review_history(*, run, environment, history):
    if (type(run) is not dict or type(environment) is not dict
            or type(history) is not list):
        raise ValueError("missing native GitHub review provenance")
    run_id, actor = run.get("id"), run.get("actor")
    if (type(run_id) is not int or run_id < 1
            or type(run.get("run_attempt")) is not int
            or run["run_attempt"] != 1
            or run.get("event") != "workflow_dispatch"
            or type(actor) is not dict or type(actor.get("login")) is not str
            or not actor["login"]
            or type(run.get("repository")) is not dict
            or run["repository"].get("full_name") != REPOSITORY):
        raise ValueError("untrusted triggering run")
    if (environment.get("name") != ENVIRONMENT
            or environment.get("can_admins_bypass") is not False
            or type(environment.get("protection_rules")) is not list):
        raise ValueError("environment review is missing or bypassable")
    rules=[r for r in environment["protection_rules"]
           if type(r) is dict and r.get("type")=="required_reviewers"]
    if (len(rules)!=1 or type(rules[0].get("reviewers")) is not list
            or rules[0].get("prevent_self_review") is not True):
        raise ValueError("native required reviewers and self-review protection required")
    reviewers=set()
    for r in rules[0]["reviewers"]:
        if (type(r) is not dict or r.get("type")!="User"
                or type(r.get("reviewer")) is not dict
                or type(r["reviewer"].get("login")) is not str
                or not r["reviewer"]["login"]):
            raise ValueError("unverifiable human reviewer configuration")
        reviewers.add(r["reviewer"]["login"])
    if not reviewers or actor["login"] in reviewers:
        raise ValueError("no independent required human reviewer")
    if len(history)!=1:
        raise ValueError("run has no unique native approval record")
    approval=history[0]
    if (type(approval) is not dict
            or approval.get("state")!="approved"
            or type(approval.get("user")) is not dict
            or approval["user"].get("login") not in reviewers
            or approval["user"]["login"]==actor["login"]
            or type(approval.get("environments")) is not list
            or len(approval["environments"])!=1
            or type(approval["environments"][0]) is not dict
            or approval["environments"][0].get("name")!=ENVIRONMENT):
        raise ValueError("native history lacks distinct approved environment")
    return {
        "scope":"A2R_NATIVE_REVIEW_HISTORY_SNAPSHOT_NOT_L3",
        "run_id":run_id, "approval_reviewer":approval["user"]["login"],
        "snapshot_consistent":True,
        "api_snapshot_immutable":False,
        "external_approval_attested":False,
        "launch_authorized":False,
        "study_admissible":False,
        "general_L3":"NOT_ESTABLISHED",
    }

def audit_native_live_review(*, run, api_get=None):
    """Independent API read; a private endpoint may return 403, fail closed."""
    if type(run) is not dict or type(run.get("id")) is not int or run["id"]<1:
        raise ValueError("missing run ID")
    base="/repos/"+REPOSITORY
    if api_get is None:
        api_get=lambda path, expect: _fetch_github_json(path, expected_type=expect)
    rid=str(run["id"])
    live_run=api_get(base+"/actions/runs/"+rid,dict)
    environment=api_get(base+"/environments/"+ENVIRONMENT,dict)
    approvals=api_get(base+"/actions/runs/"+rid+"/approvals",list)
    if live_run.get("head_sha")!=run.get("head_sha"):
        raise ValueError("live run differs from separately pinned source")
    return verify_native_review_history(
        run=live_run,environment=environment,history=approvals)
