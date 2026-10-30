"""Fail-closed A2-R one-life launch context; NEVER authorizes a study.

This contract checks operator-provided, OUTSIDE-pinned source/run provenance.
It cannot independently establish that an environment variable was issued by
GitHub or that a reviewer approved the registered scientific launch. Those
require GitHub's protected environment and an independent run-event audit.
No life is born in this module.
"""
from __future__ import annotations

import json
import re
from hashlib import sha256

from i1_a2r_archive_guard import (
    MATRIX, SHA40, SHA64, _unique_dict, _no_constants, canonical_bytes,
    origin_lock, validate_lock, _identity,
)

REPOSITORY = "josselin-orta-lab/individual-zero"
WORKFLOW_REF = (
    REPOSITORY + "/.github/workflows/i1-a2r-confirmatory-one-shot.yml"
    "@refs/heads/main"
)
PROTOCOL = "I1_ECO_A2R_REWARD_PREREGISTRATION_2026-10-30"
SCOPE = "A2R_RUN_CONTEXT_PREFLIGHT_NOT_EXTERNAL_ATTESTATION_NOT_L3"
_INT = re.compile(r"[1-9][0-9]*\Z")


def validate_launch_context(*, role, seed, mode, raw_lock,
                            externally_pinned_sha256, github, approval):
    """Require exact row, original one-shot GitHub run and reviewed source lock.

    The lock's own 'authorization' field is intentionally NOT_AUTHORIZED.
    Review is a separate protected-environment obligation; an approval dict
    is only a checked claim, not a cryptographic signature.
    """
    if (type(role) is not str or type(seed) is not int
            or type(mode) is not str or (role, seed, mode) not in MATRIX):
        raise ValueError("A2-R row is outside the immutable 96-life matrix")
    if (type(raw_lock) is not bytes or not raw_lock
            or type(externally_pinned_sha256) is not str
            or SHA64.fullmatch(externally_pinned_sha256) is None
            or sha256(raw_lock).hexdigest() != externally_pinned_sha256):
        raise ValueError("A2-R external source/run lock SHA-256 mismatch")
    try:
        lock = json.loads(raw_lock.decode("ascii"),
                          object_pairs_hook=_unique_dict,
                          parse_constant=_no_constants)
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid canonical A2-R origin lock") from exc
    if canonical_bytes(lock) != raw_lock:
        raise ValueError("noncanonical A2-R origin lock")
    if type(github) is not dict or type(approval) is not dict:
        raise ValueError("A2-R requires external GitHub and approval inputs")
    expected_github = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
        "GITHUB_RUN_ATTEMPT": "1",
    }
    for key, value in expected_github.items():
        if github.get(key) != value:
            raise ValueError("A2-R wrong run event/ref/workflow/attempt: " + key)
    run_str = github.get("GITHUB_RUN_ID")
    source = github.get("GITHUB_SHA")
    if (type(run_str) is not str or _INT.fullmatch(run_str) is None
            or int(run_str) >= 2**63 or type(source) is not str
            or SHA40.fullmatch(source) is None):
        raise ValueError("A2-R missing exact GitHub run or source SHA")
    run_id = int(run_str)
    tree, preset = lock.get("source_tree"), lock.get("preset_sha256")
    if (type(tree) is not str or SHA40.fullmatch(tree) is None
            or type(preset) is not str or SHA64.fullmatch(preset) is None):
        raise ValueError("A2-R source tree or preset not pinned")
    validate_lock(
        lock, expected_commit=source, expected_tree=tree,
        expected_preset=preset, expected_run_id=run_id,
    )
    reviewed = {
        "A2R_REVIEWED_PROTOCOL": PROTOCOL,
        "A2R_REVIEWED_SOURCE_SHA": source,
        "A2R_REVIEWED_LOCK_SHA256": externally_pinned_sha256,
        "A2R_REVIEWED_RUN_ID": run_str,
    }
    if approval != reviewed:
        raise ValueError("A2-R launch not bound to exact reviewed source/run")
    return {
        "scope": SCOPE,
        "role": role, "seed": seed, "mode": mode,
        "identity": _identity(role, seed, mode),
        "source_commit": source,
        "source_tree": tree,
        "preset_sha256": preset,
        "github_run_id": run_id,
        "github_run_attempt": 1,
        "external_lock_sha256_claimed": externally_pinned_sha256,
        "external_run_event_independently_verified": False,
        "protected_environment_review_independently_verified": False,
        "cohort_launch_authorized_by_this_module": False,
        "general_L3": "NOT_ESTABLISHED",
    }
