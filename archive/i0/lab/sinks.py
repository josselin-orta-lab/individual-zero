"""Event sinks for Lab observability."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .events import LabEvent


class EventSink(Protocol):
    """Destination for structured Lab events."""

    def emit(self, event: LabEvent) -> None:
        """Store or forward one event."""


class MemorySink:
    """In-memory sink used by tests and small tools."""

    def __init__(self) -> None:
        self.events: list[LabEvent] = []

    def emit(self, event: LabEvent) -> None:
        self.events.append(event)


class JsonlSink:
    """Append one JSON object per line to a local artifact file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def emit(self, event: LabEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.as_dict(), sort_keys=True))
            handle.write("\n")
