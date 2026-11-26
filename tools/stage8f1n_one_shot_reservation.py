"""F1N atomic scientific GitHub claim BEFORE any N01..N48 World.step.

Pure Python stdlib, no engine imports. Only an explicit manual first-attempt
workflow_dispatch on the reviewed main SHA can consume the protected branch.
Ambiguous network failures FAIL CLOSED; no reexecution after any claim.
The preexposure document is an immutable planning record, NOT authorization.
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

from tools import stage8f1n_prereg_static_guard as FROZEN

REPO = "josselin-orta-lab/individual-zero"
CONSUMED_REF = FROZEN.CONSUMED_REF
BRANCH = CONSUMED_REF.removeprefix("refs/heads/")
MARKER_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
               "F1N_T60_CONSUMED_BEFORE_EXPOSURE.json")
PREEXPOSURE_COMMIT = "253835b7baaa54e0671bcf7cd9037c0d4b7f88ca"
GRID_BLOB = FROZEN.GRID_BLOB
PROTOCOL_BLOB = FROZEN.PROTOCOL_BLOB
GRID_PATH = str(FROZEN.GRID.relative_to(FROZEN.ROOT))
PROTOCOL_PATH = str(FROZEN.PROTOCOL.relative_to(FROZEN.ROOT))
ACK = "CONSUME_F1N_48_ROOTS_NO_SCIENTIFIC_RETRY"
DEV_WORKFLOW = ".github/workflows/i3-stage8f1n-dev-native-two-repetitions.yml"
SCIENCE_WORKFLOW = ".github/workflows/i3-stage8f1n-heldout-science-manual-once.yml"
ROOT_IDS = list(FROZEN.ROOT_IDS)
SEEDS = list(FROZEN.SEEDS)
ARMS = ["margin", "masked"]
REQUIRED_DEV_JOBS = {
    "dev_n_safety_and_smoke", "dev_na_native_t60", "dev_nb_native_t60",
    "dev_na_independent_cold_py312", "dev_nb_independent_cold_py312",
    "dev_n_disjoint_same_source_tree_verdict",
}
SOURCE_PATHS = (
    *FROZEN.ENGINE_PINS,
    *FROZEN.HISTORICAL_PINS,
    "tools/stage8f1c_paid_postaction_learning.py",
    "tools/stage8f1d_next_decision_retention.py",
    "tools/stage8f1h_prospective_native_body_value.py",
    "tools/stage8f1l_paid_content_body_value_dev.py",
    "tools/stage8f1n_prereg_static_guard.py",
    "tools/stage8f1n_paid_margin_mind.py",
    "tools/stage8f1n_dev_native_transport.py",
    "tools/stage8f1n_independent_dev_cold.py",
    "tools/stage8f1n_one_shot_reservation.py",
    "tools/stage8f1n_scientific_native.py",
    "tools/stage8f1n_one_shot_evidence.py",
    "tools/stage8f1n_independent_scientific_cold.py",
    "tools/stage8f1n_one_shot_cold_entry.py",
    "tools/stage8f1n_one_shot_publish_status.py",
    SCIENCE_WORKFLOW,
    DEV_WORKFLOW,
    "tests/test_stage8f1n_one_shot_transport.py",
    "tests/test_stage8f1n_dev_transport.py",
)


class ReservationError(RuntimeError):
    pass


def require(ok, message):
    if not ok:
        raise ReservationError("F1N ONE SHOT: " + message)


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _api(method, path, payload=None):
    """Real GitHub REST call. Never mocked in any code path that can claim."""
    token = os.getenv("GITHUB_TOKEN")
    require(bool(token), "real GITHUB_TOKEN required")
    req = Request("https://api.github.com/repos/" + REPO + path,
        data=canonical(payload) if payload is not None else None,
        method=method, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "individual-zero-f1n-atomic-claim",
        })
    try:
        with urlopen(req, timeout=40) as response:
            return json.loads(response.read())
    except HTTPError as exc:
        raise ReservationError("F1N ONE SHOT: GitHub " + method + " " + path +
                               " HTTP " + str(exc.code)) from exc
    except URLError as exc:
        raise ReservationError("F1N ONE SHOT: GitHub unreachable; no World.step") from exc


def source_blobs():
    FROZEN.check_files()
    pinned = {p: blob(Path(p).read_bytes()) for p in SOURCE_PATHS}
    for p, sha in {**FROZEN.ENGINE_PINS, **FROZEN.HISTORICAL_PINS}.items():
        require(pinned[p] == sha, "historical engine/preexposure source altered: " + p)
    require(blob(Path(GRID_PATH).read_bytes()) == GRID_BLOB and
            blob(Path(PROTOCOL_PATH).read_bytes()) == PROTOCOL_BLOB,
            "F1N literal preexposure grid or protocol changed")
    grid = json.loads(Path(GRID_PATH).read_bytes())
    FROZEN.verify_grid(grid)
    require([o["id"] for o in grid["origins"]] == ROOT_IDS and
            [o["seed"] for o in grid["origins"]] == SEEDS and
            grid["design_exposure_state"]["scientific_exposure_authorized"] is False and
            grid["design_exposure_state"]["birth_steps_performed"] == 0,
            "heldout identities changed or preexposure document rewritten")
    return pinned


def context():
    env = os.environ
    require(env.get("GITHUB_REPOSITORY") == REPO and
            env.get("GITHUB_REF") == "refs/heads/main" and
            env.get("GITHUB_EVENT_NAME") == "workflow_dispatch" and
            env.get("GITHUB_RUN_ATTEMPT") == "1",
            "manual main only, first attempt; PR, retry and schedule forbidden")
    require(env.get("GITHUB_RUN_ID", "").isdigit(), "actual run id required")
    ids = env.get("F1N_REHEARSAL_RUN_IDS", "").split(",")
    require(len(ids) == 2 and all(x.isdigit() for x in ids) and
            len(set(ids)) == 2 and env["GITHUB_RUN_ID"] not in ids,
            "two DIFFERENT full DEV_N runs required, no reuse")
    head = env.get("GITHUB_SHA", "")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", head)), "invalid source SHA")
    require(head == subprocess.check_output(["git", "rev-parse", "HEAD"],
                                            text=True).strip(),
            "checkout not identical to dispatched reviewed commit")
    require(env.get("F1N_APPROVED_SOURCE_SHA") == head,
            "explicit approved main source SHA differs (no whitespace normalization)")
    require(env.get("F1N_CONSUME_ACK") == ACK,
            "owner has not typed exact F1N-specific irreversible acknowledgment")
    require(bool(env.get("GITHUB_TOKEN")), "no authenticated GitHub authority")
    return {"repository": REPO, "head_sha": head,
            "workflow_run_id": env["GITHUB_RUN_ID"], "run_attempt": 1,
            "rehearsal_run_ids": ids, "event": "workflow_dispatch"}


def protected_once_ruleset():
    """ONE active no-bypass exact-ref ruleset, creation must remain possible."""
    summaries = _api("GET", "/rulesets")
    require(isinstance(summaries, list), "rulesets inaccessible")
    candidates = []
    for item in summaries:
        if item.get("target") != "branch" or item.get("enforcement") != "active":
            continue
        d = _api("GET", "/rulesets/" + str(item["id"]))
        refs = d.get("conditions", {}).get("ref_name", {})
        rules = {rule.get("type") for rule in d.get("rules", [])}
        if (d.get("source_type") == "Repository" and
                d.get("target") == "branch" and d.get("enforcement") == "active" and
                refs.get("include") == [CONSUMED_REF] and refs.get("exclude") == [] and
                not d.get("bypass_actors") and
                {"deletion", "update", "non_fast_forward"} <= rules and
                "creation" not in rules):
            candidates.append({"id": d["id"], "exact_ref": CONSUMED_REF,
                               "enforcement": "active", "bypass_actors": [],
                               "required_rules": ["deletion", "non_fast_forward", "update"]})
    require(len(candidates) == 1,
            "ONE active F1N exact-ref repository ruleset without bypass "
            "and deletion/update/non_fast_forward mandatory BEFORE claim")
    return candidates[0]


def immutable_release_policy():
    """Admin:read fine-grained Actions secret. GET only, never print token."""
    token = os.getenv("F1L_PROTECTION_AUDIT_TOKEN")
    require(bool(token), "separate GitHub Admin read-only audit token required")
    req = Request("https://api.github.com/repos/" + REPO + "/immutable-releases",
        method="GET", headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "individual-zero-f1n-immutable-release-gate",
        })
    try:
        with urlopen(req, timeout=30) as response:
            policy = json.loads(response.read())
    except (HTTPError, URLError) as exc:
        raise ReservationError("F1N ONE SHOT: release immutability not proven") from exc
    require(policy.get("enabled") is True, "GitHub immutable releases not enabled")
    return {"enabled": True}


def verify_prior_rehearsal(ctx, tree_sha, run_id):
    """Separate real first-only DEV_N runs; BOTH full 8+8 and independent cold."""
    run = _api("GET", "/actions/runs/" + run_id)
    sha = run.get("head_sha", "")
    require(run.get("status") == "completed" and
            run.get("conclusion") == "success" and
            run.get("event") == "pull_request" and
            run.get("run_attempt") == 1 and
            run.get("path") == DEV_WORKFLOW and
            run.get("repository", {}).get("full_name") == REPO and
            bool(re.fullmatch(r"[0-9a-f]{40}", sha)),
            "DEV_N full-native / Python3.12 cold run must PASS independently")
    jobs = _api("GET", "/actions/runs/" + run_id + "/jobs?per_page=100")
    passing = {j.get("name") for j in jobs.get("jobs", [])
               if j.get("status") == "completed" and j.get("conclusion") == "success"}
    require(REQUIRED_DEV_JOBS <= passing,
            "all six DEV_NA/DEV_NB native+shams+independent cold jobs required")
    commit = _api("GET", "/git/commits/" + sha)
    require(commit.get("tree", {}).get("sha") == tree_sha,
            "DEV_N rehearsal was on a DIFFERENT Git source tree")
    return sha


def _ref_absent():
    """404 is the ONLY admissible proof of unconsumed F1N roots."""
    try:
        _api("GET", "/git/ref/heads/" + BRANCH)
    except ReservationError as exc:
        require("HTTP 404" in str(exc), "consumed ref not provably absent")
    else:
        raise ReservationError("F1N ONE SHOT: ALREADY CONSUMED; never retry")



def readonly_admin_preflight():
    """GET-only verification for PR software audit; no claim or World.step."""
    pins = source_blobs()
    rule = protected_once_ruleset()
    policy = immutable_release_policy()
    _ref_absent()
    for tag in ("i3-stage8f1n-t60-raw-heldout-once",
                "i3-stage8f1n-t60-cold-heldout-once"):
        try:
            _api("GET", "/releases/tags/" + tag)
        except ReservationError as exc:
            require("HTTP 404" in str(exc), "cannot prove F1N tag absence")
        else:
            raise ReservationError("F1N release already exists; NO retry")
    return {"status":"F1N_REMOTE_ADMIN_READONLY_PROTECTIONS_PASS_NO_EXPOSURE",
            "ruleset":rule,"immutable_release_policy":policy,
            "sources_verified":len(pins),"consumed_ref_absent":True,
            "science_heldout_world_steps":0}


def preflight_remote(ctx):
    """Read-only administrative check, NO reservation or native births."""
    pinned = source_blobs()
    rule = protected_once_ruleset()
    policy = immutable_release_policy()
    remote = _api("GET", "/git/ref/heads/main")
    require(remote.get("object", {}).get("sha") == ctx["head_sha"],
            "main advanced or dispatch SHA differs")
    _ref_absent()
    for tag in ("i3-stage8f1n-t60-raw-heldout-once",
                "i3-stage8f1n-t60-cold-heldout-once"):
        try:
            _api("GET", "/releases/tags/" + tag)
        except ReservationError as exc:
            require("HTTP 404" in str(exc), "cannot prove scientific tag absence")
        else:
            raise ReservationError("F1N ONE SHOT: release already exists, no retry")
    source = _api("GET", "/git/commits/" + ctx["head_sha"])
    tree_sha = source["tree"]["sha"]
    shas = [verify_prior_rehearsal(ctx, tree_sha, rid)
            for rid in ctx["rehearsal_run_ids"]]
    return {"source_blobs": pinned, "ruleset": rule,
            "release_policy": policy, "source_tree_sha": tree_sha,
            "rehearsal_head_shas": shas}


def reserve(output):
    """Mutating create-only claim. NEVER call from tests, PR, DEV or preflight."""
    ctx = context()
    output = Path(output)
    require(not output.exists(), "reservation receipt path already occupied")
    checked = preflight_remote(ctx)
    claim = {
        "schema": "i3-stage8f1n-atomic-preexposure-claim/v0",
        "state": "RESERVED_CONSUMED_BEFORE_ANY_F1N_WORLD_STEP",
        "reservation_ref": CONSUMED_REF,
        "reserved_at_utc": datetime.now(timezone.utc).isoformat(),
        "preregistered_main_sha": PREEXPOSURE_COMMIT,
        "frozen_grid_blob": GRID_BLOB, "frozen_protocol_blob": PROTOCOL_BLOB,
        "ruleset": checked["ruleset"],
        "release_immutability": checked["release_policy"],
        "rehearsal_verified_head_shas": checked["rehearsal_head_shas"],
        "rehearsal_verified_tree_sha": checked["source_tree_sha"],
        "root_ids": ROOT_IDS, "seeds": SEEDS, "arms": ARMS,
        "part_names": list(FROZEN.PARTS), "final_tick": 60,
        "original_parts_allocated": 336,
        "one_native_pass_only": True,
        "no_action_override": True,
        "no_retry_even_after_failure": True,
        "stage2_immutable": "NOT_ISSUED/HOLD_NO_VERDICT",
        "historical_F1L_negative": "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE",
        "historical_F1M_negative": "NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE",
        "source_blobs": checked["source_blobs"], **ctx,
    }
    data = canonical(claim) + b"\n"
    git_blob = _api("POST", "/git/blobs", {"content": data.decode("utf8"),
                                           "encoding": "utf-8"})
    tree = _api("POST", "/git/trees", {
        "base_tree": checked["source_tree_sha"],
        "tree": [{"path": MARKER_PATH, "mode": "100644", "type": "blob",
                  "sha": git_blob["sha"]}],
    })
    commit = _api("POST", "/git/commits", {
        "message": "science(i3): irrevocably consume F1N 48 native roots before birth",
        "tree": tree["sha"], "parents": [ctx["head_sha"]],
    })
    created = _api("POST", "/git/refs", {
        "ref": CONSUMED_REF, "sha": commit["sha"]})
    require(created.get("ref") == CONSUMED_REF and
            created.get("object", {}).get("sha") == commit["sha"],
            "ambiguous create-only claim; FAIL CLOSED, NEVER RETRY")
    receipt = {
        "schema": "i3-stage8f1n-github-atomic-reservation-receipt/v0",
        "reservation_ref": CONSUMED_REF,
        "reservation_commit": commit["sha"],
        "marker_git_blob": git_blob["sha"],
        "marker_sha256": sha256(data).hexdigest(),
        "claim": claim,
    }
    with output.open("xb") as f:
        f.write(canonical(receipt) + b"\n")
        f.flush()
        os.fsync(f.fileno())
    return receipt


def validate_receipt(receipt, *, same_run=True):
    require(receipt.get("schema") ==
            "i3-stage8f1n-github-atomic-reservation-receipt/v0",
            "wrong reservation receipt")
    claim = receipt.get("claim", {})
    require(claim.get("schema") == "i3-stage8f1n-atomic-preexposure-claim/v0" and
            claim.get("state") == "RESERVED_CONSUMED_BEFORE_ANY_F1N_WORLD_STEP" and
            claim.get("reservation_ref") == CONSUMED_REF and
            claim.get("preregistered_main_sha") == PREEXPOSURE_COMMIT and
            claim.get("frozen_grid_blob") == GRID_BLOB and
            claim.get("frozen_protocol_blob") == PROTOCOL_BLOB and
            claim.get("root_ids") == ROOT_IDS and claim.get("seeds") == SEEDS and
            claim.get("arms") == ARMS and
            claim.get("part_names") == list(FROZEN.PARTS) and
            claim.get("original_parts_allocated") == 336 and
            claim.get("final_tick") == 60 and
            claim.get("release_immutability") == {"enabled": True} and
            claim.get("one_native_pass_only") is True and
            claim.get("no_action_override") is True and
            claim.get("no_retry_even_after_failure") is True and
            claim.get("stage2_immutable") == "NOT_ISSUED/HOLD_NO_VERDICT" and
            claim.get("historical_F1L_negative") ==
                "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE" and
            claim.get("historical_F1M_negative") ==
                "NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE" and
            type(claim.get("rehearsal_run_ids")) is list and
            len(claim["rehearsal_run_ids"]) == 2 and
            len(set(claim["rehearsal_run_ids"])) == 2 and
            all(str(x).isdigit() for x in claim["rehearsal_run_ids"]) and
            type(claim.get("rehearsal_verified_head_shas")) is list and
            len(claim["rehearsal_verified_head_shas"]) == 2 and
            all(bool(re.fullmatch(r"[0-9a-f]{40}", x))
                for x in claim["rehearsal_verified_head_shas"]) and
            bool(re.fullmatch(r"[0-9a-f]{40}",
                       claim.get("rehearsal_verified_tree_sha", ""))) and
            claim.get("source_blobs") == source_blobs(),
            "claim does not bind frozen 48-root source/all genuine funding controls")
    require(receipt.get("reservation_ref") == CONSUMED_REF and
            bool(re.fullmatch(r"[0-9a-f]{40}",
                              receipt.get("reservation_commit", ""))) and
            receipt.get("marker_git_blob") == blob(canonical(claim) + b"\n") and
            receipt.get("marker_sha256") ==
                sha256(canonical(claim) + b"\n").hexdigest(),
            "reservation marker digest invalid")
    if same_run:
        ctx = context()
        require(claim.get("workflow_run_id") == ctx["workflow_run_id"] and
                claim.get("head_sha") == ctx["head_sha"] and
                claim.get("rehearsal_run_ids") == ctx["rehearsal_run_ids"],
                "different run or attempt claimed the same F1N roots")
    return claim


def verify_remote(receipt, *, same_run=True):
    claim = validate_receipt(receipt, same_run=same_run)
    require(claim.get("release_immutability") == immutable_release_policy(),
            "release policy disabled after claim")
    require(claim.get("ruleset") == protected_once_ruleset(),
            "protected ref has drifted or bypass exception was introduced")
    ref = _api("GET", "/git/ref/heads/" + BRANCH)
    require(ref.get("object", {}).get("sha") == receipt["reservation_commit"],
            "consumed ref missing/moved after reservation")
    file = _api("GET", "/contents/" + quote(MARKER_PATH) +
                "?ref=" + quote(BRANCH))
    require(file.get("sha") == receipt["marker_git_blob"] and
            file.get("encoding") == "base64" and
            base64.b64decode(file["content"]) == canonical(claim) + b"\n",
            "remote immutable preexposure marker differs from own claim")
    return claim


def load_receipt(path):
    return json.loads(Path(path).read_bytes())


def main():
    parser = argparse.ArgumentParser(description="F1N scientific atomic one-shot claim")
    opt = parser.add_mutually_exclusive_group(required=True)
    opt.add_argument("--readonly-pins", action="store_true")
    opt.add_argument("--readonly-admin", action="store_true")
    opt.add_argument("--reserve", type=Path)
    opt.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.readonly_pins:
        pins = source_blobs()
        print(json.dumps({"status": "F1N_PREEXPOSURE_SOURCES_ONLY",
                          "sources_verified": len(pins),
                          "native_heldout_world_steps": 0,
                          "scientific_dispatch_authorized": False}, sort_keys=True))
    elif args.readonly_admin:
        print(json.dumps(readonly_admin_preflight(),sort_keys=True))
    elif args.reserve:
        receipt = reserve(args.reserve)
        print(json.dumps({"status": "F1N_IRREVERSIBLY_RESERVED_BEFORE_FIRST_BIRTH",
                          "reservation_commit": receipt["reservation_commit"],
                          "new_heldout_steps": 0}, sort_keys=True))
    else:
        claim = verify_remote(load_receipt(args.verify))
        print(json.dumps({"status": "F1N_REMOTE_CLAIM_VERIFIED",
                          "science_run_id": claim["workflow_run_id"],
                          "approved_source_sha": claim["head_sha"]}, sort_keys=True))


if __name__ == "__main__":
    main()