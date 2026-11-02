"""Two scientifically distinct post-contact memory questions.

1. Separate fixed-prior and learned lives do not share the ninth-choice
   affordances or prior history. Their actions cannot be causally compared.
2. On the SAME verified learned predecision capture, a researcher-only
   omission of the last positive result changes the unboosted score
   ranking, but the energy survival reflex would still favor EAT.
No SQLite owner or behavioral policy is manipulated in this ablation.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.chosen_outcome_study import observed_chosen_scores
from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, EAT, PRIORS, _PreviousResults,
    paired_decision_contrast,
)


class PostContactMemoryAblation(unittest.TestCase):
    def create(self, path, *, learning):
        impulses = SCENARIOS["restoration"] + (6, 6)
        return IsolatedI2.create(
            path, learning=learning, impulses=impulses,
            initial_energy=40, initial_uc=60,
            last_resort_exploration=True,
            extended_postcontact_study=True,
        )

    def test_separate_lives_have_unmatched_ninth_affordances(self):
        with tempfile.TemporaryDirectory() as tmp:
            outcomes = {}
            for learning, label in ((True, "learning"), (False, "fixed")):
                life = self.create(Path(tmp) / (label + ".sqlite"),
                                   learning=learning)
                life.run_world(ticks=18)
                outcomes[label] = (life.decision_evidence(), life.audit())
            learned, learned_audit = outcomes["learning"]
            fixed, fixed_audit = outcomes["fixed"]
            self.assertEqual(len(learned), 9)
            self.assertEqual(len(fixed), 9)
            self.assertEqual(learned[8]["candidate_scores"][EAT], 9)
            self.assertIn(EAT, learned[8]["visible"])
            # Fixed-prior behavior consumed food at different earlier ticks.
            # EAT is not even offered on its ninth capture. Comparing an
            # invented fixed EAT score is scientifically invalid.
            self.assertNotIn(EAT, fixed[8]["visible"])
            self.assertNotIn(EAT, fixed[8]["candidate_scores"])
            self.assertNotEqual(learned[8]["before_inventory"],
                                fixed[8]["before_inventory"])
            contrast = paired_decision_contrast(learned, fixed)
            self.assertIsNotNone(contrast["first_divergence_seq"])
            self.assertLess(contrast["first_divergence_seq"], 9)
            self.assertTrue(
                contrast["not_a_natural_learning_or_survival_verdict"])
            self.assertFalse(learned_audit["m11_authenticated"])
            self.assertFalse(fixed_audit["m11_authenticated"])

    def test_same_capture_memory_omission_changes_raw_ranking_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            life = self.create(Path(tmp) / "learned.sqlite", learning=True)
            life.run_world(ticks=16)
            self.assertEqual(life.audit()["revision"], 8)
            life.advance_physics()
            life.advance_physics()
            _meta, body, rows = life._read()
            self.assertEqual(body["tick_count"], 18)
            claim = life._claim(
                body["revision"], body["energy"], body["inventory"],
                body["resources"], rows, physical_ticks=body["tick_count"],
            )
            history = life._history(rows)
            self.assertEqual(history[-1].chosen_action_ref, EAT)
            self.assertEqual(history[-1].observed_net, 4)
            without_last_recovery = history[:-1]
            full = observed_chosen_scores(
                claim=claim, results=history,
                source=_PreviousResults(history), priors=PRIORS,
            )
            omitted = observed_chosen_scores(
                claim=claim, results=without_last_recovery,
                source=_PreviousResults(history), priors=PRIORS,
            )
            self.assertEqual((full[EAT], omitted[EAT]), (9, -5))
            self.assertGreater(full[EAT], full[COLLECT])
            self.assertLess(omitted[EAT], omitted[COLLECT])
            # Even without the +4 memory, the same urgent energy state
            # has its own last-resort signal; a paid EAT would not
            # establish that memory was necessary for the motor choice.
            reflex = LocalEnergySurvivalReflex(claim, body["energy"])
            self.assertEqual(reflex.state, "CONSTRAIN")
            self.assertEqual(reflex.last_resort_food_priority(), EAT)
            ninth = life.step()
            self.assertEqual(ninth.chosen, EAT)
            self.assertEqual(ninth.actual_uc_spent, 5)
            self.assertFalse(life.decision_evidence()[8][
                "last_resort_priority_applied"])
            self.assertFalse(life.audit()["m11_authenticated"])


if __name__ == "__main__":
    unittest.main()
