"""Fail-closed tests for the ECO-v1 operator-only score, no I1 birth."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from i1_eco_metrics import evaluate_life, NEEDS


def body(energy=70, food=35, water=35, integrity=85):
    return dict(energy=energy, food=food, water=water, integrity=integrity)


SETPOINTS = dict.fromkeys(NEEDS, 60.)
SCALES = dict.fromkeys(NEEDS, 60.)


def evaluate(steps, horizon, status, **changes):
    params = dict(initial_body=body(), steps=steps, horizon=horizon,
                  status=status, setpoints=SETPOINTS, scales=SCALES)
    params.update(changes)
    return evaluate_life(**params)


class EcoV1MetricsTests(unittest.TestCase):
    def test_dead_life_pays_full_deficit_after_terminal_step(self):
        a = [
            {"step": 1, "body": body(60, 60, 60, 60),
             "action": "attendre", "status": "active"},
            {"step": 2, "body": body(0, 0, 0, 0),
             "action": "attendre", "status": "dead"},
        ]
        v = evaluate(a, 5, "dead")
        self.assertEqual(v["restricted_life_steps"], 2)
        self.assertTrue(v["mortality"])
        self.assertFalse(v["censored"])
        self.assertEqual(v["deficit_area_by_need"], dict.fromkeys(NEEDS, 4.))
        self.assertEqual(v["deficit_area_total"], 16.)
        self.assertEqual(v["adaptive_benefit"], "NOT_ESTABLISHED")

    def test_complete_live_life_has_no_postdeath_penalty(self):
        a = [
            {"step": 1, "body": body(60, 60, 60, 60),
             "action": "manger", "status": "active"},
            {"step": 2, "body": body(60, 60, 60, 60),
             "action": "dormir", "status": "active"},
        ]
        v = evaluate(a, 2, "active")
        self.assertTrue(v["censored"])
        self.assertEqual(v["deficit_area_total"], 0.)
        self.assertEqual(v["sleep_fraction"], 0.5)
        self.assertEqual(v["productive_actions"]["manger"], 1)
        self.assertEqual(v["learning_use_causal"], "NOT_ESTABLISHED")

    def test_excess_above_setpoint_not_penalized_in_deficit_metric(self):
        a = [{"step": 1, "body": body(100, 100, 100, 100),
              "action": "boire", "status": "active"}]
        self.assertEqual(evaluate(a, 1, "active")["deficit_area_total"], 0.)

    def test_invalid_lives_fail_closed(self):
        dead = {"step": 1, "body": body(), "action": "attendre", "status": "dead"}
        alive = {"step": 1, "body": body(), "action": "attendre", "status": "active"}
        invalid = [
            ([alive], 2, "active", {}),
            ([dead, {**alive, "step": 2}], 2, "active", {}),
            ([{**alive, "step": 2}], 2, "active", {}),
            ([{**alive, "action": "forced_manger"}], 1, "active", {}),
            ([{**alive, "body": {**body(), "food": float("nan")}}], 1, "active", {}),
            ([dead], 1, "active", {}),
            ([alive], 1, "active", {"setpoints": {"food": 60}}),
            ([alive], 1, "active", {"scales": {**SCALES, "food": 0}}),
            ([alive], 0, "active", {}),
            ([alive], True, "active", {}),
        ]
        for steps, horizon, status, other in invalid:
            with self.subTest(status=status, horizon=horizon, other=other):
                with self.assertRaises(ValueError):
                    evaluate(steps, horizon, status, **other)


if __name__ == "__main__":
    unittest.main()
