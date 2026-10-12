"""Compare archive claims with externally supplied operator trust anchors.

The anchor is explicitly supplied outside the imported archive. This is
byte-level custody only, NOT an independent physical-world attestation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from .frame_validation import validate_frames
from .journal_preflight import check_chain
from .frame_alignment import compare_frames_to_journal

HASH = re.compile(r"[0-9a-f]{64}\Z")


def check_custody(frames_path: Path, journal_path: Path, *,
                  trusted_frame_sha256: str, trusted_journal_head: str,
                  trusted_journal_count: int) -> dict:
    result = {"operator_anchor_match": False, "frame_claims_match": False,
              "recorded_step_alignment": False, "physical_truth_verified": False,
              "full_causal_audit": False, "map_authorized": False,
              "error": None}
    if not isinstance(trusted_frame_sha256, str) or not HASH.fullmatch(trusted_frame_sha256) or not isinstance(trusted_journal_head, str) or not HASH.fullmatch(trusted_journal_head) or type(trusted_journal_count) is not int or trusted_journal_count < 1:
        result["error"] = "invalid_external_anchor"
        return result
    structure = validate_frames(frames_path)
    if not structure["structurally_valid"]:
        result["error"] = "invalid_frames"
        return result
    chain = check_chain(journal_path, expected_head=trusted_journal_head,
                        expected_count=trusted_journal_count)
    if not chain["chain_valid"] or not chain["trusted_tail_verified"]:
        result["error"] = "journal_anchor_mismatch"
        return result
    try:
        with frames_path.open("rb") as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        if hashlib.sha256(raw).hexdigest() != trusted_frame_sha256:
            result["error"] = "frame_anchor_mismatch"
            return result
        result["operator_anchor_match"] = True
        declaration = json.loads(raw)["attestation"]
        result["frame_claims_match"] = (
            declaration["journal_head_sha256"] == trusted_journal_head
            and declaration["journal_event_count"] == trusted_journal_count
        )
        if not result["frame_claims_match"]:
            result["error"] = "frame_journal_claim_mismatch"
            return result
        alignment = compare_frames_to_journal(frames_path, journal_path)
        result["recorded_step_alignment"] = alignment["frame_step_alignment"]
        if not result["recorded_step_alignment"]:
            result["error"] = alignment["error"]
        return result
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        result["error"] = "unreadable_custody_sources"
        return result
