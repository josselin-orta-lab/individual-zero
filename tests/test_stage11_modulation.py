"""Stage 11 P-23/P-24 profile state and INV-06 software regressions."""
from dataclasses import replace
from types import SimpleNamespace
import unittest

from i0.modules.global_modulation import (
    GlobalModulation, ModulationConfig, ModulationSignals,
)


TERMS = {"b": 1.0, "n": 1.0, "urg": 1.0, "risk": 1.0, "value": 1.0}


def config(*, confirmation=2):
    return ModulationConfig(
        version="p23-p24-stage11-dev-v1",
        threat_enter=0.7, threat_exit=0.25,
        recovery_enter=0.65, recovery_exit=0.35,
        confirmation_steps=confirmation,
        multipliers={
            "normal": dict(TERMS),
            "threat": {**TERMS, "risk": 1.5, "urg": 1.5, "n": 0.5},
            "exploration": {**TERMS, "n": 1.5},
            "recovery": {**TERMS, "n": 0.5, "value": 1.2},
        },
    )


def signals(*, threat=None, recovery=0.1, satisfied=False, bored=False):
    return ModulationSignals(threat, recovery, satisfied, bored)


class ModulationTests(unittest.TestCase):
    def test_immediate_threat_and_no_exit_from_missing_information(self):
        mod = GlobalModulation(config())
        self.assertEqual(mod.freeze(signals=signals(threat=0.95), world_step=1, cycle=1), "threat")
        for step in range(2, 6):
            self.assertEqual(mod.freeze(signals=signals(threat=None), world_step=step, cycle=1), "threat")
        self.assertEqual(mod.multipliers()["risk"], 1.5)
        self.assertEqual(mod.multipliers()["n"], 0.5)
        self.assertEqual(mod.freeze(signals=signals(threat=0), world_step=6, cycle=1), "threat")
        self.assertEqual(mod.freeze(signals=signals(threat=0), world_step=6, cycle=2), "threat")
        self.assertEqual(mod.freeze(signals=signals(threat=0), world_step=7, cycle=1), "normal")

    def test_recovery_requires_distinct_world_steps(self):
        mod = GlobalModulation(config())
        low = signals(recovery=0.85)
        for cycle in range(1, 20):
            self.assertEqual(mod.freeze(signals=low, world_step=1, cycle=cycle), "normal")
        self.assertEqual(mod.freeze(signals=low, world_step=2, cycle=1), "recovery")
        self.assertEqual(mod.freeze(signals=signals(recovery=None), world_step=3, cycle=1), "recovery")
        self.assertEqual(mod.freeze(signals=signals(recovery=0.2), world_step=4, cycle=1), "recovery")
        self.assertEqual(mod.freeze(signals=signals(recovery=0.2), world_step=5, cycle=1), "normal")

    def test_exploration_needs_boredom_and_satisfied_needs(self):
        mod = GlobalModulation(config())
        ready = signals(satisfied=True, bored=True)
        self.assertEqual(mod.freeze(signals=ready, world_step=1, cycle=1), "normal")
        self.assertEqual(mod.freeze(signals=ready, world_step=2, cycle=1), "exploration")
        self.assertEqual(mod.multipliers()["n"], 1.5)
        self.assertEqual(mod.freeze(signals=signals(satisfied=None, bored=None), world_step=3, cycle=1), "exploration")
        self.assertEqual(mod.freeze(signals=signals(satisfied=True, bored=False), world_step=4, cycle=1), "exploration")
        self.assertEqual(mod.freeze(signals=signals(satisfied=True, bored=False), world_step=5, cycle=1), "normal")

    def test_threat_preempts_recovery_and_snapshot_replays(self):
        a = GlobalModulation(config())
        a.freeze(signals=signals(recovery=0.8), world_step=1, cycle=1)
        b = GlobalModulation(config())
        b.restore_causal_state(a.export_causal_state())
        self.assertEqual(b.export_causal_state(), a.export_causal_state())
        for subject in (a, b):
            self.assertEqual(
                subject.freeze(signals=signals(threat=0.8, recovery=0.8), world_step=1, cycle=2),
                "threat",
            )
        self.assertEqual(a.export_causal_state(), b.export_causal_state())

    def test_repeat_same_cycle_does_not_change_frozen_profile(self):
        m = GlobalModulation(config())
        m.freeze(signals=signals(), world_step=1, cycle=1)
        self.assertEqual(
            m.freeze(signals=signals(threat=1), world_step=1, cycle=1),
            "normal",
        )
        self.assertEqual(m.freeze(signals=signals(threat=1), world_step=1, cycle=2), "threat")
        with self.assertRaises(ValueError):
            m.freeze(signals=signals(), world_step=1, cycle=1)

    def test_missing_confirmation_signal_suspends_not_resets_counter(self):
        entering = GlobalModulation(config())
        self.assertEqual(entering.freeze(
            signals=signals(recovery=0.8), world_step=1, cycle=1,
        ), "normal")
        self.assertEqual(entering.freeze(
            signals=signals(recovery=None), world_step=2, cycle=1,
        ), "normal")
        self.assertEqual(entering.freeze(
            signals=signals(recovery=0.8), world_step=3, cycle=1,
        ), "recovery")

        exiting = GlobalModulation(config())
        exiting.freeze(signals=signals(threat=0.9), world_step=1, cycle=1)
        self.assertEqual(exiting.freeze(
            signals=signals(threat=0.0), world_step=2, cycle=1,
        ), "threat")
        self.assertEqual(exiting.freeze(
            signals=signals(threat=None), world_step=3, cycle=1,
        ), "threat")
        self.assertEqual(exiting.freeze(
            signals=signals(threat=0.0), world_step=4, cycle=1,
        ), "normal")

    def test_only_published_st_fixed_and_preempted_slot_infer_indicators(self):
        st = SimpleNamespace(
            fixed={"body": {"energy": 20.0, "integrity": 100.0},
                   "modulation_signals": {"boredom": True, "needs_satisfied": False}},
            competitive=(SimpleNamespace(preempted=True, reliability=1.0,
                      decomposition={"risk": 0.8}),),
        )
        s = GlobalModulation.indicators_from_st(st)
        self.assertEqual(s, ModulationSignals(0.8, 0.8, False, True))
        empty = SimpleNamespace(fixed={"body": {}}, competitive=())
        self.assertEqual(GlobalModulation.indicators_from_st(empty).threat_risk, None)

    def test_no_undocumented_or_invalid_configuration(self):
        with self.assertRaises(ValueError):
            replace(config(), multipliers={"normal": dict(TERMS)}).validate()
        with self.assertRaises(ValueError):
            replace(config(), recovery_exit=0.7).validate()
        with self.assertRaises(ValueError):
            replace(config(), multipliers={
                **config().multipliers,
                "recovery": {**TERMS, "unknown": 5},
            }).validate()

    def test_snapshot_rejects_corruption_atomically(self):
        mod = GlobalModulation(config())
        mod.freeze(signals=signals(recovery=0.8), world_step=1, cycle=1)
        saved = mod.export_causal_state()
        with self.assertRaises(ValueError):
            mod.restore_causal_state({**saved, "candidate_steps": -1})
        self.assertEqual(mod.export_causal_state(), saved)


if __name__ == "__main__":
    unittest.main()
