"""G2 falsifier: no research-controller-forced eat after a paid I2 recommendation.

Every offer uses the LAST test-world inventory, never the hidden food
consequence. An offline controller applies exactly one nonmotor Competition /
Action Control recommendation per capture. Only the actual chosen outcome can
enter the NEXT capture's observational readout. This is *not* a born I2, true
motor autonomy, authenticated first-person evidence or an M11 WorldBody.

The fixed toy priors (A=3 collect, B=4 eat, C=1 drink) are experimenter inputs.
A visible berry in inventory offers B. No hidden delta enters valuation; all
regime labels and inventory counts below belong to the research harness.
Results are exploratory, especially after the documented post-hoc +5 offset
in PR #784. Distinct runs start with the same synthetic UC, but spend may
differ because actual offered candidates and advice differ.
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
    LIFE, A, B, C, claim, ObservationPort, Current, Safety, Terminal, Values,
)
from test_science_first_behavioral_slice import TinyControlledWorld
from test_science_first_sequential_shadow import _semantic
from test_science_first_chosen_outcome_adaptation import RecordedSource
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.chosen_outcome_study import (
    ObservedChosenResult, ChosenOutcomeValuationStudy,
)

CAPTURES = (10, 18, 26, 34, 42, 50, 58, 66)
INITIAL_SYNTHETIC_UC = 60
# Fixed BEFORE interpreting the new test's outcome; not physiological priors.
PRIORS = {A: 3, B: 4, C: 1}
STABLE = (8,) * 8
ADVERSE = (-8,) * 8
REVERSAL = (8, 8, 8, -8, -8, -8, -8, -8)
RECOVERY = (8, -8, -8, -8, 8, 8, 8, 8)
NEUTRAL = (0,) * 8
REGIMES = {
    "stable": STABLE, "adverse": ADVERSE, "reversal": REVERSAL,
    "recovery": RECOVERY, "neutral": NEUTRAL,
}


class InventoryOfferedWorld(TinyControlledWorld):
    """Same physical law as earlier G2 tests; only availability is observable.

    Eating is not offered when inventory is empty. The private inventory count
    and hidden completion delta NEVER enter valuation or the subjective claim.
    """

    def visible(self) -> tuple[str, ...]:
        return tuple(sorted((A, B, C) if self._inventory else (A, C)))


def run_unforced(regimes: tuple[int, ...], *, variant: str,
                 withhold_outcome_index: int | None = None) -> tuple[dict, ...]:
    """Research controller follows each opinion or does nothing, never scripts B."""
    if (type(regimes) is not tuple or len(regimes) != len(CAPTURES) or
            any(type(delta) is not int for delta in regimes) or
            variant not in ("fixed", "observational", "revisit") or
            (withhold_outcome_index is not None and
             (type(withhold_outcome_index) is not int or
              not 0 <= withhold_outcome_index < len(CAPTURES)))):
        raise ValueError("fixed eight-capture research protocol required")
    with tempfile.TemporaryDirectory() as temporary:
        db = Path(temporary) / "one-synthetic-cognition-owner.sqlite"
        world = InventoryOfferedWorld(completion_delta=regimes[0])
        observation_source = ObservationPort()
        chosen_source = RecordedSource()
        history: list[ObservedChosenResult] = []
        rows: list[dict] = []
        spent = 0
        ports = dict(
            path=db, life_ref=LIFE, observation_source=observation_source,
            current_source=Current(), safety_source=Safety(),
            terminal_source=Terminal(),
            genesis_ref="genesis:unforced-g2-" + variant,
        )
        for index, (step, hidden_delta) in enumerate(zip(CAPTURES, regimes)):
            available = world.visible()
            current = observation_source.add(claim(step, visible=available))
            valuation = (
                Values(PRIORS) if variant == "fixed" else
                ChosenOutcomeValuationStudy(
                    claim=current, results=tuple(history),
                    source=chosen_source, priors=PRIORS,
                    revisit_after=2 if variant == "revisit" else None,
                    revisit_bonus=9 if variant == "revisit" else 0,
                )
            )
            fixture = (
                CognitiveCycleFixture.create(
                    synthetic_uc=INITIAL_SYNTHETIC_UC,
                    valuation_source=valuation, **ports,
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
            advice = _semantic(
                db, index + 1, receipt.control_suggested_candidate_ref,
            )
            # NEVER infer motor authority from this advisory receipt. The
            # separate researcher merely follows it in a test-world function.
            assert receipt.motor_authority == "NONE"
            assert advice is None or advice in available
            cost = receipt.intake_uc + receipt.competition_uc + receipt.control_uc
            assert receipt.intake_uc == 1
            assert receipt.competition_uc == len(available)
            assert receipt.control_uc == (0 if advice is None else 1)
            spent += cost
            assert fixture.audit()["remaining_synthetic_uc"] == INITIAL_SYNTHETIC_UC - spent
            assert fixture.audit()["feedback_version"] == 0
            assert fixture.audit()["m11_authenticated"] is False
            assert CognitiveCycleFixture.reopen(
                valuation_source=valuation, **ports,
            ).audit() == fixture.audit()

            # Only AFTER paid advice may the experimenter set the hidden
            # world regime and apply the *same* suggested single action.
            # NO forced second step, no fabricated counterfactual, no shadow.
            observed_net = None
            withheld = False
            if advice is not None:
                world._completion_delta = hidden_delta
                event = world.intervene(step=step + 1, semantic=advice)
                observed_net = event.lived_delta
                withheld = index == withhold_outcome_index
                if not withheld:
                    result = ObservedChosenResult(
                        LIFE, current.capture.ref, advice, step + 1,
                        f"observed:unforced:{step}", observed_net,
                    )
                    chosen_source.add(result)
                    history.append(result)
            rows.append({
                "cycle": index,
                "capture_step": step,
                "visible": available,
                "hidden_regime_research_only": hidden_delta,
                "advice": advice,
                "controller_followed": advice,  # None means NO intervention
                "controller_forced_action": False,
                "observed_net": observed_net,
                "withheld_from_valuation": withheld,
                "inventory_after_research_only": world._inventory,
                "synthetic_uc_step": cost,
                "synthetic_uc_cumulative": spent,
                "motor_authority": receipt.motor_authority,
            })
        return tuple(rows)


def action_letters(rows: tuple[dict, ...]) -> str:
    letters = {A: "A", B: "B", C: "C", None: "_"}
    return "".join(letters[row["advice"]] for row in rows)


def net(rows: tuple[dict, ...]) -> int:
    return sum(row["observed_net"] for row in rows
               if row["observed_net"] is not None)


class UnforcedActionChainG2Tests(unittest.TestCase):
    def test_each_action_is_advised_without_scripted_eating_or_motor_right(self):
        """Negative/positive conditions and ablations retain losses and costs."""
        expected = {
            "stable": {"fixed": ("ABABABAB", 16, 36),
                       "observational": ("ABABABAB", 16, 36),
                       "revisit": ("ABABABAB", 16, 36)},
            "adverse": {"fixed": ("ABABABAB", -48, 36),
                        "observational": ("ABAAAAAA", -24, 38),
                        "revisit": ("ABAABAAB", -40, 38)},
            "reversal": {"fixed": ("ABABABAB", -32, 36),
                         "observational": ("ABABAAAA", -16, 37),
                         "revisit": ("ABABAABA", -24, 37)},
            "recovery": {"fixed": ("ABABABAB", -16, 36),
                         "observational": ("ABAAAAAA", -24, 38),
                         "revisit": ("ABAABBAB", 0, 37)},
            "neutral": {"fixed": ("ABABABAB", -16, 36),
                        "observational": ("ABA_____", -6, 33),
                        "revisit": ("ABA_____", -6, 33)},
        }
        report = {}
        for name, regimes in REGIMES.items():
            report[name] = {}
            for variant in ("fixed", "observational", "revisit"):
                with self.subTest(regime=name, variant=variant):
                    rows = run_unforced(regimes, variant=variant)
                    self.assertEqual(len(rows), len(CAPTURES))
                    self.assertTrue(all(
                        r["advice"] == r["controller_followed"] and
                        not r["controller_forced_action"] and
                        r["motor_authority"] == "NONE"
                        for r in rows
                    ))
                    # The experimenter never gives the agent a hidden regime,
                    # only its directly available action names. B is offered
                    # only AFTER collection and disappears once consumed.
                    for row in rows:
                        self.assertEqual(B in row["visible"],
                                         row["cycle"] != 0 and
                                         # Current inventory BEFORE actuation
                                         (rows[row["cycle"] - 1][
                                            "inventory_after_research_only"] > 0))
                    trace = (action_letters(rows), net(rows),
                             rows[-1]["synthetic_uc_cumulative"])
                    self.assertEqual(trace, expected[name][variant])
                    report[name][variant] = {
                        "advice_trace": trace[0],
                        "net": trace[1],
                        "paid_synthetic_uc": trace[2],
                        "controller_forced_actions": 0,
                    }
        self.assertEqual(report["stable"]["fixed"]["advice_trace"],
                         report["stable"]["observational"]["advice_trace"])
        self.assertLess(report["recovery"]["observational"]["net"],
                        report["recovery"]["fixed"]["net"])
        self.assertGreater(report["recovery"]["revisit"]["net"],
                           report["recovery"]["observational"]["net"])
        self.assertNotEqual(report["adverse"]["fixed"]["paid_synthetic_uc"],
                            report["adverse"]["observational"]["paid_synthetic_uc"])
        print("I2_UNFORCED_G2 " +
              json.dumps(report, sort_keys=True, separators=(",", ":")))

    def test_missing_adverse_eating_outcome_prevents_early_avoidance(self):
        """One physical consequence can occur without admitted evidence."""
        observed = run_unforced(ADVERSE, variant="observational")
        withheld = run_unforced(
            ADVERSE, variant="observational", withhold_outcome_index=1,
        )
        self.assertEqual(action_letters(observed), "ABAAAAAA")
        self.assertEqual(action_letters(withheld), "ABABAAAA")
        self.assertTrue(withheld[1]["withheld_from_valuation"])
        self.assertFalse(observed[1]["withheld_from_valuation"])
        self.assertEqual(net(observed), -24)
        self.assertEqual(net(withheld), -32)
        self.assertEqual(withheld[3]["advice"], B)
        self.assertTrue(all(row["controller_forced_action"] is False
                            for row in withheld))


if __name__ == "__main__":
    unittest.main()
