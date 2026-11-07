"""P5e full funded competition witness: synthetic and development-only parity."""
from copy import deepcopy
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
                    if comp is None:
                        self.assertEqual(row["scored_options"], 0)
                        self.assertIn(row["decision_outcome"],
                                      ("no_processing_budget", "no_funded_score"))
                        continue
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

            self.assertEqual(
                combined["observer_full_competition"]["steps"],
                observed["observer_full_competition"]["steps"])
            for comp_row, resource_row in zip(
                    combined["observer_full_competition"]["steps"],
                    combined["observer_resource_acquisition"]["steps"]):
                self.assertEqual(comp_row["inventory_before_decision"],
                                 resource_row["capture_inventory"])
                self.assertEqual(comp_row["body_before_decision"],
                                 resource_row["body_before_decision"])
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


    def test_frontier_information_score_schema_is_authenticated_separately(self):
        from i3.modules.body import CognitiveBudget, CognitiveWork, BodyLaws
        body = (80., 70., 30., 80., 80.)
        allowance = CognitiveBudget(body, BodyLaws())
        score = {
            "option": "explorer:1,0",
            "base_return": -10.0,
            "information_value": 1.5,
            "total_score": -8.5,
            "score_kind": "frontier_water_expected_distress",
            "curiosity_bonus_computed": 0.0,
            "curiosity_bonus_applied": 0.0,
            "risk_penalty_computed": 0.0,
            "risk_penalty_applied": 0.0,
        }
        info = {
            "option": "explorer:1,0",
            "funding": "FUNDED",
            "observer": {
                "score_witness": [score],
                "offered_options": 1,
                "scored_options": 1,
                "offered_families": {"explore": 1},
                "scored_families": {"explore": 1},
                "decision_outcome": "action_admitted",
                "competition_witness": {
                    "scored_order": ["explorer:1,0"],
                    "winner_before_control": "explorer:1,0",
                    "control_order": ["explorer:1,0"],
                    "control_attempts": [{
                        "option": "explorer:1,0", "admitted": True}],
                    "final_admitted_option": "explorer:1,0",
                    "final_admitted_action": "se_deplacer",
                    "paid_competition_cycles": 0,
                },
            },
        }
        receipt = capture_competition(
            info=info, action="se_deplacer", param="E",
            work=CognitiveWork(), allowed=allowance,
            capture={"body": body, "inventory": ()})
        self.assertEqual(
            receipt["paid_option_scores"][0]["information_value"], 1.5)

        bad_total = deepcopy(info)
        bad_total["observer"]["score_witness"][0]["total_score"] = -8.4
        with self.assertRaisesRegex(RuntimeError, "forged"):
            capture_competition(
                info=bad_total, action="se_deplacer", param="E",
                work=CognitiveWork(), allowed=allowance,
                capture={"body": body, "inventory": ()})

        bad_information = deepcopy(info)
        bad_information["observer"]["score_witness"][0]["information_value"] = 1.4
        with self.assertRaisesRegex(RuntimeError, "forged"):
            capture_competition(
                info=bad_information, action="se_deplacer", param="E",
                work=CognitiveWork(), allowed=allowance,
                capture={"body": body, "inventory": ()})

        bad_addend = deepcopy(info)
        bad_addend["observer"]["score_witness"][0][
            "curiosity_bonus_computed"] = 0.1
        with self.assertRaisesRegex(RuntimeError, "historical addends"):
            capture_competition(
                info=bad_addend, action="se_deplacer", param="E",
                work=CognitiveWork(), allowed=allowance,
                capture={"body": body, "inventory": ()})

    def test_local_information_field_keeps_historical_score_identity(self):
        from i3.modules.body import CognitiveBudget, CognitiveWork, BodyLaws
        body = (80., 70., 30., 80., 80.)
        allowance = CognitiveBudget(body, BodyLaws())
        info = {
            "option": "attendre",
            "funding": "FUNDED",
            "observer": {
                "score_witness": [{
                    "option": "attendre",
                    "base_return": -5.0,
                    "information_value": 2.0,
                    "total_score": -5.0,
                    "score_kind": "local_expected_distress",
                    "curiosity_bonus_applied": 0.0,
                    "risk_penalty_applied": 0.0,
                }],
                "offered_options": 1,
                "scored_options": 1,
                "offered_families": {"rest": 1},
                "scored_families": {"rest": 1},
                "decision_outcome": "action_admitted",
                "competition_witness": {
                    "scored_order": ["attendre"],
                    "winner_before_control": "attendre",
                    "control_order": ["attendre"],
                    "control_attempts": [{
                        "option": "attendre", "admitted": True}],
                    "final_admitted_option": "attendre",
                    "final_admitted_action": "attendre",
                    "paid_competition_cycles": 0,
                },
            },
        }
        receipt = capture_competition(
            info=info, action="attendre", param=None,
            work=CognitiveWork(), allowed=allowance,
            capture={"body": body, "inventory": ()})
        self.assertEqual(receipt["paid_option_scores"][0]["total_score"], -5.0)


if __name__ == "__main__":
    unittest.main()
