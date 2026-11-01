"""Static context routing tests: no cognitive engine imports, births or cohort runs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_context", ROOT / "tools/agent_context.py")
router = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(router)


class ContextRouting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "config").mkdir(parents=True)
        context_map = json.loads((ROOT / "config/agent-context-map.json").read_text(encoding="utf-8"))
        (self.root / router.MAP).write_text(json.dumps(context_map), encoding="utf-8")
        (self.root / router.REGISTRY).write_text(json.dumps({
            "active_generation": "I1", "generations": {"I1": {"role": "active"},
                                                        "I0": {"role": "frozen_reference"}}
        }), encoding="utf-8")
        (self.root / router.INVENTORY).write_text(json.dumps({
            "active_ci_scripts": ["scripts/check_engine_repository.py"],
            "research_or_legacy_review": ["scripts/audit_i0_sqlite.py"]
        }), encoding="utf-8")
        for gen, status in (("i1", "active"), ("i2", "proposal")):
            target = self.root / f"src/{gen}/engine.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({"generation": gen.upper(), "status": status,
                                          "entrypoints": {} if gen == "i2" else {"runtime": "stub"},
                                          "activation": "NOT_REGISTERED_NOT_EXECUTABLE" if gen == "i2" else "active"}),
                              encoding="utf-8")
        for route in context_map["routes"].values():
            for field in ("documents", "owners", "tests", "match_paths"):
                for raw in route[field]:
                    path = self.root / raw.rstrip("/")
                    if raw.endswith("/"):
                        path.mkdir(parents=True, exist_ok=True)
                    elif field == "match_paths" and not Path(raw).suffix:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        (path.parent / (path.name + "_stub.py")).write_text("# stub\n")
                    elif not path.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("# Stub\n", encoding="utf-8")
        for name in context_map["workflows"]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("name: Placeholder\n", encoding="utf-8")

    def test_manifest_and_paths_are_valid(self):
        checked = router.inspect(self.root)
        self.assertEqual(checked["status"], "PASS", checked["errors"])
        self.assertEqual(checked["scientific_gate"], "NOT_EVALUATED")

    def test_path_specificity_beats_broad_i2_route(self):
        result = router.route_context(self.root, paths=["src/i2/modules/lifecycle_external_witness.py"])
        self.assertEqual(result["route"], "i2-witness")
        self.assertEqual(result["contract_status"], "proposal")
        self.assertEqual(result["scientific_gate"], "NOT_EVALUATED")
        self.assertIn("NOT_REGISTERED", result["activation"])

    def test_i1_memory_and_m11_take_specific_owner(self):
        for path, expected in (("src/i1/modules/memory.py", "i1-memory"),
                               ("src/i1/runtime/m11_transactional_mortal.py", "i1-m11")):
            with self.subTest(path=path):
                self.assertEqual(router.route_context(self.root, paths=[path])["route"], expected)

    def test_task_routing_is_not_i2_activation(self):
        result = router.route_context(self.root, task="Review I2 external witness")
        self.assertEqual(result["route"], "i2-witness")
        self.assertNotEqual(result["generation"], result["active_generation"])
        self.assertTrue(result["warning"].startswith("Routing never"))

    def test_ambiguous_paths_fail_closed(self):
        result = router.route_context(self.root, paths=["src/i1/modules/memory.py",
                                                        "src/i1/modules/action_control.py"])
        self.assertEqual(result["status"], "AMBIGUOUS")
        self.assertIn("i1-action", result["candidates"])
        self.assertIn("i1-memory", result["candidates"])

    def test_multidomain_task_asks_for_an_explicit_route(self):
        result = router.route_context(self.root, task="Improve I1 memory and M11")
        self.assertEqual(result["status"], "AMBIGUOUS")
        self.assertEqual(result["candidates"], ["i1-m11", "i1-memory"])

    def test_bad_path_and_wrong_generation_are_rejected(self):
        with self.assertRaises(ValueError):
            router.route_context(self.root, paths=["../../outside.py"])
        with self.assertRaises(ValueError):
            router.route_context(self.root, selected="i2-witness", generation="I1")
        with self.assertRaises(ValueError):
            router.route_context(self.root, selected="i2-witness", paths=["../outside.py"])
        with self.assertRaises(ValueError):
            router.route_context(self.root, selected="i2-witness", paths=["src/i1/modules/memory.py"])

    def test_unknown_workflow_and_script_are_unreviewed(self):
        result = router.route_context(self.root, paths=[".github/workflows/old-science.yml"])
        self.assertEqual(result["execution_metadata"][0]["classification"], "UNREVIEWED")
        self.assertEqual(result["execution_metadata"][0]["permission"], "NOT_GRANTED_BY_ROUTER")
        legacy = router.route_context(self.root, paths=["scripts/audit_i0_sqlite.py"])
        self.assertEqual(legacy["execution_metadata"][0]["classification"],
                         "REVIEW_REQUIRED_NOT_PROVEN_OBSOLETE")

    def test_missing_document_fails_audit(self):
        (self.root / "src/i2/docs/LIFECYCLE_EXTERNAL_WITNESS.md").unlink()
        checked = router.inspect(self.root)
        self.assertEqual(checked["status"], "FAIL")
        self.assertTrue(any("LIFECYCLE_EXTERNAL_WITNESS" in s for s in checked["errors"]))

    def test_handoff_is_never_pretend_validated(self):
        handoff = router.handoff_template(self.root, "i2-witness", "a" * 40)
        self.assertIn("NOT_RUN", handoff)
        self.assertIn("NOT_EVALUATED", handoff)
        self.assertIn("a" * 40, handoff)
        with self.assertRaises(ValueError):
            router.handoff_template(self.root, "i2-witness", "invalidsha")


if __name__ == "__main__":
    unittest.main()
