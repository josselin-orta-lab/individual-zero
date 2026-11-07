"""Reference-repertoire Stage-1 branch memory: software only, no life study."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (ACTIONS, BodyLaws, CognitiveBudget, CognitiveWork,
                             debit_cognition)
from i3.modules.personal_outcomes import NoPersonalSupport
from i3.modules.reference_branches import (
    BRANCHES_PER_ACTION, CAPACITY, ReferenceBranchMemory, STORE_WORK)

BODY = (40., 40., 40., 80., 40.)


def budget(body=BODY):
    return CognitiveBudget(body, BodyLaws())


def record(memory, key, delta):
    decision = CognitiveWork(cycles=5, simulated_steps=2, memory_items=3)
    funded, _ = debit_cognition(BODY, BodyLaws(), decision)
    after = tuple(a + d for a, d in zip(funded, delta))
    b = CognitiveBudget(after, BodyLaws())
    memory.observe(key, BODY, decision, b)
    if b.work != STORE_WORK:
        raise AssertionError("unexpected storage work")
    return b


class ReferenceBranchMemoryTests(unittest.TestCase):
    def test_fixed_global_capacity_is_three_per_primitive_action_class(self):
        m = ReferenceBranchMemory()
        self.assertEqual(BRANCHES_PER_ACTION, 3)
        self.assertEqual(CAPACITY, 3 * len(ACTIONS))
        self.assertEqual(CAPACITY, 18)
        self.assertEqual(m._samples.maxlen, 18)
        self.assertEqual(len(m._samples), 0)

    def test_module_import_is_detached_from_runtime_and_world(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.modules.reference_branches import ReferenceBranchMemory; "
            "ReferenceBranchMemory(); "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules"
        ], check=True)

    def test_empty_support_is_not_a_zero_prior_and_scan_is_paid(self):
        m, b, receipt = ReferenceBranchMemory(), budget(), {}
        with self.assertRaises(NoPersonalSupport):
            m.branches(("boire", None), b, work_receipt=receipt)
        self.assertEqual(
            b.work, CognitiveWork(cycles=1, memory_items=2))
        self.assertEqual(receipt["status"], "NO_SUPPORT")
        self.assertEqual(receipt["access"], "direct_scan")
        self.assertEqual(receipt["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 2, "replays": 0})

    def test_internal_read_error_is_not_mislabeled_as_missing_support(self):
        m, b, receipt = ReferenceBranchMemory(), budget(), {}
        with patch.object(m, "_supports", side_effect=RuntimeError("broken read")):
            with self.assertRaisesRegex(RuntimeError, "broken read"):
                m.branches(("boire", None), b, work_receipt=receipt)
        self.assertEqual(
            b.work, CognitiveWork(cycles=1, memory_items=2))
        self.assertEqual(receipt, {})

    def test_exact_recent_support_precedes_same_action_fallback(self):
        m = ReferenceBranchMemory()
        record(m, ("manger", "a"), (0., 1., 0., 0., 0.))
        record(m, ("manger", "b"), (0., 2., 0., 0., 0.))
        record(m, ("manger", "a"), (0., 3., 0., 0., 0.))
        record(m, ("manger", "b"), (0., 4., 0., 0., 0.))
        record(m, ("manger", "a"), (0., 5., 0., 0., 0.))
        exact = m.branches(("manger", "a"), budget())
        fallback = m.branches(("manger", "new"), budget())
        self.assertEqual([round(x[1], 9) for x in exact], [1., 3., 5.])
        self.assertEqual([round(x[1], 9) for x in fallback], [3., 4., 5.])

    def test_many_token_names_cannot_grow_memory(self):
        m = ReferenceBranchMemory()
        for i in range(24):
            record(m, ("collecter", f"tok{i}"), (0., float(i), 0., 0., 0.))
        self.assertEqual(len(m._samples), CAPACITY)
        rows = m.branches(("collecter", "unseen"), budget())
        self.assertEqual([round(x[1], 9) for x in rows], [21., 22., 23.])

    def test_paid_read_cost_tracks_retained_ring_not_token_namespace(self):
        m = ReferenceBranchMemory()
        record(m, ("boire", None), (0., 0., 4., 0., 0.))
        record(m, ("boire", None), (0., 0., 6., 0., 0.))
        b, receipt = budget(), {}
        rows = m.branches(("boire", None), b, work_receipt=receipt)
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            b.work, CognitiveWork(cycles=1, memory_items=16))
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertEqual(receipt["branches"], 2)

    def test_decision_local_index_reuses_scan_but_lookups_stay_paid(self):
        m = ReferenceBranchMemory()
        record(m, ("boire", None), (0., 0., 4., 0., 0.))
        record(m, ("attendre", None), (0., -.2, -.4, 0., 0.))
        index = m.begin_support_index()
        first_budget, first_receipt = budget(), {}
        m.branches(("boire", None), first_budget,
                   support_index=index, work_receipt=first_receipt)
        self.assertEqual(first_receipt["access"], "shared_scan")
        self.assertEqual(
            first_budget.work, CognitiveWork(cycles=1, memory_items=16))

        second_budget, second_receipt = budget(), {}
        m.branches(("attendre", None), second_budget,
                   support_index=index, work_receipt=second_receipt)
        self.assertEqual(second_receipt["access"], "indexed_lookup")
        self.assertEqual(
            second_budget.work, CognitiveWork(cycles=1, memory_items=2))

        record(m, ("dormir", None), (2., -.2, -.4, 0., 3.))
        stale = budget()
        with self.assertRaises(ValueError):
            m.branches(("boire", None), stale, support_index=index)
        self.assertEqual(stale.work, CognitiveWork())

    def test_opaque_token_renaming_preserves_branch_arithmetic(self):
        a, b = ReferenceBranchMemory(), ReferenceBranchMemory()
        for amount in (-7., 3., 11.):
            record(a, ("manger", "tokA"), (0., amount, 0., -1., 0.))
            record(b, ("manger", "renamed"), (0., amount, 0., -1., 0.))
        ba, bb = budget(), budget()
        ra = a.branches(("manger", "tokA"), ba)
        rb = b.branches(("manger", "renamed"), bb)
        for xa, xb in zip(ra, rb):
            for va, vb in zip(xa, xb):
                self.assertAlmostEqual(va, vb)
        self.assertEqual(ba.work, bb.work)

    def test_no_read_after_physical_death(self):
        m = ReferenceBranchMemory()
        b = budget((40., 0., 40., 80., 40.))
        with self.assertRaises(ValueError):
            m.branches(("attendre", None), b)
        self.assertEqual(b.work, CognitiveWork())

    def test_substrate_is_not_a_runtime_policy(self):
        from i3.runtime.life import run_life
        with self.assertRaisesRegex(ValueError, "unknown decision policy"):
            run_life({}, None, 1, 1, decision_policy="reference_information_v1")


if __name__ == "__main__":
    unittest.main()
