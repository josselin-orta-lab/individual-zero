"""Stage 10 sleep custody contract: no oracle and no fabricated command send."""
import json
import unittest
from copy import deepcopy
from dataclasses import dataclass
from types import SimpleNamespace
from i0.modules.sleep_session import SleepSession


@dataclass(frozen=True)
class Command:
    primitive: str = "dormir"
    id: str = "cmd:1"


def admission(command=Command(), ok=True):
    return SimpleNamespace(ok=ok, command=command)


def prepared(command=Command(), source="decision", option_ref="option:sleep"):
    return SimpleNamespace(command=command, source=source, option_ref=option_ref,
                           trigger_ref="stimulus:1" if source == "reflex" else None)


@dataclass(frozen=True)
class Signals:
    consecutive_sleep_steps: int
    admitted_reflex: bool = False
    consolidation_active: bool = True
    alert: bool = False
    intention: bool = False


class Rule:
    config = SimpleNamespace(version="P41:test")

    def wake_reason(self, *, signals, frozen_sleep_pressure):
        if signals.admitted_reflex:
            return "reflex"
        if signals.alert:
            return "alert"
        if signals.intention:
            return "dated_intention"
        if signals.consecutive_sleep_steps >= 3:
            return "maximum_duration"
        if frozen_sleep_pressure < 0.1 and not signals.consolidation_active:
            return "natural_end"
        return None


def start():
    s = SleepSession(wake_policy_version="P41:test")
    s.open_world_step(1)
    s.record_applied_sleep_decision(
        world_step=1, admission=admission(), prepared=prepared(),
        motive_type="sleep_pressure", execution_status="applied",
    )
    assert s.mode == "awake"
    assert s.open_world_step(2) == "sleeping"
    return s


class SleepSessionTests(unittest.TestCase):
    def test_sleep_entry_only_next_world_step_after_applied_admitted_decision(self):
        s = start()
        self.assertEqual((s.mode, s.entry_step, s.sleep_duration), ("sleeping", 2, 1))
        self.assertEqual(s.last_world_step, 2)

    def test_inadmissible_or_unapplied_commands_cannot_start_sleep(self):
        variants = [
            dict(admission=admission(ok=False)),
            dict(prepared=prepared(command=Command(id="other"))),
            dict(prepared=prepared(source="reflex")),
            dict(admission=admission(Command(primitive="attendre"))),
            dict(motive_type="recovery_goal"),
            dict(execution_status="rolled_back"),
        ]
        for changes in variants:
            s = SleepSession(wake_policy_version="P41:test")
            s.open_world_step(1)
            data = dict(world_step=1, admission=admission(), prepared=prepared(),
                        motive_type="sleep_pressure", execution_status="applied")
            data.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                s.record_applied_sleep_decision(**data)
            self.assertEqual(s.mode, "awake")

    def test_sleep_requires_new_action_control_admission_every_step(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1), frozen_sleep_pressure=1.0, wake_rule=Rule())
        self.assertFalse(d.woke)
        self.assertTrue(d.require_sleep_command)
        with self.assertRaises(ValueError):
            s.finish_sleep_step(decision=d, command_sent=True, world_advanced=True)
        self.assertEqual(s.mode, "sleeping")
        s.finish_sleep_step(decision=d, command_sent=True, world_advanced=True,
                            admission=admission(), prepared=prepared())
        self.assertEqual(s.open_world_step(3), "sleeping")

    def test_reflex_wake_is_not_called_a_cognitive_choice(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1, admitted_reflex=True),
                                  frozen_sleep_pressure=1.0, wake_rule=Rule())
        self.assertEqual(d.reason, "reflex")
        self.assertFalse(d.resume_cognition)
        self.assertTrue(d.interrupt_consolidation)
        with self.assertRaises(ValueError):
            s.finish_sleep_step(decision=d, command_sent=True, world_advanced=True)
        direct = Command(primitive="se_deplacer", id="reflex:1")
        s.finish_sleep_step(decision=d, command_sent=True, world_advanced=True,
                            admission=admission(direct),
                            prepared=prepared(direct, source="reflex", option_ref=None),
                            consolidation_interrupted=True)
        self.assertEqual(s.mode, "awake")

    def test_threat_wakes_and_resumes_cognition_same_step(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1, alert=True),
                                  frozen_sleep_pressure=0.9, wake_rule=Rule())
        self.assertEqual((d.reason, d.resume_cognition), ("alert", True))
        action = Command(primitive="attendre", id="after-wake")
        s.finish_sleep_step(decision=d, command_sent=True, world_advanced=True,
                            admission=admission(action), prepared=prepared(action),
                            consolidation_interrupted=True)

    def test_authorized_dated_intention_wake(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1, intention=True),
                                  frozen_sleep_pressure=1.0, wake_rule=Rule())
        self.assertEqual(d.reason, "dated_intention")

    def test_maximum_duration_bounds_persistent_pressure(self):
        s = start()
        for step in (2, 3, 4):
            d = s.evaluate_sleep_step(signals=Signals(step - 1),
                                      frozen_sleep_pressure=1.0, wake_rule=Rule())
            self.assertEqual(d.woke, step == 4)
            action = Command(primitive="attendre", id="after-cap") if step == 4 else Command()
            s.finish_sleep_step(decision=d, admission=admission(action), prepared=prepared(action),
                                command_sent=True, world_advanced=True,
                                consolidation_interrupted=step == 4)
            if step < 4:
                s.open_world_step(step + 1)
        self.assertEqual(s.mode, "awake")

    def test_natural_wake_not_allowed_while_consolidation_active(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1),
                                  frozen_sleep_pressure=0, wake_rule=Rule())
        self.assertIsNone(d.reason)

    def test_snapshot_roundtrip_after_open_before_sleep_command(self):
        s = start()
        d = s.evaluate_sleep_step(signals=Signals(1), frozen_sleep_pressure=1.0, wake_rule=Rule())
        state = json.loads(json.dumps(s.export_causal_state()))
        restored = SleepSession(wake_policy_version="P41:test")
        restored.restore_causal_state(state)
        self.assertEqual(restored.export_causal_state(), state)
        restored.finish_sleep_step(decision=d, admission=admission(), prepared=prepared(),
                                   command_sent=True, world_advanced=True)
        self.assertEqual(restored.open_world_step(3), "sleeping")

    def test_malformed_snapshot_restore_does_not_change_state(self):
        s = start()
        before = s.export_causal_state()
        modified = deepcopy(before)
        modified["entry_step"] = 900
        with self.assertRaises(ValueError):
            s.restore_causal_state(modified)
        self.assertEqual(s.export_causal_state(), before)

    def test_sleep_owner_never_sends_commands(self):
        s = start()
        methods = set(dir(s))
        self.assertFalse({"dispatch", "send", "world_apply", "capture"} & methods)


if __name__ == "__main__":
    unittest.main()
