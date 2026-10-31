"""Offline adversarial tests for navigation-only corpus indexing and deltas."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("research_corpus", ROOT / "tools/research_corpus.py")
corpus = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(corpus)


class ResearchCorpusTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.roots = ["docs/research", "src/i1/docs", "src/i2/docs",
                      "docs/architecture/proposals", "experiments"]
        for dirname in self.roots:
            (self.root / dirname).mkdir(parents=True, exist_ok=True)
        (self.root / "config").mkdir()
        (self.root / "config/research-program.json").write_text(
            json.dumps({"catalog_roots": self.roots}), encoding="utf-8")
        self.write("docs/research/a1-c-preregistration.md",
                   "# A1-C: preregistration\n\nissue #304 was defined before results.\n"
                   "No conclusions; test the same physical worlds.\n")
        self.write("docs/research/a1-c-results.md",
                   "# A1-C: results\n\nIssue #304, software CI PASS; "
                   "scientific A1-C NO_GO.\nA2-R NOT_EXECUTED.\n"
                   "\x60\x60\x60md\nIssue #999 and EXP-9999 are fictitious.\n\x60\x60\x60\n")
        self.write("src/i1/docs/EXPERIMENT_305_TD.md",
                   "# #305 instrumental credit study\n"
                   "[prior method](../../../docs/research/a1-c-preregistration.md)\n"
                   "The result is INCONCLUSIVE for causal attribution.\n")
        self.write("src/i2/docs/DELAYED_CREDIT_STUDY.md",
                   "# Synthetic H2\nIssue #663\n"
                   "G2 synthetic witness only; it does not imply motor authority.\n")
        self.write("docs/architecture/proposals/i2-g1-review.md",
                   "# I2 proposal\nissue #662 needs an independent decision.\n")
        self.write("experiments/TEMPLATE.md", "# Generic preregistration template\n")

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def index(self) -> dict:
        return corpus.build_index(self.root)

    def test_deterministic_inventory_and_hash(self):
        first, second = self.index(), self.index()
        self.assertEqual(first, second)
        self.assertEqual(first["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(first["summary"]["documents"], 6)
        self.assertEqual(first["head_sha"], "UNKNOWN")
        doc = next(d for d in first["documents"] if d["path"].endswith("a1-c-results.md"))
        self.assertEqual(doc["blob_sha"], corpus.git_blob((self.root / doc["path"]).read_bytes()))
        self.assertEqual(doc["filename_hint"], "possible_results")
        self.assertEqual(doc["parse_status"], "EXTRACTED_HINTS_ONLY")
        self.assertIn("study:A1-C", [x["key"] for x in doc["topics"]])
        self.assertNotIn("issue:999", [x["key"] for x in doc["topics"]])
        self.assertNotIn("exp:EXP-9999", [x["key"] for x in doc["topics"]])
        self.assertEqual(len([x for x in doc["status_mentions"] if "NO_GO" in x["signals"]]), 1)
        self.assertTrue(all(s["interpretation"] == "TEXT_MENTION_NOT_SCIENTIFIC_VERDICT"
                            for s in doc["status_mentions"]))

    def test_explicit_links_and_issue_heading(self):
        item = next(d for d in self.index()["documents"] if d["path"].endswith("EXPERIMENT_305_TD.md"))
        self.assertIn("issue:305", [x["key"] for x in item["topics"]])
        self.assertEqual(item["links"][0]["target"], "docs/research/a1-c-preregistration.md")
        self.assertTrue(item["links"][0]["target_exists"])
        self.assertEqual(item["generation_scope"], "I1_DOCUMENTATION")

    def test_grouped_protocol_result_is_lead_not_verdict(self):
        rows = corpus.related_groups(self.index(), topic="study:A1-C")
        self.assertEqual(rows["total_groups"], 1)
        group = rows["groups"][0]
        self.assertEqual(group["document_count"], 2)
        self.assertIn("possible_preregistration", group["kind_hints"])
        self.assertIn("possible_results", group["kind_hints"])
        self.assertIn("NO_GO", group["status_signals"])
        self.assertEqual(group["status"], "POSSIBLE_STATUS_SCOPE_DISAGREEMENT_REVIEW")
        self.assertIn("not evidence of scientific", rows["warning"])
        self.assertEqual(rows["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(corpus.related_groups(self.index(), topic="issue:000000")["status"],
                         "NO_EXPLICIT_TOPIC_MATCH")

    def test_delta_reports_only_file_changes_and_topics(self):
        before = self.index()
        self.write("docs/research/a1-c-results.md",
                   (self.root / "docs/research/a1-c-results.md").read_text() + "\nNew explanation.\n")
        self.write("docs/research/new-observation.md", "# New\nIssue #304 evidence to review.\n")
        (self.root / "experiments/TEMPLATE.md").unlink()
        new = self.index()
        changes = corpus.diff_index(before, new)
        self.assertEqual(changes["added"], ["docs/research/new-observation.md"])
        self.assertEqual(changes["removed"], ["experiments/TEMPLATE.md"])
        self.assertEqual(changes["changed"], ["docs/research/a1-c-results.md"])
        self.assertIn("issue:304", changes["topics_for_independent_review"])
        self.assertEqual(changes["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(corpus.diff_index(new, new)["status"], "NO_FILE_CHANGES")

    def test_malicious_or_mismatched_baseline_rejected(self):
        good = self.index()
        bad = json.loads(json.dumps(good))
        bad["documents"][0]["path"] = "../../secrets.md"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            corpus.diff_index(bad, good)
        bad = json.loads(json.dumps(good))
        bad["documents"].append(dict(bad["documents"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            corpus.diff_index(bad, good)
        bad = json.loads(json.dumps(good))
        bad["roots"] = ["docs/other"]
        with self.assertRaisesRegex(ValueError, "scope"):
            corpus.diff_index(bad, good)

    def test_symlink_escape_and_root_traversal_rejected(self):
        outside = self.root.parent / "private-outside-data.md"
        path = self.root / "docs/research/unsafe.md"
        try:
            path.symlink_to(outside)
            index = self.index()
            self.assertIn("docs/research/unsafe.md", index["skipped_symlink_paths"])
        finally:
            path.unlink(missing_ok=True)
        self.assertFalse(corpus.safe_relative("../outside"))
        self.assertFalse(corpus.safe_relative("/tmp/outside"))
        with self.assertRaises(ValueError):
            corpus.collect_paths(self.root, ["../outside"])

    def test_large_and_invalid_utf8_have_no_asserted_content(self):
        path = self.root / "docs/research/big-results.md"
        path.write_bytes(b"# prefix\n" + b"X" * 1500)
        item = corpus.extract_metadata(self.root, "docs/research/big-results.md",
                                       path.read_bytes(), max_bytes=1024)
        self.assertEqual(item["parse_status"], "TOO_LARGE_SKIPPED")
        self.assertEqual(item["topics"], [])
        path.write_bytes(b"\xff\x00\xfe")
        item = corpus.extract_metadata(self.root, "docs/research/big-results.md",
                                       path.read_bytes(), max_bytes=1024)
        self.assertEqual(item["parse_status"], "INVALID_UTF8_SKIPPED")

    def test_cli_index_delta_review_report_without_mutation(self):
        snapshot = self.root / "baseline.json"
        with redirect_stdout(io.StringIO()) as stream:
            self.assertEqual(corpus.main(["--root", str(self.root), "index", "--output", str(snapshot)]), 0)
        self.assertEqual(json.loads(stream.getvalue())["status"], "WRITTEN_LOCAL_ONLY")
        self.assertTrue(snapshot.is_file())
        self.assertEqual(corpus.validate_snapshot(json.loads(snapshot.read_text()),
                        roots=corpus.load_roots(self.root))["docs/research/a1-c-results.md"]["bytes"],
                         len((self.root / "docs/research/a1-c-results.md").read_bytes()))
        for command in (["delta", "--baseline", str(snapshot)],
                        ["review", "--topic", "issue:304"], ["report"]):
            with self.subTest(command=command), redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(corpus.main(["--root", str(self.root), *command]), 0)
                self.assertTrue(stream.getvalue())
        self.assertEqual(self.index()["summary"]["documents"], 6)
        with redirect_stderr(io.StringIO()):
            self.assertEqual(corpus.main(["--root", str(self.root), "index", "--max-parse-bytes", "100"]), 2)


if __name__ == "__main__":
    unittest.main()
