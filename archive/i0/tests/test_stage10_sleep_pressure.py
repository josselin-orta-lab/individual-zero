"""Stage-10 DC-13 pure formula and wake-policy development tests.

These tests are code correctness only, not a sleep/consolidation experiment,
scientific campaign calibration or a Stage-10 completion claim.
"""
import unittest
from dataclasses import replace

from i0.modules.sleep_pressure import (
    SleepPressureConfig, SleepPressureRules, WakeSignals,
)


def config() -> SleepPressureConfig:
    # Explicit test-only numbers; NO normative P-39/P-40/P-41 calibration.
    return SleepPressureConfig(
        version="p39-p40-p41-unit-development-v1",
        fatigue_gain=0.6,
        sleep_fatigue_recovery=0.1,
        waking_recovery_profile_relief=0.05,
        fatigue_weight=0.5,
        consolidation_weight=0.3,
        night_weight=0.2,
        unconsolidated_episode_reference=8.0,
        memory_saturation_reference=2.0,
        natural_wake_threshold=0.2,
        alert_wake_threshold=0.65,
        max_consecutive_sleep_steps=5,
    )


def wake(
    *, reflex=False, alert=None, due=False, duration=1, active=False,
) -> WakeSignals:
    return WakeSignals(reflex, alert, due, duration, active)


