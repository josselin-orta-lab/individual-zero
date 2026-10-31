"""Fixed G2 research battery: report successes AND failures, no selection.

All synthetic outcomes are listed below before any comparison is run.
Every prediction uses a cold-replayed H2 snapshot from the one v5 owner.
This is not independent pre-registration or proof of natural learning.
"""
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_feedback_calibration import Source, opportunity, forecast, heldout
from test_unified_control_cycle import A, B, C, Values, Current, Safety, Terminal
from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost, FaultInjected,
)
from i2.modules.delayed_credit_study import (
    empty_feedback_memory, learn_from_feedback, read_feedback,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim


# Frozen, deterministic, equal-length regimes. No RNG, tuning or exclusions.
# Historical contrast of the supplied fixed training pair is +7.
REGIMES = (
    ("stable_adverse", (-8,) * 24),
    ("baseline_aligned", (7,) * 24),
    ("abrupt_reversal", (-8,) * 12 + (7,) * 12),
    ("alternating", (-8, 7) * 12),
    ("gradual_drift", tuple(range(-8, 16))),
)
TRIALS = len(REGIMES)
SAMPLES_PER_TRIAL = 24
START_STEP = 10
STEP_SPACING = 15
COLD_REOPEN_EACH_CYCLE = True
PRECOMMIT_FAULT = ("abrupt_reversal", 7)
ACK_LOST = ("abrupt_reversal", 14)


class FrozenH2Battery(unittest.TestCase):
    def run_regime(self, label, outcomes, *, return_shadow=False,
                   fault_index=None, lost_ack_index=None, return_three=False):
        with tempfile.TemporaryDirectory() as folder:
            old = empty_feedback_memory(opportunity(START_STEP))
            life = old.life_ref

            class Subject:
                def verify(self, *, life_ref, claim, digest):
                    return life_ref == life and claim.life_ref == life

            ports = {
                "path": Path(folder) / "one-owner-v5.sqlite",
                "life_ref": life,
                "observation_source": Subject(),
                "valuation_source": Values(),
                "current_source": Current(),
                "safety_source": Safety(),
                "genesis_ref": "genesis:fixed-h2-battery",
                "terminal_source": Terminal(),
            }
            owner = CognitiveCycleFixture.create(synthetic_uc=160, **ports)
            source = Source()
            history = []
            for i, outcome in enumerate(outcomes):
                issue_step = START_STEP + STEP_SPACING * i
                readout = read_feedback(
                    memory=old, forecast=forecast(issue_step), source=source,
                )
                prepared, control = heldout(issue_step + 2, outcome, 0)
                update = learn_from_feedback(
                    memory=old, readout=readout,
                    prepared=prepared, control=control, source=source,
                )
                step = issue_step + 10
                evidence = f"evidence:battery:{label}:{step}"
                capture = ObservationClaim(
                    life, FirstPersonCapture(
                        step, f"capture:battery:{label}:{step}",
                        old.goal_ref, tuple(sorted((A, B, C))),
                    ),
                    f"source:battery:{label}:{step}", (evidence,),
                )

                if ((label, i) == PRECOMMIT_FAULT or
                        (fault_index is not None and i == fault_index)):
                    before = owner.audit()
                    with self.assertRaises(FaultInjected):
                        owner.observe(
                            claim=capture, feedback_previous=old,
                            feedback_update=update, _fault_at="before_commit",
                        )
                    self.assertEqual(owner.audit(), before)
                    self.assertEqual(owner.feedback_snapshot(), old)

                if i == 0:
                    owner.open(
                        claim=capture, semantic_ref=A, evidence_ref=evidence,
                        ttl_steps=12, feedback_previous=old,
                        feedback_update=update,
                    )
                elif ((label, i) == ACK_LOST or
                      (lost_ack_index is not None and i == lost_ack_index)):
                    with self.assertRaises(CommitAcknowledgmentLost):
                        owner.observe(
                            claim=capture, feedback_previous=old,
                            feedback_update=update, _fault_at="after_commit",
                        )
                    # Never retry after a lost COMMIT acknowledgment.
                else:
                    owner.observe(
                        claim=capture, feedback_previous=old,
                        feedback_update=update,
                    )

                if COLD_REOPEN_EACH_CYCLE:
                    owner = CognitiveCycleFixture.reopen(**ports)
                old = owner.feedback_snapshot()
                self.assertEqual(old, update.new_memory)
                self.assertEqual(owner.audit()["feedback_version"], i + 1)

                if label == "abrupt_reversal" and i == 4:
                    # Intra-life context switching is NOT implemented;
                    # a foreign context is rejected, not silently learned.
                    next_step = issue_step + STEP_SPACING
                    foreign = replace(
                        forecast(next_step),
                        opportunity=replace(
                            opportunity(next_step),
                            context_signature=("context:foreign",),
                        ),
                    )
                    unchanged = owner.audit()
                    with self.assertRaisesRegex(ValueError, "different context"):
                        read_feedback(memory=old, forecast=foreign, source=source)
                    self.assertEqual(owner.audit(), unchanged)

                history.append(outcome)

            self.assertEqual(len(history), SAMPLES_PER_TRIAL)
            shadow = owner.feedback_horizon_shadow_report()
            self.assertEqual(shadow["samples"], SAMPLES_PER_TRIAL)
            self.assertEqual(shadow["h2_16_mae"], owner.feedback_scorecard()["adaptive_mae"])
            self.assertEqual(shadow, CognitiveCycleFixture.reopen(**ports).feedback_horizon_shadow_report())
            self.assertEqual(shadow["motor_authority"], "NONE")
            shadow_history = []
            shadow_errors4 = []
            shadow_errors16 = []
            for idx, row in enumerate(shadow["rows"]):
                expected4 = (Fraction(sum(shadow_history[-4:]), len(shadow_history[-4:]))
                             if shadow_history else Fraction(7))
                expected16 = (Fraction(sum(shadow_history[-16:]), len(shadow_history[-16:]))
                              if shadow_history else Fraction(7))
                expected_horizon = (4 if shadow_errors4 and
                    sum(shadow_errors4[-8:]) < sum(shadow_errors16[-8:]) else 16)
                self.assertEqual(row["horizon"], expected_horizon)
                self.assertEqual(row["selected_prediction"],
                    expected4 if expected_horizon == 4 else expected16)
                shadow_errors4.append(abs(expected4-outcomes[idx]))
                shadow_errors16.append(abs(expected16-outcomes[idx]))
                shadow_history.append(outcomes[idx])
            report = owner.feedback_scorecard()
            self.assertEqual(
                report,
                CognitiveCycleFixture.reopen(**ports).feedback_scorecard(),
            )
            self.assertEqual(report["samples"], SAMPLES_PER_TRIAL)
            self.assertEqual(owner.audit()["committed"], SAMPLES_PER_TRIAL)
            self.assertEqual(owner.audit()["feedback_version"], SAMPLES_PER_TRIAL)
            self.assertEqual(owner.audit()["remaining_synthetic_uc"], 40)
            self.assertEqual(report["motor_authority"], "NONE")
            self.assertIs(report["m11_authenticated"], False)
            self.assertIs(report["scheduler_uc_authenticated"], False)

            seen = []
            for i, row in enumerate(report["rows"]):
                issue_step = START_STEP + STEP_SPACING * i
                expected_h2 = (
                    Fraction(sum(seen[-16:]), len(seen[-16:]))
                    if seen else Fraction(7)
                )
                persistence = seen[-1] if seen else 7
                self.assertEqual(row["issue_capture_ref"], f"capture:{issue_step}")
                self.assertEqual(row["observed"], history[i])
                self.assertEqual(row["historical_prediction"], 7)
                self.assertEqual(row["adaptive_prediction"], expected_h2)
                self.assertEqual(row["persistence_prediction"], persistence)
                self.assertEqual(row["adaptive_error"], abs(expected_h2 - history[i]))
                self.assertEqual(row["historical_error"], abs(7 - history[i]))
                self.assertEqual(row["persistence_error"], abs(persistence - history[i]))
                seen.append(history[i])

            self.assertEqual(
                report["adaptive_mae"],
                sum((row["adaptive_error"] for row in report["rows"]), Fraction(0))
                / SAMPLES_PER_TRIAL,
            )
            if return_three:\n                return report, shadow, owner.feedback_three_way_shadow_report()\n            return (report, shadow) if return_shadow else report

    def test_all_frozen_regimes_are_reported_including_losses(self):
        self.assertEqual(TRIALS, 5)
        self.assertTrue(all(len(sequence) == SAMPLES_PER_TRIAL
                            for _, sequence in REGIMES))
        results = {}
        for label, sequence in REGIMES:
            with self.subTest(regime=label):
                result = self.run_regime(label, sequence)
                results[label] = result

        self.assertEqual(set(results), {name for name, _ in REGIMES})
        stable = results["stable_adverse"]
        self.assertLess(stable["adaptive_mae"], stable["historical_mae"])
        self.assertEqual(stable["adaptive_mae"], stable["persistence_mae"])

        aligned = results["baseline_aligned"]
        self.assertEqual(
            (aligned["adaptive_mae"], aligned["historical_mae"],
             aligned["persistence_mae"]),
            (0, 0, 0),
        )

        reversal = results["abrupt_reversal"]
        self.assertGreater(reversal["adaptive_mae"], reversal["persistence_mae"])

        alternating = results["alternating"]
        self.assertGreater(alternating["adaptive_mae"], alternating["historical_mae"])
        self.assertLess(alternating["adaptive_mae"], alternating["persistence_mae"])

        drift = results["gradual_drift"]
        self.assertGreater(drift["adaptive_mae"], drift["persistence_mae"])

        # Outputs are complete, machine-readable, deterministic and derived
        # from the audited committed journal, not an in-memory fake score.
        digestible = {
            name: {
                "n": result["samples"],
                "h2_mae": str(result["adaptive_mae"]),
                "historical_mae": str(result["historical_mae"]),
                "persistence_mae": str(result["persistence_mae"]),
            }
            for name, result in results.items()
        }
        print("I2_H2_FROZEN_BATTERY_RESULTS " +
              json.dumps(digestible, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
