"""F1K held-out reservation: atomic remote branch claim BEFORE the first World.step.

No engine imports. This is a GitHub-owned one-shot guard, not an unbreakable
cryptographic lock against administrators deleting refs or rewriting history.
Mock the API in tests. NEVER reserve the real branch in development or CI.
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
CONSUMED_REF = "refs/heads/i3-stage8-f1k-heldout-consumed-once"
BRANCH = CONSUMED_REF.removeprefix("refs/heads/")
MARKER_PATH = (
    "docs/research/studies/stage8f1-paid-microdecision/"
    "F1K_T60_CONSUMED_BEFORE_EXPOSURE.json"
)
PREEXPOSURE = "212d656f71ed5f4011c069575f9235b5b11d30fd"
GRID_BLOB = "bae149207c1fc41fb7fcc6fff11462e03dd17407"
PROTOCOL_BLOB = "f551f751eab04e58c93f432662c3181721228b13"
ACK = "CONSUME_F1K_16_ROOTS_NO_SCIENTIFIC_RETRY"
SOURCE_PATHS = (
    "src/i3/modules/mind.py",
    "src/i3/modules/body.py",
    "src/i3/modules/world.py",
    "src/i3/modules/genome.py",
    "tools/stage8f1j_fixed_round_paid_competition.py",
    "tools/stage8f1k_policy_cost_value_prospective.py",
    "tools/stage8f1k_independent_policy_value_cold_audit.py",
    "tools/stage8f1k_one_shot_reservation.py",
    "tools/stage8f1k_one_shot_evidence.py",
    "tools/stage8f1k_one_shot_cold_entry.py",
    "tools/stage8f1k_one_shot_publish_status.py",
    ".github/workflows/i3-stage8f1k-heldout-science-manual-once.yml",
)
ENGINE_PINS = {
    "src/i3/modules/mind.py":"a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py":"22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py":"d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py":"003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
}
GRID_PATH = (
    "docs/research/studies/stage8f1-paid-microdecision/"
    "STAGE8F1K_HELDOUT_POLICY_VALUE_GRID_2026-11-21.json"
)
PROTOCOL_PATH = (
    "docs/research/studies/stage8f1-paid-microdecision/"
    "STAGE8F1K_HELDOUT_POLICY_VALUE_PREEXPOSURE_2026-11-21.md"
)


class ReservationError(RuntimeError):
    pass


def require(condition: bool, message: str):
    if not condition:
        raise ReservationError("F1K ONE SHOT: " + message)


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _api(method: str, path: str, payload=None):
    token = os.environ.get("GITHUB_TOKEN")
    require(bool(token), "GITHUB_TOKEN missing; never reserve without real GitHub authority")
    body = canonical(payload) if payload is not None else None
    req = Request("https://api.github.com/repos/" + REPO + path, data=body,
                  method=method,
                  headers={"Authorization": "Bearer " + token,
                           "Accept": "application/vnd.github+json",
                           "X-GitHub-Api-Version": "2022-11-28",
                           "Content-Type": "application/json",
                           "User-Agent": "i3-f1k-once-gate"})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        raise ReservationError(
            "F1K ONE SHOT: GitHub " + method + " " + path
            + " returned HTTP " + str(exc.code)) from exc
    except URLError as exc:
        raise ReservationError(
            "F1K ONE SHOT: GitHub unavailable; no World.step admitted") from exc


def _current_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip()


def source_blobs() -> dict:
    sources = {p: blob(Path(p).read_bytes()) for p in SOURCE_PATHS}
    require(all(sources[p] == b for p, b in ENGINE_PINS.items()),
            "P1.3/F1J/physics source differs from original")
    require(blob(Path(GRID_PATH).read_bytes()) == GRID_BLOB
            and blob(Path(PROTOCOL_PATH).read_bytes()) == PROTOCOL_BLOB,
            "F1K preexposure grid or protocol altered")
    return sources


def context() -> dict:
    env = os.environ
    require(env.get("GITHUB_REPOSITORY") == REPO,
            "wrong repository")
    require(env.get("GITHUB_REF") == "refs/heads/main",
            "only a manual dispatch against main is admissible")
    require(env.get("GITHUB_EVENT_NAME") == "workflow_dispatch",
            "PR, push, schedule and reruns cannot consume science")
    require(env.get("GITHUB_RUN_ATTEMPT") == "1",
            "any retry attempt forbidden, including failed runs")
    require(env.get("GITHUB_RUN_ID", "").isdigit(), "missing real Actions run")
    require(env.get("F1K_REHEARSAL_RUN_ID", "").isdigit()
            and env["F1K_REHEARSAL_RUN_ID"] != env["GITHUB_RUN_ID"],
            "exact successful independent DEV_R rehearsal run ID required")
    head = env.get("GITHUB_SHA", "")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", head)),
            "invalid checkout SHA")
    require(head == _current_commit(), "checkout differs from dispatched HEAD")
    require(env.get("F1K_APPROVED_SOURCE_SHA") == head,
            "explicit reviewed 40-hex source SHA acknowledgement missing")
    require(env.get("F1K_CONSUME_ACK") == ACK, "explicit one-shot acknowledgement missing")
    require(bool(env.get("GITHUB_TOKEN")), "token required for atomic GitHub claim")
    return {
        "repository": REPO, "head_sha": head,
        "workflow_run_id": env["GITHUB_RUN_ID"], "run_attempt": 1,
        "rehearsal_run_id": env["F1K_REHEARSAL_RUN_ID"],
        "event": "workflow_dispatch",
    }


def verify_prior_rehearsal(ctx: dict, current_tree_sha: str) -> str:
    """Gate real K exposure on a prior fully successful EXACT-TREE DEV_R CI.

    Squash merges change commit SHAs but preserve the tree object. This
    compares the exact approved code/data tree, not the PR number or title.
    """
    run = _api("GET", "/actions/runs/" + ctx["rehearsal_run_id"])
    require(run.get("conclusion") == "success"
            and run.get("status") == "completed"
            and run.get("event") == "pull_request"
            and run.get("path") ==
                ".github/workflows/i3-stage8f1k-t60-dev-rehearsal.yml"
            and run.get("repository",{}).get("full_name") == REPO
            and bool(re.fullmatch(r"[0-9a-f]{40}",
                                  run.get("head_sha", ""))),
            "no successful exact FULL T60 16 DEV_R source cold rehearsal")
    technical = _api("GET", "/git/commits/" + run["head_sha"])
    require(technical.get("tree",{}).get("sha") == current_tree_sha,
            "DEV_R rehearsal tested a different tree; no science exposure")
    return run["head_sha"]


def reserve(output: Path) -> dict:
    """Create immutable-intent Git objects, then atomically create a NEW ref.

    A failed or ambiguous POST to refs always halts exposure. The ref will
    exist even when later original production/cold audit fails. Never delete
    this ref to recover a scientific result.
    """
    ctx = context()
    require(not output.exists(), "reservation receipt path already exists")
    sources = source_blobs()
    main = _api("GET", "/git/ref/heads/main")
    require(main.get("object", {}).get("sha") == ctx["head_sha"],
            "main advanced before reservation")
    # This GET is informational; the later POST /git/refs is the atomic gate.
    try:
        _api("GET", "/git/ref/heads/" + BRANCH)
    except ReservationError as exc:
        require("HTTP 404" in str(exc), "cannot verify absence of the one-shot ref")
    else:
        raise ReservationError("F1K ONE SHOT: reservation already consumed; NO RETRY")
    original = _api("GET", "/git/commits/" + ctx["head_sha"])
    rehearsal_head = verify_prior_rehearsal(ctx,original["tree"]["sha"])
    claim = {
        "schema": "i3-stage8f1k-pre-worldstep-once-claim/v0",
        "state": "RESERVED_CONSUMED_BEFORE_ANY_F1K_WORLD_STEP",
        "reservation_ref": CONSUMED_REF,
        "reserved_at_utc": datetime.now(timezone.utc).isoformat(),
        "preexposure_main_sha": PREEXPOSURE,
        "frozen_grid_blob": GRID_BLOB,
        "frozen_protocol_blob": PROTOCOL_BLOB,
        "f1i_immutable_status": "INCONCLUSIVE_COST_GATE",
        "reference": "P1.3-funded-v2-no-code-change",
        "policy": "F1JFixedRoundMind-opt-in",
        "rehearsal_verified_head_sha": rehearsal_head,
        "rehearsal_verified_tree_sha": original["tree"]["sha"],
        "root_ids": ["K" + str(i).zfill(2) for i in range(1, 17)],
        "seeds": list(range(202611219101, 202611219117)),
        "arms": ["reference_p13", "reference_sham", "fixed_round_f1j"],
        "final_tick": 60,
        "no_action_override": True,
        "no_retry_even_after_failure": True,
        "source_blobs": sources,
        **ctx,
    }
    data = canonical(claim) + b"\n"
    created_blob = _api("POST", "/git/blobs", {
        "content": data.decode("utf-8"), "encoding": "utf-8"})
    tree = _api("POST", "/git/trees", {
        "base_tree": original["tree"]["sha"],
        "tree": [{"path": MARKER_PATH, "mode": "100644",
                  "type": "blob", "sha": created_blob["sha"]}],
    })
    commit = _api("POST", "/git/commits", {
        "message": "science(i3): irrevocably consume F1K T60 holdout before first step",
        "tree": tree["sha"], "parents": [ctx["head_sha"]],
    })
    # Only the first successful GitHub create-ref wins. Never PATCH or force.
    created_ref = _api("POST", "/git/refs", {
        "ref": CONSUMED_REF, "sha": commit["sha"]})
    require(created_ref.get("ref") == CONSUMED_REF
            and created_ref.get("object", {}).get("sha") == commit["sha"],
            "atomic create-ref not acknowledged; fail closed")
    receipt = {
        "schema": "i3-stage8f1k-github-atomic-reservation-receipt/v0",
        "reservation_ref": CONSUMED_REF,
        "reservation_commit": commit["sha"],
        "marker_git_blob": created_blob["sha"],
        "marker_sha256": sha256(data).hexdigest(),
        "claim": claim,
    }
    # Never overwrite. Losing this receipt after Git ref creation also closes
    # the one-shot population; it does not authorize a restart.
    with output.open("xb") as stream:
        stream.write(canonical(receipt) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return receipt


def validate_receipt(receipt: dict, *, same_run: bool = True):
    require(receipt.get("schema") ==
            "i3-stage8f1k-github-atomic-reservation-receipt/v0",
            "wrong reservation receipt schema")
    claim = receipt.get("claim", {})
    require(claim.get("schema") ==
            "i3-stage8f1k-pre-worldstep-once-claim/v0"
            and claim.get("state") ==
            "RESERVED_CONSUMED_BEFORE_ANY_F1K_WORLD_STEP"
            and claim.get("root_ids") ==
            ["K" + str(i).zfill(2) for i in range(1, 17)]
            and claim.get("seeds") == list(range(202611219101, 202611219117))
            and bool(re.fullmatch(r"[0-9a-f]{40}",
                                  claim.get("rehearsal_verified_head_sha", "")))
            and bool(re.fullmatch(r"[0-9a-f]{40}",
                                  claim.get("rehearsal_verified_tree_sha", "")))
            and claim.get("preexposure_main_sha") == PREEXPOSURE
            and claim.get("frozen_grid_blob") == GRID_BLOB
            and claim.get("frozen_protocol_blob") == PROTOCOL_BLOB
            and claim.get("reservation_ref") == CONSUMED_REF
            and claim.get("reference") == "P1.3-funded-v2-no-code-change"
            and claim.get("no_retry_even_after_failure") is True
            and claim.get("source_blobs") == source_blobs(),
            "reservation does not bind exact F1K population and native source")
    require(receipt.get("reservation_ref") == CONSUMED_REF
            and bool(re.fullmatch(r"[0-9a-f]{40}",
                                 receipt.get("reservation_commit", "")))
            and receipt.get("marker_git_blob") ==
            blob(canonical(claim) + b"\n")
            and receipt.get("marker_sha256") ==
            sha256(canonical(claim) + b"\n").hexdigest(),
            "reservation marker fingerprint inconsistent")
    if same_run:
        require(os.environ.get("GITHUB_REPOSITORY") == REPO
                and os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
                and os.environ.get("GITHUB_REF") == "refs/heads/main"
                and os.environ.get("GITHUB_RUN_ATTEMPT") == "1"
                and claim.get("workflow_run_id") == os.environ.get("GITHUB_RUN_ID")
                and claim.get("head_sha") == os.environ.get("GITHUB_SHA")
                and claim.get("head_sha") == _current_commit(),
                "reservation is not from this specific first-try Actions run")
    return claim


def verify_remote(receipt: dict, *, same_run: bool = True):
    claim = validate_receipt(receipt, same_run=same_run)
    remote = _api("GET", "/git/ref/heads/" + BRANCH)
    require(remote.get("object", {}).get("sha") ==
            receipt["reservation_commit"],
            "one-shot ref disappeared or was moved since reservation")
    response = _api("GET", "/contents/" + quote(MARKER_PATH)
                    + "?ref=" + quote(BRANCH))
    require(response.get("sha") == receipt["marker_git_blob"]
            and response.get("encoding") == "base64",
            "remote marker absent or altered")
    remote_data = base64.b64decode(response["content"])
    require(remote_data == canonical(claim) + b"\n",
            "remote claim not byte-identical to pre-exposure receipt")
    return claim


def load_receipt(path: Path):
    return json.loads(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description="F1K atomic first-only GitHub gate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reserve", type=Path)
    group.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.reserve:
        result = reserve(args.reserve)
        print(json.dumps({
            "state": "CLAIMED_BEFORE_EXPOSURE",
            "branch": result["reservation_ref"],
            "run_id": result["claim"]["workflow_run_id"],
            "commit": result["reservation_commit"],
            "no_native_steps_yet": True,
        }, sort_keys=True))
    else:
        claim = verify_remote(load_receipt(args.verify))
        print(json.dumps({"state": "REMOTE_RESERVATION_VERIFIED",
                          "run_id": claim["workflow_run_id"],
                          "head": claim["head_sha"]}, sort_keys=True))


if __name__ == "__main__":
    main()
