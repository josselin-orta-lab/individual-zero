"""Focused no-World future prequential custody admission and negative controls."""
import copy
import json
import math
import unittest
from unittest.mock import patch

from i3.lab.stage2_future_prequential_custody import FuturePrequentialCustody
from i3.modules.mind import Mind
from i3.modules.world import World


SOURCE_SHA = "b" * 64
ZERO = [0., 0., 0., 0., 0.]
ONE = [0., 0., 1., 0., 0.]


def ledger(ids=("a", "b")):
    return FuturePrequentialCustody(ids, source_sha256=SOURCE_SHA)


def settle_one(store, identity, *, baseline=None, candidate=None, actual=None, step=1):
    token = store.freeze(identity, step=step,
                         baseline_forecast=ZERO if baseline is None else baseline,
                         candidate_forecast=ONE if candidate is None else candidate)
    return store.settle(identity, frozen_sha256=token,
                        actual_delta=ONE if actual is None else actual)


class FuturePrequentialCustodyTests(unittest.TestCase):
    def test_all_assigned_nulls_and_adverse_units_are_retained(self):
        ids = ["gain", "harm", "unsupported", "denied", "death", "censored"]
        with patch.object(World, "__init__",
                          side_effect=AssertionError("never construct World")), patch.object(
                              Mind, "decide", side_effect=AssertionError("never run Mind")):
            store = ledger(ids)
            settle_one(store, "gain")
            store.close("gain", reason="COMPLETE")
            settle_one(store, "harm", actual=ZERO)
            store.close("harm", reason="COMPLETE")
            store.close("unsupported", reason="NO_PERSONAL_SUPPORT")
            store.close("denied", reason="DENIED_FUNDING")
            t = store.freeze("death", step=1, baseline_forecast=ZERO,
                             candidate_forecast=ONE)
            store.close("death", reason="DEAD_BEFORE_OPPORTUNITY",
                        frozen_sha256=t)
            t = store.freeze("censored", step=1, baseline_forecast=ONE,
                             candidate_forecast=ZERO)
            store.close("censored", reason="RIGHT_CENSORED", frozen_sha256=t)
            result = store.report()
        self.assertEqual(result["assigned_units"], 6)
        self.assertEqual(result["scored_units"], 2)
        self.assertEqual(result["never_scored_units"], 4)
        self.assertEqual(result["scored_events"], 2)
        self.assertEqual(result["censored_pending_events"], 2)
        self.assertEqual(sum(result["closures"].values()), 6)
        self.assertEqual(result["descriptive_candidate_better_units"], 1)
        self.assertEqual(result["descriptive_candidate_worse_units"], 1)
        self.assertEqual(result["descriptive_mean_of_unit_mean_mse_difference"], 0.)
        self.assertEqual(result["scientific_worlds"], 0)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(result["externally_authenticated_preoutcome_order"])
        self.assertFalse(result["real_world_paid_forecasts"])
        print("I3_FUTURE_PREQUENTIAL_CUSTODY=" +
              json.dumps(result, sort_keys=True, separators=(",", ":"),
                         allow_nan=False))

    def test_freeze_is_required_and_caller_mutation_does_not_change_forecast(self):
        store = ledger(["a"])
        with self.assertRaisesRegex(ValueError, "no open frozen"):
            store.settle("a", frozen_sha256="f"*64, actual_delta=ONE)
        b, c = ZERO.copy(), ONE.copy()
        token = store.freeze("a", step=1, baseline_forecast=b,
                             candidate_forecast=c)
        b[2] = 50.
        c[2] = -50.
        with self.assertRaisesRegex(ValueError, "wrong pre-outcome"):
            store.settle("a", frozen_sha256="a"*64, actual_delta=ONE)
        store.settle("a", frozen_sha256=token, actual_delta=ONE)
        store.close("a", reason="COMPLETE")
        self.assertAlmostEqual(store.report()["units"][0]["mean_baseline_mse"], .2)
        self.assertAlmostEqual(store.report()["units"][0]["mean_candidate_mse"], 0.)

    def test_serial_events_do_not_create_fake_independent_units(self):
        store = ledger(["one", "unobserved"])
        for step in range(1, 6):
            settle_one(store, "one", step=step, actual=ONE if step != 5 else ZERO)
        store.close("one", reason="RIGHT_CENSORED")
        store.close("unobserved", reason="DEAD_BEFORE_OPPORTUNITY")
        result=store.report()
        self.assertEqual(result["assigned_units"],2)
        self.assertEqual(result["scored_units"],1)
        self.assertEqual(result["scored_events"],5)
        self.assertEqual(result["descriptive_candidate_better_units"],1)
        self.assertEqual(result["descriptive_candidate_worse_units"],0)
        self.assertEqual(result["units"][0]["scored_events"],5)
        self.assertAlmostEqual(result["units"][0]["worst_candidate_event_mse"], .2)
        self.assertAlmostEqual(result["units"][0]["worst_baseline_event_mse"], .2)

    def test_censor_never_imputes_zero_loss_or_an_unseen_outcome(self):
        store = ledger(["a"])
        token = store.freeze("a", step=1, baseline_forecast=ZERO,
                             candidate_forecast=ONE)
        with self.assertRaises(ValueError):
            store.close("a", reason="COMPLETE", frozen_sha256=token)
        with self.assertRaises(ValueError):
            store.close("a", reason="NO_PERSONAL_SUPPORT", frozen_sha256=token)
        with self.assertRaises(ValueError):
            store.close("a", reason="RIGHT_CENSORED", frozen_sha256="f"*64)
        store.close("a", reason="RIGHT_CENSORED", frozen_sha256=token)
        row = store.report()["units"][0]
        self.assertEqual(row["scored_events"],0)
        self.assertIsNone(row["mean_candidate_mse"])
        self.assertIsNone(row["mean_baseline_mse"])
        self.assertEqual(row["unscored_pending"]["frozen_sha256"], token)
        self.assertIsNone(row["unscored_pending"]["actual_delta"])
        self.assertIsNone(row["unscored_pending"]["loss"])

    def test_strict_sequence_no_replay_no_postclosure_no_cherrypick(self):
        store = ledger(["a","b"])
        with self.assertRaises(ValueError):
            store.report()
        with self.assertRaises(ValueError):
            store.freeze("a", step=2, baseline_forecast=ZERO,
                         candidate_forecast=ONE)
        token=store.freeze("a", step=1, baseline_forecast=ZERO,
                           candidate_forecast=ONE)
        with self.assertRaises(ValueError):
            store.freeze("a", step=1, baseline_forecast=ZERO,
                         candidate_forecast=ONE)
        store.settle("a", frozen_sha256=token, actual_delta=ONE)
        with self.assertRaises(ValueError):
            store.settle("a", frozen_sha256=token, actual_delta=ONE)
        with self.assertRaises(ValueError):
            store.report()  # 'b' must remain in denominator
        store.close("a", reason="COMPLETE")
        store.close("b", reason="DENIED_FUNDING")
        with self.assertRaises(ValueError):
            store.close("b", reason="DENIED_FUNDING")
        with self.assertRaises(ValueError):
            store.freeze("a", step=2, baseline_forecast=ZERO,
                         candidate_forecast=ONE)
        with self.assertRaises(ValueError):
            store.settle("b", frozen_sha256=token, actual_delta=ONE)
        self.assertEqual(store.report()["assigned_units"], 2)

    def test_bad_source_assignments_outcomes_and_types_rejected(self):
        for src in ("b"*63, "B"*64, "g"*64, None, 2):
            with self.subTest(src=src), self.assertRaises(ValueError):
                FuturePrequentialCustody(["a"], source_sha256=src)
        for ids in ([], ("a","a"), ("",), ("a b",), ("a",True), "a"):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                FuturePrequentialCustody(ids, source_sha256=SOURCE_SHA)
        store=ledger(["a"])
        for bad in ([], [0.]*4, [True]*5, [float("nan")]*5,
                    [float("inf")]*5, [101.]*5, [-101.]*5, "0"*5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                store.freeze("a", step=1, baseline_forecast=bad,
                             candidate_forecast=ONE)
        for step in (0, 1.0, True, 3):
            with self.subTest(step=step), self.assertRaises(ValueError):
                store.freeze("a", step=step, baseline_forecast=ZERO,
                             candidate_forecast=ONE)
        t=store.freeze("a", step=1, baseline_forecast=ZERO,
                       candidate_forecast=ONE)
        for bad in (["nan",0,0,0,0], [float("nan")]*5, [-200.]*5):
            with self.subTest(actual=bad), self.assertRaises(ValueError):
                store.settle("a", frozen_sha256=t, actual_delta=bad)
        store.settle("a", frozen_sha256=t, actual_delta=ONE)
        store.close("a", reason="COMPLETE")

    def test_equal_prediction_negative_control_and_no_positive_conclusion(self):
        store=ledger(["same", "null"])
        t=store.freeze("same", step=1, baseline_forecast=ONE,
                       candidate_forecast=ONE)
        store.settle("same", frozen_sha256=t, actual_delta=ZERO)
        store.close("same", reason="COMPLETE")
        store.close("null", reason="NO_PERSONAL_SUPPORT")
        result=store.report()
        self.assertEqual(result["descriptive_tie_units"],1)
        self.assertEqual(result["descriptive_candidate_better_units"],0)
        self.assertEqual(result["descriptive_candidate_worse_units"],0)
        self.assertIsNone(result["units"][1]["mean_candidate_mse"])
        self.assertTrue(result["unit_draw_independence_not_established"])
        self.assertEqual(result["status"],
                         "SOFTWARE_PREQUENTIAL_CUSTODY_READY_NO_EFFICACY_VERDICT")

    def test_deterministic_identical_ledgers_and_digest_chain(self):
        def make():
            s=ledger(["a","b"])
            t=s.freeze("a", step=1, baseline_forecast=ZERO,
                       candidate_forecast=ONE)
            h=s.settle("a", frozen_sha256=t, actual_delta=ONE)
            s.close("a", reason="COMPLETE")
            s.close("b", reason="NO_PERSONAL_SUPPORT")
            return t,h,s.report()
        self.assertEqual(make(),make())
        self.assertEqual(len(make()[0]),64)
        self.assertEqual(len(make()[1]),64)
        self.assertEqual(len(make()[2]["deterministic_sha256"]),64)


if __name__ == "__main__":
    unittest.main()
