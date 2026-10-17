"""Stage-11 prior-experience forecast: strict prospective provenance gates.

Controlled test rows stand in for the *read-only export* of the Causal Model.
They are not observations emitted into a living individual or evidence for
scientific causal establishment.
"""
from copy import deepcopy
from unittest import TestCase

from i0.modules.lived_prediction import (
    LivedPredictionConfig, LivedWaterPredictor,
)


def row(
    step=5, before=40.0, after=52.0, position=(2, 2),
    episode=None, transition=None,
):
    return {
        "identifier": f"lived:{step}",
        "contingency_ref": "causal:hydration",
        "contingency_version": 3,
        "option_ref": "option:causal-test:causal:hydration:v3",
        "motive_type": "test_causal",
        "sent_t_monde": step,
        "observed_t_monde": step + 1,
        "water_before": before,
        "water_observed": after,
        "position": list(position),
        "command_event_ref": f"physical:command:{step}",
        "transition_event_ref": transition or f"physical:transition:{step}",
        "physical_episode_ref": episode or f"episode:closed:{step}",
    }


def predictor(minimum=2, spread=1, precision=0.2, maximum=2):
    return LivedWaterPredictor(LivedPredictionConfig(
        version="stage11-test-lived-forecast-v1",
        min_distinct_episodes=minimum,
        maximum_spread=spread,
        precision_floor=precision,
        max_precision=maximum,
    ))


def forecast(p, rows, *, t=11, before=50, position=(2, 2)):
    return p.predict(
        canonical_state={
            "lived_causal_actions": deepcopy(rows),
            "causal_action_witnesses": [],
        },
        t_monde=t, water_before=before, position=position,
    )


class LivedWaterPredictionTests(TestCase):
    def test_requires_independent_already_closed_physical_episodes(self):
        p = predictor()
        self.assertIsNone(forecast(p, []))
        self.assertIsNone(forecast(p, [row(5)]))
        result = forecast(p, [row(5), row(7)])
        self.assertIsNotNone(result)
        self.assertEqual(result.consequence.variable, "water")
        self.assertEqual(result.consequence.value_or_delta, 62.0)
        self.assertEqual(result.consequence.precision, 0.2)
        self.assertEqual(result.source_steps, (5, 7))
        self.assertEqual(result.source_transition_refs, (
            "physical:transition:5", "physical:transition:7",
        ))

    def test_prediction_is_prospective_no_same_step_or_future_information(self):
        p = predictor(minimum=1)
        self.assertIsNone(forecast(p, [row(10)], t=11))
        self.assertIsNone(forecast(p, [row(11)], t=11))
        self.assertIsNone(forecast(p, [row(12)], t=11))
        self.assertIsNotNone(forecast(p, [row(9)], t=11))

    def test_missing_memory_closure_or_capture_is_not_sample(self):
        p = predictor(minimum=1)
        for field in ("physical_episode_ref", "command_event_ref",
                      "transition_event_ref", "water_observed"):
            with self.subTest(field=field):
                invalid = row()
                invalid[field] = None
                self.assertIsNone(forecast(p, [invalid]))
        # A final command is not a source until a later accessible capture.
        pending = row()
        pending["observed_t_monde"] = None
        self.assertIsNone(forecast(p, [pending]))

    def test_repeated_episode_or_physical_transition_rejected(self):
        p = predictor()
        for changed in (
            {"physical_episode_ref": "episode:closed:5"},
            {"transition_event_ref": "physical:transition:5"},
            {"sent_t_monde": 5, "observed_t_monde": 6},
        ):
            with self.subTest(changed=changed):
                copy = row(7)
                copy.update(changed)
                with self.assertRaises(ValueError):
                    forecast(p, [row(5), copy])

    def test_context_bounds_and_inconsistent_deltas_fail_closed(self):
        p = predictor(spread=0.5, maximum=1)
        self.assertIsNone(forecast(p, [row(5), row(7, after=60)]))
        self.assertIsNone(forecast(p, [row(5), row(7, position=(5,5))]))
        self.assertIsNone(forecast(p, [row(5), row(7)], position=(0,0)))
        self.assertEqual(
            forecast(p, [row(5), row(7)], before=97).consequence.value_or_delta,
            100.0,
        )

    def test_prior_samples_can_be_archived_by_canonical_owner(self):
        p = predictor()
        state = {
            "lived_causal_actions": [row(5)],
            "causal_action_witnesses": [row(7)],
        }
        result = p.predict(
            canonical_state=state, t_monde=11,
            water_before=50.0, position=(2,2),
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.source_steps, (5, 7))

    def test_invalid_config_and_capture_fail_closed(self):
        from dataclasses import replace
        cfg = predictor().config
        for bad in (
            replace(cfg, min_distinct_episodes=0),
            replace(cfg, precision_floor=-1),
            replace(cfg, maximum_spread=float("nan")),
            replace(cfg, max_precision=0.1),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    LivedWaterPredictor(bad)
        with self.assertRaises(ValueError):
            forecast(predictor(), [row(5), row(7)], t=True)
        with self.assertRaises(ValueError):
            forecast(predictor(), [row(5), row(7)], before=float("nan"))

    def test_pure_read_no_canonical_state_mutation(self):
        p = predictor()
        state = {
            "lived_causal_actions": [row(5), row(7)],
            "causal_action_witnesses": [],
        }
        before = deepcopy(state)
        forecast1 = p.predict(
            canonical_state=state,
            t_monde=11, water_before=50.0, position=(2,2),
        )
        forecast2 = p.predict(
            canonical_state=state,
            t_monde=11, water_before=50.0, position=(2,2),
        )
        self.assertEqual(forecast1, forecast2)
        self.assertEqual(state, before)
