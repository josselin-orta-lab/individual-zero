"""Paid ninth-decision memory ablation without hidden-world knowledge.

Compare identical restored hidden physics with learning enabled versus
fixed priors in fresh separate lives. The selected policy's eighth
experience is never copied to the control. Divergence is descriptive,
not a causal experiment with matched pre-choice histories.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT

class PostContactMemoryAblation(unittest.TestCase):
    def test_learning_vs_fixed_priors_in_extended_world(self):
        with tempfile.TemporaryDirectory() as tmp:
            outcomes={}
            impulses=SCENARIOS["restoration"]+(6,6)
            for learning, label in ((True,"learning"),(False,"fixed")):
                life=IsolatedI2.create(
                    Path(tmp)/(label+".sqlite"), learning=learning,
                    impulses=impulses, initial_energy=40,initial_uc=60,
                    last_resort_exploration=True,
                    extended_postcontact_study=True)
                life.run_world(ticks=18)
                rows=life.decision_evidence()
                outcomes[label]=(rows,life.audit())
            learned,la=outcomes["learning"]
            fixed,fa=outcomes["fixed"]
            self.assertEqual(len(learned),9)
            self.assertEqual(len(fixed),9)
            self.assertEqual(learned[8]["candidate_scores"][EAT],9)
            self.assertEqual(fixed[8]["candidate_scores"][EAT],4)
            self.assertEqual(learned[8]["chosen"],EAT)
            self.assertEqual(fixed[8]["chosen"],EAT)
            self.assertFalse(learned[8]["last_resort_priority_applied"])
            self.assertFalse(fixed[8]["last_resort_priority_applied"])
            self.assertEqual(learned[8]["uc_spent"],fixed[8]["uc_spent"])
            self.assertFalse(la["m11_authenticated"])
            self.assertFalse(fa["m11_authenticated"])
            # The new observed value changes the score, but not the
            # final motor choice in this already-food-favoring control.
            self.assertNotEqual(
                learned[8]["candidate_scores"][EAT],
                fixed[8]["candidate_scores"][EAT])

if __name__=="__main__":
    unittest.main()
