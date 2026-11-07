"""Local-policy software falsifiers, NOT a survival or generalization study."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.information_mind import (InformationMind, StationaryUnknownOutcomes,
    continuation_options, effect_key, local_options)
from i3.modules.information_value import SubjectiveOutcome, paid_information_value
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import PersonalOutcomes, STORE_WORK
from i3.modules.world import World, WorldSpec, WaterSource
from i3.runtime.life import run_life
from i3.lab.stage0_energy import energy_receipt
from i3.lab.stage1_cost_profile import summarize_decision_cost

BASE = "942b973faec73f1020505bd53b841691eb01c590"
BODY = (80., 60., 30., 80., 80.)
ZERO = (0.,) * 5
MODE = "local_information_v1"


def fixture(body=BODY):
    return WorldSpec("local-information-software-fixture", 1, 1, (0, 0), body,
                     water={(0, 0): WaterSource(20.)})


def run(**kwargs):
    return run_life(midpoint(), fixture(), 7, 8, keep_trace=True,
                    protocol="STAGE1_LOCAL_SOFTWARE_ONLY", decision_policy=MODE, **kwargs)


def untimed(result):
    result = deepcopy(result)
    result.pop("mean_step_ms", None)
    result.pop("run_elapsed_ms", None)
    return result


def remember(history, key, delta):
    """Explicitly synthetic personal input, never a scientific acquired history."""
    after = tuple(x + d for x, d in zip(BODY, delta))
    history.observe(key, BODY, CognitiveWork(), CognitiveBudget(after, BodyLaws()))


class LocalStructureTests(unittest.TestCase):
    def setUp(self):
        self.mapping = {(0, 0): (True, ("tok0",)), (1, 0): (False, ()), (0, -1): None}

    def test_no_unseen_move_or_uncarried_meal(self):
        names = [o[0] for o in local_options((0, 0), self.mapping, ())]
        self.assertIn("move:E", names)
        self.assertNotIn("move:N", names)
        self.assertNotIn("move:S", names)
        self.assertNotIn("manger:tok0", names)

    def test_consumption_cannot_reuse_last_item(self):
        opts = local_options((0, 0), self.mapping, (("tok0", 1),))
        eat = next(o for o in opts if o[0] == "manger:tok0")
        after = dict(continuation_options((0, 0), self.mapping, (("tok0", 1),), eat))
        self.assertNotIn("manger:tok0", after)
        two = dict(continuation_options((0, 0), self.mapping, (("tok0", 2),), eat))
        self.assertIn("manger:tok0", two)
        with self.assertRaises(ValueError):
            continuation_options((0, 0), self.mapping, (), eat)

    def test_collection_grants_one_item_not_infinite_stock(self):
        collect = next(o for o in local_options((0, 0), self.mapping, ()) if o[0].startswith("collecter:"))
        after = dict(continuation_options((0, 0), self.mapping, (), collect))
        self.assertIn("manger:tok0", after)
        self.assertNotIn("collecter:tok0", after)
        self.assertEqual(self.mapping[(0, 0)], (True, ("tok0",)))

    def test_drink_does_not_invent_remaining_stock(self):
        drink = next(o for o in local_options((0, 0), self.mapping, ()) if o[0] == "boire")
        self.assertNotIn("boire", dict(continuation_options((0, 0), self.mapping, (), drink)))

    def test_movement_does_not_reveal_new_cells(self):
        move = next(o for o in local_options((0, 0), self.mapping, ()) if o[0] == "move:E")
        after = dict(continuation_options((0, 0), self.mapping, (), move))
        self.assertIn("move:W", after)
        self.assertNotIn("move:E", after)
        self.assertNotIn("collecter:tok0", after)
        self.assertEqual(effect_key(move), ("se_deplacer", None))


class PriorAndBudgetTests(unittest.TestCase):
    def test_birth_has_no_experience_and_no_positive_prior(self):
        mind = InformationMind(midpoint(), 7)
        self.assertEqual(len(mind.personal._samples), 0)
        b = CognitiveBudget(BODY, BodyLaws())
        outcomes = mind.personal.construct(("manger", "tok0"), (("rest", ("dormir", None)),), b)
        self.assertTrue(all(o.probe_delta == ZERO for o in outcomes))
        self.assertTrue(all(o.continuations == (("rest", ZERO),) for o in outcomes))
        self.assertEqual(mind.personal.unknown_reads, 2)
        self.assertEqual(len(mind.personal._samples), 0)
        self.assertGreater(b.work.cycles, 0)

    def test_empirical_support_replaces_prior_without_cross_action_transfer(self):
        h = StationaryUnknownOutcomes(16)
        remember(h, ("manger", "tok0"), (0., -10., 0., -5., 0.))
        b = CognitiveBudget(BODY, BodyLaws())
        outcomes = h.construct(("manger", "new"), (("collect", ("collecter", "new")),), b)
        self.assertEqual(outcomes[0].probe_delta, (0., -10., 0., -5., 0.))
        self.assertEqual(outcomes[0].continuations[0][1], ZERO)
        self.assertEqual(h.unknown_reads, 1)

    def test_joint_episodic_capacity_and_new_birth(self):
        g = midpoint()
        g["genes"]["m_max"] = 33.
        a, b = InformationMind(g, 1), InformationMind(g, 1)
        self.assertEqual(a.m_max + a.personal._samples.maxlen, 33)
        for _ in range(40):
            remember(a.personal, ("attendre", None), ZERO)
        self.assertEqual(len(a.personal._samples), 16)
        self.assertEqual(len(b.personal._samples), 0)
        self.assertEqual(g["genes"]["m_max"], 33.)

    def test_unfunded_processing_never_reads_or_perceives(self):
        w = World(fixture((0., 20., 20., 80., 0.)))
        m = InformationMind(midpoint(), 1)
        with patch.object(m, "perceive", side_effect=AssertionError("unfunded perception")):
            a, _, work, info = m.decide(w.capture(), CognitiveBudget(w.body, w.laws))
        self.assertIsNone(a)
        self.assertEqual(work, CognitiveWork())
        self.assertEqual(info["funding"], "NO_PROCESSING_BUDGET")

    def test_partial_construction_is_paid_without_command(self):
        w = World(fixture((.10, 20., 20., 80., .20)))
        m = InformationMind(midpoint(), 1, observer_decision_diagnostics=True)
        b = CognitiveBudget(w.body, w.laws)
        a, _, work, info = m.decide(w.capture(), b)
        self.assertIsNone(a)
        self.assertGreater(work.cycles, 0)
        self.assertEqual(info["funding"], "NO_FUNDED_SCORE")
        self.assertEqual(info["observer"]["score_witness"], [])
        w.step(a, None, work)
        self.assertLess(w.body[0], .10)

    def test_no_postmortem_decision_or_recording(self):
        m = InformationMind(midpoint(), 1)
        w = World(fixture((80., 0., 30., 80., 80.)))
        with self.assertRaises(ValueError):
            m.decide(w.capture(), CognitiveBudget(w.body, w.laws))
        m._pending_personal = ("must not be read",)
        self.assertEqual(m.learn_from_outcome({"dead": ("zero_food",)}), 0)
        self.assertIsNone(m._pending_personal)
        self.assertEqual(m.personal_records, 0)

    def test_common_forecast_is_not_extra_physical_billing(self):
        outcomes = (SubjectiveOutcome(.5, "body", ZERO, (("a", ZERO),)),) * 2
        m = Mind(midpoint(), 1)
        a, b = CognitiveBudget(BODY, BodyLaws()), CognitiveBudget(BODY, BodyLaws())
        ordinary = paid_information_value(m, outcomes, a)
        ceiling = CognitiveWork(a.work.cycles + 2, a.work.simulated_steps + 10,
                                a.work.memory_items, 0)
        common = paid_information_value(m, outcomes, b, forecast_work=ceiling)
        self.assertEqual(a.work, b.work)
        self.assertEqual(a.remaining, b.remaining)
        self.assertLess(common["forecast_start_body"][0], ordinary["forecast_start_body"][0])

    def test_common_quote_cannot_hide_work_or_waive_funding(self):
        outcomes = (SubjectiveOutcome(.5, "body", ZERO, (("a", ZERO),)),) * 2
        m = Mind(midpoint(), 1)
        with self.assertRaises(ValueError):
            paid_information_value(m, outcomes, CognitiveBudget(BODY, BodyLaws()),
                                   forecast_work=CognitiveWork())
        with self.assertRaises(ValueError):
            paid_information_value(m, outcomes, CognitiveBudget(BODY, BodyLaws()),
                                   perceive_cost=False, forecast_work=CognitiveWork(cycles=100))
        with self.assertRaises(CognitiveFundingError):
            paid_information_value(m, outcomes, CognitiveBudget(BODY, BodyLaws()),
                                   forecast_work=CognitiveWork(cycles=1000000, simulated_steps=1000000,
                                                                memory_items=1000000))


    def test_exact_cell_reuse_preserves_score_and_forecast_but_reduces_work(self):
        outcomes = (SubjectiveOutcome(.5, "body", ZERO, (("a", ZERO),)),) * 2
        m = Mind(midpoint(), 1)
        ceiling = CognitiveWork(cycles=20, simulated_steps=20, memory_items=100)
        full_budget = CognitiveBudget(BODY, BodyLaws())
        cached_budget = CognitiveBudget(BODY, BodyLaws())
        full = paid_information_value(m, outcomes, full_budget, forecast_work=ceiling)
        cached = paid_information_value(
            m, outcomes, cached_budget, forecast_work=ceiling, cell_cache={})
        for key in ("informed_value", "uninformed_value", "information_value",
                    "conditional_choices", "common_best_continuations",
                    "forecast_start_body"):
            self.assertEqual(full[key], cached[key])
        self.assertEqual(cached["cell_reuse"], {"computed": 1, "reused": 1, "cache_size": 1})
        self.assertLess(cached_budget.work.cycles, full_budget.work.cycles)
        self.assertLess(cached_budget.work.simulated_steps, full_budget.work.simulated_steps)
        self.assertGreater(cached_budget.remaining[0], full_budget.remaining[0])
        self.assertGreater(cached_budget.remaining[4], full_budget.remaining[4])

    def test_cell_cache_requires_common_forecast_and_plain_dict(self):
        outcomes = (SubjectiveOutcome(.5, "body", ZERO, (("a", ZERO),)),) * 2
        m = Mind(midpoint(), 1)
        with self.assertRaises(ValueError):
            paid_information_value(m, outcomes, CognitiveBudget(BODY, BodyLaws()),
                                   cell_cache={})
        with self.assertRaises(ValueError):
            paid_information_value(m, outcomes, CognitiveBudget(BODY, BodyLaws()),
                                   forecast_work=CognitiveWork(cycles=20, simulated_steps=20,
                                                               memory_items=100),
                                   cell_cache=[])


    def test_personal_construction_receipt_does_not_change_work_or_outcomes(self):
        a, b = StationaryUnknownOutcomes(16), StationaryUnknownOutcomes(16)
        for history in (a, b):
            remember(history, ("boire", None), (0., 0., 5., 0., 0.))
        ba, bb = CognitiveBudget(BODY, BodyLaws()), CognitiveBudget(BODY, BodyLaws())
        plain = a.construct(("boire", None), (("wait", ("attendre", None)),), ba)
        receipt = {}
        observed = b.construct(
            ("boire", None), (("wait", ("attendre", None)),), bb,
            work_receipt=receipt)
        self.assertEqual(plain, observed)
        self.assertEqual(ba.work, bb.work)
        self.assertEqual(ba.remaining, bb.remaining)
        self.assertEqual(receipt["status"], "COMPLETE")
        self.assertEqual(receipt["phase"], "complete")
        total = CognitiveWork(**receipt["total"])
        self.assertEqual(total, bb.work)
        parts = CognitiveWork(*(
            receipt["setup"][k] + receipt["history_scan"][k] +
            receipt["branch_build"][k] for k in
            ("cycles", "simulated_steps", "memory_items", "replays")))
        self.assertEqual(parts, total)


    def test_one_history_pass_preserves_exact_and_same_action_support(self):
        h = StationaryUnknownOutcomes(16)
        for key, delta in (
            (("manger", "a"), (1., 0., 0., 0., 0.)),
            (("manger", "b"), (2., 0., 0., 0., 0.)),
            (("manger", "a"), (3., 0., 0., 0., 0.)),
            (("manger", "b"), (4., 0., 0., 0., 0.)),
            (("manger", "a"), (5., 0., 0., 0., 0.)),
        ):
            remember(h, key, delta)
        supports = h._supports((
            ("manger", "a"), ("manger", "new"), ("collecter", "new")))
        self.assertEqual(
            [row[0] for row in supports[("manger", "a")]], [1., 3., 5.])
        self.assertEqual(
            [row[0] for row in supports[("manger", "new")]], [3., 4., 5.])
        self.assertEqual(supports[("collecter", "new")], (ZERO,))
        self.assertEqual(h.unknown_reads, 1)

    def test_construct_charges_one_history_pass_for_all_requested_keys(self):
        h = StationaryUnknownOutcomes(16)
        for i in range(5):
            remember(h, ("manger", "a" if i % 2 == 0 else "b"),
                     (float(i + 1), 0., 0., 0., 0.))
        receipt = {}
        budget = CognitiveBudget(BODY, BodyLaws())
        h.construct(
            ("manger", "a"),
            (("eat-b", ("manger", "b")), ("wait", ("attendre", None))),
            budget, work_receipt=receipt)
        self.assertEqual(
            receipt["history_scan"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 41, "replays": 0})


class OnlineChoiceTests(unittest.TestCase):
    def test_personal_effect_changes_issued_motor_not_only_a_score(self):
        actions = []
        for gain in (10., -10.):
            m = InformationMind(midpoint(), 7, observer_decision_diagnostics=True)
            remember(m.personal, ("boire", None), (0., 0., gain, 0., 0.))
            w = World(fixture((80., 60., 10., 80., 80.)))
            a, param, work, _ = m.decide(w.capture(), CognitiveBudget(w.body, w.laws))
            w.step(a, param, work)
            actions.append(a)
        self.assertEqual(actions[0], "boire")
        self.assertNotEqual(actions[1], "boire")

    def test_online_history_is_recorded_and_used_on_later_decisions(self):
        uses, stores = [], []
        supports = StationaryUnknownOutcomes._supports
        observe = PersonalOutcomes.observe
        def seen_supports(history, keys):
            actions = {key[0] for key in keys}
            uses.append(any(s.key[0] in actions for s in history._samples))
            return supports(history, keys)
        def seen_observe(history, key, before, work, budget):
            result = observe(history, key, before, work, budget)
            stores.append(budget.work)
            return result
        with patch.object(StationaryUnknownOutcomes, "_supports", seen_supports), \
             patch.object(PersonalOutcomes, "observe", seen_observe):
            life = run()
        self.assertGreater(len(stores), 0)
        self.assertTrue(any(uses))
        self.assertTrue(all(w == STORE_WORK for w in stores))
        self.assertEqual(life["personal_effect_memory"]["recorded"], len(stores))
        receipt = energy_receipt(life, expected_protocol="STAGE1_LOCAL_SOFTWARE_ONLY",
                                expected_source_sha256=life["manifest"]["source"]["sha256"])
        self.assertEqual(receipt["steps_lived"], 8)

    def test_bonus_free_complete_scores_share_common_forecast_body(self):
        life = run(observer_full_competition=True)
        checked = 0
        for row in life["observer_full_competition"]["steps"]:
            scores = row["paid_option_scores"]
            if not scores:
                continue
            checked += 1
            self.assertEqual(len({tuple(s["forecast_start_body"]) for s in scores}), 1)
            for score in scores:
                self.assertEqual(score["base_return"], score["total_score"])
                for name in ("curiosity_bonus_computed", "curiosity_bonus_applied",
                             "risk_penalty_computed", "risk_penalty_applied"):
                    self.assertEqual(score[name], 0.)
        self.assertGreater(checked, 0)

    def test_online_choice_reuses_only_decision_local_exact_cells(self):
        life = run(observer_full_competition=True)
        reused = 0
        for row in life["observer_full_competition"]["steps"]:
            for score in row["paid_option_scores"]:
                witness = score["kernel_cell_reuse"]
                self.assertGreaterEqual(witness["computed"], 0)
                self.assertGreaterEqual(witness["reused"], 0)
                self.assertGreaterEqual(witness["cache_size"], witness["computed"])
                reused += witness["reused"]
        self.assertGreater(reused, 0)

    def test_synthetic_phase_profile_reconciles_empty_and_populated_history(self):
        summaries = {}
        for label in ("empty", "populated"):
            m = InformationMind(midpoint(), 7, observer_decision_diagnostics=True)
            if label == "populated":
                patterns = (
                    (("dormir", None), (2., -.2, -.4, .2, 3.)),
                    (("attendre", None), (0., -.2, -.4, .2, 0.)),
                    (("boire", None), (0., -.2, 8., 0., 0.)),
                )
                for i in range(m.personal._samples.maxlen):
                    remember(m.personal, *patterns[i % len(patterns)])
            w = World(fixture((100., 80., 60., 80., 100.)))
            action, param, work, info = m.decide(
                w.capture(), CognitiveBudget(w.body, w.laws))
            self.assertIsNotNone(action)
            profile = info["observer"]["cost_profile"]
            summary = summarize_decision_cost(profile, w.laws)
            saved = CognitiveWork(**profile["forecast_exhaustive_scan_savings"])
            self.assertEqual(saved.cycles, 6)
            self.assertEqual(
                saved.memory_items,
                7 * len(m.personal._samples) * 6)
            self.assertEqual(summary["total_work"], {
                "cycles": work.cycles,
                "simulated_steps": work.simulated_steps,
                "memory_items": work.memory_items,
                "replays": work.replays,
            })
            summaries[label] = summary
            compact = {
                "total_energy": summary["total_energy"],
                "total_vigilance": summary["total_vigilance"],
                "dominant_energy_phase": summary["dominant_energy_phase"],
                "dominant_vigilance_phase": summary["dominant_vigilance_phase"],
                "history_scan": summary["focus"]["personal_history_scan"],
                "unique_cells": summary["focus"]["kernel_unique_cells"],
            }
            print("STAGE1_COST_PROFILE", label, json.dumps(compact, sort_keys=True))
        self.assertGreaterEqual(
            summaries["populated"]["focus"]["personal_history_scan"]["energy"],
            summaries["empty"]["focus"]["personal_history_scan"]["energy"])
        self.assertEqual(
            summaries["populated"]["focus"]["personal_history_scan"]["vigilance"],
            summaries["empty"]["focus"]["personal_history_scan"]["vigilance"])


    def test_observers_preserve_actions_paid_evidence_and_rng(self):
        original = InformationMind.decide
        states = []
        def observed(m, cap, budget):
            result = original(m, cap, budget)
            states.append((m.rng.getstate(), m._budget_rng.getstate(), m.personal_records))
            return result
        with patch.object(InformationMind, "decide", observed):
            off = run(observer_mind_digest=True)
            off_states, states[:] = states[:], []
            on = run(observer_mind_digest=True, observer_full_competition=True,
                     observer_resource_acquisition=True, observer_decision_diagnostics=True)
        self.assertEqual(off_states, states)
        for field in ("evidence_head", "trace_head", "final_body", "actions",
                      "cognitive_accounting", "outcome_model_sha256", "personal_outcomes_sha256"):
            self.assertEqual(off[field], on[field])

    def test_unused_old_bonus_genes_do_not_change_candidate_choices(self):
        g = midpoint()
        h = deepcopy(g)
        g["genes"].update(beta_u=0., lambda_r=0.)
        h["genes"].update(beta_u=2., lambda_r=1.)
        a = run_life(g, fixture(), 7, 8, keep_trace=True, decision_policy=MODE)
        b = run_life(h, fixture(), 7, 8, keep_trace=True, decision_policy=MODE)
        for key in ("trace", "actions", "final_body", "cognitive_accounting"):
            self.assertEqual(a[key], b[key])

    def test_first_choice_ignores_token_names_and_hidden_world_effects(self):
        from i3.modules.world import FoodPatch
        decisions = []
        for token, gain, stock in (("first", 5., 1), ("renamed", 99., None)):
            spec = fixture()
            spec.name = token
            spec.water[(0, 0)] = WaterSource(gain, stock=stock)
            spec.food[(0, 0)] = FoodPatch(token, 2, 2)
            spec.token_effects[token] = (gain, -gain)
            w = World(spec)
            m = InformationMind(midpoint(), 7, observer_decision_diagnostics=True)
            action, param, work, info = m.decide(w.capture(), CognitiveBudget(w.body, w.laws))
            decisions.append((action, "token" if param == token else param, work, info))
        self.assertEqual(decisions[0], decisions[1])

    def test_policy_is_bound_before_birth_and_unsupported_modes_fail(self):
        result = run()
        self.assertEqual(result["manifest"]["experimental_policy"]["name"], MODE)
        with patch("i3.runtime.life.World", side_effect=AssertionError("born too soon")):
            for kwargs in ({"decision_policy": "unknown"},
                           {"decision_policy": MODE, "learning_mode": "discard_values"},
                           {"decision_policy": MODE, "score_addend_mode": "discard_both_bonus_terms"},
                           {"decision_policy": MODE, "effect_readout": "blind_all"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    run_life(midpoint(), fixture(), 1, 3, **kwargs)

    def test_exhaustion_and_death_remain_outcomes(self):
        life = run_life(midpoint(), fixture((0., 20., 20., 80., 0.)), 1, 3,
                        keep_trace=True, decision_policy=MODE)
        self.assertEqual(life["actions"], {"physical_inactivity": 3})
        self.assertEqual(life["personal_effect_memory"]["recorded"], 0)
        dead = run_life(midpoint(), fixture((80., 0., 20., 80., 80.)), 1, 3,
                        keep_trace=True, decision_policy=MODE)
        self.assertEqual(dead["steps_lived"], 0)
        self.assertEqual(dead["terminal"], "dead")

    def test_real_development_fixtures_have_settled_two_phase_receipts(self):
        from i3.lab.p2_ecologies import world_for
        # Existing software-fixture indices only, no held-out world exposure.
        for index in (0, 1):
            spec = world_for("stable", "development", index)
            life = run_life(midpoint(), spec, 10 + index, 8, keep_trace=True,
                            protocol="LOCAL_DEV_SOFTWARE", decision_policy=MODE)
            energy_receipt(life, expected_protocol="LOCAL_DEV_SOFTWARE",
                           expected_source_sha256=life["manifest"]["source"]["sha256"])

    def test_default_reference_matches_pinned_previous_runner(self):
        root = Path(__file__).resolve().parents[2]
        source = subprocess.run(["git", "show", BASE + ":src/i3/runtime/life.py"],
                                cwd=root, check=True, capture_output=True, text=True).stdout
        old = {}
        exec(compile(source, "pinned_previous_life.py", "exec"), old)
        kwargs = dict(keep_trace=True, observer_mind_digest=True,
                      observer_full_competition=True, observer_resource_acquisition=True)
        with patch.object(InformationMind, "__init__", side_effect=AssertionError("implicit candidate")):
            actual = run_life(midpoint(), fixture(), 7, 8, **kwargs)
        expected = old["run_life"](midpoint(), fixture(), 7, 8, **kwargs)
        self.assertEqual(untimed(expected), untimed(actual))
        self.assertNotIn("experimental_policy", actual["manifest"])


if __name__ == "__main__":
    unittest.main()
