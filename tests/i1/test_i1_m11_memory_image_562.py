"""#562: independent, observer-only committed Memory export reuse tests."""
import sys
from pathlib import Path
from copy import deepcopy
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from i1_m11_memory_image import CommittedMemoryImage


class FakeMemory:
    def __init__(self):
        self.state = {"episodes": [], "seen_event_refs": [],
                      "last_recalled_ref": None}
        self.exports = 0

    @property
    def episode_count(self):
        return len(self.state["episodes"])

    def export_causal_state(self):
        self.exports += 1
        return deepcopy(self.state)


class CommittedMemoryImage562(unittest.TestCase):
    def test_reuses_previous_detached_post_step_without_extra_export(self):
        owner, observer = FakeMemory(), CommittedMemoryImage()
        before = observer.before_step(owner, episode_count=0)
        self.assertEqual(owner.exports, 1)
        owner.state["episodes"].append({"id": "episode:0", "event_refs": ["a"]})
        owner.state["seen_event_refs"].append("a")
        after = observer.after_step(owner, episode_count=0)
        self.assertEqual(owner.exports, 2)
        self.assertEqual(before["episodes"], [])
        self.assertEqual(after["seen_event_refs"], ["a"])
        owner.state["episodes"][0]["event_refs"].append("new owner ref")
        owner.state["seen_event_refs"].append("uncommitted")
        cached = observer.before_step(owner, episode_count=1)
        self.assertIs(cached, after)
        self.assertEqual(owner.exports, 2)
        self.assertEqual(cached["episodes"][0]["event_refs"], ["a"])
        self.assertEqual(cached["seen_event_refs"], ["a"])
        self.assertEqual(observer.export_calls, 2)
        self.assertEqual(observer.exported_episode_rows, 1)
        self.assertEqual(observer.exported_seen_refs, 1)

    def test_growth_reduces_exports_without_changing_all_step_images(self):
        owner, observer = FakeMemory(), CommittedMemoryImage()
        for step in range(1, 9):
            expected_before = owner.export_causal_state()
            before = observer.before_step(owner, episode_count=step - 1)
            self.assertEqual(before, expected_before)
            owner.state["episodes"].append(
                {"id": f"episode:{step-1}", "event_refs": [f"src:{step}"]})
            owner.state["seen_event_refs"].append(f"src:{step}")
            expected_after = owner.export_causal_state()
            after = observer.after_step(owner, episode_count=step - 1)
            self.assertEqual(after, expected_after)
        self.assertEqual(observer.export_calls, 9)
        self.assertEqual(observer.exported_episode_rows, sum(range(9)))
        self.assertEqual(observer.exported_seen_refs, sum(range(9)))

    def test_count_drift_and_invalid_export_fail_closed(self):
        owner, observer = FakeMemory(), CommittedMemoryImage()
        with self.assertRaises(RuntimeError):
            observer.before_step(owner, episode_count=1)
        observer.before_step(owner, episode_count=0)
        owner.state["episodes"].append({"id": "episode:0", "event_refs": []})
        observer.after_step(owner, episode_count=0)
        with self.assertRaises(RuntimeError):
            observer.before_step(owner, episode_count=0)
        owner.state["episodes"].clear()
        with self.assertRaises(RuntimeError):
            observer.after_step(owner, episode_count=1)
        self.assertEqual(len(observer._last_post_step["episodes"]), 1)

    def test_invalid_owner_image_does_not_advance_cache(self):
        owner, observer = FakeMemory(), CommittedMemoryImage()
        observer.before_step(owner, episode_count=0)
        owner.state["episodes"].append({"id": "episode:0", "event_refs": []})
        accepted = observer.after_step(owner, episode_count=0)
        owner.state["seen_event_refs"] = "invalid shape"
        with self.assertRaises(RuntimeError):
            observer.after_step(owner, episode_count=1)
        self.assertIs(observer._last_post_step, accepted)


if __name__ == "__main__":
    unittest.main()
