"""Derived, operator-only closed-source index for the I1 M11 world observer.

This is never a Memory owner, a causal state, an input to I1, or a
replacement for independent cold SQLite/journal verification.
"""

class ClosedSourceOccurrenceIndex:
    def __init__(self):
        self._occurrences = {}
        self._episode_count = 0
        self.inspected_refs = 0

    def before_step(self, *, episode_count):
        if type(episode_count) is not int or episode_count != self._episode_count:
            raise RuntimeError("incremental M11 closed-episode count drift")
        # The M11 runner consults this mapping only before extend_committed(),
        # and _closed_custody_at_sleep_recall creates its own working copy.
        return self._occurrences

    def extend_committed(self, newly_closed):
        # The caller must invoke this ONLY after auditing an authentically
        # committed M11 generation, never during the private staging step.
        for episode in newly_closed:
            for ref in episode["event_refs"]:
                self._occurrences[ref] = self._occurrences.get(ref, 0) + 1
                self.inspected_refs += 1
            self._episode_count += 1

    @property
    def episode_count(self):
        return self._episode_count
