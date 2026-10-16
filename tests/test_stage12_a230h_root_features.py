"""Negative controls for A2.30-H exact-input census."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_stage12_issue110_b_a230h_root_features import (
    categorize_root_edge, expanded_field_difference, hashed_input,
)
from lab.determinism import canonical_causal_bytes, sha256_hex

WAIT = {"primitive": "attendre", "parameters": {}}
SLEEP = {"primitive": "dormir", "parameters": {}}


def state():
    return {
        "schema_version": "a230h-test-state-v1",
        "x": 2, "y": 2,
        "body": {
            "energy": 70.0, "food": 35.0, "water": 70.0,
            "integrity": 100.0,
        },
        "inventory": {"berry_a": 0},
        "current_water_source": False,
        "current_resources": [],
        "adjacent": [{
            "direction": "east", "x": 3, "y": 2,
            "passable": True, "water_source": False,
            "resources": [], "creature": False,
        }],
        "known_shelter_here": False,
        "is_night": False,
    }


def unknown_edge(s, command, category, fields=None):
    return {
        "state_sha256": sha256_hex(canonical_causal_bytes(s)),
        "input_sha256": hashed_input(s, command),
        "command": command,
        "complete": False,
        "reason": "equipment_input_unseen",
        "category": category,
        "nearest_differing_fields": fields or [],
    }


class A230HRootFeatureTests(unittest.TestCase):
    def test_same_known_command_changed_food_is_not_an_unknown_command(self):
        known = state()
        life = copy.deepcopy(known)
        life["body"]["food"] = 34.3
        example = {
            "state": known, "command": WAIT,
            "input_sha256": hashed_input(known, WAIT),
        }
        row = categorize_root_edge(
            unknown_edge(life, WAIT, "unseen_state_for_known_command",
                         ["body"]), life, [example],
        )
        self.assertEqual(
            row["category"], "unseen_state_for_known_command"
        )
        self.assertEqual(row["top_fields"], ("body",))
        self.assertEqual(row["differences"], ("body.food",))

    def test_missing_command_does_not_impute_body_differences(self):
        trained = state()
        query = copy.deepcopy(trained)
        query["body"]["food"] = 12.0
        row = categorize_root_edge(
            unknown_edge(query, SLEEP, "unseen_command"),
            query,
            [{"state": trained, "command": WAIT,
              "input_sha256": hashed_input(trained, WAIT)}],
        )
        self.assertEqual(row["category"], "unseen_command")
        self.assertEqual(row["differences"], ())

    def test_training_exact_key_must_never_be_called_missing(self):
        trained = state()
        with self.assertRaisesRegex(ValueError, "trained original input"):
            categorize_root_edge(
                unknown_edge(trained, WAIT,
                             "unseen_state_for_known_command", ["body"]),
                trained, [{
                    "state": trained, "command": WAIT,
                    "input_sha256": hashed_input(trained, WAIT),
                }],
            )

    def test_spatial_differences_are_not_promoted_to_causal_effects(self):
        trained = state()
        query = copy.deepcopy(trained)
        query["adjacent"][0]["passable"] = False
        query["inventory"]["berry_a"] = 1
        self.assertEqual(
            expanded_field_difference(query, trained),
            ("adjacent.east.passable", "inventory.berry_a"),
        )

    def test_tampered_root_state_hash_is_rejected(self):
        trained = state()
        tampered = unknown_edge(trained, SLEEP, "unseen_command")
        tampered["state_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "root state SHA"):
            categorize_root_edge(tampered, trained, [])


if __name__ == "__main__":
    unittest.main()
