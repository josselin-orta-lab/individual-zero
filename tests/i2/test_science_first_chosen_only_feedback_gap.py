"""Science-first G2 NEGATIVE experiment: advice-following trials without paired probes.

The research controller applies an I2 nonmotor *suggestion* to its own
deterministic test world and records that actual chosen-arm outcome. No
WorldBody/M11/agent motor authority is granted. Existing H2 only accepts a
complete matched prepared-versus-control pair, which does not exist when
one arm is repeatedly chosen. This is an intentional falsification of
"chosen consequences alone are enough to update the current H2 mechanism".
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_unified_control_cycle import (
    LIFE, A, B, C, claim, ObservationPort, Values, Current, Safety, Terminal,
)
from test_science_first_behavioral_slice import (
    TinyControlledWorld, CONTEXT, BASE_VALUES,
)
from test_science_first_sequential_shadow import (
    IssuedControlledEvidence, _observed_episode, _semantic, CAPTURES,
    STABLE, REVERSAL, SYNTHETIC_UC, run_sequence,
)
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.delayed_credit_study import (
    ForecastOpportunity, MatchedLivedEpisode, PaidFeedbackValuationPort,
    project_matched_outcome, empty_feedback_memory, compare_matched_outcomes,
)


def chosen_only(regimes: tuple[int, ...]):
    """Two separately controlled offline worlds follow each arm's *advice*.

    The only imposed paired samples are the initial shared training examples.
    After that, no new counterfactual/control episode is generated for H2.
    All results below are observed in the research harness after the decision,
    never used as a privileged value at that same capture.
    """
    if type(regimes) is not tuple or len(regimes) != len(CAPTURES):
        raise ValueError("exactly four preregistered conditions required")
    with tempfile.TemporaryDirectory() as folder:
        adaptive_db = Path(folder) / "adaptive.sqlite"
        ablation_db = Path(folder) / "ablation.sqlite"
        training = TinyControlledWorld(completion_delta=8)
        evidence = IssuedControlledEvidence()
        prepared = _observed_episode(
            training, evidence, name="training:prepare", start=1, first=A,
        )
        control = _observed_episode(
            training, evidence, name="training:control", start=4, first=C,
        )
        adaptive_world = TinyControlledWorld(completion_delta=8)
        ablation_world = TinyControlledWorld(completion_delta=8)
        observation = ObservationPort()
        shared = dict(
            life_ref=LIFE, observation_source=observation,
            current_source=Current(), safety_source=Safety(),
            terminal_source=Terminal(),
        )
        observed_choices = []
        rows = []
        for index, (step, delta) in enumerate(zip(CAPTURES, regimes)):
            # Both arms receive equal visible affordances and no hidden delta.
            current_claim = observation.add(
                claim(step, visible=adaptive_world.visible()),
            )
            opportunity = ForecastOpportunity(
                LIFE, current_claim.capture.goal_ref, current_claim.capture.ref,
                step, CONTEXT, A, C, B,
            )
            evidence._opportunity = opportunity
            forecast = project_matched_outcome(
                prepared=prepared, control=control,
                opportunity=opportunity, source=evidence,
            )
            evidence._issued = forecast
            evidence.expected_version = 0
            initial_memory = empty_feedback_memory(opportunity)
            valuation = PaidFeedbackValuationPort(
                claim=current_claim, forecast=forecast,
                memory=initial_memory, source=evidence,
                baseline=Values(BASE_VALUES),
            )
            adaptive_ports = dict(
                path=adaptive_db, valuation_source=valuation,
                genesis_ref="genesis:chosen-only-adaptive", **shared,
            )
            ablation_ports = dict(
                path=ablation_db, valuation_source=Values(BASE_VALUES),
                genesis_ref="genesis:chosen-only-ablation", **shared,
            )
            if index == 0:
                adaptive = CognitiveCycleFixture.create(
                    synthetic_uc=SYNTHETIC_UC, **adaptive_ports,
                )
                ablation = CognitiveCycleFixture.create(
                    synthetic_uc=SYNTHETIC_UC, **ablation_ports,
                )
            else:
                adaptive = CognitiveCycleFixture.reopen(**adaptive_ports)
                ablation = CognitiveCycleFixture.reopen(**ablation_ports)
            kwargs = (dict(
                claim=current_claim, semantic_ref=A,
                evidence_ref=f"evidence:{step}", ttl_steps=64,
            ) if index == 0 else dict(claim=current_claim))
            if index == 0:
                advice = adaptive.open(**kwargs)
                baseline = ablation.open(**kwargs)
            else:
                advice = adaptive.observe(**kwargs)
                baseline = ablation.observe(**kwargs)
            chosen = _semantic(
                adaptive_db, index + 1, advice.control_suggested_candidate_ref,
            )
            ablated = _semantic(
                ablation_db, index + 1,
                baseline.control_suggested_candidate_ref,
            )
            assert (advice.motor_authority, baseline.motor_authority) == ("NONE", "NONE")
            assert chosen in (A, C) and ablated in (A, C)
            assert adaptive.audit()["committed"] == index + 1
            assert adaptive.audit()["feedback_version"] == 0
            assert ablation.audit()["feedback_version"] == 0
            assert adaptive.feedback_snapshot() is None
            assert adaptive.audit()["remaining_synthetic_uc"] == SYNTHETIC_UC - 5 * (index + 1)
            assert ablation.audit()["remaining_synthetic_uc"] == adaptive.audit()["remaining_synthetic_uc"]

            # The controller, NOT I2's Action Control, chooses to FOLLOW advice.
            # Its consequence is observed only after this cognitive COMMIT.
            adaptive_world._completion_delta = delta
            ablation_world._completion_delta = delta
            first = adaptive_world.intervene(step=step + 1, semantic=chosen)
            result = adaptive_world.intervene(step=step + 2, semantic=B)
            baseline_first = ablation_world.intervene(
                step=step + 1, semantic=ablated,
            )
            baseline_result = ablation_world.intervene(step=step + 2, semantic=B)
            evidence.record(first)
            evidence.record(result)
            observed_choices.append((first, result))
            observed_net = first.lived_delta + result.lived_delta
            control_net = baseline_first.lived_delta + baseline_result.lived_delta
            rows.append({
                "cycle": index,
                "hidden_regime_for_research_controller": delta,
                "h2_advice_followed_by_controller": chosen,
                "ablation_advice_followed_by_controller": ablated,
                "observed_chosen_net": observed_net,
                "observed_ablation_net": control_net,
                "observed_advantage": observed_net - control_net,
                "controller_forced_eating_after_advice": True,
                "h2_feedback_version": adaptive.audit()["feedback_version"],
                "uc_per_arm": 5,
                "motor_authority": advice.motor_authority,
            })
            # Both arms must survive a cold, fully audited read. These local
            # records authenticate no outside consequence or personal agency.
            assert CognitiveCycleFixture.reopen(**adaptive_ports).audit() == adaptive.audit()
            assert CognitiveCycleFixture.reopen(**ablation_ports).audit() == ablation.audit()

        assert len(observed_choices) == len(CAPTURES)
        assert len(evidence._events) == 4 + 2 * len(CAPTURES)
        return tuple(rows), tuple(observed_choices), evidence


class ChosenOnlyFeedbackGapTests(unittest.TestCase):
    def test_advice_following_does_not_fabricate_missing_counterfactuals(self):
        reports = {}
        for name, regimes in (("stable", STABLE), ("reversal", REVERSAL)):
            with self.subTest(name=name):
                rows, chosen_events, evidence = chosen_only(regimes)
                self.assertEqual(len(rows), 4)
                self.assertEqual(
                    [x["h2_advice_followed_by_controller"] for x in rows],
                    [A, A, A, A],
                )
                self.assertEqual(
                    [x["ablation_advice_followed_by_controller"] for x in rows],
                    [C, C, C, C],
                )
                self.assertEqual([x["h2_feedback_version"] for x in rows],
                                 [0, 0, 0, 0])
                self.assertEqual([x["uc_per_arm"] for x in rows], [5] * 4)
                self.assertEqual([x["motor_authority"] for x in rows], ["NONE"] * 4)
                self.assertTrue(all(
                    evidence.verify_lived(event=result)
                    for pair in chosen_events for result in pair
                ))
                # Each chosen A outcome was really recorded, but does not
                # invent the missing later B episode. Reusing the same
                # observed A trial as a counterfactual is rejected.
                first_episode = MatchedLivedEpisode(
                    "chosen:cycle:0", CONTEXT, chosen_events[0],
                )
                with self.assertRaisesRegex(
                    ValueError, "independently matched",
                ):
                    compare_matched_outcomes(
                        prepared=first_episode, control=first_episode,
                        preparatory_action_ref=A,
                        completion_action_ref=B, source=evidence,
                    )
                reports[name] = rows
        self.assertEqual(
            [x["observed_advantage"] for x in reports["stable"]],
            [8, 8, 8, 8],
        )
        self.assertEqual(
            [x["observed_advantage"] for x in reports["reversal"]],
            [8, -8, -8, -8],
        )
        self.assertEqual(
            sum(x["observed_advantage"] for x in reports["reversal"]),
            -16,
        )
        # Compare directly to the previous CONTROLLED-PAIR protocol: this
        # one can update H2, because an experimenter supplied both arms.
        paired, paired_memory = run_sequence(REVERSAL)
        self.assertEqual(paired_memory.total_observations, 3)
        self.assertEqual(
            [x["h2_advice"] for x in paired], [A, A, A, C],
        )
        print("I2_CHOSEN_ONLY_FEEDBACK_GAP_G2 " + json.dumps(
            reports, sort_keys=True, separators=(",", ":"),
        ))


if __name__ == "__main__":
    unittest.main()
