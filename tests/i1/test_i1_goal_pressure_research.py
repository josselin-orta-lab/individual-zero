"""Exact I1 goal-pressure research checks, no actions or motor simulation.

The calibrated arms change only the new individual's GoalManager thresholds.
These tests use pressure proposals that can actually be produced by I1's
temperament-normalized Value/Needs, never introduce a forced water command.
"""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from i1.contracts import GoalProposal
from i1.modules.goal_manager import GoalManager, GoalManagerConfig
from run_i1_minimal_learning import GOAL_ARBITRATION_ARMS


def proposal(kind, pressure, *, t=1, cycle=1):
    target = {"recover_energy":"energy", "drink":"water", "eat":"food"}[kind]
    return GoalProposal(
        id=f"goal-proposal:{kind}:{t}:{cycle}",
        source="value_needs",
        goal_type=kind, target=target,
        base_pressure=pressure, current_pressure=pressure,
        justification_ref=f"need-alert:{target}:{t}:{cycle}",
        t_monde=t, cycle=cycle, rule_version="study",
    )


def manager(arm):
    hysteresis, critical = GOAL_ARBITRATION_ARMS[arm]
    cfg = GoalManagerConfig(
        version="i1-study-"+arm, p_min=.1,
        replacement_hysteresis=hysteresis, critical_pressure=critical,
        impossible_failures_required=2, refractory_steps=3,
    )
    return GoalManager(cfg)


class GoalPressureResearchTests(unittest.TestCase):
    def test_registered_arms_are_exact_and_distinct(self):
        self.assertEqual(GOAL_ARBITRATION_ARMS, {
            "baseline": (.1,.9),
            "calibrated-004": (.04,.35),
            "responsive-002": (.02,.25),
        })

    def test_critical_thirst_can_replace_existing_energy_goal(self):
        # Birth temperament example: integrity weight 1.3956016, so the
        # maximum water pressure is .429922 and energy pressure .358268.
        factor = 1.3956016
        energy = .5/factor
        water = .6/factor
        for arm in GOAL_ARBITRATION_ARMS:
            with self.subTest(arm=arm):
                owner = manager(arm)
                self.assertEqual(owner.arbitrate([proposal("recover_energy",energy)],
                                                 t_monde=1,cycle=1).goal_type,
                                 "recover_energy")
                actual = owner.arbitrate([
                    proposal("recover_energy",energy,t=2),
                    proposal("drink",water,t=2),
                ],t_monde=2,cycle=1)
                self.assertEqual(actual.goal_type, "recover_energy" if arm=="baseline" else "drink")

    def test_minor_pressure_fluctuations_do_not_cause_chattering(self):
        for arm in ("calibrated-004","responsive-002"):
            with self.subTest(arm=arm):
                owner=manager(arm)
                self.assertEqual(owner.arbitrate([proposal("drink",.43)],
                                                 t_monde=1,cycle=1).goal_type,"drink")
                # Both pressures remain nearly equal within the new hyst.
                for t in range(2,12):
                    owner.arbitrate([proposal("drink",.43,t=t),
                                     proposal("recover_energy",.44,t=t)],
                                    t_monde=t,cycle=1)
                    self.assertEqual(owner.active_goal.goal_type,"drink")

    def test_refractory_is_bypassable_by_physically_reachable_need(self):
        for arm in GOAL_ARBITRATION_ARMS:
            with self.subTest(arm=arm):
                owner=manager(arm)
                owner.arbitrate([proposal("recover_energy",.4)],t_monde=1,cycle=1)
                self.assertFalse(owner.note_non_plannable(
                    material_context_hash="same-percept",t_monde=2))
                self.assertTrue(owner.note_non_plannable(
                    material_context_hash="same-percept",t_monde=2))
                # One third of body range is a real feasible pressure,
                # yet the canonical critical pressure .9 is unreachable.
                later=owner.arbitrate([proposal("recover_energy",.4,t=3)],
                                      t_monde=3,cycle=1)
                self.assertEqual(later is not None, arm!="baseline")

    def test_no_motor_shortcuts_exist_in_intervention(self):
        # Only the config changes. No user-tuned effect enters policy runtime.
        self.assertGreater(GOAL_ARBITRATION_ARMS["baseline"][0],
                           GOAL_ARBITRATION_ARMS["calibrated-004"][0])
        self.assertEqual(set(GOAL_ARBITRATION_ARMS),{
            "baseline","calibrated-004","responsive-002",
        })


if __name__=="__main__":
    unittest.main()
