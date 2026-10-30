"""Read-only A2-R deployment-environment observation from GitHub Actions.

This probe is deliberately NOT part of a confirmatory run. It reports only
current public GitHub environment policy metadata and never authorizes birth,
configuration changes, scientific evidence or retrospective approval.
"""
from __future__ import annotations

import json
import os

from i1_a2r_actions_provenance import _fetch_github_json, REPOSITORY
from i1_a2r_environment_review import ENVIRONMENT

SCOPE = "A2R_REAL_ENVIRONMENT_READONLY_OBSERVATION_NOT_ATTESTED_NOT_L3"
ENDPOINT = "/repos/" + REPOSITORY + "/environments/" + ENVIRONMENT


def classify_environment_snapshot(environment):
    """Inspect GET /environments/{name}, no run IDs or implied approval."""
    if type(environment) is not dict or environment.get("name") != ENVIRONMENT:
        raise ValueError("wrong GitHub environment response")
    rules = environment.get("protection_rules")
    if type(rules) is not list:
        raise ValueError("environment protection rules absent from response")
    required = [r for r in rules
                if type(r) is dict and r.get("type") == "required_reviewers"]
    unique_rule = len(required) == 1
    rule = required[0] if unique_rule else {}
    people = rule.get("reviewers")
    # A team may be a valid GitHub reviewer but cannot attest a specifically
    # independent named human in this preregistered scientific protocol.
    valid_users = (type(people) is list and len(people) > 0
                   and all(type(p) is dict and p.get("type") == "User"
                           and type(p.get("reviewer")) is dict
                           and type(p["reviewer"].get("login")) is str
                           and bool(p["reviewer"]["login"]) for p in people))
    no_bypass = environment.get("can_admins_bypass") is False
    no_self_review = unique_rule and rule.get("prevent_self_review") is True
    review_rule_valid = bool(unique_rule and valid_users and no_bypass
                             and no_self_review)
    policy = environment.get("deployment_branch_policy")
    branch_policy_present = (type(policy) is dict
                             and (policy.get("protected_branches") is True
                                  or policy.get("custom_branch_policies") is True))
    return {
        "scope": SCOPE,
        "repository": REPOSITORY,
        "environment": ENVIRONMENT,
        "observation": ("REVIEW_RULE_OBSERVED" if review_rule_valid
                        else "REVIEW_POLICY_INSUFFICIENT"),
        "unique_required_review_rule": unique_rule,
        "individual_reviewers_present": bool(valid_users),
        "prevent_self_review_true": bool(no_self_review),
        "admin_bypass_disabled": no_bypass,
        "deployment_branch_policy_present": branch_policy_present,
        "deployment_restricted_to_main_independently_verified": False,
        "real_approving_person_independently_verified": False,
        "external_immutable_approval_attested": False,
        "birth_authorized": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }


def observe_live_environment(*, api_get=None, token=None):
    """Use explicitly supplied read-only token without leaking it in reports.

    A missing or unauthorized token must remain API_UNVERIFIABLE. The token
    does not prove a protected review, an external lock or a launch permit.
    """
    get = (api_get if api_get is not None else
           lambda endpoint: _fetch_github_json(endpoint, token=token))
    try:
        response = get(ENDPOINT)
        return classify_environment_snapshot(response)
    except (ValueError, OSError) as exc:
        # No error detail or credentials in CI logs: 403, 404 and transport
        # errors all mean *unverifiable*, not proven absent.
        return {
            "scope": SCOPE,
            "repository": REPOSITORY,
            "environment": ENVIRONMENT,
            "observation": "API_UNVERIFIABLE",
            "reason": type(exc).__name__,
            "real_environment_configuration_verified": False,
            "external_immutable_approval_attested": False,
            "birth_authorized": False,
            "study_admissible": False,
            "general_L3": "NOT_ESTABLISHED",
        }


def main():
    print("I1_A2R_ENVIRONMENT_OBSERVATION=" + json.dumps(
        observe_live_environment(token=os.environ.get("GITHUB_TOKEN")),
        sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
