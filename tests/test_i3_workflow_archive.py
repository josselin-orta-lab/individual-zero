"""Static custody guard for I3's retired, already-disabled one-shot jobs.

No World, life, cognition, original receipt or scientific experiment executes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / ".github/workflows/i3-proposal-checks.yml"
ARCHIVED = ROOT / "archive/i3/workflows/i3-proposal-checks-original-2026-11-16.yml"
ORIGINAL_BLOB = "370f34867330bce828d5de03135bb4f801917641"
RETIRED = (
    "b1-original-custody",
    "stage2-three-arm-exploratory-once",
    "stage2-content-48-exploratory-once",
    "stage2-water-divergence-24-once",
    "stage2-realstate-fork-24-exploratory-once",
    "stage2-next-decision-24-exploratory-once",
)


def parts(data: str) -> tuple[str, dict[str, str]]:
    before, divider, body = data.partition("\njobs:\n")
    if not divider:
        raise AssertionError("missing jobs key")
    matches = list(re.finditer(r"(?m)^  ([a-zA-Z0-9_-]+):[ \t]*$", body))
    if not matches:
        raise AssertionError("no jobs discovered")
    result = {}
    for i, match in enumerate(matches):
        name = match.group(1)
        if name in result:
            raise AssertionError("duplicate job name: " + name)
        result[name] = body[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(body)]
    return before, result


class I3WorkflowRetirement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = ARCHIVED.read_bytes()
        cls.archived_text = cls.original.decode("utf-8")
        cls.live_text = LIVE.read_text(encoding="utf-8")
        cls.header_archive, cls.archive_jobs = parts(cls.archived_text)
        cls.header_live, cls.live_jobs = parts(cls.live_text)

    def test_original_source_git_blob_is_unchanged(self):
        blob = b"blob " + str(len(self.original)).encode("ascii") + b"\x00" + self.original
        self.assertEqual(hashlib.sha1(blob).hexdigest(), ORIGINAL_BLOB)
        self.assertEqual(len(self.archive_jobs), 28)
        self.assertEqual(len(self.live_jobs), 22)
        self.assertFalse(ARCHIVED.is_symlink())
        self.assertTrue(ARCHIVED.is_relative_to(ROOT / "archive"))
        self.assertFalse(ARCHIVED.is_relative_to(ROOT / ".github/workflows"))

    def test_original_events_permissions_and_cancellation_are_unchanged(self):
        self.assertEqual(self.header_live, self.header_archive)
        for phrase in (
            "    branches: [main, 'i3/**']",
            "    branches: [main]",
            "      - 'src/i3/docs/studies/stage2-replay-gate-selected-design/B1_ARCHIVE_ONCE.json'",
            "      - 'src/i3/docs/studies/stage2-replay-gate-selected-design/NEXT_DECISION_24_LAUNCH_ONCE.json'",
            "  contents: read",
            "  cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
        ):
            self.assertIn(phrase, self.header_live)
        self.assertNotIn("workflow_dispatch:", self.header_live)

    def test_only_six_originally_disabled_one_shots_were_removed(self):
        self.assertEqual(set(self.archive_jobs) - set(self.live_jobs), set(RETIRED))
        self.assertEqual(set(self.live_jobs) - set(self.archive_jobs), set())
        self.assertEqual(list(self.live_jobs),
                         [k for k in self.archive_jobs if k not in RETIRED])
        for name in RETIRED:
            self.assertRegex(self.archive_jobs[name], r"(?m)^    if: false$")
            self.assertNotIn(name, self.live_jobs)
        for name, content in self.live_jobs.items():
            with self.subTest(job=name):
                self.assertEqual(content, self.archive_jobs[name],
                                 "surviving job differs from frozen source")

    def test_remaining_jobs_cannot_dispatch_on_historical_main_push(self):
        self.assertIn("python-version: ['3.11', '3.12']", self.live_jobs["software"])
        self.assertIn("ref: ${{ github.event.pull_request.head.sha }}",
                      self.live_jobs["software"])
        self.assertIn("python -m unittest discover -s tests/i3 -p 'test_*.py' -v",
                      self.live_jobs["software"])
        for name, job in self.live_jobs.items():
            match = re.search(r"(?m)^    if: (.+)$", job)
            self.assertIsNotNone(match, name + ": missing explicit execution gate")
            condition = match.group(1)
            self.assertTrue(
                condition == "github.event_name == 'pull_request'"
                or condition.startswith("startsWith(github.head_ref, 'research/i3-"),
                name + ": unexpected auto-execution condition: " + condition,
            )
            self.assertNotIn("github.event_name == 'push'", condition)


if __name__ == "__main__":
    unittest.main()
