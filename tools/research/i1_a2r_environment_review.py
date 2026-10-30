"""Read-only GitHub environment/reviewer evidence for A2-R, never launch authority.

Consumes separately retrieved REST objects. A passing result only attests
snapshot consistency, not tamper-proof approval, durable one-shot operation,
or permission to start a life. No network calls or I1 births in this module.
"""
from __future__ import annotations

SCOPE="A2R_ENVIRONMENT_REVIEW_SNAPSHOT_NOT_LAUNCH_AUTHORIZATION"
ENVIRONMENT="i1-a2r-confirmatory"
REPO="josselin-orta-lab/individual-zero"


def verify_protected_review(*, run, environment, approvals, jobs):
    """Require an independent human reviewer on this exact original run."""
    if any(type(x) is not dict for x in (run, environment, approvals, jobs)):
        raise ValueError("missing GitHub provenance objects")
    run_id=run.get("id")
    actor=run.get("actor")
    if (type(run_id) is not int or run_id < 1
            or run.get("run_attempt") != 1
            or type(actor) is not dict
            or type(actor.get("login")) is not str or not actor["login"]
            or run.get("event") != "workflow_dispatch"
            or run.get("repository",{}).get("full_name") != REPO):
        raise ValueError("invalid original run and triggering actor")
    if (environment.get("name") != ENVIRONMENT
            or type(environment.get("protection_rules")) is not list):
        raise ValueError("expected protected confirmatory environment absent")
    review=[r for r in environment["protection_rules"]
            if type(r) is dict and r.get("type") == "required_reviewers"]
    if len(review)!=1:
        raise ValueError("unique required human review not configured")
    rule=review[0]
    if (rule.get("prevent_self_review") is not True
            or type(rule.get("reviewers")) is not list
            or not rule["reviewers"]):
        raise ValueError("self-review allowed or required reviewers absent")
    reviewers={x.get("reviewer",{}).get("login") for x in rule["reviewers"]
               if type(x) is dict and x.get("type")=="User"
               and type(x.get("reviewer")) is dict}
    if not reviewers or None in reviewers or actor["login"] in reviewers:
        raise ValueError("reviewers not independent of run initiator")
    if (type(approvals.get("reviewers")) is not list
            or len(approvals["reviewers"]) != 1):
        raise ValueError("ambiguous or absent environment approval")
    approval=approvals["reviewers"][0]
    if (type(approval) is not dict
            or approval.get("state") != "approved"
            or approval.get("run_id") != run_id
            or approval.get("run_attempt") != 1
            or approval.get("environment") != ENVIRONMENT
            or approval.get("reviewer") not in reviewers
            or approval["reviewer"] == actor["login"]):
        raise ValueError("review not bound to independent exact run")
    if (type(jobs.get("jobs")) is not list or not jobs["jobs"]):
        raise ValueError("no original protected jobs")
    for job in jobs["jobs"]:
        if (type(job) is not dict or job.get("run_id") != run_id
                or job.get("run_attempt") != 1
                or job.get("environment") != ENVIRONMENT):
            raise ValueError("job outside protected original run/environment")
    return {
        "scope":SCOPE, "github_run_id":run_id,
        "environment":ENVIRONMENT,
        "snapshot_required_reviewer_verified":True,
        "snapshot_independent_approval_verified":True,
        "external_immutable_approval_attested":False,
        "launch_authorized":False,
        "study_admissible":False,
        "general_L3":"NOT_ESTABLISHED",
    }
