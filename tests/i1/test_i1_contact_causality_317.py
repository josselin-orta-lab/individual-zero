"""Adversarial synthetic tests: no synthetic episode counts as lived proof."""
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location(
    "audit_contact_317", TOOLS / "audit_i1_317_contact_causality.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sample():
    def e(kind, data=None, **kwargs):
        return dict(kind=kind, t_monde=4, attempt_ref="attempt:4",
                    data={} if data is None else data, **kwargs)
    body = {"energy": 70.0, "food": 42.0, "water": 28.0,
            "integrity": 80.0}
    changed = dict(body, water=67.6)
    rows = [
        e("perceptual_capture", {
            "position": {"x": 5, "y": 5},
            "dual_scope_visible_body": body}),
        e("i1_entity_place_observed", {
            "entity_id": "sighting:artifact:5:5", "entity_type": "artifact",
            "source": "perceptual_capture",
            "position": [5, 5]}),
        e("command_admitted", {"command_hash": "command:4",
                                "primitive": "boire", "option_ref": "option:4"}),
        e("command_experienced", primitive="boire", command_hash="command:4"),
        e("world_transition_experienced", effects={"drank": True},
          position_after={"x": 5, "y": 5}, body_after=changed),
        e("step_closed", {"outcome": "normal",
                           "applied_command_count": 1,
                           "world_advance_count": 1}),
        dict(kind="stage8_option_evaluation", t_monde=7,
             attempt_ref="attempt:7", data={
                 "learning_signature": "memory_place_return:sighting:artifact:5:5",
                 "learned_value_status": "learned", "learned_value": 2.0}),
    ]
    return rows


class ContactCausality317Tests(unittest.TestCase):
    def test_realistically_shaped_positive_contact_does_not_prove_causality(self):
        result = module.classify(sample())
        self.assertEqual(result["counters"]["physically_certified_contacts"], 1)
        self.assertEqual(result["counters"]["positive_water_delta"], 1)
        self.assertEqual(
            result["counters"]["contacts_with_later_learned_memory_evaluation"], 1)
        self.assertFalse(result["entity_causal_learning_proven"])
        self.assertEqual(result["examples"][0]["entity_causal_benefit"],
                         "not_established")

    def test_carried_food_cannot_credit_colocated_site(self):
        events = sample()
        events[3]["primitive"] = "manger"
        events[3]["parameters"] = {"target": "berry_a"}
        events[2]["data"]["primitive"] = "manger"
        events[4]["effects"] = {"ate": "berry_a"}
        events[4]["body_after"] = {
            "energy": 69.5, "food": 51.8,
            "water": 27.6, "integrity": 80.0}
        counts = module.classify(events)["counters"]
        self.assertEqual(counts["inventory_mediated_ingestions"], 1)
        self.assertEqual(counts["collection_with_unique_witnessed_type"], 0)
        self.assertEqual(module.classify(events)["examples"][0][
            "direct_target_witnesses"], [])

    def test_collected_type_must_match_perceived_entity(self):
        events = sample()
        events[3]["primitive"] = "collecter"
        events[3]["parameters"] = {"target": "berry_a"}
        events[2]["data"]["primitive"] = "collecter"
        events[4]["effects"] = {
            "collected": {"kind": "berry_a", "quantity": 1}}
        counts = module.classify(events)["counters"]
        self.assertEqual(counts["collection_without_unique_witnessed_type"], 1)
        events[1]["data"]["entity_type"] = "berry_a"
        counts = module.classify(events)["counters"]
        self.assertEqual(counts["collection_with_unique_witnessed_type"], 1)
        self.assertEqual(module.classify(events)["examples"][0][
            "entity_causal_benefit"], "not_established")

    def test_preexisting_td_is_not_new_entity_learning(self):
        events = sample()
        entity = "memory_place_return:sighting:artifact:5:5"
        events.insert(0, dict(
            kind="td_update_published", t_monde=2, attempt_ref="before",
            data={"updated_signatures": [entity]}))
        result = module.classify(events)
        counts = result["counters"]
        self.assertEqual(
            counts["contacts_with_preexisting_memory_td_and_later_read"], 1)
        self.assertEqual(counts["contacts_followed_by_memory_td_update"], 0)
        self.assertFalse(result["entity_causal_learning_proven"])

    def test_later_td_trace_is_not_entity_effect(self):
        events = sample()
        events.append(dict(
            kind="td_update_published", t_monde=6, attempt_ref="after",
            data={"updated_signatures": [
                "memory_place_return:sighting:artifact:5:5"]}))
        result = module.classify(events)
        self.assertEqual(
            result["counters"]["contacts_followed_by_memory_td_update"], 1)
        self.assertTrue(result["examples"][0]["post_contact_td_action_update"])
        self.assertFalse(result["entity_causal_learning_proven"])

    def test_multiple_entities_remain_ambiguous(self):
        events = sample()
        other = dict(events[1], data=dict(events[1]["data"],
                   entity_id="sighting:other:5:5", entity_type="other"))
        events.insert(2, other)
        counts = module.classify(events)["counters"]
        self.assertEqual(counts["multiple_colocated_sightings"], 1)
        self.assertEqual(counts["one_colocated_sighting"], 0)

    def test_wrong_command_hash_or_order_is_not_physical_evidence(self):
        events = sample()
        events[3]["command_hash"] = "unrelated"
        result = module.classify(events)
        self.assertEqual(result["counters"]["physically_certified_contacts"], 0)
        self.assertEqual(result["counters"]["unverifiable_contacts"], 1)
        events = sample()
        events.insert(2, events.pop(5))
        self.assertEqual(module.classify(events)["counters"][
            "physically_certified_contacts"], 0)

    def test_missing_physiology_never_creates_zero_effect(self):
        events = sample()
        del events[4]["body_after"]["water"]
        self.assertEqual(module.classify(events)["counters"][
            "unverifiable_contacts"], 1)

    def test_later_evaluation_is_not_preexisting_causal_learning(self):
        events = sample()
        events[-1]["t_monde"] = 2
        result = module.classify(events)
        self.assertEqual(result["counters"][
            "contacts_with_later_learned_memory_evaluation"], 0)
        self.assertFalse(result["entity_causal_learning_proven"])


if __name__ == "__main__":
    unittest.main()
