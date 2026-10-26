"""Derived, operator-only closed-source index for the I1 M11 world observer.

This is never a Memory owner, a causal state, an input to I1, or a
replacement for independent cold SQLite/journal verification.
"""

from types import MappingProxyType


class ClosedSourceOccurrenceIndex:
    def __init__(self):
        self._occurrences = {}
        # Read-only, zero-copy view; updates happen AFTER current-step audits.
        self._view = MappingProxyType(self._occurrences)
        self._episode_count = 0
        self._episode_ids = set()
        self.inspected_refs = 0

    def before_step(self, *, episode_count):
        if type(episode_count) is not int or episode_count != self._episode_count:
            raise RuntimeError("incremental M11 closed-episode count drift")
        # A live view, not a snapshot: the runner finishes all audits BEFORE
        # extend_committed(). No caller can mutate this index.
        return self._view

    def extend_committed(self, newly_closed):
        # The caller must invoke this ONLY after auditing an authentically
        # committed M11 generation, never during the private staging step.
        # Check the *whole* new batch before publishing any mutation, keeping
        # an invalid generation from corrupting a valid observer index.
        ids = set()
        refs = []
        for episode in newly_closed:
            if (type(episode) is not dict
                    or type(episode.get("id")) is not str
                    or not episode["id"].startswith("episode:")
                    or episode["id"] in self._episode_ids
                    or episode["id"] in ids
                    or type(episode.get("event_refs")) not in (list, tuple)):
                raise ValueError("invalid newly closed M11 episode")
            ids.add(episode["id"])
            for ref in episode["event_refs"]:
                if type(ref) is not str or not ref:
                    raise ValueError("invalid closed M11 source reference")
                refs.append(ref)
        for ref in refs:
            self._occurrences[ref] = self._occurrences.get(ref, 0) + 1
        self._episode_ids.update(ids)
        self._episode_count += len(ids)
        self.inspected_refs += len(refs)

    @property
    def episode_count(self):
        return self._episode_count
