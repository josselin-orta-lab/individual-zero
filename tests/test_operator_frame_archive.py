"""Durable operator archive is separate from I0 and never rewinds a life."""
import json
import tempfile
from pathlib import Path

import pytest

from lab.operator_frame_archive import OperatorFrameArchive


def test_append_only_fsync_receipts_and_exclusive_birth():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "frames.jsonl"
        with OperatorFrameArchive(str(path)) as archive:
            archive.append({"frame": {"t_monde": 1, "step_boundary": "committed"}})
            with pytest.raises(ValueError):
                archive.append({"frame": {"t_monde": 1, "step_boundary": "committed"}})
            archive.append({"frame": {"t_monde": 2, "step_boundary": "committed"}})
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        assert [row["frame"]["t_monde"] for row in rows] == [1, 2]
        with pytest.raises(FileExistsError):
            OperatorFrameArchive(str(path))


def test_uncommitted_receipt_rejected():
    with tempfile.TemporaryDirectory() as directory:
        with OperatorFrameArchive(str(Path(directory) / "frames.jsonl")) as archive:
            with pytest.raises(ValueError):
                archive.append({"frame": {"t_monde": 1}})

def test_export_single_attempt_for_observer():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "receipts.jsonl"
        output = Path(directory) / "frames.json"
        with OperatorFrameArchive(str(path)) as archive:
            archive.append({
                "frame": {"t_monde": 1, "step_boundary": "committed",
                          "individual_pose": {"x": 1, "y": 1}, "entities": []},
                "geometry": {"coordinate_system": "grid-xy-top-left",
                             "width": 4, "height": 4},
                "attempt_ref": "attempt-1",
                "journal_head_sha256": "a" * 64,
                "journal_event_count": 3,
            })
        OperatorFrameArchive.export_world_frames(
            str(path), str(output), individual_id="i0", life_generation=0,
        )
        exported = json.loads(output.read_text())
        assert exported["frames"][0]["individual_pose"] == {"x": 1, "y": 1}
        assert exported["attestation"]["verifier"] == "engine-receipt-export-unverified"


def test_export_supports_multiple_attempt_refs():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "receipts.jsonl"
        output = Path(directory) / "frames.json"
        with OperatorFrameArchive(str(path)) as archive:
            for step in (1, 2):
                archive.append({
                    "frame": {"t_monde": step, "step_boundary": "committed",
                              "individual_pose": {"x": 1, "y": 1}, "entities": []},
                    "geometry": {"coordinate_system": "grid-xy-top-left",
                                 "width": 4, "height": 4},
                    "attempt_ref": f"attempt-{step}",
                    "journal_head_sha256": "a" * 64,
                    "journal_event_count": step,
                })
        OperatorFrameArchive.export_world_frames(
                str(path), str(output), individual_id="i0", life_generation=0,
            )
        exported = json.loads(output.read_text())
        assert [f["attempt_ref"] for f in exported["frames"]] == ["attempt-1", "attempt-2"]
