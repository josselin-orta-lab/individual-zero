"""#495 negative evidence: waking receipt custody is per exact M11 attempt."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_i1_world_preset import _same_attempt_waking_reentry


def receipts():
    return [
        {"kind": kind, "t_monde": 5, "attempt_ref": "attempt:5"}
        for kind in ("stage10_reduced_capture", "stage10_sleep_woke",
                     "perceptual_capture", "command_experienced")
    ]


def eligible(events):
    return _same_attempt_waking_reentry(
        events=events, reduced=events[0], woke=events[1],
        capture=events[2], command=events[3],
    )


class FirstPersonWakeAttempt495(unittest.TestCase):
    def test_exact_source_order_is_eligible_but_not_a_memory(self):
        self.assertTrue(eligible(receipts()))

    def test_cross_attempt_and_cross_step_are_rejected(self):
        for index in range(3):
            with self.subTest(index=index):
                events = receipts()
                events[index]["attempt_ref"] = "attempt:foreign"
                self.assertFalse(eligible(events))
                events = receipts()
                events[index]["t_monde"] = 4
                self.assertFalse(eligible(events))

    def test_missing_duplicate_or_out_of_order_occurrences_are_rejected(self):
        events = receipts()
        self.assertFalse(_same_attempt_waking_reentry(
            events=events[:-1], reduced=events[0], woke=events[1],
            capture=events[2], command=events[3]))
        events = receipts()
        self.assertFalse(_same_attempt_waking_reentry(
            events=events + [events[1]], reduced=events[0], woke=events[1],
            capture=events[2], command=events[3]))
        events = receipts()
        events[1], events[2] = events[2], events[1]
        self.assertFalse(_same_attempt_waking_reentry(
            events=events, reduced=events[0], woke=events[2],
            capture=events[1], command=events[3]))

    def test_unseen_fabricated_receipt_is_rejected(self):
        events = receipts()
        fake = dict(events[1])
        self.assertFalse(_same_attempt_waking_reentry(
            events=events, reduced=events[0], woke=fake,
            capture=events[2], command=events[3]))


if __name__ == "__main__":
    unittest.main()
