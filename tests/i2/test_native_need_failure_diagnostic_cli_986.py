"""#986 CLI guard: no birth, no running life, read-only completed journal."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.i2_native_need_failure_diagnostic import diagnose_existing_life


class CompletedLifeDiagnosticCLI986(unittest.TestCase):
    @patch("tools.i2_native_need_failure_diagnostic.sqlite3.connect")
    @patch("tools.i2_native_need_failure_diagnostic.NativePaidI2.inspect")
    def test_incomplete_life_refused_before_any_sqlite_open(self, inspect, connect):
        inspect.return_value.audit.return_value = {
            "revision": 1, "max_steps": 96, "terminal": False,
        }
        with self.assertRaisesRegex(ValueError, "only physically terminal"):
            diagnose_existing_life("/nonexistent/partial.sqlite")
        inspect.return_value.audit.assert_called_once()
        connect.assert_not_called()

    @patch("tools.i2_native_need_failure_diagnostic.report_need_failure_opportunities")
    @patch("tools.i2_native_need_failure_diagnostic.sqlite3.connect")
    @patch("tools.i2_native_need_failure_diagnostic.NativePaidI2.inspect")
    def test_complete_cold_audited_life_opens_read_only(
            self, inspect, connect, observer):
        inspect.return_value.life_ref = "i2:local:example"
        inspect.return_value.genesis_ref = "genesis:example"
        inspect.return_value.audit.return_value = {
            "revision": 1, "max_steps": 1, "terminal": False,
            "temperament": {
                "reward_sensitivity": 0.0, "threat_sensitivity": .5,
                "exploration": .3, "goal_protection": 0.0,
                "affiliation": 0.0,
            },
            "body": {"energy": 78.0, "food": 46.0,
                     "water": 44.0, "integrity": 94.0},
            "site": "camp",
        }
        body = json.dumps({"energy": 78.0, "food": 46.0,
                           "water": 44.0, "integrity": 94.0},
                          sort_keys=True, separators=(",", ":"))
        traits = json.dumps({
            "reward_sensitivity": 0.0, "threat_sensitivity": .5,
            "exploration": .3, "goal_protection": 0.0, "affiliation": 0.0,
        }, sort_keys=True, separators=(",", ":"))
        event = {"claim": {"capture": {"accessible_semantics": ["attendre"]}},
                 "frame": None, "advice": None}
        db = MagicMock()
        connect.return_value.__enter__.return_value = db
        birth = MagicMock()
        birth.fetchone.return_value = (
            "i2:local:example", "genesis:example", traits, 1, 1)
        events = MagicMock()
        events.fetchall.return_value = [(json.dumps(event),)]
        physical = MagicMock()
        physical.fetchall.return_value = [("NO_ACTION", body, body)]
        db.execute.side_effect = [MagicMock(), birth, events, physical]
        observer.return_value = {
            "summary": {"paid_ticks": 1, "diagnostic_only": True},
            "ticks": [{"tick": 1}],
        }
        result = diagnose_existing_life("/nonexistent/complete.sqlite")
        inspect.return_value.audit.assert_called_once()
        self.assertTrue(connect.call_args.kwargs["uri"])
        self.assertIn("mode=ro", connect.call_args.args[0])
        self.assertEqual(result["native_cold_audit"], "PASS")
        self.assertTrue(result["right_censored"])
        self.assertEqual(result["summary"]["paid_ticks"], 1)
        self.assertEqual(observer.call_args.kwargs["factor_enabled"], True)
        self.assertEqual(len(observer.call_args.kwargs["physical"]), 1)
        self.assertEqual(inspect.return_value.audit.call_count, 1)


    @patch("tools.i2_native_need_failure_diagnostic.report_need_failure_opportunities")
    @patch("tools.i2_native_need_failure_diagnostic.sqlite3.connect")
    @patch("tools.i2_native_need_failure_diagnostic.NativePaidI2.inspect")
    def test_refuses_different_extracted_identity_after_cold_audit(
            self, inspect, connect, observer):
        inspect.return_value.life_ref = "i2:expected"
        inspect.return_value.genesis_ref = "genesis:expected"
        inspect.return_value.audit.return_value = {
            "revision": 1, "max_steps": 1, "terminal": False,
            "temperament": {}, "body": {}, "site": "camp",
        }
        db = MagicMock()
        connect.return_value.__enter__.return_value = db
        birth = MagicMock()
        birth.fetchone.return_value = (
            "i2:different", "genesis:expected", "unused", 1, 1)
        events = MagicMock()
        events.fetchall.return_value = [("{}",)]
        physical = MagicMock()
        physical.fetchall.return_value = [("NO_ACTION", "{}", "{}")]
        db.execute.side_effect = [MagicMock(), birth, events, physical]
        with self.assertRaisesRegex(ValueError, "genesis/journal mismatch"):
            diagnose_existing_life("/nonexistent/replaced.sqlite")
        observer.assert_not_called()

    @patch("tools.i2_native_need_failure_diagnostic.report_need_failure_opportunities")
    @patch("tools.i2_native_need_failure_diagnostic.sqlite3.connect")
    @patch("tools.i2_native_need_failure_diagnostic.NativePaidI2.inspect")
    def test_refuses_replaced_final_body_after_cold_audit(
            self, inspect, connect, observer):
        inspect.return_value.life_ref = "i2:expected"
        inspect.return_value.genesis_ref = "genesis:expected"
        inspect.return_value.audit.return_value = {
            "revision": 1, "max_steps": 1, "terminal": False,
            "temperament": {
                "reward_sensitivity": 0.0, "threat_sensitivity": .5,
                "exploration": .3, "goal_protection": 0.0,
                "affiliation": 0.0,
            },
            "body": {"energy": 77.0, "food": 46.0,
                     "water": 44.0, "integrity": 94.0},
            "site": "camp",
        }
        body = json.dumps({"energy": 78.0, "food": 46.0,
                           "water": 44.0, "integrity": 94.0},
                          sort_keys=True, separators=(",", ":"))
        traits = json.dumps({
            "reward_sensitivity": 0.0, "threat_sensitivity": .5,
            "exploration": .3, "goal_protection": 0.0, "affiliation": 0.0,
        }, sort_keys=True, separators=(",", ":"))
        db = MagicMock()
        connect.return_value.__enter__.return_value = db
        birth = MagicMock()
        birth.fetchone.return_value = (
            "i2:expected", "genesis:expected", traits, 1, 1)
        events = MagicMock()
        events.fetchall.return_value = [("{}",)]
        physical = MagicMock()
        physical.fetchall.return_value = [("NO_ACTION", body, body)]
        db.execute.side_effect = [MagicMock(), birth, events, physical]
        with self.assertRaisesRegex(ValueError, "disagrees with cold-audited endpoint"):
            diagnose_existing_life("/nonexistent/replaced-body.sqlite")
        observer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
