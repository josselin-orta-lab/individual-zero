"""Native I2 full paid cycle: lived state, later evidence and SQLite custody."""
import sys
import tempfile
import sqlite3
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import NativePaidI2, NativeRefusal


class NativePaidCycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "native.sqlite"
        self.traits = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def birth(self, **kw):
        body = kw.pop("body", Body(60, 40, 40, 90))
        traits = kw.pop("temperament", self.traits)
        return NativePaidI2.create(
            self.path, body=body, temperament=traits, **kw)

    def test_owned_native_paid_action_and_later_first_person_capture(self):
        actor = self.birth()
        before = actor.audit()
        first = actor.step()
        self.assertEqual(first["revision"], 1)
        self.assertLess(first["remaining_uc"], before["remaining_uc"])
        self.assertEqual(first["m11_authenticated"], False)
        self.assertNotEqual(first["body"], before["body"])
        later = actor.step()
        self.assertEqual(later["revision"], 2)
        self.assertEqual(actor.audit(), later)
        with sqlite3.connect(self.path) as conn:
            events = [row[0] for row in conn.execute(
                "SELECT event_json FROM events ORDER BY seq")]
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM native_physical_events").fetchone()[0], 2)
        self.assertNotIn("evidence:i2:native:outcome:1", events[0])
        self.assertIn("evidence:i2:native:outcome:1", events[1])

    def test_before_commit_rollback_and_uncertain_commit_halts(self):
        from i2.modules.cognitive_cycle_fixture import (
            FaultInjected, CommitAcknowledgmentLost)
        actor = self.birth()
        before = actor.audit()
        with self.assertRaises(FaultInjected):
            actor.step(fault="before_commit")
        self.assertEqual(actor.audit(), before)
        with self.assertRaises(CommitAcknowledgmentLost):
            actor.step(fault="after_commit")
        self.assertEqual(actor.audit()["revision"], 1)
        with self.assertRaises(NativeRefusal):
            actor.step()

    def test_paid_abstention_advances_real_physics_without_fake_motor(self):
        actor = self.birth(learning=False)
        actor.step()
        second = actor.step()
        self.assertEqual(second["revision"], 2)
        with sqlite3.connect(self.path) as conn:
            action = conn.execute(
                "SELECT admitted_action FROM native_physical_events "
                "WHERE seq=2").fetchone()[0]
            self.assertEqual(action, "NO_ACTION")
            self.assertLessEqual(second["body"]["water"], 39.2)
            saved = conn.execute(
                "SELECT event_json FROM events WHERE seq=2").fetchone()[0]
            self.assertNotIn("evidence:i2:native:outcome:2", saved)
        self.assertEqual(actor.audit()["revision"], 2)

    def test_explicit_veto_is_not_an_action_and_passive_time_elapses(self):
        actor = self.birth()
        before = actor.audit()
        after = actor.step(veto=True)
        self.assertEqual(after["revision"], 1)
        self.assertEqual(after["body"]["energy"], before["body"]["energy"])
        self.assertAlmostEqual(after["body"]["food"], 39.8)
        self.assertAlmostEqual(after["body"]["water"], 39.6)
        with sqlite3.connect(self.path) as db:
            action, marker = db.execute(
                "SELECT admitted_action,admission_ref "
                "FROM native_physical_events WHERE seq=1").fetchone()
        self.assertEqual(action, "NO_ACTION")
        self.assertTrue(marker.startswith("no-motor:"))
        self.assertLess(after["remaining_uc"], before["remaining_uc"])

    def test_terminal_after_veto_stops_body_and_cold_reentry(self):
        actor = self.birth(body=Body(60, 0.1, 40, 90))
        stopped = actor.step(veto=True)
        self.assertTrue(stopped["terminal"])
        self.assertEqual(stopped["body"]["food"], 0.0)
        with self.assertRaises(NativeRefusal):
            actor.step()
        cold = NativePaidI2.inspect(self.path)
        self.assertEqual(cold.audit(), actor.audit())
        with self.assertRaises(NativeRefusal):
            cold.step()

    def test_rehashed_but_physically_false_transition_is_rejected(self):
        import hashlib
        import json
        from i2.runtime.native_physiology_journal import (
            SCHEMA, audit_native_body)
        actor = self.birth()
        actor.step()
        with sqlite3.connect(self.path) as db:
            seq, action, ref, cog, before, after, relief, terminal, prev = db.execute(
                "SELECT seq,admitted_action,admission_ref,cognition_hash,"
                "before_json,after_json,net_physiological_relief,terminal,"
                "previous_hash FROM native_physical_events WHERE seq=1").fetchone()
            forged = json.dumps(
                {"energy": 99.0, "food": 99.0, "water": 99.0,
                 "integrity": 99.0},
                sort_keys=True, separators=(",", ":"))
            payload = json.dumps(
                [SCHEMA, seq, action, ref, cog, before, forged,
                 relief, bool(terminal), prev],
                sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(payload.encode("ascii")).hexdigest()
            db.execute(
                "UPDATE native_physical_events SET after_json=?,event_hash=? "
                "WHERE seq=1", (forged, digest))
            db.execute("UPDATE native_physiology SET body_json=?,head=? "
                       "WHERE id=1", (forged, digest))
            # Structural hashes and heads are internally consistent.
            self.assertEqual(audit_native_body(db)["revision"], 1)
        with self.assertRaisesRegex(NativeRefusal, "physiology"):
            actor.audit()


    def test_critical_personal_failure_prompts_a_paid_alternative(self):
        """No oracle, no automatic actuation and no guaranteed benefit."""
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0,
                           water_stock=4, drink_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            actions = [r[0] for r in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
            third = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
        self.assertEqual(actions, ["boire", "boire", "collecter"])
        self.assertTrue(any(
            v["evidence_ref"].endswith(":native-body:personal-nonrestoration")
            for v in third["advice"]["values"]))
        for seq in (1, 2):
            self.assertIn("evidence:i2:native:outcome:" + str(seq),
                          third["claim"]["subjective_evidence_refs"])
        self.assertNotIn("evidence:i2:native:outcome:3",
                         third["claim"]["subjective_evidence_refs"])
        self.assertFalse(actor.audit()["m11_authenticated"])

    def test_native_intention_is_retired_without_falsely_hiding_action(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0,
                           drink_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            event = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
        self.assertEqual(event["intention_kind"], "goal_changed")
        self.assertEqual(event["claim"]["capture"]["goal_ref"],
                         "goal:physical-last-resort")
        self.assertIn("boire", event["claim"]["capture"]["accessible_semantics"])
        self.assertEqual(actor.audit()["revision"], 3)

    def test_depleted_water_does_not_erase_failed_personal_strategy(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0, water_stock=2,
                           drink_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            third = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
            actions = [r[0] for r in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
        self.assertEqual(actions[:2], ["boire", "boire"])
        self.assertEqual(third["intention_kind"], "goal_changed")
        self.assertEqual(third["claim"]["capture"]["goal_ref"],
                         "goal:physical-last-resort")
        self.assertNotIn("boire",
                         third["claim"]["capture"]["accessible_semantics"])
        self.assertEqual(actor.audit()["revision"], 3)

    def test_depleted_water_does_not_invent_failure_or_permanent_impossibility(self):
        import json
        for label, learning, gain, stock in (
            ("fixed", False, 0.0, 2),
            ("restored", True, 25.0, 2),
            ("never-tried", True, 0.0, 0),
        ):
            with self.subTest(label=label):
                path = Path(self.tmp.name) / (label + "-depleted.sqlite")
                actor = NativePaidI2.create(
                    path, body=Body(80, 60, 3, 100),
                    temperament=self.traits, learning=learning,
                    food_stock=0, water_stock=stock, drink_water_gain=gain)
                for _ in range(3):
                    actor.step()
                with sqlite3.connect(path) as db:
                    last = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
                self.assertEqual(last["claim"]["capture"]["goal_ref"],
                                 "goal:physical-needs")
                self.assertNotEqual(last["intention_kind"], "goal_changed")
                self.assertEqual(actor.audit()["revision"], 3)

    def test_restoration_and_no_learning_do_not_revise_goal(self):
        import json
        for name, learning, gain in (
            ("restoring", True, 25.0),
            ("fixed", False, 0.0)):
            with self.subTest(name=name):
                path = Path(self.tmp.name) / (name + "-goal.sqlite")
                actor = NativePaidI2.create(
                    path, body=Body(80, 60, 3, 100),
                    temperament=self.traits, food_stock=0,
                    learning=learning, drink_water_gain=gain)
                for _ in range(3):
                    actor.step()
                with sqlite3.connect(path) as db:
                    event = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
                self.assertEqual(event["claim"]["capture"]["goal_ref"],
                                 "goal:physical-needs")
                self.assertNotEqual(event["intention_kind"], "goal_changed")
                self.assertEqual(actor.audit()["revision"], 3)

    def test_last_resort_is_new_untested_action_not_a_predicted_reward(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0,
                           water_stock=4, drink_water_gain=0.0)
        for _ in range(4):
            actor.step()
        with sqlite3.connect(self.path) as db:
            events = [json.loads(v[0]) for v in db.execute(
                "SELECT event_json FROM events ORDER BY seq")]
            effects = [tuple(row) for row in db.execute(
                "SELECT admitted_action,before_json,after_json "
                "FROM native_physical_events ORDER BY seq")]
        third, fourth = events[2], events[3]
        self.assertEqual(effects[2][0], "collecter")
        self.assertIn("collecter",
                      third["claim"]["capture"]["accessible_semantics"])
        self.assertNotIn("evidence:i2:native:outcome:3",
                         third["claim"]["subjective_evidence_refs"])
        self.assertIn("evidence:i2:native:outcome:3",
                      fourth["claim"]["subjective_evidence_refs"])
        before, after = json.loads(effects[2][1]), json.loads(effects[2][2])
        self.assertLess(after["energy"], before["energy"])
        self.assertLess(after["water"], before["water"])
        self.assertFalse(actor.audit()["m11_authenticated"])

    def test_no_unearned_exploration_before_lived_failure(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=False, food_stock=0,
                           drink_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            events = [json.loads(v[0]) for v in db.execute(
                "SELECT event_json FROM events ORDER BY seq")]
        for event in events:
            self.assertIn(
                "collecter", event["claim"]["capture"]["accessible_semantics"])
            self.assertEqual(event["claim"]["capture"]["goal_ref"],
                             "goal:physical-needs")
        self.assertEqual(actor.audit()["revision"], 3)

    def test_no_learning_retains_innate_reflex_but_not_lived_reassessment(self):
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=False, food_stock=0,
                           water_stock=4, drink_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            actions = [r[0] for r in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
        self.assertEqual(actions, ["boire", "boire", "boire"])
        self.assertFalse(actor.audit()["engine_registered"])

    def test_restore_or_noncritical_failed_action_is_not_discarded(self):
        import json
        for name, body, gain in (
            ("restored", Body(80, 60, 3, 100), 25.0),
            ("noncritical", Body(80, 60, 50, 100), 0.0),
        ):
            with self.subTest(name=name):
                path = Path(self.tmp.name) / (name + ".sqlite")
                actor = NativePaidI2.create(
                    path, body=body, temperament=self.traits,
                    learning=True, food_stock=0, drink_water_gain=gain)
                for _ in range(3):
                    actor.step()
                with sqlite3.connect(path) as db:
                    event = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
                self.assertFalse(any(
                    v["evidence_ref"].endswith(":personal-nonrestoration")
                    for v in event["advice"]["values"]))
                self.assertEqual(actor.audit()["revision"], 3)


    def test_failed_nutrition_critical_food_changes_goal_not_just_water(self):
        import json
        actor = self.birth(
            body=Body(80, 3, 60, 100), food_stock=2, water_stock=0,
            berry_food_gain=0.0, learning=True)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            actions = [row[0] for row in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
            event = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
        self.assertEqual(actions[:2], ["manger", "manger"])
        self.assertEqual(event["intention_kind"], "goal_changed")
        self.assertEqual(event["claim"]["capture"]["goal_ref"],
                         "goal:physical-last-resort")
        self.assertNotIn("manger",
                         event["claim"]["capture"]["accessible_semantics"])
        self.assertEqual(actor.audit()["revision"], 3)

    def test_hunger_during_drinking_is_not_a_failed_drink(self):
        import json
        actor = self.birth(
            body=Body(80, 3, 50, 100), food_stock=0, water_stock=2,
            drink_water_gain=0.0, learning=True)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            actions = [row[0] for row in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
            event = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
        self.assertEqual(actions[:2], ["boire", "boire"])
        self.assertEqual(event["claim"]["capture"]["goal_ref"],
                         "goal:physical-needs")
        self.assertNotEqual(event["intention_kind"], "goal_changed")
        self.assertEqual(actor.audit()["revision"], 3)

    def test_eating_while_thirsty_is_not_falsely_labelled_hydration_failure(self):
        import json
        actor = self.birth(
            body=Body(80, 60, 3, 100), food_stock=2, water_stock=0,
            berry_food_gain=20.0, learning=True)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            actions = [row[0] for row in db.execute(
                "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
            event = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
        self.assertEqual(actions[:2], ["manger", "manger"])
        self.assertEqual(event["claim"]["capture"]["goal_ref"],
                         "goal:physical-needs")
        self.assertNotEqual(event["intention_kind"], "goal_changed")
        self.assertEqual(actor.audit()["revision"], 3)

    def test_paid_probe_reveals_hidden_water_only_after_commit(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0, water_stock=4,
                           drink_water_gain=0.0, discovered_water_gain=30.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            events = [json.loads(x[0]) for x in db.execute(
                "SELECT event_json FROM events ORDER BY seq")]
            found = db.execute(
                "SELECT seq,found FROM native_discoveries").fetchall()
        self.assertEqual(found, [(3, 1)])
        self.assertNotIn(
            "boire_decouverte", events[2]["claim"]["capture"]["accessible_semantics"])
        self.assertNotIn(
            "evidence:i2:native:water-found:3",
            events[2]["claim"]["subjective_evidence_refs"])
        actor.step()
        with sqlite3.connect(self.path) as db:
            fourth = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=4").fetchone()[0])
        self.assertIn(
            "boire_decouverte", fourth["claim"]["capture"]["accessible_semantics"])
        self.assertIn(
            "evidence:i2:native:water-found:3",
            fourth["claim"]["subjective_evidence_refs"])
        self.assertEqual(actor.audit()["revision"], 4)
        # The previous CI proved the learned policy consumed the new source
        # already at seq4, NOT at seq5. Check the actual chosen transition,
        # without requiring a second, physically impossible consumption.
        with sqlite3.connect(self.path) as db:
            taken = db.execute("SELECT admitted_action,before_json,after_json "
                               "FROM native_physical_events WHERE seq=4").fetchone()
        self.assertEqual(taken[0], "boire_decouverte")
        self.assertGreater(json.loads(taken[2])["water"],
                           json.loads(taken[1])["water"])
        actor.step()
        with sqlite3.connect(self.path) as db:
            fifth = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=5").fetchone()[0])
            physical_uses = db.execute(
                "SELECT COUNT(*) FROM native_physical_events "
                "WHERE admitted_action='boire_decouverte'").fetchone()[0]
        self.assertNotIn("boire_decouverte",
                         fifth["claim"]["capture"]["accessible_semantics"])
        self.assertEqual(physical_uses, 1)
        self.assertEqual(actor.audit()["revision"], 5)

    def test_observed_new_water_is_scored_from_current_thirst_not_hidden_gain(self):
        from i2.runtime.native_paid_cycle import innate_adjustment
        from i2.modules.native_physiological_needs import assess_needs
        body = Body(80, 60, 1.8, 100)
        initial = {"boire_decouverte": 1, "boire": 1, "manger": 4,
                   "collecter": 2, "dormir": 2, "attendre": 1}
        scores = innate_adjustment(initial, body, self.traits)
        thirst = round(8 * assess_needs(body, self.traits).pressures["water"])
        self.assertEqual(scores["boire_decouverte"], 1 + thirst)
        self.assertEqual(scores["boire"], 1 + thirst)
        self.assertGreater(scores["boire_decouverte"], scores["dormir"])

    def test_learning_and_control_born_with_same_exploration_site(self):
        import json
        states = []
        for learned in (True, False):
            with self.subTest(learning=learned):
                path = Path(self.tmp.name) / ("paired-" + str(learned) + ".sqlite")
                actor = NativePaidI2.create(
                    path, body=Body(80, 60, 3, 100),
                    temperament=self.traits, learning=learned,
                    sleep_consolidation=False, food_stock=0, water_stock=4,
                    drink_water_gain=0.0, discovered_water_gain=30.0)
                birth = actor.audit()
                actor.step()
                with sqlite3.connect(path) as db:
                    event = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=1").fetchone()[0])
                semantics = event["claim"]["capture"]["accessible_semantics"]
                self.assertIn("collecter", semantics)
                self.assertNotIn("boire_decouverte", semantics)
                self.assertEqual(event["claim"]["capture"]["goal_ref"],
                                 "goal:physical-needs")
                states.append((birth["body"], birth["temperament"],
                               tuple(semantics), actor.audit()["body"]))
        self.assertEqual(states[0], states[1])

    def test_paired_lives_same_access_distinguish_lived_strategy_update(self):
        """One predetermined world: difference is policy, not source access."""
        import json
        observations = []
        for learned in (True, False):
            with self.subTest(learning=learned):
                path = Path(self.tmp.name) / ("world-pair-" + str(learned) + ".sqlite")
                actor = NativePaidI2.create(
                    path, body=Body(80, 60, 3, 100),
                    temperament=self.traits, learning=learned,
                    sleep_consolidation=False, food_stock=0, water_stock=4,
                    drink_water_gain=0.0, discovered_water_gain=30.0)
                born = actor.audit()
                for _ in range(4):
                    actor.step()
                with sqlite3.connect(path) as db:
                    events = [json.loads(r[0]) for r in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                    actions = [r[0] for r in db.execute(
                        "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                    discoveries = db.execute(
                        "SELECT seq,found FROM native_discoveries ORDER BY seq").fetchall()
                observations.append({
                    "birth": born,
                    "initial_actions": events[0]["claim"]["capture"]["accessible_semantics"],
                    "actions": actions,
                    "discoveries": discoveries,
                    "water": actor.audit()["body"]["water"],
                    "audit": actor.audit(),
                })
        learned, fixed = observations
        self.assertEqual(learned["birth"]["body"], fixed["birth"]["body"])
        self.assertEqual(learned["birth"]["temperament"], fixed["birth"]["temperament"])
        self.assertEqual(learned["initial_actions"], fixed["initial_actions"])
        self.assertEqual(learned["actions"][:2], ["boire", "boire"])
        self.assertEqual(fixed["actions"][:2], ["boire", "boire"])
        self.assertEqual(learned["actions"][2:], ["collecter", "boire_decouverte"])
        self.assertEqual(learned["discoveries"], [(3, 1)])
        self.assertNotIn("collecter", fixed["actions"])
        self.assertEqual(fixed["discoveries"], [])
        self.assertGreater(learned["water"], fixed["water"])
        self.assertEqual(learned["audit"]["revision"], 4)
        self.assertEqual(fixed["audit"]["revision"], 4)
        self.assertFalse(learned["audit"]["m11_authenticated"])

    def test_probe_without_hidden_water_never_claims_discovery(self):
        import json
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0, water_stock=4,
                           drink_water_gain=0.0, discovered_water_gain=0.0)
        for _ in range(4):
            actor.step()
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute(
                "SELECT seq,found FROM native_discoveries").fetchall(), [(3, 0)])
            fourth = json.loads(db.execute(
                "SELECT event_json FROM events WHERE seq=4").fetchone()[0])
        self.assertNotIn(
            "boire_decouverte", fourth["claim"]["capture"]["accessible_semantics"])
        self.assertEqual(actor.audit()["revision"], 4)

    def test_discovery_and_sleep_ablation_are_physically_matched_before_sleep(self):
        """Neither sleep switch reveals water nor changes physics pre-sleep."""
        import json
        arms = []
        for enabled in (True, False):
            path = Path(self.tmp.name) / ("combined-" + str(enabled) + ".sqlite")
            actor = NativePaidI2.create(
                path, body=Body(80, 60, 3, 100),
                temperament=self.traits, learning=True,
                sleep_consolidation=enabled, food_stock=0, water_stock=4,
                drink_water_gain=0.0, discovered_water_gain=30.0)
            born = actor.audit()
            for _ in range(4):
                actor.step()
            with sqlite3.connect(path) as db:
                events = [json.loads(r[0]) for r in db.execute(
                    "SELECT event_json FROM events ORDER BY seq")]
                effects = [tuple(r) for r in db.execute(
                    "SELECT admitted_action,before_json,after_json "
                    "FROM native_physical_events ORDER BY seq")]
                discoveries = db.execute(
                    "SELECT seq,found FROM native_discoveries").fetchall()
            self.assertEqual(discoveries, [(3, 1)])
            self.assertEqual([e[0] for e in effects],
                             ["boire", "boire", "collecter", "boire_decouverte"])
            self.assertNotIn(
                "boire_decouverte", events[2]["claim"]["capture"]["accessible_semantics"])
            self.assertIn(
                "boire_decouverte", events[3]["claim"]["capture"]["accessible_semantics"])
            self.assertGreater(json.loads(effects[3][2])["water"],
                               json.loads(effects[3][1])["water"])
            self.assertNotIn("sleep-consolidated",
                             " ".join(json.dumps(e) for e in events))
            self.assertEqual(actor.audit()["revision"], 4)
            arms.append((born["body"], born["temperament"],
                         [e[0] for e in effects], actor.audit()["body"]))
        self.assertEqual(arms[0], arms[1])

    def test_tampered_found_water_fails_native_cold_replay(self):
        actor = self.birth(body=Body(80, 60, 3, 100),
                           learning=True, food_stock=0, water_stock=4,
                           drink_water_gain=0.0, discovered_water_gain=0.0)
        for _ in range(3):
            actor.step()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE native_discoveries SET found=1 WHERE seq=3")
        with self.assertRaises(ValueError):
            actor.audit()

    def test_sleep_consolidates_only_personally_observed_repetition(self):
        from i2.runtime.native_paid_cycle import sleep_consolidated_scores
        rows = (
            (1, "c1", "boire", -0.20, "before1", "after1"),
            (2, "c2", "boire", -0.40, "before2", "after2"),
            (3, "c3", "dormir", 0.10, "before3", "after3"),
        )
        learned, proven = sleep_consolidated_scores(
            {"boire": 1, "dormir": 2}, previous=rows,
            learning=True, enabled=True)
        # Mean observed net is -6; fixed valuation offset is +5.
        self.assertEqual(learned["boire"], -1)
        self.assertEqual(proven, frozenset({"boire"}))
        for learning, enabled in ((False, True), (True, False)):
            same, markers = sleep_consolidated_scores(
                {"boire": 1, "dormir": 2}, previous=rows,
                learning=learning, enabled=enabled)
            self.assertEqual(same["boire"], 1)
            self.assertEqual(markers, frozenset())
        premature, _ = sleep_consolidated_scores(
            {"boire": 1}, previous=rows[:2], learning=True, enabled=True)
        self.assertEqual(premature["boire"], 1)
        # A later lived consequence overrides the older sleep summary.
        renewed, _ = sleep_consolidated_scores(
            {"boire": 7}, previous=rows + (
                (4, "c4", "boire", 0.1, "before4", "after4"),),
            learning=True, enabled=True)
        self.assertEqual(renewed["boire"], 7)

    def test_sleep_ablations_share_birth_and_physical_sleep_cost(self):
        import json
        traces = []
        for enabled in (True, False):
            path = Path(self.tmp.name) / ("sleep-" + str(enabled) + ".sqlite")
            actor = NativePaidI2.create(
                path, body=Body(50, 40, 50, 90),
                temperament=self.traits, learning=True,
                sleep_consolidation=enabled, food_stock=0, water_stock=0)
            before = actor.audit()
            actor.step()
            after = actor.audit()
            self.assertEqual(after["revision"], 1)
            self.assertEqual(after["body"], actor.audit()["body"])
            with sqlite3.connect(path) as db:
                event = json.loads(db.execute(
                    "SELECT event_json FROM events WHERE seq=1").fetchone()[0])
            self.assertIn("dormir", event["claim"]["capture"]["accessible_semantics"])
            traces.append((before["body"], before["temperament"]))
        self.assertEqual(traces[0], traces[1])

    def test_native_body_journal_tamper_rejected(self):
        actor = self.birth()
        actor.step()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE native_physical_events SET after_json='{}'")
        with self.assertRaises(ValueError):
            actor.audit()

    def test_innate_traits_and_zero_learning_flag_do_not_fake_experiences(self):
        actor = self.birth(learning=False)
        self.assertEqual(actor.audit()["temperament"], self.traits.as_dict())
        actor.step()
        actor.step()
        with sqlite3.connect(self.path) as conn:
            events = [row[0] for row in conn.execute(
                "SELECT event_json FROM events ORDER BY seq")]
        self.assertIn("evidence:i2:native:outcome:1", events[1])
        self.assertFalse(actor.audit()["engine_registered"])


if __name__ == "__main__":
    unittest.main()
