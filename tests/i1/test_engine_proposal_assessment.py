"""Future-engine readiness is strictly read-only and cannot activate a life."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from new_engine import apply_workspace
from assess_engine_proposal import inspect_proposal


class EngineProposalAssessmentTests(unittest.TestCase):
    def _fixture(self, root):
        (root / "config").mkdir()
        (root / "config/engine-registry.json").write_bytes(
            (ROOT / "config/engine-registry.json").read_bytes())
        apply_workspace("I2", "I1", root / "src/i2", root=root)

    def test_inert_generated_proposal_is_not_ready_for_registration(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self._fixture(root)
            before = (root / "config/engine-registry.json").read_bytes()
            report = inspect_proposal("I2", root=root)
            self.assertEqual(report["status"], "BLOCKED")
            self.assertTrue(report["checks"]["contract_is_proposal"])
            self.assertTrue(report["checks"]["registered_earlier_parent"])
            for key in ("lab_implementation_present",
                        "runtime_implementation_present",
                        "cognition_implementation_present",
                        "independent_tests_present"):
                self.assertIn(key, report["blocked_by"])
            self.assertEqual(report["activation"], "FORBIDDEN")
            self.assertEqual(report["registration"], "FORBIDDEN")
            self.assertEqual(report["scientific_evidence"], "NOT_EVALUATED")
            self.assertEqual((root / "config/engine-registry.json").read_bytes(),
                             before)

    def test_parent_runtime_import_is_flagged_not_inherited(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self._fixture(root)
            (root / "src/i2/modules/adaptation.py").write_text(
                "from i1lab.i1_natural_runtime import I1Runtime\n")
            report = inspect_proposal("I2", root=root)
            self.assertFalse(report["checks"]["no_parent_runtime_imports"])
            self.assertIn("no_parent_runtime_imports", report["blocked_by"])

    def test_fake_activation_or_registration_is_never_authorized(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self._fixture(root)
            contract_path = root / "src/i2/engine.json"
            c = json.loads(contract_path.read_text())
            c["activation"] = "ACTIVE"
            c["entrypoints"] = {"birth": "example"}
            contract_path.write_text(json.dumps(c))
            report = inspect_proposal("I2", root=root)
            self.assertIn("contract_is_proposal", report["blocked_by"])
            self.assertEqual(report["activation"], "FORBIDDEN")
            with self.assertRaises(ValueError):
                inspect_proposal("I1", root=root)


if __name__ == "__main__":
    unittest.main()
