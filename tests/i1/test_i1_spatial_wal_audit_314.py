"""Synthetic false-positive resistance for the read-only WAL classifier.

Synthetic events do NOT constitute experimental or physical evidence.
"""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[2] / "tools/audit_i1_spatial_navigation_314.py"
SPEC = importlib.util.spec_from_file_location("_audit314", MODULE)
audit314 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit314)


def event(kind, data, *, step=4, attempt="attempt:4", **fields):
    return dict(kind=kind, data=data, t_monde=step,
                attempt_ref=attempt, **fields)


class SpatialWalAuditTests(unittest.TestCase):
    def example(self):
        ref = "option:place-memory:test:4"
        events = [
            event("i1_entity_place_observed", dict(
                entity_id="sighting:water_source:2:1", entity_type="water_source",
                position=[2, 1], first_seen_step=1, source="perceptual_capture"),
                  step=1, attempt="attempt:1"),
            event("i1_place_memory_option_proposed", dict(
                option_ref=ref, entity_id="sighting:water_source:2:1",
                target=[2, 1], next=[2, 1])),
            event("i1_place_memory_option_registration",
                  dict(option_ref=ref, registered=True)),
            event("competition_cycle", {"traces": [
                dict(option_ref=ref, crossed=True)]}),
            event("command_admitted", dict(option_ref=ref,
                primitive="se_deplacer", command_hash="h")),
            event("command_experienced", {}, emitter="action_control",
                  primitive="se_deplacer", command_hash="h"),
            event("world_transition_experienced", {},
                  position_after={"x": 2, "y": 1}),
            event("step_closed", dict(outcome="normal",
                applied_command_count=1, world_advance_count=1)),
        ]
        return events

    def test_valid_sequence_can_prove_first_person_return(self):
        report = audit314.classify_events(self.example())
        self.assertTrue(report["proven_memory_action_applied"])
        self.assertTrue(report["proven_return_arrival"])
        self.assertFalse(report["causal_learning_proven"])

    def test_317_local_sighting_is_not_remote_navigation(self):
        rows = self.example()
        rows.insert(1, event("perceptual_capture", {
            "capture_t_monde": 4, "position": {"x": 1, "y": 1},
            "agency_visible_adjacent": [
                {"x": 2, "y": 1, "direction": "east", "passable": True},
            ],
        }))
        report = audit314.classify_events(rows)
        self.assertTrue(report["proven_return_arrival"])
        metrics = report["memory_causality_317"]
        self.assertEqual(metrics["proposals_to_unseen_sites"], 0)
        self.assertEqual(metrics["physically_applied_unseen_multihop_first_hops"], 0)
        self.assertEqual(metrics["physically_arrived_from_outside_current_perception"], 0)
        self.assertFalse(metrics["examples"][0]["target_outside_perception"])

    def test_317_remote_intention_is_not_physical_result(self):
        rows = self.example()[:3]
        rows.insert(1, event("perceptual_capture", {
            "capture_t_monde": 4, "position": {"x": 0, "y": 1},
            "agency_visible_adjacent": [
                {"x": 1, "y": 1, "direction": "east", "passable": True},
            ],
        }))
        for row in rows:
            if row["kind"] == "i1_place_memory_option_proposed":
                row["data"]["next"] = [1, 1]
        metrics = audit314.classify_events(rows)["memory_causality_317"]
        self.assertEqual(metrics["proposed_unseen_multihop_options"], 1)
        self.assertEqual(metrics["physically_applied_unseen_multihop_first_hops"], 0)
        self.assertEqual(metrics["physically_applied_memory_actions_using_prior_td"], 0)

    def test_317_late_unrelated_td_is_not_learned_memory(self):
        rows = self.example()
        rows.insert(1, event("perceptual_capture", {
            "capture_t_monde": 4, "position": {"x": 1, "y": 1},
            "agency_visible_adjacent": [{"x": 2, "y": 1}],
        }))
        rows.append(event("td_update_published", {
            "updated_signatures": ["memory_place_return:sighting:water_source:2:1"],
        }, step=5, attempt="attempt:5"))
        metrics = audit314.classify_events(rows)["memory_causality_317"]
        self.assertEqual(metrics["physically_applied_memory_actions_using_prior_td"], 0)
        self.assertEqual(metrics["assessments_with_prior_published_td"], 0)

    def test_317_remote_multihop_arrival_across_sleep_is_certified(self):
        entity = "sighting:wood:9:8"
        old = "option:place-memory:place:sighting:wood:9:8:at:9:8:from:11:8:via:10:8"
        new = "option:place-memory:place:sighting:wood:9:8:at:9:8:from:10:8:via:9:8"
        rows = [event("i1_entity_place_observed", dict(
            entity_id=entity, position=[9,8], first_seen_step=1,
            source="perceptual_capture"),step=1,attempt="a1")]
        def add_step(t, start, finish, option, *, sleep=False):
            attempt = "a"+str(t)
            if not sleep:
                rows.append(event("perceptual_capture", dict(
                    capture_t_monde=t, position={"x":start[0],"y":start[1]},
                    agency_visible_adjacent=[
                        {"x": start[0]-1, "y":start[1]}],
                ),step=t,attempt=attempt))
                rows.append(event("i1_place_memory_option_proposed",dict(
                    option_ref=option,entity_id=entity,target=[9,8],
                    next=list(finish)),step=t,attempt=attempt))
                rows.append(event("i1_place_memory_option_registration",
                    dict(option_ref=option,registered=True),step=t,attempt=attempt))
                rows.append(event("competition_cycle", {"traces":[dict(
                    option_ref=option,crossed=True)]},step=t,attempt=attempt))
            primitive="dormir" if sleep else "se_deplacer"
            ref="option:sleep" if sleep else option
            h="hash"+str(t)
            rows.extend([
                event("command_admitted",dict(option_ref=ref,
                    primitive=primitive,command_hash=h),step=t,attempt=attempt),
                event("command_experienced",{},step=t,attempt=attempt,
                    emitter="action_control",primitive=primitive,command_hash=h),
                event("world_transition_experienced",{},step=t,attempt=attempt,
                    emitter="world_and_body",
                    position_after={"x":finish[0],"y":finish[1]}),
                event("step_closed",dict(outcome="normal",
                    applied_command_count=1,world_advance_count=1),
                    step=t,attempt=attempt)])
        add_step(4,(11,8),(10,8),old)
        rows.append(event("i1_place_memory_intention_continued",dict(
            previous_option_ref=old,next_option_ref=new,
            confirmed_position=[10,8],
            source="previous_applied_command_and_current_perception",
            forced_motor_selection=False),step=5,attempt="a5"))
        add_step(5,(10,8),(10,8),None,sleep=True)
        add_step(6,(10,8),(10,8),None,sleep=True)
        add_step(7,(10,8),(9,8),new)
        answer=audit314.classify_events(rows)["memory_causality_317"]
        self.assertEqual(answer["completed_remote_multihop_returns"],1)
        self.assertEqual(answer["completed_remote_returns_after_sleep"],1)
        self.assertEqual(answer["completed_remote_return_examples"][0][
            "motor_world_steps"],[4,7])
        # No physical completion without the intermediate explicit cognitive
        # continuation event, irrespective of a later matching physical hop.
        damaged=[e for e in rows if e["kind"] !=
                 "i1_place_memory_intention_continued"]
        self.assertEqual(audit314.classify_events(damaged)[
            "memory_causality_317"]["completed_remote_multihop_returns"],0)

    def test_proposal_without_action_cannot_prove_return(self):
        report = audit314.classify_events(self.example()[:4])
        self.assertFalse(report["proven_memory_action_applied"])
        self.assertEqual(report["stages"]["physically_applied"], 0)

    def test_command_different_from_admitted_option_is_not_proof(self):
        rows = self.example()
        rows[4]["data"]["option_ref"] = "other"
        report = audit314.classify_events(rows)
        self.assertFalse(report["proven_memory_action_applied"])

    def test_unseen_future_resource_cannot_be_past_experience(self):
        rows = self.example()
        rows[0]["t_monde"] = 5
        report = audit314.classify_events(rows)
        self.assertFalse(report["proven_memory_action_applied"])

    def test_not_at_destination_is_not_arrival(self):
        rows = self.example()
        rows[6]["position_after"] = {"x": 3, "y": 1}
        report = audit314.classify_events(rows)
        self.assertFalse(report["proven_memory_action_applied"])

    def test_uncommitted_transition_is_not_physical_proof(self):
        rows = self.example()[:-1]
        report = audit314.classify_events(rows)
        self.assertEqual(report["stages"]["physically_applied"], 0)


if __name__ == "__main__":
    unittest.main()
