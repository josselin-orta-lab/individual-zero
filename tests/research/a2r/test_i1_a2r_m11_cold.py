"""No-birth adversarial contracts for read-only A2-R M11 evidence."""
import copy
import unittest

from i1_a2r_m11_cold import (
    body, numeric, reward, check_owner_state, physical_steps,
    evidence_life, compare_pre_reward,
)

NEEDS = ("energy", "food", "water", "integrity")
S = dict.fromkeys(NEEDS, 60.)
W = dict.fromkeys(NEEDS, 1.)


def physical(t, before, after, action="attendre"):
    common = {"t_monde": t, "attempt_ref": "attempt-" + str(t)}
    return [
        {"kind": "command_experienced", "primitive": action,
         "parameters": {}, **common},
        {"kind": "world_transition_experienced", "body_before": before,
         "body_after": after, **common},
        {"kind": "step_closed", "data": {"outcome": "normal",
         "applied_command_count": 1, "world_advance_count": 1}, **common},
    ]


def events(mode, *, tamper_return=False):
    a = dict(energy=80., food=50., water=48., integrity=100.)
    b = dict(energy=79.5, food=49.8, water=47.6, integrity=100.)
    c = dict(energy=79., food=49.6, water=47.2, integrity=100.)
    result = []
    for t, before, after in ((1, a, b), (2, b, c)):
        result.extend([
            {"kind": "stage8_option_evaluation", "t_monde": t,
             "cycle": 1, "data": {"option_ref": "permanent:attendre",
                "learning_signature": "primitive:attendre",
                "learned_value_status": "unlearned", "learned_value": None,
                "evidence": 0.2}},
            {"kind": "competition_cycle", "t_monde": t, "cycle": 1,
             "data": {"traces": [{"option_ref": "permanent:attendre",
                                  "evidence": 0.2, "crossed": True}]}},
            {"kind": "command_admitted", "t_monde": t, "cycle": 1,
             "data": {"source": "decision", "option_ref": "permanent:attendre",
                      "primitive": "attendre"}},
        ])
        result.extend(physical(t, before, after))
        if t == 2:
            result.append({"kind": "td_update_published", "t_monde": 2,
                "cycle": 1, "data": {
                "previous_signature": "primitive:attendre",
                "next_signature": "primitive:attendre",
                "segment_length": 1, "return_g": (
                    reward(a, b, setpoints=S, weights=W, mode=mode)
                    + (100 if tamper_return else 0))}})
    return result


def audited(mode):
    data = events(mode)
    return evidence_life(data, generation=2, status="active",
                         mode=mode, setpoints=S, weights=W)


