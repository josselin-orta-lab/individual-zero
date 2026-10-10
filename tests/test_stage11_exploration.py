"""Unit and integration tests for Stage 11 developmental P-48 slice."""
import unittest
from dataclasses import replace
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch, sentinel

from i0.modules.exploration import Exploration, ExplorationConfig
from i0.modules.causal_model import CausalModelConfig
from i0.modules.causal_test_planning import Stage9OptionEvaluator
from i0.interfaces import PrimitiveCommand
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from test_stage9_causal_test_targets import hypothesis


def causal_option(version=1):
    return SimpleNamespace(
        motive_ref=SimpleNamespace(
            type="test_causal", id="test_causal:causal:hydration",
        ),
        id=f"option:causal-test:causal:hydration:v{version}",
        provenance="test_causal",
    )


def grounded_state(interventions=()):
    return {
        "published": [{
            "ref": "causal:hydration", "version": 1,
            "causal_status": "hypothese_causale", "safety_status": "aucun",
        }],
        "causal_observations": [
            {"identifier": "treated", "contingency_ref": "causal:hydration",
             "observation_ref": "world:1", "source": "monde",
             "independent_episode": True, "cause_present": True},
            {"identifier": "control", "contingency_ref": "causal:hydration",
             "observation_ref": "world:2", "source": "monde",
             "independent_episode": True, "cause_present": False},
        ],
        "causal_review_proofs": [{
            "identifier": "review:water", "contingency_ref": "causal:hydration",
            "contrasting_pairs": [["treated", "control"]],
        }],
        "causal_interventions": [
            {"identifier": key, "contingency_ref": "causal:hydration",
             "action_applied": True, "source": "monde"}
            for key in interventions
        ],
    }


def dev_exploration(coefficient=0.0):
    return Exploration(
        ExplorationConfig("p48-test-v1", 0.5, 0.3, 2, 2),
        coefficient=coefficient,
    )


def hydration_runtime():
    base = build_stage11_reference_runtime()
    causal = CausalModelConfig(
        version="stage11-dev-hydration-v1", n1=2, n2=2, n_sec=2, m_sec=2,
        causal_predicates=("hydration_effect",),
        safe_test_actions=(("hydration_effect", "water", "boire"),),
    )
    config = replace(
        base._stage11_config,
        stage9=replace(base._stage11_config.stage9, causal=causal),
    )
    return Stage11Runtime(
        world_config=base.world.config, layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=base.equipment,
    )


class ExplorationTests(unittest.TestCase):
    def test_missing_proof_is_unavailable_not_zero(self):
        model = dev_exploration()
        self.assertEqual(model.motivation(causal_option()).status, "unavailable")
        source = grounded_state()
        source["causal_review_proofs"] = []
        model.observe_causal_state(source)
        self.assertEqual(model.motivation(causal_option()).status, "unavailable")

    def test_repeated_proposals_do_not_create_visits_or_progress(self):
        model = dev_exploration()
        source = grounded_state()
        model.observe_causal_state(source)
        initial = model.motivation(causal_option())
        self.assertGreater(initial.value, 0)
        for _ in range(20):
            model.observe_causal_state(source)
        self.assertEqual(model.motivation(causal_option()), initial)
        self.assertEqual(model.export_causal_state()["questions"][0][1]["visits"], 0)

    def test_noisy_tv_and_snapshot_replay(self):
        model = dev_exploration()
        model.observe_causal_state(grounded_state())
        model.observe_causal_state(grounded_state(("first",)))
        model.observe_causal_state(grounded_state(("first", "second")))
        self.assertEqual(model.motivation(causal_option()).value, 0.0)
        self.assertEqual(model.cibles(), ())
        restored = dev_exploration()
        restored.restore_causal_state(model.export_causal_state())
        self.assertEqual(restored.export_causal_state(), model.export_causal_state())

    def test_applied_actions_habituate_without_fabricating_interventions(self):
        exploration = dev_exploration()
        exploration.observe_causal_state(grounded_state())
        option = causal_option()
        self.assertEqual(exploration.export_causal_state()["questions"][0][1]["ids"], ())
        self.assertTrue(exploration.record_applied_causal_test(
            option=option, sent_step=8,
        ))
        self.assertFalse(exploration.record_applied_causal_test(
            option=option, sent_step=8,
        ))
        self.assertTrue(exploration.record_applied_causal_test(
            option=option, sent_step=9,
        ))
        q = exploration.export_causal_state()["questions"][0][1]
        self.assertEqual(q["visits"], 2)
        self.assertEqual(q["stagnant"], 2)
        self.assertEqual(q["ids"], ())
        self.assertEqual(exploration.motivation(option).value, 0.0)
        self.assertTrue(exploration.boredom_detected())
        self.assertEqual(exploration.cibles(), ())
        self.assertFalse(exploration.record_applied_causal_test(
            option=causal_option(version=999), sent_step=10,
        ))
        with self.assertRaises(ValueError):
            exploration.record_applied_causal_test(
                option=option, sent_step=True,
            )

    def test_later_physically_joined_intervention_is_not_second_visit(self):
        exploration = dev_exploration()
        exploration.observe_causal_state(grounded_state())
        option = causal_option()
        exploration.record_applied_causal_test(option=option, sent_step=8)
        next_state = grounded_state(("trial:first",))
        next_state["causal_interventions"][0].update({
            "command_ref": option.id, "emitted_step": 8,
        })
        exploration.observe_causal_state(next_state)
        q = exploration.export_causal_state()["questions"][0][1]
        self.assertEqual(q["ids"], ("trial:first",))
        self.assertEqual(q["visits"], 1)
        self.assertEqual(q["stagnant"], 1)
        self.assertEqual(q["progress"], 0.0)

    def test_invalidated_question_cannot_survive_and_earn_interest(self):
        exploration = dev_exploration()
        exploration.observe_causal_state(grounded_state())
        self.assertEqual(exploration.motivation(causal_option()).status, "available")
        empty = grounded_state()
        empty["published"] = []
        exploration.observe_causal_state(empty)
        self.assertEqual(exploration.motivation(causal_option()).status, "unavailable")
        self.assertEqual(exploration.cibles(), ())
        self.assertEqual(exploration.export_causal_state()["questions"], [])

    def test_snapshot_rejects_corrupted_visit_ledger_atomically(self):
        exploration = dev_exploration()
        exploration.observe_causal_state(grounded_state())
        exploration.record_applied_causal_test(
            option=causal_option(), sent_step=8,
        )
        saved = exploration.export_causal_state()
        for mutation in ("negative_visits", "duplicate_applied", "wrong_schema"):
            corrupted = deepcopy(saved)
            if mutation == "negative_visits":
                corrupted["questions"][0][1]["visits"] = -5
            elif mutation == "duplicate_applied":
                keys = corrupted["questions"][0][1]["executed_keys"]
                corrupted["questions"][0][1]["executed_keys"] = keys * 2
            else:
                corrupted["state_schema"] = "untrusted"
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    exploration.restore_causal_state(corrupted)
                self.assertEqual(exploration.export_causal_state(), saved)

    def test_temperament_affects_intrinsic_only(self):
        low, high = dev_exploration(-1), dev_exploration(1)
        for model in (low, high):
            model.observe_causal_state(grounded_state())
        self.assertEqual(low.motivation(causal_option()).value, 0)
        self.assertGreater(high.motivation(causal_option()).value, 0)
        self.assertEqual(high.motivation(causal_option(version=2)).status, "unavailable")


