"""Independent GitHub Actions run attestation for prospective I1 A2-R.

Reads a lock whose SHA comes from outside the run, and separately queries
GitHub's REST API. A live GitHub listing alone is NOT a durable once-ever
proof: privileged operators can delete records. No births or L3 assertions.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

from i1_a2r_archive_guard import SHA40, SHA64, load_canonical_json, validate_lock

SCHEMA = "individual-zero-i1-a2r-actions-run-attestation/1"
REPOSITORY = "josselin-orta-lab/individual-zero"
WORKFLOW_PATH = ".github/workflows/i1-a2r-confirmatory-one-shot.yml"
BRANCH = "main"
_FINISHED = frozenset(("success", "failure", "cancelled", "timed_out",
                       "skipped", "action_required", "neutral"))


def _positive(value, label):
    if type(value) is not int or value <= 0:
        raise ValueError("invalid GitHub Actions " + label)
    return value


def _sha(value, pattern, label):
    if type(value) is not str or not pattern.fullmatch(value):
        raise ValueError("invalid pinned " + label)
    return value


def _check_lock(lock, *, commit, tree, preset, run_id):
    _sha(commit, SHA40, "source commit")
    _sha(tree, SHA40, "source tree")
    _sha(preset, SHA64, "oasis preset")
    _positive(run_id, "run id")
    validate_lock(lock, expected_commit=commit, expected_tree=tree,
                  expected_preset=preset, expected_run_id=run_id)


def verify_actions_run(*, lock, commit, tree, preset, run_id, run, workflow,
                       git_commit, dispatch_listing, phase="after_run"):
    """Cross-check separately fetched GitHub REST records and external lock.

    Prebirth phase only checks a pending or running first attempt. Postrun
    phase records ALL terminal outcomes, including failure. Neither phase
    authorizes another run or independently proves that I1 source executed.
    The workflow path is reserved exclusively for confirmatory births and
    must never be used for disposable CI software tests.
    """
    _check_lock(lock, commit=commit, tree=tree, preset=preset, run_id=run_id)
    if phase not in ("before_birth", "after_run"):
        raise ValueError("unregistered A2-R provenance phase")
    for obj, name in ((run, "run"), (workflow, "workflow"),
                      (git_commit, "commit"), (dispatch_listing, "dispatch listing")):
        if type(obj) is not dict:
            raise ValueError("missing independent GitHub REST " + name)

    wf_id = _positive(run.get("workflow_id"), "workflow id")
    if (type(run.get("id")) is not int or run["id"] != run_id
            or run.get("event") != "workflow_dispatch"
            or run.get("path") != WORKFLOW_PATH
            or run.get("head_sha") != commit
            or run.get("head_branch") != BRANCH
            or type(run.get("run_attempt")) is not int
            or run["run_attempt"] != 1
            or type(run.get("run_number")) is not int
            or run["run_number"] < 1):
        raise ValueError("run origin, workflow or first attempt differs from frozen lock")
    if (type(run.get("repository")) is not dict
            or run["repository"].get("full_name") != REPOSITORY
            or type(run.get("head_repository")) is not dict
            or run["head_repository"].get("full_name") != REPOSITORY
            or type(run.get("head_commit")) is not dict
            or run["head_commit"].get("id") != commit):
        raise ValueError("run is forked or not from externally pinned commit")
    if (type(workflow.get("id")) is not int or workflow["id"] != wf_id
            or workflow.get("path") != WORKFLOW_PATH
            or workflow.get("state") != "active"):
        raise ValueError("GitHub registered workflow id/path/state mismatch")
    if (git_commit.get("sha") != commit
            or type(git_commit.get("tree")) is not dict
            or git_commit["tree"].get("sha") != tree):
        raise ValueError("GitHub commit tree differs from independent source lock")

    # The GitHub workflow-runs endpoint supplies server-side total_count.
    # Checking a single page without checking total_count is insufficient.
    if (type(dispatch_listing.get("total_count")) is not int
            or dispatch_listing["total_count"] != 1
            or type(dispatch_listing.get("workflow_runs")) is not list
            or len(dispatch_listing["workflow_runs"]) != 1):
        raise ValueError("one-shot workflow has zero or multiple dispatch runs")
    single = dispatch_listing["workflow_runs"][0]
    if (type(single) is not dict
            or type(single.get("id")) is not int
            or single["id"] != run_id
            or single.get("workflow_id") != wf_id
            or single.get("event") != "workflow_dispatch"
            or single.get("head_sha") != commit
            or type(single.get("run_attempt")) is not int
            or single["run_attempt"] != 1):
        raise ValueError("GitHub dispatch history does not match sole original run")

    status, conclusion = run.get("status"), run.get("conclusion")
    if phase == "before_birth":
        if (status not in ("queued", "in_progress", "waiting",
                           "pending", "requested") or conclusion is not None):
            raise ValueError("run is not prebirth or in progress")
    elif status != "completed" or conclusion not in _FINISHED:
        raise ValueError("postrun attestation requires a terminal Actions outcome")

    return {
        "schema": SCHEMA, "repository": REPOSITORY,
        "workflow_path": WORKFLOW_PATH, "head_branch": BRANCH,
        "source_commit": commit, "source_tree": tree, "preset_sha256": preset,
        "github_run_id": run_id, "github_workflow_id": wf_id,
        "github_run_attempt": 1, "phase": phase,
        "actions_status": status, "actions_conclusion": conclusion,
        "observed_workflow_dispatch_total_count": 1,
        "live_api_metadata_matches_external_lock": True,
        "once_only_in_current_github_listing": True,
        "immutable_once_only_guaranteed": False,
        "runtime_executed_source_independently_proven": False,
        "full_m11_archive_verified": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED", "historical_A1C": "NO_GO",
    }


def _fetch_github_json(path, *, token=None):
    """GitHub API HTTPS only; do not read self-reported in-run manifests."""
    if type(path) is not str or not path.startswith(
            "/repos/" + REPOSITORY + "/") or len(path) > 512:
        raise ValueError("unsupported live GitHub provenance endpoint")
    url = "https://api.github.com" + path
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "individual-zero-a2r-provenance-audit",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as stream:
            if stream.geturl() != url:
                raise ValueError("GitHub API provenance unexpectedly redirected")
            raw = stream.read(5_000_001)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise ValueError("GitHub API provenance unavailable") from exc
    if len(raw) > 5_000_000:
        raise ValueError("oversized GitHub provenance JSON")
    try:
        obj = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed GitHub provenance JSON") from exc
    if type(obj) is not dict:
        raise ValueError("GitHub provenance root must be an object")
    return obj


def audit_live_github_run(*, lock_path, expected_lock_sha256, commit, tree,
                          preset, run_id, phase="after_run", api_get=None):
    """Consume an externally hashed lock plus INDEPENDENT live API reads.

    Unit tests may inject api_get; production callers should omit it. The
    lock SHA and commit/tree/preset/run_id must be retrieved independently
    of the run and cannot come only from the run's generated artifacts.
    """
    _sha(expected_lock_sha256, SHA64, "external lock hash")
    lock = load_canonical_json(Path(lock_path),
                               expected_digest=expected_lock_sha256)
    _check_lock(lock, commit=commit, tree=tree, preset=preset, run_id=run_id)
    if api_get is None:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        api_get = lambda endpoint: _fetch_github_json(endpoint, token=token)
    base = "/repos/" + REPOSITORY
    run = api_get(base + "/actions/runs/" + str(run_id))
    if type(run) is not dict:
        raise ValueError("missing live GitHub Actions run")
    wf_id = _positive(run.get("workflow_id"), "workflow id")
    workflow = api_get(base + "/actions/workflows/" + str(wf_id))
    git_commit = api_get(base + "/git/commits/" + commit)
    dispatch = api_get(base + "/actions/workflows/" + str(wf_id)
                       + "/runs?event=workflow_dispatch&per_page=100")
    return verify_actions_run(
        lock=lock, commit=commit, tree=tree, preset=preset, run_id=run_id,
        run=run, workflow=workflow, git_commit=git_commit,
        dispatch_listing=dispatch, phase=phase,
    )
