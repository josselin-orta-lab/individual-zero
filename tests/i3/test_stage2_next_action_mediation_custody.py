"""No living worlds: preflight a future paired next-action original receipt."""
import json
import unittest
from unittest.mock import patch

from i3.lab.stage2_next_action_mediation_custody import NextActionPairCustody
from i3.modules.body import (
    BodyLaws, CognitiveWork, debit_cognition, transition)
from i3.modules.mind import Mind
from i3.modules.world import World


LAWS = BodyLaws()
BASE = CognitiveWork(cycles=3, memory_items=12)
EXTRA = CognitiveWork(cycles=6, memory_items=48)
TOTAL = CognitiveWork(cycles=9, memory_items=60)
LEARN = CognitiveWork(cycles=2, simulated_steps=16, memory_items=1)
CHOICE = CognitiveWork(cycles=2)
BODY = (70., 60., 60., 90., 60.)
FORECASTS = {"action": -0.25, "global": -0.5, "persistence": -0.75}


def account(work):
    return debit_cognition((80., 80., 80., 80., 80.), LAWS, work)[1]


def pair(body=BODY, initial_action="attendre"):
    source = NextActionPairCustody(
        source_label="UNAUTHORIZED_SYNTHETIC_TEST_ONLY",
        world_spec_sha="a"*64, genome_sha="b"*64,
        initial_living_mind_sha="c"*64, pair_seed=130502)
    seals = {}
    for arm in ("visible", "discard"):
        seals[arm] = source.freeze_first(
            arm, before_body=body, action=initial_action, param=None,
            original_work=BASE, personal_memory_count=0,
            forecasts=FORECASTS)
    return source, seals


def first_outcome(source, seals, *, body=BODY, initial_action="attendre"):
    immediate, dead = transition(body, initial_action, LAWS, TOTAL)
    if dead:
        learning_work, status, post = (
            CognitiveWork(), "TERMINAL_NO_LEARNING", immediate)
    else:
        learning_work, status = LEARN, "PAID_LEARNING"
        post, _ = debit_cognition(immediate, LAWS, LEARN)
    for arm in ("visible", "discard"):
        source.settle_first(
            arm, seal=seals[arm], action=initial_action, param=None,
            decision_work=TOTAL, decision_account=account(TOTAL),
            immediate_body=immediate, dead=dead,
            learning_status=status, learning_work=learning_work,
            learning_account=account(learning_work),
            post_paid_learning_body=post)
    return post, dead


def next_outcome(source, first_seals, post, *, choices):
    for arm, choice in choices.items():
        seal = source.freeze_next(
            arm, first_seal=first_seals[arm],
            source_decision_origin="LIVING_MIND_DECIDE",
            actual_capture_body=post, action=choice, param=None,
            work=CHOICE, next_capture_sha="e"*64)
        immediate, dead = transition(post, choice, LAWS, CHOICE)
        if dead:
            status = "TERMINAL_NO_LEARNING"
            lw = CognitiveWork()
            after = immediate
        else:
            status, lw = "PAID_LEARNING", LEARN
            after, _ = debit_cognition(immediate, LAWS, lw)
        source.settle_next(
            arm, seal=seal, actual_executed_in_world=True,
            action=choice, param=None, decision_work=CHOICE,
            decision_account=account(CHOICE),
            immediate_body=immediate, dead=dead,
            learning_status=status, learning_work=lw,
            learning_account=account(lw),
            post_paid_learning_body=after)