class Stage10SleepPressureTests(unittest.TestCase):
    def test_waking_fatigue_counts_only_simulated_logical_uc(self):
        rules = SleepPressureRules(config())
        self.assertAlmostEqual(
            rules.waking_cycle_fatigue(
                f_cog=0.1, consumed_uc=40, c_max=4,
                b_cycle_uc=100,
            ), 0.16,
        )
        # Splitting the same budget across cycles gives the same result
        # before the prescribed saturation cap.
        first = rules.waking_cycle_fatigue(
            f_cog=0.1, consumed_uc=20, c_max=4, b_cycle_uc=100,
        )
        second = rules.waking_cycle_fatigue(
            f_cog=first, consumed_uc=20, c_max=4, b_cycle_uc=100,
        )
        self.assertAlmostEqual(second, 0.16)
        self.assertEqual(rules.waking_cycle_fatigue(
            f_cog=0.99, consumed_uc=100, c_max=1,
            b_cycle_uc=100,
        ), 1.0)
        self.assertEqual(rules.waking_cycle_fatigue(
            f_cog=0.2, consumed_uc=0, c_max=4,
            b_cycle_uc=0,
        ), 0.2)

    def test_sleep_recovery_and_waking_recovery_are_disjoint(self):
        rules = SleepPressureRules(config())
        self.assertAlmostEqual(rules.sleep_step_fatigue(f_cog=0.65), 0.55)
        self.assertEqual(rules.sleep_step_fatigue(f_cog=0), 0)
        self.assertAlmostEqual(
            rules.close_waking_step_fatigue(
                f_cog=0.7, recovery_profile=True,
            ), 0.65,
        )
        self.assertEqual(rules.close_waking_step_fatigue(
            f_cog=0.7, recovery_profile=False,
        ), 0.7)

    def test_pressure_is_only_fatigue_memory_night(self):
        rules = SleepPressureRules(config())
        assessment = rules.assess_step(
            f_cog=0.6, unconsolidated_episodes=2,
            memory_occupancy=0.5, is_night=False, awake=True,
        )
        self.assertAlmostEqual(assessment.consolidation_pressure, 0.5)
        self.assertAlmostEqual(assessment.sleep_pressure, 0.45)
        self.assertEqual(assessment.intrinsic_status, "applicable")
        self.assertAlmostEqual(assessment.intrinsic_value, 0.45)
        night = rules.assess_step(
            f_cog=0.6, unconsolidated_episodes=2,
            memory_occupancy=0.5, is_night=True, awake=True,
        )
        self.assertAlmostEqual(night.sleep_pressure, 0.65)
        asleep = rules.assess_step(
            f_cog=0.6, unconsolidated_episodes=2,
            memory_occupancy=0.5, is_night=True, awake=False,
        )
        self.assertEqual(asleep.intrinsic_status, "not_applicable")
        self.assertIsNone(asleep.intrinsic_value)
        self.assertEqual(asleep.sleep_pressure, night.sleep_pressure)

    def test_occupancy_fraction_independent_of_physical_capacity(self):
        rules = SleepPressureRules(config())
        a = rules.assess_step(
            f_cog=0.1, unconsolidated_episodes=3,
            memory_occupancy=10 / 100, is_night=False, awake=True,
        )
        b = rules.assess_step(
            f_cog=0.1, unconsolidated_episodes=3,
            memory_occupancy=100 / 1000, is_night=False, awake=True,
        )
        self.assertEqual(a, b)
        saturated = rules.assess_step(
            f_cog=1, unconsolidated_episodes=100,
            memory_occupancy=1, is_night=True, awake=True,
        )
        self.assertEqual(saturated.consolidation_pressure, 1)
        self.assertEqual(saturated.sleep_pressure, 1)

    def test_wake_precedence_no_false_natural_end_during_consolidation(self):
        rules = SleepPressureRules(config())
        signals = wake(reflex=True, alert=1, due=True, duration=6, active=True)
        self.assertEqual(rules.wake_reason(
            signals=signals, frozen_sleep_pressure=0,
        ), "reflex")
        self.assertEqual(rules.wake_reason(
            signals=replace(signals, admitted_reflex=False),
            frozen_sleep_pressure=0,
        ), "alert")
        self.assertEqual(rules.wake_reason(
            signals=replace(signals, admitted_reflex=False,
                            reduced_perception_alert=0.0),
            frozen_sleep_pressure=0,
        ), "dated_intention")
        self.assertEqual(rules.wake_reason(
            signals=wake(duration=6, active=True),
            frozen_sleep_pressure=1,
        ), "maximum_duration")
        self.assertEqual(rules.wake_reason(
            signals=wake(duration=1, active=True),
            frozen_sleep_pressure=0.1,
        ), None)
        self.assertEqual(rules.wake_reason(
            signals=wake(duration=1, active=False),
            frozen_sleep_pressure=0.1,
        ), "natural_end")
        self.assertEqual(rules.wake_reason(
            signals=wake(duration=1, alert=None),
            frozen_sleep_pressure=0.9,
        ), None)

    def test_sleep_reference_values_explicit_and_fail_closed(self):
        cfg = config()
        for invalid in (
            replace(cfg, fatigue_gain=float("nan")),
            replace(cfg, sleep_fatigue_recovery=-0.1),
            replace(cfg, unconsolidated_episode_reference=0),
            replace(cfg, memory_saturation_reference=0),
            replace(cfg, natural_wake_threshold=0),
            replace(cfg, alert_wake_threshold=1.1),
            replace(cfg, max_consecutive_sleep_steps=0),
            replace(cfg, version=""),
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    SleepPressureRules(invalid)

    def test_malformed_inputs_never_become_sleep_motivation(self):
        rules = SleepPressureRules(config())
        for bad in (
            dict(f_cog=float("nan")),
            dict(f_cog=-1),
            dict(unconsolidated_episodes=-1),
            dict(unconsolidated_episodes=True),
            dict(memory_occupancy=2),
            dict(memory_occupancy=float("inf")),
            dict(is_night=1),
            dict(awake=0),
        ):
            kwargs = {
                "f_cog": 0.1, "unconsolidated_episodes": 1,
                "memory_occupancy": 0.2, "is_night": False, "awake": True,
                **bad,
            }
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    rules.assess_step(**kwargs)
        for bad in (
            dict(consumed_uc=-1),
            dict(consumed_uc=True),
            dict(consumed_uc=101),
            dict(c_max=0),
            dict(b_cycle_uc=-1),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    rules.waking_cycle_fatigue(**{
                        "f_cog": 0.1, "consumed_uc": 20, "c_max": 2,
                        "b_cycle_uc": 100, **bad,
                    })

    def test_untrusted_wake_signals_do_not_imply_wake(self):
        rules = SleepPressureRules(config())
        for invalid in (
            wake(duration=-1),
            wake(alert=float("nan")),
            wake(alert=2),
            replace(wake(), admitted_reflex=1),
            replace(wake(), authorized_dated_intention_due=1),
            replace(wake(), consolidation_active=1),
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    rules.wake_reason(
                        signals=invalid, frozen_sleep_pressure=0.5,
                    )


if __name__ == "__main__":
    unittest.main()
