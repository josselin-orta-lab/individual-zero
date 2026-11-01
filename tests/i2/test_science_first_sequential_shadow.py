"""G2 sequential test of delayed outcome -> durable H2 -> later paid advice.

Not an autonomous I2 life. A research controller intervenes in a deterministic
test world to supply matched observed episodes AFTER each prospective issue.
It separately computes a SHADOW consequence of the advice (never dispatches
an agent action). No future consequence is sent to a cognitive port.
Test a fixed stable regime and a sudden reversal, with no-H2 ablation.
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

from test_science_first_behavioral_slice import (
    TinyControlledWorld, ControlledEvidence, CONTEXT, BASE_VALUES, _shadow_net,
)
from test_unified_control_cycle import (
    LIFE, A, B, C, claim, ObservationPort, Values, Current, Safety, Terminal,
)
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.delayed_credit_study import (
    MatchedLivedEpisode, ForecastOpportunity, PaidFeedbackValuationPort,
    empty_feedback_memory, project_matched_outcome, read_feedback,
    learn_from_feedback,
)

# All conditions and their order are fixed, not tuned from CI output.
STABLE = (8, 8, 8, 8)
REVERSAL = (8, -8, -8, -8)
CAPTURES = (10, 30, 50, 70)
SYNTHETIC_UC = 30


class IssuedControlledEvidence(ControlledEvidence):
    """Synthetic readout verification for the one owner, NOT M11 issuance."""

    def __init__(self):
        super().__init__()
        self.expected_version = 0

    def verify_feedback_issue(self, *, readout):
        return (readout.baseline is self._issued and
                readout.memory_version == self.expected_version)


def _observed_episode(world, evidence, *, name, start, first):
    initial = world.intervene(step=start, semantic=first)
    result = world.intervene(step=start + 1, semantic=C)
    evidence.record(initial)
    evidence.record(result)
    return MatchedLivedEpisode(name, CONTEXT, (initial, result))


def _semantic(db, seq, candidate_ref):
    with sqlite3.connect(db) as conn:
        event = json.loads(conn.execute(
            "SELECT event_json FROM events WHERE seq=?", (seq,)
        ).fetchone()[0])
    if candidate_ref is None:
        return None
    return next((x["semantic_ref"] for x in event["frame"]["candidates"]
                 if x["candidate_ref"] == candidate_ref), None)


def run_sequence(regimes: tuple[int, ...], *, suppress_first_outcome=False):
    if type(regimes) is not tuple or len(regimes) != len(CAPTURES):
        raise ValueError("four controlled observation regimes required")
    with tempfile.TemporaryDirectory() as folder:
        adaptive_db = Path(folder) / "adaptive.sqlite"
        ablation_db = Path(folder) / "ablation.sqlite"
        subjective = ObservationPort()
        evidence = IssuedControlledEvidence()
        world = TinyControlledWorld(completion_delta=8)

        # These intervention-produced observations are *training* data,
        # supplied by the research controller, not I2's own chosen actions.
        training_a = _observed_episode(
            world, evidence, name="train:prepare", start=1, first=A,
        )
        training_b = _observed_episode(
            world, evidence, name="train:control", start=4, first=B,
        )
        shared = dict(
            life_ref=LIFE, observation_source=subjective,
            current_source=Current(), safety_source=Safety(),
            terminal_source=Terminal(),
        )
        pending = None
        rows = []
        for index, (step, hidden_delta) in enumerate(zip(CAPTURES, regimes)):
            current_claim = subjective.add(
                claim(step, visible=world.visible())
            )
            op = ForecastOpportunity(
                LIFE, current_claim.capture.goal_ref, current_claim.capture.ref,
                step, CONTEXT, A, B, C,
            )
            evidence._opportunity = op
            forecast = project_matched_outcome(
                prepared=training_a, control=training_b,
                opportunity=op, source=evidence,
            )
            evidence._issued = forecast

            if index == 0:
                prior = empty_feedback_memory(op)
            else:
                previous = CognitiveCycleFixture.reopen(
                    path=adaptive_db, valuation_source=Values(BASE_VALUES),
                    genesis_ref="genesis:sequential-adaptive", **shared,
                )
                prior = previous.feedback_snapshot()
                assert prior is not None
            evidence.expected_version = prior.total_observations
            value_source = PaidFeedbackValuationPort(
                claim=current_claim, forecast=forecast, memory=prior,
                source=evidence, baseline=Values(BASE_VALUES),
            )
            adaptive_ports = dict(
                path=adaptive_db, valuation_source=value_source,
                genesis_ref="genesis:sequential-adaptive", **shared,
            )
            ablation_ports = dict(
                path=ablation_db, valuation_source=Values(BASE_VALUES),
                genesis_ref="genesis:sequential-ablation", **shared,
            )
            adaptive = (CognitiveCycleFixture.create(
                synthetic_uc=SYNTHETIC_UC, **adaptive_ports,
            ) if index == 0 else CognitiveCycleFixture.reopen(**adaptive_ports))
            ablation = (CognitiveCycleFixture.create(
                synthetic_uc=SYNTHETIC_UC, **ablation_ports,
            ) if index == 0 else CognitiveCycleFixture.reopen(**ablation_ports))
            # Feedback committed on cycle t is not read by Competition until
            # t+1: the present v5 owner evaluates advice BEFORE H2 update.
            before = read_feedback(
                memory=prior, forecast=forecast, source=evidence,
            )
            kwargs = (
                dict(claim=current_claim, semantic_ref=A,
                     evidence_ref=f"evidence:{step}", ttl_steps=64)
                if index == 0 else dict(claim=current_claim)
            )
            if index:
                receipt = adaptive.observe(
                    **kwargs, feedback_previous=prior, feedback_update=pending,
                )
                baseline = ablation.observe(**kwargs)
            else:
                receipt = adaptive.open(**kwargs)
                baseline = ablation.open(**kwargs)
            audit = adaptive.audit()
            base_audit = ablation.audit()
            assert audit["committed"] == base_audit["committed"] == index + 1
            assert receipt.motor_authority == baseline.motor_authority == "NONE"
            assert audit["m11_authenticated"] is base_audit["m11_authenticated"] is False
            assert (receipt.intake_uc, receipt.competition_uc,
                    receipt.control_uc) == (1, 3, 1)
            assert (baseline.intake_uc, baseline.competition_uc,
                    baseline.control_uc) == (1, 3, 1)
            selected = _semantic(
                adaptive_db, index + 1, receipt.control_suggested_candidate_ref,
            )
            ablated = _semantic(
                ablation_db, index + 1, baseline.control_suggested_candidate_ref,
            )
            after = adaptive.feedback_snapshot()
            if index == 0:
                assert after is None
                updated = prior
            else:
                assert after == pending.new_memory
                updated = after
            assert audit["feedback_version"] == index
            assert base_audit["feedback_version"] == 0
            assert audit["remaining_synthetic_uc"] == SYNTHETIC_UC - 5 * (index + 1)
            assert base_audit["remaining_synthetic_uc"] == audit["remaining_synthetic_uc"]
            # Run the outcome projection only in a separate research controller.
            # It does not write a motor action or a physical outcome into I2.
            a_shadow = _shadow_net(hidden_delta, selected)
            b_shadow = _shadow_net(hidden_delta, ablated)
            rows.append({
                "cycle": index,
                "capture_step": step,
                "h2_version_before": prior.total_observations,
                "h2_prediction_before": str(before.predicted_outcome_difference),
                "hidden_regime_for_shadow": hidden_delta,
                "h2_advice": selected,
                "ablation_advice": ablated,
                "h2_shadow_net": a_shadow,
                "ablation_shadow_net": b_shadow,
                "shadow_gain": a_shadow - b_shadow,
                "uc_per_arm": 5,
            })

            # Reopen cold after each COMMIT: next cycle must use its audited
            # memory, never a shadow/controller memory copy.
            cold = CognitiveCycleFixture.reopen(**adaptive_ports)
            assert cold.audit() == audit
            assert cold.feedback_snapshot() == after

            if index == len(CAPTURES) - 1:
                break
            # The prospective readout is issued after cognition, but BEFORE
            # collecting the future matched observations. No future result
            # can affect advice or the issuance at this step.
            evidence.expected_version = updated.total_observations
            issued = read_feedback(
                memory=updated, forecast=forecast, source=evidence,
            )
            world._completion_delta = hidden_delta  # research-controller only
            start = step + 2
            prepared = _observed_episode(
                world, evidence, name=f"heldout:prepared:{index}",
                start=start, first=A,
            )
            control = _observed_episode(
                world, evidence, name=f"heldout:control:{index}",
                start=start + 4, first=B,
            )
            if suppress_first_outcome and index == 0:
                # Delete the authenticated result AFTER intervention: the
                # causal world outcome exists, but the subjective port
                # cannot claim that the individual has observed it.
                del evidence._events[prepared.events[-1].capture_ref]
            pending = learn_from_feedback(
                memory=updated, readout=issued,
                prepared=prepared, control=control, source=evidence,
            )

        last = CognitiveCycleFixture.reopen(**adaptive_ports)
        assert last.audit()["committed"] == len(CAPTURES)
        return tuple(rows), last.feedback_snapshot()


class SequentialScienceFirstTests(unittest.TestCase):
    def test_stable_and_reversal_keep_losses_and_delay_visible(self):
        reports = {}
        for name, sequence in (("stable", STABLE), ("reversal", REVERSAL)):
            with self.subTest(name=name):
                rows, memory = run_sequence(sequence)
                self.assertEqual(len(rows), 4)
                self.assertEqual(memory.total_observations, 3)
                self.assertEqual([x["h2_version_before"] for x in rows],
                                 [0, 0, 1, 2])
                self.assertEqual([x["uc_per_arm"] for x in rows], [5] * 4)
                self.assertEqual([x["ablation_advice"] for x in rows], [B] * 4)
                reports[name] = rows

        stable = reports["stable"]
        self.assertEqual([x["h2_advice"] for x in stable], [A, A, A, A])
        self.assertEqual([x["shadow_gain"] for x in stable], [8, 8, 8, 8])
        reversal = reports["reversal"]
        # Delayed memory reacts, but does NOT rescue the earlier losses.
        self.assertEqual([x["h2_advice"] for x in reversal], [A, A, A, B])
        self.assertEqual([x["shadow_gain"] for x in reversal], [8, -8, -8, 0])
        self.assertEqual([x["h2_prediction_before"] for x in reversal],
                         ["8", "8", "8", "0"])
        self.assertLess(
            sum(x["shadow_gain"] for x in reversal), 0,
            "a reversal disadvantage must be reported, not optimized away",
        )
        print("I2_SEQUENTIAL_SHADOW_G2 " + json.dumps(
            reports, sort_keys=True, separators=(",", ":"),
        ))

    def test_missing_post_decision_outcome_prevents_feedback(self):
        with self.assertRaisesRegex(
            ValueError, "complete subjective episode",
        ):
            run_sequence(REVERSAL, suppress_first_outcome=True)


if __name__ == "__main__":
    unittest.main()
