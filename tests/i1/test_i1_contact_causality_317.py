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
            "entity_id": "sighting:artifact:5:5", "source": "perceptual_capture",
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

    def test_multiple_entities_remain_ambiguous(self):
        events = sample()
        other = dict(events[1], data=dict(events[1]["data"],
                   entity_id="sighting:other:5:5"))
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
