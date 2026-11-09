"""Stage 2.1 replay gate unit tests on synthetic states outside the falsifier fixtures."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import stage2_replay_gate_falsifier as F
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.p13_replay_gate_mind import P13ReplayGateMind, strict_top
from i3.modules.stage2_random_equal_mean import scheduled_replays

BODY = (70.0, 70.0, 70.0, 70.0, 70.0)
CAP = {"body": BODY, "here": (True, ()), "neighbors": F.NEIGHBORS, "inventory": ()}
SLEEP_BODY = (90.0, 85.0, 85.0, 85.0, 90.0)


def gate(mode="gate"):
    return F._prime(P13ReplayGateMind(midpoint(), F.SEED, mode=mode,
                                      observer_decision_diagnostics=True))


def p13():
    return F._prime(Mind(midpoint(), F.SEED, observer_decision_diagnostics=True))


class Decision(unittest.TestCase):
    def test_decision_identical_to_p13_plus_one_audit_cycle(self):
        a, b = F._decide(p13(), CAP), F._decide(gate(), CAP)
        self.assertEqual((a["option"], a["action"], a["param"]),
                         (b["option"], b["action"], b["param"]))
        self.assertEqual(a["scores"], b["scores"])
        self.assertEqual(b["work"].cycles - a["work"].cycles, 1)
        self.assertEqual(b["work"].simulated_steps, a["work"].simulated_steps)

    def test_audit_updates_first_person_counters(self):
        m = gate()
        F._decide(m, CAP)
        self.assertEqual((m.decisions_total, m.audited_decisions), (1, 1))

    def test_residual_part_matches_zeroed_values(self):
        m = gate()
        b = CognitiveBudget((100.0,) * 5, BodyLaws())
        m._drift = m.drift()
        full, _s, _u = m.simulate(BODY, [("attendre",)], 8, b)
        residual = m._last_residual
        z = deepcopy(m)
        z.values = [[0.0] * len(v) for v in z.values]
        bare, _s, _u = z.simulate(BODY, [("attendre",)], 8,
                                  CognitiveBudget((100.0,) * 5, BodyLaws()))
        self.assertAlmostEqual(full - bare, residual, places=12)


class Gate(unittest.TestCase):
    def test_forced_open_prepares_p13_limit(self):
        a = F.sleep_step(p13(), SLEEP_BODY)
        b = F.sleep_step(gate("forced_open"), SLEEP_BODY)
        self.assertEqual(a["prepared"], b["prepared"])
        self.assertEqual(a["values"], b["values"])

    def test_gate_stays_shut_without_any_relevant_margin(self):
        m = gate()
        m.decisions_total = 30
        m.audited_decisions, m.relevant_decisions, m.margin_sum = 30, 0, 0.0
        out = F.sleep_step(m, SLEEP_BODY)
        self.assertEqual(out["prepared"], 0)
        self.assertEqual(out["gate_simulations"], 2)

    def test_zero_perceived_cost_never_replays_less_than_gate(self):
        hist = {"audited_decisions": 30, "relevant_decisions": 20,
                "margin_sum": 20 * 0.02, "decisions_total": 40, "sleep_steps": 3}
        ks = []
        for mode in ("gate", "zero_perceived_cost"):
            m = gate(mode)
            for k, v in hist.items():
                setattr(m, k, v)
            ks.append(F.sleep_step(m, (30.0, 85.0, 85.0, 85.0, 30.0))["prepared"])
        self.assertLessEqual(ks[0], ks[1])

    def test_gate_is_paid_one_cycle_and_two_simulations(self):
        m = gate()
        out = F.sleep_step(m, SLEEP_BODY)
        extra = out["work"].cycles - out["base"].cycles
        self.assertEqual(extra, 1)
        self.assertGreater(out["work"].simulated_steps, out["base"].simulated_steps)



class RandomEqualMeanControl(unittest.TestCase):
    def test_decision_and_paid_audit_identical_to_gate(self):
        a, b = F._decide(gate("gate"), CAP), F._decide(gate("random_equal_mean"), CAP)
        self.assertEqual((a["option"], a["action"], a["param"], a["scores"], a["work"]),
                         (b["option"], b["action"], b["param"], b["scores"], b["work"]))

    def test_nominal_draw_is_reproducible_but_work_actually_paid(self):
        a = gate("random_equal_mean")
        out = F.sleep_step(a, SLEEP_BODY)
        nominal = scheduled_replays(F.SEED, 0)
        self.assertEqual(out["gate_simulations"], 2)
        self.assertEqual(a._random_sleep_ordinal, 1)
        self.assertEqual((a.random_schedule_draws, a.random_nominal_replays), (1, nominal))
        self.assertEqual(out["gate"]["random_nominal_k"], nominal)
        self.assertEqual(out["gate"]["k"], min(nominal, out["gate"]["eligible"]))
        self.assertEqual(a.random_eligible_replays, out["gate"]["k"])
        self.assertEqual(out["prepared"], out["executed"])
        self.assertEqual(out["prepared"], out["work"].replays)
        self.assertLessEqual(out["prepared"], out["gate"]["k"])
        self.assertEqual(out["work"].cycles - out["base"].cycles, 1)
        self.assertGreater(out["work"].simulated_steps, out["base"].simulated_steps)
        self.assertEqual(F.sleep_step(gate("random_equal_mean"), SLEEP_BODY)["gate"], out["gate"])

    def test_sleep_ordinal_includes_unaffordable_learning_without_faking_charge(self):
        a = gate("random_equal_mean")
        body = (0.01,) * 5
        a.last = (body, ("dormir",), "dormir", None)
        result = {"body": body, "dead": False, "moved": False}
        budget = CognitiveBudget(body, BodyLaws())
        self.assertIsNone(a.prepare_learning(result, budget))
        self.assertEqual(a._random_sleep_ordinal, 1)
        self.assertEqual(a.random_schedule_draws, 0)
        self.assertEqual(a.random_nominal_replays, 0)
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual(a.sleep_steps, 0)
        self.assertIsNone(a.prepare_learning({**result, "dead": True},
                                              CognitiveBudget(body, BodyLaws())))
        self.assertEqual(a._random_sleep_ordinal, 1)

    def test_random_count_does_not_change_genome_or_action_authority(self):
        a, b = gate("gate"), gate("random_equal_mean")
        for attr in ("theta", "p", "w", "gammas", "n_base",
                     "h_max", "m_max", "beta_u", "lambda_r"):
            with self.subTest(attr=attr):
                self.assertEqual(getattr(a, attr), getattr(b, attr))
        self.assertEqual(type(a), type(b))


class Helpers(unittest.TestCase):
    def test_strict_top(self):
        self.assertEqual(strict_top({"a": 2.0, "b": 1.0}), "a")
        self.assertIsNone(strict_top({"a": 1.0, "b": 1.0}))

    def test_static_isolation(self):
        _modules, banned = F.static_isolation()
        self.assertEqual(banned, [])

    def test_no_work_is_free(self):
        self.assertNotEqual(gate()._replay_work(), CognitiveWork())

    def test_r_hat_uses_all_scored_decisions_not_only_audited(self):
        m = gate()
        m.decisions_total = 59
        m.audited_decisions = 50
        m.relevant_decisions = 25
        m.margin_sum = 25 * 0.05
        r_hat, m_hat, _H = m.gate_inputs()
        self.assertAlmostEqual(r_hat, 26.0 / 61.0)
        self.assertAlmostEqual(m_hat, 0.05)


if __name__ == "__main__":
    unittest.main()
