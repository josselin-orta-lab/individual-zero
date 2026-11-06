"""P5a selective retention falsifiers, DEVELOPMENT worlds only.

No P3/P4 selection, validation or reserve lives are opened. These tests
exercise computation actually executed and charged before an intervention.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero, midpoint
from i3.modules.mind import Mind
from i3.runtime.life import run_life


class P5aSelectiveRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p2_ecologies.world_for("stable", "development", 16)
        cls.genome = generation_zero(777)

    def life(self, mode, horizon=90):
        return run_life(self.genome, self.spec, 245, horizon,
                        learning_mode=mode, observer_mind_digest=True,
                        keep_trace=True)

    def test_default_normal_retains_historical_life_behavior(self):
        baseline = run_life(self.genome, self.spec, 245, 90,
                            observer_mind_digest=True)
        explicit = self.life("normal")
        for key in ("terminal", "steps_lived", "trace_head", "actions",
                    "final_body", "cognitive_accounting",
                    "outcome_model_sha256", "spatial_beliefs_sha256"):
            self.assertEqual(baseline[key], explicit[key])

    def test_each_selective_ablation_executes_paid_learning(self):
        normal = self.life("normal")
        for mode in ("discard_effects", "discard_values", "discard_replay"):
            with self.subTest(mode=mode):
                life = self.life(mode)
                self.assertEqual(life["learning_intervention"], mode)
                self.assertGreater(life["retained_outcome_learning_updates"], 0)
                self.assertGreater(life["cognitive_accounting"]["learning_updates"], 0)
                self.assertEqual(life["cognitive_accounting"]["shortfall_steps"], 0)
                self.assertEqual(life["cognitive_accounting"]["pending_replays"], 0)
                self.assertEqual(life["manifest"]["world_sha256"],
                                 normal["manifest"]["world_sha256"])
                self.assertTrue(life["spatial_beliefs_sha256"])
                self.assertEqual(len(life["observer_internal_position"]), 2)
                for record in life["trace"]:
                    phases = record["funding_phases"]
                    for phase in ("decision", "learning"):
                        for channel in ("energy", "vigilance"):
                            bill = phases[phase]["accounting"][channel]
                            self.assertEqual(bill["unpaid"], 0.0)
                            self.assertAlmostEqual(bill["requested"], bill["paid"])
                    if record["dead"]:
                        self.assertEqual(sum(phases["learning"]["work"].values()), 0)

    def test_discarded_effects_cannot_be_retained(self):
        normal = self.life("normal")
        no_effects = self.life("discard_effects")
        self.assertNotEqual(normal["outcome_model_sha256"],
                            no_effects["outcome_model_sha256"])

    def test_discard_values_retains_other_learning(self):
        normal = self.life("normal")
        no_values = self.life("discard_values")
        self.assertNotEqual(normal["outcome_model_sha256"],
                            no_values["outcome_model_sha256"])

    def test_replay_ablation_only_discards_replay_contribution(self):
        genome = midpoint()
        body = (65., 70., 70., 80., 65.)
        result = {"body": (64., 69., 69., 80., 65.),
                  "dead": [], "moved": False}
        base = Mind(genome, 42)
        base.last = (body, ("dormir",), "dormir", None)
        base.buffer.append((1.0, body, result["body"], False))
        normal = deepcopy(base)
        no_replay = deepcopy(base)
        n = normal.learn_from_outcome(result, replay_limit=1)
        d = no_replay.learn_from_outcome(result, replay_limit=1,
                                          replay_retention=False)
        self.assertEqual(n, d)
        self.assertEqual(n, 1)
        self.assertEqual(normal.effects.stats, no_replay.effects.stats)
        self.assertNotEqual(normal.values, no_replay.values)

    def test_only_known_modes_accepted(self):
        with self.assertRaises(ValueError):
            self.life("unpaid_skip_learning")


if __name__ == "__main__":
    unittest.main()
