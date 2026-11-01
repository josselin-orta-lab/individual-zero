"""Dossier provenance tests: synthetic sources, no engine imports or scientific approval."""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_dossiers", ROOT / "tools/research_dossiers.py")
dossier = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(dossier)


class ResearchDossierTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        manifest = json.loads((ROOT / dossier.MANIFEST).read_text(encoding="utf-8"))
        self.manifest = manifest
        for folder in ("config", "src/i2"):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        (self.root / dossier.REGISTRY).write_text(json.dumps({
            "active_generation": "I1",
            "generations": {"I0": {"role": "frozen_reference"}, "I1": {"role": "active"}}
        }), encoding="utf-8")
        (self.root / "src/i2/engine.json").write_text(json.dumps({
            "generation": "I2", "status": "proposal", "entrypoints": {}
        }), encoding="utf-8")
        (self.root / dossier.PROGRAM).write_text(json.dumps({
            "questions": [{"id": q} for q in {d["question_id"] for d in manifest["dossiers"]}]
        }), encoding="utf-8")
        by_path = {}
        for src in manifest["sources"]:
            by_path.setdefault(src["path"], []).append(src["anchor"])
        for path, markers in by_path.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Synthetic source\n" + "\n".join(markers) +
                              "\nCI PASS refers only to tests.\n", encoding="utf-8")
        for src in manifest["sources"]:
            src["blob_sha"] = self.hash_file(src["path"])
        self.persist()

    def persist(self):
        (self.root / dossier.MANIFEST).write_text(
            json.dumps(self.manifest), encoding="utf-8")

    def hash_file(self, relative):
        raw = (self.root / relative).read_bytes()
        return hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

    def views(self):
        return dossier.load_views(self.root)

    def test_audit_only_validates_sources_not_science(self):
        result = dossier.validate(self.root)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["sources"], len(self.manifest["sources"]))
        self.assertEqual(result["dossiers"], 4)
        self.assertEqual(result["scientific_verdict"], "NOT_EVALUATED")
        self.assertTrue(all(s["status"] == "PIN_MATCH"
                            for s in result["source_integrity"].values()))

    def test_no_original_a1c_result_pretended(self):
        _, audit, views = self.views()
        view = next(v for v in views if v["id"] == "I1-A1C-TARGETED")
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(view["reported_assessment"], "NO_GO")
        self.assertEqual(view["primary_record"], "PRIMARY_ORIGINAL_RESULT_NOT_LINKED")
        self.assertEqual(view["scientific_verdict"], "NOT_EVALUATED")
        self.assertEqual(view["approval"], "NOT_GRANTED")
        self.assertIn("primary-outcome-record", {x["id"] for x in view["review_gaps"]})
        self.assertNotIn("reported_result", {x["role"] for x in view["sources"]})

    def test_unexecuted_cohort_never_has_results_or_approval(self):
        _, _, views = self.views()
        a2r = next(v for v in views if v["id"] == "I1-A2R-REWARD")
        self.assertEqual(a2r["reported_assessment"], "NOT_EXECUTED")
        self.assertEqual(a2r["primary_record"], "NO_RESULTS_EXPECTED_NOT_EXECUTED")
        self.assertIn("NOT_EXECUTED", {x["state"] for x in a2r["review_gaps"]})
        for d in self.manifest["dossiers"]:
            if d["id"] == "I1-A2R-REWARD":
                d["source_roles"].append({"source_id": "a235b-results", "role": "reported_result"})
        self.persist()
        self.assertTrue(any("cannot have claimed results" in e
                            for e in dossier.validate(self.root)["errors"]))

    def test_historical_inconclusive_not_overridden_by_ci_pass(self):
        _, _, views = self.views()
        v = next(x for x in views if x["id"] == "I1-A235B-COMPETITION")
        self.assertEqual(v["reported_assessment"], "INCONCLUSIVE")
        self.assertEqual(v["primary_record"], "RESULT_REPORT_LINKED_NOT_INDEPENDENTLY_ATTESTED")
        self.assertEqual(v["scientific_verdict"], "NOT_EVALUATED")
        self.assertIn("reported_result", [s["role"] for s in v["sources"]])

    def test_i2_proposal_never_approved(self):
        _, _, views = self.views()
        g1 = next(x for x in views if x["generation"] == "I2")
        self.assertEqual(g1["reported_assessment"], "REVIEW_REQUIRED")
        self.assertEqual(g1["primary_record"], "REVIEW_PROPOSALS_ONLY")
        self.assertEqual(g1["decision"], "REVIEW_ONLY_NO_AUTOMATIC_DECISION")
        self.assertFalse(any(s["role"] == "reported_result" for s in g1["sources"]))
        reg = json.loads((self.root / dossier.REGISTRY).read_text())
        reg["generations"]["I2"] = {"role": "active"}
        (self.root / dossier.REGISTRY).write_text(json.dumps(reg))
        self.assertEqual(dossier.validate(self.root)["status"], "FAIL")

    def test_blob_drift_even_when_anchor_survives(self):
        path = "docs/research/I1_ECO_A1C_PREREGISTRATION_2026-10-29.md"
        target = self.root / path
        target.write_text(target.read_text() + "\nUnexpected post-hoc edit.")
        _, aud, views = self.views()
        self.assertEqual(aud["status"], "FAIL")
        self.assertEqual(aud["source_integrity"]["a1c-prereg"]["status"], "SOURCE_BLOB_DRIFT")
        changed = next(x for x in views if x["id"] == "I1-A1C-TARGETED")
        original = next(x for x in views if x["id"] == "I1-A2R-REWARD")
        self.assertEqual(changed["source_integrity"], "SOURCE_RECONCILIATION_REQUIRED")
        pair = dossier.compare_views(original, changed)
        self.assertEqual(pair["status"], "SOURCE_RECONCILIATION_REQUIRED")

    def test_a1c_and_a2r_have_distinct_scopes(self):
        _, _, views = self.views()
        left, right = views[0], views[1]
        compared = dossier.compare_views(left, right)
        self.assertFalse(compared["same_explicit_scope"])
        self.assertEqual(compared["status"], "DIFFERENT_EXPERIMENT_OR_ENDPOINT_NO_CONTRADICTION_INFERRED")
        self.assertEqual(compared["scientific_verdict"], "NOT_EVALUATED")

    def test_same_scope_different_reported_assessments_are_review_leads(self):
        _, _, views = self.views()
        left = views[0]
        modified = deepcopy(views[1])
        modified["scope"] = left["scope"].copy()
        compared = dossier.compare_views(left, modified)
        self.assertEqual(compared["status"], "POSSIBLE_SAME_SCOPE_REPORTED_ASSESSMENT_DISAGREEMENT_REVIEW")
        self.assertNotIn("PROVEN_CONTRADICTION", compared["status"])
        with self.assertRaises(ValueError):
            dossier.compare_views(left, left)

    def test_forged_scientific_authority_and_missing_owners_rejected(self):
        self.manifest["dossiers"][0]["scientific_gate"] = "APPROVED"
        self.persist()
        self.assertEqual(dossier.validate(self.root)["status"], "FAIL")
        self.manifest["dossiers"][0]["scientific_gate"] = "NOT_EVALUATED"
        self.manifest["policy"]["no_auto_scientific_approval"] = False
        self.persist()
        self.assertEqual(dossier.validate(self.root)["status"], "FAIL")

    def test_unsafe_paths_and_source_swaps_rejected(self):
        self.manifest["sources"][0]["path"] = "../../private.md"
        self.persist()
        self.assertEqual(dossier.validate(self.root)["status"], "FAIL")
        self.manifest["sources"][0]["path"] = "docs/research/I1_ECO_A1C_PREREGISTRATION_2026-10-29.md"
        self.manifest["dossiers"][0]["source_roles"][0]["source_id"] = "a235b-results"
        self.persist()
        errors = dossier.validate(self.root)["errors"]
        self.assertTrue(any("preregistration role" in e for e in errors))

    def test_compact_gap_report_and_cli(self):
        _, _, views = self.views()
        gaps = dossier.gaps_report(views)
        self.assertEqual(gaps["status"], "REVIEW_QUEUE_ONLY")
        self.assertGreater(len(gaps["open_gaps"]), 4)
        self.assertEqual(gaps["execution"], "NOT_PERFORMED")
        for argv in (["audit"], ["list"], ["gaps"],
                     ["show", "--id", "I1-A1C-TARGETED"],
                     ["compare", "--left", "I1-A1C-TARGETED", "--right", "I1-A2R-REWARD"]):
            with self.subTest(argv=argv), redirect_stdout(io.StringIO()) as out:
                self.assertEqual(dossier.main(argv, self.root), 0)
                payload = json.loads(out.getvalue())
                self.assertEqual(payload["scientific_verdict"], "NOT_EVALUATED")



    def test_structure_only_exposes_live_status_drift_and_strict_fails(self):
        path = self.root / "src/i2/docs/STATUS.md"
        path.write_text(path.read_text(encoding="utf-8") +
                        "\nG2 synthetic witness note, no new authorization.\n",
                        encoding="utf-8")
        structural = dossier.validate(self.root, strict_sources=False)
        self.assertEqual(structural["status"], "PASS")
        self.assertEqual(structural["source_status"], "SOURCE_REVIEW_REQUIRED")
        self.assertIn("i2-status", structural["source_review_required"])
        self.assertEqual(structural["scientific_verdict"], "NOT_EVALUATED")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(dossier.main(["audit", "--structure-only"], self.root), 0)
        self.assertEqual(json.loads(out.getvalue())["audit_mode"], "STRUCTURE_ONLY")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(dossier.main(["audit"], self.root), 2)
        self.assertEqual(json.loads(out.getvalue())["status"], "FAIL")
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(dossier.main(["show", "--id", "I2-G1-INDEPENDENT-REVIEW"], self.root), 2)
        view = json.loads(out.getvalue())
        self.assertEqual(view["decision"], "REVIEW_SOURCE_CHANGES_FIRST")
        self.assertEqual(view["approval"], "NOT_GRANTED")


if __name__ == "__main__":
    unittest.main()
