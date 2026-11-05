#!/usr/bin/env python3
"""#990 offline-prepared single-use GitHub ref claim. NEVER births an I2 life.

This utility is NOT wired to a runnable workflow. The operator must arrange
independent tag-deletion protection, review, and mandatory artifact custody
before making a separately approved one-shot workflow executable.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = "josselin-orta-lab/individual-zero"
WORKFLOW = ".github/workflows/i2-p4-990-manual-study.yml"
WORKFLOW_REF = f"{REPOSITORY}/{WORKFLOW}@refs/heads/main"
CONSUMED_REF = "refs/tags/i2-p4-990-single-use-spent"
CONFIRMATION = "RUN-I2-P4-990-ONCE"
API_URL = "https://api.github.com"
_FULL_SHA = re.compile(r"[0-9a-f]{40}\Z")
_DECIMAL = re.compile(r"[1-9][0-9]*\Z")


class ClaimRefused(ValueError):
    """Fail closed: no native birth may be attempted on this outcome."""


def check_preflight(expected_sha, confirmation, environ):
    """Validate unambiguous first dispatch before using the network."""
    if not isinstance(expected_sha, str) or not _FULL_SHA.fullmatch(expected_sha):
        raise ClaimRefused("full lowercase reviewed Git SHA required")
    if confirmation != CONFIRMATION:
        raise ClaimRefused("exact explicit study confirmation required")
    expected = {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
        "GITHUB_SHA": expected_sha,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_NUMBER": "1",
    }
    for key, value in expected.items():
        if environ.get(key) != value:
            raise ClaimRefused("unapproved workflow dispatch context: " + key)
    run_id = environ.get("GITHUB_RUN_ID", "")
    if not isinstance(run_id, str) or not _DECIMAL.fullmatch(run_id):
        raise ClaimRefused("invalid GitHub run id")
    return run_id


def _json_request(opener, url, token, *, method="GET", body=None):
    payload = None if body is None else json.dumps(body, sort_keys=True).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=payload, headers=headers, method=method)
    try:
        with opener(req, timeout=15) as response:
            status = response.status
            data = json.loads(response.read())
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        # No automatic retry, especially after an ambiguous POST. Retrying
        # an unknown-outcome claim could birth a second scientific cohort.
        raise ClaimRefused("GitHub claim or verification refused") from exc
    if status != (201 if method == "POST" else 200) or not isinstance(data, dict):
        raise ClaimRefused("unexpected GitHub claim response")
    return data



def verify_marker_ruleset(opener, base, token, ruleset_id):
    """Require reviewed active exact-tag delete AND update protection.

    A repository admin can still change rulesets; this is an operational
    precondition, never a cryptographic or externally witnessed guarantee.
    """
    if not isinstance(ruleset_id, str) or not _DECIMAL.fullmatch(ruleset_id):
        raise ClaimRefused("dedicated reviewed tag ruleset id required")
    ruleset = _json_request(opener, base + "/rulesets/" + ruleset_id, token)
    conditions = ruleset.get("conditions") or {}
    names = conditions.get("ref_name") or {}
    types = {item.get("type") for item in ruleset.get("rules", [])
             if isinstance(item, dict)}
    if (ruleset.get("target") != "tag" or
            ruleset.get("source_type") != "Repository" or
            ruleset.get("enforcement") != "active" or
            names.get("include") != [CONSUMED_REF] or
            names.get("exclude") != [] or
            not {"deletion", "update"}.issubset(types) or
            ruleset.get("bypass_actors") != []):
        raise ClaimRefused("tag marker is not protected against update/deletion")
    return True

def claim_once(expected_sha, confirmation, *, environ=None, opener=None,
               api_url=API_URL):
    """Consume one GitHub tag ref atomically before any native birth.

    The remote POST /git/refs must return 201 exactly once. A 422 duplicate,
    timeout, 5xx or ambiguous response burns the attempt; never retry.
    Tag deletion remains an admin-level threat and MUST be restricted by a
    reviewed repository ruleset before this is attached to an actual run.
    """
    if environ is None:
        environ = os.environ
    run_id = check_preflight(expected_sha, confirmation, environ)
    token = environ.get("GITHUB_TOKEN", "")
    if not isinstance(token, str) or not token.strip():
        raise ClaimRefused("scoped GitHub token required")
    if opener is None:
        opener = urlopen

    base = api_url.rstrip("/") + "/repos/" + REPOSITORY
    marker_ruleset = environ.get("I2_P4_990_TAG_RULESET_ID", "")
    verify_marker_ruleset(opener, base, token, marker_ruleset)
    head = _json_request(
        opener, base + "/git/ref/heads/main", token)
    if head.get("object", {}).get("sha") != expected_sha:
        raise ClaimRefused("main moved after the reviewed dispatch SHA")

    claimed = _json_request(
        opener, base + "/git/refs", token, method="POST",
        body={"ref": CONSUMED_REF, "sha": expected_sha})
    if (claimed.get("ref") != CONSUMED_REF or
            claimed.get("object", {}).get("sha") != expected_sha):
        # An anomalous response may mean the tag was created; refuse the
        # experiment rather than try to claim another time.
        raise ClaimRefused("claimed marker did not match reviewed source")
    # A ruleset modified in the claim window is a hard fail. This remains
    # a best-effort live GitHub check, not an atomic ruleset transaction.
    verify_marker_ruleset(opener, base, token, marker_ruleset)
    return {
        "protocol": "i2-P4-origin-failure-unknown-alternative-990-v1",
        "claim": "GITHUB_CREATE_REF_201",
        "consumed_ref": CONSUMED_REF,
        "source_sha": expected_sha,
        "workflow_run_id": run_id,
        "workflow_run_attempt": 1,
        "scientific_result": "NOT_EXECUTED_BY_THIS_GUARD",
        "m11_authenticated": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args(argv)
    try:
        receipt = claim_once(args.expected_head, args.confirm)
    except ClaimRefused as exc:
        print("I2_P4_990_CLAIM_REFUSED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
