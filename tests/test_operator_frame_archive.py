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