class A2RColdPureTests(unittest.TestCase):
    def test_frozen_math_vs_absolute(self):
        before = dict.fromkeys(NEEDS, 60.)
        after = dict(before)
        before["water"], after["water"] = 48., 88.
        self.assertEqual(reward(before, after, setpoints=S, weights=W,
                                mode="CANONICAL_ABS"), -16.)
        self.assertEqual(reward(before, after, setpoints=S, weights=W,
                                mode="RESEARCH_DEFICIT"), 12.)

    def test_native_canonical_float_decoder(self):
        self.assertEqual(numeric({"$f64": (48.125).hex()}), 48.125)
        for cell in ({"$f64": "0x1.8p+5"}, {"$f64": "nan"},
                     float("nan"), {"$f64": "nothex"}, True, []):
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                numeric(cell)
        with self.assertRaises(ValueError):
            body({"energy": 75})

    def test_owner_both_modes_with_td(self):
        base = {
            "config_version": "native-v1", "td_values": {
                "config_version": "p31-stage8-reference-v1",
                "feature_version": "p32",
                "weights": {}
            }
        }
        self.assertEqual(check_owner_state(base, mode="CANONICAL_ABS")["mode"],
                         "CANONICAL_ABS")
        a = dict(base, config_version=base["config_version"] +
                 "+i1-a2r-deficit-reward-v1",
                 i1_a2r_reward_policy="i1-a2r-reward-deficit-owner-v1")
        self.assertEqual(check_owner_state(a, mode="RESEARCH_DEFICIT")["mode"],
                         "RESEARCH_DEFICIT")
        for wrong_mode, value in ((False, a), (True, base),
                                  (True, dict(a, i1_a2r_reward_policy="forged")),
                                  (False, dict(base, i1_a2r_reward_policy="forged"))):
            with self.assertRaises(ValueError):
                check_owner_state(value, mode="RESEARCH_DEFICIT" if wrong_mode else "CANONICAL_ABS")

    def test_reward_td_segment_and_stage8_competition(self):
        for mode in ("CANONICAL_ABS", "RESEARCH_DEFICIT"):
            row = audited(mode)
            self.assertEqual(row["td_returns_checked"], 1)
            self.assertEqual(row["stage8_competition_links"], 2)
            self.assertFalse(row["full_q_replay_verified"])
            self.assertEqual(row["adaptive_learning_go"], "NOT_ESTABLISHED")

    def test_physical_repeats_and_order_fail(self):
        original = events("CANONICAL_ABS")
        variants = []
        v = copy.deepcopy(original)
        v.insert(6, copy.deepcopy(next(e for e in v if e["kind"] == "step_closed")))
        variants.append(v)
        v = copy.deepcopy(original)
        item = next(e for e in v if e["kind"] == "world_transition_experienced")
        item["body_before"]["water"] = -5.
        variants.append(v)
        v = copy.deepcopy(original)
        item = next(e for e in v if e["kind"] == "step_closed")
        item["data"]["world_advance_count"] = 2
        variants.append(v)
        v = copy.deepcopy(original)
        item = next(e for e in v if e["kind"] == "world_transition_experienced"
                    and e["t_monde"] == 2)
        item["body_before"] = {**item["body_before"], "water": 100.}
        variants.append(v)
        for variant in variants:
            with self.subTest(index=variants.index(variant)), self.assertRaises(ValueError):
                physical_steps(variant, generation=2, status="active")

    def test_refuse_forged_td_return_and_competition(self):
        with self.assertRaisesRegex(ValueError, "TD return"):
            evidence_life(events("CANONICAL_ABS", tamper_return=True),
                          generation=2, status="active", mode="CANONICAL_ABS",
                          setpoints=S, weights=W)
        v = events("CANONICAL_ABS")
        next(x for x in v if x["kind"] == "competition_cycle")["data"]["traces"][0]["evidence"] = .9
        with self.assertRaisesRegex(ValueError, "Competition diverges"):
            evidence_life(v, generation=2, status="active",
                          mode="CANONICAL_ABS", setpoints=S, weights=W)

    def test_pre_reward_pair_is_only_preflight_not_l3(self):
        result = compare_pre_reward(
            canonical=audited("CANONICAL_ABS"),
            candidate=audited("RESEARCH_DEFICIT"),
            setpoints=S, weights=W)
        self.assertEqual(result["first_reward_difference_step"], 1)
        self.assertIsNone(result["first_motor_difference_step"])
        self.assertFalse(result["mechanism_exposed"])
        self.assertFalse(result["full_q_replay_verified"])

    def test_pre_reward_motor_divergence_rejected(self):
        candidate = audited("RESEARCH_DEFICIT")
        candidate["physical_steps"][0]["action"] = "collecter"
        with self.assertRaisesRegex(ValueError, "before any changed reward"):
            compare_pre_reward(
                canonical=audited("CANONICAL_ABS"), candidate=candidate,
                setpoints=S, weights=W)

    def test_cannot_treat_incomplete_live_life_as_dead(self):
        ev = events("CANONICAL_ABS")
        with self.assertRaisesRegex(ValueError, "terminal status"):
            physical_steps(ev, generation=2, status="dead")
        with self.assertRaises(ValueError):
            physical_steps(ev, generation=193, status="active")

if __name__ == "__main__":
    unittest.main()
