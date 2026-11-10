"""Engineering-only live first-person scoring, source and decision isolation."""
import unittest
from unittest.mock import patch

from i3.lab import stage2_lived_distress_shadow_engineering as ENG
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World
from i3.lab.dev_worlds import dev_open_field
from i3.runtime.life import run_life


class LivedShadowEngineeringTests(unittest.TestCase):
    def test_source_is_reference_only_and_preoutcome(self):
        source = Mind(midpoint(), 19)
        witness = ENG.LivedDistressShadowWitness(19)
        # No synthetic memory injection or hidden World state.
        witness.before_actual_step(source, {"body": (70.,60.,50.,90.,80.)}, "attendre")
        self.assertIsNone(witness.report()["first_event"])
        self.assertEqual(witness.report()["status"], "NO_ELIGIBLE_PERSONAL_HISTORY")
        self.assertFalse(witness.report()["shadow_computation_physically_paid"])
        self.assertEqual(witness.report()["scientific_lives"], 0)

    def test_misordered_or_forged_event_rejected(self):
        witness = ENG.LivedDistressShadowWitness(19)
        witness.pending = True
        with self.assertRaises(RuntimeError):
            witness.before_actual_step(None, {}, "attendre")
        with self.assertRaises(RuntimeError):
            witness.report()
        witness.pending = False
        with self.assertRaises(ValueError):
            ENG.LivedDistressShadowWitness(-1)

    def test_two_matched_actual_engineering_lives_are_neutral(self):
        report = ENG.rehearse()
        self.assertEqual(report["engineering_matched_on_off_pairs"], 2)
        self.assertEqual(report["physical_and_decision_parity_pairs"], 2)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertFalse(report["shadow_cpu_physically_paid"])
        self.assertFalse(report["stage2_2_activation"])
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(report["real_first_person_scored_windows"], sum(
            x["first_event"] is not None for x in report["rows"]))
        for row in report["rows"]:
            event = row["first_event"]
            if event:
                self.assertTrue(event["frozen_before_actual_world_step"])
                self.assertTrue(event["preoutcome_prediction_sha256"])
                self.assertEqual(event["actual_outcome"]["status"],
                                 "SCORED_OBSERVED_FIRST_PERSON_OUTCOME")
                self.assertEqual(event["shadow_replay_updates_per_arm"], 3)
                self.assertGreaterEqual(event["past_memories_available"], 6)

    def test_spy_is_restored_after_observation(self):
        old_decide, old_step = Mind.decide, World.step
        ENG.run_observed_reference(midpoint(), dev_open_field(), 920041, 8)
        self.assertIs(Mind.decide, old_decide)
        self.assertIs(World.step, old_step)

    def test_only_world_step_can_supply_scored_actual_outcome(self):
        spy = ENG.LivedDistressShadowWitness(920041)
        # An outcome without an original frozen prediction stays unscored.
        spy.after_actual_step("attendre", {"dead": (), "body": (70.,60.,50.,90.,80.)})
        self.assertEqual(spy.report()["scored_real_world_outcomes"], 0)


if __name__ == "__main__":
    unittest.main()
