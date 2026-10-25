"""#490: adversarial boundaries for operator-only applied sleep decision grouping."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_i1_world_preset import _split_applied_sleep_decisions


def step(t, kind, *, wake=False, reduced=False, primitive="dormir"):
    return {
        "world_step": t,
        "physical_journal_observation": {"primitive": primitive},
        "sleep_custody_observation": {
            "provenance": kind, "woke": wake, "reduced_perception": reduced,
        },
        "autobiographical_sleep_custody_467": {
            "physical_source_refs": (f"command:{t}", f"transition:{t}")
        },
    }


class DecisionBoundaryNegative490(unittest.TestCase):
    def test_contiguous_commands_with_wake_are_two_decisions(self):
        rows = [
            step(1, "ordinary_awake_admission"),
            step(2, "reduced_sleep_continuation", reduced=True),
            step(3, "readmitted_after_wake", wake=True, reduced=True),
            step(4, "reduced_sleep_continuation", reduced=True),
        ]
        groups = _split_applied_sleep_decisions(rows)
        self.assertEqual([g["decision_step"] for g in groups], [1, 3])
        self.assertEqual([g["steps"] for g in groups], [[1, 2], [3, 4]])
        self.assertEqual([len(g["source_refs"]) for g in groups], [4, 4])

    def test_non_sleep_command_cuts_continuation(self):
        rows = [
            step(1, "ordinary_awake_admission"),
            step(2, "not_sleep", primitive="boire"),
            step(3, "reduced_sleep_continuation", reduced=True),
        ]
        with self.assertRaisesRegex(RuntimeError, "unowned"):
            _split_applied_sleep_decisions(rows)

    def test_reduced_continuation_without_decision_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "unowned"):
            _split_applied_sleep_decisions([
                step(1, "reduced_sleep_continuation", reduced=True)
            ])

    def test_reduced_continuation_must_have_reduced_perception_and_no_gap(self):
        with self.assertRaisesRegex(RuntimeError, "reduced"):
            _split_applied_sleep_decisions([
                step(1, "ordinary_awake_admission"),
                step(2, "reduced_sleep_continuation", reduced=False),
            ])
        with self.assertRaisesRegex(RuntimeError, "nonconsecutive"):
            _split_applied_sleep_decisions([
                step(1, "ordinary_awake_admission"),
                step(3, "reduced_sleep_continuation", reduced=True),
            ])

    def test_waking_continuation_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "waking"):
            _split_applied_sleep_decisions([
                step(1, "ordinary_awake_admission"),
                step(2, "reduced_sleep_continuation", reduced=True, wake=True),
            ])

    def test_unproven_readmission_and_reduced_ordinary_rejected(self):
        for wake, reduced in ((False, True), (True, False), (False, False)):
            with self.subTest(wake=wake, reduced=reduced):
                with self.assertRaisesRegex(RuntimeError, "readmission"):
                    _split_applied_sleep_decisions([
                        step(1, "readmitted_after_wake", wake=wake, reduced=reduced)
                    ])
        with self.assertRaisesRegex(RuntimeError, "ordinary"):
            _split_applied_sleep_decisions([
                step(1, "ordinary_awake_admission", reduced=True)
            ])

    def test_unknown_class_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "unknown"):
            _split_applied_sleep_decisions([step(1, "fabricated")])

    def test_no_personal_memory_is_inferred(self):
        self.assertEqual(_split_applied_sleep_decisions([]), [])
        self.assertEqual(_split_applied_sleep_decisions([
            step(1, "not_sleep", primitive="manger")]), [])


if __name__ == "__main__":
    unittest.main()
