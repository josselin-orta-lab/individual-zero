"""P5e full funded competition witness: synthetic and development-only parity."""
from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero
from i3.modules.mind import Mind
from i3.runtime.life import run_life
from i3.runtime.competition_observer import capture_competition


class P5eFullCompetitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.genome = generation_zero(901)
        cls.spec = p2_ecologies.world_for("stable", "development", 32)

    def test_flag_rejects_non_boolean(self):
        with self.assertRaises(TypeError):
            Mind(self.genome, 17, observer_full_competition=1)
        with self.assertRaises(TypeError):
            run_life(self.genome, self.spec, 17, 1,
                     observer_full_competition=1)

    def test_real_original_decisions_are_identical_with_and_without_observer(self):
        # Exactly same code, genome, seed, ecology and payable operations.
        # These are software development controls, not a new scientific life.
        for mode in ("normal", "discard_curiosity_bonus"):
            common = dict(
                keep_trace=True, observer_mind_digest=True,
                score_addend_mode=mode)
            control = run_life(self.genome, self.spec, 860032, 72, **common)
            observed = run_life(
                self.genome, self.spec, 860032, 72,
                observer_full_competition=True, **common)
            combined = run_life(
                self.genome, self.spec, 860032, 72,
                observer_full_competition=True,
                observer_resource_acquisition=True, **common)
            for pair in (observed, combined):
                for key in ("manifest_id", "trace_head", "evidence_head",
                            "actions", "terminal", "final_body",
                            "cognitive_accounting", "steps_lived",
                            "outcome_model_sha256", "spatial_beliefs_sha256",
                            "learning_intervention", "replays_executed"):
                    self.assertEqual(control.get(key), pair.get(key), (mode, key))
                rows = pair["observer_full_competition"]["steps"]
                self.assertEqual(len(rows), pair["steps_lived"])
                for row, original in zip(rows, pair["trace"]):
                    obs = original["info"]["observer"]
                    self.assertEqual(
                        len(row["paid_option_scores"]), obs["scored_options"])
                    self.assertEqual(row["physical_action"], original["action"])
                    self.assertEqual(row["chosen_option"], original["option"])
                    comp = row["competition"]
                    self.assertIsNotNone(comp)
                    paid = {w["option"]: w["total_score"] for w in row["paid_option_scores"]}
                    self.assertEqual(set(paid), set(comp["scored_order"]))
                    self.assertEqual(set(paid), set(comp["normalized_evidence"]))
                    self.assertEqual(set(paid), set(comp["thresholds"]))
                    self.assertEqual(set(paid), set(comp["accumulators_before"]))
                    self.assertEqual(set(paid), set(comp["accumulators_after_residual"]))
                    self.assertIn(comp["winner_before_control"], paid)
                    self.assertIn(comp["selection_mechanism"],
                                  ("threshold_crossing", "raw_score_fallback"))
                    if comp["status"] == "ACTION_ADMITTED":
                        self.assertEqual(comp["final_admitted_option"],
                                         original["option"])
                    self.assertLessEqual(
                        comp["paid_competition_cycles"],
                        row["paid_decision_work"]["cycles"])
                    self.assertEqual(row["inventory_before_decision"],
                                     [list(item) for item in
                                      original["info"].get("capture_inventory", [])]
                                     if "capture_inventory" in original["info"] else
                                     row["inventory_before_decision"])
            self.assertNotIn("observer_full_competition", control)
            self.assertNotIn("observer_resource_acquisition", control)
            self.assertNotIn("observer_resource_acquisition", observed)

    def test_direct_competition_selection_ties_and_state_are_inert(self):
        scored = [("manger:tok0", 0.1), ("attendre", 1.0), ("dormir", -0.5)]
        normal = Mind(self.genome, 12)
        inspected = Mind(self.genome, 12, observer_full_competition=True)
        for mind in (normal, inspected):
            mind.acc = {"manger:tok0": 0.3, "attendre": 0.3}
            mind.intention = "manger:tok0"
        for budget_cycles in (0, 1, 8):
            a = normal._compete(scored, budget_cycles)
            b = inspected._compete(scored, budget_cycles)
            self.assertEqual(a, b)
            self.assertEqual(normal.acc, inspected.acc)
            self.assertEqual(normal.rng.getstate(), inspected.rng.getstate())
            self.assertEqual(normal.intention, inspected.intention)
            self.assertEqual(
                inspected._observer_competition["paid_competition_cycles"], b[1])
            self.assertEqual(inspected._observer_competition["winner_before_control"], b[0])

    def test_incomplete_or_forged_competition_is_rejected(self):
        from i3.modules.body import CognitiveBudget, CognitiveWork, BodyLaws
        body = (80., 70., 70., 80., 80.)
        allowance = CognitiveBudget(body, BodyLaws())
        info = {
            "option": "manger:tok0", "funding": "FUNDED",
            "observer": {
                "score_witness": [{
                    "option": "manger:tok0", "base_return": 1.,
                    "curiosity_bonus_applied": 0.2,
                    "risk_penalty_applied": -0.1,
                    "total_score": 1.1}],
                "offered_options": 1, "scored_options": 1,
                "offered_families": {"resource": 1},
                "scored_families": {"resource": 1},
                "decision_outcome": "action_admitted",
            },
        }
        with self.assertRaises(RuntimeError):
            capture_competition(
                info=info, action="manger", param="t",
                work=CognitiveWork(), allowed=allowance,
                capture={"body": body, "inventory": (("t", 1),)})
        info["observer"]["competition_witness"] = {
            "scored_order": ["manger:tok0"],
            "winner_before_control": "manger:tok0",
            "control_order": ["manger:tok0"],
            "control_attempts": [{"option": "manger:tok0", "admitted": True}],
            "final_admitted_option": "manger:tok0",
            "final_admitted_action": "manger",
            "paid_competition_cycles": 0,
        }
        receipt = capture_competition(
            info=info, action="manger", param="t",
            work=CognitiveWork(), allowed=allowance,
            capture={"body": body, "inventory": (("t", 1),)})
        self.assertEqual(receipt["physical_action"], "manger")
        info["observer"]["score_witness"][0]["total_score"] = 15
        with self.assertRaises(RuntimeError):
            capture_competition(
                info=info, action="manger", param="t",
                work=CognitiveWork(), allowed=allowance,
                capture={"body": body, "inventory": (("t", 1),)})


if __name__ == "__main__":
    unittest.main()
