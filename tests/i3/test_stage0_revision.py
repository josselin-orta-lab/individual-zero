"""Revision endpoint arithmetic, adversarial joins and bounded runtime fixtures."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import stage0_revision as revision


def event(step, position=(0, 0), water=False, paid=True, drink=False):
    return {"step": step, "position": position, "water_here": water,
            "processing_paid": paid, "positive_drink": drink}


def outcome(events, terminal="censored", horizon=None):
    return revision._timeline(events, steps_lived=len(events),
                              horizon=horizon or max(1, len(events)), terminal=terminal)


def joining_fixture():
    """Synthetic field-join example, deliberately NOT a funded life receipt."""
    before = [80., 70., 40., 90., 100.]
    physical = [79., 69.8, 39.6, 90., 99.]
    work = dict(cycles=3, simulated_steps=0, memory_items=0, replays=0)
    bill = {ch: dict(requested=0., paid=0., unpaid=0.) for ch in ("energy", "vigilance")}
    phases = {p: {"work": dict(work), "accounting": deepcopy(bill),
                   "body_before": before[:] if p == "decision" else physical[:],
                   "body_after_debit": physical[:]} for p in ("decision", "learning")}
    row = {"t": 1, "action": "attendre", "param": None, "option": "attendre",
           "body": physical[:], "pos": [5, 6], "dead": [], "funding_phases": phases,
           "info": {"funding": "FUNDED", "observer": {"decision_outcome": "action_admitted"}}}
    witness = {"step": 1, "action": "attendre", "param": None, "chosen_option": "attendre",
               "death_causes": [], "world_position_observer_only": [5, 6],
               "personal_position": [0, 0], "body_before_decision": before[:],
               "body_after_physics": physical[:], "body_after_paid_learning": physical[:],
               "decision_funding": "FUNDED", "decision_outcome": "action_admitted",
               "capture_here_water": False, "positive_water_uptake": False,
               "water_uptake_above_decay": None,
               "phase_payment": {p: {"work": dict(work), "accounting": deepcopy(bill)}
                                 for p in phases},
               "paid_decision_work": dict(work), "paid_learning_work": dict(work)}
    return {"manifest": {"world": {"spawn": [5, 6], "laws": {"water_decay": 0.4}}},
            "trace": [row], "observer_resource_acquisition": {
                "schema": "i3-p5d-resource-acquisition-observer/v1", "steps": [witness]}}


class RevisionTimelineTests(unittest.TestCase):
    def test_empty_death_not_missing_or_efficient_revision(self):
        r = outcome([], "dead")
        self.assertEqual(r["status"], "NO_EXPOSURE")
        self.assertEqual(r["no_exposure_reason"], "NO_PRIOR_POSITIVE_UPTAKE")
        self.assertIsNone(r["latency_from_available_steps"])

    def test_dry_unknown_location_is_not_loss_of_a_used_source(self):
        r = outcome([event(1), event(2)])
        self.assertEqual(r["status"], "NO_EXPOSURE")

    def test_last_drink_does_not_start_a_hidden_stock_clock(self):
        r = outcome([event(1, water=True, drink=True)])
        self.assertEqual(r["no_exposure_reason"], "NO_LOCAL_ABSENCE")
        self.assertIsNone(r["first_available_absence_decision"])

    def test_absence_and_positive_alternative_have_action_boundary_latency(self):
        rows = [event(1, water=True, drink=True), event(2),
                event(3, (1, 0)), event(4, (2, 0), True, True, True)]
        r = outcome(rows)
        self.assertEqual(r["status"], "REACQUIRED")
        self.assertEqual(r["first_available_absence_decision"], 2)
        self.assertEqual(r["alternative_positive_uptake_step"], 4)
        self.assertEqual(r["latency_from_available_steps"], 3)
        self.assertEqual(r["origin_previous_uptake_step"], 1)

    def test_available_evidence_is_not_unpaid_processing(self):
        rows = [event(1, water=True, drink=True), event(2, paid=False), event(3),
                event(4, (1, 0), True, True, True)]
        r = outcome(rows)
        self.assertEqual(r["first_paid_absence_decision"], 3)
        self.assertEqual(r["latency_from_available_steps"], 3)
        self.assertEqual(r["latency_from_paid_steps"], 2)

    def test_unprocessed_absence_before_death_stays_visible(self):
        r = outcome([event(1, water=True, drink=True), event(2, paid=False)], "dead", 10)
        self.assertEqual(r["status"], "EXPOSED_NO_REACQUISITION")
        self.assertIsNone(r["first_paid_absence_decision"])
        self.assertEqual(r["observed_followup_steps"], 1)

    def test_old_refilled_source_is_not_an_alternative(self):
        r = outcome([event(1, water=True, drink=True), event(2),
                     event(3, water=True, drink=True)])
        self.assertEqual(r["status"], "EXPOSED_NO_REACQUISITION")

    def test_command_or_source_visibility_without_uptake_is_not_success(self):
        r = outcome([event(1, water=True, drink=True), event(2),
                     event(3, (1, 0), True)])
        self.assertIsNone(r["alternative_positive_uptake_step"])

    def test_reacquisition_is_not_survival(self):
        r = outcome([event(1, water=True, drink=True), event(2),
                     event(3, (1, 0), True, True, True)], "dead", 10)
        self.assertEqual(r["status"], "REACQUIRED")
        self.assertEqual(r["terminal"], "dead")

    def test_first_episode_is_not_reselected_for_a_shorter_latency(self):
        rows = [event(1, water=True, drink=True), event(2),
                event(3, (1, 0), True, True, True), event(4, (1, 0)),
                event(5, (2, 0), True, True, True)]
        self.assertEqual(outcome(rows)["alternative_positive_uptake_step"], 3)

    def test_translation_does_not_change_latency(self):
        rows = [event(1, water=True, drink=True), event(2), event(3, (1, 0), True, True, True)]
        translated = deepcopy(rows)
        for row in translated:
            row["position"] = [row["position"][0] + 17, row["position"][1] - 9]
        self.assertEqual(outcome(rows)["latency_from_available_steps"],
                         outcome(translated)["latency_from_available_steps"])

    def test_invalid_time_counts_flags_and_positions_fail(self):
        for field, value in (("step", True), ("step", 2), ("position", [0, True]),
                             ("water_here", 1), ("processing_paid", 0)):
            row = event(1)
            row[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                outcome([row])
        for kwargs in (dict(steps_lived=True, horizon=1, terminal="dead"),
                       dict(steps_lived=0, horizon=1, terminal="censored"),
                       dict(steps_lived=1, horizon=1, terminal="crashed")):
            with self.assertRaises(ValueError):
                revision._timeline([], **kwargs)

    def test_unpaid_or_dry_positive_drink_rejected(self):
        for row in (event(1, drink=True), event(1, water=True, paid=False, drink=True)):
            with self.assertRaises(ValueError):
                outcome([row])


class RevisionJoinTests(unittest.TestCase):
    def test_valid_join_detached_and_no_hidden_world_fields_required(self):
        life = joining_fixture()
        before = deepcopy(life)
        self.assertEqual(revision._resource_events(life), [event(1)])
        self.assertEqual(life, before)

    def test_missing_and_reordered_sidecar_rejected(self):
        for mutation in (lambda e: e.clear(), lambda e: e[0].update(step=2)):
            life = joining_fixture()
            mutation(life["observer_resource_acquisition"]["steps"])
            with self.assertRaises(ValueError):
                revision._resource_events(life)

    def test_action_position_body_and_phase_disagreement_rejected(self):
        for key, value in (("action", "dormir"), ("personal_position", [1, 0]),
                           ("world_position_observer_only", [0, 0]),
                           ("body_after_physics", [0.] * 5),
                           ("paid_decision_work", {"cycles": 0}),
                           ("death_causes", ["zero_water"])):
            life = joining_fixture()
            life["observer_resource_acquisition"]["steps"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                revision._resource_events(life)

    def test_upper_cost_shadow_work_does_not_fake_p13_processing(self):
        life = joining_fixture()
        shadow = dict(
            cycles=3, simulated_steps=0, memory_items=347, replays=0)
        zero = dict(
            cycles=0, simulated_steps=0, memory_items=0, replays=0)
        row = life["trace"][0]
        witness = life["observer_resource_acquisition"]["steps"][0]
        life["manifest"]["experimental_policy"] = {
            "name": revision.UPPER_COST_POLICY}
        row.update(action=None, param=None, option=None)
        row["info"] = {
            "experimental_policy": revision.UPPER_COST_POLICY,
            "funding": "NO_PROCESSING_BUDGET",
            "observer": {"decision_outcome": "no_processing_budget"},
            "cost_control": {
                "schema": revision.UPPER_COST_SCHEMA,
                "motor_authority": "P1.3_REFERENCE_ONLY",
                "candidate_motor_authority": False,
                "settlement_authority":
                    "CUMULATIVE_V2_PHASE_START_BODY",
                "sequential_settlement_max_abs_gap": 0.0,
                "candidate_shadow_work": dict(shadow),
                "reference_choice_work": dict(zero),
                "total_work": dict(shadow),
            },
        }
        row["funding_phases"]["decision"]["work"] = dict(shadow)
        witness.update(
            action=None, param=None, chosen_option=None,
            decision_funding="NO_PROCESSING_BUDGET",
            decision_outcome="no_processing_budget",
            paid_decision_work=dict(shadow))
        witness["phase_payment"]["decision"]["work"] = dict(shadow)

        joined = revision._resource_events(life)
        self.assertEqual(len(joined), 1)
        self.assertFalse(joined[0]["processing_paid"])

    def test_upper_cost_processing_receipt_must_authenticate_total_work(self):
        life = joining_fixture()
        shadow = dict(
            cycles=3, simulated_steps=0, memory_items=347, replays=0)
        zero = dict(
            cycles=0, simulated_steps=0, memory_items=0, replays=0)
        row = life["trace"][0]
        witness = life["observer_resource_acquisition"]["steps"][0]
        life["manifest"]["experimental_policy"] = {
            "name": revision.UPPER_COST_POLICY}
        row.update(action=None, param=None, option=None)
        row["info"] = {
            "experimental_policy": revision.UPPER_COST_POLICY,
            "funding": "NO_PROCESSING_BUDGET",
            "observer": {"decision_outcome": "no_processing_budget"},
            "cost_control": {
                "schema": revision.UPPER_COST_SCHEMA,
                "motor_authority": "P1.3_REFERENCE_ONLY",
                "candidate_motor_authority": False,
                "settlement_authority":
                    "CUMULATIVE_V2_PHASE_START_BODY",
                "sequential_settlement_max_abs_gap": 0.0,
                "candidate_shadow_work": dict(shadow),
                "reference_choice_work": dict(zero),
                "total_work": dict(shadow),
            },
        }
        row["funding_phases"]["decision"]["work"] = dict(shadow)
        witness.update(
            action=None, param=None, chosen_option=None,
            decision_funding="NO_PROCESSING_BUDGET",
            decision_outcome="no_processing_budget",
            paid_decision_work=dict(shadow))
        witness["phase_payment"]["decision"]["work"] = dict(shadow)
        row["info"]["cost_control"]["total_work"]["memory_items"] += 1
        with self.assertRaisesRegex(ValueError, "work mismatch"):
            revision._resource_events(life)

    def test_ordinary_no_processing_still_requires_zero_total_work(self):
        life = joining_fixture()
        row = life["trace"][0]
        witness = life["observer_resource_acquisition"]["steps"][0]
        row.update(action=None, param=None, option=None)
        row["info"] = {
            "funding": "NO_PROCESSING_BUDGET",
            "observer": {"decision_outcome": "no_processing_budget"},
        }
        witness.update(
            action=None, param=None, chosen_option=None,
            decision_funding="NO_PROCESSING_BUDGET",
            decision_outcome="no_processing_budget")
        with self.assertRaisesRegex(ValueError, "paid base block"):
            revision._resource_events(life)

    def test_false_processing_and_water_uptake_rejected(self):
        for key, value in (("decision_funding", "NO_PROCESSING_BUDGET"),
                           ("decision_outcome", "no_processing_budget"),
                           ("water_uptake_above_decay", 30.),
                           ("positive_water_uptake", True), ("capture_here_water", 1)):
            life = joining_fixture()
            life["observer_resource_acquisition"]["steps"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                revision._resource_events(life)

    def test_drink_uptake_is_recomputed_not_assumed_from_command(self):
        for gain in (0., 10.):
            life = joining_fixture()
            row = life["trace"][0]
            witness = life["observer_resource_acquisition"]["steps"][0]
            row.update(action="boire", option="boire")
            row["funding_phases"]["learning"]["body_before"][2] += gain
            witness.update(action="boire", chosen_option="boire", capture_here_water=True,
                           body_after_physics=deepcopy(row["funding_phases"]["learning"]["body_before"]),
                           water_uptake_above_decay=gain, positive_water_uptake=gain > 0)
            self.assertEqual(revision._resource_events(life)[0]["positive_drink"], gain > 0)
            witness["water_uptake_above_decay"] = float("nan")
            with self.assertRaises(ValueError):
                revision._resource_events(life)


class RevisionRuntimeTests(unittest.TestCase):
    def test_paid_processing_matches_actual_perception_and_observers_are_inert(self):
        from unittest.mock import patch
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.modules.mind import Mind
        from i3.runtime.life import run_life

        original = Mind.perceive
        for index in (0, 1):
            seen = []
            def watch(mind, capture, miss):
                seen.append((tuple(mind.pos), bool(capture["here"][0])))
                return original(mind, capture, miss)
            spec = world_for("depletion", "development", index)
            genome = generation_zero(901 + index)
            args = (genome, spec, 860000 + index, 24)
            common = dict(keep_trace=True, protocol="STAGE0_REVISION_SOFTWARE_FIXTURE")
            control = run_life(*args, **common)
            with patch.object(Mind, "perceive", watch):
                observed = run_life(*args, observer_resource_acquisition=True,
                                    observer_full_competition=True, **common)
            for key in ("trace_head", "evidence_head", "actions", "cognitive_accounting",
                        "final_body", "terminal"):
                self.assertEqual(control[key], observed[key])
            joined = revision._resource_events(observed)
            self.assertEqual(seen, [(e["position"], e["water_here"]) for e in joined
                                    if e["processing_paid"]])
            pin = observed["manifest"]["source"]["sha256"]
            report = revision.revision_receipt(observed, expected_protocol=common["protocol"],
                                               expected_source_sha256=pin)
            self.assertIn(report["status"], ("NO_EXPOSURE", "REACQUIRED", "EXPOSED_NO_REACQUISITION"))
            self.assertEqual(report["scientific_verdict"], "NOT_EVALUATED")
            with self.assertRaises(ValueError):
                revision.revision_receipt(control, expected_protocol=common["protocol"],
                                          expected_source_sha256=pin)
            corrupt = deepcopy(observed)
            corrupt["trace"][0]["cognitive_work"]["cycles"] += 1
            with self.assertRaises(ValueError):
                revision.revision_receipt(corrupt, expected_protocol=common["protocol"],
                                          expected_source_sha256=pin)

    def test_actual_dead_at_birth_retained(self):
        from dataclasses import replace
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life

        spec = world_for("depletion", "development", 0)
        spec = replace(spec, body=(80., 70., 0., 90., 100.))
        life = run_life(generation_zero(901), spec, 17, 4, keep_trace=True,
                        observer_resource_acquisition=True, protocol="REVISION_ZERO_STEP_FIXTURE")
        report = revision.revision_receipt(life, expected_protocol=life["manifest"]["protocol"],
                                          expected_source_sha256=life["manifest"]["source"]["sha256"])
        self.assertEqual(report["status"], "NO_EXPOSURE")
        self.assertEqual(report["death_causes"], ["zero_water"])
        self.assertEqual(report["terminal"], "dead")


if __name__ == "__main__":
    unittest.main()
