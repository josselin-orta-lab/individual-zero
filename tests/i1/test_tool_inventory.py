"""Current tools inventory is conservative, complete and non-destructive."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from check_tool_inventory import check


class ScriptInventoryTests(unittest.TestCase):
    def test_current_script_inventory_is_complete(self):
        self.assertEqual(check(ROOT)["status"], "PASS", check(ROOT))
        inventory = json.loads((ROOT / "config/tool-inventory.json").read_text())
        self.assertGreater(len(inventory["research_or_legacy_review"]), 75)
        self.assertNotIn("scripts/test_i1_ci.py",
                         inventory["research_or_legacy_review"])

    def test_missing_or_unclassified_script_is_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "scripts").mkdir()
            data = json.loads((ROOT / "config/tool-inventory.json").read_text())
            for script in data["active_ci_scripts"] + data["research_or_legacy_review"]:
                p = root / script
                p.write_text("# mock\n")
            (root / "config/tool-inventory.json").write_text(json.dumps(data))
            self.assertEqual(check(root)["status"], "PASS")
            (root / "scripts/unclassified.py").write_text("# extra\n")
            self.assertEqual(check(root)["status"], "FAIL")
