"""P2 opt-in born, previously lived site evidence only at tied paid moves.

Physics-only handcrafted history checks provenance, not endogenous return.
Actual native lives are never given scripted movement or hidden site payoff.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import _json
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, personally_observed_place_tie,
    PLACE_RETURN_EVIDENCE,
)


def record(seq, action, before=None, after=None):
    before = before or Body(85, 90, 35, 100)
    after = after or Body(84, 89.8, 34.6, 100)
    return (seq, "cap:" + str(seq), action, 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


def claim(*actions):
    return SimpleNamespace(
        capture=SimpleNamespace(accessible_semantics=tuple(actions)))


class NativePlaceReturnTieP2(unittest.TestCase):
    TRAITS = BirthTemperament(0, .5, .3, 0, 0)
    MOVES = ("se_deplacer_vers_camp", "se_deplacer_vers_source")
    SCORES = {"se_deplacer_vers_camp":4,
              "se_deplacer_vers_source":4,"dormir":2}

    def test_personal_restoration_favors_uniquely_remembered_adjacent_site(self):
        history = (
            record(1, "boire", after=Body(84, 89.8, 59.6, 100)),
            record(2, "se_deplacer_vers_passage",
                   Body(84, 89.8, 59.6, 100),
                   Body(82, 89.6, 59.2, 100)))
        body = Body(82, 89.6, 52, 100)
        values, sources = personally_observed_place_tie(
            self.SCORES, claim=claim(*self.MOVES), body=body,
            traits=self.TRAITS, previous=history,
            learning=True, enabled=True)
        self.assertEqual(values["se_deplacer_vers_camp"], 5)
        self.assertEqual(values["se_deplacer_vers_source"], 4)
        self.assertEqual(sources, frozenset({"se_deplacer_vers_camp"}))
        # The physically useful site is historical, not a future guarantee.
        for on, learn in ((False, True), (True, False)):
            found, referenced = personally_observed_place_tie(
                self.SCORES, claim=claim(*self.MOVES), body=body,
                traits=self.TRAITS, previous=history,
                learning=learn, enabled=on)
            self.assertEqual(found, self.SCORES)
            self.assertEqual(referenced, frozenset())

    def test_unknown_failed_satiated_or_multiple_sites_never_get_favored(self):
        old = record(1, "boire", after=Body(84, 89.8, 59.6, 100))
        move = record(2, "se_deplacer_vers_passage")
        histories = (
            (),
            (record(1, "boire"), move),  # negative observed effect
            (old, move))
        for history in histories:
            for body in (Body(82,90,90,100), Body(82,90,35,100)):
                values, ref = personally_observed_place_tie(
                    self.SCORES, claim=claim(*self.MOVES), body=body,
                    traits=self.TRAITS, previous=history,
                    learning=True, enabled=True)
                if history == (old, move) and body.water < 70:
                    self.assertEqual(values["se_deplacer_vers_camp"],5)
                else:
                    self.assertEqual(values,self.SCORES)
                    self.assertEqual(ref,frozenset())
        initial = (
            old,
            record(2,"se_deplacer_vers_passage"),
            record(3,"se_deplacer_vers_source"),
            record(4,"boire", after=Body(84,89.8,59.6,100)),
            record(5,"se_deplacer_vers_passage"))
        vals, ref = personally_observed_place_tie(
            self.SCORES, claim=claim(*self.MOVES),
            body=Body(82,90,35,100),
            traits=self.TRAITS, previous=initial,
            learning=True, enabled=True)
        self.assertEqual(vals,self.SCORES)
        self.assertEqual(ref,frozenset())
        # No arbitrary conversion of an untied action into a winner.
        vals, _ = personally_observed_place_tie(
            {**self.SCORES,"dormir":9},
            claim=claim(*self.MOVES,"dormir"),
            body=Body(82,90,35,100),traits=self.TRAITS,
            previous=(old, move), learning=True, enabled=True)
        self.assertEqual(vals["se_deplacer_vers_camp"],4)

    def test_native_birth_gate_and_same_owner_cold_replay(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(NativeRefusal):
                NativePaidI2.create(
                    Path(root)/"nonspatial.db", body=Body(85,90,35,100),
                    temperament=self.TRAITS, spatial_world=False,
                    place_return_tie=True)
            for learning in (False,True):
                for enabled in (False,True):
                    path = Path(root)/("L%s-P%s.db" % (learning, enabled))
                    life = NativePaidI2.create(
                        path,body=Body(85,90,35,100),
                        temperament=self.TRAITS,
                        spatial_world=True,ordinary_water_site="camp",
                        water_stock=2,food_stock=0,learning=learning,
                        place_return_tie=enabled,max_steps=8,uc=170,
                        sleep_consolidation=False)
                    for _ in range(8):
                        if life.audit()["terminal"]:
                            break
                        life.step()  # NO user-selected motor, all choices paid
                    state = life.audit()
                    self.assertEqual(NativePaidI2.inspect(path).audit(),state)
                    self.assertFalse(state["engine_registered"])
                    self.assertFalse(state["m11_authenticated"])
                    self.assertEqual(state["scientific_verdict"],"NOT_ESTABLISHED")
                    self.assertEqual(state["revision"],8)


if __name__ == "__main__":
    unittest.main()
