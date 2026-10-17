from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lab.events import LabEvent
from lab.sinks import JsonlSink


class JsonlSinkTests(unittest.TestCase):
    def test_sink_writes_valid_json_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            sink = JsonlSink(path)

            sink.emit(LabEvent(run_id="r1", kind="example", cycle=0, data={"value": 1}))

            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ]

            self.assertEqual(
                rows,
                [
                    {
                        "run_id": "r1",
                        "kind": "example",
                        "cycle": 0,
                        "data": {"value": 1},
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
