"""F1M atomic GitHub first-only science reservation, BEFORE any heldout World.step.

Pure standard-library transport: no i3 engine imports, no seed execution.
The remote create-only ref wins atomically. All ambiguous network outcomes
FAIL CLOSED, and failure after reservation permanently consumes the 32 roots.
A repository administrator can still alter history; enforce a no-bypass ruleset.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO = "josselin-orta-lab/individual-zero"
CONSUMED_REF = "refs/heads/i3-stage8-f1m-heldout-consumed-once"
BRANCH = CONSUMED_REF.removeprefix("refs/heads/")
MARKER_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
               "F1M_T60_CONSUMED_BEFORE_EXPOSURE.json")
PREEXPOSURE = "d79eb0712daccab2dad0839d5c9a6eaa717eef9f"
GRID_BLOB = "659b72c2c5894a0ba89995a23419d66b61436465"
PROTOCOL_BLOB = "342a6794ecd26789da82940c2d1f10e427e3979c"
ACK = "CONSUME_F1M_32_ROOTS_NO_SCIENTIFIC_RETRY"
GRID_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
             "STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_GRID_2026-11-23.json")
PROTOCOL_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
                 "STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_PREEXPOSURE_2026-11-23.md")
DEV_WORKFLOW = ".github/workflows/i3-stage8f1m-dev-causal-pilot.yml"
SOURCE_PATHS = (
    "src/i3/modules/mind.py",
    "src/i3/modules/body.py",
    "src/i3/modules/world.py",
    "src/i3/modules/genome.py",
    "tools/stage8f1j_fixed_round_paid_competition.py",
    "tools/stage8f1h_prospective_native_body_value.py",
    "tools/stage8f1c_paid_postaction_learning.py",
    "tools/stage8f1d_next_decision_retention.py",
    "tools/stage8f1m_dev_residual_mediation.py",
    "tools/stage8f1m_independent_dev_cold.py",
    "tools/stage8f1m_one_shot_reservation.py",
    "tools/stage8f1m_scientific_native.py",
    "tools/stage8f1m_one_shot_evidence.py",
    "tools/stage8f1m_independent_scientific_cold.py",
    "tools/stage8f1m_one_shot_cold_entry.py",
    "tools/stage8f1m_one_shot_publish_status.py",
    ".github/workflows/i3-stage8f1m-heldout-science-manual-once.yml",
    DEV_WORKFLOW,
    "tools/stage8f1m_prereg_static_guard.py",
)
ENGINE_PINS = {
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
    "tools/stage8f1h_prospective_native_body_value.py":
        "02c5ece502729e3fa341f17cfa9cdc03e8c50bf4",
    "tools/stage8f1c_paid_postaction_learning.py":
        "c3d00fe078cac0ad9487ac39c2c8c7e081f32313",
    "tools/stage8f1d_next_decision_retention.py":
        "19f10a02b73759b52856e177ac3731f5826281c6",
}
ROOT_IDS = ["M%02d" % i for i in range(1, 33)]
SEEDS = list(range(202611239701, 202611239733))
ARMS = ["recent/carry", "recent/zero", "stale/carry", "stale/zero"]
REQUIRED_DEV_JOBS = {
    "dev_m_safety_and_smoke",
    "dev_m_smoke_cold_py312",
    "dev_m_full_t60",
    "dev_m_full_t60_cold_py312",
}


class ReservationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ReservationError("F1M ONE SHOT: " + message)


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _api(method, path, payload=None):
    token = os.getenv("GITHUB_TOKEN")
    require(bool(token), "real GitHub token required; cannot simulate consumption")
    data = canonical(payload) if payload is not None else None
    req = Request(
        "https://api.github.com/repos/" + REPO + path,
        data=data, method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "individual-zero-f1m-atomic-gate",
        },
    )
    try:
        with urlopen(req, timeout=40) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        raise ReservationError(
            "F1M ONE SHOT: GitHub " + method + " " + path
            + " returned HTTP " + str(exc.code)) from exc
    except URLError as exc:
        raise ReservationError("F1M ONE SHOT: GitHub unavailable; NO World.step") from exc


def source_blobs():
    from tools import stage8f1m_prereg_static_guard as frozen
    frozen.check_files()
    sources = {p: blob(Path(p).read_bytes()) for p in SOURCE_PATHS}
    require(all(sources[p] == value for p, value in ENGINE_PINS.items()),
            "reference P1.3, F1J, native body/world, or paid learning changed")
    require(blob(Path(GRID_PATH).read_bytes()) == GRID_BLOB and
            blob(Path(PROTOCOL_PATH).read_bytes()) == PROTOCOL_BLOB,
            "frozen preexposure sources were rewritten")
    grid = json.loads(Path(GRID_PATH).read_bytes())
    require(grid.get("phase") == "PREEXPOSURE_ONLY_NO_WORLD_STEP"
            and grid.get("scientific_exposure_authorized") is False
            and grid.get("temporary_content_readout_tick") == 5
            and grid.get("final_tick") == 60
            and grid.get("arms") == ARMS
            and grid.get("scientific_workflow_dispatch_allowed") is False
            and grid.get("residual_intervention_before_tick") == 6
            and [r["id"] for r in grid["origins"]] == ROOT_IDS
            and [r["seed"] for r in grid["origins"]] == SEEDS
            and len(grid["ecologies"]) == 8
            and all(sum(r["ecology"] == e["id"] for r in grid["origins"]) == 4
                    for e in grid["ecologies"]),
            "preallocated reserve, ecology or frozen intent changed")
    return sources


def context():
    e = os.environ
    require(e.get("GITHUB_REPOSITORY") == REPO
            and e.get("GITHUB_REF") == "refs/heads/main"
            and e.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and e.get("GITHUB_RUN_ATTEMPT") == "1",
            "science is manual main only, first attempt; no PR, schedule or rerun")
    require(e.get("GITHUB_RUN_ID", "").isdigit(), "missing real GitHub Actions run")
    ids = e.get("F1M_REHEARSAL_RUN_IDS", "").split(",")
    require(len(ids) == 2 and len(set(ids)) == 2
            and all(x.isdigit() and x != e["GITHUB_RUN_ID"] for x in ids),
            "TWO distinct same-tree DEV_M full+cold rehearsals required")
    head = e.get("GITHUB_SHA", "")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", head)), "invalid source SHA")
    require(head == subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip(),
        "checkout differs from dispatched commit")
    require(e.get("F1M_APPROVED_SOURCE_SHA") == head,
            "the explicit approved main source SHA differs")
    require(e.get("F1M_CONSUME_ACK") == ACK, "missing exact consume acknowledgement")
    require(bool(e.get("GITHUB_TOKEN")), "no remote authority")
    return {
        "repository": REPO, "head_sha": head,
        "workflow_run_id": e["GITHUB_RUN_ID"], "run_attempt": 1,
        "rehearsal_run_ids": ids,
        "event": "workflow_dispatch",
    }


def protected_once_ruleset():
    """Require an active, no-bypass, exact-ref GitHub rule blocking all ref writes."""
    items = _api("GET", "/rulesets")
    require(isinstance(items, list), "cannot inspect repository rulesets")
    candidates = []
    for item in items:
        if item.get("enforcement") != "active" or item.get("target") != "branch":
            continue
        detail = _api("GET", "/rulesets/" + str(item["id"]))
        conditions = detail.get("conditions", {}).get("ref_name", {})
        rules = {r.get("type") for r in detail.get("rules", [])}
        if (detail.get("enforcement") == "active"
                and detail.get("source_type") == "Repository"
                and detail.get("target") == "branch"
                and conditions.get("include") == [CONSUMED_REF]
                and conditions.get("exclude") == []
                and not detail.get("bypass_actors")
                and {"deletion", "non_fast_forward", "update"} <= rules):
            candidates.append({
                "id": detail["id"],
                "included_ref": CONSUMED_REF,
                "required_rules": sorted({"deletion", "non_fast_forward", "update"}),
                "bypass_actors": [],
                "enforcement": "active",
            })
    require(len(candidates) == 1,
            "F1M consumed branch must have ONE active exact-ref no-bypass "
            "deletion+non-fast-forward+update ruleset BEFORE claim")
    return candidates[0]



def immutable_release_policy():
    """GitHub admin-read API: require immutable NEW releases before exposure.

    The normal GITHUB_TOKEN has no Administration:read permission. A separate,
    read-only fine-grained F1L_PROTECTION_AUDIT_TOKEN is required; never log it.
    See GitHub REST GET /repos/{owner}/{repo}/immutable-releases.
    """
    token = os.getenv("F1L_PROTECTION_AUDIT_TOKEN")
    require(bool(token), "read-only admin token required for release immutability")
    req = Request(
        "https://api.github.com/repos/" + REPO + "/immutable-releases",
        method="GET",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "individual-zero-f1m-immutable-release-gate",
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
    except (HTTPError, URLError) as exc:
        raise ReservationError(
            "F1M ONE SHOT: immutable release policy not demonstrably enabled; "
            "no scientific source may start") from exc
    require(data.get("enabled") is True,
            "GitHub release immutability disabled or unverifiable")
    return {"enabled": True}


def verify_prior_rehearsal(ctx, current_tree_sha, run_id):
    run = _api("GET", "/actions/runs/" + run_id)
    sha = run.get("head_sha", "")
    require(run.get("status") == "completed"
            and run.get("conclusion") == "success"
            and run.get("event") == "pull_request"
            and run.get("path") == DEV_WORKFLOW
            and run.get("repository", {}).get("full_name") == REPO
            and bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
            "prior successful full DEV_M T60 engineering source run missing")
    jobs = _api("GET", "/actions/runs/" + run_id
                + "/jobs?per_page=100")
    passed = {j.get("name") for j in jobs.get("jobs", [])
              if j.get("status") == "completed"
              and j.get("conclusion") == "success"}
    require(REQUIRED_DEV_JOBS <= passed,
            "DEV_L native T60, engine-free cold T60, smoke + adversarial checks "
            "did not all pass")
    prior_commit = _api("GET", "/git/commits/" + sha)
    require(prior_commit.get("tree", {}).get("sha") == current_tree_sha,
            "DEV_L was audited on a DIFFERENT Git source tree")
    return sha


def reserve(output):
    """Atomic create-only claim; any failure afterwards consumes the allocation."""
    ctx = context()
    require(not output.exists(), "reservation receipt already exists")
    sources = source_blobs()
    ruleset = protected_once_ruleset()
    release_immutability = immutable_release_policy()
    head = _api("GET", "/git/ref/heads/main")
    require(head.get("object", {}).get("sha") == ctx["head_sha"],
            "main advanced before exposure claim")
    try:
        _api("GET", "/git/ref/heads/" + BRANCH)
    except ReservationError as exc:
        require("HTTP 404" in str(exc), "cannot establish consumed ref absence")
    else:
        raise ReservationError("F1M ONE SHOT: already consumed, NO RETRY")
    original = _api("GET", "/git/commits/" + ctx["head_sha"])
    tree_sha = original["tree"]["sha"]
    rehearsal_shas = [verify_prior_rehearsal(ctx, tree_sha, rid)
                       for rid in ctx["rehearsal_run_ids"]]
    claim = {
        "schema": "i3-stage8f1m-atomic-preexposure-claim/v0",
        "state": "RESERVED_CONSUMED_BEFORE_ANY_F1M_WORLD_STEP",
        "reservation_ref": CONSUMED_REF,
        "reserved_at_utc": datetime.now(timezone.utc).isoformat(),
        "preregistered_main_sha": PREEXPOSURE,
        "frozen_grid_blob": GRID_BLOB,
        "frozen_protocol_blob": PROTOCOL_BLOB,
        "ruleset": ruleset,
        "release_immutability": release_immutability,
        "rehearsal_verified_head_shas": rehearsal_shas,
        "rehearsal_verified_tree_sha": tree_sha,
        "root_ids": ROOT_IDS, "seeds": SEEDS, "arms": ARMS,
        "final_tick": 60,
        "no_action_override": True,
        "no_retry_even_after_failure": True,
        "native_passes_allocated": 1,
        "preexposure_static_guard_git_blob": "007a8e1597f9ee7ab0a4a4802fd6b3a55be60af9",
        "F1L_immutable": "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE",
        "stage2_immutable": "NOT_ISSUED/HOLD_NO_VERDICT",
        "source_blobs": sources, **ctx,
    }
    data = canonical(claim) + b"\n"
    git_blob = _api("POST", "/git/blobs", {
        "content": data.decode("utf-8"), "encoding": "utf-8"})
    tree = _api("POST", "/git/trees", {
        "base_tree": tree_sha,
        "tree": [{"path": MARKER_PATH, "mode": "100644",
                  "type": "blob", "sha": git_blob["sha"]}],
    })
    commit = _api("POST", "/git/commits", {
        "message": "science(i3): consume F1M 32-root T60 allocation before any step",
        "tree": tree["sha"], "parents": [ctx["head_sha"]],
    })
    created = _api("POST", "/git/refs", {
        "ref": CONSUMED_REF, "sha": commit["sha"]})
    require(created.get("ref") == CONSUMED_REF
            and created.get("object", {}).get("sha") == commit["sha"],
            "ambiguous atomic ref create: FAIL CLOSED; do not retry")
    receipt = {
        "schema": "i3-stage8f1m-github-atomic-reservation-receipt/v0",
        "reservation_ref": CONSUMED_REF,
        "reservation_commit": commit["sha"],
        "marker_git_blob": git_blob["sha"],
        "marker_sha256": sha256(data).hexdigest(),
        "claim": claim,
    }
    with Path(output).open("xb") as out:
        out.write(canonical(receipt) + b"\n")
        out.flush()
        os.fsync(out.fileno())
    return receipt


def validate_receipt(receipt, *, same_run=True):
    require(receipt.get("schema") ==
            "i3-stage8f1m-github-atomic-reservation-receipt/v0",
            "wrong reservation receipt schema")
    claim = receipt.get("claim", {})
    require(claim.get("schema") == "i3-stage8f1m-atomic-preexposure-claim/v0"
            and claim.get("state") ==
            "RESERVED_CONSUMED_BEFORE_ANY_F1M_WORLD_STEP"
            and claim.get("reservation_ref") == CONSUMED_REF
            and claim.get("preregistered_main_sha") == PREEXPOSURE
            and claim.get("frozen_grid_blob") == GRID_BLOB
            and claim.get("frozen_protocol_blob") == PROTOCOL_BLOB
            and claim.get("root_ids") == ROOT_IDS
            and claim.get("seeds") == SEEDS
            and claim.get("arms") == ARMS
            and claim.get("final_tick") == 60
            and claim.get("F1L_immutable") == "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE"
            and claim.get("native_passes_allocated") == 1
            and claim.get("release_immutability") == {"enabled": True}
            and claim.get("no_action_override") is True
            and claim.get("no_retry_even_after_failure") is True
            and claim.get("source_blobs") == source_blobs(),
            "receipt does not bind exact frozen F1M population/source")
    require(receipt.get("reservation_ref") == CONSUMED_REF
            and bool(re.fullmatch(r"[0-9a-f]{40}",
                                  receipt.get("reservation_commit", "")))
            and receipt.get("marker_git_blob") ==
            blob(canonical(claim) + b"\n")
            and receipt.get("marker_sha256") ==
            sha256(canonical(claim) + b"\n").hexdigest(),
            "reservation marker or hashes not authentic")
    if same_run:
        ctx = context()
        require(claim.get("workflow_run_id") == ctx["workflow_run_id"]
                and claim.get("head_sha") == ctx["head_sha"]
                and claim.get("rehearsal_run_id") == run_id,
                "not the issued reservation from THIS first-only GitHub run")
    return claim


def verify_remote(receipt, *, same_run=True):
    claim = validate_receipt(receipt, same_run=same_run)
    require(claim.get("release_immutability") == immutable_release_policy(),
            "immutable release policy was disabled after claim")
    require(claim.get("ruleset") == protected_once_ruleset(),
            "no-bypass ref protection changed since the reservation")
    remote = _api("GET", "/git/ref/heads/" + BRANCH)
    require(remote.get("object", {}).get("sha") ==
            receipt["reservation_commit"],
            "consumed ref disappeared or was moved")
    record = _api("GET", "/contents/" + quote(MARKER_PATH)
                  + "?ref=" + quote(BRANCH))
    require(record.get("sha") == receipt["marker_git_blob"]
            and record.get("encoding") == "base64"
            and base64.b64decode(record["content"]) ==
            canonical(claim) + b"\n",
            "remote pre-exposure marker differs from native receipt")
    return claim


def load_receipt(path):
    return json.loads(Path(path).read_bytes())


def main():
    p = argparse.ArgumentParser(description="F1M GitHub atomic first-only gate")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--readonly-pins", action="store_true")
    g.add_argument("--reserve", type=Path)
    g.add_argument("--verify", type=Path)
    args = p.parse_args()
    if args.readonly_pins:
        pins = source_blobs()
        print(json.dumps({"status": "F1M_PREEXPOSURE_PINS_ONLY",
                          "sources_verified": len(pins),
                          "native_heldout_world_steps": 0}, sort_keys=True))
    elif args.reserve:
        result = reserve(args.reserve)
        print(json.dumps({
            "status": "F1M_CLAIMED_BEFORE_ANY_STEP",
            "ref": result["reservation_ref"],
            "commit": result["reservation_commit"],
            "source": result["claim"]["head_sha"],
            "heldout_world_steps": 0,
        }, sort_keys=True))
    else:
        claim = verify_remote(load_receipt(args.verify))
        print(json.dumps({"status": "F1M_REMOTE_RESERVATION_VERIFIED",
                          "run_id": claim["workflow_run_id"],
                          "source": claim["head_sha"]}, sort_keys=True))


if __name__ == "__main__":
    main()