class Stage11IntegratedTests(unittest.TestCase):
    def test_stage11_runs_without_duplicate_snapshot_owner(self):
        runtime = build_stage11_reference_runtime()
        names = [owner.owner_id for owner in runtime.causal_owners]
        self.assertEqual(names.count("exploration"), 1)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertTrue(runtime.journal.verify())

    def test_lived_proof_candidate_reaches_ordinary_competition(self):
        runtime = hydration_runtime()
        hypothesis(runtime.causal_model)
        runtime.run_step()
        entries = [
            item.causal_event for item in runtime.journal.entries
            if item.causal_event.get("kind") == "stage11_intrinsic_evaluation"
        ]
        self.assertTrue(entries)
        self.assertTrue(any(
            row["data"]["status"] == "evaluated"
            and row["data"]["intrinsic_value"] > 0
            for row in entries
        ))
        self.assertTrue(runtime.journal.verify())
        self.assertEqual(
            runtime.competition._config.gain,
            build_stage9_reference_runtime().competition._config.gain,
        )

    def test_forged_causal_plan_cannot_earn_intrinsic_evidence(self):
        runtime = hydration_runtime()
        hypothesis(runtime.causal_model)
        runtime.run_step()
        proposal = next(
            p for p in runtime.competition.candidate_proposals
            if p.option.motive_ref.type == "test_causal"
        )
        evaluator = runtime.stage8_option_evaluator
        self.assertTrue(evaluator._safe_causal_test_shape(proposal))
        step = proposal.plan.steps[0]
        malformed = (
            replace(proposal, plan=None),
            replace(proposal, plan=replace(
                proposal.plan, steps=(
                    replace(step, command=PrimitiveCommand(
                        "manger", {"target": "berry_b"},
                    )),
                ),
            )),
            replace(proposal, plan=replace(
                proposal.plan, steps=(
                    replace(step, command=PrimitiveCommand(
                        "boire", {"target": "unknown"},
                    )),
                ),
            )),
            replace(proposal, option=replace(
                proposal.option, learning_signature="false_intrinsic_reward",
            )),
            replace(proposal, option=replace(
                proposal.option, goal_ref="arbitrary_goal",
            )),
            replace(proposal, plan=replace(
                proposal.plan, steps=(step, step),
            )),
        )
        for candidate in malformed:
            with self.subTest(candidate=candidate):
                self.assertFalse(evaluator._safe_causal_test_shape(candidate))
                # Invalid option never consults Exploration's motivational
                # valuation, even if its motive/id imitates a valid test.
                with patch.object(
                    Stage9OptionEvaluator, "evaluate",
                    return_value=sentinel.historical_unscored,
                ) as historical, patch.object(
                    runtime.exploration, "motivation",
                    side_effect=AssertionError("forged plan was rewarded"),
                ):
                    result = evaluator.evaluate(
                        proposal=candidate, evaluation_state=None,
                        initial_state=None, cycle=1, t_monde=1,
                    )
                self.assertIs(result, sentinel.historical_unscored)
                historical.assert_called_once()

    def test_exact_reexecution_on_public_fixture(self):
        left, right = hydration_runtime(), hydration_runtime()
        for runtime in (left, right):
            hypothesis(runtime.causal_model)
            for _ in range(4):
                runtime.run_step()
        self.assertEqual(left.journal.canonical_bytes(), right.journal.canonical_bytes())
        self.assertEqual(left.exploration.export_causal_state(),
                         right.exploration.export_causal_state())


if __name__ == "__main__":
    unittest.main()
