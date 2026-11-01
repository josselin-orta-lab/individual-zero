"""Read-only research graph, source coverage and traceability tests."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_coordinator_graph", ROOT / "tools/research_coordinator.py")
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


class ResearchKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.program = json.loads((ROOT / rc.PROGRAM).read_text(encoding="utf-8"))
        for dirname in self.program["catalog_roots"]:
            (self.root / dirname).mkdir(parents=True, exist_ok=True)
        (self.root / "config").mkdir(exist_ok=True)
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program), encoding="utf-8")
        (self.root / rc.REGISTRY).write_text(json.dumps(
            {"active_generation": "I1", "generations": {
                "I0": {"role": "frozen_reference"}, "I1": {"role": "active"}}}))
        for gen, status in (("i1", "active"), ("i2", "proposal")):
            path = self.root / f"src/{gen}/engine.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"generation": gen.upper(), "status": status,
                                        "entrypoints": {} if gen == "i2" else {"runtime": "fake"}}))
        by_path = {}
        for s in self.program["source_checks"]:
            by_path.setdefault(s["path"], []).append(s["marker"])
        for relative, markers in by_path.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Synthetic source\n" + "\n".join(markers))
        for source in self.program["source_checks"]:
            raw = (self.root / source["path"]).read_bytes()
            source["blob_sha"] = hashlib.sha1(
                b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program), encoding="utf-8")
        self.sha = "a" * 40

    def state(self):
        return rc.research_state(self.root, at_sha=self.sha)

    def test_manifest_and_typed_graph(self):
        self.assertEqual(rc.audit(self.root)["status"], "PASS")
        knowledge = rc.knowledge_graph(self.program, self.state())
        node_ids = [x["id"] for x in knowledge["nodes"]]
        self.assertEqual(len(node_ids), len(set(node_ids)))
        self.assertEqual(knowledge["scientific_verdict"], "NOT_EVALUATED")
        self.assertIn("question:I1-L3", node_ids)
        self.assertIn("finding:I1-A1C-TARGETED-NOGO", node_ids)
        self.assertIn("finding:I1-A2R-NOT-EXECUTED", node_ids)
        links = {(x["from"], x["to"], x["relation"]) for x in knowledge["edges"]}
        self.assertIn(("finding:I1-A1C-TARGETED-NOGO", "question:I1-L3",
                       "qualifies_question"), links)
        self.assertIn(("gate:I2-G6", "gate:I2-G5", "requires_unapproved_gate"), links)
        self.assertIn(("intervention:I2-G1-REVIEW", "issue:662", "tracked_by"), links)
        self.assertIn(("source:i1-a1c", "artifact:src/i1/docs/STATUS.md",
                       "located_in"), links)
        self.assertFalse(next(x for x in knowledge["nodes"]
                              if x["id"] == "gate:I2-G3")["gate_approved"])

    def test_trace_preserves_negative_and_null_results(self):
        trace = rc.explain(rc.knowledge_graph(self.program, self.state()), "question:I1-L3")
        ids = {x["id"] for x in trace["nodes"]}
        self.assertIn("finding:I1-A1C-TARGETED-NOGO", ids)
        self.assertIn("finding:I1-A2R-NOT-EXECUTED", ids)
        self.assertIn("source:i1-l3", ids)
        self.assertEqual(trace["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(trace["status"], "PROVENANCE_LINKS_ONLY")

    def test_missing_source_blocks_valid_trace(self):
        (self.root / "src/i1/docs/STATUS.md").write_text("# Missing target markers\n")
        state = self.state()
        trace = rc.explain(rc.knowledge_graph(self.program, state), "I1-L3")
        self.assertEqual(trace["status"], "SOURCE_REVIEW_REQUIRED")
        self.assertIn("source:i1-a1c", trace["changed_or_missing_sources"])
        self.assertFalse(any(g["gate_approved"] for g in state["gates"]))

    def test_catalog_is_explicitly_unreviewed(self):
        (self.root / "docs/research/exp-thing-results.md").write_text(
            "UNVERIFIED: these aren't scientific findings")
        (self.root / "docs/research/experiment-prereg.md").write_text(
            "Protocol draft, no observations")
        result = rc.catalog(self.root, self.program, 20)
        self.assertEqual(result["status"], "NAVIGATION_ONLY")
        self.assertTrue(result["total_markdown_files"] >= 4)
        self.assertEqual(result["scientific_verdict"], "NOT_EVALUATED")
        filenames = {item["path"]: item for item in result["sample_unreviewed"]}
        self.assertEqual(filenames["docs/research/exp-thing-results.md"]["filename_hint"],
                         "possible_result")
        self.assertEqual(filenames["docs/research/exp-thing-results.md"]["review"],
                         "NOT_REVIEWED_FOR_RESEARCH_GRAPH")
        self.assertEqual(len(rc.catalog(self.root, self.program, 0)["sample_unreviewed"]), 0)

    def test_graph_rejects_malformed_finding_and_catalog_location(self):
        self.program["findings"][0]["questions"] = ["NOT-A-QUESTION"]
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program))
        self.assertEqual(rc.audit(self.root)["status"], "FAIL")
        self.program["findings"][0]["questions"] = ["I1-L3"]
        self.program["catalog_roots"].append("../../external")
        (self.root / rc.PROGRAM).write_text(json.dumps(self.program))
        self.assertEqual(rc.audit(self.root)["status"], "FAIL")
        with self.assertRaises(ValueError):
            rc.catalog(self.root, self.program)

    def test_exact_source_blob_changes_even_when_marker_remains(self):
        path = self.root / "src/i1/docs/STATUS.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "\nNew information that changes interpretation.\n",
                        encoding="utf-8")
        state = self.state()
        self.assertEqual(state["status"], "SOURCE_REVIEW_REQUIRED")
        self.assertEqual(state["source_checks"]["i1-a1c"]["status"], "SOURCE_BLOB_DRIFT")
        self.assertNotEqual(state["source_checks"]["i1-a1c"]["actual_blob_sha"],
                            state["source_checks"]["i1-a1c"]["pinned_blob_sha"])
        trace = rc.explain(rc.knowledge_graph(self.program, state), "I1-L3")
        self.assertEqual(trace["status"], "SOURCE_REVIEW_REQUIRED")
        self.assertTrue(trace["human_review_required"])

    def test_mermaid_no_raw_injection(self):
        knowledge = rc.knowledge_graph(self.program, self.state())
        knowledge["nodes"][0]["label"] = 'bad"]\nBAD --> DANGER'
        rendered = rc.graph_mermaid(knowledge)
        self.assertNotIn('bad"]', rendered)
        self.assertNotIn("\nBAD -->", rendered)
        self.assertIn("flowchart LR", rendered)

    def test_cli_modes_are_read_only(self):
        before = (self.root / rc.PROGRAM).read_bytes()
        for args in (["graph", "--mode", "knowledge", "--format", "json"],
                     ["trace", "--id", "finding:I1-A1C-TARGETED-NOGO", "--at-sha", self.sha],
                     ["catalog", "--limit", "1"],
                     ["status", "--at-sha", self.sha, "--format", "json"]):
            with self.subTest(args=args), redirect_stdout(io.StringIO()) as out:
                self.assertEqual(rc.main(args, self.root), 0)
                data = json.loads(out.getvalue())
                self.assertIn("status", data)
        self.assertEqual((self.root / rc.PROGRAM).read_bytes(), before)

    def test_ambiguous_and_unknown_trace_is_rejected(self):
        knowledge = rc.knowledge_graph(self.program, self.state())
        with self.assertRaises(ValueError):
            rc.explain(knowledge, "UNDECLARED")
        self.assertEqual(rc.explain(knowledge, "I2-G1")["focus"]["kind"], "gate")


if __name__ == "__main__":
    unittest.main()
