"""Offline I2 vertical slice: controlled outcome -> H2 -> paid Competition advice.

This is a G2 hypothesis test, NOT an I2 runtime, individual, autonomous
motor action, WorldBody authority or living experiment. A separate research
controller applies training interventions to a tiny deterministic test world,
then evaluates any proposed action as an OFFLINE SHADOW outcome. No proposed
action is ever dispatched by the cognitive fixture. Full negatives are kept.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_unified_control_cycle import (
    LIFE, A, B, C, claim, ObservationPort, Values, Current, Safety, Terminal,
)
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.delayed_credit_study import (
    ClaimedLivedStep, MatchedLivedEpisode, ForecastOpportunity,
    project_matched_outcome, empty_feedback_memory, PaidFeedbackValuationPort,
)

CONTEXT = ("context:synthetic",)
# A=collect berry, B=eat berry, C=drink water. C is the matched
# no-preparation control, while B is the SAME completion in both arms.
# These are simulated action costs and outcomes, not physiological measurements.
BASE_VALUES = {A: 0, B: 0, C: 2}
REGIMES = (("beneficial", 8), ("neutral", 0), ("adverse", -8))
ORDERS = ((A, C), (C, A))


class TinyControlledWorld:
    """Research-only physical toy world, not an I2 WorldBody or motor executor.

    A=collect, B=eat, C=drink. Only B can consume an A-collected berry.
    All three options remain synthetically visible, including an unsuccessful
    attempt to eat with an empty inventory; physical admission is NOT modeled.
    """

    def __init__(self, *, completion_delta: int) -> None:
        self._completion_delta = completion_delta
        self._inventory = 0
        self._last_step = -1

    def visible(self) -> tuple[str, ...]:
        # Identical personal affordances in every hidden world regime.
        return tuple(sorted((A, B, C)))

    def intervene(self, *, step: int, semantic: str) -> ClaimedLivedStep:
        if step <= self._last_step or semantic not in self.visible():
            raise ValueError("invalid research-controller intervention")
        self._last_step = step
        if semantic == A:  # collect: costs effort, stores berry; never feeds
            self._inventory += 1
            outcome = -2
        elif semantic == B:  # eat: ONLY action that consumes the berry
            if self._inventory:
                self._inventory -= 1
                outcome = self._completion_delta - 2
            else:
                outcome = -2  # ineffective eating attempt on empty inventory
        else:  # C is drinking: it never consumes berry or grants food value
            outcome = -2
        # The observed outcome is recorded only after the intervention.
        return ClaimedLivedStep(
            LIFE, step, f"history:capture:{step}", "goal:food", semantic,
            f"research:admission:{step}",
            f"history:subjective:{step}", f"history:outcome:{step}", outcome,
        )


class ControlledEvidence:
    """Exact recorded test evidence, NOT independent first-person M11."""

    def __init__(self) -> None:
        self._events: dict[str, ClaimedLivedStep] = {}
        self._opportunity: ForecastOpportunity | None = None
        self._issued: object | None = None

    def record(self, event: ClaimedLivedStep) -> None:
        event.validate()
        if event.capture_ref in self._events:
            raise ValueError("repeated controlled evidence")
        self._events[event.capture_ref] = event

    def verify_lived(self, *, event: ClaimedLivedStep) -> bool:
        return self._events.get(event.capture_ref) == event

    def verify_complete_episode(self, *, episode: MatchedLivedEpisode) -> bool:
        return all(self.verify_lived(event=e) for e in episode.events)

    def verify_forecast_capture(self, *, opportunity: ForecastOpportunity) -> bool:
        return self._opportunity == opportunity

    def verify_issued_forecast(self, *, forecast: object) -> bool:
        return forecast is self._issued

    def verify_feedback_issue(self, *, readout: object) -> bool:
        # Synthetic structural check only, not an issuance/authentication service.
        return (getattr(readout, "baseline", None) is self._issued
                and getattr(readout, "memory_version", None) == 0)


def _shadow_net(completion_delta: int, proposed: str | None) -> int | None:
    """Research-controller shadow roll-out. NOT a motor command from I2."""
    if proposed is None:
        return None
    control_world = TinyControlledWorld(completion_delta=completion_delta)
    preparation = control_world.intervene(step=40, semantic=proposed)
    completion = control_world.intervene(step=41, semantic=B)
    return preparation.lived_delta + completion.lived_delta


def exercise(*, completion_delta: int, order: tuple[str, str],
             adaptive: bool, veto: bool = False, synthetic_uc: int = 20,
             omit_observation: bool = False) -> dict[str, object]:
    """Run separate training, advisory owner and offline shadow phases."""
    if sorted(order) != sorted((A, B)):
        raise ValueError("exact paired training order required")
    world = TinyControlledWorld(completion_delta=completion_delta)
    evidence = ControlledEvidence()
    episodes = {}
    for episode_index, first in enumerate(order):
        start = 1 + 3 * episode_index
        first_event = world.intervene(step=start, semantic=first)
        last_event = world.intervene(step=start + 1, semantic=B)
        evidence.record(first_event)
        if not (omit_observation and first == A):
            evidence.record(last_event)
        episodes[first] = MatchedLivedEpisode(
            f"research:episode:{episode_index}:{first}",
            CONTEXT, (first_event, last_event),
        )

    subjective = ObservationPort()
    current_claim = subjective.add(claim(30, visible=world.visible()))
    opportunity = ForecastOpportunity(
        LIFE, current_claim.capture.goal_ref, current_claim.capture.ref,
        current_claim.capture.step, CONTEXT, A, C, B,
    )
    evidence._opportunity = opportunity
    forecast = project_matched_outcome(
        prepared=episodes[A], control=episodes[C],
        opportunity=opportunity, source=evidence,
    )
    evidence._issued = forecast
    baseline = Values(BASE_VALUES)
    valuation = (PaidFeedbackValuationPort(
        claim=current_claim, forecast=forecast,
        memory=empty_feedback_memory(opportunity),
        source=evidence, baseline=baseline,
    ) if adaptive else baseline)

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "single-owner-g2.sqlite"
        ports = dict(
            path=path, life_ref=LIFE, observation_source=subjective,
            valuation_source=valuation, current_source=Current(),
            safety_source=Safety(veto=veto),
            genesis_ref="genesis:offline-science-first",
            terminal_source=Terminal(),
        )
        fixture = CognitiveCycleFixture.create(
            synthetic_uc=synthetic_uc, **ports,
        )
        receipt = fixture.open(
            claim=current_claim, semantic_ref=A,
            evidence_ref="evidence:30", ttl_steps=12,
        )
        audit = fixture.audit()
        with sqlite3.connect(path) as connection:
            event = json.loads(connection.execute(
                "SELECT event_json FROM events WHERE seq=1"
            ).fetchone()[0])
        candidates = ({
            item["candidate_ref"]: item["semantic_ref"]
            for item in event["frame"]["candidates"]
        } if event["frame"] is not None else {})
        suggestion = candidates.get(receipt.suggested_candidate_ref)
        control_suggestion = candidates.get(receipt.control_suggested_candidate_ref)
        assert CognitiveCycleFixture.reopen(**ports).audit() == audit
        assert receipt.motor_authority == "NONE"
        assert audit["m11_authenticated"] is False
        assert audit["committed"] == 1
        return {
            "training_contrast": forecast.predicted_outcome_difference,
            "suggestion": suggestion,
            "control_suggestion": control_suggestion,
            "control_status": receipt.control_status,
            "competition_status": receipt.competition_status,
            "uc_spent": synthetic_uc - audit["remaining_synthetic_uc"],
            "shadow_net": _shadow_net(completion_delta, control_suggestion),
            "motor_authority": receipt.motor_authority,
        }


class ScienceFirstBehavioralSlice(unittest.TestCase):
    def test_full_battery_with_ablation_and_training_order_counterbalance(self):
        rows = []
        for name, observed_delta in REGIMES:
            for order in ORDERS:
                with self.subTest(regime=name, order=order):
                    adaptive = exercise(
                        completion_delta=observed_delta,
                        order=order, adaptive=True,
                    )
                    ablated = exercise(
                        completion_delta=observed_delta,
                        order=order, adaptive=False,
                    )
                    self.assertEqual(adaptive["training_contrast"], observed_delta)
                    self.assertEqual(ablated["training_contrast"], observed_delta)
                    self.assertEqual(ablated["suggestion"], C)
                    self.assertEqual(adaptive["suggestion"],
                                     A if observed_delta > 2 else C)
                    self.assertEqual(
                        (adaptive["uc_spent"], ablated["uc_spent"]), (5, 5))
                    self.assertEqual(adaptive["control_suggestion"],
                                     adaptive["suggestion"])
                    self.assertEqual(adaptive["motor_authority"], "NONE")
                    self.assertEqual(ablated["motor_authority"], "NONE")
                    self.assertEqual(
                        adaptive["shadow_net"] - ablated["shadow_net"],
                        observed_delta if observed_delta > 2 else 0,
                    )
                    rows.append({
                        "regime": name,
                        "training_order": "A_then_C" if order[0] == A else "C_then_A",
                        "observed_contrast": observed_delta,
                        "h2_advice": adaptive["suggestion"],
                        "ablation_advice": ablated["suggestion"],
                        "h2_shadow_net": adaptive["shadow_net"],
                        "ablation_shadow_net": ablated["shadow_net"],
                        "h2_uc": adaptive["uc_spent"],
                        "ablation_uc": ablated["uc_spent"],
                    })
        self.assertEqual(len(rows), 6)
        self.assertEqual({row["regime"] for row in rows},
                         {name for name, _ in REGIMES})
        print("I2_SCIENCE_FIRST_OFFLINE_SLICE " +
              json.dumps(rows, sort_keys=True, separators=(",", ":")))

    def test_consumption_requires_eat_and_drink_does_not_spend_inventory(self):
        """Physical semantics, not evidence of autonomous motor admission."""
        world = TinyControlledWorld(completion_delta=8)
        preparation = world.intervene(step=1, semantic=A)
        self.assertEqual(preparation.lived_delta, -2)
        self.assertEqual(world._inventory, 1)
        drinking = world.intervene(step=2, semantic=C)
        self.assertEqual(drinking.lived_delta, -2)
        self.assertEqual(world._inventory, 1)
        eating = world.intervene(step=3, semantic=B)
        self.assertEqual(eating.lived_delta, 6)
        self.assertEqual(world._inventory, 0)
        empty_eating = world.intervene(step=4, semantic=B)
        self.assertEqual(empty_eating.lived_delta, -2)

        adverse = TinyControlledWorld(completion_delta=-8)
        self.assertEqual(adverse.intervene(step=1, semantic=A).lived_delta, -2)
        self.assertEqual(adverse.intervene(step=2, semantic=B).lived_delta, -10)
        self.assertEqual(adverse._inventory, 0)
        # No food effect may be credited after collecting alone or drinking.
        no_eat = TinyControlledWorld(completion_delta=8)
        self.assertEqual(no_eat.intervene(step=1, semantic=A).lived_delta, -2)
        self.assertEqual(no_eat.intervene(step=2, semantic=C).lived_delta, -2)
        self.assertEqual(no_eat._inventory, 1)

    def test_veto_and_unfunded_cases_keep_advice_nonmotor(self):
        vetoed = exercise(
            completion_delta=8, order=ORDERS[0], adaptive=True, veto=True,
        )
        self.assertEqual(vetoed["suggestion"], A)
        self.assertIsNone(vetoed["control_suggestion"])
        self.assertEqual(vetoed["control_status"], "VETOED")
        self.assertIsNone(vetoed["shadow_net"])
        self.assertEqual(vetoed["uc_spent"], 5)

        unfunded = exercise(
            completion_delta=8, order=ORDERS[0], adaptive=True,
            synthetic_uc=3,
        )
        self.assertEqual(unfunded["competition_status"], "UNFUNDED")
        self.assertIsNone(unfunded["suggestion"])
        self.assertIsNone(unfunded["shadow_net"])
        self.assertEqual(unfunded["uc_spent"], 1)
        self.assertEqual(unfunded["motor_authority"], "NONE")

    def test_unobserved_training_consequence_cannot_influence_advice(self):
        with self.assertRaisesRegex(ValueError, "complete subjective episode"):
            exercise(
                completion_delta=8, order=ORDERS[0],
                adaptive=True, omit_observation=True,
            )


if __name__ == "__main__":
    unittest.main()
