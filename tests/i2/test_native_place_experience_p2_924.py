"""P2 first primitive: extract ONLY real site-associated body experiences.

Physics-only fabricated replay rows verify attribution, not voluntary return.
A separate source-locked no-motor cohort is required for the P2 gate.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_owner_support import _json
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_place_experience import (
    lived_place_outcomes, summarized_site_experience
)


def row(seq, action, before, after):
    return (seq, "capture:" + str(seq), action, 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


class P2PersonalPlaceExperience924(unittest.TestCase):
    TRAITS = BirthTemperament(0, .5, .3, 0, 0)

    def test_only_physically_used_site_and_correct_unmet_need(self):
        thirsty = Body(85, 85, 40, 100)
        restored = Body(84.5, 84.8, 49.6, 100)
        ineffective = Body(84.5, 84.8, 39.6, 100)
        hungry = Body(83, 35, 90, 100)
        fed = Body(82.5, 44.8, 89.6, 100)
        history = (
            row(1, "boire", thirsty, restored),  # physically at camp
            row(2, "se_deplacer_vers_passage", restored,
                Body(82.5,84.6,49.2,100)),
            row(3, "boire", thirsty, ineffective),  # passage, failure
            row(4, "se_deplacer_vers_source", ineffective,
                Body(82.5,84.6,39.2,100)),
            row(5, "manger", hungry, fed),  # at source
            row(6, "attendre", hungry, hungry),
        )
        observed = lived_place_outcomes(
            history, traits=self.TRAITS, enabled=True)
        self.assertEqual([(v.site,v.targeted_need,v.restored) for v in observed],
            [("camp","water",True),("passage","water",False),
             ("source","food",True)])
        scored = summarized_site_experience(observed)
        self.assertEqual(scored[("camp","water")][0:2], (1,0))
        self.assertEqual(scored[("passage","water")][0:2], (0,1))
        self.assertEqual(scored[("source","food")][0:2], (1,0))
        self.assertNotIn(("source","water"), scored)
        self.assertNotIn(("camp","food"), scored)

    def test_not_a_hidden_place_or_clock_or_wrong_need_or_motor(self):
        satisfied = Body(85,85,90,100)
        after = Body(84.5,84.8,89.6,100)
        # Actual drink with no water need supplies no learned site signal.
        history = (row(1,"boire",satisfied,after),)
        self.assertEqual(lived_place_outcomes(
            history,traits=self.TRAITS,enabled=True), ())
        self.assertEqual(lived_place_outcomes(
            history,traits=self.TRAITS,enabled=False), ())
        with self.assertRaises(ValueError):
            lived_place_outcomes(
                (row(1,"se_deplacer_vers_passage",satisfied,after),),
                traits=self.TRAITS,enabled=False)
        with self.assertRaises(ValueError):
            lived_place_outcomes(
                (row(1,"se_deplacer_vers_source",satisfied,after),),
                traits=self.TRAITS,enabled=True)
        with self.assertRaises(ValueError):
            lived_place_outcomes(
                (row(2,"boire",satisfied,after),),
                traits=self.TRAITS,enabled=True)
        with self.assertRaises(ValueError):
            lived_place_outcomes(history,traits=self.TRAITS,enabled=1)


if __name__ == "__main__":
    unittest.main()
