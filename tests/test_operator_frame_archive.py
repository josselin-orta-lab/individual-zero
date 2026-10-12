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
                    "journal_event_count": step + 2,
                })
        OperatorFrameArchive.export_world_frames(
                str(path), str(output), individual_id="i0", life_generation=0,
            )
        exported = json.loads(output.read_text())
        assert [f["attempt_ref"] for f in exported["frames"]] == ["attempt-1", "attempt-2"]


def test_export_rejects_regressing_journal_counts():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "receipts.jsonl"
        output = Path(directory) / "frames.json"
        with OperatorFrameArchive(str(path)) as archive:
            for step, count in ((1, 4), (2, 3)):
                archive.append({
                    "frame": {"t_monde": step, "step_boundary": "committed",
                              "individual_pose": {"x": 1, "y": 1}, "entities": []},
                    "geometry": {"coordinate_system": "grid-xy-top-left",
                                 "width": 4, "height": 4},
                    "attempt_ref": f"attempt-{step}",
                    "journal_head_sha256": "a" * 64,
                    "journal_event_count": count,
                })
        with pytest.raises(ValueError, match="nonmonotonic"):
            OperatorFrameArchive.export_world_frames(
                str(path), str(output), individual_id="i0", life_generation=0)
        assert not output.exists()


def test_export_rejects_duplicate_json_keys_before_export():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "receipts.jsonl"
        output = Path(directory) / "frames.json"
        path.write_bytes(b'{"frame":{},"frame":{}}\n')
        with pytest.raises(ValueError, match="duplicate operator receipt key"):
            OperatorFrameArchive.export_world_frames(
                str(path), str(output), individual_id="i0", life_generation=0)
        assert not output.exists()


def test_verified_export_rejects_receipt_with_wrong_closure_hash():
    import hashlib
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        journal = root / "journal"
        receipts = root / "receipts.jsonl"
        output = root / "frames.json"
        previous = "00" * 32
        rows = []
        for index, kind in enumerate(("step_opened", "step_closed")):
            event = {"kind": kind, "t_monde": 1, "attempt_ref": "a"}
            eid = f"e{index}"
            payload = json.dumps({"event_id": eid, "causal_event": event},
                                 sort_keys=True, separators=(",", ":")).encode()
            digest = hashlib.sha256(bytes.fromhex(previous) + payload).hexdigest()
            rows.append({"index": index, "event_id": eid, "previous_hash": previous,
                         "event_hash": digest, "causal_event": event})
            previous = digest
        journal.write_bytes(b"\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
                                       for row in rows))
        with OperatorFrameArchive(str(receipts)) as archive:
            archive.append({
                "frame": {"t_monde": 1, "step_boundary": "committed",
                          "individual_pose": {"x": 1, "y": 1}, "entities": []},
                "geometry": {"coordinate_system": "grid-xy-top-left",
                             "width": 4, "height": 4},
                "attempt_ref": "a",
                "journal_closure_hash": "f" * 64,
                "journal_head_sha256": previous,
                "journal_event_count": 2,
            })
        with pytest.raises(ValueError, match="does not match journal closure"):
            OperatorFrameArchive.export_world_frames(
                str(receipts), str(output), individual_id="i0", life_generation=0,
                journal_path=str(journal))
        assert not output.exists()
