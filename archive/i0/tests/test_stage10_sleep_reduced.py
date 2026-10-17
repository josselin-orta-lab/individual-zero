"""Reduced sleep observations must never be unrestricted waking captures."""
import unittest
from copy import deepcopy
from i0.modules.sleep_reduced import reduced_sleep_capture


def fixture():
    local = {
        "t_monde": 4,
        "position": {"x": 3, "y": 7},
        "adjacent": [
            {"direction": "south", "position": {"x": 3, "y": 8},
             "creature": True, "passable": True, "water_source": True,
             "resources": ["berry_a"], "oracle_canary": "SECRET"},
            {"direction": "north", "position": {"x": 3, "y": 6},
             "creature": False, "passable": True, "resources": ["berry_b"]},
        ],
        "visible_entities": [{"entity_id": "hidden_secret", "properties": {"secret": "SECRET"}}],
        "inventory": {"wood": 3}, "current_water_source": True,
        "current_resources": ["berry_b"], "oracle_canary": "SECRET",
    }
    tele = {"energy": 30.0, "food": 60.0, "water": 12.0, "integrity": 80.0, "hidden_health": "SECRET"}
    return dict(local_state=local, telemetry=tele, source_capture_ref="physical:4",
                world_step=4, critical_thresholds={"water": 15.0, "integrity": 10.0})


class ReducedSleepTests(unittest.TestCase):
    def test_only_authorized_fields_reach_reflex(self):
        result = reduced_sleep_capture(**fixture())
        self.assertEqual(result.world_step, 4)
        self.assertTrue(result.adjacent_creature)
        self.assertEqual(result.critical_body_channels, ("water",))
        self.assertEqual(len(result.capture.adjacent_creatures), 1)
        self.assertEqual(result.capture.current_resources, ())
        self.assertFalse(result.capture.current_water_source)
        self.assertEqual(result.capture.visible_entities, ())
        self.assertEqual(result.capture.inventory, {})
        self.assertTrue(all(not cell.resources and not cell.water_source for cell in result.capture.adjacent))
        self.assertNotIn("SECRET", repr(result))
        self.assertNotIn("berry_a", repr(result))

    def test_no_retroactive_perception_or_mutation_of_source(self):
        original = fixture()
        source = deepcopy(original)
        result = reduced_sleep_capture(**source)
        source["local_state"]["adjacent"].append({"direction": "east", "position": {"x": 4, "y": 7},
                                                      "creature": False, "passable": True})
        self.assertEqual(len(result.capture.adjacent), 2)
        self.assertEqual(original["local_state"], fixture()["local_state"])

    def test_wake_signal_does_not_fabricate_numeric_risk(self):
        result = reduced_sleep_capture(**fixture())
        self.assertNotIn("risk", result.__dataclass_fields__)
        self.assertNotIn("alert_score", result.__dataclass_fields__)

    def test_stale_or_inconsistent_clock_rejected(self):
        x = fixture()
        x["world_step"] = 5
        with self.assertRaises(ValueError):
            reduced_sleep_capture(**x)

    def test_invalid_body_telemetry_rejected(self):
        for bad in (float("nan"), float("inf"), -1.0, True, None):
            x = fixture()
            x["telemetry"]["water"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reduced_sleep_capture(**x)

    def test_duplicate_or_invented_reflex_directions_rejected(self):
        x = fixture()
        x["local_state"]["adjacent"].append(deepcopy(x["local_state"]["adjacent"][0]))
        with self.assertRaises(ValueError):
            reduced_sleep_capture(**x)
        y = fixture()
        y["local_state"]["adjacent"][0]["direction"] = "north-west"
        with self.assertRaises(ValueError):
            reduced_sleep_capture(**y)

    def test_critical_threshold_must_be_finite_in_range(self):
        x = fixture()
        x["critical_thresholds"] = {"water": float("nan")}
        with self.assertRaises(ValueError):
            reduced_sleep_capture(**x)
        x = fixture()
        x["critical_thresholds"] = {"oracle": 10.0}
        with self.assertRaises(ValueError):
            reduced_sleep_capture(**x)

    def test_no_threat_uses_no_new_creature_evidence(self):
        x = fixture()
        for raw in x["local_state"]["adjacent"]:
            raw["creature"] = False
        result = reduced_sleep_capture(**x)
        self.assertFalse(result.adjacent_creature)
        self.assertEqual(result.capture.adjacent_creatures, ())


if __name__ == "__main__":
    unittest.main()
