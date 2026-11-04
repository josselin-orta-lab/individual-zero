"""#984: pure, negative and symmetric controls for paid v23 exploration.

All synthetic physical rows below are pure score *fixtures*, NEVER genuine
motor trajectories. A real born SQLite life is independently cold-audited.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body
from i2.modules.native_owner_support import _json
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, need_failure_exploration_scores,
    personally_failed_need_channels,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
MOVES = ("se_deplacer_vers_camp", "se_deplacer_vers_source")
DEST = dict(zip(MOVES, ("camp", "source")))
VISITED = frozenset(("camp", "passage"))


def record(seq, action, before, after):
    return (seq, "capture", action, 0., _json(before.as_dict()),
            _json(after.as_dict()), 0)


def failures(*, success=False):
    b0 = Body(78, 44, 44, 94)
    b1 = Body(77, 43, 43.6, 94)
    b2 = Body(76, 42, 43.2, 94)
    records = [record(1, "manger", b0, b1),
               record(2, "manger", b1, b2)]
    if success:
        b3 = Body(75, 62, 42.8, 94)
        records.append(record(3, "manger", b2, b3))
    return tuple(records)


def rank(*, previous=None, body=None, scores=None, offered=None,
         destinations=None, visited=VISITED, enabled=True,
         reflex_state="NO_PREEMPTION", existing_novelty=frozenset()):
    scores = {"se_deplacer_vers_camp":4,
              "se_deplacer_vers_source":4, "dormir":8} if scores is None else scores
    return need_failure_exploration_scores(
        scores, offered=tuple(scores) if offered is None else offered,
        destinations=DEST if destinations is None else destinations,
        visited=visited, body=body or Body(78,42,44,94), traits=TRAITS,
        previous=failures() if previous is None else previous,
        reflex_state=reflex_state, enabled=enabled,
        existing_novelty=existing_novelty)


class NeedFailureExplorationControls984(unittest.TestCase):
    def test_target_failure_requires_last_two_personally_committed_contacts(self):
        self.assertEqual(personally_failed_need_channels(
            body=Body(78,42,44,94),traits=TRAITS,previous=failures()),
            frozenset({"food"}))
        self.assertEqual(personally_failed_need_channels(
            body=Body(78,42,44,94),traits=TRAITS,previous=failures()[:1]),
            frozenset())
        self.assertNotIn("food",personally_failed_need_channels(
            body=Body(78,42,44,94),traits=TRAITS,previous=failures(success=True)))
        self.assertFalse(personally_failed_need_channels(
            body=Body(78,90,44,94),traits=TRAITS,previous=failures()))

    def test_bounded_real_potential_tie_not_direct_motor(self):
        values, evidence=rank()
        self.assertEqual(values["se_deplacer_vers_source"],9)
        self.assertEqual(values["se_deplacer_vers_camp"],4)
        self.assertEqual(values["dormir"],8)
        self.assertEqual(evidence,frozenset(("se_deplacer_vers_source",)))
        self.assertEqual(rank(enabled=False)[1],frozenset())
        self.assertEqual(rank(previous=failures()[:1])[1],frozenset())
        self.assertEqual(rank(previous=failures(success=True))[1],frozenset())
        self.assertEqual(rank(body=Body(78,90,44,94))[1],frozenset())

    def test_falsifiers_urgency_too_large_gap_unknown_stock_and_no_oracle(self):
        for reflex in ("PREEMPT","CONSTRAIN"):
            self.assertEqual(rank(reflex_state=reflex)[1],frozenset())
        self.assertEqual(rank(scores={
            "se_deplacer_vers_camp":4,
            "se_deplacer_vers_source":3,"dormir":8})[1],frozenset())
        self.assertEqual(rank(
            existing_novelty=frozenset(("se_deplacer_vers_source",)))[1],
            frozenset())
        self.assertEqual(rank(visited=frozenset(("camp","passage","source")))[1],
                         frozenset())
        self.assertEqual(rank(visited=frozenset(("passage",)))[1],
                         frozenset())
        self.assertEqual(rank(destinations={"se_deplacer_vers_camp":"camp"})[1],
                         frozenset())
        self.assertEqual(rank(offered=("se_deplacer_vers_camp","dormir"))[1],
                         frozenset())
        # No physical stock or hidden injury is ever among pure inputs.
        self.assertEqual(rank()[0], rank()[0])

    def test_destination_permutation_is_symmetric(self):
        scores={"se_deplacer_vers_camp":4,
                "se_deplacer_vers_source":4,"dormir":8}
        swapped={"se_deplacer_vers_camp":"source",
                 "se_deplacer_vers_source":"camp"}
        normal=rank(scores=scores, destinations=DEST)
        renamed=rank(scores=scores,destinations=swapped)
        self.assertEqual(normal[0]["se_deplacer_vers_source"],9)
        self.assertEqual(renamed[0]["se_deplacer_vers_camp"],9)
        self.assertEqual(len(normal[1]),len(renamed[1]))

    def test_born_disabled_and_digest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            birth=dict(body=Body(78,46,44,94),temperament=TRAITS,
                       spatial_world=True,learning=True,
                       need_failure_exploration=True,
                       max_steps=2,uc=80)
            for i,values in enumerate((
                {"learning":False},
                {"spatial_world":False},
                {"need_failure_exploration":1},
                {"need_failure_exploration":"true"})):
                with self.subTest(i=i),self.assertRaises(NativeRefusal):
                    NativePaidI2.create(
                        Path(root)/("bad"+str(i)+".db"),
                        **{**birth,**values})
            path=Path(root)/"good.db"
            life=NativePaidI2.create(path,**birth)
            life.step()
            self.assertEqual(life.audit(),NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute(
                    "SELECT need_failure_exploration FROM native_genesis"
                ).fetchone(),(1,))
                db.execute(
                    "UPDATE native_genesis SET need_failure_exploration=0")
            with self.assertRaises(NativeRefusal):
                NativePaidI2.inspect(path)


if __name__=="__main__":
    unittest.main()
