"""Fail-closed verifier for operator-owned engine-recorded 2D histories.

This reader has NO Core imports, never restores a life, executes no
simulation, and refuses untrusted imported geometry. The geometric cells are
captured by the real physical owner during a local run. Hashes and journal
positions are checked independently of that producer's Python process.

A successful result is an ENGINE-RECORDED replay, not scientific Oracle truth.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .frame_validation import validate_frames
from .journal_preflight import check_chain
from .step_boundaries import check_step_boundaries
from .frame_alignment import compare_frames_to_journal


def verify_engine_recording(frames_path: Path, journal_path: Path, *,
                            report: dict[str, Any], frame_hash: str,
                            journal_hash: str, step: int) -> dict[str, Any]:
    outcome = {
        "available": False,
        "capture_integrity_verified": False,
        "engine_pose_journal_match": False,
        "physical_truth_verified": False,
        "scientific_validation": None,
        "geometry": None,
        "frame": None,
        "step": step,
        "origin": "operator_local_engine_capture",
        "reason": "unverified_capture",
    }
    def fail(reason: str) -> dict[str, Any]:
        outcome["reason"] = reason
        return outcome
    if type(step) is not int or step < 1:
        return fail("invalid_step")
    if not isinstance(report, dict) or report.get("offline_audit_completed") is not True:
        return fail("missing_independent_journal_audit_receipt")
    if (report.get("external_oracle_loaded") is not False
            or report.get("external_bench_loaded") is not False):
        return fail("unexpected_external_science")
    if report.get("terminal_deaths") != 0:
        return fail("terminal_history_requires_separate_custody")
    if type(report.get("steps_physically_executed")) is not int:
        return fail("missing_executed_step_count")
    if not validate_frames(frames_path)["structurally_valid"]:
        return fail("invalid_geometry_archive")
    try:
        with frames_path.open("rb") as stream:
            frame_bytes = stream.read(16 * 1024 * 1024 + 1)
        with journal_path.open("rb") as stream:
            journal_bytes = stream.read(32 * 1024 * 1024 + 1)
        if hashlib.sha256(frame_bytes).hexdigest() != frame_hash:
            return fail("frame_manifest_digest_mismatch")
        if hashlib.sha256(journal_bytes).hexdigest() != journal_hash:
            return fail("journal_manifest_digest_mismatch")
        if hashlib.sha256(journal_bytes).hexdigest() != report.get("journal_bytes_sha256"):
            return fail("journal_receipt_digest_mismatch")
        doc = json.loads(frame_bytes)
        if doc.get("identity", {}).get("individual_id") != report.get("individual_id"):
            return fail("individual_identity_mismatch")
        if doc["identity"]["life_generation"] != 0:
            return fail("unknown_life_generation")
        claim = doc["attestation"]
        if (claim["journal_head_sha256"] != report.get("journal_head_sha256")
                or claim["journal_event_count"] != report.get("journal_event_count")
                or claim["source_sha256"] != report.get("journal_bytes_sha256")):
            return fail("unmatched_producer_receipt")
        chain = check_chain(journal_path,
                            expected_head=report["journal_head_sha256"],
                            expected_count=report["journal_event_count"])
        if not chain["chain_valid"] or not chain["trusted_tail_verified"]:
            return fail("invalid_journal_chain")
        steps = check_step_boundaries(journal_path)
        if not steps["recorded_boundaries_valid"]:
            return fail("invalid_physical_step_boundaries")
        count = report["steps_physically_executed"]
        if (len(doc["frames"]) != count
                or steps["closed_steps"] != list(range(1, count + 1))):
            return fail("incomplete_physical_history")
        aligned = compare_frames_to_journal(frames_path, journal_path)
        if not aligned["frame_step_alignment"]:
            return fail("frame_attempt_or_step_mismatch")
        # Compare every recorded WorldBody post-transition position to the
        # independently read frame. A self-consistent header cannot compensate
        # for a falsified pose.
        transitions = {}
        for raw in journal_bytes.split(b"\n"):
            event = json.loads(raw)["causal_event"]
            if event.get("kind") != "world_transition_experienced":
                continue
            key = (event.get("t_monde"), event.get("attempt_ref"))
            if key in transitions:
                return fail("duplicate_physical_transition")
            transitions[key] = event.get("position_after")
        if len(transitions) != count:
            return fail("missing_physical_transitions")
        for frame in doc["frames"]:
            key = (frame["t_monde"], frame["attempt_ref"])
            if transitions.get(key) != frame["individual_pose"]:
                return fail("engine_position_journal_mismatch")
        outcome["engine_pose_journal_match"] = True
        if step > count:
            return fail("step_outside_recorded_life")
        selected = doc["frames"][step - 1]
        if selected["t_monde"] != step:
            return fail("nonconsecutive_frame_selection")
        outcome.update(
            available=True,
            capture_integrity_verified=True,
            geometry=doc["geometry"],
            frame=selected,
            reason=None,
        )
        return outcome
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, OverflowError):
        return fail("unreadable_or_invalid_engine_evidence")
