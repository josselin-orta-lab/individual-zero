"""Same-capture, source-verified analytic choice ablation.

This study asks whether the last personally observed restored-food result
changes *raw paid candidate ordering* at identical observed body state.
It does NOT pretend omission is a second physically executed life.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.chosen_outcome_study import observed_chosen_scores
from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, PRIORS, EAT, COLLECT, _PreviousResults,
)


class MatchedMemoryDecisionIsolation(unittest.TestCase):
    def test_same_capture_ranking_flips_but_reflex_confounds_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            life = IsolatedI2.create(
                Path(tmp) / "life.sqlite", learning=True,
                impulses=SCENARIOS["restoration"] + (6, 6),
                initial_energy=40, initial_uc=60, resources=8,
                last_resort_exploration=True, extended_postcontact_study=True,
            )
            life.run_world(ticks=16)
            life.advance_physics()
            life.advance_physics()
            _meta, body, rows = life._read()
            claim = life._claim(body["revision"], body["energy"],
                                body["inventory"], body["resources"], rows,
                                physical_ticks=body["tick_count"])
            # The same capture can be inspected analytically but no
            # speculative 'memory removal' is committed to the owner.
            history = life._history(rows)
            self.assertEqual(history[-1].observed_net, 4)
            complete = observed_chosen_scores(
                claim=claim, results=history,
                source=_PreviousResults(history), priors=PRIORS)
            without_recovery = observed_chosen_scores(
                claim=claim, results=history[:-1],
                source=_PreviousResults(history), priors=PRIORS)
            self.assertEqual(complete[EAT], 9)
            self.assertEqual(without_recovery[EAT], -5)
            self.assertGreater(complete[EAT], complete[COLLECT])
            self.assertLess(without_recovery[EAT], without_recovery[COLLECT])
            actual = life.step()
            observed = life.decision_evidence()[8]
            self.assertEqual(actual.chosen, EAT)
            self.assertEqual(observed["chosen"], EAT)
            # The actual reflex alone can still rescue the risky choice.
            # The memory-dependent raw ranking does not isolate motor causality.
            self.assertIn(observed["survival_reflex"]["state"],
                          ("CONSTRAIN", "PREEMPT"))
            self.assertFalse(observed["last_resort_priority_applied"])
            self.assertFalse(life.audit()["m11_authenticated"])


if __name__ == "__main__":
    unittest.main()