class NextActualActionCustodyTests(unittest.TestCase):
    def test_four_source_labels_with_zero_real_worlds(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("NO WORLD")), patch(
                          "i3.runtime.life.run_life",
                          side_effect=AssertionError("NO LIFE")), patch.object(
                          Mind, "decide",
                          side_effect=AssertionError("NO MOTOR")), patch.object(
                          Mind, "learn_from_outcome",
                          side_effect=AssertionError("NO LEARNING")):
            cases = {}
            x, seals = pair()
            post, dead = first_outcome(x, seals)
            self.assertFalse(dead)
            next_outcome(x, seals, post,
                         choices={"visible": "attendre", "discard": "attendre"})
            cases["same_actual_next_action_claim"] = x.summary()
            self.assertEqual(cases["same_actual_next_action_claim"]["status"],
                             "ACTUAL_NEXT_ACTION_SAME")
            x, seals = pair()
            post, dead = first_outcome(x, seals)
            next_outcome(x, seals, post,
                         choices={"visible": "dormir", "discard": "attendre"})
            cases["different_actual_next_action_claim"] = x.summary()
            self.assertEqual(
                cases["different_actual_next_action_claim"]["status"],
                "ACTUAL_NEXT_ACTION_DIFFERENCE")

            terminal_body = (99.95, .23, 60., 90., 99.95)
            x, seals = pair(terminal_body, "dormir")
            _, dead = first_outcome(
                x, seals, body=terminal_body, initial_action="dormir")
            self.assertEqual(dead, ("zero_food",))
            for arm in ("visible", "discard"):
                x.close_without_next(
                    arm, first_seal=seals[arm],
                    reason="TERMINAL_BEFORE_NEXT")
            cases["terminal_before_next"] = x.summary()
            self.assertEqual(cases["terminal_before_next"]["status"],
                             "INCOMPLETE_OR_CENSORED")
            x, seals = pair()
            first_outcome(x, seals)
            for arm in ("visible", "discard"):
                x.close_without_next(
                    arm, first_seal=seals[arm],
                    reason="RIGHT_CENSORED_NOT_SCORED")
            cases["no_next_observation"] = x.summary()
            self.assertEqual(cases["no_next_observation"]["status"],
                             "INCOMPLETE_OR_CENSORED")
        print("I3_NEXT_ACTION_MEDIATION_PREFLIGHT_RESULT="+json.dumps(
            {"schema": "i3-stage2.1-next-actual-decision-custody-software/v1",
             "technical_fixture_pairs": 4, "results": cases,
             "born_originals_verified": 0, "worlds_opened": 0,
             "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED"},
            sort_keys=True))
        for result in cases.values():
            self.assertFalse(result["source_originals_independently_verified"])
            self.assertFalse(result["controller_delivery_independently_verified"])
            self.assertIsNone(result["causal_information_benefit"])
            self.assertIsNone(result["survival_effect"])
            self.assertEqual(result["scientific_lives"], 0)
            self.assertFalse(result["stage2_2_go"])

    def test_unfundable_extra_ticket_or_motor_reserve_fails_before_receipt(self):
        for body, act in (
            ((.45, 60., 60., 90., 60.), "attendre"),
            ((70., 60., 60., 90., .30), "dormir")):
            with self.subTest(body=body, act=act):
                custody = NextActionPairCustody(
                    source_label="SYNTHETIC_NO_SCIENCE",
                    world_spec_sha="a"*64, genome_sha="b"*64,
                    initial_living_mind_sha="c"*64, pair_seed=1)
                with self.assertRaises(ValueError):
                    custody.freeze_first(
                        "visible", before_body=body, action=act,
                        param=None, original_work=BASE,
                        personal_memory_count=0, forecasts=FORECASTS)
                self.assertEqual(custody.summary()["pair_arms_frozen"], [])

    def test_pair_initial_preexposure_mismatch_and_duplicates_fail(self):
        x, seals = pair()
        with self.assertRaises(RuntimeError):
            x.freeze_first(
                "visible", before_body=BODY, action="attendre", param=None,
                original_work=BASE, personal_memory_count=0,
                forecasts=FORECASTS)
        y = NextActionPairCustody(
            source_label="SYNTHETIC_NO_SCIENCE", world_spec_sha="a"*64,
            genome_sha="b"*64, initial_living_mind_sha="c"*64, pair_seed=2)
        y.freeze_first(
            "visible", before_body=BODY, action="attendre", param=None,
            original_work=BASE, personal_memory_count=0,
            forecasts=FORECASTS)
        with self.assertRaises(PermissionError):
            y.freeze_first(
                "discard", before_body=BODY, action="dormir", param=None,
                original_work=BASE, personal_memory_count=0,
                forecasts=FORECASTS)
        self.assertEqual(y.summary()["status"],"INCOMPLETE_OR_CENSORED")

    def test_tampered_shas_forged_work_or_incomplete_two_currency_bill_fail(self):
        x, seals = pair()
        immediate, dead = transition(BODY, "attendre", LAWS, TOTAL)
        post, _ = debit_cognition(immediate, LAWS, LEARN)
        kwargs = dict(action="attendre", param=None,
                      decision_work=TOTAL, decision_account=account(TOTAL),
                      immediate_body=immediate, dead=dead,
                      learning_status="PAID_LEARNING", learning_work=LEARN,
                      learning_account=account(LEARN),
                      post_paid_learning_body=post)
        with self.assertRaises(PermissionError):
            x.settle_first("visible", seal="f"*64, **kwargs)
        with self.assertRaises(PermissionError):
            x.settle_first(
                "visible", seal=seals["visible"],
                **{**kwargs, "decision_work": BASE})
        bad=account(TOTAL)
        bad["vigilance"]["paid"]=0.
        with self.assertRaises(ValueError):
            x.settle_first(
                "visible", seal=seals["visible"],
                **{**kwargs, "decision_account": bad})
        self.assertEqual(x.summary()["arm_phases"]["visible"],"FROZEN_FIRST")
        x.settle_first("visible", seal=seals["visible"], **kwargs)
        with self.assertRaises(RuntimeError):
            x.settle_first("visible", seal=seals["visible"], **kwargs)

    def test_terminal_or_censor_cannot_be_recast_as_lived_next_choice(self):
        terminal_body=(99.95,.23,60.,90.,99.95)
        x,seals=pair(terminal_body,"dormir")
        after,dead=first_outcome(x,seals,body=terminal_body,
                                 initial_action="dormir")
        self.assertTrue(dead)
        with self.assertRaises(RuntimeError):
            x.freeze_next(
                "visible",first_seal=seals["visible"],
                source_decision_origin="LIVING_MIND_DECIDE",
                actual_capture_body=after,action="attendre",param=None,
                work=CHOICE,next_capture_sha="e"*64)
        with self.assertRaises(ValueError):
            x.close_without_next(
                "visible",first_seal=seals["visible"],
                reason="RIGHT_CENSORED_NOT_SCORED")
        x.close_without_next("visible",first_seal=seals["visible"],
                             reason="TERMINAL_BEFORE_NEXT")
        with self.assertRaises(RuntimeError):
            x.close_without_next("visible",first_seal=seals["visible"],
                                 reason="TERMINAL_BEFORE_NEXT")
        self.assertIsNone(x.summary()["next_actions_differ_claimed"])

    def test_detached_next_shadow_and_after_outcome_forgery_rejected(self):
        x, seals = pair()
        post, _ = first_outcome(x, seals)
        kwargs=dict(first_seal=seals["visible"],
                    actual_capture_body=post,action="attendre",param=None,
                    work=CHOICE,next_capture_sha="e"*64)
        with self.assertRaises(PermissionError):
            x.freeze_next("visible",source_decision_origin="DETACHED_SHADOW",
                          **kwargs)
        with self.assertRaises(ValueError):
            x.freeze_next("visible",source_decision_origin="LIVING_MIND_DECIDE",
                          **{**kwargs,"actual_capture_body":BODY})
        seal=x.freeze_next("visible",source_decision_origin="LIVING_MIND_DECIDE",
                           **kwargs)
        immediate,dead=transition(post,"attendre",LAWS,CHOICE)
        nxt, _=debit_cognition(immediate,LAWS,LEARN)
        args=dict(action="attendre",param=None,decision_work=CHOICE,
                  decision_account=account(CHOICE),immediate_body=immediate,
                  dead=dead,learning_status="PAID_LEARNING",learning_work=LEARN,
                  learning_account=account(LEARN),
                  post_paid_learning_body=nxt)
        with self.assertRaises(PermissionError):
            x.settle_next("visible",seal="f"*64,
                          actual_executed_in_world=True,**args)
        with self.assertRaises(PermissionError):
            x.settle_next("visible",seal=seal,
                          actual_executed_in_world=False,**args)
        x.settle_next("visible",seal=seal,
                      actual_executed_in_world=True,**args)
        self.assertEqual(x.summary()["status"],"INCOMPLETE_OR_CENSORED")

    def test_genuine_none_action_label_distinct_from_wait_in_second_frame(self):
        x, seals = pair()
        post, dead = first_outcome(x, seals)
        self.assertFalse(dead)
        next_outcome(x,seals,post,choices={"visible": None,
                                         "discard":"attendre"})
        report=x.summary()
        self.assertEqual(report["status"],"ACTUAL_NEXT_ACTION_DIFFERENCE")
        self.assertTrue(report["next_actions_differ_claimed"])

    def test_paid_learning_terminal_and_zero_vital_body_rules_fail_closed(self):
        x, seals=pair()
        immediate,_=transition(BODY,"attendre",LAWS,TOTAL)
        with self.assertRaises(ValueError):
            x.settle_first(
                "visible",seal=seals["visible"],
                action="attendre",param=None,
                decision_work=TOTAL,decision_account=account(TOTAL),
                immediate_body=(immediate[0],0.,*immediate[2:]),
                dead=(),learning_status="PAID_LEARNING",
                learning_work=LEARN,learning_account=account(LEARN),
                post_paid_learning_body=immediate)
        with self.assertRaises(ValueError):
            x.settle_first(
                "visible",seal=seals["visible"],
                action="attendre",param=None,
                decision_work=TOTAL,decision_account=account(TOTAL),
                immediate_body=immediate,dead=(),
                learning_status="TERMINAL_NO_LEARNING",
                learning_work=CognitiveWork(),
                learning_account=account(CognitiveWork()),
                post_paid_learning_body=immediate)
        self.assertEqual(x.summary()["arm_phases"]["visible"],"FROZEN_FIRST")


if __name__=="__main__":
    unittest.main()
