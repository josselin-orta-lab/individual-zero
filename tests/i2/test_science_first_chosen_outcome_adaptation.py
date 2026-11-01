"""G2 chosen-only adaptation with one bounded research-controller exploration.

No born I2, motor authority, authenticated perception or online learning
owner. Controller follows a nonmotor recommendation and separately imposes
one exploration trial, then returns ONLY the chosen result to next capture.
Fixed regimes and frozen prior/offset; no hidden outcome reaches cognition.
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
    LIFE, A, B, C, claim, ObservationPort, Current, Safety, Terminal,
)
from test_science_first_behavioral_slice import (
    TinyControlledWorld, BASE_VALUES,
)
from test_science_first_sequential_shadow import _semantic
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.chosen_outcome_study import (
    ObservedChosenResult, ChosenOutcomeValuationStudy,
    observed_chosen_scores,
)

CAPTURES = (10, 20, 30, 40, 50, 60)
STABLE = (8, 8, 8, 8, 8, 8)
REVERSAL = (8, -8, -8, -8, -8, -8)
ADVERSE = (-8, -8, -8, -8, -8, -8)
RECOVERY = (8, -8, -8, 8, 8, 8)
PRIORS = {A: 3, B: 2, C: 0}


class RecordedSource:
    def __init__(self):
        self.entries = {}

    def add(self, result):
        result.validate()
        if result.evidence_ref in self.entries:
            raise ValueError("duplicate experimental outcome")
        self.entries[result.evidence_ref] = result

    def verify_chosen_result(self, *, result):
        return self.entries.get(result.evidence_ref) == result


def run(regimes, *, explore=False):
    if type(regimes) is not tuple or len(regimes) != len(CAPTURES):
        raise ValueError("fixed six-step sequence required")
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "single-cognitive-owner.sqlite"
        source = ObservationPort()
        evidence = RecordedSource()
        world = TinyControlledWorld(completion_delta=8)
        history = []
        rows = []
        ports = dict(
            path=path, life_ref=LIFE, observation_source=source,
            current_source=Current(), safety_source=Safety(),
            terminal_source=Terminal(),
            genesis_ref="genesis:chosen-only-g2-research",
        )
        for index, (step, hidden_delta) in enumerate(zip(CAPTURES, regimes)):
            current = source.add(claim(step, visible=world.visible()))
            valuation = ChosenOutcomeValuationStudy(
                claim=current, results=tuple(history),
                source=evidence, priors=PRIORS,
            )
            fixture = (
                CognitiveCycleFixture.create(
                    synthetic_uc=35, valuation_source=valuation, **ports,
                ) if index == 0 else CognitiveCycleFixture.reopen(
                    valuation_source=valuation, **ports,
                )
            )
            receipt = (
                fixture.open(
                    claim=current, semantic_ref=A,
                    evidence_ref=f"evidence:{step}", ttl_steps=64,
                ) if index == 0 else fixture.observe(claim=current)
            )
            recommendation = _semantic(
                path, index + 1, receipt.control_suggested_candidate_ref,
            )
            assert recommendation in (A, B)
            assert receipt.motor_authority == "NONE"
            assert (receipt.intake_uc, receipt.competition_uc,
                    receipt.control_uc) == (1, 3, 1)
            assert fixture.audit()["remaining_synthetic_uc"] == 35 - 5 * (index+1)
            assert fixture.audit()["feedback_version"] == 0
            assert CognitiveCycleFixture.reopen(
                valuation_source=valuation, **ports,
            ).audit() == fixture.audit()
            # Exploration is the ONE externally controlled trial on cycle 3.
            # It is not chosen, admitted or dispatched by I2 itself.
            chosen = ((B if recommendation == A else A)
                      if explore and index == 3 else recommendation)
            world._completion_delta = hidden_delta
            first = world.intervene(step=step + 1, semantic=chosen)
            completion = world.intervene(step=step + 2, semantic=C)
            observed_net = first.lived_delta + completion.lived_delta
            lived = ObservedChosenResult(
                LIFE, current.capture.ref, chosen, step + 2,
                f"observed:chosen:{step}", observed_net,
            )
            evidence.add(lived)
            history.append(lived)
            rows.append({
                "cycle": index,
                "regime_known_only_to_researcher": hidden_delta,
                "advice": recommendation,
                "controller_followed": chosen,
                "exploration_intervention": chosen != recommendation,
                "observed_net": observed_net,
                "uc": 5,
            })
        assert len(history) == 6
        return tuple(rows)


class ChosenOutcomeAdaptationTests(unittest.TestCase):
    def test_stable_reversal_recovery_and_adverse_with_ablation(self):
        reports = {}
        for name, sequence in (
            ("stable", STABLE), ("reversal", REVERSAL),
            ("recovery", RECOVERY), ("adverse", ADVERSE),
        ):
            with self.subTest(condition=name):
                exploratory = run(sequence, explore=True)
                no_exploration = run(sequence, explore=False)
                for rows in (exploratory, no_exploration):
                    self.assertEqual(len(rows), 6)
                    self.assertEqual([r["uc"] for r in rows], [5]*6)
                    self.assertTrue(all(r["advice"] in (A, B) for r in rows))
                self.assertEqual(sum(r["exploration_intervention"]
                                     for r in exploratory), 1)
                self.assertFalse(any(r["exploration_intervention"]
                                     for r in no_exploration))
                reports[name] = (exploratory, no_exploration)

        stable, stable_no = reports["stable"]
        self.assertEqual([r["advice"] for r in stable], [A]*6)
        self.assertEqual(sum(r["observed_net"] for r in stable), 28)
        self.assertEqual(sum(r["observed_net"] for r in stable_no), 36)

        reversal, reversal_no = reports["reversal"]
        self.assertEqual([r["advice"] for r in reversal], [A, A, B, B, B, B])
        self.assertEqual([r["advice"] for r in reversal_no], [A, A, B, B, B, B])
        self.assertEqual(sum(r["observed_net"] for r in reversal), -20)
        self.assertEqual(sum(r["observed_net"] for r in reversal_no), -12)

        adverse, adverse_no = reports["adverse"]
        self.assertEqual([r["advice"] for r in adverse], [A, B, B, B, B, B])
        self.assertEqual(sum(r["observed_net"] for r in adverse), -28)
        self.assertEqual(sum(r["observed_net"] for r in adverse_no), -20)

        recovery, recovery_no = reports["recovery"]
        self.assertEqual([r["advice"] for r in recovery], [A, A, B, B, A, A])
        self.assertEqual([r["advice"] for r in recovery_no], [A, A, B, B, B, B])
        self.assertEqual(sum(r["observed_net"] for r in recovery), 12)
        self.assertEqual(sum(r["observed_net"] for r in recovery_no), -12)

        print("I2_CHOSEN_OBSERVATIONAL_G2 "+json.dumps({
            n: {"bounded_exploration": list(a),
                "no_exploration": list(b)}
            for n, (a,b) in reports.items()
        },sort_keys=True,separators=(",",":")))

    def test_cannot_read_current_future_forged_or_replayed_evidence(self):
        source = RecordedSource()
        observer = ObservationPort()
        current = observer.add(claim(30))
        original = ObservedChosenResult(
            LIFE, "capture:10", A, 12, "observed:12", 6,
        )
        source.add(original)
        self.assertEqual(
            observed_chosen_scores(
                claim=current, results=(original,), source=source, priors=PRIORS,
            )[A], 10,
        )
        from dataclasses import replace
        for bad in (
            replace(original, observed_step=30),
            replace(original, observed_step=31),
            replace(original, life_ref="life:foreign"),
            replace(original, observed_net=-10),
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                observed_chosen_scores(
                    claim=current, results=(bad,), source=source, priors=PRIORS,
                )
        with self.assertRaises(ValueError):
            observed_chosen_scores(
                claim=current, results=(original, original),
                source=source, priors=PRIORS,
            )


if __name__=="__main__":
    unittest.main()
