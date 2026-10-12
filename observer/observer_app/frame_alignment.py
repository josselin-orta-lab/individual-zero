"""Conservative cross-check of frame steps against recorded journal closures.

This is NOT an independent physical-world or complete causal audit.
"""
from __future__ import annotations

import json
from pathlib import Path

from .frame_validation import validate_frames
from .step_boundaries import check_step_boundaries


def compare_frames_to_journal(frames_path: Path, journal_path: Path) -> dict:
    result = {"frame_step_alignment": False, "independently_verified": False,
              "map_authorized": False, "checked_frames": 0, "error": None}
    structure = validate_frames(frames_path)
    if not structure["structurally_valid"]:
        result["error"] = "invalid_frame_structure"
        return result
    steps = check_step_boundaries(journal_path)
    if not steps["recorded_boundaries_valid"]:
        result["error"] = "invalid_recorded_step_boundaries"
        return result
    try:
        with frames_path.open("rb") as stream:
            data = json.loads(stream.read(16 * 1024 * 1024 + 1))
        requested = [frame["t_monde"] for frame in data["frames"]]
        closed = set(steps["closed_steps"])
        result["checked_frames"] = len(requested)
        if not requested:
            result["error"] = "empty_frame_sequence"
        elif any(step not in closed for step in requested):
            result["error"] = "frame_at_unclosed_step"
        else:
            # A closed step number alone is insufficient: reject frames
            # attributed to another execution attempt.
            with journal_path.open("rb") as stream:
                journal_bytes = stream.read(32 * 1024 * 1024 + 1)
            if len(journal_bytes) > 32 * 1024 * 1024:
                result["error"] = "journal_too_large"
                return result
            closed_attempts = {}
            for line in journal_bytes.split(bytes([10])):
                event = json.loads(line)["causal_event"]
                if event.get("kind") == "step_closed":
                    closed_attempts[event["t_monde"]] = event["attempt_ref"]
            expected_attempt = data["identity"]["attempt_ref"]
            if any(closed_attempts.get(step) != expected_attempt for step in requested):
                result["error"] = "frame_attempt_mismatch"
            else:
                result["frame_step_alignment"] = True
        return result
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        result["error"] = "unreadable_frame_data"
        return result
