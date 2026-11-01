"""Negative contracts for post hoc A1-C bias trace, no births."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "research"))
from i1_a1c_td_bias import reconstruct_bias_updates


def update(step, signature, n, delta, signatures):
    return {"kind": "td_update_published", "t_monde": step,
            "data": {"previous_signature": signature,
                     "segment_length": n, "delta": delta,
                     "updated_signatures": signatures}}


class TestA1CBiasTD(unittest.TestCase):
    def test_one_step_and_delayed_bias_math(self):
        events = [update(2, "collect", 1, 1, ["collect"]),
                  update(3, "manger", 1, 2, ["collect", "manger"]),
                  update(5, "other", 2, -1, ["collect", "manger", "other"])]
        rows = reconstruct_bias_updates(
            events, beta=.8, lambda_e=.8, eta=.05)
        self.assertAlmostEqual(rows[1]["trace_bias"]["collect"], .64)
        self.assertAlmostEqual(
            rows[1]["bias_weight_increment"]["collect"], .064)
        self.assertAlmostEqual(rows[2]["trace_bias"]["collect"], .64 ** 3)

    def test_signed_credit_is_not_always_rewarding(self):
        rows = reconstruct_bias_updates(
            [update(2, "collect", 1, 1, ["collect"]),
             update(3, "manger", 1, -4, ["collect", "manger"])],
            beta=.8, lambda_e=.8, eta=.05)
        self.assertGreater(rows[1]["trace_bias"]["collect"], 0)
        self.assertLess(rows[1]["bias_weight_increment"]["collect"], 0)

    def test_contradictory_M11_signatures_fail(self):
        for bad in (["manger"], ["collect", "manger", "alien"],
                    ["collect", "manger", "manger"]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reconstruct_bias_updates(
                    [update(2, "collect", 1, 1, ["collect"]),
                     update(3, "manger", 1, 1, bad)],
                    beta=.8, lambda_e=.8, eta=.05)

    def test_bad_lengths_coefficients_and_delta_fail(self):
        for n in (0, -1, 1.5, True):
            with self.subTest(n=n), self.assertRaises(ValueError):
                reconstruct_bias_updates(
                    [update(2, "collect", n, 1, ["collect"])],
                    beta=.8, lambda_e=.8, eta=.05)
        for kwargs in ({"beta":1,"lambda_e":.8,"eta":.05},
                       {"beta":.8,"lambda_e":1.1,"eta":.05},
                       {"beta":.8,"lambda_e":.8,"eta":0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                reconstruct_bias_updates([], **kwargs)
        with self.assertRaises(ValueError):
            reconstruct_bias_updates(
                [update(2, "collect", 1, float("nan"), ["collect"])],
                beta=.8, lambda_e=.8, eta=.05)


if __name__ == "__main__":
    unittest.main()
