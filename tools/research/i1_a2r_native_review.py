"""Conservative native GitHub review-history observer. No launch authorization."""
from i1_a2r_actions_provenance import _fetch_github_json, REPOSITORY
from i1_a2r_environment_review import ENVIRONMENT

def verify_native_review(*, run, environment, history):
    if type(run) is not dict or type(environment) is not dict or type(history) is not list:
        raise ValueError("missing native GitHub data")
    actor=run.get("actor")
    if (run.get("event")!="workflow_dispatch" or type(run.get("id")) is not int
            or type(run.get("run_attempt")) is not int or run["run_attempt"]!=1
            or type(actor) is not dict or not actor.get("login")
            or run.get("repository",{}).get("full_name")!=REPOSITORY):
        raise ValueError("wrong original GitHub run")
    if (environment.get("name")!=ENVIRONMENT
            or environment.get("can_admins_bypass") is not False):
        raise ValueError("environment absent or admin bypass possible")
    rules=environment.get("protection_rules")
    if type(rules) is not list:
        raise ValueError("environment rules absent")
    required=[r for r in rules if type(r) is dict and r.get("type")=="required_reviewers"]
    if len(required)!=1:
        raise ValueError("required reviewers missing or ambiguous")
    rule=required[0]
    # Native environment details may omit prevent_self_review. Never
    # manufacture proof that the policy forbids self-review.
    if rule.get("prevent_self_review") is not True:
        raise ValueError("self-review protection not independently attested")
    people=rule.get("reviewers")
    if type(people) is not list or not people:
        raise ValueError("no registered reviewers")
    allowed=set()
    for p in people:
        if type(p) is not dict or p.get("type")!="User" or type(p.get("reviewer")) is not dict:
            raise ValueError("non-individual/ambiguous reviewer")
        login=p["reviewer"].get("login")
        if type(login) is not str or not login:
            raise ValueError("invalid reviewer identity")
        allowed.add(login)
    if actor["login"] in allowed:
        raise ValueError("initiator is designated reviewer")
    if len(history)!=1:
        raise ValueError("review history not unique")
    review=history[0]
    if (type(review) is not dict or review.get("state")!="approved"
            or type(review.get("user")) is not dict
            or review["user"].get("login") not in allowed
            or review["user"]["login"]==actor["login"]
            or type(review.get("environments")) is not list
            or len(review["environments"])!=1
            or review["environments"][0].get("name")!=ENVIRONMENT):
        raise ValueError("native approval not traceable to independent reviewer/environment")
    return {"scope":"A2R_NATIVE_REVIEW_SNAPSHOT_NOT_LAUNCH_AUTHORIZATION",
            "github_run_id":run["id"],
            "snapshot_approval_observed":True,
            "self_review_protection_independently_attested":True,
            "durable_external_approval_proven":False,
            "launch_authorized":False,"study_admissible":False,
            "general_L3":"NOT_ESTABLISHED"}

def audit_live_native_review(*, run_id, token=None, api_get=None):
    if type(run_id) is not int or run_id<=0:
        raise ValueError("invalid run id")
    if api_get is None:
        def api_get(path, expected_type=dict):
            return _fetch_github_json(path,token=token,expected_type=expected_type)
    root="/repos/"+REPOSITORY
    run=api_get(root+"/actions/runs/"+str(run_id))
    environment=api_get(root+"/environments/"+ENVIRONMENT)
    history=api_get(root+"/actions/runs/"+str(run_id)+"/approvals",list)
    return verify_native_review(run=run,environment=environment,history=history)
