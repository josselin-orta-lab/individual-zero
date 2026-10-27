"""Committed Memory images for the external M11 world observer (#562).

This is NOT a cognitive owner or an M11 recovery cache. The external observer
uses the detached, post-commit Memory export of generation N as its pre-step
reference for generation N+1. No runtime, UC, journal or persistence changes.
The runner retains its independent cold SQLite audit and final Memory export.
"""


class CommittedMemoryImage:
    def __init__(self):
        self._last_post_step = None
        # Operator-only operation counts, never included in I1 life reports.
        self.export_calls = 0
        self.exported_episode_rows = 0
        self.exported_seen_refs = 0

    def _export(self, owner):
        image = owner.export_causal_state()
        if (type(image) is not dict
                or type(image.get("episodes")) is not list
                or type(image.get("seen_event_refs")) is not list):
            raise RuntimeError("malformed M11 observer Memory image")
        if len(image["episodes"]) != owner.episode_count:
            raise RuntimeError("M11 observer Memory export/owner count drift")
        self.export_calls += 1
        self.exported_episode_rows += len(image["episodes"])
        self.exported_seen_refs += len(image["seen_event_refs"])
        return image

    def before_step(self, owner, *, episode_count):
        if (type(episode_count) is not int or episode_count < 0
                or owner.episode_count != episode_count):
            raise RuntimeError("M11 observer pre-step episode count drift")
        if self._last_post_step is None:
            # The first genuine birth has no previously committed step.
            return self._export(owner)
        if len(self._last_post_step["episodes"]) != episode_count:
            raise RuntimeError("M11 observer cached Memory count drift")
        # The previous image is detached by Memory.export_causal_state().
        # Nothing between committed steps writes to the Memory owner.
        return self._last_post_step

    def after_step(self, owner, *, episode_count):
        if type(episode_count) is not int or episode_count < 0:
            raise RuntimeError("invalid M11 pre-step episode count")
        image = self._export(owner)
        if len(image["episodes"]) < episode_count:
            raise RuntimeError("M11 observer Memory episode count regressed")
        # Install only after a complete, validated owner export.
        self._last_post_step = image
        return image
