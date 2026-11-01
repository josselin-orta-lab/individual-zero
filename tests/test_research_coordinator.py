"""Research coordination is read-only: synthetic repository fixtures only."""
from datetime import datetime, timezone, timedelta
import importlib.util
import json
import hashlib
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("research_coordinator", ROOT / "tools/research_coordinator.py")
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


class ResearchCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.program = json.loads((ROOT / rc.PROGRAM).read_text(encoding="utf-8"))
        (self.root / "config").mkdir(parents=True)
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program), encoding="utf-8")
        (self.root / rc.REGISTRY).write_text(json.dumps(
            {"active_generation":"I1", "generations":{"I0":{"role":"frozen_reference"},"I1":{"role":"active"}}}))
        for dirname in self.program.get("catalog_roots", []):
            (self.root / dirname).mkdir(parents=True, exist_ok=True)
        for gen, status, entrypoints in (("i1","active",{"birth":"example"}),
                                          ("i2","proposal",{})):
            p = self.root / f"src/{gen}/engine.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"status":status,"entrypoints":entrypoints}))
        by_path = {}
        for src in self.program["source_checks"]:
            by_path.setdefault(src["path"], []).append(src["marker"])
        for name, markers in by_path.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# Source\n" + "\n".join(markers) + "\n", encoding="utf-8")
        for source in self.program["source_checks"]:
            raw = (self.root / source["path"]).read_bytes()
            source["blob_sha"] = hashlib.sha1(
                b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program), encoding="utf-8")
        self.sha = "a" * 40

    def test_manifest_and_evidence_markers(self):
        result = rc.audit(self.root)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertTrue(all(v["status"] == "PIN_MATCH"
                            for v in rc.source_integrity(self.root,self.program).values()))

    def test_global_gates_and_generation_boundary(self):
        state = rc.research_state(self.root, at_sha=self.sha)
        self.assertEqual(state["active_generation"], "I1")
        self.assertFalse(state["generations"]["I2"]["active"])
        self.assertFalse(state["generations"]["I2"]["entrypoints_declared"])
        self.assertEqual(state["generations"]["I2"]["registry_role"], "UNREGISTERED")
        self.assertTrue(all(not g["gate_approved"] for g in state["gates"]))
        self.assertEqual(state["scientific_verdict"], "NOT_EVALUATED")

    def test_next_action_is_review_not_experiment(self):
        state = rc.research_state(self.root, at_sha=self.sha)
        ranked = rc.recommendations(state, self.program, 8)
        self.assertEqual(ranked["recommended_next"]["id"], "I2-G3-CONTRACT")
        self.assertFalse(ranked["recommended_next"]["human_review_required"])
        self.assertEqual(ranked["execution"], "NOT_PERFORMED")
        self.assertEqual(ranked["promotion"], "NOT_AUTHORIZED")
        compare = next(x for x in ranked["proposals"] if x["id"] == "I2-G5-COMPARISON")
        self.assertEqual(compare["stage"], "BLOCKED_GATE")
        self.assertIn("I2-G0", compare["blocked_by_gates"])

    def test_changed_citation_disallows_outdated_recommendation(self):
        (self.root / "src/i2/docs/STATUS.md").write_text("Source changed, review required")
        state = rc.research_state(self.root, at_sha=self.sha)
        self.assertEqual(state["status"], "SOURCE_REVIEW_REQUIRED")
        ranked = rc.recommendations(state, self.program, 8)
        self.assertNotEqual(ranked["recommended_next"]["id"], "I2-G3-CONTRACT")
        self.assertTrue(any(p["stage"] == "SOURCE_REVIEW_REQUIRED" for p in ranked["proposals"]))

    def test_snapshot_cannot_prove_approval_even_if_issue_closed(self):
        now = datetime.now(timezone.utc)
        p = self.root / "issues.json"
        p.write_text(json.dumps({"schema": rc.GITHUB_SCHEMA,
            "repository": "josselin-orta-lab/individual-zero",
            "commit_sha":self.sha, "captured_at":now.isoformat(),
            "issues":[{"number":661,"state":"closed",
                       "url":"https://github.com/josselin-orta-lab/individual-zero/issues/661"}]}))
        status = rc.issue_snapshot(p, self.program["project"], self.sha, 24)
        self.assertEqual(status["status"], "SCHEMA_VALID_NOT_ATTESTED")
        state = rc.research_state(self.root, at_sha=self.sha, snapshot=p)
        ranked = rc.recommendations(state, self.program, 8)
        review = next(x for x in ranked["proposals"] if x["id"]=="I1-G0-ARCHIVE")
        self.assertEqual(review["stage"], "CLOSED_ISSUE_RECONCILIATION_REQUIRED")
        self.assertTrue(ranked["external_verification_required"])
        self.assertEqual(rc.issue_snapshot(p,self.program["project"],"b"*40,24)["status"], "INVALID_OR_STALE")
        self.assertEqual(rc.issue_snapshot(p,self.program["project"],None,24)["status"], "INVALID_OR_STALE")

    def test_cycle_is_rejected(self):
        self.program["gates"][0]["prerequisites"] = ["I2-G6"]
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program))
        result = rc.audit(self.root)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("cyclic" in e for e in result["errors"]))

    def test_no_minted_scientific_gate(self):
        self.program["gates"][1]["reported_assessment"] = "APPROVED"
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program))
        self.assertEqual(rc.audit(self.root)["status"], "FAIL")
        registry = json.loads((self.root / rc.REGISTRY).read_text())
        registry["generations"]["I2"] = {"role":"active"}
        (self.root / rc.REGISTRY).write_text(json.dumps(registry))
        self.assertTrue(any("proposal" in e for e in rc.audit(self.root)["errors"]))

    def test_dependency_graph_and_cli(self):
        diagram = rc.graph(self.program)
        self.assertIn("I2_G1 --> I2_G3", diagram)
        self.assertIn("I2_G5 --> I2_G6", diagram)
        self.assertEqual(rc.main(["audit"],self.root), 0)
        self.assertEqual(rc.main(["recommend","--top","2","--at-sha",self.sha,
                                  "--format","json"],self.root), 0)
        self.assertEqual(rc.main(["recommend","--top","31"],self.root), 2)



    def test_structural_audit_reports_live_status_drift_without_scientific_approval(self):
        path = self.root / "src/i2/docs/STATUS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nG2 synthetic status updated.\n",
                        encoding="utf-8")
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(rc.main(["audit", "--structure-only"], self.root), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["audit_mode"], "STRUCTURE_ONLY")
        self.assertEqual(report["source_status"], "SOURCE_REVIEW_REQUIRED")
        self.assertIn("i2-proposal", report["source_review_required"])
        self.assertEqual(report["scientific_verdict"], "NOT_EVALUATED")
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(rc.main(["audit"], self.root), 1)
        self.assertEqual(json.loads(output.getvalue())["status"], "FAIL")
        state = rc.research_state(self.root, at_sha=self.sha)
        self.assertEqual(state["status"], "SOURCE_REVIEW_REQUIRED")
        self.assertTrue(all(not gate["gate_approved"] for gate in state["gates"]))


    def test_cross_manifest_source_pins_must_agree_even_for_structural_ci(self):
        referenced = next(s for s in self.program["source_checks"]
                          if s["id"] == "i2-proposal")
        dossier_path = self.root / "config/research-dossiers.json"
        dossier_path.write_text(json.dumps({"sources": [{
            "id": "i2-status", "path": referenced["path"],
            "blob_sha": "b" * 40}]}), encoding="utf-8")
        outcome = rc.audit(self.root)
        self.assertEqual(outcome["status"], "FAIL")
        self.assertTrue(any("source pins diverge" in error
                            for error in outcome["errors"]))
        with redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(rc.main(["audit", "--structure-only"], self.root), 1)
        self.assertEqual(json.loads(stream.getvalue())["status"], "FAIL")

        dossier_path.write_text(json.dumps({"sources": [{
            "id": "i2-status", "path": referenced["path"],
            "blob_sha": referenced["blob_sha"]}]}), encoding="utf-8")
        self.assertEqual(rc.audit(self.root)["status"], "PASS")

    def test_duplicate_dossier_pins_for_same_path_are_rejected(self):
        referenced = next(s for s in self.program["source_checks"]
                          if s["id"] == "i2-proposal")
        dossier_path = self.root / "config/research-dossiers.json"
        dossier_path.write_text(json.dumps({"sources": [
            {"id": "a", "path": referenced["path"], "blob_sha": referenced["blob_sha"]},
            {"id": "b", "path": referenced["path"], "blob_sha": "b" * 40}
        ]}), encoding="utf-8")
        outcome = rc.audit(self.root)
        self.assertEqual(outcome["status"], "FAIL")
        self.assertTrue(any("inconsistent dossier source pins" in e
                            for e in outcome["errors"]))


if __name__ == "__main__":
    unittest.main()
